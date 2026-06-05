# junior-dev

A Claude Code plugin that delegates **junior-level coding tasks** to a local
[Ollama](https://ollama.com) model — saving Claude usage on work that's simple,
self-contained, and easy to verify.

Claude stays in charge: it triages the task, writes a precise spec, hands
generation to your local model, runs an objective check (tests / typecheck /
lint), then reports back. Conservative by design — when in doubt, Claude just
does it itself.

## Why it saves money

The expensive part is Claude's token generation. For mechanical work (boilerplate,
test stubs, simple functions) the local model does the bulk generation for free,
while Claude only spends tokens on triage + verification. Local "thinking" tokens
are also free, so the model can reason for a better first pass — which means fewer
expensive Claude-side retries.

## Requirements
- [Ollama](https://ollama.com) running locally (`ollama serve`)
- At least one model pulled (e.g. `ollama pull gemma2:9b`)
- `python3` (standard library only — no `pip install`, no `curl`)

## Install
```
/plugin marketplace add davidnet/junior-dev
/plugin install junior-dev@junior-dev
```

## Use
Work normally. When Claude spots a junior task it offers to delegate and asks you
to confirm. Or invoke it explicitly:
```
/junior-dev:junior write unit-test stubs for utils.py
```

## Configuration (env vars)
| Var | Default | Meaning |
|-----|---------|---------|
| `OLLAMA_HOST`  | `http://localhost:11434` | Ollama API endpoint |
| `JUNIOR_MODEL` | first installed model    | Model to use |
| `JUNIOR_TEMP`  | `0`                      | Sampling temperature |
| `JUNIOR_THINK` | `0`                      | `1` = let the model reason before answering |

Set them in your shell profile, e.g.:
```
export JUNIOR_MODEL=gemma2:9b
```

## How it works
`triage → confirm → spec → delegate (local model) → verify (objective gate) →
accept / retry ≤2 / stop & report`. The full rubric lives in
[`skills/junior-dev/SKILL.md`](skills/junior-dev/SKILL.md).

## Testing
```
python3 -m unittest discover -s tests   # unit tests for the cleaning/resolve logic (no network)
python3 tests/smoke.py                  # live round-trip vs Ollama (SKIPs if it's down)
```

## License
MIT
