"""In-process tests of the engine's declared environment (scripts/kbengine/env.py, ADR-0021, #205).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Every case runs with an empty environment and a throwaway HOME.
"""
import contextlib, io, os, pathlib, tempfile, unittest
from unittest import mock

from kbengine import env


class Env(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = pathlib.Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.set()

    def set(self, **extra):
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home), **extra}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)


class Declared(Env):
    def test_every_variable_has_a_default_and_an_effect(self):
        for v in env.VARIABLES:
            self.assertTrue(v.name and v.default and v.effect, v)

    def test_names_are_the_declared_ones_once_each(self):
        self.assertEqual(len(set(env.names())), len(env.VARIABLES))
        self.assertEqual(set(env.names()), {
            "KB_PACKETS", "KB_REPORTS", "KB_LIBRARY_HOME", "KB_NUDGE", "KB_TODAY", "KB_ENGINE_ROOT",
            "KB_CLAUDE", "KB_SYSTEMCTL", "KB_CRONTAB", "CLAUDE_CONFIG_DIR"})

    def test_no_xdg_variable_is_declared(self):
        self.assertFalse([n for n in env.names() if n.startswith("XDG_")])

    def test_names_cli_prints_one_per_line(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(env.main(["--names"]), 0)
        self.assertEqual(out.getvalue().split(), env.names())


class Locations(Env):
    def test_defaults_are_under_home(self):
        self.assertEqual(env.state_dir(), self.home / ".local/state/ai-kb")
        self.assertEqual(env.packets_dir(), self.home / ".local/state/ai-kb/packets")
        self.assertEqual(env.reports_dir(), self.home / ".local/state/ai-kb/reports")
        self.assertEqual(env.config_dir(), self.home / ".config")
        self.assertEqual(env.registry_path(), self.home / ".config/ai-kb/libraries")
        self.assertEqual(env.claude_projects(), self.home / ".claude/projects")

    def test_xdg_variables_move_nothing(self):
        self.set(XDG_STATE_HOME="/elsewhere/state", XDG_CONFIG_HOME="/elsewhere/config")
        self.assertEqual(env.state_dir(), self.home / ".local/state/ai-kb")
        self.assertEqual(env.packets_dir(), self.home / ".local/state/ai-kb/packets")
        self.assertEqual(env.reports_dir(), self.home / ".local/state/ai-kb/reports")
        self.assertEqual(env.config_dir(), self.home / ".config")
        self.assertEqual(env.registry_path(), self.home / ".config/ai-kb/libraries")

    def test_packets_and_reports_have_explicit_overrides(self):
        self.set(KB_PACKETS="/p", KB_REPORTS="/r")
        self.assertEqual(env.packets_dir(), pathlib.Path("/p"))
        self.assertEqual(env.reports_dir(), pathlib.Path("/r"))
        self.assertEqual(env.state_dir(), self.home / ".local/state/ai-kb")

    def test_an_empty_override_is_no_override(self):
        self.set(KB_PACKETS="", KB_REPORTS="")
        self.assertEqual(env.packets_dir(), self.home / ".local/state/ai-kb/packets")
        self.assertEqual(env.reports_dir(), self.home / ".local/state/ai-kb/reports")

    def test_home_is_read_at_the_time_of_the_call(self):
        other = self.home / "other"
        self.set(HOME=str(other))
        self.assertEqual(env.state_dir(), other / ".local/state/ai-kb")

    def test_claude_config_dir_moves_the_transcripts(self):
        self.set(CLAUDE_CONFIG_DIR="/cc")
        self.assertEqual(env.claude_projects(), pathlib.Path("/cc/projects"))

    def test_path_cli_prints_a_resolved_location(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(env.main(["--path", "reports"]), 0)
        self.assertEqual(out.getvalue().strip(), str(env.reports_dir()))

    def test_an_unknown_path_name_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(env.main(["--path", "nope"]), 2)


class Others(Env):
    def test_library_home_override_expands_a_tilde(self):
        self.assertIsNone(env.library_home_override())
        self.set(KB_LIBRARY_HOME="~/libs")
        self.assertEqual(env.library_home_override(), self.home / "libs")

    def test_claude_binary_prefers_kb_claude_then_path(self):
        self.set(PATH="/nonexistent")
        self.assertIsNone(env.claude_binary())
        bindir = self.home / "bin"; bindir.mkdir()
        (bindir / "claude").write_text("#!/bin/sh\n"); (bindir / "claude").chmod(0o755)
        self.set(PATH=str(bindir))
        self.assertEqual(env.claude_binary(), str(bindir / "claude"))
        self.set(PATH=str(bindir), KB_CLAUDE="/mine/claude")
        self.assertEqual(env.claude_binary(), "/mine/claude")

    def test_systemctl_and_crontab_default_to_the_system_ones(self):
        self.assertEqual((env.systemctl_binary(), env.crontab_binary()), ("systemctl", "crontab"))
        self.set(KB_SYSTEMCTL="/s", KB_CRONTAB="/c")
        self.assertEqual((env.systemctl_binary(), env.crontab_binary()), ("/s", "/c"))


if __name__ == "__main__":
    unittest.main()
