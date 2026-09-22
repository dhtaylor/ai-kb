# Working with the knowledge base

This repository is the **engine**: the contract, the tooling and the skills. It holds no facts.
Facts live in **domain libraries** — one repository per domain, cloned into `kb/` — and in each
project's own `knowledge/` tree. The separation is the point: behaviour here, knowledge there, and
neither pretending to be the other.

[CONVENTIONS.md](CONVENTIONS.md) is the contract and settles anything this guide leaves open. This
is the path through it, not a summary of it.

---

## Setting up a machine

```bash
git clone https://github.com/dhtaylor/ai-kb.git ~/kb-engine      # the engine, anywhere you like
mkdir -p ~/kb-engine/kb
git clone <library-url> ~/kb-engine/kb/<library-name>            # each library you need
~/kb-engine/scripts/kb-bootstrap                                 # register it on this machine
```

`kb-bootstrap` takes no arguments: the engine is wherever the script lives. It writes
`~/.claude/settings.json` (the engine path, the plugin, the session hook), `git config --global
kb.engineRoot`, a `PATH` block in your shell rc, and `core.hooksPath` in each installed library. It
merges with what is already there, backs a file up before changing it, and is safe to run again —
run it again whenever the engine moves, or when you clone another library.

**Then restart your terminal and any open Claude Code session.** A shell profile is read at shell
start, and Claude reads its settings and plugin content once per session.

Check it whenever you are unsure:

```bash
kb-bootstrap --check      # reports drift, changes nothing, exits 1 if anything is out of step
```

### In each project

```bash
cd <project>
kb-init                   # new project: scaffolds knowledge/, .claude/ and a CLAUDE.md stanza
                          # already set up (you cloned it): wires the commit hook, nothing else
```

**Run `kb-init` in every clone, including one you cloned yesterday.** `core.hooksPath` is local
config that git does not clone, so a fresh clone runs *no* hook at all — observed: a file with a
mismatched name, the wrong scope and no router line committed with exit 0 and no output whatsoever.

---

## The daily loop

**Capture as you go.** In a Claude session, `/kb-capture`; from a terminal, `kb-capture`. It writes
a dated note under `knowledge/episodic/` in the nearest tree and routes it.

A capture **records; it does not decide**. Keep what you saw separate from what you concluded, and
keep the hedges in the words that show them — "probably", "we didn't test that", "the docs say".
Distillation decides what becomes a fact by reading those words, and retrieval refuses to serve a
guess *because the note admits it is one*. A capture that reads well and has lost its hedges is
worse than no capture.

The title matters most: it becomes the filename and the line a retrieval agent reads first. Say
what was **done and seen**, never what you concluded.

> Right: `Checkout 504s in staging; 47 idle-in-transaction connections; terminating them restored service`
> Wrong: `Checkout 504s traced to idle connections exhausting the pool`

**Distil periodically.** The `kb-distill` skill turns notes into durable facts: observed material
becomes a fact with a `Source:` and a currency stamp; a speculation stays in the note. Facts land in
the tier they belong to — this deployment's quirk in the project tree, the product's behaviour in a
library.

**Retrieve with the `kb-retrieve` agent** rather than asking a model to recall. It descends from a
router, cites every file, refuses a disputed fact, says "fact not found" when the knowledge base is
silent, and answers only from the knowledge base — not from the code or config beside it. Reading
the source is the caller's job; that is how a gap stays visible instead of being quietly papered
over.

---

## Curating

| You want to | Skill |
|---|---|
| Fold a document, spec or vendor page into a domain that exists | `kb-update-domain` |
| Stand up a domain that does not exist yet | `kb-create-domain` |
| Turn session notes into facts | `kb-distill` |
| Split, merge or rename files in a lumpy domain | `kb-organize-domain` |
| Sweep for decay and build a needs-attention queue | `kb-audit` |

Four rules run through all of them, and they are the ones worth knowing before you start.

**One home per fact.** A fact true only of this deployment goes in the project tree; a fact true
wherever the product appears goes in a library. The tie-breaker: would it stop being true if you
swapped the vendor? Yes means `product:<vendor>`; no means `general`. Never restate a fact across a
boundary — link it with `[[library:slug]]`.

**Provenance and currency per section**, not per file:

```
Source: [[some-source]]
Verified: 2026-09-22 · by: agent · method: query
```

No evidence, no stamp. An unstamped fact reads as `unknown`, which is honest; a stamp on something
nobody checked is not.

Where a **command can decide** the claim, write the assertion under the stamp:

```
Recheck: t=$(mktemp -d); … ; exit $r      # exit 0 = the fact still holds
```

`kb-verify <tree>` then re-runs the assertions of sections past their horizon. It prints the
commands and runs them only with `--yes`; a pass restamps only with `--apply`; **a failure is
reported and never applied**, because a failure may mean the fact is stale, the assertion is wrong,
or the world changed — three different repairs, and only a person picks between them. Stale sections
with no assertion are listed as needing a human, which is most of them.

**Author every assertion with its negative control.** Break the thing on purpose and confirm the
command notices. One of the first three written here could not fail, and would have certified a fact
forever.

**Contradictions are flagged, never resolved by whoever finds them.** Mark the narrowest unit —
split the disputed claim into its own subsection first, so its sound neighbours stay retrievable —
with `status: CONFLICTED · since: <date>`, state both claims, and register it in
`<domain>-contradictions.md`. A retrieval agent then refuses that section and surfaces the conflict.

**Every domain carries a golden set** (`<domain>-golden.md`): the questions that must be answerable,
with the file and excerpt that must answer them. It is deliberately **not routed**, and retrieval
agents must never read or search it — an agent that can reach the answer key proves nothing. Repair
it in the same change that invalidates it, or it quietly stops testing anything.

---

## What the hooks enforce

Every commit in a library or a project tree runs the engine's checks. They catch structure, never
meaning:

| Check | Refuses |
|---|---|
| `check-kb` | missing frontmatter, `name` that disagrees with the filename, dead links, slug collisions, **orphans** — any file no router reaches |
| `check-scope` | a scope value that disagrees with its library, a project tree holding general facts, a relative link climbing out of a library |
| `check-golden` | a golden record whose file is missing or whose excerpt is not in that file, too few negative cases |
| `check-xlinks` | a `[[library:slug]]` into an installed library that does not have that slug — from a library or from a project tree |
| `check-secrets`, `check-exec-bits`, `check-embedded-facts` | committed credentials, scripts git records non-executable, facts inlined into the behaviour layer |

`kb-verify` is **not** in the hooks: it executes commands, which is not something a commit should do
on your behalf.

**Changing a check?** `tests/run-checks` breaks one thing on purpose per case and requires the check
to notice. The engine's hook runs it when a commit touches `scripts/` or `tests/`, and CI runs it
every time. Add a case with the fix whenever a check misses something — all four checks that have
ever been wrong here were wrong in a way no existing case covered.

---

## The sweep cadence

A tree is due for a `kb-audit` sweep every `sweep_interval` — 30 days for a library, 14 for a
project tree, set in its `INDEX.md`. `kb-audit` writes `last_swept:` when it finishes, whether or
not it found anything: a clean sweep writes no queue file, so without that line nobody could tell a
clean sweep from one that never happened.

Session start tells you when something is due, and says nothing when nothing is. Ask for it yourself
any time:

```bash
kb-due "$KB_ENGINE_ROOT" knowledge      # the installed libraries, plus this project's tree
```

A clean run means structurally sound. It does not mean verified: nothing here checks whether a fact
is true, whether its source still says so, or whether it landed where a reader would look.

---

## When something looks wrong

**"knowledge: engine not found — structural checks skipped"** — this machine has no engine
registered. Run `kb-bootstrap`. The hook deliberately skips rather than failing, so an unconfigured
machine is not blocked from working, which does mean an unbootstrapped clone is unguarded.

**A commit went through unchecked** — either the above, or `core.hooksPath` is unset in that clone.
Run `kb-init` in it.

**A skill behaves like an older version** — plugin content is loaded once, at session start.
Restart the session. Files read with Read or Bash are live, which is why the two can disagree
mid-session.

**`orphan — no router reaches it`** — the file exists but nothing lists it, so retrieval will never
find it. Add its line to the right `INDEX.md`. The golden set and `documents/` are exempt by design.

**`scope 'x' disagrees with its library`** — the fact is in the wrong home. Move it, or link to it
from where it belongs rather than restating it.

---

## Adding a library

A library is its own repository, one domain, self-contained: its facts, its sources, its archived
evidence and its golden set travel together, so it stays useful wherever it is cloned. Use
`kb-create-domain` to scaffold one, give it a remote, and clone it into `kb/` on each machine that
needs it — then `kb-bootstrap` again to wire its hook.

Nothing registers a library anywhere. It is discovered by being present under `kb/`, and the session
hook enumerates what it finds. A machine that has not cloned a library gets a warning, never a
broken link: libraries are portable, and absence is not breakage.
