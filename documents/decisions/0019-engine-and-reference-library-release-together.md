# ADR-0019: The engine and its reference library release together, under one tag

- **Status:** Accepted
- **Date:** 2026-11-06
- **Deciders:** Dandy Taylor
- **Amends:** [0015](0015-releases-and-pinning.md), "A library release records the engine it was
  verified against", for ai-kb-architecture only. Every other library keeps its own version.

## Context and problem statement

Two repositories are released: the engine (`ai-kb`) and the knowledge-architecture library
(`ai-kb-architecture`). The library is, in essence, the engine's detailed documentation: how the
engine works and why. It is folded from the engine before each release, so it describes one engine
version. It is tied to the engine in a way no other library is.

ADR-0015 gave each library its own version number, and ADR-0016 kept that rule for every library,
because most libraries will belong to people the engine's maintainer never hears from. Following
those rules, the two releases have never shared a number:

| Date | Engine | ai-kb-architecture |
|---|---|---|
| 2026-10-16 | v0.2.0 | v0.1.0 |
| 2026-10-31 | v0.3.0 | v0.2.0 |
| 2026-11-11 | v0.4.0 | v0.4.0 |

The owner treats the two as one release package. Two version numbers for one package make a reader
ask which library goes with which engine, and the only answer is a line in the release notes.

## Decision

**ai-kb-architecture takes the engine's release tag.** Each engine release `vX.Y.Z` tags the library
`vX.Y.Z` on the same day, at the library commit verified against that engine. The next release is
v0.4.0 for both, so the library goes from v0.2.0 to v0.4.0, and no library v0.3.0 exists.

- **Published tags stay as they are.** Library v0.1.0 and v0.2.0 are not moved or renamed. Someone
  may have pinned them.
- **Release notes still name the engine.** The library's notes say "verified against ai-kb vX.Y.Z"
  and the library contract it declares. ADR-0016 requires a library's notes to name only the
  contract. Naming the engine too is this library's rule. A matching number does not replace that
  proof.
- **A fix to the library alone, between releases, waits for the next release.** It lands on `main`
  as usual (corrections propagate when they land, ADR-0003), but it gets no tag of its own. An
  engine patch release `vX.Y.Z+1` tags the library too, even if the library has not changed.
- **This is the only exception.** Every other library is released separately and versions itself,
  under ADR-0015 and ADR-0016. The five personal libraries have no release cycle.

### Release day

The two-day freeze (ADR-0015) covers both repositories. The release script stops at the first step
that fails, and checks that nothing moved since the fresh-clone check:

1. **Preflight.** Both `main` branches are still the commits the fresh-clone check passed. Neither
   repository has tag `vX.Y.Z` yet. Both working trees are clean. The release pull request is green
   and its head is the checked commit.
2. **Merge the engine's release pull request** and confirm the merged tree matches the checked head.
3. **Tag the engine `vX.Y.Z`** and publish its GitHub release from the CHANGELOG's `vX.Y.Z` section.
4. **Tag ai-kb-architecture `vX.Y.Z`** at its verified commit, with the message "verified against
   ai-kb vX.Y.Z". Publish its GitHub release from its library notes.
5. **Cross-link the two releases.** The engine's notes name the library release, and the library's
   notes name the engine release.

## Consequences

**Good.**

- A reader sees one package: ai-kb vX.Y.Z and ai-kb-architecture vX.Y.Z.
- One version number for both repositories, so the release script has no second version to set.

**Bad.**

- The library's number skips v0.3.0, which looks like a missing release to someone reading its tag
  list. Its v0.4.0 notes say why.
- A library-only fix has no release of its own. It waits until the engine's next release.
- The library's version number no longer says how much the library changed. Its CHANGELOG or release
  notes have to.

## Review trigger

Revisit if ai-kb-architecture ever needs a release the engine does not, or if a second library joins
the release package.
