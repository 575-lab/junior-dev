"""Unit tests for the pure logic in lib/junior_ollama.py (no network needed).

Run:  python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import junior_ollama as jo  # noqa: E402


class TestClean(unittest.TestCase):
    def test_plain_code_unchanged(self):
        self.assertEqual(jo.clean("def f():\n    return 1"), "def f():\n    return 1")

    def test_strips_gemma_thought_block(self):
        raw = "<|channel>thought\nlet me reason about this<channel|>def f():\n    return 1"
        self.assertEqual(jo.clean(raw), "def f():\n    return 1")

    def test_strips_empty_thought_block(self):
        # thinking disabled still emits the tags with an empty thought
        raw = "<|channel>thought\n<channel|>def f():\n    return 1"
        self.assertEqual(jo.clean(raw), "def f():\n    return 1")

    def test_strips_fenced_block_with_language(self):
        self.assertEqual(jo.clean("```python\ndef f():\n    return 1\n```"), "def f():\n    return 1")

    def test_strips_fenced_block_no_language(self):
        self.assertEqual(jo.clean("```\ndef f():\n    return 1\n```"), "def f():\n    return 1")

    def test_strips_thought_then_fence_together(self):
        raw = "<|channel>thought\nreasoning<channel|>```python\ndef f():\n    return 1\n```"
        self.assertEqual(jo.clean(raw), "def f():\n    return 1")

    def test_trims_surrounding_whitespace(self):
        self.assertEqual(jo.clean("\n\n  def f(): pass  \n\n"), "def f(): pass")


class TestResolveModel(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.get("JUNIOR_MODEL")

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("JUNIOR_MODEL", None)
        else:
            os.environ["JUNIOR_MODEL"] = self._saved

    def test_env_override_wins_without_network(self):
        # With JUNIOR_MODEL set, resolve_model must NOT touch the network.
        os.environ["JUNIOR_MODEL"] = "some-model:latest"
        self.assertEqual(jo.resolve_model(), "some-model:latest")


class TestHost(unittest.TestCase):
    def test_default_host(self):
        saved = os.environ.pop("OLLAMA_HOST", None)
        try:
            self.assertEqual(jo.host(), "http://localhost:11434")
        finally:
            if saved is not None:
                os.environ["OLLAMA_HOST"] = saved

    def test_host_trailing_slash_stripped(self):
        saved = os.environ.get("OLLAMA_HOST")
        os.environ["OLLAMA_HOST"] = "http://example:1234/"
        try:
            self.assertEqual(jo.host(), "http://example:1234")
        finally:
            if saved is None:
                os.environ.pop("OLLAMA_HOST", None)
            else:
                os.environ["OLLAMA_HOST"] = saved


if __name__ == "__main__":
    unittest.main()
