"""In-process tests of the golden set (scripts/kbengine/golden.py, #252).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Libraries are built in a temp dir; the registry is a throwaway HOME's, empty, so a record names the
library it is in. check-kb's reachability and markers, which check-golden passes in, are stubs here.
"""
import os, pathlib, tempfile, unittest
from unittest import mock

from kbengine import citations, golden

FACT = "The flag is on."
BODY = (f"# Widgets\n\n## Plain\n\n{FACT}\n\nSource: manual\n\n"
        "## Checked\n\nThe cache holds ten.\n\nSource: manual\nVerified: 2026-11-01 · by: agent · method: manual\n"
        "Recheck: grep -q ten widgets.md\n\n"
        "## Worded\n\nThe port is 80.\n\nSource: manual\nVerified: 2026-11-01 · by: agent · method: manual\n")
RECORDS = f"""- case: positive
  question: "Is the flag on?"
  expected_file: widgets.md
  expected_excerpt: '{FACT}'
  alt_excerpt: it's on
- case: negative
  question: Who owns it?
  expected_excerpt: fact not found
"""


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        home = pathlib.Path(self.tmp.name).resolve()
        patcher = mock.patch.dict(os.environ, {"HOME": str(home)}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        citations.installed.cache_clear()
        self.addCleanup(citations.installed.cache_clear)
        self.root = home / "fx"
        self.root.mkdir()
        (self.root / "INDEX.md").write_text("---\ndomain: fx\n---\n# fx\n")
        (self.root / "widgets.md").write_text(BODY)

    def check(self, **record):
        """(defects, unchecked) of one record, with every file reachable and no section marked."""
        return golden.validate(self.root, record, "fx-golden.md record 1", lambda owner: {
            f.resolve() for f in owner.glob("*.md")}, lambda text: [])


class Records(Fixture):
    def test_a_golden_set_round_trips_through_parse(self):
        (self.root / "fx-golden.md").write_text("---\nname: fx-golden\n---\n# Golden\n\n" + RECORDS)
        records = golden.load(self.root)
        self.assertEqual([r["case"] for r in records], ["positive", "negative"])
        self.assertEqual(records[0]["question"], "Is the flag on?")
        self.assertEqual(records[0]["expected_excerpt"], FACT)
        self.assertEqual(records[0]["alt_excerpt"], ["it's on"])
        self.assertEqual(records[1]["expected_excerpt"], "fact not found")
        self.assertNotIn("expected_file", records[1])

    def test_unquote_reads_a_value_the_way_yaml_does(self):
        self.assertEqual(golden.unquote("'the owner''s call'"), "the owner's call")
        self.assertEqual(golden.unquote('"the \\"on\\" flag"'), 'the "on" flag')
        self.assertEqual(golden.unquote('"a \\q b"'), "a \\q b")        # an escape JSON lacks: kept
        self.assertEqual(golden.unquote('the flag is "on"'), 'the flag is "on"')

    def test_alt_excerpt_repeats(self):
        r = golden.parse("- case: positive\n  alt_excerpt: a\n  alt_excerpt: b\n")
        self.assertEqual(r[0]["alt_excerpt"], ["a", "b"])

    def test_text_outside_a_record_is_not_one(self):
        self.assertEqual(golden.parse("# Golden\n\nquestion: stray\n"), [])

    def test_no_golden_set_is_refused(self):
        with self.assertRaises(golden.NoGoldenSet):
            golden.load(self.root)

    def test_files_finds_each_golden_set(self):
        (self.root / "fx-golden.md").write_text(RECORDS)
        self.assertEqual(golden.files(self.root), [self.root / "fx-golden.md"])

    def test_read_mapping(self):
        (self.root / "t.jsonl").write_text("{}\n")
        m = self.root / "map"
        m.write_text("# comment\n\nQ2|t.jsonl\n")
        self.assertEqual(golden.read_mapping(m, 3), {2: self.root / "t.jsonl"})

    def test_read_mapping_refuses_a_bad_mapping(self):
        (self.root / "t.jsonl").write_text("{}\n")
        m = self.root / "map"
        for text, why in (("Q1 t.jsonl\n", "expected Q<n>|<transcript>"), ("Q9|t.jsonl\n", "not a case"),
                          ("Q1|t.jsonl\nQ1|t.jsonl\n", "mapped twice"), ("Q1|gone.jsonl\n", "not found"),
                          ("# nothing\n", "no cases mapped")):
            with self.subTest(why=why):
                m.write_text(text)
                with self.assertRaisesRegex(ValueError, why):
                    golden.read_mapping(m, 3)
        with self.assertRaisesRegex(ValueError, "is not a file"):
            golden.read_mapping(self.root / "absent", 3)


class Validation(Fixture):
    def test_a_sound_record_has_no_defect(self):
        self.assertEqual(self.check(case="positive", question="q", expected_file="widgets.md",
                                    expected_excerpt=FACT, alt_excerpt=["The flag is on"]), ([], []))

    def test_an_unknown_case_type(self):
        defects, _ = self.check(case="maybe")
        self.assertIn("case 'maybe' is not one of", defects[0])

    def test_a_record_with_no_question(self):
        defects, _ = self.check(case="positive", expected_file="widgets.md", expected_excerpt=FACT)
        self.assertEqual(defects, ["fx-golden.md record 1 [positive]: no question"])

    def test_a_refusal_case_names_no_file_and_needs_its_phrase(self):
        defects, _ = self.check(case="negative", question="q", expected_file="widgets.md")
        self.assertEqual(len(defects), 2)
        self.assertIn("a refusal case must name no file", defects[0])
        self.assertIn("no expected_excerpt (the refusal to produce)", defects[1])

    def test_alt_excerpt_is_not_allowed_on_a_refusal_case(self):
        for case in ("negative", "unresolved"):
            with self.subTest(case=case):
                defects, _ = self.check(case=case, question="q", expected_excerpt="x", alt_excerpt=["y"])
                self.assertIn("alt_excerpt is not allowed on a refusal case", defects[0])

    def test_a_case_that_needs_a_file_and_names_none(self):
        defects, _ = self.check(case="positive", question="q", expected_excerpt=FACT)
        self.assertEqual(defects, ["fx-golden.md record 1 [positive]: no expected_file"])

    def test_a_file_that_does_not_exist(self):
        defects, _ = self.check(case="positive", question="q", expected_file="gone.md", expected_excerpt=FACT)
        self.assertIn("expected_file 'gone.md' does not exist", defects[0])

    def test_a_file_no_router_reaches(self):
        defects, _ = golden.validate(self.root, {"case": "positive", "question": "q", "expected_file": "widgets.md",
                                                 "expected_excerpt": FACT}, "w", lambda owner: set(), lambda t: [])
        self.assertIn("is not reachable from fx/INDEX.md by router links", defects[0])

    def test_no_excerpt(self):
        defects, _ = self.check(case="positive", question="q", expected_file="widgets.md")
        self.assertEqual(defects, ["fx-golden.md record 1 [positive]: no expected_excerpt"])

    def test_an_excerpt_the_file_does_not_hold(self):
        defects, _ = self.check(case="positive", question="q", expected_file="widgets.md", expected_excerpt="The flag is off.")
        self.assertIn("excerpt not found in widgets.md — the oracle tests nothing: 'The flag is off.'", defects[0])

    def test_an_alt_excerpt_is_held_to_the_same_standard(self):
        defects, _ = self.check(case="positive", question="q", expected_file="widgets.md",
                                expected_excerpt=FACT, alt_excerpt=["absent"])
        self.assertIn("alt_excerpt not found in widgets.md", defects[0])

    def test_a_line_break_in_the_file_does_not_hide_an_excerpt(self):
        (self.root / "widgets.md").write_text("# W\n\nThe flag\nis on.\n")
        self.assertEqual(self.check(case="positive", question="q", expected_file="widgets.md", expected_excerpt=FACT), ([], []))

    def test_an_unresolved_case_needs_the_refusal_and_a_conflicted_section(self):
        defects, _ = self.check(case="unresolved", question="q", expected_file="widgets.md", expected_excerpt="x")
        self.assertIn(f"expected_excerpt must be the refusal '{golden.DISPUTED}'", defects[0])
        self.assertIn("has no CONFLICTED section", defects[1])
        (self.root / "widgets.md").write_text(BODY + "\nstatus: CONFLICTED\n")
        self.assertEqual(self.check(case="unresolved", question="q", expected_file="widgets.md",
                                    expected_excerpt=golden.DISPUTED), ([], []))

    def test_an_uncorroborated_case_needs_a_marked_section_holding_the_excerpt(self):
        record = dict(case="uncorroborated", question="q", expected_file="widgets.md", expected_excerpt=FACT)
        reach = lambda owner: {f.resolve() for f in owner.glob("*.md")}
        defects, _ = golden.validate(self.root, record, "w", reach, lambda t: [])
        self.assertIn("has no UNCORROBORATED section", defects[0])
        defects, _ = golden.validate(self.root, record, "w", reach, lambda t: ["Something else."])
        self.assertIn("excerpt is not in a section marked UNCORROBORATED", defects[0])
        self.assertEqual(golden.validate(self.root, record, "w", reach, lambda t: [f"## Plain\n{FACT}"]), ([], []))

    def test_another_library_may_be_named_only_by_a_cross_root_case(self):
        defects, unchecked = self.check(case="positive", question="q", expected_file="gamma:w.md", expected_excerpt="x")
        self.assertIn("names another library — only a cross-root case may", defects[0])
        defects, unchecked = self.check(case="cross-root", question="q", expected_file="gamma:w.md", expected_excerpt="x")
        self.assertEqual(defects, [])
        self.assertIn("library 'gamma' is not installed on this machine", unchecked[0])


class Evidence(Fixture):
    def test_evidence_of_a_section(self):
        self.assertEqual(golden.evidence_of(BODY, "The cache holds ten."), "check")
        self.assertEqual(golden.evidence_of(BODY, "The port is 80."), "word")
        self.assertEqual(golden.evidence_of(BODY, FACT), "unstamped")
        self.assertIsNone(golden.evidence_of(BODY, "No section says this."))

    def test_the_phrases(self):
        self.assertEqual(golden.EVIDENCE, {"check": "carries a check", "word": "someone's word"})

    def test_expected_evidence_the_file_bears_out(self):
        for ev, fact in (("check", "The cache holds ten."), ("word", "The port is 80.")):
            with self.subTest(ev=ev):
                self.assertEqual(self.check(case="positive", question="q", expected_file="widgets.md",
                                            expected_excerpt=fact, expected_evidence=ev), ([], []))

    def test_expected_evidence_the_file_contradicts(self):
        for ev, fact, why in (("word", "The cache holds ten.", "carries a Recheck:"),
                              ("check", "The port is 80.", "has no Recheck:"),
                              ("word", FACT, "has no Verified: stamp")):
            with self.subTest(ev=ev, fact=fact):
                defects, _ = self.check(case="positive", question="q", expected_file="widgets.md",
                                        expected_excerpt=fact, expected_evidence=ev)
                self.assertIn(f"expected_evidence '{ev}' but the section holding the excerpt in widgets.md {why}", defects[0])

    def test_an_unknown_evidence_and_a_case_that_may_not_carry_one(self):
        defects, _ = self.check(case="positive", question="q", expected_file="widgets.md", expected_excerpt=FACT,
                                expected_evidence="asserted")
        self.assertIn("expected_evidence 'asserted' is not one of ['check', 'word']", defects[0])
        defects, _ = self.check(case="cross-root", question="q", expected_file="widgets.md", expected_excerpt=FACT,
                                expected_evidence="word")
        self.assertIn("expected_evidence is for a positive case only", defects[0])


class Grading(Fixture):
    rec = {"case": "positive", "expected_file": "widgets.md", "expected_excerpt": FACT}

    def test_a_grounded_answer_citing_the_file_passes(self):
        v = golden.grade(self.root, self.rec, "widgets.md", f'It says: "{FACT}"')
        self.assertEqual((v.passed, v.grounded, v.cited_ok, v.reasons), (True, True, True, []))

    def test_quote_characters_case_and_spacing_are_not_grounding(self):
        self.assertTrue(golden.grade(self.root, self.rec, "widgets.md", "THE  flag\nis on").passed)

    def test_an_answer_that_paraphrases_fails(self):
        v = golden.grade(self.root, self.rec, "widgets.md", "The flag is enabled.")
        self.assertEqual((v.passed, v.grounded, v.cited_ok, v.reasons), (False, False, True, ["excerpt not in answer"]))

    def test_an_answer_citing_the_wrong_file_fails(self):
        v = golden.grade(self.root, self.rec, "INDEX.md", FACT)
        self.assertEqual((v.passed, v.grounded, v.cited_ok), (False, True, False))
        self.assertEqual(v.reasons, ["cited 'INDEX.md', expected 'widgets.md'"])

    def test_an_answer_citing_nothing_fails(self):
        self.assertEqual(golden.grade(self.root, self.rec, "", FACT).reasons, ["cited '(none)', expected 'widgets.md'"])

    def test_a_refusal_case_passes_by_citing_nothing(self):
        rec = {"case": "negative", "expected_excerpt": "fact not found"}
        self.assertTrue(golden.grade(self.root, rec, "", "Fact not found.").passed)
        self.assertFalse(golden.grade(self.root, rec, "widgets.md", "Fact not found.").passed)

    def test_an_excerpt_gone_from_its_file_is_oracle_rot(self):
        (self.root / "widgets.md").write_text("# W\n\nChanged.\n")
        v = golden.grade(self.root, self.rec, "widgets.md", FACT)
        self.assertEqual(v.reasons, ["excerpt not in the expected file — ORACLE ROT"])
        self.assertFalse(v.passed)      # a grounded, correctly cited answer still fails
        self.assertTrue(v.grounded and v.cited_ok)

    def test_either_alt_excerpt_may_be_quoted(self):
        rec = dict(self.rec, alt_excerpt=["The flag is on"])
        self.assertTrue(golden.grade(self.root, rec, "widgets.md", "the flag is on, yes").passed)

    def test_an_answer_quoting_only_the_alt_excerpt_passes(self):
        (self.root / "widgets.md").write_text(f"# W\n\n{FACT} It is enabled.\n")
        rec = dict(self.rec, alt_excerpt=["It is enabled."])
        v = golden.grade(self.root, rec, "widgets.md", "Yes: it is enabled")
        self.assertEqual((v.passed, v.grounded, v.reasons), (True, True, []))
        self.assertFalse(golden.grade(self.root, self.rec, "widgets.md", "Yes: it is enabled").passed)

    def test_an_uncorroborated_answer_must_lead_with_the_caveat(self):
        rec = dict(self.rec, case="uncorroborated")
        self.assertTrue(golden.grade(self.root, rec, "widgets.md", f"**{golden.LEAD}**: {FACT}").passed)
        v = golden.grade(self.root, rec, "widgets.md", f"{FACT} ({golden.LEAD})")
        self.assertEqual(v.reasons, [f"does not lead with {golden.LEAD!r}"])

    def test_an_answer_states_its_evidence_in_the_words_retrieval_uses(self):
        check = dict(self.rec, expected_evidence="check")
        self.assertTrue(golden.grade(self.root, check, "widgets.md", f"It carries a check. {FACT}").passed)
        self.assertTrue(golden.grade(self.root, check, "widgets.md", f"{FACT} It carries a check.").passed)
        v = golden.grade(self.root, check, "widgets.md", FACT)
        self.assertEqual(v.reasons, ["does not state its evidence as 'carries a check'"])

    def test_someones_word_must_come_before_the_fact(self):
        word = dict(self.rec, expected_evidence="word")
        self.assertTrue(golden.grade(self.root, word, "widgets.md", f"Someone's word: {FACT}").passed)
        v = golden.grade(self.root, word, "widgets.md", f"{FACT} Someone's word.")
        self.assertEqual(v.reasons, ["does not state its evidence as \"someone's word\" before the answer"])

    def test_the_expected_file_may_be_one_of_several_cited(self):
        self.assertTrue(golden.grade(self.root, self.rec, "INDEX.md, widgets.md", FACT).passed)


if __name__ == "__main__":
    unittest.main()
