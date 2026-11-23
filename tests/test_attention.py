"""In-process tests of what needs a person's attention in a library (scripts/kbengine/attention.py, #204).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Libraries are built in a temp dir, dated from today; kb-verify, check-kb and kb-sources are the real
scripts. Each category is asserted on the structured result; nothing is printed.
"""
import datetime, os, pathlib, subprocess, tempfile, unittest
from unittest import mock

from kbengine import attention, clock, contract, library, queue
from kbengine.attention import Failed

NEWEST = contract.fmt(max(contract.known_contracts()))
FM = ("---\nname: widgets\ndescription: x.\nmemory_type: reference\ndomain: fx\nscope: general\n"
      "metadata:\n  type: topic\n  node_type: memory\n  created: 2026-09-22\ntags: [fx]\nkeywords: [fx]\n---\n")


def ago(n):
    """n days before the engine's today (clock.today(): KB_TODAY when set), so a stamp's age is
    what the module under test sees, on the real clock or the suite's frozen one (#217)."""
    return (clock.today() - datetime.timedelta(days=n)).isoformat()


def section(title, age=None, by="agent", recheck=None, attended=False, source=True):
    s = f"\n## {title}\n\nA claim about {title}.\n\n" + ("Source: manual\n" if source else "")
    if age is not None:
        s += f"Verified: {ago(age)} · by: {by} · method: manual\n"
    if recheck:
        s += f"Recheck{' (attended)' if attended else ''}: {recheck}\n"
    return s


def record(i, status="open", category="drift"):
    return f"- id: {i}\n  category: {category}\n  status: {status}\n  file: \"widgets.md\"\n  date: 2026-10-01\n"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name) / "fx"

    def make(self, body="", swept="never", horizon="freshness_horizon: 90d\n", extra="", declared=NEWEST,
             budget=5, queue_text=None, episodic=(), stubs=None):
        self.root.mkdir(exist_ok=True)
        (self.root / "INDEX.md").write_text(
            f"---\nname: fx-index\ndomain: fx\nscope: general\n{horizon}verifier_budget: {budget}\n"
            f"sweep_interval: 30d\nkb_contract: \"{declared}\"\nlast_swept: {swept}\n{extra}---\n# fx\n\n- [widgets](widgets.md) — w\n")
        (self.root / "widgets.md").write_text(FM + "# Widgets\n" + body)
        if queue_text is not None:
            (self.root / "needs-attention.md").write_text("---\nname: needs-attention\n---\n# Q\n\n```yaml\n" + queue_text + "```\n")
        if episodic:
            (self.root / "episodic").mkdir(exist_ok=True)
            for i, text in enumerate(episodic):
                (self.root / "episodic" / f"n{i}.md").write_text(text)
        if stubs:
            (self.root / "sources").mkdir(exist_ok=True)
            for name, text in stubs.items():
                (self.root / "sources" / name).write_text(text)
        return self.root

    def att(self, packets=(), consumed=()):
        return attention.attention(self.root, list(packets), set(consumed))

    def git_commit(self):
        run = lambda *a: subprocess.run(["git", "-C", str(self.root), "-c", "user.email=t@t", "-c", "user.name=t", *a],
                                        capture_output=True, check=True)
        run("init", "-q")
        run("add", "-A")
        run("commit", "-qm", "i")


class Packets(Fixture):
    def test_only_this_librarys_packets_are_kept_and_say_what_they_cover(self):
        self.make()
        mine = (pathlib.Path("p1.md"), {"library_path": str(self.root.resolve()), "packet": "kb-audit"})
        other = (pathlib.Path("p2.md"), {"library_path": "/elsewhere", "packet": "kb-distill"})
        a = self.att([mine, other])
        self.assertEqual(a.packets, [mine])
        self.assertTrue(a.sweep_covered)
        self.assertFalse(a.distill_covered)
        self.assertEqual(self.att([other]).packets, [])


class Sweep(Fixture):
    def test_never_swept_is_due_with_no_age(self):
        self.make()
        self.assertEqual(self.att().sweep, attention.Sweep(True, None, 30))

    def test_a_recent_sweep_is_not_due_and_an_old_one_is(self):
        self.make(swept=ago(3))
        self.assertEqual(self.att().sweep, attention.Sweep(False, 3, 30))
        self.make(swept=ago(31))
        self.assertEqual(self.att().sweep, attention.Sweep(True, 31, 30))

    def test_a_date_it_cannot_read_is_due(self):
        self.make(swept="yesterday")
        self.assertEqual(self.att().sweep, attention.Sweep(True, None, 30))


class Rechecks(Fixture):
    def test_due_list_is_oldest_first_with_the_attended_flag_and_the_budget(self):
        self.make(section("New", 100, recheck="true") + section("Old", 200, recheck="true")
                  + section("Att", 150, recheck="true", attended=True) + section("Fresh", 1, recheck="true"),
                  budget=2)
        r = self.att().rechecks
        self.assertEqual([s["heading"] for s in r.due], ["Old", "Att", "New"])
        self.assertEqual([bool(s["attended"]) for s in r.due], [False, True, False])
        self.assertEqual(r.budget, 2)
        self.assertEqual([s["heading"] for s in r.capped], ["Old", "Att"])
        self.assertEqual([s["heading"] for s in r.attended], ["Att"])

    def test_an_asserted_stamp_stays_fresh_for_the_horizon_whoever_wrote_it(self):
        # ADR-0022: the evidence sets the lease, not by:. 20d is past the short lease (9d of 90d).
        self.make(section("A", 20, recheck="true") + section("H", 20, by="human", recheck="true")
                  + section("Past", 100, recheck="true"))
        self.assertEqual([s["heading"] for s in self.att().rechecks.due], ["Past"])

    def test_an_assertion_the_lint_flags_is_on_the_short_lease_and_says_why(self):
        self.make(section("Weak", 20, recheck="curl -fsSL https://example.com/a | grep -qF 'Widgets'")
                  + section("Att", 20, recheck="true", attended=True))
        due = self.att().rechecks.due
        self.assertEqual([(s["heading"], s["lint"]) for s in due], [("Weak", ["short-fragment"])])

    def test_without_a_horizon_nothing_is_due_and_nothing_failed(self):
        self.make(section("Old", 200, recheck="true"), horizon="")
        a = self.att()
        self.assertEqual(a.rechecks.due, [])
        self.assertEqual(a.stale, [])

    def test_an_agent_ttl_that_cannot_be_used_fails_both_without_raising(self):
        self.make(section("Old", 200, recheck="true"), extra="agent_ttl: 90d\n")
        a = self.att()
        self.assertIsInstance(a.rechecks, Failed)
        self.assertIn("agent_ttl", a.rechecks.reason)
        self.assertEqual(a.rechecks.kind, "ValueError")
        self.assertEqual(a.stale, a.rechecks)

    def test_the_fact_files_are_read_once_for_rechecks_and_stale_together(self):
        self.make(section("Old", 200, recheck="true") + section("NoCmd", 200))
        a = self.att()
        verify = attention.script("kb-verify")
        with mock.patch.object(verify, "due_sections", wraps=verify.due_sections) as due:
            a.rechecks, a.stale
        self.assertEqual(due.call_count, 1)


class Stale(Fixture):
    def test_stamped_past_the_horizon_with_no_recheck(self):
        self.make(section("NoCmd", 200) + section("Cmd", 200, recheck="true") + section("Fresh", 1))
        self.assertEqual([s["heading"] for s in self.att().stale], ["NoCmd"])

    def test_a_human_stamp_buys_no_longer_lease(self):
        # ADR-0022: someone's word is on the short lease (9d of 90d), whoever gave it.
        self.make(section("H", 20, by="human") + section("A", 20) + section("Fresh", 5, by="human"))
        self.assertEqual([s["heading"] for s in self.att().stale], ["H", "A"])


class Queue(Fixture):
    def test_open_records_one_per_id_and_none_without_a_queue_file(self):
        self.make(queue_text=record("aaaaaaaa") + record("aaaaaaaa") + record("bbbbbbbb", status="resolved")
                  + record("cccccccc", category="stale"))
        self.assertEqual([(r["id"], r["category"]) for r in self.att().queue], [("aaaaaaaa", "drift"), ("cccccccc", "stale")])
        self.assertEqual(self.att().queue_unreadable, [])
        (self.root / "needs-attention.md").unlink()
        a = self.att()
        self.assertEqual((a.queue, a.queue_unreadable), ([], []))

    def test_records_the_reader_skips_are_named_by_line(self):
        self.make(queue_text=record("aaaaaaaa") + "id: ffffffff\ncategory: bare\nstatus: open\n")
        bad = self.att().queue_unreadable
        self.assertEqual([line for _n, line in bad], ["id: ffffffff"])

    def test_a_queue_that_cannot_be_read_fails_both_fields(self):
        self.make(queue_text=record("aaaaaaaa"))
        with mock.patch.object(pathlib.Path, "read_text", side_effect=PermissionError("no read")):
            a = self.att()
            self.assertEqual(a.queue, Failed("no read", "PermissionError"))
            self.assertEqual(a.queue_unreadable, a.queue)

    def test_a_queue_the_parser_chokes_on_fails_only_that_field(self):
        self.make(queue_text=record("aaaaaaaa"))
        with mock.patch.object(queue, "open_findings", side_effect=ValueError("boom")):
            a = self.att()
            self.assertEqual(a.queue, Failed("boom", "ValueError"))
            self.assertEqual(a.queue_unreadable, [])


class Episodic(Fixture):
    def test_counts_notes_without_a_distill_heading(self):
        self.make(episodic=["# a\n", "# b\n## Distilled\nx\n", "# c\n## Distillation record\nx\n", "# d\n"])
        (self.root / "episodic" / "INDEX.md").write_text("# not a note\n")
        self.assertEqual(self.att().episodic, 2)

    def test_none_without_an_episodic_folder(self):
        self.make()
        self.assertEqual(self.att().episodic, 0)

    def test_a_note_that_cannot_be_read_fails(self):
        self.make(episodic=["# a\n"])
        with mock.patch.object(pathlib.Path, "read_text", side_effect=OSError("gone")):
            self.assertEqual(self.att().episodic, Failed("gone", "OSError"))


class Unstamped(Fixture):
    BODY = section("Stamped", 1) + section("One", None) + section("Two", None)

    def test_without_git_every_unstamped_source_is_counted(self):
        self.make(self.BODY, swept=ago(1))
        u = self.att().unstamped
        self.assertEqual(u, attention.Unstamped(2, 2, False, None))
        self.assertEqual((u.count, self.att().unstamped_total), (2, 2))

    def test_after_a_committed_sweep_only_the_new_ones_count(self):
        self.make(section("One", None), swept=ago(1))
        self.git_commit()
        (self.root / "widgets.md").write_text((self.root / "widgets.md").read_text() + section("Two", None))
        u = self.att().unstamped
        self.assertEqual((u.total, u.new, u.since_sweep, u.git_error), (2, 1, True, None))
        self.assertEqual(u.count, 1)
        self.assertEqual(self.att().unstamped_total, 2)

    def test_never_swept_counts_them_all(self):
        self.make(self.BODY)
        self.git_commit()
        self.assertEqual(self.att().unstamped, attention.Unstamped(2, 2, False, None))

    def test_a_git_failure_keeps_the_full_count_and_says_why(self):
        self.make(self.BODY, swept=ago(1))
        with mock.patch.object(attention, "_sweep_baseline", side_effect=OSError("no git")):
            u = self.att().unstamped
        self.assertEqual(u, attention.Unstamped(2, 2, False, "no git"))

    def test_none_when_everything_is_stamped(self):
        self.make(section("Stamped", 1), swept=ago(1))
        self.assertEqual(self.att().unstamped, attention.Unstamped(0, 0, False, None))

    def test_check_kb_that_will_not_load_fails_the_fields_that_need_it(self):
        self.make(self.BODY)
        with mock.patch.dict(attention._scripts, {"check-kb": ImportError("gone")}):
            a = self.att()
            for got in (a.unstamped, a.unstamped_total, a.unsourced):
                self.assertEqual(got, Failed("check-kb could not be loaded", "RuntimeError"))


class Unsourced(Fixture):
    def test_sections_with_content_and_no_source_line(self):
        self.make(section("Cited", 1) + section("Bare", 1, source=False) + section("Bare2", None, source=False))
        self.assertEqual(self.att().unsourced, 2)

    def test_none_when_all_are_cited(self):
        self.make(section("Cited", 1))
        self.assertEqual(self.att().unsourced, 0)


class ContractField(Fixture):
    def test_current_behind_ahead_unsupported_and_malformed(self):
        for declared, state in ((NEWEST, "current"), ("2.1", "behind"), ("2.99", "ahead"), ("7.0", "unsupported"),
                                ("x.y", "malformed")):
            self.make(declared=declared)
            got = self.att().contract
            self.assertIsInstance(got, attention.Contract, declared)
            self.assertEqual(got.state, state, declared)
        self.make(declared="2.1")
        got = self.att().contract
        self.assertEqual((got.version, got.newest), ((2, 1), max(contract.known_contracts())))
        self.assertTrue(got.newer)

    def test_an_engine_that_cannot_read_its_own_conventions_fails_the_field(self):
        self.make()
        a = self.att()
        a.lib.contract = None
        with mock.patch.object(contract, "known_contracts", side_effect=RuntimeError("no section 14")):
            self.assertEqual(a.contract, Failed("no section 14", "RuntimeError"))


class ManualStubs(Fixture):
    def test_lists_the_stubs_marked_liveness_manual(self):
        self.make(stubs={"INDEX.md": "# Sources\n", "m.md": "# Source: m\n\n- **URL:** http://x.invalid/\n- **Liveness:** manual\n",
                         "ok.md": "# Source: ok\n\n- **URL:** http://x.invalid/ok\n"})
        self.assertEqual(self.att().manual_stubs, ["sources/m.md"])
        self.make()
        (self.root / "sources" / "m.md").unlink()
        self.assertEqual(self.att().manual_stubs, [])

    def test_a_reader_that_will_not_load_fails_the_field(self):
        self.make()
        with mock.patch.dict(attention._scripts, {"kb-sources": ImportError("gone")}):
            self.assertEqual(self.att().manual_stubs, Failed("gone", "ImportError"))


class Shelving(Fixture):
    def test_archived_and_read_only(self):
        self.make(extra="archived: moved to fy\n")
        a = self.att()
        self.assertEqual(a.archived, "moved to fy")
        self.assertFalse(a.read_only)
        self.assertTrue(attention.shelved(a, set()))                      # archived, not registered
        self.assertFalse(attention.shelved(a, {self.root.resolve()}))     # registered: served whatever it declares
        self.make()
        a = self.att(consumed={self.root.resolve()})
        self.assertTrue(a.read_only and attention.shelved(a, {self.root.resolve()}))
        self.assertIsNone(a.archived)
        self.assertFalse(attention.shelved(self.att(), set()))


class ReadOnce(Fixture):
    def test_index_is_read_once_for_every_field(self):
        self.make(section("Old", 200, recheck="true") + section("NoCmd", 200), queue_text=record("aaaaaaaa"), episodic=["# a\n"])
        with mock.patch.object(library, "library", wraps=library.library) as lib:
            a = self.att()
            for name in ("sweep", "rechecks", "stale", "queue", "queue_unreadable", "episodic", "unstamped",
                         "unstamped_total", "unsourced", "contract", "manual_stubs", "archived"):
                getattr(a, name)
        self.assertEqual(lib.call_count, 1)

    def test_a_field_is_not_worked_out_until_it_is_read(self):
        self.make(section("Old", 200, recheck="true"))
        with mock.patch.object(attention, "_unstamped_keys", side_effect=AssertionError("read early")), \
                mock.patch.object(attention, "script", side_effect=AssertionError("loaded early")):
            a = self.att()
            a.sweep, a.archived, a.contract, a.packets


class Label(unittest.TestCase):
    def test_a_project_knowledge_tree_is_named_after_the_project(self):
        self.assertEqual(attention.label(pathlib.Path("/work/proj/knowledge")), "proj")
        self.assertEqual(attention.label(pathlib.Path("/work/kb/widgets")), "widgets")


if __name__ == "__main__":
    unittest.main()
