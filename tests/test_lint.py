"""In-process tests of the assertion lint (kbengine.lint) as structured findings (#235): which
sections the weak-assertion and outside-the-library checks flag, and why, so the lease (ADR-0022) and
assertion coverage can use them. The printed warnings are covered by tests/run-checks.

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
"""
import pathlib, tempfile, unittest

from kbengine import attention, lint

FM = ("---\nname: {n}\ndescription: x.\nmemory_type: reference\ndomain: fx\nscope: general\n"
      "metadata:\n  type: topic\n  node_type: memory\n  created: 2026-09-22\ntags: [fx]\nkeywords: [fx]\n---\n")
LONG = "Widgets ship with exactly four sprockets each"


def section(title, recheck):
    return (f"\n## {title}\n\nA claim about {title}.\n\nSource: manual\n"
            f"Verified: 2026-11-01 · by: agent · method: doc-review\nRecheck: {recheck}\n")


class Findings(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name) / "fx"
        (self.root / "sub").mkdir(parents=True)
        self.v = attention.script("kb-verify")

    def write(self, name, *sections):
        (self.root / name).write_text(FM.format(n=pathlib.Path(name).stem) + "# T\n" + "".join(sections))

    def findings(self):
        found = [s for f in sorted(self.root.rglob("*.md")) for s in self.v.sections(f)]
        got = lint.lint_findings(self.root, [s for s in found if s["cmd"]])
        return {s["heading"]: sorted(got.get((s["file"], s["line"]), [])) for s in found}

    def test_names_each_flagged_section_and_why(self):
        self.write("widgets.md",
                   section("Title grep", "curl -fsSL https://example.com/a | grep -qF 'Widgets'"),
                   section("Shared one", f"curl -fsSL https://example.com/b | grep -qF '{LONG}'"),
                   section("Sound", "curl -fsSL https://example.com/c | grep -qF 'Each gadget weighs two hundred grams'"))
        self.write("gadgets.md",
                   section("Shared two", f"curl -fsSL https://example.com/b | grep -qF '{LONG}'"))
        self.write("sub/deep.md",
                   section("Climbs out", "../../../scripts/check-kb ."))
        self.assertEqual(self.findings(), {
            "Title grep": ["short-fragment"],
            "Shared one": ["reused-fragment"],
            "Shared two": ["reused-fragment"],
            "Sound": [],
            "Climbs out": ["outside"],
        })


if __name__ == "__main__":
    unittest.main()
