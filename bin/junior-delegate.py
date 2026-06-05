#!/usr/bin/env python3
"""junior-delegate — send a spec (stdin) to a local Ollama model, print clean code.

Usage:   printf '%s' "<spec>" | junior-delegate.py
Config (env):
    OLLAMA_HOST   default http://localhost:11434
    JUNIOR_MODEL  default: first installed model
    JUNIOR_TEMP   default 0
    JUNIOR_THINK  default 0 (thinking OFF). Set 1 to let the model reason first.
Exit:  0 ok | 2 empty spec | 3 unreachable | 4 no model | 5 request failed
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from junior_ollama import OllamaError, generate  # noqa: E402


def main():
    spec = sys.stdin.read()
    if not spec.strip():
        print("junior-delegate: empty spec on stdin", file=sys.stderr)
        return 2
    try:
        code = generate(
            spec,
            think=os.environ.get("JUNIOR_THINK", "0") == "1",
            temperature=float(os.environ.get("JUNIOR_TEMP", "0")),
        )
    except OllamaError as e:
        print(f"junior-delegate: {e}", file=sys.stderr)
        return e.code
    print(code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
