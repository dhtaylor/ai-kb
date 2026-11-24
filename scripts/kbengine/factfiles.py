"""The fact-file reader: which files of a library are knowledge, what kind each is, and what the
sections of one say (CONVENTIONS §2, §6, §7). The engine's scripts read a library through this,
so a fence, a stamp or a fact file means one thing in all of them (#201). Stdlib only.

files(root)     every markdown file under root that is part of the knowledge base, with its kind.
kind_of(parts)  the same classification for a library-relative path, for paths not on disk.
sections(text)  the sections of one file: headings, status, Source: lines, stamps, Rechecks.
"""
import os, pathlib, re
from dataclasses import dataclass, field

# Folders that are not the knowledge base: decision records, the behaviour plugin, tooling and CI
# config. Ordinary files with no frontmatter contract; they are pruned, never walked.
EXCLUDED_DIRS = frozenset({"documents", "plugins", "scripts", ".github", ".githooks",
                           ".claude-plugin", ".claude", ".git"})
# §5: reached by relative path, never a [[slug]] target.
PATH_ADDRESSED = frozenset({"INDEX.md", "CONVENTIONS.md"})
STATE_LEAF = re.compile(r"-(open-questions|contradictions)\.md$")

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
SOURCE = re.compile(r"^Source:")
STAMP = re.compile(r"^Verified:\s*(\d{4}-\d{2}-\d{2})(.*)$")
BY = re.compile(r"\bby:\s*(\S+)")
METHOD = re.compile(r"\bmethod:\s*(\S+)")
# `Recheck (attended):` marks an assertion that needs a person (contract 2.2).
RECHECK = re.compile(r"^Recheck(\s*\(attended\))?:\s*(.+?)\s*$")
# A Source: citation runs on over the lines it wraps onto, until a blank line or the next marker.
CITATION_STOP = re.compile(r"^(Source:|Verified:|Recheck(?:\s*\(attended\))?:|#{1,6}\s)")
CONFLICTED = re.compile(r"^\s*status:\s*CONFLICTED\b")
UNCORROBORATED = re.compile(r"^\s*status:\s*UNCORROBORATED\b")
# Indented, a stamp looks stamped and certifies nothing, and its Recheck never runs (§7).
INDENTED = re.compile(r"^\s+(Verified|Recheck)(?:\s*\(attended\))?:")


# ---------------------------------------------------------------------------- files ----
def kind_of(parts):
    """The kind of the file at library-relative `parts`: fact, router, golden, queue, state_leaf,
    episodic, source_stub or path_addressed. None under an excluded folder. Only `fact` states
    facts (§6): the rest are records whose sections cite nothing."""
    if EXCLUDED_DIRS & set(parts[:-1]):
        return None
    name = parts[-1]
    if "episodic" in parts[:-1]:
        return "episodic"
    if name == "INDEX.md":
        return "router"
    if name == "CONVENTIONS.md":
        return "path_addressed"
    if name.endswith("-golden.md"):
        return "golden"
    if name == "needs-attention.md":
        return "queue"
    if STATE_LEAF.search(name):
        return "state_leaf"
    if "sources" in parts[:-1]:
        return "source_stub"
    return "fact"


def files(root):
    """(path, kind) for each markdown file under root outside the excluded folders, sorted by
    path. Excluded folders are PRUNED during the walk, not filtered after it: on a slow
    filesystem (a Windows drive under WSL) walking .git alone took seconds on every session
    start, and kb-due's nudge reads the tree from that hook."""
    root, out = pathlib.Path(root), []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for n in filenames:
            if n.endswith(".md"):
                p = pathlib.Path(dirpath) / n
                out.append((p, kind_of(p.relative_to(root).parts)))
    return iter(sorted(out))


# ------------------------------------------------------------------------- sections ----
@dataclass
class Recheck:
    line: int            # 1-based
    cmd: str
    attended: bool


@dataclass
class Stamp:
    line: int
    date: str            # YYYY-MM-DD, as written
    by: str = None       # None when the stamp does not say
    method: str = None
    recheck: Recheck = None


@dataclass
class Source:
    line: int
    text: str            # the Source: line, stripped
    cite: str            # the line and any lines it wraps onto, joined with \n
    stamp: Stamp = None  # the first stamp after it, before the next Source: line


@dataclass
class Section:
    line: int            # of the heading; 0 for the text before the first heading
    level: int           # 0 before the first heading
    heading: str         # the heading line, stripped
    title: str           # its text without the #s
    text: str            # every line of the section, heading included
    conflicted: bool = False
    uncorroborated: bool = False
    has_content: bool = False   # a line that is not blank, a Source: line or a CONFLICTED marker
    sources: list = field(default_factory=list)
    stamps: list = field(default_factory=list)          # every stamp, in order
    orphan_rechecks: list = field(default_factory=list)  # Rechecks that no stamp owns
    indented: list = field(default_factory=list)         # (line, "Verified" | "Recheck") read as nothing

    @property
    def served(self) -> bool:
        """Not CONFLICTED (§8): the sections check-kb reads. Unlike in_scope it keeps the level-0 text
        before the first heading and the level-1 title, so the `verified:` floor and the unstamped
        Source: keys see the whole file. Merging the two would move floors in published libraries."""
        return not self.conflicted

    @property
    def in_scope(self) -> bool:
        """A section a reader is served: below the title, and not CONFLICTED. Sourced, unsourced and
        assertion coverage all start from it, so they cannot disagree about which sections count.
        It is `served` without the level-0 and level-1 sections."""
        return self.level >= 2 and self.served

    @property
    def sourced(self) -> bool:
        return self.in_scope and bool(self.sources)

    @property
    def unsourced(self) -> bool:
        """Content and no Source: line (§6, #154)."""
        return self.in_scope and self.has_content and not self.sources

    @property
    def status(self):
        return "CONFLICTED" if self.conflicted else "UNCORROBORATED" if self.uncorroborated else "served"


def sections(text):
    """The sections of `text`, in order; the first holds whatever precedes the first heading.
    Pure. A fence (``` or ~~~) hides what it holds: a heading, stamp or Source: line inside one
    is an example. Stamps, Rechecks and Source: lines are read only at column 0. A Recheck
    belongs to the stamp above it, on the next line or after one blank line."""
    lines = text.split("\n")
    out, fenced, rechecks = [], False, {}
    cur, buf = None, []

    def close():
        if cur:
            cur.text = "\n".join(buf)
            out.append(cur)

    def new(n, level, heading, title):
        nonlocal cur, buf
        close()
        cur, buf = Section(n, level, heading, title, ""), []

    new(0, 0, "", "")
    for n, line in enumerate(lines, 1):
        buf.append(line)
        if FENCE.match(line):
            fenced = not fenced
            cur.has_content = True
            continue
        if fenced:
            cur.has_content = cur.has_content or bool(line.strip())
            continue
        if m := HEADING.match(line):
            buf.pop()
            new(n, len(line) - len(line.lstrip("#")), line.strip(), m.group(2).strip())
            buf.append(line)
        elif SOURCE.match(line):
            cite, j = line, n               # lines[j] is the line after the Source: line (1-based n)
            while j < len(lines) and lines[j].strip() and not CITATION_STOP.match(lines[j]):
                cite += "\n" + lines[j]
                j += 1
            cur.sources.append(Source(n, line.strip(), cite))
        elif m := STAMP.match(line):
            by, method = BY.search(m.group(2)), METHOD.search(m.group(2))
            stamp = Stamp(n, m.group(1), by and by.group(1), method and method.group(1))
            cur.stamps.append(stamp)
            cur.has_content = True
            if cur.sources and cur.sources[-1].stamp is None:
                cur.sources[-1].stamp = stamp
        elif m := RECHECK.match(line):
            rechecks[n] = (cur, Recheck(n, m.group(2), bool(m.group(1))))
            cur.has_content = True
        elif CONFLICTED.match(line):
            cur.conflicted = True
        else:
            if UNCORROBORATED.match(line):
                cur.uncorroborated = True
            if m := INDENTED.match(line):
                cur.indented.append((n, m.group(1)))
            cur.has_content = cur.has_content or bool(line.strip())
    close()

    claimed = set()
    for sec in out:
        for st in sec.stamps:
            for at in (st.line + 1, st.line + 2):           # the next line, or after one blank
                if at in rechecks:
                    st.recheck = rechecks[at][1]
                    claimed.add(at)
                    break
                if at > len(lines) or lines[at - 1].strip():   # anything else ends the search
                    break
    for at, (sec, rc) in rechecks.items():
        if at not in claimed:
            sec.orphan_rechecks.append(rc)
    return out
