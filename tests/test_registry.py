"""In-process tests of the registry reader (scripts/kbengine/registry.py, #210).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Every case runs with an empty environment and a throwaway HOME holding its own registry.
"""
import os, pathlib, subprocess, tempfile, unittest
from unittest import mock

from kbengine import registry


def make_library(root: pathlib.Path, name: str, contract: str = ""):
    root.mkdir(parents=True)
    (root / "INDEX.md").write_text(f"---\ndomain: {name}\n{contract}---\n# {name}\n")
    return root


class Registry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name)
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home)}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.reg = self.home / ".config" / "ai-kb" / "libraries"

    def register(self, name, path, **fields):
        self.reg.parent.mkdir(parents=True, exist_ok=True)
        for k, v in {"path": path, **fields}.items():
            subprocess.run(["git", "config", "--file", str(self.reg), f"library.{name}.{k}", str(v)], check=True)


class Entries(Registry):
    def test_no_registry_is_no_entries(self):
        self.assertEqual(registry.entries(), [])
        self.assertEqual(registry.installed(), {})
        self.assertEqual(registry.read_only_paths(), set())
        self.assertIsNone(registry.read_only(self.home))

    def test_entries_are_in_name_order_with_their_fields_and_state(self):
        b = make_library(self.home / "b", "bee")
        a = make_library(self.home / "a", "ay")
        self.register("bee", b, origin="https://example.com/bee.git")
        self.register("ay", a, readOnly="true", ref="v1.0")
        self.register("gone", self.home / "nothing")
        self.assertEqual([e["name"] for e in registry.entries()], ["ay", "bee", "gone"])
        ay, bee, gone = registry.entries()
        self.assertEqual((ay["read_only"], ay["ref"], ay["origin"], ay["state"]), (True, "v1.0", "", "ok"))
        self.assertEqual((bee["read_only"], bee["origin"], bee["path"]), (False, "https://example.com/bee.git", b))
        self.assertEqual(gone["state"], "missing")

    def test_states(self):
        (self.home / "empty").mkdir()
        make_library(self.home / "other", "different")
        make_library(self.home / "future", "future", 'kb_contract: "99.0"\n')
        self.register("empty", self.home / "empty")
        self.register("other", self.home / "other")
        self.register("future", self.home / "future")
        self.assertEqual({e["name"]: e["state"] for e in registry.entries()},
                         {"empty": "not-a-library", "other": "name-mismatch", "future": "unsupported-contract"})

    def test_an_entry_without_a_path_is_dropped(self):
        self.reg.parent.mkdir(parents=True)
        subprocess.run(["git", "config", "--file", str(self.reg), "library.x.origin", "o"], check=True)
        self.assertEqual(registry.entries(), [])

    def test_installed_is_only_the_ok_ones_resolved(self):
        ok = make_library(self.home / "ok", "ok")
        self.register("ok", ok)
        self.register("gone", self.home / "nothing")
        self.assertEqual(registry.installed(), {"ok": ok.resolve()})

    def test_an_unreadable_registry_raises_from_entries_but_reads_as_no_read_only_entry(self):
        self.reg.parent.mkdir(parents=True)
        self.reg.write_text("[library\n")
        with self.assertRaises(RuntimeError):
            registry.entries()
        with self.assertRaises(RuntimeError):
            registry.read_only_paths()
        self.assertIsNone(registry.read_only(self.home))


class ReadOnly(Registry):
    def test_read_only_finds_the_entry_by_resolved_path(self):
        pub = make_library(self.home / "pub", "pub")
        mine = make_library(self.home / "mine", "mine")
        self.register("pub", pub, readOnly="TRUE", origin="https://example.com/pub.git")
        self.register("mine", mine)
        self.assertEqual(registry.read_only(pub / ".." / "pub")["name"], "pub")
        self.assertIsNone(registry.read_only(mine))
        self.assertEqual(registry.read_only_paths(), {pub.resolve()})

    def test_refusal_names_the_origin_or_the_publisher(self):
        e = {"name": "pub", "path": pathlib.Path("/x/pub"), "origin": "https://example.com/pub.git"}
        self.assertIn("File what you found with https://example.com/pub.git.", registry.refusal("kb-prepare", e))
        self.assertTrue(registry.refusal("kb-prepare", dict(e, origin="")).startswith(
            "kb-prepare: pub is registered read-only on this machine"))
        self.assertIn("with its publisher.", registry.refusal("t", dict(e, origin="")))
        self.assertTrue(registry.refusal("t", e).endswith("kb-library add /x/pub"))


if __name__ == "__main__":
    unittest.main()
