"""In-process tests of the reader of a library's root INDEX.md (scripts/kbengine/library.py, #203).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Libraries are built in a temp dir; contract states are read from the engine's own §14.
"""
import datetime, pathlib, tempfile, unittest

from kbengine import contract, library


def fm(**fields):
    return "\n".join(f"{k}: {v}" for k, v in fields.items())


class Value(unittest.TestCase):
    """The one rule: a space-preceded ` #` outside quotes ends the value; then one matching pair of
    quotes comes off. Each row is (written, value, raw)."""
    ROWS = [
        ("plain", "plain", "plain"),
        ("plain  # a note", "plain", "plain"),
        ('"quoted"', "quoted", '"quoted"'),
        ("'quoted'", "quoted", "'quoted'"),
        ('"quoted"  # a note', "quoted", '"quoted"'),
        ("'quoted' # a note", "quoted", "'quoted'"),
        ('"a # b"', "a # b", '"a # b"'),
        ('"a # b" # c', "a # b", '"a # b"'),
        ("a#b", "a#b", "a#b"),
        ('"a"#b', '"a"#b', '"a"#b'),
        ("# only a comment", "", ""),
        ("", "", ""),
        ('"unterminated # note', '"unterminated', '"unterminated'),
        ("""'it''s'""", "it''s", """'it''s'"""),
        ('"a" "b"', 'a" "b', '"a" "b"'),
        ("one # two # three", "one", "one"),
        ('"mismatched\'', "\"mismatched'", "\"mismatched'"),
        ("[a, b]  # tags", "[a, b]", "[a, b]"),
    ]

    def test_table(self):
        for written, value, raw in self.ROWS:
            with self.subTest(written):
                f = library.parse(f"k: {written}").fields["k"]
                self.assertEqual((f.value, f.raw), (value, raw))

    def test_the_value_of_an_undeclared_key_is_none(self):
        self.assertIsNone(library.parse("a: 1").get("b"))
        self.assertEqual(library.parse("a:").get("a"), "")


class Parse(unittest.TestCase):
    def test_top_level_keys_in_any_case_of_spacing(self):
        f = library.parse("name: x\nkb_contract:\"2.6\"\nlast-swept:   never  ")
        self.assertEqual((f.get("name"), f.get("kb_contract"), f.get("last-swept")), ("x", "2.6", "never"))

    def test_blanks_comments_and_nested_lines_are_not_keys(self):
        f = library.parse("# top\n\nname: x\nmetadata:\n  type: index\n  node_type: memory\ntags: [a]\n")
        self.assertEqual(sorted(f.fields), ["metadata", "name", "tags"])
        self.assertIsNone(f.bad)
        self.assertNotIn("type", f)

    def test_a_block_key_collects_its_children_and_items(self):
        f = library.parse("links_to:\n  a: https://x/a.git  # where\n  b-c: 'https://x/b.git'\n"
                          "  not a pair\nkeywords:\n  - one  # first\n  - \"two\"\ntags:\n- a\n- b\nafter: 1\n")
        self.assertEqual(f.fields["links_to"].children,
                         {"a": "https://x/a.git", "b-c": "https://x/b.git"})
        self.assertEqual(f.fields["keywords"].items, ("one", "two"))
        self.assertEqual(f.fields["tags"].items, ("a", "b"))    # a top-level sequence is still its list
        self.assertEqual(f.get("after"), "1")
        self.assertIsNone(f.bad)

    def test_a_block_ends_at_the_next_key_and_a_comment_does_not_end_it(self):
        f = library.parse("tags:\n  - a\n# aside\n  - b\nnext: x\n  - c\n")
        self.assertEqual(f.fields["tags"].items, ("a", "b"))
        self.assertEqual(f.fields["next"].items, ())

    def test_a_key_with_a_value_has_no_block(self):
        self.assertEqual(library.parse("tags: [a]\n  - b\n").fields["tags"].items, ())

    def test_the_first_unparseable_line_is_reported_as_check_kb_does_and_the_rest_still_read(self):
        f = library.parse("name: x\nthis is not a key\n9bad: 1\ndomain: d\n")
        self.assertEqual(f.bad, (2, "this is not a key"))
        self.assertEqual((f.get("name"), f.get("domain")), ("x", "d"))

    def test_a_repeated_key_keeps_its_first(self):
        self.assertEqual(library.parse("a: 1\na: 2").get("a"), "1")

    def test_read_takes_a_whole_files_text_and_only_its_frontmatter(self):
        f = library.read("---\nname: x\n---\nfreshness_horizon: 9d\n")
        self.assertEqual(f.get("name"), "x")
        self.assertNotIn("freshness_horizon", f)
        self.assertEqual(library.read("no frontmatter\nname: x\n").fields, {})

    def test_an_unclosed_frontmatter_still_reads_to_the_end(self):
        self.assertEqual(library.read("---\nname: x\n").get("name"), "x")


class Descriptor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)

    def lib(self, frontmatter, body="# fx\n"):
        (self.root / "INDEX.md").write_text(f"---\n{frontmatter}\n---\n{body}")
        return library.library(self.root)

    def test_a_full_index_reads_every_field(self):
        newest = max(contract.known_contracts())
        lib = self.lib("name: fx-index\ndescription: \"Router for fx\"  # note\ndomain: fx\nscope: product:fx\n"
                       f"freshness_horizon: 90d\nagent_ttl: 30d\nverifier_budget: 7\nsweep_interval: 14d\n"
                       f"kb_contract: \"{contract.fmt(newest)}\"\nlast_swept: 2026-10-16\narchived: moved to fy\n"
                       "links_to:\n  other: https://x/o.git\n"
                       "tags: [Widgets, data_model]\nkeywords:\n  - Fixtures # why\n  - fx")
        self.assertEqual((lib.name, lib.scope, lib.description), ("fx", "product:fx", "Router for fx"))
        self.assertEqual((lib.horizon, lib.agent_ttl, lib.budget, lib.sweep_interval), (90, 30, 7, 14))
        self.assertEqual(lib.last_swept, datetime.date(2026, 10, 16))
        self.assertEqual((lib.archived, lib.links_to), ("moved to fy", {"other": "https://x/o.git"}))
        self.assertEqual(lib.terms, {"widget", "data-model", "fixture", "fx"})
        self.assertEqual(lib.contract[:2], ("current", newest))
        self.assertEqual(lib.problems, [])

    def test_defaults_when_nothing_is_declared(self):
        lib = self.lib("domain: fx")
        self.assertEqual((lib.horizon, lib.agent_ttl, lib.budget, lib.sweep_interval, lib.last_swept),
                         (None, None, library.DEFAULT_BUDGET, library.DEFAULT_INTERVAL, None))
        self.assertEqual((lib.scope, lib.archived, lib.links_to, lib.terms), (None, None, {}, frozenset()))
        self.assertEqual(lib.contract[:2], ("behind", (2, 0)))      # absent reads as 2.0
        self.assertEqual(lib.problems, [])

    def test_the_agent_ttl_is_a_tenth_of_the_horizon_and_at_least_a_day(self):
        self.assertEqual(self.lib("freshness_horizon: 90d").agent_ttl, 9)
        self.assertEqual(self.lib("freshness_horizon: 5d").agent_ttl, 1)

    def test_a_declared_agent_ttl_is_checked_against_the_horizon(self):
        for ttl in ("90d", "100d", "0d", "30", "soon", '""', ""):
            with self.subTest(ttl):
                lib = self.lib(f"freshness_horizon: 90d\nagent_ttl: {ttl}")
                self.assertIsNone(lib.agent_ttl)
                self.assertIn("must be <N>d and shorter than freshness_horizon (90d)", lib.problem("agent_ttl"))
        self.assertEqual(self.lib('freshness_horizon: 90d\nagent_ttl: "30d" # why').agent_ttl, 30)

    def test_an_agent_ttl_with_no_usable_horizon_is_judged_against_zero(self):
        self.assertIn("(0d)", self.lib("agent_ttl: 30d").problem("agent_ttl"))
        self.assertIn("(0d)", self.lib("freshness_horizon: soon\nagent_ttl: 30d").problem("agent_ttl"))

    def test_an_unusable_horizon_is_none_with_a_problem(self):
        lib = self.lib("freshness_horizon: soon")
        self.assertIsNone(lib.horizon)
        self.assertIn("freshness_horizon", lib.problem("freshness_horizon"))
        self.assertEqual(self.lib('freshness_horizon: "90d"  # q').horizon, 90)
        self.assertEqual(self.lib("freshness_horizon: 0d").horizon, 0)

    def test_budget_zero_or_unreadable_is_the_default(self):
        self.assertEqual(self.lib("verifier_budget: 0").budget, library.DEFAULT_BUDGET)
        lib = self.lib("verifier_budget: lots")
        self.assertEqual(lib.budget, library.DEFAULT_BUDGET)
        self.assertIn("verifier_budget", lib.problem("verifier_budget"))

    def test_sweep_interval_is_one_word_of_digits(self):
        self.assertEqual(self.lib("sweep_interval: 7d").sweep_interval, 7)
        self.assertEqual(self.lib("sweep_interval: weekly").sweep_interval, library.DEFAULT_INTERVAL)
        lib = self.lib("sweep_interval: 14 days")
        self.assertEqual(lib.sweep_interval, library.DEFAULT_INTERVAL)
        self.assertIn("sweep_interval", lib.problem("sweep_interval"))

    def test_last_swept_never_and_unreadable_are_both_none_and_only_the_second_a_problem(self):
        self.assertIsNone(self.lib("last_swept: never").last_swept)
        self.assertEqual(self.lib("last_swept: never").problems, [])
        lib = self.lib("last_swept: yesterday")
        self.assertIsNone(lib.last_swept)
        self.assertIn("last_swept", lib.problem("last_swept"))
        self.assertEqual(self.lib('last_swept: "2026-10-16"').last_swept, datetime.date(2026, 10, 16))

    def test_a_malformed_contract_is_a_state_and_a_problem(self):
        lib = self.lib("kb_contract: 2.6")
        self.assertEqual(lib.contract[:2], ("malformed", None))
        self.assertIn("must be quoted", lib.problem("kb_contract"))
        self.assertEqual(self.lib('kb_contract: "3.0"').contract[0], "unsupported")
        self.assertEqual(self.lib('kb_contract: "2.6"  # pinned').problems, [])

    def test_the_quoted_form_is_read_from_the_raw_text_not_the_value(self):
        # kb_contract: 2.6 # note is as unquoted as 2.6: the comment does not make it a string
        self.assertEqual(self.lib("kb_contract: 2.6  # note").contract[:2], ("malformed", None))

    def test_a_quoted_value_with_a_trailing_comment_reads_as_the_value(self):    # the relaxation, #203
        lib = self.lib('domain: "widgets"  # note\nscope: \'general\' # note')
        self.assertEqual((lib.name, lib.scope), ("widgets", "general"))

    def test_only_the_frontmatter_is_read(self):                                  # #203
        lib = self.lib("domain: fx", body="freshness_horizon: 90d\nverifier_budget: 9\narchived: yes\n"
                                          "kb_contract: \"2.6\"\nlinks_to:\n  a: b\n")
        self.assertEqual((lib.horizon, lib.budget, lib.archived, lib.links_to), (None, 5, None, {}))
        self.assertEqual(lib.contract[:2], ("behind", (2, 0)))

    def test_a_missing_or_frontmatterless_index_never_raises(self):
        lib = library.library(self.root)
        self.assertEqual([p.field for p in lib.problems], ["INDEX.md"])
        self.assertIn("no INDEX.md", lib.problems[0].message)
        (self.root / "INDEX.md").write_text("# fx\n\ndomain: fx\n")
        lib = library.library(self.root)
        self.assertIsNone(lib.name)
        self.assertIn("no frontmatter", lib.problems[0].message)

    def test_an_unreadable_line_is_a_problem_and_the_other_fields_read(self):
        lib = self.lib("domain: fx\nwhat is this\nscope: general")
        self.assertEqual((lib.name, lib.scope), ("fx", "general"))
        self.assertIn("unparseable frontmatter line 2: 'what is this'", lib.problems[0].message)

    def test_an_unclosed_frontmatter_is_a_problem(self):
        (self.root / "INDEX.md").write_text("---\ndomain: fx\n")
        lib = library.library(self.root)
        self.assertEqual(lib.name, "fx")
        self.assertIn("not closed", lib.problems[0].message)

    def test_a_binary_index_does_not_raise(self):
        (self.root / "INDEX.md").write_bytes(b"---\ndomain: f\xffx\n---\n")
        self.assertIsInstance(library.library(self.root).name, str)

    def test_terms_normalise_as_the_registry_does(self):
        self.assertEqual(library.normalize_term(' "Data_Models" '), "data-model")
        self.assertEqual(library.normalize_term("class"), "class")
        self.assertEqual(library.normalize_term("gas"), "gas")


if __name__ == "__main__":
    unittest.main()
