# ADR-0002: Governance structure without enforcement

- **Status:** Accepted, amended 2026-09-22 (see *What changed on 2026-09-22*)
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

**Amended 2026-09-19 — the table above predates the engine/library split and is superseded.**
Paths moved (`scripts/` is no longer under `knowledge/`), and enforcement is now per repository:

| Repository | Committer-side | Server-side |
|---|---|---|
| **engine** (ai-kb) | exec bits, secret scan, embedded-fact lint. **Not** `check-kb` — the engine holds no knowledge, and running it here would check zero files and report success | CI: the same three |
| **domain library** | exec bits, secret scan, `check-kb` against itself — borrowed from the engine, skipped with a clear message when no engine is reachable | none — libraries have no CI of their own |
| **workspace** (ws_v1) | secret scan only, skipped when the knowledge repo is absent | none |

A library cloned alone is unguarded until an engine is in reach. That is the price of not making a
portable library depend on an engine it is designed to outlive, and it is a deliberate trade rather
than an oversight.

### Written but dormant

`.github/CODEOWNERS` exists and names an owner per area — in the engine and, since 2026-09-22, in
each library. It remains **advisory text**: owner review becomes a requirement only when branch
protection requires pull requests and CODEOWNERS approval, which is deferred while one person
cannot approve their own pull request. What it does do today is answer who a sweep's finding belongs
to, resolved by `kb-owner` rather than by eye (`ai-kb:scripts/kb-owner`).

### Not yet in place

- **True push rejection.** GitHub secret-scanning push protection *rejects* a push carrying a
  credential before it lands. It is **not available for this private repository on the current
  plan** — checked 2026-09-19, the option is absent from the repository's code-security
  settings. The CI workflow above is the compensating control, and the difference is material:
  CI lets the push land and then fails the run, so a real leak still requires rotation **and**
  a history rewrite. Revisit if the repository becomes public or the plan changes.
- **Pull requests, CODEOWNERS review and self-merge blocking on `main`.** Still deferred, and now
  for a sharper reason than before: GitHub does not let an author approve their own pull request, so
  requiring approval with one contributor does not raise the bar — it stops all work. Enable with
  the second contributor, not before.
  (Requiring the status check itself, and blocking force-push, *were* enabled — see below.)
- **Signed commits** for merges.
- **A second owner per domain.** Not satisfiable with one contributor.

## Consequences

**Good.** Every control is either working or explicitly listed as absent. The structure
activates rather than needing invention the day a second contributor arrives.

**Bad — the honest part.** Guardrails were **advisory** in every repository until 2026-09-22, and
remain so in the libraries. A committer who runs `--no-verify`, or a clone that never ran the
activation step, is unguarded. This is the accepted risk of the single-contributor phase; it is not
mitigated, it is bounded by there being one contributor who knows it.

**Activation is manual.** `core.hooksPath` is local git config and is not cloned. Every
clone must run once:

```
git config core.hooksPath .githooks
```

A clone that skips it has no guardrails at all, silently. Until a bootstrap command exists,
this is a documented manual step and a real failure mode.

## What changed on 2026-09-22

The engine repository was made **public**, which moved it into a different enforcement tier and
produced an asymmetry worth stating plainly.

**Enabled on `ai-kb` (public):** `main` is protected, the `guardrails` workflow is a **required
status check**, and force-pushes and deletions are blocked. Verified from the public API:
`"protected": true`, contexts `["guardrails"]`.

**Not enabled, deliberately:** `"enforcement_level": "non_admins"` — the gate exempts repository
admins, which today means it exempts the only person using it. **Observed on the very next push**,
which was a direct push of this amendment:

    remote: Bypassed rule violations for refs/heads/main:
    remote: - Required status check "guardrails" is expected.

So a direct push does violate the rule and is admitted only by the exemption: binding the admin
would not merely be stricter, it would reject direct pushes and force a pull request per change,
because a commit has passed no check at the instant it is pushed. That is the right trade the day
someone else has push access, so that the exemption describes an escape hatch rather than the whole
population. Until then every push to this repository is a rule violation that GitHub allows and
announces — which is a more honest description of the control than "enabled".

**Not available on the libraries (private):** branch protection and rulesets need a paid plan for
private repositories, the same limitation that put push protection out of reach in 2026-09-19. Their
CI runs the same checks and reports, and nothing forces anyone to heed it.

**So the asymmetry is:** the repository holding *behaviour* is gated on the server; the repositories
holding *knowledge* are not. That is backwards from where the risk sits — a wrong fact is served to
an agent, while a wrong script fails loudly — and it is a property of the billing plan rather than
of any decision made here. It is the strongest argument for either paying for the private repos or
accepting that the libraries' real guardrail is the commit hook plus a human reading a red run.

## Review trigger

Revisit this ADR when any of these becomes true: a second contributor joins (enable pull requests,
CODEOWNERS review, and admin enforcement); the shared tier gains a consuming project; any agent
gains the ability to mutate a production system; or the account's plan changes, which would let the
private libraries carry the protection the public engine now has.
