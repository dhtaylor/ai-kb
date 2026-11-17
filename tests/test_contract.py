"""In-process tests of the contract versions (scripts/kbengine/contract.py, #203).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
§14 is read from a temp CONVENTIONS.md, so the tests do not move when the real one gains a version.
"""
import pathlib, tempfile, unittest

from kbengine import contract

ENGINE = pathlib.Path(__file__).resolve().parent.parent
SECTION = ("# Conventions\n\n## 13. Checks\n\nx\n\n## 14. Contract versions\n\nIntro.\n\n"
           "### 1.0\n\nOne point oh.\nStill the same paragraph.\n\nMore.\n\n"
           "### 2.0\n\nTwo point oh.\n\n### 2.1\n\nTwo point one.\n\n### 2.2\n\nTwo point two.\n\n"
           "## 15. After\n\n### 9.9\n\nNot a contract.\n")


class Engine(unittest.TestCase):
    def engine(self, text=SECTION):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        (pathlib.Path(tmp.name) / "CONVENTIONS.md").write_text(text)
        return pathlib.Path(tmp.name)


class Known(Engine):
    def test_reads_the_headings_of_section_14_and_the_first_paragraph_under_each(self):
        known = contract.known_contracts(self.engine())
        self.assertEqual(list(known), [(1, 0), (2, 0), (2, 1), (2, 2)])
        self.assertEqual(known[(1, 0)], "One point oh. Still the same paragraph.")
        self.assertEqual(known[(2, 2)], "Two point two.")

    def test_a_section_listing_no_version_raises(self):
        with self.assertRaisesRegex(RuntimeError, "lists no contract versions"):
            contract.known_contracts(self.engine("# Conventions\n\n## 14. Contract versions\n\nnone\n"))

    def test_a_missing_conventions_raises_oserror(self):
        with tempfile.TemporaryDirectory() as t, self.assertRaises(OSError):
            contract.known_contracts(t)

    def test_is_read_once_per_engine(self):
        root = self.engine()
        first = contract.known_contracts(root)
        (root / "CONVENTIONS.md").write_text(SECTION + "\n### 2.3\n")   # not in §14: past ## 15
        self.assertIs(contract.known_contracts(root), first)

    def test_the_default_engine_is_the_one_the_package_sits_in(self):
        self.assertEqual(contract.ENGINE, ENGINE)
        self.assertIn(max(contract.known_contracts()), contract.known_contracts())


class Version(unittest.TestCase):
    def test_absent_is_2_0(self):
        self.assertEqual(contract.contract_version(None), (2, 0))

    def test_quoted_major_minor_in_either_quote(self):
        self.assertEqual(contract.contract_version('"2.10"'), (2, 10))
        self.assertEqual(contract.contract_version("'2.6'"), (2, 6))

    def test_bare_is_malformed_and_says_why(self):
        with self.assertRaisesRegex(ValueError, r"kb_contract: 2\.6 must be quoted"):
            contract.contract_version("2.6")

    def test_empty_is_malformed_not_absent(self):
        with self.assertRaises(ValueError):
            contract.contract_version("")

    def test_not_plain_major_minor_is_malformed(self):
        for bad in ('"2.01"', '"2"', '"2.1.1"', '"v2.1"', '"2.x"', '""'):
            with self.subTest(bad), self.assertRaisesRegex(ValueError, "must be MAJOR.MINOR"):
                contract.contract_version(bad)


class Status(Engine):
    def status(self, declared):
        return contract.contract_status(declared, self.engine())

    def test_current(self):
        self.assertEqual(self.status('"2.2"'), ("current", (2, 2), (2, 2), []))

    def test_behind_lists_what_the_newer_versions_add_oldest_first(self):
        state, v, newest, newer = self.status('"2.0"')
        self.assertEqual((state, v, newest), ("behind", (2, 0), (2, 2)))
        self.assertEqual(newer, [((2, 1), "Two point one."), ((2, 2), "Two point two.")])

    def test_absent_is_behind_as_2_0(self):
        self.assertEqual(self.status(None)[:2], ("behind", (2, 0)))

    def test_ahead_is_a_newer_minor_of_a_supported_major(self):
        self.assertEqual(self.status('"2.9"'), ("ahead", (2, 9), (2, 2), []))

    def test_the_last_two_majors_are_supported_and_no_other(self):
        self.assertEqual(self.status('"1.0"')[0], "behind")
        self.assertEqual(self.status('"3.0"'), ("unsupported", (3, 0), (2, 2), []))
        self.assertEqual(self.status('"0.9"')[0], "unsupported")

    def test_a_major_with_no_published_version_is_unsupported(self):
        root = self.engine("## 14. Contract versions\n\n### 1.0\n\na\n\n### 3.0\n\nb\n")
        self.assertEqual(contract.contract_status('"2.0"', root)[0], "unsupported")
        self.assertEqual(contract.contract_status('"1.0"', root)[0], "unsupported")
        self.assertEqual(contract.contract_status('"3.0"', root)[0], "current")

    def test_malformed_raises(self):
        with self.assertRaises(ValueError):
            self.status("2.0")

    def test_supported_majors_names_them_for_a_message(self):
        self.assertEqual(contract.supported_majors(self.engine()), "1.x and 2.x")

    def test_fmt(self):
        self.assertEqual(contract.fmt((2, 10)), "2.10")


if __name__ == "__main__":
    unittest.main()
