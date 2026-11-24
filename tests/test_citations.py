"""In-process tests of citation resolution (scripts/kbengine/citations.py, #252).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Every case runs with an empty environment and a throwaway HOME holding its own registry and a
kb/ folder of two libraries, alpha (the one graded) and beta.
"""
import os, pathlib, subprocess, tempfile, unittest
from unittest import mock

from kbengine import citations


def make_library(root: pathlib.Path, name: str):
    root.mkdir(parents=True)
    (root / "INDEX.md").write_text(f"---\ndomain: {name}\n---\n# {name}\n")
    (root / "widgets.md").write_text("# Widgets\n")
    return root


class Citations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name).resolve()
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home)}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        citations.installed.cache_clear()
        self.addCleanup(citations.installed.cache_clear)
        self.alpha = make_library(self.home / "kb" / "alpha", "alpha")
        self.beta = make_library(self.home / "kb" / "beta", "beta")
        reg = self.home / ".config" / "ai-kb" / "libraries"
        reg.parent.mkdir(parents=True)
        for name, path in (("alpha", self.alpha), ("beta", self.beta)):
            subprocess.run(["git", "config", "--file", str(reg), f"library.{name}.path", str(path)], check=True)

    def test_installed_is_the_registered_libraries_by_name(self):
        self.assertEqual(citations.installed(), {"alpha": self.alpha, "beta": self.beta})

    def test_declared_is_the_name_a_library_gives_itself(self):
        self.assertEqual(citations.declared(self.alpha), "alpha")
        self.assertIsNone(citations.declared(self.home))

    def test_library_root_prefers_the_library_graded_then_the_registry(self):
        self.assertEqual(citations.library_root(self.alpha, "alpha"), self.alpha)
        self.assertEqual(citations.library_root(self.alpha, "beta"), self.beta)
        self.assertIsNone(citations.library_root(self.alpha, "gamma"))

    def test_a_library_not_registered_is_still_found_by_its_declared_name(self):
        loose = make_library(self.home / "loose", "loose")
        self.assertEqual(citations.library_root(loose, "loose"), loose.resolve())

    def test_expected_target_own_library(self):
        self.assertEqual(citations.expected_target(self.alpha, "widgets.md"), (self.alpha, "widgets.md"))

    def test_expected_target_names_another_library(self):
        self.assertEqual(citations.expected_target(self.alpha, "beta:widgets.md"), (self.beta, "widgets.md"))

    def test_expected_target_of_a_library_not_installed_has_no_root(self):
        self.assertEqual(citations.expected_target(self.alpha, "gamma:widgets.md"), (None, "widgets.md"))

    def test_candidates_library_relative(self):
        self.assertIn(self.alpha / "widgets.md", citations.candidates(self.alpha, "widgets.md"))

    def test_candidates_library_prefixed(self):
        self.assertIn(self.alpha / "widgets.md", citations.candidates(self.alpha, "alpha/widgets.md"))

    def test_candidates_kb_rooted(self):
        self.assertIn(self.beta / "widgets.md", citations.candidates(self.alpha, "kb/beta/widgets.md"))

    def test_candidates_absolute(self):
        self.assertIn(self.beta / "widgets.md", citations.candidates(self.alpha, str(self.beta / "widgets.md")))

    def test_each_form_resolves_to_the_expected_file(self):
        for cited in ("widgets.md", "alpha/widgets.md", "kb/alpha/widgets.md", str(self.alpha / "widgets.md")):
            with self.subTest(cited=cited):
                self.assertTrue(citations.resolves_to(self.alpha, "widgets.md", {cited}))

    def test_a_same_named_file_in_another_library_is_not_the_expected_file(self):
        self.assertFalse(citations.resolves_to(self.alpha, "widgets.md", {"beta/widgets.md"}))
        self.assertFalse(citations.resolves_to(self.alpha, "widgets.md", {"kb/beta/widgets.md"}))

    def test_a_cross_root_expected_file_resolves_in_its_own_library(self):
        self.assertTrue(citations.resolves_to(self.alpha, "beta:widgets.md", {"beta/widgets.md"}))
        self.assertFalse(citations.resolves_to(self.alpha, "beta:widgets.md", {"widgets.md"}))

    def test_an_expected_file_in_a_library_not_installed_resolves_to_nothing(self):
        self.assertFalse(citations.resolves_to(self.alpha, "gamma:widgets.md", {"widgets.md"}))

    def test_any_one_citation_among_several_is_enough(self):
        self.assertTrue(citations.resolves_to(self.alpha, "widgets.md", {"INDEX.md", "alpha/widgets.md"}))

    def test_a_suffix_is_not_a_match(self):
        self.assertFalse(citations.resolves_to(self.alpha, "widgets.md", {"old-widgets.md"}))


if __name__ == "__main__":
    unittest.main()
