"""The assertion lint (#249, from kb-verify; ADR-0022): which Recheck: assertions cannot fail,
and which reach outside the library, as structured findings and as the warnings kb-verify
prints. Stdlib only.

assess(root, sections)           Assessment(findings, weak, outside) from one run of the lint: what the
                                 lease (kbengine.lease) reads.
lint_findings(root, sections)    {(file, stamp line): [kind, ...]}, kind one of
                                 short-fragment, reused-fragment, outside.
weak_rechecks(root, sections)    the printed WEAK warnings.
outside_rechecks(root, sections) the printed OUTSIDE warnings.

A section is a dict with at least file, heading, line and cmd, as kb-verify's sections()
builds it; the lint reads them and writes nothing. It was a pure move out of the script: its
judgements are unchanged.
"""
import pathlib, re, shlex
from typing import NamedTuple

URL =re.compile(r"https?://[^\s'\"|;)<>]+")
# A command fetches when it runs one of these (issue #185); a URL that is only text in it (a
# fixture origin, an echoed string) does not make it a fetch.
FETCHER = re.compile(r"(?<![\w./-])(curl|wget|https?|xh)(?![\w.-]|://)|\b(urlopen|urlretrieve|urllib|requests|httpx|aiohttp)\b")
SHORT_FRAGMENT = 4      # words; 26 of 31 fragments in the #34 sample were 1-4 words long
REUSE_LIMIT = 2         # sections one (url, fragment) pair may back, all in one file (#41)
CLIMB = re.compile(r"(?<![\w.])((?:\.\./)+|(?:\.\./)*\.\.(?![\w./]))")


def last_grep(cmd: str):
    """(options, pattern) of the command's last grep, or None when there is no grep or its
    arguments cannot be read. Options are the tokens before the pattern; -e names the pattern
    explicitly."""
    m = list(re.finditer(r"\bgrep\b", cmd))
    if not m:
        return None
    lex = shlex.shlex(cmd[m[-1].end():], posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        toks = list(lex)
    except ValueError:
        return None
    opts = []
    for i, tok in enumerate(toks):
        if tok in ("|", "||", "&&", ";", "&", ">", "<"):
            return None
        if tok == "-e":
            return (opts, toks[i + 1]) if i + 1 < len(toks) else None
        if not tok.startswith("-"):
            return opts, tok
        opts.append(tok)
    return None


def grep_fragment(cmd: str):
    """The string the command's last grep looks for, or None (see last_grep)."""
    g = last_grep(cmd)
    return g[1] if g else None


def grep_mode(options: list) -> str:
    """F (fixed strings), E (extended), P (Perl) or G (basic, grep's default); the last
    flag given wins, as in grep."""
    mode = "G"
    long = {"--fixed-strings": "F", "--extended-regexp": "E", "--perl-regexp": "P", "--basic-regexp": "G"}
    for o in options:
        if o in long:
            mode = long[o]
        elif o.startswith("-") and not o.startswith("--"):
            for c in o[1:]:
                if c in "FEPG":
                    mode = c
    return mode


TAG = re.compile(r"<[^<>]*>")
SEP = "\x00"


def text_runs(pattern: str, mode: str) -> list:
    """For each alternative of the pattern, the runs of literal text it requires, split by
    markup tags and, outside -F, by regex syntax (issue #65). A run must hold a letter or
    digit to count. Under -F every character is literal, so only tags split it."""
    if mode == "F":
        alts = [pattern]
    else:
        alt_bar = "\\|" if mode == "G" else "|"
        alts, depth, cur, i = [], 0, "", 0
        while i < len(pattern):
            c = pattern[i]
            if c == "\\" and i + 1 < len(pattern):
                if pattern[i:i + 2] == alt_bar and depth == 0:
                    alts.append(cur); cur = ""; i += 2; continue
                cur += pattern[i:i + 2]; i += 2; continue
            if c in "([":
                depth += 1
            elif c in ")]" and depth:
                depth -= 1
            elif c == "|" and alt_bar == "|" and depth == 0:
                alts.append(cur); cur = ""; i += 1; continue
            cur += c; i += 1
        alts.append(cur)
    # A group holding an alternation requires none of its branches in particular, so it
    # contributes no run: `(DENY|Deny)` must not count as two.
    if mode == "G":
        grouped_alt = re.compile(r"\\\((?:(?!\\[()]).)*?\\\|(?:(?!\\[()]).)*?\\\)")
    else:
        grouped_alt = re.compile(r"\((?:[^()\\]|\\.)*?\|(?:[^()\\]|\\.)*?\)")
    out = []
    for alt in alts:
        if mode != "F":
            while grouped_alt.search(alt):
                alt = grouped_alt.sub(SEP, alt)
            meta = ".*[^$" + ("" if mode == "G" else "()+?{}|")
            lit, i = "", 0
            while i < len(alt):
                c = alt[i]
                if c == "\\" and i + 1 < len(alt):
                    n = alt[i + 1]
                    lit += SEP if n.isalnum() or (mode == "G" and n in "(){}+?|") else n
                    i += 2; continue
                if c == "[":
                    j = alt.find("]", i + 2)
                    lit += SEP; i = (j + 1) if j != -1 else len(alt); continue
                lit += SEP if c in meta else c
                i += 1
            alt = lit
        runs = [r for r in re.split(r"<[^<>]*>|\x00", alt) if re.search(r"[A-Za-z0-9]", r)]
        out.append(runs)
    return out

def weak_rechecks(root: pathlib.Path, sections: list) -> list:
    """The printed WEAK warnings, one per finding of _weak (below)."""
    return [msg for _, _, msg in _weak(root, sections)]


def _weak(root: pathlib.Path, sections: list) -> list:
    """(flagged sections, kind, message) per finding.

    Doc-review assertions that cannot fail (§7, issues #34 and #41): a page fetched and
    grepped for a fragment of a few words (its title, its subject, an identifier), or one
    (url, fragment) pair backing many sections or sections in several files. Either passes
    for as long as the page exists, which says nothing about the claim. Static — nothing is
    fetched or run — and a warning, never a failure: a heuristic must not block a sweep.
    Only commands that fetch a URL (run curl, wget, http, xh, or a python urllib, requests or
    httpx call) and grep it are judged. A URL that is only text in the command, such as a fixture
    origin written to a temp library, is not a fetch, and nor is a local query (issue #185).
    A short pattern that binds two runs of text — split by markup, or outside -F by regex —
    tests a relation (a field and its value), not a title, and is not flagged; an
    alternation is as weak as its weakest branch (issue #65)."""
    out, pairs = [], {}
    for s in sections:
        cmd = s["cmd"] or ""
        fetch, frag = FETCHER.search(cmd), grep_fragment(cmd)
        url = fetch and (URL.search(cmd, fetch.end()) or URL.search(cmd))
        if not (url and frag):
            continue
        where = f"{s['file'].relative_to(root)} § {s['heading']}"
        words = len(frag.split())
        bound = all(len(runs) > 1 for runs in text_runs(frag, grep_mode(last_grep(s["cmd"])[0])))
        if words <= SHORT_FRAGMENT and not bound:
            out.append(([s], "short-fragment",
                        f"WEAK {where}: greps {words} word{'s' if words != 1 else ''} ('{frag[:60]}') — "
                        f"a title or identifier passes while the page exists"))
        pairs.setdefault((url.group(0), frag), []).append((s, where))
    for (url, frag), backs in pairs.items():
        files = {s["file"] for s, _ in backs}
        if len(backs) > REUSE_LIMIT or len(files) > 1:
            out.append(([s for s, _ in backs], "reused-fragment",
                        f"WEAK one fragment backs {len(backs)} sections in {len(files)} "
                        f"file{'s' if len(files) != 1 else ''} ('{frag[:60]}' at {url}): "
                        + "; ".join(w for _, w in backs)
                        + " — it cannot test each section's own claim"))
    return out


def outside_rechecks(root: pathlib.Path, sections: list) -> list:
    """The printed OUTSIDE warnings, one per finding of _outside (below)."""
    return [msg for _, _, msg in _outside(root, sections)]


def _outside(root: pathlib.Path, sections: list) -> list:
    """(flagged sections, kind, message) per finding.

    Assertions whose relative path climbs above the library root (issue #60). Static, a
    warning: the path resolves only in one layout, and elsewhere the fact reads as stale."""
    out = []
    for s in sections:
        depth = len(s["file"].parent.relative_to(root).parts)
        if any(m.group(1).count("..") > depth for m in CLIMB.finditer(s["cmd"] or "")):
            out.append(([s], "outside",
                        f"OUTSIDE {s['file'].relative_to(root)} § {s['heading']}: a relative path climbs "
                        f"out of the library — name the engine as \"$KB_ENGINE_ROOT/scripts/...\""))
    return out


class Assessment(NamedTuple):
    findings: dict       # as lint_findings gives it
    weak: tuple          # the printed WEAK warnings
    outside: tuple       # the printed OUTSIDE warnings


def assess(root: pathlib.Path, sections: list) -> Assessment:
    """The findings and both sets of printed warnings from one run of the lint over `sections`
    (#250): the lease takes all three from it, so the library is linted once."""
    weak, outside, got = _weak(root, sections), _outside(root, sections), {}
    for flagged, kind, _ in weak + outside:
        for s in flagged:
            got.setdefault((s["file"], s["line"]), []).append(kind)
    return Assessment(got, tuple(m for _, _, m in weak), tuple(m for _, _, m in outside))


def lint_findings(root: pathlib.Path, sections: list) -> dict:
    """{(file, stamp line): [kind, ...]} for every section the assertion lint flags, kind one of
    short-fragment, reused-fragment, outside (#235). The same findings the printed warnings
    report, keyed so the lease and assertion coverage (ADR-0022) can tell which sections they cover."""
    return assess(root, sections).findings
