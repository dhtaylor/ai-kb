---
name: kb-audit
description: Sweep a knowledge base for decay — dead links, orphaned files, stale or missing currency stamps, index bloat, empty routed leaves, ageing contradictions and scope misfiling — and build a prioritised needs-attention queue. Detection only; it proposes and never mutates. Use as the acceptance gate after a wave of knowledge work, or as a recurring hygiene sweep. Do NOT use it to fix what it finds.
---

# kb-audit

The sweep. Its one discipline: **it detects and it reports. It does not fix.**

That split is the standing rule of the whole system. Being wrong about detection costs a glance at
a false flag; being wrong about mutation poisons the single source of truth everyone cites. A sweep
that helpfully tidies as it goes has silently crossed from the cheap side of that line to the
expensive one.

**Two kinds of repository.** Your session context names the **engine** (the contract, the tooling,
the skills) and the **libraries** installed under it at `kb/`. Behaviour and content are
separate repositories: the engine holds no domains, and each library is its own repository
holding exactly one. Write facts into a library, never into the engine.

**Read the contract first.** Your session context names the engine; the contract is
`<engine>/CONVENTIONS.md`. If the root is unconfigured, stop and say so.

## Step 1 — Run the mechanical checks first

Run the engine's checks and report each one's output verbatim:

- `scripts/check-kb <library>` — frontmatter completeness, `name`/filename agreement, link
  resolution, within-library slug uniqueness;
- `scripts/check-scope <library>` — scope values well-formed and in agreement with the library;
- `scripts/check-golden <library>` — every golden record well-formed, its file present, its excerpt
  present in that file;
- `scripts/check-xlinks <kb-root>` — `[[library:slug]]` references into other installed libraries
  (the `kb/` directory the library sits in; skip it for a project tree, which has no siblings).

A failure these report is already a finding — put it in the queue; do not re-derive it by hand.

Then state plainly what they do **not** cover, so nobody reads a clean run as a clean bill of
health: orphans, currency, contradiction ageing, whether the golden set's unresolved cases match
the domain's actual `CONFLICTED` sections, scope *content* (as opposed to scope labels), and
external `Source:` URL liveness.

## Step 2 — Find what the scripts cannot

These are the sweep's own work. Each is a real decay mode no current tool catches.

**Orphans.** A file that no router points at. `check-kb` verifies that links resolve, not that
every file is reachable — so an unrouted file passes every check and is invisible to retrieval.
Walk the library: every `.md` file should be a direct child of exactly one `INDEX.md` listing, or be
a router itself. Report every file nothing routes to.

**Two exemptions, and only two.** The golden set (`*-golden.md`) and archived evidence under
`documents/` are deliberately unrouted — apparatus and provenance, not knowledge. An agent that can
descend to the oracle can read the answers, so routing it would defeat the eval. Do not report
either as an orphan; do report a golden set that has gone missing entirely.

**Missing currency.** A section with a `Source:` but no `Verified:` stamp is `unknown`, not fresh,
and per the contract §7 it surfaces **first** — a sweep cannot flag what was never written, so the
absence is the finding.

**Stale currency.** A stamp older than its domain's `freshness_horizon`. Agent-verified stamps
expire at **one tenth** the human interval. High-blast-radius facts — deploy targets, environment
routing, credential references — are stale the moment their last stamp was written by an agent,
regardless of date.

**Index bloat.** A domain past roughly 15 topic files still flat. That is `kb-organize-domain`'s
trigger; report it, do not reshape.

**Empty routed leaves.** A router line pointing at a file that holds no content, or at a folder
with no children. The contract forbids creating these; they appear when content is removed.

**Ageing contradictions.** Every `status: CONFLICTED` marker and every entry in a
`<domain>-contradictions.md`. Report how long each has stood, whether it is blocking or
informational, and whether the two records agree with each other — an inline marker with no
register entry, or a register entry whose inline marker has vanished, is itself a finding.
Anything past **14 days** escalates.

**Scope misfiling.** `check-scope` catches a *label* that disagrees with its library; it cannot
catch a fact whose label is consistent but whose content is not — a deployment detail in a
`general` library, or one vendor's behavior filed as `general`. Sample rather than exhaustively audit, and say what you sampled.

**Golden-set rot.** Every `expected_file:` should name a file that exists, and every
`expected_excerpt:` should actually appear in it. Grep it; do not assume. Also check the set against
what §10 actually requires: every record carries a `case:` label, the domain has **≥2 negative
cases**, **≥1 unresolved case wherever the domain holds a `CONFLICTED` section** (a stated reason
does not excuse its absence when a conflict is live), and a cross-root case exists *or* the file says why it does not
apply. A domain with content and no golden set has no oracle at all — report that as a finding in
its own right. A rotted oracle is worse than a missing one: it reports success.

## Step 3 — Build the queue, do not fix the findings

Write findings to `<library>/needs-attention.md` — the queue belongs to the library it describes, not to the engine. Create it only if there are findings; an
empty queue file is an empty state leaf.

**The queue is a file like any other, and the sweep's own rules apply to it.** Give it full
frontmatter, and add its router line to the library's own `INDEX.md` — otherwise the file you just
wrote is an orphan that fails `check-kb`, and the next sweep dutifully reports your own output as a
finding.

```yaml
---
name: needs-attention
description: Open findings from the most recent hygiene sweep, by severity.
memory_type: reference
domain: <the library's domain, from its INDEX.md>
scope: <the library's scope, from its INDEX.md>
metadata:
  type: index
  node_type: memory
  created: <today>
tags: [meta, hygiene, queue]
keywords: [needs attention, queue, findings, sweep, stale, orphan]
---
```

Copy `domain:` and `scope:` from the library's own `INDEX.md` — never write `general` into a library
that is not. Every file in a library carries the library's scope (§1), the queue included, and
`check-scope` fails the library — and blocks the next commit — on one that does not.

Each item carries:

- a **stable ID** — the first 8 hex characters of the SHA-1 of `<category>|<file>|<section>` (the
  severity category's name as listed below, the library-relative path, the heading text or `-` for
  a whole-file finding) — so repeat sweeps, by any agent, **deduplicate** rather than re-raising
  what was already seen. Compute it (`printf '%s' 'orphan|webhooks.md|-' | sha1sum | cut -c1-8`);
  never invent it;
- a **status**: `open`, `acknowledged`, `resolved`. An acknowledged item is not re-raised unless its
  underlying source changes;
- the **owner**, from CODEOWNERS where one exists;
- a **severity**, triaged in this order — every finding type has a place, so nothing lands in an
  undefined middle:

  1. **blocking contradiction** — a disputed fact that is actively needed;
  2. **high-blast-radius fact unstamped or stale** — deploy targets, environment routing,
     credential references;
  3. **golden-set rot** — the oracle is wrong, so it reports success while testing nothing;
  4. **unstamped fact** (`unknown`) — ahead of stale, per §7: absence hides more easily than age;
  5. **stale fact** — past its domain horizon, agent stamps at one tenth the interval;
  6. **orphan** — real knowledge nothing can route to;
  7. **informational contradiction, empty routed leaf, index bloat, scope misfiling**.

  A contradiction is **blocking** only when something names it as needed — a consumer, a golden
  case, a caller in the task. When nothing in front of you establishes that either way, file it at
  severity 7 and write `blocking: undetermined`; never assume the answer in either direction. A
  malformed marker (no `since:`, no register entry) is the same item, with the defect stated;

  **Write the queue sorted by severity, 1 first**, and within a severity by age, oldest first;
- the **age**, and an escalation flag past 14 days. A `CONFLICTED` marker carries its own `since:`
  date (§8) and a stamp carries its date, so those are exact. Where no date exists — a golden-set
  record that silently drifted, an orphan nobody logged — say the age is **unknown** and name the
  proxy you used if you used one. Never present a proxy date as if it were the real one; an
  escalation clock built on invented ages escalates the wrong things.

**Cap what you raise per owner — default 10 per sweep.** One item is one defect: two defects in the
same place are two items, not one merged to fit under the cap. A queue nobody can work through is noise, and noise is how a
real finding gets ignored. If you are over the cap, raise the highest-severity items and say how
many you held back.

## Step 4 — Report

Give the acceptance verdict plainly: is this knowledge base in a state where the next wave of work
should proceed, or is something blocking? A blocking contradiction in a domain about to be promoted
is a stop, per the contract §8.

Say what you actually checked, what you sampled, and what you could not check because the tooling
does not exist. A sweep that implies more coverage than it had is worse than no sweep — it converts
an unknown into a false assurance.

## Refusals

- **Do not fix what you find.** Not the dead link, not the missing stamp, not the obvious typo in a
  router line. Every one of those is a mutation, and mutation is gated behind a human.
- Do not resolve a contradiction, delete a file, or re-stamp a `Verified:` date. Re-stamping in
  particular is manufacturing freshness — you did not re-verify anything, you ran a sweep.
- Do not report a clean sweep as a verified knowledge base. State the coverage gap every time.
