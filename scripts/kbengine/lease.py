"""The lease of every stamp in a library (#250, ADR-0022): the one place that says whether a stamp is
asserted, what lease it is on, whether it is due or stale, and how much of the library is asserted.
Stdlib only.

sweep(tree, *, horizon=None, unasserted_ttl=None)   a Leases for the library `tree` (a factfiles.Tree
                                                    of a library on disk, from factfiles.tree(root)).

The sweep is eager. It takes the library already parsed, so a caller that also reads the fact files for
something else (Attention) parses each once; it runs the assertion lint (kbengine.lint) once over the
whole library, reads the clock (kbengine.clock) once, and returns frozen values; nothing is written back
into the sections it read. It takes plain numbers, not a Library: the caller says what the library
declares (kb-verify and Attention read INDEX.md; a test passes numbers).

    Leases.stamps      every stamp of the fact files, in file and line order.
    Leases.rechecks    those with a Recheck:, oldest first, however fresh (kb-verify --all).
    Leases.due         the rechecks past their lease, oldest first, uncapped, attended included.
    Leases.stale       the stamps past their lease with no Recheck:, in file order.
    Leases.coverage    Coverage(asserted, sourced): see below.
    Leases.weak        the WEAK warnings kb-verify prints; outside: the OUTSIDE ones.

    Stamp              file, heading, line (0-based, of the Verified: line), date, by, method, cmd (the
                       Recheck: command or None), attended, lint (the lint's kinds, a tuple), asserted,
                       age (days), lease (days), lease_label, due.

An asserted stamp is a passing Recheck: the lint does not flag, attended or not, whoever wrote it. Its
lease is the full horizon; every other stamp's is the short lease, unasserted_ttl. It is due once its
age exceeds its lease (age equal to the lease is not due). The lease label reads "full horizon",
"short lease: <lint kinds>" or "short lease: no Recheck".

Without a horizon no lease applies: lease is None, due and stale are empty and every stamp's due is
false, but coverage and the lint still work. A horizon with no usable unasserted_ttl (a whole number
of days, at least 1 and shorter than the horizon) raises ValueError, and an unreadable file raises
what reading it raises; the caller decides what a failure means.

Assertion coverage counts a sourced section (factfiles' in_scope, with a Source: line) once when any
of its stamps is asserted, however old. The budget cap and skipping attended assertions are policy
and stay with the callers (kb-verify, Attention's Rechecks).
"""
import datetime, pathlib
from dataclasses import dataclass
from typing import NamedTuple

from . import clock, lint


class Coverage(NamedTuple):
    asserted: int        # sourced sections with an asserted stamp
    sourced: int         # served sections with a Source: line


@dataclass(frozen=True)
class Stamp:
    file: pathlib.Path
    heading: str         # "(file)" for a stamp before the first heading
    line: int            # 0-based, of the Verified: line
    date: datetime.date
    by: str              # "agent" when the stamp names none
    method: str          # "unknown" when the stamp names none
    cmd: object          # the Recheck: command, or None
    attended: bool
    lint: tuple          # the lint's finding kinds
    asserted: bool
    age: int             # days
    lease: object        # days, or None without a horizon
    lease_label: object  # None without a horizon
    due: bool


@dataclass(frozen=True)
class Leases:
    stamps: tuple
    rechecks: tuple
    due: tuple
    stale: tuple
    coverage: Coverage
    weak: tuple
    outside: tuple


def _label(cmd, kinds: tuple, asserted: bool) -> str:
    if asserted:
        return "full horizon"
    return "short lease: " + ", ".join(kinds) if cmd else "short lease: no Recheck"


def sweep(tree, *, horizon=None, unasserted_ttl=None) -> Leases:
    if horizon is not None and not (isinstance(unasserted_ttl, int) and 0 < unasserted_ttl < horizon):
        raise ValueError(f"unasserted_ttl: {unasserted_ttl!r} is not a short lease: it must be a whole "
                         f"number of days, at least 1 and shorter than the horizon ({horizon}d)")
    today = clock.today()

    parsed = []       # (section, [stamp as the lint reads it])
    for f in tree.facts:        # a Recheck in a note, a stub or a router is an example, not an assertion
        for sec in f.sections:
            parsed.append((sec, [
                {"file": f.path, "heading": sec.title if sec.level else "(file)", "line": st.line - 1,
                 "date": datetime.date.fromisoformat(st.date), "by": st.by or "agent",
                 "method": st.method or "unknown", "cmd": st.recheck and st.recheck.cmd,
                 "attended": bool(st.recheck and st.recheck.attended)} for st in sec.stamps]))
    found = lint.assess(tree.root, [r for _, rows in parsed for r in rows if r["cmd"]])

    stamps, hit, sourced = [], 0, 0
    for sec, rows in parsed:
        made = []
        for r in rows:
            kinds = tuple(found.findings.get((r["file"], r["line"]), ()))
            asserted = bool(r["cmd"]) and not kinds
            age = (today - r["date"]).days
            days = None if horizon is None else horizon if asserted else unasserted_ttl
            made.append(Stamp(r["file"], r["heading"], r["line"], r["date"], r["by"], r["method"],
                              r["cmd"], r["attended"], kinds, asserted, age, days,
                              None if horizon is None else _label(r["cmd"], kinds, asserted),
                              days is not None and age > days))
        stamps += made
        if sec.sourced:
            sourced += 1
            hit += any(s.asserted for s in made)

    rechecks = tuple(sorted((s for s in stamps if s.cmd), key=lambda s: s.date))
    return Leases(tuple(stamps), rechecks,
                  tuple(s for s in rechecks if s.due), tuple(s for s in stamps if s.due and not s.cmd),
                  Coverage(hit, sourced), found.weak, found.outside)
