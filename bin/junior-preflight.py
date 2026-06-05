#!/usr/bin/env python3
"""junior-preflight — check a local Ollama is reachable and has a model.

Prints a short status and exits 0 when ready, non-zero otherwise.
Config (env): OLLAMA_HOST, JUNIOR_MODEL
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from junior_ollama import OllamaError, host, list_models  # noqa: E402


def main():
    try:
        models = list_models()
    except OllamaError as e:
        print(f"junior-dev: {e}")
        print("  Start it with 'ollama serve', or set OLLAMA_HOST to your endpoint.")
        return 1
    if not models:
        print(f"junior-dev: Ollama is up at {host()} but no models are installed.")
        print("  Pull one, e.g. 'ollama pull gemma2:9b', then set JUNIOR_MODEL.")
        return 1
    using = os.environ.get("JUNIOR_MODEL") or f"{models[0]}  (auto: first model)"
    print(f"junior-dev: ready. Host={host()}")
    print(f"  Installed: {' '.join(models)}")
    print(f"  Using:     {using}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
