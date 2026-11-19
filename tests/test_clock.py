"""In-process tests of the engine's clock (scripts/kbengine/clock.py, #205).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
"""
import contextlib, datetime, io, os, unittest
from unittest import mock

from kbengine import clock


def with_env(**env):
    return mock.patch.dict(os.environ, env, clear=True)


class Today(unittest.TestCase):
    def test_unset_is_the_real_date(self):
        with with_env():
            self.assertEqual(clock.today(), datetime.date.today())

    def test_empty_is_the_real_date(self):
        with with_env(KB_TODAY=""):
            self.assertEqual(clock.today(), datetime.date.today())

    def test_a_set_value_is_the_date(self):
        with with_env(KB_TODAY="2026-10-01"):
            self.assertEqual(clock.today(), datetime.date(2026, 10, 1))

    def test_it_is_read_at_each_call_not_at_import(self):
        with with_env(KB_TODAY="2026-10-01"):
            first = clock.today()
            os.environ["KB_TODAY"] = "2026-10-02"
            self.assertEqual((first, clock.today()), (datetime.date(2026, 10, 1), datetime.date(2026, 10, 2)))

    def test_malformed_values_raise_and_name_the_variable(self):
        for bad in ("tomorrow", "2026-13-01", "2026-02-30", "20261001", "2026-W40-1", "2026-1-1", " 2026-10-01", "2026-10-01\n"):
            with self.subTest(bad), with_env(KB_TODAY=bad):
                with self.assertRaises(clock.BadToday) as cm:
                    clock.today()
                self.assertIn("KB_TODAY", str(cm.exception))

    def test_a_malformed_value_is_a_value_error(self):
        self.assertTrue(issubclass(clock.BadToday, ValueError))


class Guard(unittest.TestCase):
    def test_passes_the_result_through(self):
        with with_env(KB_TODAY="2026-10-01"):
            self.assertEqual(clock.guard(lambda x: x + 1, 4), 5)

    def test_a_malformed_value_is_exit_2_and_a_message(self):
        err = io.StringIO()
        with with_env(KB_TODAY="soon"), contextlib.redirect_stderr(err):
            self.assertEqual(clock.guard(clock.today), 2)
        self.assertIn("KB_TODAY='soon'", err.getvalue())

    def test_other_errors_are_not_swallowed(self):
        with self.assertRaises(KeyError):
            clock.guard(lambda: {}["x"])


if __name__ == "__main__":
    unittest.main()
