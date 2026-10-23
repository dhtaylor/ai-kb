# Working with the knowledge base

New to capturing a fact? Read [CAPTURE.md](CAPTURE.md) first — one page, nothing else required.

This repository is the **engine**: the contract, the tooling and the skills. It holds no facts.
Facts live in **domain libraries** — one repository per domain, cloned anywhere and registered on
the machine — and in each
project's own `knowledge/` tree. The separation is the point: behaviour here, knowledge there, and
neither pretending to be the other.

[CONVENTIONS.md](CONVENTIONS.md) is the contract and settles anything this guide leaves open. This
is the path through it, not a summary of it.

---

## Setting up a machine

```bash
git clone https://github.com/dhtaylor/ai-kb.git ~/kb-engine      # the engine, anywhere you like
~/kb-engine/scripts/kb-bootstrap --apply                         # register the engine on this machine
~/kb-engine/scripts/kb-library add <library-git-url>             # each library you need
```

`kb-library add <git-url>` clones into the **library home** and registers the clone. The home is
`<engine>/kb/` unless you choose another: `kb-bootstrap --apply --library-home <dir>` records it, and
`KB_LIBRARY_HOME` overrides it for one shell. `kb-library add <path>` registers a library you have
already cloned anywhere. Setting up a second machine with the same libraries is
`kb-library export > libraries.txt` on the first and `kb-library import libraries.txt` on the second:
the export carries each library's name and origin, never a path.

The engine is wherever the script lives; nothing else is typed. `kb-bootstrap` writes
`~/.claude/settings.json` (the engine path, the plugin, the session hook), `git config --global
kb.engineRoot` and a `PATH` block in your shell rc, and points each registered library's local
`core.hooksPath` at the engine's library hook — but only with `--apply`. It merges with what is
already there, backs a file up before changing it, and is safe to run again — run it again whenever
the engine moves. `kb-library add` registers a library in `~/.config/ai-kb/libraries` and wires its
hook; it writes nothing into the library itself. `kb-library list` shows what is registered.

**Then restart your terminal and any open Claude Code session.** A shell profile is read at shell
start, and Claude reads its settings and plugin content once per session.

**Gated, like `kb-verify`.** Run with no flag (or `--check`) at any time to see what it would do
without changing anything:

```bash
kb-bootstrap               # reports drift, changes nothing, exits 1 if anything is out of step
kb-bootstrap --check       # the same, spelled out
kb-bootstrap --apply       # makes the changes above
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
a dated note under `knowledge/episodic/` in the nearest tree and routes it, unless the body holds a credential or personal identifier, in which case it is refused.

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
router and cites every file its answer rests on. It refuses a disputed fact with "disputed — not
served", setting out both claims and citing the file that holds the conflict. It says "fact not
found — check KB" when the knowledge base is silent, citing nothing and naming what it checked.
It answers only from the knowledge base — not from the code or config beside it. Reading
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

**Where files go in a library.** Two folders are easy to confuse:

| Folder | Holds | Example |
|---|---|---|
| `sources/` | only `.md` **citation stubs**: title, origin, date ingested, and where the artifact lives. Routed, and what a `Source:` line cites | `sources/billing-schema.md` |
| `documents/` | the **artifacts themselves**, archived verbatim so a citation resolves on any machine. Not routed | `documents/billing-schema/*.sql`, the ERD export |

A schema dump, an ERD, a PDF or a pasted document goes in `documents/`, with one stub in `sources/`
pointing at it. Archive text as UTF-8, and redact any credential first (`CONVENTIONS.md` §6). The
secret scan reads raw artifacts under `documents/` without the rule that flags long identifiers, so
a schema dump does not drown in false alarms; under `sources/` it would, and `check-kb` rejects it
there anyway.

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

`kb-sources <tree>` does the same for external URLs: it lists every URL a source stub cites and the
fact sections that depend on it, and fetches nothing until you approve with `--yes`. A dead or
unreachable URL is queued to the library's `needs-attention.md`; no fact or stub is edited or marked.

**Author every assertion with its negative control.** Break the thing on purpose and confirm the
command notices. One of the first three written here could not fail, and would have certified a fact
forever.

**Contradictions are flagged, never resolved by whoever finds them.** Mark the narrowest unit —
split the disputed claim into its own subsection first, so its sound neighbours stay retrievable —
with `status: CONFLICTED · since: <date>`, state both claims, and register it in
`<domain>-contradictions.md`. A retrieval agent then refuses that section and surfaces the conflict.

**Every domain carries a golden set** (`<domain>-golden.md`): the questions that must be answerable,
with the file and excerpt that must answer them. It is deliberately **not routed**, and retrieval
agents must never read or search it — an agent that can reach the answer key proves nothing. The same
goes for eval evidence kept under a library's `documents/eval-<date>/`, which records earlier answers
to the same questions. Repair the golden set in the same change that invalidates it, or it quietly
stops testing anything.

Two record rules catch people out (the full set is in [CONVENTIONS.md](CONVENTIONS.md) §10):

- **An `unresolved` case** exists only where the domain really holds a `CONFLICTED` section. Its
  `expected_file` is that file, and its `expected_excerpt` is exactly `disputed — not served`, the
  refusal an agent must give.
- **`alt_excerpt:`** (optional, repeatable, positive and cross-root cases only) names a second
  sentence in the same file stating the same fact, so an agent quoting either one is grounded. One
  added after seeing results is an amendment: record it beside the record.

---

## What the hooks enforce

Every commit in a library or a project tree runs the engine's checks. They catch structure, never
meaning:

| Check | Refuses |
|---|---|
| `check-kb` | missing frontmatter, `name` that disagrees with the filename, dead links, slug collisions, **orphans** — any file no router reaches |
| `check-scope` | a scope value that disagrees with its library, a project tree holding general facts, a relative link climbing out of a library |
| `check-golden` | a golden record whose file is missing, no router reaches, or whose excerpt (or `alt_excerpt`) is not in that file, too few negative cases, an `unresolved` case without the exact refusal phrase or pointing at a file with no `CONFLICTED` section |
| `check-xlinks` | a `[[library:slug]]` into an installed library that does not have that slug — from a library or from a project tree |
| `check-secrets`, `check-exec-bits`, `check-embedded-facts` | committed credentials, scripts git records non-executable, facts inlined into the behaviour layer |
| `check-stamps` (CI only — the engine's and every library's; it reads commit messages, which a pre-commit hook never sees) | a commit that announces agent co-authorship and also stamps a fact `by: human` — which would buy ten times the re-check interval |

`grade-routing` is **not** in the hooks either: it grades a subagent transcript a person ran, to check an agent routed to the expected file ([ADR-0013](documents/decisions/0013-steady-state-surfaced-not-scheduled.md)).

`kb-verify` and `kb-sources` are **not** in the hooks: one executes commands and the other opens
network connections, neither of which is something a commit should do on your behalf.

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

### Keeping libraries current without remembering

One command turns on a weekly job; nothing runs until you do
([ADR-0017](documents/decisions/0017-unattended-preparation-attended-decisions.md)):

```bash
kb-schedule install              # detection and the weekly report only
kb-schedule install --prepare    # also draft review packets with a capped, read-only model run
kb-schedule status               # installed?, next run, last run
kb-schedule remove               # takes it all out again
```

Every Monday at 07:00 (or at the next start, if the machine was off), it re-runs the rechecks that
need no person, checks cited URLs and watched sources, and, with `--prepare`, drafts what
`kb-distill` and `kb-audit` would propose. Then it writes the week's report of decisions to
`~/.local/state/ai-kb/reports/`. It never edits a fact. When the session-start nudge names the
report, open it. For a packet, ask a session to review it: the skill re-checks it, asks you to
decide each item, and only then writes.

### Commands you can schedule

A command is **schedulable** when it is safe to run unattended, from cron, a systemd timer or
`kb-schedule` ([ADR-0017](documents/decisions/0017-unattended-preparation-attended-decisions.md)).
That means:

- It never prompts.
- It works from any directory, with no shell startup files: `env -i HOME=… PATH=/usr/bin:/bin` from `/`.
- Exit 0 means clean, 1 means findings, 2 means it could not run.
- It never prints a fact's or a source's text, or a secret-check hit. It prints paths, headings, URLs,
  counts and ids. Assertion output and drifted values still reach a person at a terminal.
- It is idempotent, and a queue write replaces the file in one rename, so it can run beside a
  session working in the same library.

| Command | Schedulable form | Exit codes |
|---|---|---|
| `kb-verify` | `kb-verify <library> --yes --unattended`: skips `Recheck (attended):`, runs the rest with no inherited credentials, refuses `--apply` | 0 / 1 / 2 |
| `kb-sources` | `kb-sources <library-or-kb> --yes` | 0 / 1 / 2 |
| `kb-watch` | `kb-watch <allowlist.json>` | 0 / 1 / 2 |
| `check-xlinks` | `check-xlinks --installed` | 0 / 1 / 2 |
| `check-secrets` | `check-secrets --redact < in > out`, a filter: 0 nothing redacted, 1 redacted (output safe), 2 could not scan (no output) | 0 / 1 / 2 |
| `kb-prepare` | `kb-prepare distill\|audit <library>`: a capped, read-only model run, only when due (ADR-0017) | 0 nothing to decide / 1 packet waiting / 2 |
| `kb-apply` | `kb-apply list` | 0 none waiting / 1 waiting / 2 |
| `kb-report` | `kb-report`: the weekly decisions report, outside every library (ADR-0017) | 0 nothing to decide / 1 decisions / 2 |
| `kb-schedule` | `kb-schedule run`: the weekly job itself; logs exit codes only | 0 ran (findings included) / 2 a step could not run |
| `kb-due` | `kb-due … --nudge` | always 0: it is a reminder, and the session hook reads any other exit as a failure |

Each row is a regression case in `tests/run-checks`, run from `/` with a stripped environment
against fixtures that carry a canary in the text a careless command would echo.

---

## When something looks wrong

**"knowledge: engine not found — structural and secret checks skipped"** — this machine has no engine
registered. Run `kb-bootstrap --apply`. The hook deliberately skips rather than failing, so an
unconfigured machine is not blocked from working, which does mean an unbootstrapped clone is
unguarded.

**A commit went through unchecked** — either the above, or `core.hooksPath` is unset in that clone.
Run `kb-init` in it.

**A skill behaves like an older version** — plugin content is loaded once, at session start.
Restart the session. Files read with Read or Bash are live, which is why the two can disagree
mid-session.

**`orphan — no router reaches it`** — the file exists but nothing lists it, so retrieval will never
find it. Add its line to the right `INDEX.md`. The golden set and `documents/` are exempt by design.

**`raw artifact in sources/`** — a non-`.md` file is in the folder for citation stubs. Move it to
`documents/` and write (or point) a stub in `sources/` at it.

**`scope 'x' disagrees with its library`** — the fact is in the wrong home. Move it, or link to it
from where it belongs rather than restating it.

---

## Adding a library

A library is its own repository, one domain, self-contained: its facts, its sources, its archived
evidence and its golden set travel together, so it stays useful wherever it is cloned. Use
`kb-create-domain` to scaffold one, give it a remote, and on each machine that needs it clone it
anywhere and run `kb-library add <path>`. That registers it under the name its `INDEX.md` declares and
wires its clone to the engine's hook. It writes nothing into the library, which may belong to someone
else.

A library is installed by being registered on the machine (ADR-0014). `kb-library list` shows what is
registered and whether each is servable; the session hook lists the same and names any that went
missing. A machine that has not cloned a library gets a warning, never a
broken link: libraries are portable, and absence is not breakage.
