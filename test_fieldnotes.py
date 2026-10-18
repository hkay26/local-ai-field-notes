import argparse
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
import fieldnotes as fn

class EndpointTests(unittest.TestCase):
    def test_loopback_only_and_no_embedded_secrets(self):
        for value in ["http://127.0.0.1:11434","http://localhost:8000","http://[::1]:8080"]:
            self.assertEqual(fn.endpoint_url(value),value)
        for value in ["https://example.com","http://127.0.0.1@evil.example","http://u:p@localhost",
                      "http://localhost?token=secret","http://localhost/#fragment","file:///tmp/model","http://localhost/api"]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                fn.endpoint_url(value)

class CheckTests(unittest.TestCase):
    def test_json_requires_types_and_plain_json(self):
        check={"type":"json_subset","expected":{"count":1}}
        self.assertEqual(fn.validate_output('{"count":1}',check)["status"],"pass")
        for response in ['{"count":true}','{"count":"1"}','markdown {"count":1}',"not JSON"]:
            with self.subTest(response=response):
                self.assertEqual(fn.validate_output(response,check)["status"],"fail")
    def test_human_language_check_never_auto_passes(self):
        self.assertEqual(fn.validate_output("some text",{"type":"human"})["status"],"human_review")
    def test_summary_is_a_constraint_check(self):
        check={"type":"summary_constraints","max_words":4,"required_terms":["Friday"]}
        self.assertEqual(fn.validate_output("Closed Friday at 4",check)["status"],"pass")
        self.assertEqual(fn.validate_output("Closed Saturday at 4",check)["status"],"fail")
        self.assertEqual(fn.validate_output("We are closed on Friday at 4",check)["status"],"fail")
        self.assertEqual(fn.validate_output("",check)["status"],"fail")
    def test_case_file_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"cases.json"
            case={"id":"one","prompt":"Hello","check":{"type":"human"}}
            path.write_text(json.dumps([case,case]))
            with self.assertRaises(ValueError):
                fn.read_cases(path)

class FixtureServer(BaseHTTPRequestHandler):
    mode="valid"
    def log_message(self,*args):
        pass
    def do_GET(self):
        self.send_response(200);self.end_headers()
        self.wfile.write(b'{"version":"fixture-only"}')
    def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.send_response(200);self.end_headers()
        if self.path=="/api/show":
            self.wfile.write(b'{"details":{"fixture":true},"capabilities":["completion"]}')
            return
        if type(self).mode=="malformed":
            self.wfile.write(b'not JSON\n');return
        event={"response":'{"city":"Houston","day":"Tuesday","attendees":12}',"done":False}
        self.wfile.write(json.dumps(event).encode()+b"\n");self.wfile.flush()
        if type(self).mode=="truncated":
            return
        done={"response":"","done":True,"eval_count":20,"eval_duration":2_000_000_000,"load_duration":100_000_000,"done_reason":"stop"}
        if type(self).mode=="no_metrics":
            done={"response":"","done":True,"eval_count":None,"eval_duration":None,"load_duration":None}
        self.wfile.write(json.dumps(done).encode()+b"\n")

@contextlib.contextmanager
def server(mode):
    FixtureServer.mode=mode
    instance=ThreadingHTTPServer(("127.0.0.1",0),FixtureServer)
    thread=threading.Thread(target=instance.serve_forever,daemon=True);thread.start()
    try:
        yield "http://127.0.0.1:"+str(instance.server_address[1])
    finally:
        instance.shutdown();instance.server_close();thread.join()

class WorkflowTests(unittest.TestCase):
    def args(self,tmp,base):
        return argparse.Namespace(endpoint=base,model="fixture-model",cases=str(Path(__file__).with_name("cases.json")),
            output=str(Path(tmp)/"fixture.json"),hardware_label="SYNTHETIC TEST SERVER",
            case_id="extract-event",repeat=1,context=512,max_output_tokens=64,threads=2,
            cpu=True,keep_alive="0",timeout=5,source="fixture",overwrite=False)
    def test_stream_metrics_json_and_html_workflow(self):
        with tempfile.TemporaryDirectory() as tmp,server("valid") as base:
            args=self.args(tmp,base)
            run=fn.run_experiment(args)
            self.assertEqual(run["source"],"fixture")
            self.assertEqual(run["results"][0]["check"]["status"],"pass")
            self.assertEqual(run["results"][0]["runtime_generation_tokens_per_second"],10.0)
            self.assertIsNotNone(run["results"][0]["first_content_seconds"])
            self.assertEqual(json.loads(Path(args.output).read_text())["model"],"fixture-model")
            report=fn.make_report(run,Path(tmp)/"fixture.html").read_text()
            self.assertIn("SYNTHETIC RESPONSES",report)
            self.assertIn("human review",report)
            self.assertNotIn("<script",report)
            with self.assertRaises(ValueError):
                fn.run_experiment(args)
    def test_incomplete_or_malformed_stream_is_never_success(self):
        for mode in ["truncated","malformed"]:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as tmp,server(mode) as base:
                run=fn.run_experiment(self.args(tmp,base))
                self.assertEqual(run["results"][0]["status"],"error")
                self.assertEqual(run["results"][0]["check"]["status"],"not_run")
    def test_missing_optional_metrics_preserve_a_valid_response(self):
        with tempfile.TemporaryDirectory() as tmp,server("no_metrics") as base:
            result=fn.run_experiment(self.args(tmp,base))["results"][0]
            self.assertEqual(result["status"],"completed")
            self.assertEqual(result["check"]["status"],"pass")
            self.assertIsNone(result["runtime_generation_tokens_per_second"])
            self.assertIsNone(result["runtime_load_seconds"])
    def test_report_escapes_model_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            run={"source":"fixture","model":"<img src=x onerror=alert(1)>","results":[
                {"case_id":"x","response":"<script>alert(1)</script>","status":"completed",
                 "check":{"status":"human_review"}}]}
            report=fn.make_report(run,Path(tmp)/"safe.html").read_text()
            self.assertIn("&lt;script&gt;",report)
            self.assertNotIn("<script>",report)
            self.assertNotIn("<img src=x",report)
    def test_report_rejects_missing_provenance(self):
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(ValueError):
            fn.make_report({"results":[]},Path(tmp)/"unsafe.html")

if __name__=="__main__":
    unittest.main(verbosity=2)
