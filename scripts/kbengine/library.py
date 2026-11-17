"""A library's root INDEX.md, read once and the same way by every script that needs it: the name,
scope and thresholds it declares, where it links, what contract it is built to (CONVENTIONS §3, §7,
§14). Frontmatter only: a line in the body that looks like a field is prose, not a declaration
(#203). Stdlib only.

library(root)   a Library: what root/INDEX.md declares. Never raises for its content.
parse(block)    the fields of a frontmatter block, and the first line that is not one.
read(text)      the same for a whole file's text (its frontmatter block, if it has one).

One rule reads every value: drop a trailing ` # comment` (only where a space precedes the `#`, and
outside quotes), then one pair of matching surrounding quotes. A field keeps its raw text (comment
dropped, quotes kept) beside its value, for the rules that care how it was written, as check-kb's
"kb_contract must be quoted" does.
"""
import datetime, pathlib, re
from dataclasses import dataclass, field
from typing import NamedTuple

from . import contract

# Stdlib only, deliberately: this runs in every commit hook, on machines with no PyYAML (check-kb
# once imported it and was a traceback on CI). It reads what the contract needs: `key: value` at the
# top level, and under a bare `key:` the indented `child: value` lines and `- item` lines of its block.
KEY = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
CHILD = re.compile(r"^[ \t]+([A-Za-z0-9][\w.-]*):[ \t]*(\S.*?)[ \t]*$")
DEFAULT_BUDGET = 5      # verifier_budget when a library declares none (or 0)
DEFAULT_INTERVAL = 30   # sweep_interval, in days, when a library declares none


# ----------------------------------------------------------------------------- parsing ----
def strip_comment(text: str) -> str:
    """`text` without a trailing ` # comment`, quotes kept. A `#` starts a comment only at the
    start of the value or after a space, and never inside a quoted value."""
    t = text.strip()
    start = 0
    if t[:1] in ("'", '"'):
        end = t.find(t[0], 1)
        start = end + 1 if end != -1 else 0
    if start == 0 and t.startswith("#"):
        return ""
    m = re.search(r"\s#", t[start:])
    return t[:start + m.start()].rstrip() if m else t


def unquote(v: str) -> str:
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'" else v


@dataclass(frozen=True)
class Field:
    """One top-level key. raw: the text after the colon, comment dropped, quotes kept. value: raw
    unquoted. items: the `- x` lines of its block, children: its indented `k: v` lines, each
    value read by the same rule."""
    raw: str
    value: str
    line: int
    items: tuple = ()
    children: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Frontmatter:
    """fields: {key: Field}, a repeated key keeping its last. bad: (line number, line) of the first
    line that is not a key, a comment, blank or nested, or None: check-kb reports it."""
    fields: dict
    bad: object = None

    def get(self, name):
        """The value of `name`, or None when it is not declared."""
        f = self.fields.get(name)
        return f.value if f else None

    def raw(self, name):
        f = self.fields.get(name)
        return f.raw if f else None

    def __contains__(self, name):
        return name in self.fields


def parse(block: str) -> Frontmatter:
    """The fields of a frontmatter block (the text between the two --- lines). It goes on past a
    line it cannot read, so one odd line hides no field, and reports the first such line."""
    fields, bad, cur = {}, None, None       # cur: [key, raw, value, line, items, children] being filled
    def close():
        if cur:
            fields[cur[0]] = Field(cur[1], cur[2], cur[3], tuple(cur[4]), cur[5])
    for n, line in enumerate(block.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        if line[0] in " \t-":
            if cur is None:
                continue
            body = line.strip()
            if body.startswith("-"):
                cur[4].append(unquote(strip_comment(body[1:])))
            elif m := CHILD.match(line):
                cur[5][m.group(1)] = unquote(strip_comment(m.group(2)))
            continue
        m = KEY.match(line)
        close()
        cur = None
        if not m:
            bad = bad or (n, line)
            continue
        raw = strip_comment(m.group(2))
        cur = [m.group(1), raw, unquote(raw), n, [], {}]
        if raw:
            close()
            cur = None
    close()
    return Frontmatter(fields, bad)


def frontmatter_block(text: str):
    """(block, closed) for a file's text: the lines between the opening --- and the closing one,
    or to the end of the file when none closes it. None when the file does not open with ---."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), True
    return "\n".join(lines[1:]), False


def read(text: str) -> Frontmatter:
    """The fields of a whole file's text; none when it has no frontmatter."""
    found = frontmatter_block(text)
    return parse(found[0]) if found else Frontmatter({})


# ---------------------------------------------------------------------------- the library ----
def normalize_term(t: str) -> str:
    t = re.sub(r"[\s_-]+", "-", t.strip().strip("\"'").lower()).strip("-")
    return t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t


class Problem(NamedTuple):
    field: str       # the key the message is about, or "INDEX.md" for the file itself
    message: str


@dataclass
class Library:
    """What a library's root INDEX.md declares, each as a callers use it; None when it does not
    declare it, or declares what cannot be used (`problems` says which).

    name, scope, description  the text of `domain:`, `scope:`, `description:`.
    horizon        freshness_horizon, in days (§7).
    agent_ttl      days an agent stamp stays fresh: agent_ttl:, else a tenth of the horizon, at least
                   1. None without a horizon, or when the declared one is not <N>d and shorter than
                   the horizon (an agent TTL as long as the horizon erases the trust tier between
                   agent and human stamps).
    budget         verifier_budget: how many assertions one kb-verify run executes, 5 by default.
    sweep_interval days a kb-audit sweep stays good for, 30 by default.
    last_swept     the date of the last sweep; None for never or unreadable.
    archived       the text of `archived:`: a read-only archive nothing nudges about (#141).
    links_to       {library: origin} from the `links_to:` block (contract 2.6).
    terms          the normalized `keywords:` and `tags:`.
    contract       (state, version, newest, newer) as contract.contract_status gives it, with state
                   "malformed" and version None for an unreadable kb_contract; None when this
                   engine cannot read its own §14 (an engine defect, not the library's).
    problems       [Problem] for each thing it cannot use: no INDEX.md or frontmatter, an unreadable
                   line, a declared value that is not usable."""
    name: object = None
    scope: object = None
    description: object = None
    horizon: object = None
    agent_ttl: object = None
    budget: int = DEFAULT_BUDGET
    sweep_interval: int = DEFAULT_INTERVAL
    last_swept: object = None
    archived: object = None
    links_to: dict = field(default_factory=dict)
    terms: frozenset = frozenset()
    contract: object = None
    problems: list = field(default_factory=list)

    def problem(self, name: str):
        """The message of the first problem with the key `name`, or None."""
        return next((p.message for p in self.problems if p.field == name), None)


def library(root) -> Library:
    """The Library at `root`. Never raises for its content: a file it cannot read, or a value it
    cannot use, is a None and a problem. Reads the frontmatter and nothing else."""
    lib = Library()
    problems = lib.problems
    try:
        text = (pathlib.Path(root) / "INDEX.md").read_text(errors="replace")
    except OSError:
        problems.append(Problem("INDEX.md", "has no INDEX.md"))
        text = None
    found = frontmatter_block(text) if text is not None else None
    if text is not None and not found:
        problems.append(Problem("INDEX.md", "has no frontmatter"))
    fm = parse(found[0]) if found else Frontmatter({})
    if found and not found[1]:
        problems.append(Problem("INDEX.md", "frontmatter is not closed by a --- line"))
    if fm.bad:
        problems.append(Problem("INDEX.md", f"unparseable frontmatter line {fm.bad[0]}: {fm.bad[1]!r}"))

    lib.name, lib.scope, lib.description = fm.get("domain"), fm.get("scope"), fm.get("description")
    lib.archived = fm.get("archived") or None
    if "freshness_horizon" in fm:
        m = re.match(r"(\d+)d", fm.get("freshness_horizon"))
        lib.horizon = int(m.group(1)) if m else None
        if not m:
            problems.append(Problem("freshness_horizon",
                                    f"freshness_horizon: {fm.get('freshness_horizon')!r} is not <N>d"))
    _agent_ttl(lib, fm, problems)
    if fm.get("verifier_budget") is not None:
        m = re.match(r"\d+", fm.get("verifier_budget"))
        lib.budget = int(m.group()) or DEFAULT_BUDGET if m else DEFAULT_BUDGET
        if not m:
            problems.append(Problem("verifier_budget",
                                    f"verifier_budget: {fm.get('verifier_budget')!r} is not a number"))
    interval = fm.get("sweep_interval")
    if interval is not None:
        if re.fullmatch(r"\S+", interval):    # one word, as `<N>d`; any other is not a declaration
            lib.sweep_interval = int(re.sub(r"\D", "", interval) or DEFAULT_INTERVAL)
        else:
            problems.append(Problem("sweep_interval", f"sweep_interval: {interval!r} is not <N>d"))
    swept = fm.get("last_swept")
    if swept not in (None, "never"):
        try:
            if not re.fullmatch(r"\S+", swept):
                raise ValueError(swept)
            lib.last_swept = datetime.date.fromisoformat(swept)
        except ValueError:
            problems.append(Problem("last_swept", f"last_swept: {swept!r} is not a date or 'never'"))

    lib.links_to = dict(fm.fields["links_to"].children) if "links_to" in fm else {}
    raw = []
    for key in ("keywords", "tags"):
        if key in fm:
            raw += fm.raw(key).strip("[]").split(",") + list(fm.fields[key].items)
    lib.terms = frozenset(t for t in map(normalize_term, raw) if t)

    declared = fm.raw("kb_contract")
    try:
        lib.contract = contract.contract_status(declared)
    except ValueError as e:
        problems.append(Problem("kb_contract", str(e)))
        try:
            lib.contract = ("malformed", None, max(contract.known_contracts()), [])
        except (OSError, RuntimeError):
            pass
    except (OSError, RuntimeError):
        pass
    return lib


def _agent_ttl(lib: Library, fm: Frontmatter, problems: list):
    declared = fm.get("agent_ttl")
    if declared is None:
        lib.agent_ttl = max(1, lib.horizon // 10) if lib.horizon is not None else None
        return
    horizon = lib.horizon or 0
    m = re.fullmatch(r"(\d+)d", declared)
    if not m or not 0 < int(m.group(1)) < horizon:
        problems.append(Problem("agent_ttl", f"agent_ttl: {declared!r} must be <N>d and shorter than "
                                             f"freshness_horizon ({horizon}d), or an agent stamp is "
                                             f"trusted as long as a human one"))
        return
    lib.agent_ttl = int(m.group(1))
