"""Shared helpers for the junior-dev plugin: talk to a local Ollama server.

Stdlib only (urllib) — no curl, no third-party deps. Imported by the thin
entrypoints in ../bin.
"""
import json
import os
import re
import urllib.error
import urllib.request

DEFAULT_HOST = "http://localhost:11434"


class OllamaError(RuntimeError):
    """An error with a short message and an exit code for the CLI to return."""

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def host():
    return os.environ.get("OLLAMA_HOST", DEFAULT_HOST).rstrip("/")


def _get(path, timeout=5):
    with urllib.request.urlopen(host() + path, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _post(path, payload, timeout=600):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        host() + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def list_models():
    """Installed model names. Raises OllamaError(3) if the server is unreachable."""
    try:
        data = _get("/api/tags")
    except (urllib.error.URLError, OSError) as e:
        raise OllamaError(f"Ollama not reachable at {host()} ({e})", 3)
    return [m["name"] for m in data.get("models", [])]


def resolve_model():
    """JUNIOR_MODEL if set, else the first installed model. Raises OllamaError(4)."""
    chosen = os.environ.get("JUNIOR_MODEL")
    if chosen:
        return chosen
    models = list_models()
    if not models:
        raise OllamaError("no model available (set JUNIOR_MODEL)", 4)
    return models[0]


def generate(prompt, model=None, think=False, temperature=0.0):
    """Run one non-streaming generation and return the cleaned response text.

    `think` maps to Ollama's top-level `think` flag (gemma's <|think|> token).
    Builds that reject the field are retried without it.
    """
    model = model or resolve_model()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": float(temperature)},
        "think": bool(think),
    }
    try:
        data = _post("/api/generate", payload)
    except urllib.error.HTTPError:
        payload.pop("think", None)  # model/build doesn't accept `think` — drop it
        try:
            data = _post("/api/generate", payload)
        except (urllib.error.URLError, OSError) as e:
            raise OllamaError(f"generate request failed ({e})", 5)
    except (urllib.error.URLError, OSError) as e:
        raise OllamaError(f"generate request failed ({e})", 5)
    return clean(data.get("response", ""))


_THOUGHT_RE = re.compile(r"<\|channel>thought.*?<channel\|>", re.S)
_OPEN_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_+-]*\n")
_CLOSE_FENCE_RE = re.compile(r"\n```$")


def clean(text):
    """Strip a leaked gemma 'thought' channel block and surrounding ``` fences."""
    text = _THOUGHT_RE.sub("", text)
    text = text.strip()
    text = _OPEN_FENCE_RE.sub("", text)
    text = _CLOSE_FENCE_RE.sub("", text)
    return text.strip()
