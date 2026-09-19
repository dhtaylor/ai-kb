# ADR-0002: Governance structure without enforcement

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Phase:** 0 (guardrails)

## Context and problem statement

The architecture specifies a governance model built for a team: CODEOWNERS review as a
required status check, two approvals and blocked self-merge on `main`, at least two named
owners per domain, signed commits, and CI running the link, scope and retrieval checks
before merge. High-blast-radius knowledge changes additionally require two reviewers and a
24-hour window.

This is currently a single-contributor repository. None of those controls can be satisfied
by one person: a lone owner cannot constitute two approvals, cannot avoid self-merge, and
cannot be a second named owner. The work is nonetheless headed for a team.

## Decision drivers

- A control that is declared but not enforced is worse than an absent one, because it reads
  as protection in an audit and provides none.
- Rebuilding governance later, after conventions have set, is more expensive than writing
  the structure now.
- Phase 0's exit criterion is that no secret can be committed **or pushed** — two distinct
  boundaries, only one of which is client-side.

## Decision outcome

**Write the full governance structure now; enforce what is enforceable; record the gap
explicitly rather than let the structure imply protection it does not provide.**

### Enforced today

| Control | Mechanism | Boundary |
|---|---|---|
| Secret scan | `knowledge/scripts/check-secrets` via `.githooks/pre-commit` | Committer-side, **bypassable** |
| KB integrity | `knowledge/scripts/check-kb` via the same hook | Committer-side, bypassable |
| Embedded-fact lint | `knowledge/scripts/check-embedded-facts` via the same hook | Committer-side, bypassable |
| Full-history scan | `check-secrets --all`, run on demand | Audit |
| All three checks in CI | `.github/workflows/guardrails.yml` on every push and PR | **Server-side, not bypassable** — but detection, not prevention |

**Verified 2026-09-19:** the CI workflow ran green on commit `ccedeb5` in 6s, executing all three checks
against full history. The committer-side hook was separately verified to refuse a commit carrying a test
credential, in a fresh clone, after the activation step. Both halves are observed working, not assumed.

### Written but dormant

`.github/CODEOWNERS` exists and names an owner per area. It is **advisory text** until branch
protection makes owner review a required status check.

### Not yet in place

- **True push rejection.** GitHub secret-scanning push protection *rejects* a push carrying a
  credential before it lands. It is **not available for this private repository on the current
  plan** — checked 2026-09-19, the option is absent from the repository's code-security
  settings. The CI workflow above is the compensating control, and the difference is material:
  CI lets the push land and then fails the run, so a real leak still requires rotation **and**
  a history rewrite. Revisit if the repository becomes public or the plan changes.
- **Branch protection on `main`:** require pull requests, require CODEOWNERS review, require
  status checks to pass, block force-push, block self-merge. Deliberately deferred — on a
  single-contributor repository these obstruct the only committer without supplying the second
  reviewer that justifies them.
- **Signed commits** for merges.
- **A second owner per domain.** Not satisfiable with one contributor.

## Consequences

**Good.** Every control is either working or explicitly listed as absent. The structure
activates rather than needing invention the day a second contributor arrives.

**Bad — the honest part.** Today's guardrails are **advisory**. A committer who runs
`--no-verify`, or a clone that never ran the activation step, is unguarded. Until push
protection and branch protection are enabled, nothing prevents a bad commit reaching the
remote. This is the accepted risk of the current single-contributor phase; it is not
mitigated, it is merely bounded by there being one contributor who knows it.

**Activation is manual.** `core.hooksPath` is local git config and is not cloned. Every
clone must run once:

```
git config core.hooksPath .githooks
```

A clone that skips it has no guardrails at all, silently. Until a bootstrap command exists,
this is a documented manual step and a real failure mode.

## Review trigger

Revisit this ADR when any of these becomes true: a second contributor joins; the shared tier
gains a consuming project; or any agent gains the ability to mutate a production system.
