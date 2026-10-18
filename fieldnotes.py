#!/usr/bin/env python3
"""Small, inspectable local-model experiments. Python 3.10+, standard library only."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
import ipaddress
import json
import math
import os
from pathlib import Path
import platform
import re
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "0.2.0"
MAX_RESPONSE_BYTES = 2_000_000

def endpoint_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use an http(s) loopback endpoint.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Endpoint must not contain credentials, query parameters or a fragment.")
    host = parsed.hostname.lower()
    try:
        local = ipaddress.ip_address(host).is_loopback
    except ValueError:
        local = host == "localhost"
    if not local:
        raise ValueError("This local-only tool accepts loopback hosts. Use your own SSH tunnel for a remote server.")
    if parsed.path not in ("", "/"):
        raise ValueError("Use the server origin, without an API path.")
    return value.rstrip("/")

def json_request(base: str, path: str, payload=None, timeout=10):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base+path, data=body,
        headers={"Content-Type":"application/json","User-Agent":"LocalAIFieldNotes/"+VERSION})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        data=response.read(MAX_RESPONSE_BYTES+1)
    if len(data)>MAX_RESPONSE_BYTES:
        raise ValueError("Metadata response exceeded the safety limit.")
    return json.loads(data)

def read_cases(path: Path):
    raw=path.read_bytes()
    cases=json.loads(raw)
    if not isinstance(cases,list) or not cases:
        raise ValueError("Cases must be a non-empty JSON list.")
    seen=set()
    for case in cases:
        if not isinstance(case,dict):
            raise ValueError("Each case must be an object.")
        ident=case.get("id")
        if not isinstance(ident,str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}",ident) or ident in seen:
            raise ValueError("Every case needs a unique, simple id.")
        seen.add(ident)
        if not isinstance(case.get("prompt"),str) or not case["prompt"].strip():
            raise ValueError(f"{ident}: missing prompt.")
        check=case.get("check")
        if not isinstance(check,dict) or check.get("type") not in ("json_subset","summary_constraints","human"):
            raise ValueError(f"{ident}: unsupported check.")
        if check["type"]=="json_subset" and "expected" not in check:
            raise ValueError(f"{ident}: expected JSON is required.")
        if check["type"]=="summary_constraints":
            if not isinstance(check.get("max_words"),int) or check["max_words"]<1:
                raise ValueError(f"{ident}: a positive max_words is required.")
            if not isinstance(check.get("required_terms",[]),list) or not all(isinstance(t,str) for t in check.get("required_terms",[])):
                raise ValueError(f"{ident}: required_terms must contain strings.")
    return cases,hashlib.sha256(raw).hexdigest()

def is_subset(expected,actual):
    if isinstance(expected,dict):
        return isinstance(actual,dict) and all(k in actual and is_subset(v,actual[k]) for k,v in expected.items())
    if isinstance(expected,list):
        return isinstance(actual,list) and len(expected)==len(actual) and all(is_subset(x,y) for x,y in zip(expected,actual))
    return type(expected) is type(actual) and expected==actual

def validate_output(text: str,check: dict):
    kind=check["type"]
    if kind=="human":
        return {"status":"human_review","reason":check.get("rubric","A human review is required.")}
    if kind=="json_subset":
        try:
            parsed=json.loads(text.strip())
        except json.JSONDecodeError:
            return {"status":"fail","reason":"Response is not strict JSON. Markdown fences and commentary are not accepted."}
        ok=is_subset(check["expected"],parsed)
        return {"status":"pass" if ok else "fail","reason":"Expected fields/types match." if ok else "Expected fields/types do not match."}
    words=len(text.split())
    missing=[t for t in check.get("required_terms",[]) if t.casefold() not in text.casefold()]
    ok=words<=check["max_words"] and not missing and bool(text.strip())
    return {"status":"pass" if ok else "fail","words":words,"missing_terms":missing,
            "reason":"Mechanical constraints only; this does not establish factual or semantic quality."}

def positive_number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>0

def run_case(base,model,case,settings,timeout,api_mode="generate"):
    payload={"model":model,"prompt":case["prompt"],"stream":True,
             "keep_alive":settings["keep_alive"],"think":False,
             "options":{"temperature":0,"seed":42,"num_ctx":settings["context"],
                        "num_predict":settings["max_output_tokens"],"num_thread":settings["threads"]}}
    if settings["cpu"]:
        payload["options"]["num_gpu"]=0
    if api_mode=="chat":
        payload.pop("prompt")
        payload["messages"]=[{"role":"user","content":case["prompt"]}]
    elif api_mode!="generate":
        raise ValueError("API mode must be generate or chat.")
    started=time.perf_counter()
    first_content=None
    final=None
    parts=[]
    consumed=0
    req=urllib.request.Request(base+"/api/"+api_mode,data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","User-Agent":"LocalAIFieldNotes/"+VERSION})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        while True:
            line=response.readline(MAX_RESPONSE_BYTES+1)
            if not line:
                break
            consumed+=len(line)
            if consumed>MAX_RESPONSE_BYTES:
                raise ValueError("Generation stream exceeded the size limit.")
            if not line.strip():
                continue
            event=json.loads(line)
            if event.get("error"):
                raise ValueError("Runtime returned an error: "+str(event["error"])[:400])
            if api_mode=="chat":
                message=event.get("message",{})
                if not isinstance(message,dict):
                    raise ValueError("Runtime chat message was not an object.")
                text=message.get("content","")
            else:
                text=event.get("response","")
            if not isinstance(text,str):
                raise ValueError("Runtime response content was not text.")
            if text:
                if first_content is None:
                    first_content=time.perf_counter()-started
                parts.append(text)
            if event.get("done") is True:
                final=event
                break
    elapsed=time.perf_counter()-started
    if final is None:
        raise ValueError("Stream ended without a completed event; partial output is not a successful run.")
    count=final.get("eval_count")
    duration=final.get("eval_duration")
    rate=count/(duration/1e9) if positive_number(count) and positive_number(duration) else None
    result="".join(parts)
    load_duration=final.get("load_duration")
    return {
        "case_id":case["id"],"title":case.get("title",case["id"]),"prompt":case["prompt"],
        "response":result,"wall_seconds":round(elapsed,6),
        "first_content_seconds":None if first_content is None else round(first_content,6),
        "runtime_output_tokens":count if positive_number(count) else None,
        "runtime_generation_seconds":round(duration/1e9,6) if positive_number(duration) else None,
        "runtime_generation_tokens_per_second":round(rate,4) if rate is not None else None,
        "runtime_load_seconds":load_duration/1e9 if isinstance(load_duration,(int,float)) and not isinstance(load_duration,bool) and math.isfinite(load_duration) and load_duration>=0 else None,
        "done_reason":final.get("done_reason","not_reported"),
        "check":validate_output(result,case["check"]),"status":"completed",
    }

def safe_metadata(base,model,runtime_kind="ollama"):
    metadata={}
    for label,path,payload in [("version","/api/version",None),("model","/api/show",{"model":model}),("tags","/api/tags",None)]:
        try:
            response=json_request(base,path,payload)
            if label=="version":
                metadata["runtime_version"]=response.get("version","not_reported")
            elif label=="model":
                metadata["model_details"]=response.get("details",{})
                metadata["model_capabilities"]=response.get("capabilities",[])
            else:
                match=next((m for m in response.get("models",[]) if m.get("name")==model or m.get("model")==model),None)
                if match:
                    digest=match.get("digest")
                    if isinstance(digest,str) and re.fullmatch(r"(?:sha256:)?0{64}",digest):
                        metadata["reported_model_digest"]=digest
                        metadata["model_digest"]=None
                        metadata["model_digest_note"]="Runtime returned an all-zero placeholder, not a model content digest."
                    else:
                        metadata["model_digest"]=digest
        except (OSError,ValueError) as exc:
            metadata[label+"_note"]=type(exc).__name__+": metadata unavailable"
    if runtime_kind=="lemonade":
        metadata["runtime_name"]="Lemonade"
        metadata["compatibility_api_version"]=metadata.pop("runtime_version","not_reported")
        try:
            metadata["runtime_version"]=json_request(base,"/v1/health").get("version","not_reported")
        except (OSError,ValueError) as exc:
            metadata["runtime_version"]="not_reported"
            metadata["identity_note"]=type(exc).__name__+": native runtime version unavailable"
    return metadata

def atomic_json(path: Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+".partial")
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    temp.replace(path)

def run_experiment(args):
    base=endpoint_url(args.endpoint)
    cases,case_hash=read_cases(Path(args.cases))
    if args.case_id:
        cases=[c for c in cases if c["id"]==args.case_id]
        if not cases:
            raise ValueError("Requested case id is not in the case file.")
    settings={"context":args.context,"max_output_tokens":args.max_output_tokens,
              "threads":args.threads,"cpu":args.cpu,"keep_alive":args.keep_alive,
              "temperature":0,"seed":42,"thinking":False}
    api_mode=getattr(args,"api_mode","generate")
    runtime_kind=getattr(args,"runtime_kind","ollama")
    run={
        "schema_version":1,"tool_version":VERSION,"source":args.source,
        "created_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "model":args.model,"hardware_label":args.hardware_label,"runtime_protocol":"ollama",
        "api_mode":api_mode,"runtime_kind":runtime_kind,
        "settings":settings,"case_file_sha256":case_hash,
        "host":{"os":platform.system(),"architecture":platform.machine(),"logical_cpus":os.cpu_count()},
        "notes":[
            "First-content latency measures first non-empty response content received by the client, not a tokenizer-level first-token timestamp.",
            "Throughput uses runtime-reported token counts and generation duration when available; it is distinct from end-to-end throughput.",
            "Token counts may include runtime-specific accounting. Prompt templates, cache state, model precision and runtime affect comparisons.",
            "Mechanical checks are task smoke tests, not a general intelligence score. Language quality requires human review.",
            "Small sample sizes do not establish statistical performance rankings.",
            "Settings are requested values; a compatible server may not implement every option. Inspect native configuration when verifying enforcement.",
            "A fixture run validates the tool only and must never be presented as model performance.",
        ],
        "runtime_metadata":safe_metadata(base,args.model,runtime_kind),"results":[]
    }
    output=Path(args.output)
    if output.exists() and not args.overwrite:
        raise ValueError("Output already exists. Choose a new filename or explicitly pass --overwrite.")
    for repeat in range(1,args.repeat+1):
        for case in cases:
            try:
                result=run_case(base,args.model,case,settings,args.timeout,api_mode)
                result["repeat"]=repeat
            except (OSError,ValueError,TypeError) as exc:
                result={"case_id":case["id"],"title":case.get("title",case["id"]),
                    "repeat":repeat,"status":"error","error":type(exc).__name__+": "+str(exc)[:600],
                    "check":{"status":"not_run","reason":"Generation did not finish successfully."}}
            run["results"].append(result)
            atomic_json(output,run)
            print(json.dumps({"case":case["id"],"repeat":repeat,"status":result["status"],"check":result["check"]["status"]}))
    return run

def make_report(run,path: Path):
    if run.get("source") not in ("measured","fixture"):
        raise ValueError("Run must explicitly identify its evidence source.")
    esc=lambda x:html.escape(str(x),quote=True)
    results=run.get("results",[])
    good=[r for r in results if r.get("status")=="completed"]
    times=[r["wall_seconds"] for r in good if positive_number(r.get("wall_seconds"))]
    median=f"{statistics.median(times):.3f} s" if times else "Unavailable"
    fixture=run["source"]=="fixture"
    warning=("TEST FIXTURE - SYNTHETIC RESPONSES. This report verifies the runner/report workflow. It contains no measured model performance."
             if fixture else "MEASURED RUN. Results describe only this model, configuration and test set; no broader ranking is implied.")
    metadata=run.get("runtime_metadata",{})
    reported_digest=metadata.get("reported_model_digest",metadata.get("model_digest"))
    digest_notice=("<div class=\"notice\">MODEL PROVENANCE: the compatible API returned an all-zero placeholder. "
                   "It is not a model content digest; consult the accompanying independently collected provenance.</div>"
                   if isinstance(reported_digest,str) and re.fullmatch(r"(?:sha256:)?0{64}",reported_digest) else "")
    cards=[]
    for result in results:
        status=result.get("check",{}).get("status","not_run")
        metrics=[]
        for label,key in [("Wall time","wall_seconds"),("First content","first_content_seconds"),("Runtime tok/s","runtime_generation_tokens_per_second")]:
            value=result.get(key)
            metrics.append(f"<span>{esc(label)}<b>{esc('unavailable' if value is None else value)}</b></span>")
        content=result.get("response",result.get("error","No output."))
        cards.append(f'<article><div class="row"><h2>{esc(result.get("title",result.get("case_id")))}</h2><span class="pill">{esc(status)}</span></div><p>Repetition {esc(result.get("repeat",1))} · {esc(result.get("status"))}</p><div class="metrics">{"".join(metrics)}</div><p>{esc(result.get("check",{}).get("reason",""))}</p><details><summary>Inspect prompt and output</summary><h3>Prompt</h3><pre>{esc(result.get("prompt","Not retained after failed generation."))}</pre><h3>Output / error</h3><pre>{esc(content)}</pre></details></article>')
    report=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local AI Field Notes - {esc(run.get("model"))}</title>
<style>:root{{font:16px/1.55 system-ui;color:#203448;background:#eef3f6}}body{{margin:0}}main{{max-width:1040px;margin:auto;padding:40px 22px}}header{{background:#14283f;color:white;padding:32px;border-radius:18px}}h1{{font-size:2.5rem;line-height:1.1;margin:12px 0}}header p{{color:#d5e2ef}}.eyebrow{{letter-spacing:.14em;font-size:.75rem;font-weight:700}}.notice{{border-left:4px solid #a7700a;background:#fff3d8;padding:18px;margin:22px 0}}.stats,.metrics,.row{{display:flex;gap:24px;flex-wrap:wrap}}.stats{{padding:18px 0}}.stats span,.metrics span{{font-size:.8rem;color:#5a6f80}}b{{display:block;font-size:1.2rem;color:#17394b}}article{{background:white;border:1px solid #d4e0e7;border-radius:12px;padding:24px;margin:18px 0}}h2{{margin:0;font-size:1.2rem}}.row{{align-items:center;justify-content:space-between}}.pill{{font-size:.75rem;border:1px solid #91bcb5;padding:4px 10px;border-radius:99px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:#eff4f7;border-radius:8px;font-size:.85rem}}summary{{cursor:pointer;color:#076f68}}footer{{font-size:.85rem;color:#607083}}details{{margin-top:20px}}@media print{{main{{padding:0}}article{{break-inside:avoid}}details{{display:block}}}}</style></head><body><main>
<header><div class="eyebrow">LOCAL AI FIELD NOTES / EXPERIMENT RECORD</div><h1>{esc(run.get("model"))}</h1><p>{esc(run.get("hardware_label"))}<br>{esc(run.get("created_at_utc"))}</p></header>
<div class="notice">{esc(warning)}</div>{digest_notice}<div class="stats"><span>Completed<b>{len(good)} / {len(results)}</b></span><span>Median client wall time<b>{median}</b></span><span>Evidence source<b>{esc(run["source"])}</b></span></div>
{"".join(cards)}<article><h2>Configuration and provenance</h2><pre>{esc(json.dumps({k:v for k,v in run.items() if k!="results"},indent=2,ensure_ascii=False))}</pre></article>
<footer>Generated locally with standard-library Python. No analytics, remote assets or client-side network requests. Inspect the accompanying raw JSON before drawing conclusions.</footer></main></body></html>"""
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(report,encoding="utf-8")
    return path

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run",help="Run small experiments against an already-running local Ollama-compatible server.")
    run.add_argument("--endpoint",default="http://127.0.0.1:11434")
    run.add_argument("--model",required=True)
    run.add_argument("--api-mode",choices=["generate","chat"],default="generate",help="Explicit completion or chat request; prompt rendering can differ.")
    run.add_argument("--runtime-kind",choices=["ollama","lemonade"],default="ollama",help="Use Lemonade native health metadata rather than mistaking its compatibility version for its native version.")
    run.add_argument("--cases",default=str(Path(__file__).with_name("cases.json")))
    run.add_argument("--output",required=True)
    run.add_argument("--hardware-label",required=True,help="A public, non-sensitive description; do not include serial numbers.")
    run.add_argument("--case-id")
    run.add_argument("--repeat",type=int,default=1,choices=range(1,11))
    run.add_argument("--context",type=int,default=2048)
    run.add_argument("--max-output-tokens",type=int,default=128)
    run.add_argument("--threads",type=int,default=2)
    run.add_argument("--cpu",action="store_true")
    run.add_argument("--keep-alive",default="0",help="Requested keep-alive value; Ollama uses 0 to unload. Compatible servers may differ.")
    run.add_argument("--timeout",type=float,default=90)
    run.add_argument("--source",choices=["measured","fixture"],default="measured")
    run.add_argument("--overwrite",action="store_true")
    report=sub.add_parser("report",help="Render existing raw JSON as a self-contained HTML report.")
    report.add_argument("input")
    report.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=="run":
            if args.context<128 or args.max_output_tokens<1 or args.threads<1 or not math.isfinite(args.timeout) or args.timeout<=0:
                parser.error("Context >=128, tokens >=1, threads >=1 and timeout >0 are required.")
            result=run_experiment(args)
            return 0 if all(r["status"]=="completed" for r in result["results"]) else 2
        make_report(json.loads(Path(args.input).read_text(encoding="utf-8")),Path(args.output))
        return 0
    except (OSError,ValueError) as exc:
        print(f"Error: {exc}",file=__import__("sys").stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
