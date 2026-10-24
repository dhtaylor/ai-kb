# ADR-0015: What a release is, and how libraries pin the engine

- **Status:** Accepted
- **Date:** 2026-10-16
- **Deciders:** Dandy Taylor
- **Applies:** [0003](0003-scoping-topology.md) ("Latest-wins for humans; pin for automation")

> **Amended 2026-10-21 by [ADR-0016](0016-versioned-library-contract.md).** Libraries are expected to be
> owned by people the engine's maintainer does not know, so the engine publishes a versioned library
> contract instead of coordinating pins. "Library CI pins the engine to a release tag" is superseded:
> pinning is the library owner's choice. A library release names the contract version it conforms to,
> not an engine version. The engine's semantic versioning below stands.
>
> **Amended 2026-10-23 by the owner:** a release has a code freeze two days before it. See *A release
> is preceded by a two-day freeze* below.

## Context and problem statement

Nothing had been released. The engine had no tags, no changelog and no stated meaning for a version
number; both plugins had declared `0.1.0` since the first commit, 174 commits earlier. Libraries had
no way to say which engine they were checked against.

Every library's CI clones the engine with `git clone --depth 1` and no ref, so it checks the library
against whatever `main` holds that day. An engine change can therefore fail a library's CI with no
change to the library: the stricter unstamped reader of #64 could have done so, had any library held a
second source under one stamp. ADR-0003 settled the principle ("Where the general tier feeds something
*unattended* (a CI eval, a scheduled agent), non-determinism bites, so those pin to a tagged ref") and
called it moot while there was no second consumer. A public release creates one.

## Decision

### The engine uses semantic versioning

- A release is a git tag `vMAJOR.MINOR.PATCH` on `main`, with a GitHub release whose notes come from
  `CHANGELOG.md`.
- **While the major version is 0**, any change to the contract (`CONVENTIONS.md`), to what a check
  accepts or rejects, or to a decision record is a **minor** bump. A fix that changes no rule a library
  must meet is a **patch**.
- Both plugins' `plugin.json` versions equal the engine's release version, so a plugin says which
  release it came from.
- The first release is **v0.2.0**, not v0.1.0: `0.1.0` has been in the manifests and the README all
  along, naming every unreleased state of the engine since the first commit. Tagging a release with the
  same number would give two different things one name.

### A release is preceded by a two-day freeze

- From two days before a release date, `main` takes release work only: the CHANGELOG's release
  section, version numbers, the fresh-clone check and the tag. No code, check or contract change
  merges in that window. For a release on the 31st, the freeze begins on the 29th.
- A defect the release work finds in that window is the owner's call: fix it and move the release
  date, or release without the fix and fix it in the next release.
- The freeze exists so that what is tagged is what was checked: the fresh-clone check and the notes
  describe a `main` that no longer moves under them.

### A library release records the engine it was verified against

- A library is content, and ADR-0003's rule for humans stands: a correction propagates when it lands,
  not at the next release. A library tag marks a known-good point, nothing more.
- A library tag is `vMAJOR.MINOR.PATCH` too, and its release notes name the engine release it was last
  verified against ("verified against ai-kb v0.2.0"): its checks clean and its `Recheck:` assertions
  passing under that engine.

### Library CI pins the engine to a release tag

- The library CI template (`documents/library-guardrails.yml`), and each library's copy of it, clones
  the engine at a release tag (`git clone --depth 1 --branch vX.Y.Z`), not `main`.
- Moving a library to a new engine release is a one-line pull request in that library, which its own
  CI then checks against the new engine. A rule change reaches a library when its owner moves the pin,
  not on the day the engine changes.
- The engine's own CI, the commit hooks and the session-start hook are unaffected: they run the
  engine on the machine, whatever version is installed there.

## Consequences

**Good.**

- A library's CI result depends on the library and a named engine, not on the engine's `main` that day.
- A release says what changed (`CHANGELOG.md`) and a library says what it was checked against.

**Bad.**

- Each engine release costs a pull request per library to move the pin. With six libraries and one
  maintainer, that is six one-line changes per release.
- A pinned library CI does not notice that the next engine would reject it until the pin moves. The
  engine's own suite runs every check over every installed library before a release, which catches
  that on the maintainer's machine; it does not catch it for a library the maintainer does not have.
- The commit hook uses the installed engine, so on a machine with a newer engine a commit can be held
  to rules its library's CI has not adopted yet. That is the stricter of the two, and the direction is
  deliberate.

## Review trigger

Revisit when a library is maintained by someone who is not the engine's maintainer, or when moving pins
across all libraries becomes the bottleneck of a release.
