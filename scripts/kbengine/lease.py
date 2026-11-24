"""The lease of every stamp in a library (#250, ADR-0022): the one place that says whether a stamp is
asserted, what lease it is on, whether it is due or stale, and how much of the library is asserted.
Stdlib only.

sweep(tree, *, horizon=None, unasserted_ttl=None)   a Leases for the library `tree` (a factfiles.Tree
                                                    of a library on disk, from factfiles.tree(root)).

The sweep is eager. It takes the library already parsed, so a caller that also reads the fact files for
something else (Attention) parses each once; it runs the assertion lint (kbengine.lint) once over the
whole library, reads the clock (kbengine.clock) once, reads the library's needs-attention.md once through
kbengine.queue, and returns frozen values; nothing is written back into the sections it read. It takes
plain numbers, not a Library: the caller says what the library declares (kb-verify and Attention read
INDEX.md; a test passes numbers). It takes no queue records: the library's queue is read here, so no
caller can pass a stale list or re-derive the rule from one.

    Leases.stamps      every stamp of the fact files, in file and line order.
    Leases.rechecks    those with a Recheck:, oldest first, however fresh (kb-verify --all).
    Leases.due         the rechecks past their lease, oldest first, uncapped, attended included.
    Leases.stale       the stamps past their lease with no Recheck:, in file order.
    Leases.coverage    Coverage(asserted, sourced): see below.
    Leases.weak        the WEAK warnings kb-verify prints; outside: the OUTSIDE ones.

    Stamp              file, heading, line (0-based, of the Verified: line), date, by, method, cmd (the
                       Recheck: command or None), attended, lint (the kinds that demote it, a tuple:
                       the lint's, then "failed-recheck"), asserted, age (days), lease (days),
                       lease_label, due.

An asserted stamp is a passing Recheck:, attended or not, whoever wrote it. "Passing" means two things and
no more: the lint does not flag the assertion, and the library's needs-attention.md holds no open
stale-recheck record raised against this stamp (ADR-0022 decision 1, #264). A record is raised against a
stamp when its file and section name the stamp's and its `stamp:` equals the stamp's own Verified: content,
"<date> · by: <by> · method: <method>", as kb-verify writes it (by agent, method unknown when the stamp
names none). A record with no `stamp:` (an older one) covers a stamp dated on or before the record's date,
and one whose date cannot be read covers the stamp. So the demotion lasts only until the section is
restamped: a newer stamp, such as an attended kb-verify --apply after a pass, is asserted at once, with the
record still open as the Arbiter's decision. Nothing here closes a record. A stale-recheck-error record (a
timeout, a command that would not run) does not demote, a record naming a file or heading that is not
there matches nothing, and a queue that cannot be read demotes nothing (Attention reports it on its own).
A demoting record adds the kind "failed-recheck" to the lint kinds of each Recheck: stamp it covers; it is
no WEAK or OUTSIDE warning. An asserted stamp's lease is the full horizon; every other stamp's is the short
lease, unasserted_ttl. It is due once its age exceeds its lease (age equal to the lease is not due). The
lease label reads "full horizon", "short lease: <kinds>" or "short lease: no Recheck".

Without a horizon no lease applies: lease is None, due and stale are empty and every stamp's due is
false, but coverage and the lint still work. A horizon with no usable unasserted_ttl (a whole number
of days, at least 1 and shorter than the horizon) raises ValueError, and an unreadable fact file raises
what reading it raises; the caller decides what a failure means.

Assertion coverage counts a sourced section (factfiles' in_scope, with a Source: line) once when any
of its stamps is asserted, however old. The budget cap and skipping attended assertions are policy
and stay with the callers (kb-verify, Attention's Rechecks).
"""
import datetime, pathlib
from dataclasses import dataclass
from typing import NamedTuple

from . import clock, lint, queue


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


FAILED = "failed-recheck"    # the kind a stale-recheck record adds to a stamp's lint kinds


def _failed(tree) -> dict:
    """{(library-relative file, heading): [(stamp line, date)]} for each open stale-recheck record in the
    library's needs-attention.md (ADR-0022 decision 1, #264): the stamp the failure was raised against, in
    the form kb-verify writes into `stamp:` (None for an older record with none), and the record's date.
    stale-recheck-error does not count: a timeout or a command that would not run says nothing about the
    claim. A queue that cannot be read demotes nothing: Attention reports an unreadable queue as its own
    item, and the lease of every other stamp is still worth judging."""
    qpath = tree.root and tree.root / "needs-attention.md"
    try:
        text = qpath.read_text(errors="replace") if qpath and qpath.is_file() else ""
    except OSError:
        return {}
    out = {}
    for r in queue.open_findings(text):
        if r.get("category") == "stale-recheck":
            out.setdefault((r.get("file"), r.get("section")), []).append((r.get("stamp"), r.get("date")))
    return out


def _covers(records, row) -> bool:
    """Whether an open record was raised against this stamp: its `stamp:` equals the stamp as kb-verify
    writes it. A record with no `stamp:` falls back to its date: it covers a stamp dated on or before it.
    A date that cannot be read covers the stamp."""
    mine = f"{row['date']} · by: {row['by']} · method: {row['method']}"
    for stamp, date in records:
        if stamp:
            if stamp == mine:
                return True
            continue
        try:
            if datetime.date.fromisoformat(date) >= row["date"]:
                return True
        except (TypeError, ValueError):
            return True
    return False


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
    failed = _failed(tree)
    found = lint.assess(tree.root, [r for _, rows in parsed for r in rows if r["cmd"]])

    stamps, hit, sourced = [], 0, 0
    for sec, rows in parsed:
        made = []
        for r in rows:
            kinds = tuple(found.findings.get((r["file"], r["line"]), ()))
            if failed and r["cmd"] and _covers(failed.get((r["file"].relative_to(tree.root).as_posix(), r["heading"]), ()), r):
                kinds += (FAILED,)
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
