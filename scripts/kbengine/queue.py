"""The needs-attention queue: how a finding is written to a library's needs-attention.md, and how
the queue is read back (CONVENTIONS §3). kb-watch, kb-verify and kb-sources write through this and
kb-due, kb-report and check-kb read through it, so a record, an id or an escape means one thing in
all of them (#202). Stdlib only.

Finding(category, identity, fields, untrusted)   one finding to queue.
append(root, findings, tool, dry_run=False)      write the ones not already queued -> Result.
open_findings(text)                              the open records, one per id, the first winning.
problems(text)                                   what the readers skip or double-count -> Problems.
parse_records(text)                              every record, whatever its status.
read_only_entry(path)                            (kb-libraries, registry entry or None) (ADR-0020).
render(finding)                                  one finding as its queue text.
"""
import hashlib, importlib.machinery, importlib.util, os, pathlib, re, sys
from dataclasses import dataclass

from . import clock, library

MAX_LEN = 200
ID_RE = re.compile(r"^\s*-\s*id:\s*([0-9a-f]{8})\s*$")
KV_RE = re.compile(r'^\s{2}(\w+):\s*"?(.*?)"?\s*$')
FENCE_OPEN = "```yaml\n"
FENCE_CLOSE = "```\n"
SCRIPTS = pathlib.Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------ findings ----
@dataclass(frozen=True)
class Finding:
    """category: the finding's kind, written as `category:`.
    identity: the parts that make it the same finding on a rerun; with the category they are the id.
    fields: {name: value}, in the order the record writes them, between `status` and `date`.
    untrusted: the names in `fields` whose value is a source's own text, so truncated and defanged."""
    category: str
    identity: tuple
    fields: dict
    untrusted: frozenset = frozenset()

    @property
    def id(self) -> str:
        parts = [self.category, *("" if p is None else str(p) for p in self.identity)]
        return hashlib.sha1("|".join(parts).encode()).hexdigest()[:8]


@dataclass
class Result:
    """new: ids not already in the queue, in order (what a real run writes; on `error`, nothing was).
    skipped: ids already there, in any status, or repeated within this call. error: a string or None."""
    new: list
    skipped: list
    error: object = None


def flatten(s: str) -> str:
    s = s.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", s)


def scalar(value, untrusted: bool) -> str:
    """A safe, single-line, double-quoted YAML-ish scalar. Untrusted values are additionally
    truncated and have fence-breaking backtick runs neutralised, per the drift-signal schema."""
    s = flatten("" if value is None else str(value))
    if untrusted:
        s = re.sub(r"`{3,}", "'''", s)
        if len(s) > MAX_LEN:
            s = s[:MAX_LEN] + " …[truncated]"
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def render(f: Finding) -> str:
    lines = [f"- id: {f.id}", f"  category: {scalar(f.category, False)}", f"  status: {scalar('open', False)}"]
    for key, value in f.fields.items():
        lines.append(f"  {key}: {scalar(value, key in f.untrusted)}")
    lines.append(f"  date: {scalar(clock.today().isoformat(), False)}")
    return "\n".join(lines) + "\n\n"


# ------------------------------------------------------------------------------- writing ----
def library_domain_scope(library_root: pathlib.Path):
    idx = library_root / "INDEX.md"
    if not idx.is_file():
        return None, None, f"{library_root} has no INDEX.md — not a library root"
    lib = library.library(library_root)
    if not lib.name or not lib.scope:
        return None, None, f"{idx} has no domain:/scope: in its frontmatter"
    return lib.name, lib.scope, None


def existing_ids(queue_path: pathlib.Path):
    if not queue_path.is_file():
        return set()
    return {m.group(1) for m in map(ID_RE.match, queue_path.read_text(errors="replace").splitlines())
            if m}


def new_queue_file(domain: str, scope: str) -> str:
    fm = (
        "---\n"
        "name: needs-attention\n"
        "description: Open findings from automated checks (kb-watch, kb-verify) and hygiene sweeps "
        "(kb-audit), by severity.\n"
        "memory_type: reference\n"
        f"domain: {domain}\n"
        f"scope: {scope}\n"
        "metadata:\n"
        "  type: index\n"
        "  node_type: memory\n"
        f"  created: {clock.today().isoformat()}\n"
        "tags: [meta, hygiene, queue, watcher]\n"
        "keywords: [needs attention, queue, findings, drift, watcher, unreachable]\n"
        "---\n"
        "# Needs attention\n\n"
        "Findings from automated drift checks and hygiene sweeps. Detection only — nothing here "
        "was fixed automatically. See CONVENTIONS.md §3 and "
        "plugins/knowledge-tools/skills/kb-audit/SKILL.md for the queue's conventions.\n\n"
    )
    return fm + FENCE_OPEN + FENCE_CLOSE


ROUTER_LINE = ("- [needs-attention](needs-attention.md) — open findings from automated checks and "
               "sweeps; detection only, nothing here was fixed automatically\n")


def atomic_write(path: pathlib.Path, text: str):
    """Replace `path` with `text` by writing a sibling and renaming it over the original. A session
    reading or committing the library at the same moment sees the old file or the new one, never a
    half-written one, so these writers can run on a schedule beside a working session (#95)."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(text)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def ensure_routed(library_root: pathlib.Path):
    """Add the queue's router line to the library's INDEX.md, once. Idempotent; returns an error or None."""
    idx = library_root / "INDEX.md"
    if not idx.is_file():
        return f"{library_root} has no INDEX.md — not a library root"
    text = idx.read_text(errors="replace")
    if re.search(r"\]\(needs-attention\.md\)", text):
        return None
    lines = text.splitlines(keepends=True)
    last = max((i for i, l in enumerate(lines) if l.startswith("- [")), default=None)
    if last is None:
        text = text.rstrip("\n") + "\n\n" + ROUTER_LINE
    else:
        j = last + 1                       # a router line may wrap onto indented continuation lines
        while j < len(lines) and lines[j].startswith("  ") and lines[j].strip():
            j += 1
        lines.insert(j, ROUTER_LINE)
        text = "".join(lines)
    atomic_write(idx, text)
    return None


def read_only_entry(path):
    """(kb-libraries, the registry entry if the library at path is registered read-only (ADR-0020),
    else None). The registry is not in the package yet, so it is loaded from scripts/."""
    sys.dont_write_bytecode = True
    loader = importlib.machinery.SourceFileLoader("kb_libraries", str(SCRIPTS / "kb-libraries"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod, mod.read_only(path)


def append(library_root, findings, tool: str, dry_run: bool = False) -> Result:
    """Queue `findings` in the library's needs-attention.md: the ones whose id is not already there
    (in any status, so an acknowledged record blocks a re-add) and not repeated earlier in the call.
    Creates the file and routes it from INDEX.md when absent. `tool` names the caller in a refusal;
    a read-only library is refused here as a backstop, callers check first. `dry_run` reports
    without writing."""
    root = pathlib.Path(library_root)
    queue_path = root / "needs-attention.md"
    kl, ro = read_only_entry(root)
    if ro:
        return Result([], [], kl.refusal(tool, ro))
    seen = existing_ids(queue_path)
    fresh, new, skipped = [], [], []
    for f in findings:
        if f.id in seen:
            skipped.append(f.id)
            continue
        seen.add(f.id)
        fresh.append(f)
        new.append(f.id)
    if not fresh or dry_run:
        return Result(new, skipped)
    body = "".join(render(f) for f in fresh)
    if not queue_path.is_file():
        domain, scope, err = library_domain_scope(root)
        if err:
            return Result(new, skipped, err)
        atomic_write(queue_path, new_queue_file(domain, scope)[:-len(FENCE_CLOSE)] + body + FENCE_CLOSE)
        return Result(new, skipped, ensure_routed(root))   # an unrouted queue fails check-kb (§3)
    text = queue_path.read_text(errors="replace")
    spans = list(re.finditer(r"```yaml\n(?:.*?\n)?```\n", text, re.S))
    if spans:
        insert_at = spans[-1].end() - len(FENCE_CLOSE)
        text = text[:insert_at] + body + text[insert_at:]
    else:
        text = text.rstrip("\n") + "\n\n" + FENCE_OPEN + body + FENCE_CLOSE
    atomic_write(queue_path, text)
    return Result(new, skipped)


# -------------------------------------------------------------------------------- reading ----
def parse_records(text: str):
    """The shape append writes: '- id: x' opens a record, two-space-indented 'key: value' lines
    fill it in. Line-based, no yaml library, as check-golden's parser is."""
    records, cur = [], None
    for raw in text.splitlines():
        m = ID_RE.match(raw)
        if m:
            if cur:
                records.append(cur)
            cur = {"id": m.group(1)}
            continue
        if cur is not None:
            kv = KV_RE.match(raw)
            if kv:
                cur[kv.group(1)] = re.sub(r"\\(.)", r"\1", kv.group(2))
            elif raw.strip() == "" or raw.strip().startswith("```"):
                pass
            elif not raw.startswith("  "):
                records.append(cur); cur = None
    if cur:
        records.append(cur)
    return records


def open_findings(text: str):
    """The records with status open, one per id and the first winning: a copy of an id already
    seen is one finding, not two (#172)."""
    out, seen = [], set()
    for r in parse_records(text):
        if r.get("status") != "open":
            continue
        if r.get("id") is not None:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
        out.append(r)
    return out


@dataclass
class Problems:
    """unreadable: [(line number, line)] the readers skip. duplicates: {id: [line numbers]}."""
    unreadable: list
    duplicates: dict


def problems(text: str) -> Problems:
    return Problems(_unreadable_records(text), _duplicate_ids(text))


def _duplicate_ids(text: str):
    """{id: [line numbers]} for each id that opens two or more records (#172). It walks the text
    exactly as parse_records does, so the two cannot disagree: a line opens a record when ID_RE
    matches it, wherever it sits."""
    seen = {}
    for n, raw in enumerate(text.splitlines(), 1):
        m = ID_RE.match(raw)
        if m:
            seen.setdefault(m.group(1), []).append(n)
    return {i: ns for i, ns in seen.items() if len(ns) > 1}


def _unreadable_records(text: str):
    """[(line number, line)] for each record in a ```yaml fence that parse_records does not read:
    the first line of each run of data lines it skips, such as a bare mapping with `id:` at column 0
    (#168). It walks the text exactly as parse_records does, so the two cannot disagree."""
    out, in_yaml, in_rec, run = [], False, False, False
    for n, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("```"):
            in_yaml = s == "```yaml" and not in_yaml
            in_rec = run = False
            continue
        if not in_yaml or s == "" :
            run = False
            continue
        if ID_RE.match(raw):
            in_rec, run = True, False
            continue
        if in_rec and (KV_RE.match(raw) or raw.startswith("  ")):
            continue
        in_rec = False
        if s.startswith("#"):
            run = False
            continue
        if not run:
            out.append((n, raw))
        run = True
    return out
