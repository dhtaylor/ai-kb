"""The golden set: a library's own answer key, its record format, its rules and its grading (#252,
CONVENTIONS §10). Stdlib only. A record is one `- case: x` block of `key: value` lines in the
library's <domain>-golden.md.

files(lib)                      the golden-set files of a library (sorted).
load(lib)                       the records of the library's golden set. Raises NoGoldenSet.
parse(text)                     records from a golden set's text; unquote(v) reads one value.
read_mapping(mapping, n)        {case number: transcript} from a Q<n>|<transcript> file.
evidence_of(body, excerpt)      what backs the section holding an excerpt: check, word, unstamped, or
                                None. It ignores the lint on purpose (ADR-0022 section 7).
validate(root, r, where, reachable, marked)
                                (defects, unchecked) of one record: case-type rules, alt_excerpt rules,
                                the expected file and its excerpts, expected_evidence.
grade(lib, r, cited, answer)    a Verdict of what an agent answered against one record.
EVIDENCE, DISPUTED, LEAD        the phrases: the evidence words retrieval uses (ADR-0022), the refusal of
                                a CONFLICTED fact, and what an UNCORROBORATED answer must begin with.

validate and grade resolve expected_file through kbengine.citations. Reachability, which needs the
library's routers, and the UNCORROBORATED markers belong to check-kb: check-golden passes them in as
`reachable(owner)` (the set of resolved files a router reaches) and `marked(text)` (the marked
sections), and keeps the library-level checks. It was a pure move out of scripts/check-golden and
scripts/grade-eval, which each parsed the records and loaded the other for the rest: its judgements
and wording are unchanged.
"""
import json, pathlib, re
from dataclasses import dataclass, field

from . import citations, factfiles

VALID_CASES = {"positive", "negative", "unresolved", "cross-root", "uncorroborated"}
DISPUTED = "disputed — not served"   # the refusal of a CONFLICTED fact (CONVENTIONS §10)
LEAD = "uncorroborated — single source"
# expected_evidence -> the words retrieval uses for it (ADR-0022).
EVIDENCE = {"check": "carries a check", "word": "someone's word"}
FIELD = re.compile(r"^(question|expected_file|expected_excerpt|alt_excerpt|expected_evidence):\s*(.*?)\s*$")

ws = lambda s: re.sub(r"\s+", " ", s)


class NoGoldenSet(Exception):
    """The library holds no golden set."""


# ---------------------------------------------------------------------------- records ----
def unquote(v: str) -> str:
    """A record value read the way YAML reads a scalar (#111). '...' loses its quotes and turns ''
    into '; "..." loses its quotes and reads its escapes; a plain value is kept whole, a quote of
    its own included."""
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    if len(v) >= 2 and v[0] == v[-1] == '"':
        try:
            return json.loads(v)
        except ValueError:      # a YAML escape JSON lacks: keep the text between the quotes
            return v[1:-1]
    return v


def parse(text):
    """Records are '- case: x' blocks with key: value lines under them."""
    records, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"^-\s+case:\s*(\S+)", line)
        if m:
            if cur:
                records.append(cur)
            cur = {"case": m.group(1), "_line": raw}
            continue
        if cur is not None:
            kv = FIELD.match(line)
            if kv and kv.group(1) == "alt_excerpt":     # repeatable: a second sentence stating the same fact
                cur.setdefault("alt_excerpt", []).append(unquote(kv.group(2)))
            elif kv:
                cur[kv.group(1)] = unquote(kv.group(2))
    if cur:
        records.append(cur)
    return records


def files(lib: pathlib.Path):
    return sorted(lib.glob("*-golden.md"))


def load(lib: pathlib.Path):
    """The records of the library's golden set (the first, if there are several)."""
    gs = files(lib)
    if not gs:
        raise NoGoldenSet(f"no golden set in {lib}")
    return parse(gs[0].read_text())


def read_mapping(mapping: pathlib.Path, ncases: int) -> dict:
    """{case number: transcript} from a Q<n>|<transcript> mapping file, shared with
    grade-routing. Raises ValueError on a format error: a run graded from the wrong
    transcripts would report on cases nobody ran."""
    if not mapping.is_file():
        raise ValueError(f"{mapping} is not a file")
    graded = {}
    for n, line in enumerate(mapping.read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"\s*Q(\d+)\|(.+?)\s*", line)
        if not m:
            raise ValueError(f"{mapping}: line {n}: expected Q<n>|<transcript>")
        q, t = int(m.group(1)), pathlib.Path(m.group(2))
        if not 1 <= q <= ncases:
            raise ValueError(f"{mapping}: line {n}: Q{q} is not a case in the golden set (1..{ncases})")
        if q in graded:
            raise ValueError(f"{mapping}: line {n}: Q{q} is mapped twice — one transcript per case")
        t = t if t.is_absolute() else mapping.parent / t
        if not t.is_file():
            raise ValueError(f"{mapping}: line {n}: transcript {t} not found")
        graded[q] = t
    if not graded:
        raise ValueError(f"{mapping}: no cases mapped")
    return graded


# -------------------------------------------------------------------------- validation ----
def evidence_of(body: str, excerpt: str):
    """What backs the section holding `excerpt`, as retrieval reports it: "check" if a stamp in it
    carries a `Recheck:`, "word" if it is stamped without one, "unstamped" if it has no stamp (retrieval
    says so, not "someone's word"), None if no section holds the excerpt. Retrieval can see this and
    cannot run the check, so it is all an evidence case can ask of the file."""
    for s in factfiles.sections(body):
        if ws(excerpt) in ws(s.text):
            return "check" if any(st.recheck for st in s.stamps) else "word" if s.stamps else "unstamped"
    return None


def validate(root: pathlib.Path, r: dict, where: str, reachable, marked):
    """(defects, unchecked) of one record of the golden set of the library at `root`, `where` naming
    it in each message. `reachable(owner)` is the set of resolved files the routers of the library at
    `owner` reach; `marked(text)` the sections of a file's text marked UNCORROBORATED."""
    defects, unchecked = [], []
    case = r.get("case")
    if case not in VALID_CASES:
        return [f"{where}: case '{case}' is not one of {sorted(VALID_CASES)}"], unchecked
    if not r.get("question"):
        defects.append(f"{where} [{case}]: no question")

    ef, exc = r.get("expected_file", ""), r.get("expected_excerpt", "")
    alts = r.get("alt_excerpt", [])
    if alts and case in ("negative", "unresolved"):
        # A refusal's excerpt is a fixed phrase; there is no second way to say it.
        defects.append(f"{where} [{case}]: alt_excerpt is not allowed on a refusal case")
    if case == "negative":
        if ef:
            defects.append(f"{where} [negative]: names expected_file '{ef}' — a refusal case "
                           f"must name no file")
        if not exc:
            defects.append(f"{where} [negative]: no expected_excerpt (the refusal to produce)")
        return defects, unchecked

    if not ef:
        defects.append(f"{where} [{case}]: no expected_file")
        return defects, unchecked
    owner, rel = citations.expected_target(root, ef)
    if owner != root.resolve():         # <library>:<path>, another library (issue #36)
        if case != "cross-root":
            defects.append(f"{where} [{case}]: expected_file '{ef}' names another library — "
                           f"only a cross-root case may")
            return defects, unchecked
        if owner is None:
            # A library checked on its own (its CI) cannot see the others, as check-xlinks
            # cannot. The record is checked on a machine where both are registered.
            unchecked.append(f"{where} [{case}]: library '{ef.split(':')[0]}' is not "
                             f"installed on this machine — '{ef}' is checked where it is")
            return defects, unchecked
    target = owner / rel
    if not target.is_file():
        defects.append(f"{where} [{case}]: expected_file '{ef}' does not exist")
        return defects, unchecked
    if target.resolve() not in reachable(owner):
        defects.append(f"{where} [{case}]: expected_file '{ef}' is not reachable from "
                       f"{owner.name}/INDEX.md by router links — retrieval cannot route to it")
    if not exc:
        defects.append(f"{where} [{case}]: no expected_excerpt")
        return defects, unchecked
    body = target.read_text()
    if case == "unresolved":
        # The excerpt is the fixed refusal, which no fact file contains. What must be
        # true of the file instead is that it holds the dispute the case claims to test.
        if exc != DISPUTED:
            defects.append(f"{where} [unresolved]: expected_excerpt must be the refusal "
                           f"'{DISPUTED}', not {exc[:60]!r}")
        if "status: CONFLICTED" not in body:
            defects.append(f"{where} [unresolved]: {ef} has no CONFLICTED section — the case "
                           f"tests a dispute that does not exist")
        return defects, unchecked
    # Line breaks in the source must not make a present excerpt look absent.
    if ws(exc) not in ws(body):
        defects.append(f"{where} [{case}]: excerpt not found in {ef} — "
                       f"the oracle tests nothing: {exc[:60]!r}")
    for alt in alts:                    # held to exactly the standard of the main excerpt
        if ws(alt) not in ws(body):
            defects.append(f"{where} [{case}]: alt_excerpt not found in {ef} — "
                           f"the oracle tests nothing: {alt[:60]!r}")
    ev = r.get("expected_evidence")
    if ev:
        if ev not in EVIDENCE:
            defects.append(f"{where} [{case}]: expected_evidence '{ev}' is not one of {sorted(EVIDENCE)}")
        elif case != "positive":
            defects.append(f"{where} [{case}]: expected_evidence is for a positive case only")
        elif (found := evidence_of(body, exc)) != ev:
            why = {"check": "carries a Recheck:", "word": "has no Recheck:",
                   "unstamped": "has no Verified: stamp, so retrieval reports it unstamped, not as "
                                "someone's word"}.get(found)
            if why:
                defects.append(f"{where} [{case}]: expected_evidence '{ev}' but the section holding "
                               f"the excerpt in {ef} {why}")
    if case == "uncorroborated":
        # The case tests the caveat a marked claim is served with, so its excerpt must be
        # the marked claim, not a sound neighbour in the same file.
        sections = [ws(s) for s in marked(body)]
        if not sections:
            defects.append(f"{where} [uncorroborated]: {ef} has no UNCORROBORATED section — "
                           f"the case tests a caveat nothing carries")
        else:
            for e in [exc] + alts:
                if not any(ws(e) in s for s in sections):
                    defects.append(f"{where} [uncorroborated]: excerpt is not in a section "
                                   f"marked UNCORROBORATED in {ef}: {e[:60]!r}")
    return defects, unchecked


# ------------------------------------------------------------------------------ grading ----
# Whitespace, case and QUOTE CHARACTERS are not grounding. An agent quoting a quotation escapes it
# (\"), nests it as '…', or gets curly quotes from a renderer; the words are unchanged. Every quote
# character folds to one.
QUOTES = str.maketrans({c: '"' for c in "'“”„‟″‘’‚‛′"})
norm = lambda s: re.sub(r"\s+", " ", s.replace('\\"', '"').replace("\\'", "'")
                        .translate(QUOTES)).strip().lower()


def leads(answer: str) -> bool:
    """An uncorroborated fact is served caveat first (CONVENTIONS §8): the answer must open with
    LEAD. Leading markup (bold, a heading, a quote mark) is presentation, not order."""
    return re.sub(r'^[\s*_#>"]+', "", norm(answer)).startswith(LEAD)


def evidence_ok(ev: str, answer: str, excerpts) -> bool:
    """A cited fact states what backs it in plain words (ADR-0022): `check` needs "carries a check",
    `word` needs "someone's word" ahead of the fact, so a reader who stops there knows. Retrieval
    cannot run the lint, so "carries a check", never "asserted"."""
    a, phrase = norm(answer), norm(EVIDENCE[ev])
    at = a.find(phrase)
    if at < 0:
        return False
    # `first` is where the fact is quoted, -1 when it is not quoted at all; that case is already
    # failed by the excerpt check, so the flag cannot be late and is not failed twice.
    first = min((a.find(x) for x in (norm(e).rstrip('.!?;:,"') for e in excerpts) if x in a), default=-1)
    return ev == "check" or first < 0 or at < first


@dataclass
class Verdict:
    passed: bool
    grounded: bool      # the excerpt is in the answer
    cited_ok: bool      # the answer cites the expected file
    reasons: list = field(default_factory=list)


def grade(lib: pathlib.Path, r: dict, cited: str, answer: str) -> Verdict:
    """What an agent answered, graded against one record by grep, not judgement: the expected excerpt
    must be in the answer AND in the file the answer cites. `cited` is the answer's citations, comma
    separated; each is resolved to a file (kbengine.citations), never matched as text."""
    case, ef = r.get("case", "?"), r.get("expected_file", "")
    # A quote may stop before the sentence's full stop; the excerpt's trailing
    # punctuation is not part of what it proves.
    # A fact the file states twice may be quoted from either sentence (alt_excerpt).
    excerpts = [r.get("expected_excerpt", "")] + r.get("alt_excerpt", [])
    in_answer = any(norm(e).rstrip('.!?;:,"') in norm(answer) for e in excerpts)
    # An answer may legitimately cite SEVERAL files — a cross-library question is
    # answered from two, and the contract requires citing every file used. So the
    # expected file must be AMONG those cited, not the only one. Demanding an exact
    # match would fail the very case the contract tells the agent to produce.
    cited_set = {c.strip() for c in cited.split(",") if c.strip()}
    file_ok = citations.resolves_to(lib, ef, cited_set) if ef else (not cited_set)
    in_file = True
    if ef:
        owner, rel = citations.expected_target(lib, ef)
        target = owner / rel if owner else None
        # An unresolved case's excerpt is the refusal phrase, in no fact file; its file
        # must instead still hold the dispute. Every other excerpt must be in its file.
        probes = ["status: conflicted"] if case == "unresolved" else [norm(e) for e in excerpts]
        in_file = target is not None and target.is_file() and all(pr in norm(target.read_text()) for pr in probes)

    led = case != "uncorroborated" or leads(answer)
    ev = r.get("expected_evidence")
    evidenced = not ev or evidence_ok(ev, answer, excerpts)
    why = []
    if not in_answer: why.append("excerpt not in answer")
    if not led:       why.append(f"does not lead with {LEAD!r}")
    if not evidenced: why.append(f"does not state its evidence as {EVIDENCE[ev]!r}"
                                 + (" before the answer" if ev == "word" else ""))
    if not file_ok:   why.append(f"cited {cited or '(none)'!r}, expected {ef or '(none)'!r}")
    if not in_file:   why.append("excerpt not in the expected file — ORACLE ROT")
    return Verdict(in_answer and file_ok and in_file and led and evidenced, in_answer, file_ok, why)
