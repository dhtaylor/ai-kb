"""In-process tests of when the session-start nudge is shown (kb-due's schedule, #253): the kb.nudge
setting and today decide, and the words said when the nudge is held back.

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
2026-11-09 is a Monday.
"""
import datetime, os, pathlib, subprocess, tempfile, unittest
from unittest import mock

from kbengine import attention

due = attention.script("kb-due")
MON, TUE = datetime.date(2026, 11, 9), datetime.date(2026, 11, 10)
LATEST = pathlib.Path("/r/2026-W45.md")


class Schedule(unittest.TestCase):
    def test_always_and_the_default_show_the_nudge_with_nothing_to_say(self):
        self.assertEqual(due.schedule("always", MON), due.Schedule(True, "", ""))

    def test_off_holds_it_back_and_says_so_without_claiming_nothing_is_due(self):
        got = due.schedule("off", MON)
        self.assertFalse(got.show)
        self.assertIn("(kb.nudge=off)", got.note)
        self.assertIn("kb-due --nudge reports what is due on demand", got.note)
        self.assertEqual(got.warning, "")

    def test_weekly_shows_on_its_day_in_any_spelling(self):
        for spelling in ("mon", "monday"):
            self.assertEqual(due.schedule(f"weekly:{spelling}", MON), due.Schedule(True, "", ""), spelling)
        self.assertEqual(due.schedule("weekly:thurs", datetime.date(2026, 11, 12)).show, True)
        self.assertEqual(due.schedule("weekly:sun", datetime.date(2026, 11, 15)).show, True)

    def test_weekly_on_another_day_holds_it_back_and_names_the_latest_report(self):
        got = due.schedule("weekly:monday", TUE, LATEST)
        self.assertFalse(got.show)
        self.assertIn("(kb.nudge=weekly:mon) and is not shown today", got.note)      # the day, normalized
        self.assertTrue(got.note.endswith(" Latest kb-report: /r/2026-W45.md"))
        self.assertNotIn("Latest kb-report", due.schedule("weekly:mon", TUE).note)    # none yet: nothing named

    def test_a_word_that_is_not_a_weekday_warns_and_shows_the_nudge(self):
        for setting in ("weekly:someday", "weekly:", "weekly:monday2"):
            got = due.schedule(setting, MON)
            self.assertEqual((got.show, got.note), (True, ""))
            self.assertEqual(got.warning, f"kb.nudge '{setting}' is not a weekday (use weekly:mon .. weekly:sun) — showing the nudge every session.")

    def test_any_other_setting_warns_and_shows_the_nudge(self):
        got = due.schedule("sometimes", MON)
        self.assertEqual((got.show, got.note), (True, ""))
        self.assertEqual(got.warning, "kb.nudge 'sometimes' is not one of always, weekly:<day>, off — showing the nudge every session.")


class Setting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.registry = pathlib.Path(self.tmp.name) / "libraries"
        for patch in (mock.patch.object(due.env, "registry_path", lambda: self.registry),
                      mock.patch.dict(os.environ, {}, clear=False)):
            patch.start()
            self.addCleanup(patch.stop)
        os.environ.pop("KB_NUDGE", None)

    def set_registry(self, value):
        subprocess.run(["git", "config", "--file", str(self.registry), "kb.nudge", value], check=True)

    def test_unset_is_always(self):
        self.assertEqual(due.nudge_setting(), "always")          # no registry file at all
        subprocess.run(["git", "config", "--file", str(self.registry), "kb.migrated", "true"], check=True)
        self.assertEqual(due.nudge_setting(), "always")          # a registry with no kb.nudge

    def test_the_registry_is_read_and_the_environment_wins_even_to_say_always(self):
        self.set_registry("off")
        self.assertEqual(due.nudge_setting(), "off")
        os.environ["KB_NUDGE"] = "always"
        self.assertEqual(due.nudge_setting(), "always")
        os.environ["KB_NUDGE"] = ""                               # empty falls through to the registry
        self.assertEqual(due.nudge_setting(), "off")

    def test_case_and_spaces_do_not_matter(self):
        os.environ["KB_NUDGE"] = " Weekly: Monday "
        self.assertEqual(due.nudge_setting(), "weekly:monday")


class Block(unittest.TestCase):
    def test_what_the_hook_adds_to_the_models_context(self):
        shown, held = due.Schedule(True, "", ""), due.Schedule(False, "off note", "")
        self.assertEqual(due.session_block(shown, None), "")
        self.assertEqual(due.session_block(shown, "lib: x"), f"\n{due.HEADER}\nlib: x")
        self.assertEqual(due.session_block(held, None), "\noff note")
        self.assertEqual(due.session_block(due.Schedule(True, "", "bad"), "lib: x"), f"\nWARNING: bad\n{due.HEADER}\nlib: x")


if __name__ == "__main__":
    unittest.main()
