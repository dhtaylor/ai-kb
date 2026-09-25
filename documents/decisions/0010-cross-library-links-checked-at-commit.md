# ADR-0010: Cross-library links are resolved at every commit that can break one, not in CI

- **Status:** Accepted
- **Date:** 2026-09-24
- **Deciders:** Dandy Taylor

## Context and problem statement

`check-xlinks` exists and is regression-tested in `tests/run-checks`, but nothing ran it against
real content at the point a `[[library:slug]]` link can actually break:

- A library's own CI (`kb/*/.github/workflows/guardrails.yml`) deliberately skips it — a lone
  library cannot see its siblings, so the job says so and moves on.
- The engine's pre-commit hook (`.githooks/pre-commit`) runs `check-xlinks kb`, but only fires on a
  commit made *in the engine*. A slug rename or removal happens in a library's own repository.
- Neither library's pre-commit hook called `check-xlinks` at all.

So a slug renamed or removed in library A, cited by library B via `[[A:slug]]`, committed cleanly in
A. The dead link would sit unnoticed until someone next committed to the engine and happened to run
its hook, or ran `kb-audit` by hand. Phase 3 of the combination plan names this exact gap as its
blocker: "the cross-root `check-links` resolver existing and running in CI."

## Considered options

1. **A credentialed integration CI job.** A workflow with access to both private library repos,
   triggered on push to either, running `check-xlinks` over both checkouts. This is the design the
   plan's Phase 3 sentence assumed. Rejected: the libraries are private, so the job needs a read
   token for at least one of them — some credential, stored somewhere, rotated by someone. That
   directly contradicts the reason `guardrails.yml`'s own header comment gives for fetching the
   engine anonymously: "this needs NO credential: no secret to add, none to rotate, and nothing to
   leak." A job that resolves cross-library links needs exactly the credential that design exists to
   avoid. It also cannot live in the public engine repository — a run there would log which slugs and
   paths exist in a private library, which is the leak the whole split (public behavior, private
   knowledge) is built to prevent.
2. **Leave it to `kb-audit` alone.** `kb-audit` already sweeps for dead links as part of its decay
   detection. Rejected as the *only* gate: it is a sweep run on a cadence or by hand, not a commit
   gate, so a broken citation can sit for a full sweep interval looking clean.
3. **Run `check-xlinks` at every commit that can break a link, engine and library alike, and keep
   `kb-audit` as the periodic backstop.** Chosen.

## Decision outcome

**Chosen: option 3.** The Phase 3 gate is now: cross-library links are resolved at every commit that
can break one — the engine's existing hook, plus each library's own pre-commit hook, when that
library's siblings are visible to it — with `kb-audit` catching anything that slips past both.

The library hook can only resolve truthfully when it can see the other libraries, which means it
lives at `<engine>/kb/<itself>` — the designed layout, or a clone that ran `kb-bootstrap` and points
`kb.engineRoot` at a real `kb/` directory holding siblings. The hook checks this with a realpath
comparison (`pwd -P` against `<engine>/kb/<this library's directory name>`) rather than assuming: a
library found via `kb.engineRoot` set by hand could be cloned anywhere, engine included, with no
sibling underneath it at all. When the comparison fails, the hook prints one line saying
cross-library links were not checked and exits clean — absence warns, it never fails, the same rule
`check-xlinks` itself applies to a library that is not installed. This is not a fallback bolted onto
CI; portability is why the split (§5 of the contract: a library "cannot see its siblings") exists in
the first place, and the hook's silence-vs-skip behavior is a direct expression of it.

**This is accepted as incomplete, on the record:**

- **Hooks are bypassable.** `--no-verify` skips them outright, and a clone that never ran
  `kb-bootstrap` has no hook installed at all (`core.hooksPath` is never set). Both were already true
  of every other pre-commit check in this system; this decision does not change that boundary, it
  extends the same boundary to cross-library links.
- **A library cloned outside an engine's `kb/`** — siblings not installed alongside it — gets no
  cross-link check from its own hook, by design (see above). Its citations are only checked when
  someone later commits from inside an engine that has it installed, or when `kb-audit` runs.

Both residuals are accepted, not overlooked. The mitigation is `kb-audit`, which sees the whole `kb/`
tree regardless of which repository's commit triggered it. There is no server-side backstop for
cross-library links: the server-side gates run per repository and cannot see siblings, which is the
gap option 1 would have closed.

**Trigger to revisit:** a third library (three-way link resolution starts to matter more, and the
`ENGINE/kb` realpath check gets exercised against more topologies), or a second contributor
committing to these libraries (bypass and never-bootstrapped clones stop being a single person's own
risk to accept).

## Consequences

- The plan's Phase 3 "Blocked on" sentence is resolved: the blocker was CI-shaped, the fix is
  commit-shaped, and Phase 3 can proceed.
- `tests/run-checks` gained cases that exercise the *template* hook in
  `kb-create-domain/SKILL.md` directly, not a copy of it, so a future edit to the template that
  silently drops or breaks this block is caught the same way every other guardrail regression is.
- No new credential exists anywhere in this system. That was the constraint that ruled out option 1,
  and it still holds.
