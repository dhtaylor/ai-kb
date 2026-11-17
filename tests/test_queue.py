"""In-process tests of the needs-attention queue (scripts/kbengine/queue.py, #202).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Libraries are built in a temp dir; the registry is never read (read_only_entry is stubbed).
"""
import pathlib, re, tempfile, unittest
from unittest import mock

from kbengine import queue

ENGINE = pathlib.Path(__file__).resolve().parent.parent
INDEX = ("---\nname: fx-index\ndomain: fx\nscope: general\n---\n# fx\n\n"
         "- [widgets](widgets.md) — what widgets do\n  wrapped onto a second line\n")


class FakeRegistry:
    def __init__(self, entry=None):
        self.entry = entry

    def read_only(self, path):
        return self.entry

    def refusal(self, tool, e):
        return f"{tool}: {e['name']} is registered read-only"


def finding(n="a", **over):
    kw = dict(category="drift", identity=("src", n, "new-" + n),
              fields={"source_id": "src", "field": n, "old": "o", "new": "new-" + n},
              untrusted=frozenset({"old", "new"}))
    kw.update(over)
    return queue.Finding(**kw)


class Library(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "INDEX.md").write_text(INDEX)
        self.queue = self.root / "needs-attention.md"
        patch = mock.patch.object(queue, "read_only_entry", lambda p: (FakeRegistry(), None))
        patch.start()
        self.addCleanup(patch.stop)

    def append(self, *findings, **kw):
        return queue.append(self.root, list(findings), "kb-test", **kw)


class Writing(Library):
    def test_a_new_queue_is_created_with_the_librarys_domain_and_scope(self):
        r = self.append(finding())
        self.assertEqual((r.new, r.skipped, r.error), ([finding().id], [], None))
        text = self.queue.read_text()
        self.assertIn("domain: fx\nscope: general\n", text)
        self.assertTrue(text.endswith("```\n"))
        self.assertEqual(text.count("```yaml\n"), 1)

    def test_record_field_order_is_id_category_status_fields_date(self):
        self.append(finding())
        keys = re.findall(r"^(?:- |  )(\w+):", self.queue.read_text().split("```yaml\n")[1], re.M)
        self.assertEqual(keys, ["id", "category", "status", "source_id", "field", "old", "new", "date"])
        self.assertIn(f'  date: "{queue.TODAY}"', self.queue.read_text())

    def test_a_second_append_splices_into_the_last_fence(self):
        self.append(finding("a"))
        self.append(finding("b"))
        text = self.queue.read_text()
        self.assertEqual(text.count("```yaml\n"), 1)
        self.assertEqual([r["field"] for r in queue.parse_records(text)], ["a", "b"])

    def test_a_queue_without_a_fence_gets_one(self):
        self.queue.write_text("---\nname: needs-attention\n---\n# Needs attention\n")
        self.append(finding())
        self.assertEqual(len(queue.parse_records(self.queue.read_text())), 1)

    def test_a_present_id_is_skipped_in_any_status(self):
        f = finding()
        self.queue.write_text(f"```yaml\n- id: {f.id}\n  category: \"drift\"\n  status: \"acknowledged\"\n```\n")
        before = self.queue.read_text()
        r = self.append(f)
        self.assertEqual((r.new, r.skipped), ([], [f.id]))
        self.assertEqual(self.queue.read_text(), before)

    def test_a_rerun_adds_nothing(self):
        self.append(finding())
        before = self.queue.read_text()
        r = self.append(finding())
        self.assertEqual((r.new, r.skipped), ([], [finding().id]))
        self.assertEqual(self.queue.read_text(), before)

    def test_a_repeat_within_one_call_is_written_once(self):
        r = self.append(finding(), finding())
        self.assertEqual((len(r.new), len(r.skipped)), (1, 1))
        self.assertEqual(len(queue.parse_records(self.queue.read_text())), 1)

    def test_dry_run_reports_and_writes_nothing(self):
        r = self.append(finding(), dry_run=True)
        self.assertEqual((r.new, r.error), ([finding().id], None))
        self.assertFalse(self.queue.exists())
        self.assertNotIn("needs-attention", (self.root / "INDEX.md").read_text())

    def test_the_id_is_sha1_of_the_category_and_identity_parts(self):
        import hashlib
        self.assertEqual(finding().id, hashlib.sha1(b"drift|src|a|new-a").hexdigest()[:8])
        self.assertEqual(queue.Finding("c", ("x", None), {}).id, hashlib.sha1(b"c|x|").hexdigest()[:8])

    def test_no_index_is_an_error_and_writes_nothing(self):
        (self.root / "INDEX.md").unlink()
        r = self.append(finding())
        self.assertIn("has no INDEX.md", r.error)
        self.assertFalse(self.queue.exists())

    def test_domain_and_scope_are_read_from_the_frontmatter_only(self):       # #203
        (self.root / "INDEX.md").write_text("---\nname: fx-index\n---\n# fx\n\ndomain: body\nscope: general\n")
        self.assertEqual(queue.library_domain_scope(self.root),
                         (None, None, f"{self.root / 'INDEX.md'} has no domain:/scope: in its frontmatter"))
        r = self.append(finding())
        self.assertIn("has no domain:/scope: in its frontmatter", r.error)
        self.assertFalse(self.queue.exists())

    def test_a_quoted_domain_with_a_trailing_comment_reads_as_the_value(self):    # #203
        (self.root / "INDEX.md").write_text("---\ndomain: \"fx\"  # name\nscope: 'general' # tier\n---\n# fx\n")
        self.assertEqual(queue.library_domain_scope(self.root), ("fx", "general", None))
        self.append(finding())
        self.assertIn("domain: fx\nscope: general\n", self.queue.read_text())

    def test_a_read_only_library_is_refused(self):
        with mock.patch.object(queue, "read_only_entry",
                               lambda p: (FakeRegistry({"name": "fx"}), {"name": "fx"})):
            r = self.append(finding())
        self.assertEqual(r.error, "kb-test: fx is registered read-only")
        self.assertFalse(self.queue.exists())


class Routing(Library):
    LINE = "](needs-attention.md)"

    def test_the_router_line_goes_after_the_last_entry_and_its_continuation(self):
        self.append(finding())
        lines = (self.root / "INDEX.md").read_text().splitlines()
        i = next(n for n, l in enumerate(lines) if self.LINE in l)
        self.assertEqual(lines[i - 1], "  wrapped onto a second line")

    def test_it_is_inserted_once(self):
        self.append(finding("a"))
        self.queue.unlink()
        self.append(finding("b"))
        self.assertEqual((self.root / "INDEX.md").read_text().count(self.LINE), 1)

    def test_an_index_with_no_entries_gets_the_line_appended(self):
        (self.root / "INDEX.md").write_text("---\ndomain: fx\nscope: general\n---\n# fx\n")
        self.append(finding())
        self.assertTrue((self.root / "INDEX.md").read_text().endswith(queue.ROUTER_LINE))


class Escaping(unittest.TestCase):
    def rec(self, value, trusted=False):
        f = queue.Finding("c", ("x",), {"v": value}, frozenset() if trusted else frozenset({"v"}))
        return queue.parse_records(queue.render(f))[0]["v"], queue.render(f)

    def test_newlines_cannot_start_a_line(self):
        got, text = self.rec("a\nb\r\nc\rd")
        self.assertEqual(got, "a b c d")
        self.assertEqual(len([l for l in text.splitlines() if l]), 5)

    def test_a_fence_run_is_defanged_when_untrusted(self):
        got, text = self.rec("x ```` y ``` z")
        self.assertEqual(got, "x ''' y ''' z")
        self.assertEqual(text.count("```"), 0)

    def test_a_fence_run_in_a_trusted_field_is_the_callers_to_own(self):
        self.assertIn("```", self.rec("```", trusted=True)[1])

    def test_untrusted_values_are_truncated(self):
        got, _ = self.rec("x" * 500)
        self.assertEqual(got, "x" * queue.MAX_LEN + " …[truncated]")

    def test_trusted_values_are_not_truncated(self):
        self.assertEqual(self.rec("x" * 500, trusted=True)[0], "x" * 500)

    def test_quotes_and_backslashes_round_trip(self):
        got, _ = self.rec('say "hi" \\ back\\n')
        self.assertEqual(got, 'say "hi" \\ back\\n')

    def test_a_hostile_value_stays_one_record(self):
        hostile = 'x"\n- id: deadbeef\n```\n# Heading\n' + "y" * 300
        f = queue.Finding("c", ("x",), {"v": hostile}, frozenset({"v"}))
        text = "```yaml\n" + queue.render(f) + "```\n"
        self.assertEqual(len(queue.parse_records(text)), 1)
        self.assertEqual(queue.problems(text).unreadable, [])

    def test_none_is_the_empty_string(self):
        self.assertEqual(self.rec(None)[0], "")

    def test_control_characters_become_spaces(self):
        self.assertEqual(self.rec("a\x00b\x1fc")[0], "a b c")


class Reading(unittest.TestCase):
    QUEUE = ("```yaml\n"
             "- id: 11111111\n  category: \"a\"\n  status: \"open\"\n  n: \"first\"\n\n"
             "- id: 22222222\n  category: \"a\"\n  status: \"acknowledged\"\n\n"
             "- id: 11111111\n  category: \"a\"\n  status: \"open\"\n  n: \"second\"\n\n"
             "- id: 33333333\n  category: \"b\"\n  status: \"open\"\n\n"
             "- id: 22222222\n  category: \"a\"\n  status: \"open\"\n"
             "```\n")

    def test_open_findings_are_one_per_id_and_the_first_wins(self):
        got = queue.open_findings(self.QUEUE)
        self.assertEqual([(r["id"], r.get("n")) for r in got],
                         [("11111111", "first"), ("33333333", None), ("22222222", None)])

    def test_a_closed_copy_does_not_hide_an_open_one(self):
        self.assertIn("22222222", [r["id"] for r in queue.open_findings(self.QUEUE)])

    def test_problems_name_duplicate_ids_with_their_lines(self):
        p = queue.problems(self.QUEUE)
        self.assertEqual(p.duplicates, {"11111111": [2, 11], "22222222": [7, 20]})
        self.assertEqual(p.unreadable, [])

    def test_problems_name_a_record_the_parser_skips(self):
        p = queue.problems("```yaml\nid: 55555555\ncategory: bare\n```\n")
        self.assertEqual(p.unreadable, [(2, "id: 55555555")])
        self.assertEqual(p.duplicates, {})

    def test_a_clean_queue_has_no_problems(self):
        p = queue.problems("```yaml\n" + queue.render(finding()) + "```\n")
        self.assertEqual((p.unreadable, p.duplicates), ([], {}))

    def test_a_written_record_round_trips(self):
        f = finding()
        got = queue.parse_records("```yaml\n" + queue.render(f) + "```\n")
        self.assertEqual(got, [{"id": f.id, "category": "drift", "status": "open", "source_id": "src",
                                "field": "a", "old": "o", "new": "new-a", "date": queue.TODAY}])


class AuditSkillExample(unittest.TestCase):
    """kb-audit writes records by hand; the parser must read the example its skill gives."""

    def test_the_skills_example_record_parses(self):
        skill = (ENGINE / "plugins/knowledge-tools/skills/kb-audit/SKILL.md").read_text()
        block = re.search(r"exactly this shape\.\*\*.*?```yaml\n(.*?)```", skill, re.S).group(1)
        self.assertEqual(queue.parse_records("```yaml\n" + block + "```\n"), [{
            "id": "3f2a9c1e", "category": "unstamped fact", "status": "open",
            "file": "widgets.md", "section": "Limits", "severity": "4"}])
        self.assertEqual(queue.problems("```yaml\n" + block + "```\n").unreadable, [])
        self.assertEqual([r["id"] for r in queue.open_findings(block)], ["3f2a9c1e"])


if __name__ == "__main__":
    unittest.main()
