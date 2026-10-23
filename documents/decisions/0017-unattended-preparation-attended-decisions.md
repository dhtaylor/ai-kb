# ADR-0017: Prepare unattended, decide attended, report weekly

- **Status:** Accepted
- **Date:** 2026-10-23
- **Deciders:** Dandy Taylor
- **Amends:** [0013](0013-steady-state-surfaced-not-scheduled.md) (supersedes "Cadence is a nudge at
  session start" where it declines every unattended run; the nudge itself, the queue routing, the
  offline Watcher and the capture guide stand)

## Context and problem statement

ADR-0013 runs nothing unattended. `kb-audit` and `kb-distill` "both need an agent and a human
decision", and the mechanical checks run when a person types them. The session-start nudge says what is
due. Its own consequences named the weak point: "nothing happens unless a session starts", to be
revisited "if the libraries gain readers who are not maintainers".

That point has arrived in normal use. Keeping a library current costs a person a session, a command per
library per check, and a wait before there is anything to decide. The nudge reports work, so it grows
when nobody does the work, and it becomes a list of chores rather than a list of decisions. Every
consumer who tires of this writes their own cron wrapper, and the failures come from those wrappers:
#95 records one that reported FAIL for every backup for a week because cron started it in `$HOME`.

ADR-0013 bundled two things in "needs an agent and a human decision". The legwork (finding what is due,
extracting what a note says, building the side-by-side table a reviewer reads) needs an agent, not a
person. Only the decision needs a person. Fact edits must stay attended, and that is the constraint
this decision keeps.

## Considered options

- **A. The engine ships an opt-in schedule that runs the preparation half, and a weekly report of what
  needs deciding** (chosen).
- **B. Make commands safe to schedule, and leave scheduling to the consumer.** The engine documents a
  cron line. Each consumer still has to set it up and remember it does not exist on a new machine, and
  each writes the wrapper where the failures live.
- **C. A cloud routine.** Runs while the machine is off, but needs credentials for private library
  repositories. ADR-0013 declined it for that reason, and nothing has changed it.
- **D. Keep ADR-0013.** The cost above stays, and grows with the number of libraries.

## Decision outcome

### Each curation skill splits at its existing review gate

- **Prepare** may run unattended. It covers everything up to the gate a skill already has: `kb-distill`'s
  extraction and its fact/source table, and `kb-audit`'s findings. The result is a **review packet**,
  written outside every library and never committed.
- **Decide** is always attended. A person reads the packet and approves, edits or rejects each item.
  Only then does `kb-apply` change a fact file, run the checks and commit.

Only `kb-distill` and `kb-audit` get a prepare step. `kb-update-domain` folds external material and
`kb-organize-domain` reshapes structure; both stay fully attended. A packet records the library commit
it was drafted against, and `kb-apply` re-validates it when the library has moved since.

### What may run unattended, and only when installed

The schedule is opt-in: nothing runs unless the user installs it with `kb-schedule install`, and
`kb-schedule remove` leaves no trace. It runs weekly as a systemd user timer that catches up on a missed
week, or a crontab entry where there is no systemd. It runs, per registered library:

1. Detection, which only ever queues (ADR-0005 §4's first band): `kb-verify` on assertions that need no
   credentials (#100), `kb-sources --yes`, `kb-watch`, `check-xlinks`. Installing the schedule is the
   consent `--yes` asks for.
2. Preparation, a second opt-in at install time, because it is a model run that costs money: the
   headless prepare runs, under a dollar cap per run.
3. The report.

Every command the schedule runs must have the schedulable property (#95): it never prompts, does not
depend on the working directory or shell startup files, never prints fact or source content, and gives
distinct exit codes for clean, findings and tool error.

### A headless run cannot write

The prepare run is `claude -p` given only `Read`, `Grep` and `Glob` (`--tools`), with no MCP servers, no
session persistence and a `--max-budget-usd` cap. It has no write, shell or network tool at all, so it
cannot change a library or send what it reads anywhere. This is enforcement, not instruction. A skill's
`allowed-tools:` only pre-approves (see `documents/tool-scope-matrix.md`), and the `--tools` list is
what removes the tools. Verified on Claude Code 2.1.309: a `-p` run with that list, told to overwrite a
file by any means, reported it had no tool to do so, and the file was unchanged.

The packet comes back on standard output. The engine's wrapper writes it, after
`check-secrets --redact` (#101) has replaced any flagged line, because a packet quotes source text.
Episodic notes can carry text that reads as instructions. A run that can only read, and whose output a
person reviews, can produce a bad packet but cannot act on one.

### Done is a weekly report of decisions

`kb-report` writes one dated file a week, outside every library, listing only what needs a person, per
library:

- packets waiting, each with the command that applies it;
- failed rechecks and drifted or dead sources;
- queue items older than the last report;
- a library behind the contract or on an unsupported one.

When nothing needs a decision, it says so in one line. The session-start nudge (ADR-0013) adds one
line naming the report and how many decisions wait.

### Still never automated

Resolving a `CONFLICTED` section, deleting knowledge, promoting scope, writing a human stamp, applying
`owner-approved`, and any fact edit without a person's approval. `check-blast` still gates the first
three. The schedule stores no credentials.

## Consequences

**Good.**

- A person keeping libraries current runs no commands and remembers nothing after one install. They
  read a weekly list of decisions, and each decision arrives with the legwork done.
- The no-write guarantee is the engine's, tested, rather than each consumer's wrapper.
- A consumer who installs nothing sees no change.

**Bad.**

- A model runs unattended over library content and episodic notes. The read-only tool list bounds what
  it can do, not what it concludes, so a packet can be wrong in ways that read as right. The packet
  shows each item's source excerpt beside it so the reviewer can check rather than trust. The review is
  the control.
- The schedule runs only while the machine is up. Without systemd lingering, a user timer runs only
  while the user is logged in, and a WSL distribution stops when it is idle. Catch-up depends on
  `Persistent=true` and on the machine being used.
- Preparation spends money every week, whether or not anyone reads the report. The cap bounds it, and
  preparation is off unless chosen.
- More moving parts in the engine: a scheduler, a packet format and an apply step, each with its own
  failure modes and tests.

## Delivery

In order, each its own pull request: #95 (schedulable), #100 (credential-free recheck), #101 (redact
filter), #99 (prepare and `kb-apply`, with the no-write test), #102 (`kb-report`), #103
(`kb-schedule`). Then #96 (`kb-backup`) and #97 (retrieval telemetry), which can be scheduled but do
not keep a library current, so they slip first.

## Review trigger

Revisit when a packet is applied that a reviewer later finds wrong, when the weekly report goes unread
for a month, or when a cloud schedule can run without stored credentials.
