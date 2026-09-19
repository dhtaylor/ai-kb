# ADR-0003: Scoping topology — the three homes

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Phase:** 1 (inventory, map & decide)

> **Amended 2026-09-19 by [ADR-0006](0006-behaviour-distribution.md).** This ADR placed the general
> tier at `ws_v1/knowledge/` as a directory inside the workspace repository. It is now its own git
> repository at that path, carrying the decision records, guardrails and behaviour with it. The
> locations below are unchanged — `$KB_GENERAL_ROOT/knowledge/` still resolves identically — but the
> repository boundary has moved, and the reasoning about what a project can reach is extended there.

## Context and problem statement

Knowledge falls into tiers with different owners and different rates of change, and getting
the middle tier wrong is how a shared knowledge base fails. Over-share, and every repository
couples to a churning blob. Under-share, and the same fact is copied into N repositories and
drifts — the exact failure the governed KB exists to prevent, merely relocated from files to
repositories.

This must be settled before the pilot, because every retrieval path the pilot writes is
hardcoded against it.

## Decision drivers

- **One canonical home per fact.** A fact stated twice will eventually disagree with itself.
- **A project must stay usable standalone.** A developer without the general tier gets a
  degraded answer, never a crash.
- **No literal paths.** Settled in [ADR-0001](0001-kb-root-resolution.md).
- **The topology must be testable**, not merely asserted, before it is built on.

## Considered options

1. **Single repository, `scope:` field only.** Defers the second root; no cross-root resolver
   needed. But the general tier never actually separates, and extracting it later means
   re-reading everything.
2. **Two roots** — general plus repo.
3. **Three homes** — general, repo, and personal.

## Decision outcome

**Chosen: option 3, three homes.**

| Tier | Home | Version control |
|---|---|---|
| General (`general`, `product:*`, `org:*`) | `$KB_GENERAL_ROOT/knowledge/` | the `ws_v1` repository |
| Repo (`repo:<project>`) | `<project>/knowledge/` | the project's own repository |
| Personal | `~/.claude/` | none — deliberately not team-shared |

Concretely: the general tier is `/mnt/c/workspaces/ws_v1/knowledge/`, and the first project is
`/mnt/c/workspaces/ws_v1/code/test_project/`.

### A deviation worth naming

The architecture says the general repository is cloned to a location *outside* any single
project. Here the project sits **inside** the general repository's directory tree, at
`code/test_project/`.

This is safe only because of a specific property, and it would be unsafe without it:
`test_project` is **its own git repository**, and the parent `.gitignore` excludes `code/`.
The two tiers are therefore genuinely separate *version-control* roots even though they are
nested on disk. Neither can commit the other's files; neither appears in the other's history.

The reason to accept the nesting rather than "fix" it: it makes the cross-root machinery
**testable on one machine**. A project that must resolve `[[general:slug]]` through a
configured root — rather than through a convenient relative path — exercises the resolver, the
slug manifest and graceful absence for real. Had the two tiers shared one repository, relative
paths would quietly work and the resolver would never be exercised until it failed on someone
else's machine.

The risk this accepts: nesting invites someone to reach across with a relative path, since the
files are right there. `check-embedded-facts` flags absolute paths; a relative traversal like
`../../knowledge/` is not currently caught. **Added to the check-scope backlog** ([ADR-0004](0004-scope-attribute.md)).

### Versioning stance

**Latest-wins for humans; pin for automation.** Code dependencies are pinned for reproducible
behavior; facts are the opposite — a correction should propagate immediately, not wait behind
a version bump in ten repositories. Where the general tier feeds something *unattended* (a CI
eval, a scheduled agent), non-determinism bites, so those pin to a tagged ref.

With one contributor and one machine this is currently moot: there is nothing to pull from and
no second consumer to surprise. It is recorded now because the moment a second machine exists,
the default is already decided.

## Consequences

**Good.** Each fact has exactly one home. The general tier is owned by no single project. A
project KB travels with its clone and is reviewed alongside the code it describes.

**Bad.** A cross-root `[[general:slug]]` resolver **does not exist**, and until it does every
cross-repo link is unvalidated — dead links would accrue silently. This blocks Phase 3, per the
plan. `check-kb` today resolves links within a single root only and says so.

**Neutral.** Personal knowledge is excluded from both repositories by construction rather than
by convention, which means there is no mechanism to accidentally share it and no mechanism to
back it up either.

## Open items

- The cross-root resolver and the slug→path manifest (Phase 3 blocker).
- A relative-traversal check, so nesting cannot be abused (see above).
- The bootstrap command that provisions a new machine ([ADR-0001](0001-kb-root-resolution.md)).
- Latest-wins is untested: there is no second consumer yet to propagate a correction to.
