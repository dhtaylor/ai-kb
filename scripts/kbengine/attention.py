"""What needs a person's attention in one library: the one reading of every category kb-due, kb-report
and kb-prepare each used to compute for themselves (#204). They render the result and stop there, so
what is "due" is one judgment, and a category added or changed here reaches all of them. Stdlib only.

attention(tree, packets, consumed)   an Attention for the library at `tree`.
label(tree)                          the name to show for a tree.
shelved(att, registered)             whether a nudge or report leaves the library out.

The caller reads the review packets once (kb-apply's pending()) and the read-only set once (the
registry's read-only paths, resolved), and passes both to every tree. The tree's INDEX.md is read once,
and the staleness of its sections is worked out once, however many fields use them.

Each field holds its value, or `Failed(reason)` when it could not be worked out. A failure is data:
nothing here prints, and one failed field never hides another. A field is computed when first read,
so a caller pays only for the categories it shows: the git history behind `unstamped`, the source
stubs behind `manual_stubs` and the fact files behind `unsourced` are never read for a caller that
does not ask.

    packets          [(path, header)] of the review packets waiting on this library.
    sweep_covered    a kb-audit packet is waiting, so a sweep is already in hand. distill_covered: the same
                     for kb-distill and the episodic notes.
    sweep            Sweep(due, age, interval): age in days, None when never swept (or unreadably).
    rechecks         Rechecks(due, budget): every section with a Recheck: that is due, oldest stamp first,
                     each marked "attended" when only a person can run it, and the library's
                     verifier_budget. Empty without a freshness_horizon.
    stale            [section]: stamped sections past their horizon or agent TTL with no Recheck:.
    queue            [record]: the open records in needs-attention.md, one per id.
    queue_unreadable [(line number, line)]: what the queue reader skips.
    episodic         the number of episodic notes not yet distilled.
    unstamped        Unstamped(total, new, since_sweep, git_error): Source: lines with no stamp. With a sweep
                     to compare with, `count` is only the ones new since it. unstamped_total: every one.
    unsourced        the number of sections with content and no Source: line.
    contract         Contract(state, version, newest, newer), as contract.contract_status gives it.
    manual_stubs     the source stubs marked Liveness: manual.
    archived         the text of `archived:`, or None. read_only: registered as a consumer's copy (ADR-0020).

kb-verify (due sections), check-kb (the section readers), kb-sources (manual stubs) are scripts, not
modules yet: they are loaded here, in one place, on first use, rather than by each caller.
"""
import collections, datetime, importlib.machinery, importlib.util, pathlib, re, subprocess, sys
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from . import contract, factfiles, library, queue

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today()
DISTILLED = re.compile(r"^##\s+Distill", re.M)


@dataclass(frozen=True)
class Failed:
    """A field that could not be worked out: reason is the error's message, kind its type's name."""
    reason: str
    kind: str = ""


class Sweep(NamedTuple):
    due: bool
    age: object          # days since last_swept, or None
    interval: int


class Contract(NamedTuple):
    state: str           # current, behind, ahead, unsupported or malformed
    version: object
    newest: object
    newer: object


class Unstamped(NamedTuple):
    total: int           # every Source: line with no stamp
    new: int             # the ones not already there at the last sweep; the total when there is none
    since_sweep: bool    # new was compared with the last sweep's commit
    git_error: object    # why that comparison could not be made (the total is used instead), or None

    @property
    def count(self) -> int:
        return self.new


@dataclass(frozen=True)
class Rechecks:
    due: list            # section dicts, oldest stamp first, each with "attended"
    budget: int

    @property
    def capped(self) -> list:
        """What kb-verify runs by default: the budget's worth."""
        return self.due[:self.budget]

    @property
    def attended(self) -> list:
        return [s for s in self.due if s.get("attended")]


# --------------------------------------------------------------------- the scripts ----
_scripts = {}


def script(filename: str):
    """An extensionless sibling script, imported as the file on disk, once. No bytecode is written,
    so an engine script that only reads libraries leaves no scripts/__pycache__."""
    if filename not in _scripts:
        try:
            sys.dont_write_bytecode = True
            loader = importlib.machinery.SourceFileLoader(filename.replace("-", "_"), str(SCRIPTS / filename))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            mod = importlib.util.module_from_spec(spec)
            loader.exec_module(mod)
            _scripts[filename] = mod
        except Exception as e:
            _scripts[filename] = e
    got = _scripts[filename]
    if isinstance(got, Exception):
        raise got
    return got


def _check_kb():
    try:
        return script("check-kb")
    except Exception:
        raise RuntimeError("check-kb could not be loaded") from None


def _try(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        return Failed(str(e), type(e).__name__)


# ------------------------------------------------------------------------ helpers ----
def label(tree: pathlib.Path):
    """A project tree is always called knowledge/; name it after the project instead."""
    return tree.parent.resolve().name if tree.name == "knowledge" else tree.name


def body_of(text: str) -> str:
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def git(root: pathlib.Path, *args, data=None):
    return subprocess.run(["git", "-C", str(root), *args], input=data, capture_output=True, timeout=60)


def _unstamped_keys(root: pathlib.Path, check_kb) -> collections.Counter:
    """Served sections' Source: lines with no stamp, by check-kb's own section reader (issue #29),
    each as (heading, Source: line)."""
    keys = collections.Counter()
    for f, kind in factfiles.files(root):
        if kind == "fact":       # the golden set, queue, state leaves, routers and records are no fact's home
            keys.update(check_kb.unstamped_keys(body_of(f.read_text(errors="replace"))))
    return keys


def _sweep_baseline(root: pathlib.Path, swept, now: collections.Counter, check_kb):
    """The unstamped sources as the last sweep left them (issue #142), or None when there is no
    sweep to compare with: never swept, or not in git. The sweep is the commit that last changed
    INDEX.md's last_swept line. A sweep not yet committed is compared with the files as they are,
    so nothing reads as new. Keys hold no file path: a section moved by kb-organize-domain is the
    same source, not a new one. `swept` is the text INDEX.md declares; `now` the keys as they are."""
    if swept in (None, "never"):
        return None
    r = git(root, "rev-parse", "--show-prefix")
    if r.returncode:
        return None
    prefix = r.stdout.decode().strip()
    commit = git(root, "log", "-1", "--format=%H", "-G", "^last_swept:", "--", "INDEX.md").stdout.decode().strip()
    committed = git(root, "show", f"{commit}:./INDEX.md").stdout.decode(errors="replace") if commit else ""
    if not commit or library.read(committed).get("last_swept") != swept:
        return now
    names = git(root, "ls-tree", "-r", "--name-only", "--full-name", commit, "--", ".").stdout.decode().splitlines()
    wanted = [n for n in names if n.endswith(".md") and n.startswith(prefix)
              and factfiles.kind_of(tuple(n[len(prefix):].split("/"))) == "fact"]
    out = git(root, "cat-file", "--batch", data="".join(f"{commit}:{n}\n" for n in wanted).encode()).stdout
    keys, i = collections.Counter(), 0
    for _ in wanted:   # each blob: "<sha> blob <size>\n<content>\n"
        nl = out.index(b"\n", i)
        size = int(out[i:nl].split()[2])
        keys.update(check_kb.unstamped_keys(body_of(out[nl + 1:nl + 1 + size].decode(errors="replace"))))
        i = nl + 1 + size + 1
    return keys


# ---------------------------------------------------------------------- Attention ----
class Attention:
    """What one library needs from a person; see the module docstring for the fields."""

    def __init__(self, tree, packets, consumed):
        self.tree = pathlib.Path(tree)
        self.root = self.tree.resolve()
        self.lib = library.library(self.root)           # INDEX.md, read once
        self.packets = [(p, h) for p, h in packets if h.get("library_path") == str(self.root)]
        self.read_only = self.root in consumed
        self.archived = self.lib.archived
        covered = {h.get("packet") for _, h in self.packets}
        self.sweep_covered = "kb-audit" in covered
        self.distill_covered = "kb-distill" in covered
        lib = self.lib
        age = (TODAY - lib.last_swept).days if lib.last_swept is not None else None
        self.sweep = Sweep(age is None or age > lib.sweep_interval, age, lib.sweep_interval)

    # -- facts past their horizon: one pass over the fact files serves rechecks and stale --
    @cached_property
    def _due(self):
        return _try(self._load_due)

    def _load_due(self):
        lib = self.lib
        if lib.horizon is None:
            return None                  # not computable: neither due nor stale, and no failure
        if lib.agent_ttl is None:
            raise ValueError(lib.problem("agent_ttl"))
        due, found, _with_cmd = script("kb-verify").due_sections(self.root, lib.horizon, lib.agent_ttl)
        return due, found

    @cached_property
    def rechecks(self):
        got = self._due
        if isinstance(got, Failed):
            return got
        return Rechecks(got[0] if got else [], self.lib.budget)

    @cached_property
    def stale(self):
        """Stamped sections past their horizon or agent TTL that carry no Recheck: (issue #63), by
        kb-verify's own is_due(). Not capped by the budget: nothing runs these."""
        got = self._due
        if isinstance(got, Failed):
            return got
        if got is None:
            return []
        is_due = script("kb-verify").is_due
        return _try(lambda: [s for s in got[1] if not s["cmd"] and is_due(s, self.lib.horizon, self.lib.agent_ttl)])

    # -- needs-attention.md, read once --
    @cached_property
    def _queue_text(self):
        qpath = self.root / "needs-attention.md"
        return _try(lambda: qpath.read_text(errors="replace") if qpath.is_file() else None)

    @cached_property
    def queue(self):
        text = self._queue_text
        if isinstance(text, Failed) or text is None:
            return text or []
        return _try(queue.open_findings, text)

    @cached_property
    def queue_unreadable(self):
        text = self._queue_text
        if isinstance(text, Failed) or text is None:
            return text or []
        return _try(lambda: queue.problems(text).unreadable)

    @cached_property
    def episodic(self):
        """Episodic notes not yet distilled: kb-distill marks one it has distilled with a heading
        beginning `## Distill`; a note without one is counted."""
        edir = self.root / "episodic"
        return _try(lambda: len([f for f in edir.glob("*.md")
                                 if f.name != "INDEX.md" and not DISTILLED.search(f.read_text(errors="replace"))])
                    if edir.is_dir() else 0)

    # -- Source: lines --
    @cached_property
    def _keys(self):
        return _try(lambda: _unstamped_keys(self.root, _check_kb()))

    @cached_property
    def unstamped_total(self):
        keys = self._keys
        return keys if isinstance(keys, Failed) else sum(keys.values())

    @cached_property
    def unstamped(self):
        now = self._keys
        if isinstance(now, Failed):
            return now
        total, before, git_error = sum(now.values()), None, None
        if now:
            try:
                before = _sweep_baseline(self.root, self.lib.last_swept_text, now, _check_kb())
            except Exception as e:
                git_error = str(e)
        new = sum((now - before).values()) if before is not None else total
        return Unstamped(total, new, before is not None, git_error)

    @cached_property
    def unsourced(self):
        """Sections with content and no Source: line, in fact files only, by check-kb's own rules
        (§6, issue #154). A sourceless section is never counted as unstamped."""
        def count():
            check_kb, n = _check_kb(), 0
            for f, kind in factfiles.files(self.root):
                if kind == "fact":
                    n += len(check_kb.unsourced(body_of(f.read_text(errors="replace"))))
            return n
        return _try(count)

    # -- the library's own declarations --
    @cached_property
    def contract(self):
        """ADR-0016: where the library's contract stands against this engine's."""
        def read():
            found = self.lib.contract
            if found is None:
                contract.known_contracts()    # this engine cannot read its own §14: raises why
            return Contract(*found)
        return _try(read)

    @cached_property
    def manual_stubs(self):
        """Source stubs marked `Liveness: manual` (§6, contract 2.4): only a person can check them."""
        return _try(lambda: script("kb-sources").manual_stubs(self.root))


def attention(tree, packets, consumed) -> Attention:
    """The Attention for the library at `tree`. `packets` is kb-apply's pending() ([(path, header)]);
    `consumed` the resolved paths registered read-only. Both are read once by the caller."""
    return Attention(tree, packets, consumed)


def shelved(att: Attention, registered) -> bool:
    """Whether a nudge or report leaves the library out: an archived library that is not registered
    (#141: a read-only archive cannot act on it; a registered one is served whatever it declares),
    or one registered read-only, a consumer's copy curated by its publisher (ADR-0020).
    `registered` holds the resolved paths of the registered libraries."""
    return bool((att.archived and att.root not in registered) or att.read_only)
