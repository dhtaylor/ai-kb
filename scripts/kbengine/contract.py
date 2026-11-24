"""The contract versions (CONVENTIONS §14, ADR-0016): which this engine knows, what a library's
declared `kb_contract:` means against them, and how a version is written. check-kb, kb-due,
kb-report and kb-libraries read a library's contract through this, so a version means one thing in
all of them (#203). Stdlib only.

known_contracts()           {(major, minor): what it adds} for every version §14 lists.
contract_version(declared)  a declared `kb_contract:` as (major, minor); ValueError if malformed.
contract_status(declared)   (state, version, newest, newer) for a declared `kb_contract:`.
supported_majors()          the majors this engine serves, as "2.x and 1.x" for a message.
rules_version(status)       the version whose rules a library is checked by, from its contract_status.
fmt(version)                (2, 6) as "2.6".

The engine is the one these files sit in (scripts/kbengine/ is two levels below it), so a fixture
that copies scripts/ and CONVENTIONS.md into a fake engine reads the fake's §14. §14 is read once
per process and engine.
"""
import functools, pathlib, re

ENGINE = pathlib.Path(__file__).resolve().parents[2]

CONTRACT_SECTION = re.compile(r"^## \d+\. Contract versions\n(.*?)(?=^## |\Z)", re.M | re.S)
CONTRACT_HEADING = re.compile(r"^### (0|[1-9]\d*)\.(0|[1-9]\d*)\s*$")


@functools.lru_cache(maxsize=None)
def _known(engine: pathlib.Path) -> dict:
    m = CONTRACT_SECTION.search((engine / "CONVENTIONS.md").read_text(errors="replace"))
    known, cur, para = {}, None, []
    for line in (m.group(1) if m else "").split("\n"):
        if h := CONTRACT_HEADING.match(line):
            cur, para = (int(h.group(1)), int(h.group(2))), []
            known[cur] = ""
        elif cur and not known[cur]:
            if line.strip():
                para.append(line.strip())
            elif para:
                known[cur] = " ".join(para)
    if cur and not known[cur]:
        known[cur] = " ".join(para)
    if not known:
        raise RuntimeError(f"{engine / 'CONVENTIONS.md'} lists no contract versions (§14)")
    return known


def known_contracts(engine=None) -> dict:
    """{(major, minor): what it adds} for every contract version this engine knows: the `### X.Y`
    headings of CONVENTIONS §14, each with the first paragraph under it. The spec is the one
    copy, so publishing a version is writing its §14 entry (ADR-0016). Raises RuntimeError if
    §14 lists nothing, OSError if CONVENTIONS.md cannot be read: an engine that cannot name its
    versions cannot gate by them. Callers must not change the dict."""
    return _known(pathlib.Path(engine) if engine else ENGINE)


def contract_version(declared) -> tuple:
    """The contract version a root INDEX.md declares, as (major, minor) (ADR-0016). `declared`
    is the raw text after `kb_contract:`, comment dropped, quotes included. Absent is 2.0: every
    library that predates the field was built to engine v0.2.0's rules, which are contract 2.0.
    Raises ValueError unless it is a quoted MAJOR.MINOR in plain digits. Quoted, because a YAML
    reader turns a bare 2.10 into the number 2.1; plain digits (no leading zero, patch or prefix),
    so "2.01" and "2.1" cannot both name one version."""
    if declared is None:
        return (2, 0)
    value = declared.strip()
    q = re.fullmatch(r'"([^"]*)"|\'([^\']*)\'', value)
    if not q:
        raise ValueError(f"kb_contract: {value} must be quoted, e.g. \"2.0\": a YAML reader turns "
                         f"a bare 2.10 into the number 2.1 (ADR-0016)")
    m = re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)", q.group(1) if q.group(1) is not None else q.group(2))
    if not m:
        raise ValueError(f"kb_contract: {value} must be MAJOR.MINOR, e.g. \"2.0\" (ADR-0016)")
    return (int(m.group(1)), int(m.group(2)))


def _supported(known: dict) -> set:
    newest = max(known)
    return {newest[0], newest[0] - 1} & {k[0] for k in known}


def contract_status(declared, engine=None) -> tuple:
    """(state, version, newest, newer) for a declared kb_contract (ADR-0016). state is current,
    behind (older than the newest known: `newer` lists (version, what it adds) above it), ahead
    (a newer minor of a supported major: checked by the newest rules known) or unsupported (a
    major outside the last two this engine has published). Raises ValueError if malformed."""
    v = contract_version(declared)
    known = known_contracts(engine)
    newest = max(known)
    if v[0] not in _supported(known):
        return "unsupported", v, newest, []
    if v > newest:
        return "ahead", v, newest, []
    newer = [(k, known[k]) for k in sorted(known) if k > v]
    return ("behind" if newer else "current"), v, newest, newer


def supported_majors(engine=None) -> str:
    return " and ".join(f"{m}.x" for m in sorted(_supported(known_contracts(engine))))


def rules_version(status: tuple) -> tuple:
    """The version whose rules check a library, from its contract_status (ADR-0016): the version it
    declares, or the newest the engine knows when it declares one ahead, unsupported or malformed."""
    state, version, newest, _newer = status
    return newest if state in ("ahead", "unsupported", "malformed") else version


def fmt(v: tuple) -> str:
    return f"{v[0]}.{v[1]}"
