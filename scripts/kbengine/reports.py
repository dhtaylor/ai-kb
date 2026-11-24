"""Where the weekly reports live, which is the latest, and whether it is current (ADR-0017, ADR-0021,
#253). kb-report writes them and kb-due names the latest one, and neither knows where they are kept.
Stdlib only.

directory(out)   the reports folder: `out` when given, else kbengine.env's (KB_REPORTS, or the state folder).
latest(out)      the newest report as Report(path, decisions, age), or None when there is none.
current(out)     the latest report when it is worth naming, else None: under CURRENT_DAYS old and listing
                 at least one decision. A report that says nothing is waiting is never named.

`age` is in days, from the file's modification time. Reports are named <ISO year>-W<ISO week>.md, so the
newest sorts last. A report without a `decisions:` line lists none.
"""
import datetime, pathlib, re
from typing import NamedTuple

from . import env

CURRENT_DAYS = 8
DECISIONS = re.compile(r"^decisions: (\d+)$", re.M)


class Report(NamedTuple):
    path: pathlib.Path
    decisions: int
    age: float

    @property
    def current(self) -> bool:
        return bool(self.decisions) and self.age < CURRENT_DAYS


def directory(out=None) -> pathlib.Path:
    return pathlib.Path(out) if out else env.reports_dir()


def latest(out=None):
    root = directory(out)
    found = sorted(root.glob("*-W*.md")) if root.is_dir() else []
    if not found:
        return None
    path = found[-1]
    m = DECISIONS.search(path.read_text(errors="replace"))
    age = (datetime.datetime.now().timestamp() - path.stat().st_mtime) / 86400
    return Report(path, int(m.group(1)) if m else 0, age)


def current(out=None):
    got = latest(out)
    return got if got is not None and got.current else None
