# Local AI Field Notes

**Small, inspectable experiments for people using ordinary computers.**

A Python standard-library runner and self-contained HTML report for local
Ollama-compatible model servers. It records the prompt, configuration, raw
answer, completion status and the timing evidence behind each result.

This is an early independent project by Hamza Mohammad Khan, Houston, Texas.
AI-assisted development is used. A creator channel and broader hardware study
are planned; no creator audience or sponsor approval is claimed.

## First measured record

The [raw extraction run](examples/2026-10-18-cpu-extraction.json) is a real,
single-case run on October 18, 2026: Qwen3.5:9b, Ollama 0.32.9, Q4_K_M,
i7-8700K desktop, 32 GB RAM, **CPU only with two threads**. The strict fictional
event-extraction check passed. Client wall time was 26.752 seconds, first answer
content arrived after 19.293 seconds, and the runtime reported 3.486 output
tokens/second during generation. Runtime-reported model load was 14.793 seconds.
This is one small observation, not a hardware ranking or a claim about general
model quality. It does not benchmark the desktop's GTX 1080 Ti.

An [offline HTML report](examples/2026-10-18-cpu-extraction.html) and the
[two-page project proposal](docs/project-brief.pdf) are included.

## What works in the first release

- Stream responses from an already-running local Ollama-compatible server.
- Keep client wall time separate from first-content latency and the runtime's
  own token-generation metrics.
- Check fictional structured extraction and summary constraints.
- Flag the Urdu task for human review rather than invent a language-quality score.
- Persist failed runs and reject incomplete streams.
- Produce an offline HTML report with escaped model output and explicit provenance.
- Limit requests to loopback endpoints. No API key is requested, read or stored.

## Quick start

Requires Python 3.10+ and an already-running model server. No Python dependencies
or package installation are needed.

```sh
python fieldnotes.py run \
  --model qwen3.5:9b \
  --hardware-label "My local desktop - CPU only" \
  --cpu --threads 2 --context 512 --max-output-tokens 128 \
  --case-id extract-event \
  --output runs/first-local-run.json

python fieldnotes.py report runs/first-local-run.json \
  --output runs/first-local-run.html
```

PowerShell users can place the command on one line or use PowerShell line
continuations. The model named above must already be installed; the runner
does not download models or launch a service.

Use a different `--endpoint http://127.0.0.1:PORT` for another local compatible
server. A remote machine can be used through a user-configured SSH tunnel.
The runner does not open ports or create tunnels.

`--keep-alive 0` requests unload after each generation. This does not establish
that the OS cache was cold. `--repeat 3` creates more observations, without
claiming a statistically reliable ranking. Choose an output filename that
does not already exist; overwriting requires an explicit flag.

## Evidence, not a leaderboard

| Field | Meaning |
|---|---|
| `wall_seconds` | Client-observed duration of the generation request |
| `first_content_seconds` | Time until the first non-empty answer content reaches the client |
| `runtime_generation_tokens_per_second` | Runtime-reported output tokens / runtime-reported generation time |
| `runtime_load_seconds` | Load duration reported by the server, when provided |
| `check` | A narrow mechanical result or a human-review requirement |
| `source` | `measured` or `fixture`; fixture output is not model performance |

The first-content metric is **not** a tokenizer-level first-token timestamp.
Runtime token accounting can vary. Failed or missing metrics remain visible.
The tool disables thinking in its request so answer latency has a declared
configuration; a server that rejects that option must be reported as unsupported,
not quietly retried with a different setup.

Do not compare runs as hardware-only experiments if model version, quantization,
prompt template, context size, runtime or generation settings differ.
The supplied checks do not establish general reasoning ability or semantic
correctness. The summary check only tests a word limit and named terms;
the Urdu task requires a transparent human review.

## Tests

```sh
python -m unittest -v
```

Tests use a temporary loopback HTTP fixture. They verify streaming, truncated
responses, JSON types, provenance, output escaping, local endpoint restrictions,
overwrite protection and the raw-JSON-to-HTML workflow. Fixture timings do not
benchmark a real model.

## Scope and next steps

The initial task set covers strict extraction, constrained summarization and
English-to-Urdu assistance. Next steps are additional measured local runs,
reproduction on another machine and an optional Lemonade-compatible integration.
Compatibility with Lemonade has **not** yet been verified by running that server.

The proposed first support request is a modest compute-credit grant or a
returnable review system, to extend reproducible tests and educational
walkthroughs. No sponsor approval or equipment award is claimed.

## Protocol references

- [Ollama generate API](https://docs.ollama.com/api/generate)
- [Lemonade API overview](https://lemonade-server.ai/docs/api/)

## Contact and license

Hamza Mohammad Khan · [GitHub](https://github.com/hkay26) ·
[hamzadedon@gmail.com](mailto:hamzadedon@gmail.com)

MIT license. Cases are fictional and contain no personal records.
