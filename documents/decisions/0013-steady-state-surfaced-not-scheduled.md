# ADR-0013: Steady state is surfaced when due, not run unattended

- **Status:** Accepted
- **Date:** 2026-10-01
- **Deciders:** Dandy Taylor

## Context and problem statement

Phase 5 of the combination plan asks for a one-page contributor guide, a standing Verifier and
Watcher feeding the needs-attention queue, per-domain freshness horizons, `kb-distill` on a cadence
and `kb-audit` on a schedule. Its exit criteria are that a contributor who has read only the guide
can capture a fact correctly, and that stale or drifted facts surface as a queue rather than rotting
silently.

Two of those words carried hidden choices. A "schedule" can mean a job that runs unattended, or a
reminder that something is due. A "standing" Watcher can mean one that fetches pages on its own, or
one that compares pages someone saved. Both choices trade automation against attack surface,
credentials and runs nobody watches. On a one-maintainer system (ADR-0012) the trade comes out
differently than it would for a team.

## Decision outcome

### Cadence is a nudge at session start

`kb-audit` and `kb-distill` both need an agent and a human decision, so they are not run unattended.
The SessionStart hook calls `kb-due --nudge`, which reports only what is due, per library:

- a sweep;
- facts due for recheck, counted with `kb-verify`'s own staleness logic, never executing an
  assertion;
- open queue items;
- episodic notes awaiting distillation.

It prints nothing when nothing is due, never prompts or writes, and runs in about a third of a
second. "Scheduled" here means "surfaced when due". A cloud routine and a local cron job were both
considered and declined: each runs without the owner watching, and the cloud routine would need
credentials for private library repositories.

A note counts as distilled when it carries a heading beginning `## Distill`. kb-distill's Step 5 now
names the canonical `## Distilled`, and the prefix also matches older notes' `## Distillation
record`. Counting every note instead would have asked about the same, already-distilled notes
forever, which is how a nudge becomes noise nobody reads.

### The Verifier and the Watcher both feed one queue, which they route

`kb-verify --yes` writes each failed assertion to the owning library's `needs-attention.md`.
`kb-watch` writes drift and unreachable signals to the same file, and `kb-verify` imports
`kb-watch`'s queue primitives so the two writers cannot drift apart. Neither writer edits a fact, and
only a human resolves an entry. Both now add the queue's router line to the library's `INDEX.md`, as
CONVENTIONS §3 and `kb-audit` require. An unrouted queue is an orphan that fails `check-kb`, which
would have blocked every commit in that library until someone routed it by hand.

### The Watcher's snapshots are saved by hand and kept local

`kb-watch` stays offline and model-free (ADR-0012). The owner, or a session at the owner's request,
saves a source's page, and `kb-watch` compares it against the baseline. The first watched source is
the Microsoft Learn page behind Claim B of the azure-devops CONFLICTED fact, because a change to it
bears directly on resolving that dispute. `watcher/snapshots/` is gitignored: this repository is
public, and the snapshots are copies of third-party pages. A fresh clone therefore reports every
source as `unreachable` until its snapshots are saved, which is the true answer.

### The guide is one page, and it was tested

`CAPTURE.md` is 70 lines. A fresh agent given only that page captured a realistic debugging session
correctly: the right tree, observation kept apart from hedged belief, a teammate's claim attributed,
a live password kept out. Its feedback closed three gaps in the page. `CONTRIBUTING.md` remains the
full reference.

## Consequences

- **Good:** both exit criteria are regression tests. The capture test is a recorded behavioural run,
  and the queue criterion is one end-to-end fixture: a stale fact and a drifted source both reach the
  queue and the nudge, the fact stays untouched, and `check-kb` stays clean.
- **Bad:** nothing happens unless a session starts. A library nobody opens goes unswept, and nobody
  is told. That is acceptable for one person who works in these repositories daily, and it is the
  first thing to revisit if the libraries gain readers who are not maintainers.
- **Bad:** a watched source is only as fresh as its last saved snapshot. The Watcher detects drift
  between two copies; it does not notice that a copy has gone stale. An isolated fetcher was
  declined for now, and adding one is a separate decision with its own security review (§5A).
