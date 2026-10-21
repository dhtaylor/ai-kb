# ADR-0016: The library contract is versioned, and pinning is the library's business

- **Status:** Accepted
- **Date:** 2026-10-21
- **Deciders:** Dandy Taylor
- **Amends:** [0015](0015-releases-and-pinning.md) (supersedes its "Library CI pins the engine to a
  release tag" section and the engine-version half of "A library release records the engine it was
  verified against"; its semantic versioning of the engine stands)

## Context and problem statement

ADR-0015 made every library's CI pin the engine to a release tag, and made each engine release move
those pins. That assumes the engine's maintainer knows every library. The engine is meant for wide
adoption, so the expected case is the opposite: thousands of libraries, built and owned by people the
engine's maintainer will never hear of. ADR-0015's own review trigger ("a library is maintained by
someone who is not the engine's maintainer") is the normal state, not an exception.

Two things follow. The engine cannot coordinate libraries' upgrades, so whether and how a library pins
an engine is outside what the engine can decide. And a library's author needs something stable to
build against that is not the engine's code: a published statement of what a library must hold to
work, versioned so a library can say which statement it was built to.

The pressing case is #71, merged and unreleased: `check-kb` now fails a non-`.md` file under
`sources/`. Released as it stands, it would fail libraries nobody has told, on the day their user
upgrades the engine. A library built correctly to the rules of its day must not become unusable
because the engine moved on.

## Considered options

How does a stricter rule reach a library the engine's maintainer does not know?

- **A. The library's declared contract version decides which rules apply to it** (chosen). A new
  rejection applies to libraries that declare the contract version that introduced it, and only warns
  for the rest. A library adopts it when its owner raises the declared version.
- **B. New rejections wait for a major contract version.** A minor adds only optional fields and
  warnings. Simpler to implement, but rules change in rare, large steps, each a migration for every
  library at once.
- **C. Keep ADR-0015.** The engine releases and libraries pin. Does not scale past the libraries one
  person can move, and says nothing a stranger can build to.

## Decision outcome

### The contract has its own version

- The library contract (today `CONVENTIONS.md`) carries a version `MAJOR.MINOR`, independent of the
  engine's version. It changes only when what a library must or may hold changes; an engine fix that
  changes no rule (#74) leaves it alone. Editorial changes to the text do not change it.
- The current contract is **2.0**, the rules a library met under engine v0.2.0 (`CONVENTIONS.md` has
  called itself "Version 2" since 2026-09-19). #71's rejection is the first rule of **2.1**.
- **Minor:** adds a field, a warning, or a rejection that applies only to libraries declaring the new
  version. A library valid under 2.0 is still valid, and still served, by an engine that knows 2.1.
- **Major:** changes what something a library already holds *means* (a marker, a field, a layout), so
  an engine that does not know the major could misread the library. Majors are rare by design.
- The contract keeps its own changelog: each version, what it adds, and what a library gains by
  declaring it. That text is what a library's owner is shown when the library is behind.

### A library declares the version it was built to

- The root `INDEX.md` of a library declares `kb_contract: <MAJOR.MINOR>`.
- A library that declares nothing is read as **2.0**: every library that exists today was built to
  engine v0.2.0's rules, and none of them has to change for this ADR.
- A library's own release notes, if it has releases, name the contract version it conforms to, not an
  engine version.

### An engine never makes an older library unusable

- An engine supports every contract version it has ever published. It keeps the reader for each one
  rather than dropping old versions after a window, so upgrading the engine never stops it checking or
  serving a library that was valid when it was built.
- Rules apply by the library's declared version. A rejection introduced in 2.1 fails a library that
  declares 2.1 or later; a library declaring 2.0 gets a warning naming the rule and the version that
  brings it in, and its check still passes.
- A library that is **behind** (declares an older version than the engine knows) is told so. The
  session-start nudge and `check-kb` say which library, the version it declares, the version the engine
  knows, and what the newer versions add, from the contract's changelog. It is information, not a
  failure: nothing is blocked.
- A library that is **ahead** (declares a version the engine does not know):
  - a newer minor: the engine checks and serves it by the newest rules it knows, and says the engine
    should be upgraded to check the rest;
  - a newer major: the engine does not serve it, and says why and what to upgrade. Serving a library
    whose markers may mean something this engine does not know could serve a disputed fact as settled,
    which the retrieval contract exists to prevent.

### The contract is a spec a stranger can build to

- The contract must be complete without the engine's code: a person who has read only it can build a
  library the engine accepts. Parts of `CONVENTIONS.md` today are about the engine itself (how skills
  conform, the session-start hook, precedence over the design plan); those move to engine documents,
  and what remains is the library-facing spec.
- Each contract version ships with a **conformance suite**: fixture libraries, valid and invalid,
  that an engine release must classify correctly for every version it supports. Much of this exists in
  `tests/run-checks`; it becomes a named, published part of the contract.
- An engine release's notes state the contract versions it supports ("contract 2.0–2.1").

### Pinning is out of scope

- Whether a library's CI pins an engine, to what, and when it moves, is its owner's decision. The
  engine neither requires nor tracks it, and an engine release no longer moves any library's pin.
- The CI template (`documents/library-guardrails.yml`) stays as an example. Pinning a release tag is
  still a sensible default for unattended use (ADR-0003), and the example says the choice is the
  owner's.
- The engine's own releases keep ADR-0015's semantic versioning. Publishing a new contract minor is an
  engine minor; a new contract major is an engine major once the engine is past 0.x.

## Consequences

**Good.**

- Upgrading the engine never breaks a library. A stricter rule reaches a library when its owner opts in.
- A library's owner is told what a newer contract would give them, so staying behind is a choice, not
  ignorance.
- An engine release costs no pull requests in any library.
- A library author has a versioned spec and a conformance suite to build against, without reading the
  engine.

**Bad.**

- Every new rejection carries a version check, and the engine keeps every contract version's rules for
  good. That complexity only grows; keeping majors rare is what bounds it.
- `check-kb` and its siblings can no longer simply apply "the rules": each rule needs the version that
  introduced it, and the tests must cover each rule both below and at its version.
- A library behind the contract is reminded at every session start until it moves. That is deliberate
  (ADR-0013: surfaced, not scheduled), and it may be noisy for an owner who has decided to stay.
- Splitting `CONVENTIONS.md` touches every document and skill that cites it by section.

## Delivery

In order, each its own pull request:

1. Contract versioning: the version line and the contract changelog in `CONVENTIONS.md`;
   `kb_contract` in the root `INDEX.md` schema, read as 2.0 when absent; `check-kb` rejects a
   malformed value.
2. Version-gated rules: #71's rejection becomes contract 2.1 (a warning for 2.0), with tests both
   sides of the line; the behind/ahead reporting in `check-kb` and the session-start nudge; the
   newer-major refusal in retrieval.
3. The CI template becomes an example and its comments say so; ADR-0015's pinning sections are marked
   superseded; README and CONTRIBUTING updated.
4. The split: `CONVENTIONS.md` keeps the library-facing spec; engine-internal sections move to engine
   documents.
5. The conformance suite: fixtures per contract version, published with the contract.

The next engine release waits for steps 1 and 2, so that #71 ships gated rather than as an unannounced
rejection.

## Review trigger

Revisit when keeping every contract version's rules makes a change hard to write or test, or when a
contract major is proposed.
