"""What needs a person's attention in one library: the one reading of every category kb-due, kb-report
and kb-prepare each used to compute for themselves (#204). They render the result and stop there, so
what is "due" is one judgment, and a category added or changed here reaches all of them. Stdlib only.

attention(tree, packets, consumed)   an Attention for the library at `tree`.
label(tree)                          the name to show for a tree.
shelved(att, registered)             whether a nudge or report leaves the library out.
worth_a_line(items)                  whether the nudge has a line for a library with these items.

The caller reads the review packets once (kb-apply's pending()) and the read-only set once (the
registry's read-only paths, resolved), and passes both to every tree. The tree's INDEX.md is read once,
and the staleness of its sections is worked out once, however many fields use them.

Each field holds its value, or `Failed(reason)` when it could not be worked out. A failure is data:
nothing here prints, and one failed field never hides another. A field is computed when first read,
so a caller pays only for the categories it shows: the git history behind `unstamped`, the source
stubs behind `manual_stubs` and the fact files behind `unsourced` are never read for a caller that
does not ask. The fact files are parsed as one factfiles.Tree, which `unstamped`, `unstamped_total`
and `unsourced` share.

    packets          [(path, header)] of the review packets waiting on this library.
    sweep_covered    a kb-audit packet is waiting, so a sweep is already in hand. distill_covered: the same
                     for kb-distill and the episodic notes.
    sweep            Sweep(due, age, interval): age in days, None when never swept (or unreadably).
    rechecks         Rechecks(due, budget): every stamp with a Recheck: that is due, oldest first, each
                     marked `attended` when only a person can run it, and the library's
                     verifier_budget. Empty without a freshness_horizon.
    stale            [stamp]: stamped sections past their horizon or short lease with no Recheck:.
    queue            [record]: the open records in needs-attention.md, one per id.
    queue_unreadable [(line number, line)]: what the queue reader skips.
    episodic         the number of episodic notes not yet distilled.
    unstamped        Unstamped(total, new, since_sweep, git_error): Source: lines with no stamp. With a sweep
                     to compare with, `count` is only the ones new since it. unstamped_total: every one.
    coverage         Coverage(asserted, sourced): assertion coverage (#239, ADR-0022). Sourced sections
                     are the served sections of fact files that hold a Source: line (the complement of
                     `unsourced`, a CONFLICTED one excluded). Asserted ones carry an asserted stamp,
                     a Recheck: the assertion lint does not flag, however stale; a flagged one counts
                     as unasserted. Zero is a value, never a failure, and does not need a horizon.
    unsourced        the number of sections with content and no Source: line.
    contract         Contract(state, version, newest, newer), as contract.contract_status gives it.
    manual_stubs     the source stubs marked Liveness: manual.
    archived         the text of `archived:`, or None. read_only: registered as a consumer's copy (ADR-0020).

    registered       the library is registered on this machine (the caller passes the resolved registered paths).
    items            the policy: the frozen, ordered tuple of Item that this library needs said, below.

rechecks, stale and coverage come from one kbengine.lease sweep, which owns the lease rules (#250).

items (#253). Which of the fields above need saying, and when, is decided here and nowhere else: a
packet suppresses the sweep or the notes it covers, a failed field is an item of its own, and the four
contract states that need telling (behind, ahead, unsupported, malformed) are one item. kb-due words the
items tersely and kb-report imperatively, and neither tests a condition to find them. An Item holds its
kind, `n` (how many, and what `says` is made of), whether it is a `decision` (something only a person can
settle: the weekly report lists these, the nudge lists everything), and `detail`: the field's value, or
its Failed. The kinds, in order:

    coverage          always, first: the library's assertion coverage (never a decision).
    packets           the review packets waiting. decision.
    sweep             a sweep is due and no kb-audit packet covers it. decision.
    manual_stubs      while a sweep is due, the source stubs marked Liveness: manual. decision. REPORT_ONLY:
                      the nudge does not name them.
    recheck           the facts due for recheck. A decision when one needs a person there (attended).
    stale             stale facts with no assertion.
    queue             open queue records. decision. queue_unreadable: the records the reader skipped. decision.
    distill           episodic notes to distil, and no kb-distill packet covers them. decision.
    unstamped         Source: lines with no stamp; also present, with n of 0, when only the git comparison failed.
    unsourced         sections with content and no Source: line.
    contract          behind, ahead, unsupported or malformed. decision.
    archived          declares `archived:` and is registered, so is still served and can be removed.

A field that failed is its Failed in an item of its kind (n of 0), a decision when the kind is one.

kb-sources (manual stubs) is a script, not a module yet: it is loaded here, in one place, on first
use, rather than by each caller.
"""
import collections, importlib.machinery, importlib.util, pathlib, re, subprocess, sys
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from . import clock, contract, factfiles, lease, library, queue
from .lease import Coverage

REPORT_ONLY = ("manual_stubs",)   # items only the weekly report says: the nudge leaves them out
SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
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


def describe_coverage(cov: Coverage) -> str:
    """Assertion coverage in words, for the nudge and the report alike: zero is a number like any
    other, never a warning (#239)."""
    n = cov.sourced
    return f"assertion coverage {cov.asserted} of {n} sourced section{'' if n == 1 else 's'}"


class Unstamped(NamedTuple):
    total: int           # every Source: line with no stamp
    new: int             # the ones not already there at the last sweep; the total when there is none
    since_sweep: bool    # new was compared with the last sweep's commit
    git_error: object    # why that comparison could not be made (the total is used instead), or None

    @property
    def count(self) -> int:
        return self.new


class Item(NamedTuple):
    """One thing a library needs said (see the module docstring)."""
    kind: str
    n: int               # how many; 0 for a field that failed
    decision: bool       # only a person can settle it
    detail: object       # the field's value, or its Failed

    @property
    def failed(self) -> bool:
        return isinstance(self.detail, Failed)

    @property
    def says(self) -> bool:
        """Something to say about the library, as opposed to a failure to warn of."""
        return not self.failed and bool(self.n)


@dataclass(frozen=True)
class Rechecks:
    due: list            # stamps, oldest first, each with `attended`
    budget: int

    @property
    def capped(self) -> list:
        """What kb-verify runs by default: the budget's worth."""
        return self.due[:self.budget]

    @property
    def attended(self) -> list:
        return [s for s in self.due if s.attended]


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


def _try(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        return Failed(str(e), type(e).__name__)


# ------------------------------------------------------------------------ helpers ----
def label(tree: pathlib.Path):
    """A project tree is always called knowledge/; name it after the project instead."""
    return tree.parent.resolve().name if tree.name == "knowledge" else tree.name


def git(root: pathlib.Path, *args, data=None):
    return subprocess.run(["git", "-C", str(root), *args], input=data, capture_output=True, timeout=60)


def _unstamped_keys(tree: factfiles.Tree) -> collections.Counter:
    """Served sections' Source: lines with no stamp (issue #29), each as (heading, Source: line), in
    the fact files of `tree` (the golden set, queue, state leaves, routers and records are no fact's home)."""
    keys = collections.Counter()
    for f in tree.facts:
        keys.update(factfiles.unstamped_keys(f.body_sections))
    return keys


def _sweep_baseline(root: pathlib.Path, swept, now: collections.Counter):
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
    blobs, i = {}, 0
    for n in wanted:   # each blob: "<sha> blob <size>\n<content>\n"
        nl = out.index(b"\n", i)
        size = int(out[i:nl].split()[2])
        blobs[n[len(prefix):]] = out[nl + 1:nl + 1 + size].decode(errors="replace")
        i = nl + 1 + size + 1
    return _unstamped_keys(factfiles.tree_from(blobs))


# ---------------------------------------------------------------------- Attention ----
class Attention:
    """What one library needs from a person; see the module docstring for the fields."""

    def __init__(self, tree, packets, consumed, registered=()):
        self.tree = pathlib.Path(tree)
        self.root = self.tree.resolve()
        self.lib = library.library(self.root)           # INDEX.md, read once
        self.packets = [(p, h) for p, h in packets if h.get("library_path") == str(self.root)]
        self.read_only = self.root in consumed
        self.registered = self.root in registered
        self.archived = self.lib.archived
        covered = {h.get("packet") for _, h in self.packets}
        self.sweep_covered = "kb-audit" in covered
        self.distill_covered = "kb-distill" in covered
        lib = self.lib
        today = clock.today()
        age = (today - lib.last_swept).days if lib.last_swept is not None else None
        self.sweep = Sweep(age is None or age > lib.sweep_interval, age, lib.sweep_interval)

    # -- the lease of every stamp: one sweep serves rechecks, stale and coverage --
    @cached_property
    def _leases(self):
        """kbengine.lease's one pass over the fact files (#250). Without a horizon nothing is due, and
        coverage is there all the same."""
        lib = self.lib
        def read():
            if lib.horizon is not None and lib.unasserted_ttl is None:
                raise ValueError(lib.problem("unasserted_ttl"))   # the library's reason, not the lease's
            return lease.sweep(self._tree, horizon=lib.horizon, unasserted_ttl=lib.unasserted_ttl)
        return _try(read)

    @cached_property
    def coverage(self):
        """Assertion coverage (#239, ADR-0022): sections with an asserted stamp over served sections
        with a Source: line, in fact files. A section is asserted when any of its stamps is."""
        got = self._leases
        if isinstance(got, Failed):
            # Coverage does not depend on the lease: a short lease the library cannot use fails
            # rechecks and stale, not what backs each section.
            got = _try(lease.sweep, self._tree)
        return got if isinstance(got, Failed) else got.coverage

    @cached_property
    def rechecks(self):
        got = self._leases
        return got if isinstance(got, Failed) else Rechecks(list(got.due), self.lib.budget)

    @cached_property
    def stale(self):
        """Stamped sections past their horizon or short lease that carry no Recheck: (issue #63). Not
        capped by the budget: nothing runs these."""
        got = self._leases
        return got if isinstance(got, Failed) else list(got.stale)

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

    # -- the fact files, parsed once --
    @cached_property
    def _tree(self):
        """The library's files as one factfiles.Tree. Building it reads nothing (and cannot fail: the
        walk skips what it cannot list); each file is read the first time a field asks for it."""
        return factfiles.tree(self.root)

    # -- Source: lines --
    @cached_property
    def _keys(self):
        return _try(_unstamped_keys, self._tree)

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
                before = _sweep_baseline(self.root, self.lib.last_swept_text, now)
            except Exception as e:
                git_error = str(e)
        new = sum((now - before).values()) if before is not None else total
        return Unstamped(total, new, before is not None, git_error)

    @cached_property
    def unsourced(self):
        """Sections with content and no Source: line, in fact files only, by factfiles' rules
        (§6, issue #154). A sourceless section is never counted as unstamped."""
        return _try(lambda: sum(len(factfiles.unsourced(f.body_sections)) for f in self._tree.facts))

    # -- the policy --
    @cached_property
    def items(self) -> tuple:
        """What this library needs said, in order (module docstring). Reads every field it needs."""
        out = []

        def say(kind, got, n, decision=True):
            if isinstance(got, Failed):
                out.append(Item(kind, 0, decision, got))
            elif n:
                out.append(Item(kind, n, decision, got))

        def size(got):
            return 0 if isinstance(got, Failed) else len(got)

        out.append(Item("coverage", 0, False, self.coverage))
        say("packets", self.packets, len(self.packets))
        sw = self.sweep
        say("sweep", sw, int(sw.due and not self.sweep_covered))   # a kb-audit packet is already the sweep (#204)
        if sw.due:
            stubs = self.manual_stubs
            say("manual_stubs", stubs, size(stubs))
        rc = self.rechecks
        say("recheck", rc, size(rc.due) if not isinstance(rc, Failed) else 0,
            isinstance(rc, Failed) or bool(rc.attended))
        stale = self.stale
        say("stale", stale, size(stale), False)
        queued = self.queue
        say("queue", queued, size(queued))
        bad = self.queue_unreadable   # a queue that cannot be read is said once, by `queue`
        if not (isinstance(bad, Failed) and bad == queued):
            say("queue_unreadable", bad, size(bad))
        notes = self.episodic
        say("distill", notes, 0 if isinstance(notes, Failed) or self.distill_covered else notes)   # a kb-distill packet is the distillation (#204)
        un = self.unstamped
        if isinstance(un, Failed):
            out.append(Item("unstamped", 0, False, un))
        elif un.count or un.git_error is not None:
            out.append(Item("unstamped", un.count, False, un))
        us = self.unsourced
        say("unsourced", us, 0 if isinstance(us, Failed) else us, False)
        found = self.contract
        if isinstance(found, Failed) or found.state in ("behind", "ahead", "unsupported", "malformed"):
            say("contract", found, 1)
        if self.archived and self.registered:   # served whatever it declares (#141)
            out.append(Item("archived", 1, False, self.archived))
        return tuple(out)

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


def attention(tree, packets, consumed, registered=()) -> Attention:
    """The Attention for the library at `tree`. `packets` is kb-apply's pending() ([(path, header)]);
    `consumed` the resolved paths registered read-only, `registered` those of every registered library.
    All are read once by the caller."""
    return Attention(tree, packets, consumed, registered)


def worth_a_line(items) -> bool:
    """Whether the nudge has a line for a library with these items: something is said besides coverage,
    or coverage is below full. Coverage is a measure, not something due, but a library below full coverage
    is named even when nothing is due (#239, ADR-0022)."""
    for item in items:
        if item.kind == "coverage":
            if not item.failed and item.detail.asserted < item.detail.sourced:
                return True
        elif item.says and item.kind not in REPORT_ONLY:
            return True
    return False


def shelved(att: Attention, registered=None) -> bool:
    """Whether a nudge or report leaves the library out: an archived library that is not registered
    (#141: a read-only archive cannot act on it; a registered one is served whatever it declares),
    or one registered read-only, a consumer's copy curated by its publisher (ADR-0020).
    `registered` holds the resolved paths of the registered libraries; by default, the ones the
    Attention was given."""
    registered = att.registered if registered is None else att.root in registered
    return bool((att.archived and not registered) or att.read_only)
