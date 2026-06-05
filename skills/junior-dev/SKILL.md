---
name: junior
description: Delegate a junior-level coding task to a local Ollama model to save Claude usage. Use when a task is simple, self-contained, and objectively verifiable — boilerplate, scaffolding, simple pure functions, test stubs, docstrings/comments, repetitive pattern edits, format/regex conversions. Claude triages, writes the spec, delegates generation, runs an objective check, then reports. Do NOT use for tasks needing judgment, broad codebase context, debugging, architecture, or security-sensitive code.
---

# junior-dev: delegate junior tasks to a local model

Offload **generation** of low-judgment, easily-verified code to a local Ollama
model while Claude stays the orchestrator: triage → confirm → spec → delegate →
verify → report. This saves Claude output tokens only when generation is large
and the result is cheap to check.

## 1. Triage — be conservative; when in doubt, do NOT delegate

Delegate ONLY if ALL of these hold:
- **Self-contained**: the full spec fits in a short prompt; little or no
  surrounding code context is needed to get it right (the local model can't see
  the repo).
- **Low judgment**: there is basically one reasonable implementation.
- **Objectively verifiable**: a test, typecheck, compile, lint, or a trivially
  obvious read confirms correctness. If you can't name the check up front, don't
  delegate.

Good fits: boilerplate/scaffolding, simple pure functions, test stubs, docstrings
and comments, repetitive edits across a known pattern, format conversions, regex,
simple data transforms, config files.

Never delegate: debugging, architecture/design, multi-file changes, ambiguous
requirements, security-sensitive code, or anything where "correct" requires
reading the surrounding codebase.

If a task mixes junior and senior parts, either do it yourself or split it: keep
the judgment, delegate only the mechanical sub-part.

## 2. Confirm before delegating

When you spot a junior task, briefly tell the user what you'd delegate and the
check you'll verify it with, then ask for a quick OK. Do not delegate silently.

## 3. Preflight

Run `junior-preflight.py`. If Ollama is unreachable or has no model, tell the
user and just do the task yourself.

## 4. Write a tight spec

Write an unambiguous spec for the local model: exact signature, inputs/outputs,
constraints, language, and "return ONLY code — no markdown, no explanation." Keep
it fully self-contained.

## 5. Delegate

    printf '%s' "$SPEC" | junior-delegate.py

Returns clean code on stdout (thinking block and ``` fences already stripped).

**Decide thinking per task.** Local thinking tokens are ~free (just latency), and
a better first pass means fewer expensive Claude-side retries:
- Pure boilerplate / mechanical → leave thinking off (default).
- Any real logic, edge cases, or correctness nuance → prefix with `JUNIOR_THINK=1`:

      printf '%s' "$SPEC" | JUNIOR_THINK=1 junior-delegate.py

Config via env: `JUNIOR_MODEL` (default: first installed model), `OLLAMA_HOST`
(default http://localhost:11434), `JUNIOR_TEMP` (default 0).

## 6. Verify with an OBJECTIVE gate (required)

Run the check you named in triage — tests / typecheck / compile / lint, or for
trivial output a careful read. **Never accept the output blind.**

- **Pass** → integrate it; tell the user it came from the local model.
- **Fail** → append the exact error to the spec and re-delegate (consider turning
  `JUNIOR_THINK=1` on for the retry). **Max 2 retries.**
- **Still failing after retries** → STOP. Hand back the local model's best attempt
  plus the failure and let the user decide. Do it yourself only if they ask. Don't
  silently burn tokens cleaning up bad output.

## Iron rules
- Conservative triage beats clever triage — a wrong delegation costs more than no
  delegation.
- Always verify against an objective gate before accepting.
- Bounded retries (≤2), then stop and report.
- Be transparent: say what you delegated, whether it reasoned, and how you verified.
