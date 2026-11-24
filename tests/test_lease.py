"""In-process tests of the lease module (kbengine.lease, #250, ADR-0022): which stamps of a library
are asserted, what lease each is on, which are due or stale, and the library's assertion coverage.
Libraries are built in a temp dir and the clock is pinned.

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
"""
import dataclasses, datetime, os, pathlib, tempfile, unittest
from unittest import mock

from kbengine import factfiles, lease, queue

FM = ("---\nname: {n}\ndescription: x.\nmemory_type: reference\ndomain: fx\nscope: general\n"
      "metadata:\n  type: topic\n  node_type: memory\n  created: 2026-09-22\ntags: [fx]\nkeywords: [fx]\n---\n")
TODAY = datetime.date(2026, 11, 23)
WEAK = "curl -fsSL https://example.com/a | grep -qF 'Widgets'"
LONG = "Widgets ship with exactly four sprockets each"
REUSED = f"curl -fsSL https://example.com/b | grep -qF '{LONG}'"


def ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


def section(title, age=None, by="agent", recheck=None, attended=False, source=True):
    s = f"\n## {title}\n\nA claim about {title}.\n\n" + ("Source: manual\n" if source else "")
    if age is not None:
        s += f"Verified: {ago(age)} · by: {by} · method: manual\n"
    if recheck:
        s += f"Recheck{' (attended)' if attended else ''}: {recheck}\n"
    return s


class Lib(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name) / "fx"
        (self.root / "sub").mkdir(parents=True)
        (self.root / "INDEX.md").write_text("---\nname: fx-index\n---\n# fx\n")
        clock = mock.patch.dict(os.environ, {"KB_TODAY": TODAY.isoformat()})
        clock.start()
        self.addCleanup(clock.stop)

    def write(self, name, *sections):
        (self.root / name).write_text(FM.format(n=pathlib.Path(name).stem) + "# T\n" + "".join(sections))

    def sweep(self, horizon=90, ttl=9):
        return lease.sweep(factfiles.tree(self.root), horizon=horizon, unasserted_ttl=ttl)

    def stamp(self, got, heading):
        return next(s for s in got.stamps if s.heading == heading)


class Kinds(Lib):
    def test_each_stamp_kind_is_judged_by_its_evidence(self):
        self.write("widgets.md",
                   section("Plain", 20),
                   section("Passing", 20, recheck="true"),
                   section("Flagged", 20, recheck=WEAK),
                   section("Attended", 20, recheck="true", attended=True),
                   section("Human", 20, by="human", recheck="true"),
                   section("Human word", 20, by="human"))
        got = self.sweep()
        self.assertEqual([(s.heading, s.asserted, s.lease, s.due) for s in got.stamps], [
            ("Plain", False, 9, True),
            ("Passing", True, 90, False),
            ("Flagged", False, 9, True),
            ("Attended", True, 90, False),
            ("Human", True, 90, False),
            ("Human word", False, 9, True)])
        self.assertEqual([s.lease_label for s in got.stamps], [
            "short lease: no Recheck", "full horizon", "short lease: short-fragment", "full horizon",
            "full horizon", "short lease: no Recheck"])
        self.assertEqual(self.stamp(got, "Flagged").lint, ("short-fragment",))
        self.assertEqual([s.attended for s in got.stamps], [False, False, False, True, False, False])
        self.assertEqual([s.by for s in got.stamps], ["agent"] * 4 + ["human", "human"])

    def test_a_stamp_carries_where_it_is_and_what_it_says(self):
        self.write("widgets.md", section("Plain", 20, recheck="true"))
        (s,) = self.sweep().stamps
        self.assertEqual((s.file, s.heading, s.date, s.method, s.cmd, s.age),
                         (self.root / "widgets.md", "Plain", TODAY - datetime.timedelta(days=20), "manual", "true", 20))
        lines = (self.root / "widgets.md").read_text().split("\n")
        self.assertTrue(lines[s.line].startswith("Verified:"))     # 0-based
        self.assertEqual(s.lint, ())

    def test_a_stamp_that_names_no_by_or_method_reads_as_an_agents(self):
        (self.root / "widgets.md").write_text(FM.format(n="widgets") + "# T\n\n## S\n\nc\n\nSource: m\nVerified: 2026-11-01\n")
        (s,) = self.sweep().stamps
        self.assertEqual((s.by, s.method), ("agent", "unknown"))

    def test_the_stamp_is_immutable(self):
        self.write("widgets.md", section("Plain", 20))
        (s,) = self.sweep().stamps
        with self.assertRaises(dataclasses.FrozenInstanceError):
            s.due = False
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.sweep().due = ()

    def test_only_fact_files_are_read(self):
        self.write("widgets.md", section("Plain", 20))
        (self.root / "widgets-golden.md").write_text(section("Golden", 20, recheck="true"))
        (self.root / "episodic").mkdir()
        (self.root / "episodic" / "n.md").write_text(section("Note", 20, recheck="true"))
        self.assertEqual([s.heading for s in self.sweep().stamps], ["Plain"])


class Lint(Lib):
    def test_a_fragment_reused_across_two_files_flags_both_stamps(self):
        self.write("widgets.md", section("One", 20, recheck=REUSED))
        self.write("gadgets.md", section("Two", 20, recheck=REUSED))
        got = self.sweep()
        self.assertEqual([(s.heading, s.lint, s.asserted) for s in got.stamps],
                         [("Two", ("reused-fragment",), False), ("One", ("reused-fragment",), False)])
        self.assertEqual(len(got.weak), 1)

    def test_a_path_that_climbs_out_is_flagged_and_warned(self):
        self.write("sub/deep.md", section("Climbs", 20, recheck="../../../scripts/check-kb ."))
        got = self.sweep()
        self.assertEqual(self.stamp(got, "Climbs").lint, ("outside",))
        self.assertEqual(len(got.outside), 1)
        self.assertTrue(got.outside[0].startswith("OUTSIDE sub/deep.md § Climbs"))

    def test_the_warnings_are_the_printed_ones(self):
        self.write("widgets.md", section("Title", 1, recheck=WEAK))
        self.assertEqual(self.sweep().weak,
                         ("WEAK widgets.md § Title: greps 1 word ('Widgets') — a title or identifier passes "
                          "while the page exists",))


class Sections(Lib):
    def test_a_section_with_two_stamps_one_asserted_counts_once(self):
        self.write("widgets.md",
                   "\n## Both\n\nc\n\n"
                   f"Source: a\nVerified: {ago(1)} · by: agent · method: manual\nRecheck: true\n"
                   f"Source: b\nVerified: {ago(1)} · by: agent · method: manual\n"
                   + section("Other", 1))
        got = self.sweep()
        self.assertEqual([s.asserted for s in got.stamps], [True, False, False])
        self.assertEqual(tuple(got.coverage), (1, 2))

    def test_coverage_counts_asserted_sections_over_served_sourced_sections(self):
        self.write("widgets.md",
                   section("A", 1, recheck="true"), section("Att", 1, recheck="true", attended=True),
                   section("Plain", 1), section("Unstamped"), section("NoSource", source=False),
                   section("Flagged", 1, recheck=WEAK),
                   "\n## Disputed\n\nstatus: CONFLICTED\n\nSource: m\n"
                   f"Verified: {ago(1)} · by: agent · method: manual\nRecheck: true\n")
        self.assertEqual(tuple(self.sweep().coverage), (2, 5))

    def test_a_stale_asserted_stamp_still_counts_as_asserted(self):
        self.write("widgets.md", section("Old", 200, recheck="true"))
        got = self.sweep()
        self.assertEqual(tuple(got.coverage), (1, 1))
        self.assertEqual([s.heading for s in got.due], ["Old"])

    def test_a_library_with_nothing_sourced_is_zero_of_zero(self):
        self.assertEqual(tuple(self.sweep().coverage), (0, 0))


class Due(Lib):
    def test_due_is_oldest_first_and_uncapped_with_attended_in_it(self):
        self.write("widgets.md", section("New", 100, recheck="true"), section("Old", 200, recheck="true"),
                   section("Att", 150, recheck="true", attended=True), section("Fresh", 1, recheck="true"),
                   section("NoCmd", 200))
        got = self.sweep()
        self.assertEqual([s.heading for s in got.due], ["Old", "Att", "New"])
        self.assertEqual([s.heading for s in got.rechecks], ["Old", "Att", "New", "Fresh"])
        self.assertEqual([s.heading for s in got.stale], ["NoCmd"])

    def test_stale_is_due_with_no_recheck_in_file_order(self):
        self.write("widgets.md", section("B", 20), section("A", 40, by="human"), section("Cmd", 40, recheck=WEAK),
                   section("Within", 5))
        self.assertEqual([s.heading for s in self.sweep().stale], ["B", "A"])

    def test_age_equal_to_the_lease_is_not_due_and_one_day_more_is(self):
        self.write("widgets.md", section("Short at", 9), section("Short past", 10),
                   section("Full at", 90, recheck="true"), section("Full past", 91, recheck="true"))
        got = self.sweep()
        self.assertEqual([(s.heading, s.age, s.due) for s in got.stamps],
                         [("Short at", 9, False), ("Short past", 10, True), ("Full at", 90, False), ("Full past", 91, True)])

    def test_the_clock_is_read_once_per_sweep(self):
        self.write("widgets.md", section("A", 20), section("B", 20, recheck="true"))
        with mock.patch.object(lease.clock, "today", wraps=lease.clock.today) as today:
            got = self.sweep()
        self.assertEqual(today.call_count, 1)
        self.assertEqual({s.age for s in got.stamps}, {20})


class FailedRecheck(Lib):
    """ADR-0022 decision 1 (#264): an open stale-recheck record for a section makes its stamp
    unasserted until the record is settled. The sweep reads the queue itself."""

    def queue(self, *records):
        """needs-attention.md with one record per (category, file, section, status)."""
        body = ""
        for category, file, section_, status in records:
            f = queue.Finding(category, (file, section_, "true"),
                              {"file": file, "section": section_, "assertion": "true", "stamp": "x", "exit": "exit 1"})
            body += queue.render(f).replace('status: "open"', f'status: "{status}"')
        (self.root / "needs-attention.md").write_text(
            "---\nname: needs-attention\n---\n# Needs attention\n\n```yaml\n" + body + "```\n")

    def lib(self):
        self.write("widgets.md", section("Pressure", 20, recheck="true"), section("Other", 20, recheck="true"))

    def test_an_open_stale_recheck_demotes_the_section_to_unasserted(self):
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        got = self.sweep()
        s = self.stamp(got, "Pressure")
        self.assertEqual((s.asserted, s.lease, s.due, s.lint, s.lease_label),
                         (False, 9, True, ("failed-recheck",), "short lease: failed-recheck"))
        o = self.stamp(got, "Other")
        self.assertEqual((o.asserted, o.lease, o.due, o.lint), (True, 90, False, ()))
        self.assertEqual(tuple(got.coverage), (1, 2))
        self.assertEqual([x.heading for x in got.due], ["Pressure"])
        self.assertEqual(got.weak, ())     # a failed check is a reason for the lease, not a printed lint warning

    def test_a_resolved_record_leaves_the_stamp_asserted(self):
        self.lib()
        for status in ("resolved", "acknowledged"):
            with self.subTest(status=status):
                self.queue(("stale-recheck", "widgets.md", "Pressure", status))
                got = self.sweep()
                self.assertEqual((self.stamp(got, "Pressure").asserted, tuple(got.coverage)), (True, (2, 2)))

    def test_an_open_stale_recheck_error_does_not_demote(self):
        self.lib()
        self.queue(("stale-recheck-error", "widgets.md", "Pressure", "open"))
        got = self.sweep()
        self.assertEqual((self.stamp(got, "Pressure").asserted, tuple(got.coverage)), (True, (2, 2)))

    def test_a_record_naming_a_heading_or_file_that_is_not_there_has_no_effect(self):
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "No such heading", "open"),
                   ("stale-recheck", "gone.md", "Pressure", "open"))
        got = self.sweep()
        self.assertEqual([s.asserted for s in got.stamps], [True, True])
        self.assertEqual(tuple(got.coverage), (2, 2))

    def test_no_queue_file_and_a_queue_with_no_records_are_no_failure(self):
        self.lib()
        self.assertEqual(tuple(self.sweep().coverage), (2, 2))
        self.queue()
        self.assertEqual(tuple(self.sweep().coverage), (2, 2))

    def test_the_demotion_follows_the_file_not_only_the_heading(self):
        self.write("widgets.md", section("Same", 20, recheck="true"))
        self.write("sub/deep.md", section("Same", 20, recheck="true"))
        self.queue(("stale-recheck", "sub/deep.md", "Same", "open"))
        got = self.sweep()
        self.assertEqual(sorted((s.file.name, s.asserted) for s in got.stamps), [("deep.md", False), ("widgets.md", True)])

    def test_a_flagged_assertion_keeps_its_lint_kinds_beside_the_failure(self):
        self.write("widgets.md", section("Flagged", 20, recheck=WEAK))
        self.queue(("stale-recheck", "widgets.md", "Flagged", "open"))
        self.assertEqual(self.stamp(self.sweep(), "Flagged").lint, ("short-fragment", "failed-recheck"))

    def test_without_a_horizon_coverage_still_follows_the_failure(self):
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        got = lease.sweep(factfiles.tree(self.root))
        self.assertEqual((tuple(got.coverage), got.due), ((1, 2), ()))


class Policy(Lib):
    def test_without_a_horizon_nothing_is_due_and_coverage_still_works(self):
        self.write("widgets.md", section("Old", 200, recheck="true"), section("Plain", 200))
        got = lease.sweep(factfiles.tree(self.root))
        self.assertEqual((got.due, got.stale), ((), ()))
        self.assertEqual([s.due for s in got.stamps], [False, False])
        self.assertEqual([s.lease for s in got.stamps], [None, None])
        self.assertEqual(tuple(got.coverage), (1, 2))
        self.assertEqual([s.heading for s in got.rechecks], ["Old"])

    def test_a_horizon_without_a_usable_short_lease_raises(self):
        self.write("widgets.md", section("Old", 200))
        for ttl in (None, 0, 90, 120, "9d"):
            with self.subTest(ttl=ttl), self.assertRaises(ValueError) as e:
                lease.sweep(factfiles.tree(self.root), horizon=90, unasserted_ttl=ttl)
            self.assertIn("unasserted_ttl", str(e.exception))

    def test_a_short_lease_without_a_horizon_is_not_an_error(self):
        self.write("widgets.md", section("Old", 200))
        self.assertEqual(lease.sweep(factfiles.tree(self.root), unasserted_ttl=None).due, ())

    def test_an_unreadable_file_propagates(self):
        self.write("widgets.md", section("Old", 200))
        with mock.patch.object(pathlib.Path, "read_text", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                self.sweep()


class Reads(Lib):
    def test_each_fact_file_is_read_once_per_sweep(self):
        self.write("widgets.md", section("A", 200, recheck=REUSED), section("B", 200))
        self.write("gadgets.md", section("C", 200, recheck=REUSED), section("D", 1, recheck="true"))
        self.write("sub/deep.md", section("E", 200, recheck="../../../x"))
        real, reads = pathlib.Path.read_text, []

        def counting(path, *a, **k):
            reads.append(path)
            return real(path, *a, **k)
        with mock.patch.object(pathlib.Path, "read_text", counting):
            got = self.sweep()
        self.assertEqual(len(got.stamps), 5)
        self.assertEqual(sorted(p.name for p in reads), ["deep.md", "gadgets.md", "widgets.md"])


if __name__ == "__main__":
    unittest.main()
