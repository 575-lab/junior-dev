#!/usr/bin/env python3
"""Live smoke test: preflight + one real generation against the local Ollama.

SKIPs (exit 0) if Ollama is unreachable, so it's safe to run anywhere.
Run:  python3 tests/smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import junior_ollama as jo  # noqa: E402


def main():
    try:
        models = jo.list_models()
    except jo.OllamaError as e:
        print(f"SKIP: {e}")
        return 0
    if not models:
        print("SKIP: Ollama up but no models installed.")
        return 0

    print(f"preflight OK — models: {', '.join(models)}; using: {jo.resolve_model()}")

    spec = (
        "Write a Python function add(a, b) that returns a + b. "
        "Return ONLY code, no markdown, no explanation."
    )
    code = jo.generate(spec, think=False)
    print("--- generated ---")
    print(code)
    print("-----------------")

    # Assert it produced runnable code with the right behavior.
    assert "def add" in code, "expected a function named add"
    assert "```" not in code, "code fences were not stripped"
    assert "<|channel" not in code and "<channel|>" not in code, "thought block leaked"
    ns = {}
    exec(code, ns)  # noqa: S102 - trusted local smoke test
    assert ns["add"](2, 3) == 5, "add(2,3) should be 5"

    print("PASS: generation produced correct, clean, runnable code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
