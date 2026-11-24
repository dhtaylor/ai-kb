"""What the engine reads from the environment, declared once, and where its files are (ADR-0021, #205).

VARIABLES   every variable the engine reads: Variable(name, default, effect), in the order listed.
names()     their names. `python3 -m kbengine.env --names` prints one per line, for a test that clears
            exactly this list.
state_dir() packets_dir() reports_dir() config_dir() registry_path() claude_projects()
            the engine's files, from HOME at the time of the call. They are fixed paths: no XDG_*
            variable moves them, because one set only in a terminal splits a hook, cron and a session
            (ADR-0008, ADR-0021). KB_PACKETS and KB_REPORTS are the explicit overrides.
nudge_override(), library_home_override(), claude_binary(), systemctl_binary(), crontab_binary()
            the remaining variables, read in one place.

`python3 -m kbengine.env` prints the table; `--path NAME` prints one resolved location, which the
bash one-liners in kb-session-start and kb-bootstrap are tested against. Stdlib only.
"""
import os, pathlib, shutil, sys
from typing import NamedTuple


class Variable(NamedTuple):
    name: str
    default: str
    effect: str


VARIABLES = (
    Variable("KB_PACKETS", "~/.local/state/ai-kb/packets", "where kb-prepare writes review packets and kb-apply reads them"),
    Variable("KB_REPORTS", "~/.local/state/ai-kb/reports", "where kb-report writes the weekly report, and kb-due looks for it"),
    Variable("KB_LIBRARY_HOME", "kb.libraryHome in the registry, else <engine>/kb", "where kb-library add and import clone new libraries"),
    Variable("KB_NUDGE", "kb.nudge in the registry, else always", "when kb-due --session (the session-start hook) shows the due-work nudge: always, weekly:<day>, off"),
    Variable("KB_TODAY", "the real date", "the date staleness and sweep logic treat as today (YYYY-MM-DD); timestamps stay real"),
    Variable("KB_ENGINE_ROOT", "git config --global kb.engineRoot", "the engine a hook, a recheck or a scaffolded library runs"),
    Variable("KB_CLAUDE", "claude on PATH", "the claude binary kb-prepare and kb-schedule run"),
    Variable("KB_SYSTEMCTL", "systemctl", "the systemctl kb-schedule drives (a stub, in tests)"),
    Variable("KB_CRONTAB", "crontab", "the crontab kb-schedule drives (a stub, in tests)"),
    Variable("CLAUDE_CONFIG_DIR", "~/.claude", "Claude Code's config folder: where kb-telemetry and kb-eval-sample find transcripts, and kb-bootstrap settings.json"),
)


def names() -> list:
    return [v.name for v in VARIABLES]


def _home() -> pathlib.Path:
    return pathlib.Path.home()


def state_dir() -> pathlib.Path:
    return _home() / ".local" / "state" / "ai-kb"


def packets_dir() -> pathlib.Path:
    if os.environ.get("KB_PACKETS"):
        return pathlib.Path(os.environ["KB_PACKETS"])
    return state_dir() / "packets"


def reports_dir() -> pathlib.Path:
    if os.environ.get("KB_REPORTS"):
        return pathlib.Path(os.environ["KB_REPORTS"])
    return state_dir() / "reports"


def nudge_override():
    """$KB_NUDGE, or None when unset or empty: it wins over kb.nudge in the registry."""
    return os.environ.get("KB_NUDGE") or None


def config_dir() -> pathlib.Path:
    return _home() / ".config"


def registry_path() -> pathlib.Path:
    return config_dir() / "ai-kb" / "libraries"


def claude_projects() -> pathlib.Path:
    return pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or _home() / ".claude") / "projects"


def library_home_override():
    """$KB_LIBRARY_HOME, `~` expanded, or None."""
    return pathlib.Path(os.environ["KB_LIBRARY_HOME"]).expanduser() if os.environ.get("KB_LIBRARY_HOME") else None


def claude_binary():
    """$KB_CLAUDE, else claude on PATH, else None."""
    return os.environ.get("KB_CLAUDE") or shutil.which("claude")


def systemctl_binary() -> str:
    return os.environ.get("KB_SYSTEMCTL", "systemctl")


def crontab_binary() -> str:
    return os.environ.get("KB_CRONTAB", "crontab")


PATHS = {"state": state_dir, "packets": packets_dir, "reports": reports_dir, "config": config_dir,
         "registry": registry_path, "claude-projects": claude_projects}   # for --path


def main(argv) -> int:
    if argv == ["--names"]:
        print("\n".join(names()))
    elif len(argv) == 2 and argv[0] == "--path" and argv[1] in PATHS:
        print(PATHS[argv[1]]())
    elif not argv:
        for v in VARIABLES:
            print(f"{v.name}\t{v.default}\t{v.effect}")
    else:
        print("usage: python3 -m kbengine.env [--names | --path " + "|".join(PATHS) + "]", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
