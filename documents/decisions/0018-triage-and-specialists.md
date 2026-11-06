# ADR-0018: Retrieval by triage and specialists

- **Status:** Proposed
- **Date:** 2026-11-06
- **Deciders:** Dandy Taylor
- **Amends:** [0011](0011-no-orchestrator-until-routing-fails.md) on acceptance. It supersedes "no
  orchestrator is built". The reopen trigger stays until the review trigger below is met.

## Context and problem statement

ADR-0011 built no orchestrator because `kb-retrieve`, one agent serving every library, already
routed as well as one would. It set a reopen trigger: routing below 95% on a golden-set sample, or
a library count that outgrows single-agent routing. Both have happened:

- **Routing dropped below 95%.** The full 138-case run scored 93.5% after the grader fix. The
  2026-10-26 retest scored 94.2%.
- **More libraries made it worse.** The 24-case subsample fell from 22/24 at 6 libraries to 18/24
  at 48.
- **Neighbors caused every failure:** stray reads, wrong `fact not found` refusals, and answers
  taken from the wrong library.

The owner's direction (#130) is that retrieval should work as triage plus specialists, so it scales,
using as few tokens as possible.

The design was measured before it was decided. The evidence is in
[`documents/eval-2026-11-05-triage-specialists/`](../eval-2026-11-05-triage-specialists/README.md).

## Considered options

- **A. Keep one agent for every library** (ADR-0011). The agent reads every router it judges
  relevant, which costs more as libraries are added. Its main session also rewrites the answer and
  drops the quotes and `Sources:` line: only 3 or 4 of 24 delivered answers kept them.
- **B. A triage subagent picks the library, and the main session starts the specialists.** A
  subagent cannot start other subagents, so triage has to hand back a pick. That adds an agent hop
  and its startup tokens to every question. Not built.
- **C. A triage desk in the main session, with specialists** (chosen, and measured). The desk is the
  `kb-ask` skill. It reads one generated catalog and starts one `kb-retrieve` specialist confined to
  one library. It asks a second library only when needed, never more than two, and passes the
  answer back unchanged.
- **D. A graph or embedding router.** Not tried. Every failure measured so far is between two
  libraries that both cover the topic. A better router cannot separate those; only the libraries'
  own scope statements can.

## Decision outcome

**Option C, adopted for what it measurably improves. It does not meet the routing target.**

### What is built

- **`scripts/kb-catalog`** prints each registered library's name, scope, description,
  `Not covered here:` line and router topics. It is built on demand from the root `INDEX.md` files,
  so it cannot go stale. A registered library that is not served is named, not dropped. At 6
  libraries it is about 4 KB.
- **`kb-retrieve` gets a specialist mode.** It switches on when a prompt begins
  `SPECIALIST: <library>`, and it confines the agent to that library:
  - **`not mine`:** the agent answers this after reading only the root router, when the topic is
    outside the library. It is distinct from `fact not found`, which means the topic is covered but
    the fact isn't held.
  - **Links into other libraries** are reported for the desk to decide, not followed.
  - **The rest of the retrieval contract is unchanged.**
- **The `kb-ask` skill is the desk.** It sends the question to one specialist. It asks a second only
  after `not mine` or `fact not found` (the referred library, or its runner-up), or for a question
  that needs facts from two libraries, never more than two. It passes answers back word for word,
  and flags two answers to one question as an overlap rather than choosing one. It never answers
  from the catalog or from memory.
- **New `triage` tool tier (Bash, Agent).** `check-tool-scope` gains it. The desk reads no library,
  so it declares no Read.

### What the measurement found

On the 24-case subsample, one trial per case:

| | Today's agent, 6 libraries | `kb-ask`, 6 libraries | Today's agent, 48 libraries | `kb-ask`, 48 libraries |
|---|---|---|---|---|
| Routing | 23/24 | 23/24 (adjusted) | 19/24 | 20/24 |
| Delivered with quotes and sources | 4/24 | 23/24 | 3/24 | 21/24 |
| Answered from the wrong library | 0 | 0 | 0 | 2 |
| Specialist tokens/question | 19.0k | 7.1k | 25.5k | 10.4k |
| Cost/question | $0.161 | $0.137 | $0.196 | $0.193 |

#130's acceptance targets, against those results:

- **At 6 libraries, no accuracy loss and no more than 1.3× today's tokens: met.** Routing was
  equal, and total tokens came in at 0.77×.
- **At 48 libraries, fewer tokens than the single agent: met.** Total tokens came in at 0.89×.
  Cost per question is about equal, because the catalog sits in the main session's context.
- **Routing at least 95% at 48 libraries: not met.** `kb-ask` scored 83% and today's agent 79%.
- **No answers from the wrong library: not met.** The red-team-analysis decoy answered two
  intelligence-analysis questions, because it holds devil's advocacy and pre-mortem material too.

### Why adopt it without meeting the routing target

- **It delivers the citation.** The specialist's quotes and `Sources:` line reach the person 21 to
  23 times in 24, against 3 or 4. That is the contract's purpose, and today's route loses it after
  retrieval succeeds.
- **Specialists cost a third as much,** and that share stays roughly flat as libraries are added.
- **Routing is no worse,** and the remaining failures are between libraries that both cover the
  topic. Neither design can separate those. That is a library-scope problem, and the lever for it is
  the `Not covered here:` line, which the decoys lack.

## Consequences

**Good.**

- The answer a person receives keeps the quotes and sources the specialist found.
- A wrong first pick becomes a second question, not a wrong refusal.
- A cost rule replaces a hope: one specialist in the normal case, two at most, and nothing
  broadcast.

**Bad.**

- **Router topics cut both ways.** They fixed a question whose topic was missing from a description,
  but they also drew a question to a neighbor whose topic name matched.
- **The catalog grows with the library count** and sits in the main session's context. Past
  roughly 15 libraries, the plan's sub-catalog split (§5A "Bound INDEX size") will be needed.
- **The desk runs on whatever model the main session uses.** It was measured on Sonnet only.
- **`kb-ask` is the default entry point** (owner's decision, 2026-11-06). Its description says
  so. `kb-retrieve`'s description calls it the specialist that `kb-ask` starts, to be called
  directly only when the library is already known. A session can still call it directly, and then
  it does its own triage as before.

**Neutral.**

- `grade-routing` counts a read into a library the desk then rejected as a routing failure, even
  when the delivered answer is right (az Q6). That stays: a stray read is still a read.

## Delivery

1. **This pull request** adds `kb-catalog`, specialist mode, `kb-ask` as the default entry point,
   the `triage` tier, their tests, and the evidence.
2. **A rerun with decoys that carry a `Not covered here:` line,** at 6 and 48 libraries, using the
   final skill on all 24 cases.
3. **Measure the entry point in normal use.** `kb-telemetry` counts `kb-retrieve` runs. A rise
   in direct runs, which carry no `SPECIALIST:` prompt, would show sessions bypassing the desk.

## Review trigger

**Accept this ADR**, and close ADR-0011's reopen trigger, when `kb-ask` routes at least 95% at 48
libraries with no answer from the wrong library, on decoys that carry a `Not covered here:` line.

**Reject it** if neighbors that state their scope still draw questions they don't cover: the
problem is then the libraries' boundaries, not the router.
