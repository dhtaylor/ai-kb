# ADR-0011: No orchestrator is built until retrieval's own routing is shown to fall short

- **Status:** Accepted
- **Date:** 2026-09-28
- **Deciders:** Dandy Taylor

## Context and problem statement

Phase 4 of the combination plan calls for "a thin orchestrator (routes, capped fan-out, §5A) over
the domain workers." §5A says why: "Orchestrator routes, never broadcasts." A single-domain query
should pass through to one worker, and fan-out happens only for a confirmed cross-domain question,
capped at 2 workers, because broadcasting to every worker multiplies token cost several times over.

The plan assumed one worker per domain. The system that was actually built has a different shape.
One retrieval agent, `kb-retrieve`, serves every library. Libraries are found by globbing
`kb/*/INDEX.md`, and each library's `INDEX.md` is its only router (ADR-0007). So the routing an
orchestrator would do is already the first step of `kb-retrieve`'s contract: "Start at a router,
never at a guess," and "One library unless the question genuinely spans two."

The question was whether that routing is good enough, or whether a separate routing layer earns its
cost.

## Considered options

1. **Build the orchestrator as specified.** It would read the routers, classify each question,
   dispatch at most two `kb-retrieve` workers each limited to one library, and merge their
   citations. This follows the plan's wording, but to route it must read the same six routers that
   `kb-retrieve` reads today. That adds an agent hop and a merge step, and removes no reads.
2. **Measure first, and build only if routing falls short.** Put a sample of golden-set questions
   from every library through `kb-retrieve`, and record which library each answer came from and
   which libraries each agent opened.

## Decision outcome

**Option 2.** A sample was measured on 2026-09-28: two questions from each of the six libraries,
drawn by a seeded random draw from their golden sets, including azure-devops's cross-root case. The
questions went to three `kb-retrieve` agents, four questions each, with the libraries mixed. The
evidence is in `documents/eval-2026-09-28-routing-sample/`.

- **Right library: 12 of 12.** Every answer quoted its source from the library that holds it.
- **Expected file: 11 of 12.** On the cross-root question, the agent answered correctly from both
  libraries. It cited azure-devops's router rather than the file that carries the cross-library
  link.
- **Content read from a library the question did not need: none.** Beyond the routers, each agent
  opened only the one library the answer came from, or two on the cross-root question. That is the
  pass-through and the two-worker cap the plan asks of an orchestrator.
- **The only overhead was reading the routers.** Each agent read all six `INDEX.md` files once. An
  orchestrator would have to read the same files to route.

`kb-retrieve` already does what the orchestrator was specified to do, so no orchestrator is built.

### When to revisit

Reopen this decision when any of these holds:

- **Routing accuracy falls below 95%** on a golden-set sample, or a full run.
- **The library count outgrows single-agent routing.** Reading every router stops being cheap well
  before the plan's ~15-topic sub-index threshold (§5A "Bound INDEX size") applies to the library
  set itself. When it does, the plan's parallel index reads and a routing layer start to pay.
- **A real need for several workers appears:** a question that needs specialised workers with
  different tools, or workers operating on behalf of different people. One read-only retrieval
  agent cannot serve that.

## Consequences

- **Good:** there is one fewer agent to keep in step with the contract, and no merge step where
  citations could be dropped. The plan's cost bound is met by the retrieval contract itself.
- **Bad:** the evidence is a sample of 12 questions, not all ~90. Each agent answered four
  questions, so its router reads were shared across them; a question asked alone pays for all six
  routers. That stays cheap at six libraries, and is the first thing to watch as the number grows.
- **Neutral:** Phase 4's exit criteria never depended on the orchestrator. They are the Verifier
  fixture test, the Watcher replay test, and the high-blast-radius policy. The plan's Phase 4 entry
  is amended to cite this ADR.
