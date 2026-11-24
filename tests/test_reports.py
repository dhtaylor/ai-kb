"""In-process tests of where the weekly reports live and whether the latest one is current
(scripts/kbengine/reports.py, #253).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Reports are written to a temp dir, and their age is set from the file's modification time.
"""
import os, pathlib, tempfile, time, unittest
from unittest import mock

from kbengine import env, reports


class Reports(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = pathlib.Path(self.tmp.name)

    def write(self, name, decisions=None, days_old=1.0):
        p = self.dir / name
        p.write_text("---\nreport: kb-decisions\n" + (f"decisions: {decisions}\n" if decisions is not None else "") + "---\n")
        t = time.time() - days_old * 86400
        os.utime(p, (t, t))
        return p

    def test_where_reports_live(self):
        self.assertEqual(reports.directory(self.dir), self.dir)
        with mock.patch.dict(os.environ, {"KB_REPORTS": "/elsewhere"}):
            self.assertEqual(reports.directory(), pathlib.Path("/elsewhere"))
            self.assertEqual(reports.directory(self.dir), self.dir)       # an explicit folder wins
        self.assertEqual(reports.directory(), env.reports_dir())

    def test_no_folder_and_no_report_is_none(self):
        self.assertIsNone(reports.latest(self.dir / "absent"))
        self.assertIsNone(reports.latest(self.dir))
        self.write("notes.md", 3)                       # not named <year>-W<week>.md
        self.assertIsNone(reports.latest(self.dir))
        self.assertIsNone(reports.current(self.dir))

    def test_the_latest_is_the_newest_week_and_carries_its_decisions_and_age(self):
        self.write("2026-W45.md", 9, days_old=15)
        newest = self.write("2026-W47.md", 4, days_old=2)
        got = reports.latest(self.dir)
        self.assertEqual((got.path, got.decisions), (newest, 4))
        self.assertAlmostEqual(got.age, 2, delta=0.01)
        path, decisions, age = got                       # a Report unpacks, as the tuple it replaces did
        self.assertEqual((path, decisions), (newest, 4))

    def test_current_means_under_eight_days_old_and_listing_decisions(self):
        self.write("2026-W47.md", 4, days_old=2)
        self.assertEqual(reports.current(self.dir).decisions, 4)
        self.write("2026-W47.md", 4, days_old=7.9)
        self.assertIsNotNone(reports.current(self.dir))
        self.write("2026-W47.md", 4, days_old=8.1)
        self.assertIsNone(reports.current(self.dir))                  # old
        self.assertEqual(reports.latest(self.dir).decisions, 4)      # still the latest
        self.write("2026-W47.md", 0, days_old=1)
        self.assertIsNone(reports.current(self.dir))                  # nothing waiting
        self.write("2026-W47.md", None, days_old=1)
        self.assertEqual(reports.latest(self.dir).decisions, 0)      # no decisions: line reads as none
        self.assertIsNone(reports.current(self.dir))

    def test_newest_is_any_md_file_by_name_and_not_the_latest_report(self):
        self.assertIsNone(reports.newest(self.dir / "absent"))
        self.assertIsNone(reports.newest(self.dir))
        self.write("2026-W45.md", 3)
        stray = self.write("notes.md", 0)               # sorts after the week's report, and is no report
        self.assertEqual(reports.newest(self.dir), stray)
        self.assertEqual(reports.latest(self.dir).path.name, "2026-W45.md")

    def test_only_the_newest_report_is_judged(self):
        self.write("2026-W45.md", 9, days_old=1)
        self.write("2026-W46.md", 0, days_old=1)
        self.assertIsNone(reports.current(self.dir))


if __name__ == "__main__":
    unittest.main()
