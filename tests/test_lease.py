"""In-process tests of the lease module (kbengine.lease, #250, ADR-0022): which stamps of a library
are asserted, what lease each is on, which are due or stale, and the library's assertion coverage.
Libraries are built in a temp dir and the clock is pinned.

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
"""
import dataclasses, datetime, os, pathlib, subprocess, sys, tempfile, unittest
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

    def queue(self, *records, stamp="same", date=None):
        """needs-attention.md with one record per (category, file, section, status). `stamp` is the
        record's stamp: line ("same" is the stamp section() writes at 20 days, None leaves it out, as an
        older record may); `date` replaces the record's date."""
        body = ""
        for category, file, section_, status in records:
            fields = {"file": file, "section": section_, "assertion": "true", "exit": "exit 1"}
            if stamp is not None:
                fields["stamp"] = f"{ago(20)} · by: agent · method: manual" if stamp == "same" else stamp
            r = queue.render(queue.Finding(category, (file, section_, "true"), fields)).replace('status: "open"', f'status: "{status}"')
            if date:
                r = r.replace(f'date: "{TODAY.isoformat()}"', f'date: "{date}"')
            body += r
        (self.root / "needs-attention.md").write_text(
            "---\nname: needs-attention\n---\n# Needs attention\n\n```yaml\n" + body + "```\n")

    def lib(self):
        self.write("widgets.md", section("Pressure", 20, recheck="true"), section("Other", 20, recheck="true"))

    def test_an_open_stale_recheck_demotes_the_section_to_unasserted(self):
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        got = self.sweep()
        s = self.stamp(got, "Pressure")
        self.assertEqual((s.asserted, s.lease, s.due, s.lint, s.failed, s.lease_label),
                         (False, 9, True, (), True, "short lease: failed-recheck"))
        o = self.stamp(got, "Other")
        self.assertEqual((o.asserted, o.lease, o.due, o.lint, o.failed), (True, 90, False, (), False))
        self.assertEqual(tuple(got.coverage), (1, 2))
        self.assertEqual([x.heading for x in got.due], ["Pressure"])
        self.assertEqual(got.weak, ())     # a failed check is a reason for the lease, not a printed lint warning

    def test_a_section_restamped_since_the_failure_is_asserted_with_the_record_still_open(self):
        # the record was raised against the 20-day-old stamp; the section now carries a 5-day-old one
        self.write("widgets.md", section("Pressure", 5, recheck="true"), section("Other", 20, recheck="true"))
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        got = self.sweep()
        s = self.stamp(got, "Pressure")
        self.assertEqual((s.asserted, s.lease, s.due, s.lint, s.failed, s.lease_label),
                         (True, 90, False, (), False, "full horizon"))
        self.assertEqual(tuple(got.coverage), (2, 2))
        self.assertIn('status: "open"', (self.root / "needs-attention.md").read_text())

    def test_a_record_with_no_stamp_demotes_only_a_stamp_not_newer_than_its_date(self):
        self.lib()      # both stamps are dated 20 days ago
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"), stamp=None)   # dated today
        self.assertEqual(tuple(self.sweep().coverage), (1, 2))
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"), stamp=None, date=ago(20))   # the stamp's own day
        self.assertEqual(tuple(self.sweep().coverage), (1, 2))
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"), stamp=None, date=ago(21))   # before the stamp
        self.assertEqual(tuple(self.sweep().coverage), (2, 2))

    def test_a_record_date_that_cannot_be_read_demotes_nothing(self):
        self.lib()
        for date in ("not a date", "2026-13-45"):
            with self.subTest(date=date):
                self.queue(("stale-recheck", "widgets.md", "Pressure", "open"), stamp=None, date=date)
                self.assertEqual(tuple(self.sweep().coverage), (2, 2))

    def test_the_stamp_is_compared_as_kb_verify_writes_it(self):
        # no by: or method: reads as agent / unknown; kb-verify queues what the sweep reads
        (self.root / "widgets.md").write_text(FM.format(n="widgets") + f"# T\n\n## S\n\nc\n\nSource: m\nVerified: {ago(20)}\nRecheck: true\n")
        self.queue(("stale-recheck", "widgets.md", "S", "open"), stamp=f"{ago(20)} · by: agent · method: unknown")
        self.assertEqual(tuple(self.sweep().coverage), (0, 1))
        self.queue(("stale-recheck", "widgets.md", "S", "open"), stamp=f"{ago(20)} · by: human · method: unknown")
        self.assertEqual(tuple(self.sweep().coverage), (1, 1))

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
        s = self.stamp(self.sweep(), "Flagged")
        self.assertEqual((s.lint, s.failed, s.lease_label), (("short-fragment",), True, "short lease: short-fragment, failed-recheck"))

    def test_an_unreadable_queue_demotes_nothing_and_stops_nothing(self):
        # Attention reports an unreadable queue on its own; it is no reason to stop judging the leases.
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        real = pathlib.Path.read_text

        def deny(path, *a, **k):
            if path.name == "needs-attention.md":
                raise PermissionError("denied")
            return real(path, *a, **k)
        with mock.patch.object(pathlib.Path, "read_text", deny):
            got = self.sweep()
        self.assertEqual((tuple(got.coverage), [s.asserted for s in got.stamps]), ((2, 2), [True, True]))

    def test_without_a_horizon_coverage_still_follows_the_failure(self):
        self.lib()
        self.queue(("stale-recheck", "widgets.md", "Pressure", "open"))
        got = lease.sweep(factfiles.tree(self.root))
        self.assertEqual((tuple(got.coverage), got.due), ((1, 2), ()))


class RoundTrip(Lib):
    """kb-verify writes the record and the sweep reads it back: the one form of a stamp and of a record's
    key, whatever the heading holds (#264)."""

    HEADINGS = ("Pressure", "Heading with `` `` a backtick run ``` inside", "L" + "o" * 250 + "ng heading",
                "Line one\tand a tab")

    def test_a_record_kb_verify_wrote_is_matched_by_the_sweep(self):
        (self.root / "INDEX.md").write_text(
            "---\nname: fx-index\ndomain: fx\nscope: general\nfreshness_horizon: 90d\nverifier_budget: 9\n---\n# fx\n")
        self.write("widgets.md", *(section(h, 20, recheck="false") for h in self.HEADINGS))
        self.write("sub/deep.md", section("Deep", 20, recheck="false"))
        env = {**os.environ, "KB_TODAY": TODAY.isoformat()}
        script = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "kb-verify"
        r = subprocess.run([sys.executable, str(script), str(self.root), "--all", "--yes"], env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(tuple(self.sweep().coverage), (0, len(self.HEADINGS) + 1))
        self.assertEqual(sorted(s.heading for s in self.sweep().stamps if not s.asserted and s.failed),
                         sorted((*self.HEADINGS, "Deep")))


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
