# ADR-0007: The engine holds no knowledge; content lives in per-domain library repositories

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Amends:** [0003](0003-scoping-topology.md), [0006](0006-behaviour-distribution.md)

## Context and problem statement

[ADR-0006](0006-behaviour-distribution.md) made the knowledge base its own repository, carrying the
contract, the tooling, the decisions, the behaviour **and the facts**. That last inclusion is the
problem.

The design thesis this whole architecture rests on is *separate knowledge from behaviour*. The
engine was doing both in one repository — the single place where the separation most needs to be
visible, because everything downstream follows its example. A repository that asserts the principle
in its own contract and violates it in its own layout teaches the violation.

There is also a practical failure. With one general tier there was one shared `sources/`, one
`golden-retrieval/`, one router chain. A domain could not be moved, shared or cloned without
dragging the rest of the tier with it, and every citation it made was a citation into a tree it did
not own.

## Decision outcome

**The engine holds no domains. Content lives in per-domain library repositories, installed under
the engine's `kb/`, which the engine creates and never tracks.**

```
<engine>/                 ai-kb — behaviour only
  CONVENTIONS.md          the contract
  scripts/  plugins/  documents/decisions/
  kb/                     created by the engine, gitignored by the engine
    <domain>/             its own repository, exactly one domain
```

- **One repository per domain.** A library is self-contained: its facts, its `sources/`, its
  archived evidence and its golden set travel together. Clone it onto a machine with no engine and
  no sibling libraries and it still makes sense.
- **No router chain, no registry.** `INDEX.md` at the library root *is* the domain router. Libraries
  are discovered by being present under `kb/`; the session-start hook enumerates them. A registry
  would have to live in the engine, which does not track `kb/` — so it would be untracked state that
  drifts, or tracked state that lies on every machine with a different set installed.
- **The engine's own checks changed.** `check-kb` now requires an explicit target, because the
  engine has no knowledge to check and a silent default would report a clean run over zero files —
  coverage that does not exist. The engine's pre-commit runs the secret scan and the embedded-fact
  lint only; `check-kb` is exercised by each library's own hook.

### Cross-repository citation — the rule this forces

Splitting content into libraries makes cross-repo citation structural rather than accidental. Three
cases, and only one is hard:

1. **Inside the library** — `[[slug]]` or a relative path. Unchanged.
2. **Never in any repository** (a vendor page, a spec) — the stub records origin, not a path.
3. **In another repository** — two rules, in order:
   - **Evidence travels with the domain it was folded from.** Archive the artifact in the library's
     `documents/`. This is not a single-canonical-home violation: **the rule is one home per fact,
     not per document.** A fact stated twice drifts because someone edits a copy; an archived
     artifact does not, because if it changes it is a new artifact with a new ingestion date.
   - **What cannot travel gets a repo-qualified reference** — `ai-kb:CONVENTIONS.md`,
     `<repo>:<path>`. **Never a relative path across a repository boundary.** That resolves only
     while two repositories sit in the expected layout and fails silently everywhere else. The
     qualified form degrades honestly: without the other repository you still know exactly what was
     cited, you simply cannot open it.

This was not theoretical. Extracting the first library broke eight `[[adr-…]]` links immediately —
they pointed at stubs that had lived in the engine's shared `sources/`. The rule was applied on
contact rather than designed in the abstract.

## Consequences

**Good.** The engine demonstrates the principle it asserts. A library is portable, shareable and
independently versioned — research a topic, curate it into a library, hand the library to someone
else without handing over an engine or anyone else's domains. The six ADR stubs disappeared
entirely: the engine's own documents are in one repository and reach each other by ordinary relative
links, so the `[[slug]]` machinery is reserved for what it was built for.

**Bad.** There are now three kinds of repository to keep straight, and a domain library has no
guardrails of its own — its hook borrows the engine's checkers and skips when it cannot find them.
A library cloned alone is unguarded until an engine is in reach, which is the price of not making it
depend on one.

**Open.** `[[slug]]` resolution *across* libraries is undefined. Within a library it works; between
two installed libraries there is no resolver, no manifest and no uniqueness constraint. That was the
cross-root problem ADR-0003 deferred, and splitting into N libraries multiplies rather than solves
it. Nothing depends on it yet — there is one library — and it blocks any second one that needs to
cite the first.

## Review trigger

Revisit when a second library needs to cite a first, which is the point the cross-library resolver
stops being deferrable.
