# ADR-0012: Phase 4 safety hardening, scoped to what one maintainer on one machine can enforce

- **Status:** Accepted
- **Date:** 2026-09-29
- **Deciders:** Dandy Taylor

## Context and problem statement

Phase 4 of the combination plan asks for a least-privilege tool audit, confirmation gates on
state-changing commands, a Verifier fixture test, a Watcher replay test, and an enforced
high-blast-radius PR policy. The plan wrote these for a team. It assumed **service accounts per
agent tier** as the primary control ("`permissions.deny`-style config is client-side; the primary
control is the service account each agent authenticates as"), and it assumed **two reviewers and a
24-hour window** for high-blast changes.

This environment has neither. There is one maintainer, one machine, agents that run as that person,
and no second owner. Building Phase 4 as written would mean either claiming controls that do not
exist or blocking on conditions that cannot be met. This ADR records what was built, what each
control does and does not enforce, and what stays dormant.

## Decision outcome

### Least-privilege: declared everywhere, enforced only where the runtime allows

Every agent, command and skill declares a `tier:` (retrieval, curation, analysis, verification) and
a tool scope. `check-tool-scope` fails any file with no tier, no scope, an unknown tier, or a tool
outside its tier, in pre-commit and in CI.

The audit found that only a **subagent's** `tools:` field restricts anything. It is an allowlist,
so `kb-retrieve` really is read-only. A **skill's or command's** `allowed-tools:` only pre-approves
the named tools for one turn, and every other tool stays callable (`documents/tool-scope-matrix.md`,
citing the Claude Code docs). So for the six skills, the declared scope is intent the runtime does
not enforce.

**Accepted, by the owner's choice (path 1):** skills run in the owner's own session, so the
session's permission mode is the gate. In default mode every write is approved by hand. Moving
skill work into restricted subagents was considered and declined. It would restructure skills that
had just been validated, and the gain is bounded by the next limitation anyway.

**No service accounts.** Every tool runs as the one local user, so client-side scopes are the only
control, and a determined bypass beats them. This is an accepted limitation, not a gap left unseen.
It must be revisited before any agent touches a shared or production system.

### Mutation is gated; detection runs unattended

`documents/state-change-gates.md` bands every entry point by the plan's rule: detection may run
unattended, and mutation needs an explicit gate.

- `kb-bootstrap`, the one script that writes machine-level configuration, now reports by default
  and applies only with `--apply`, as `kb-verify` already did.
- The curation skills stop for approval **before committing**, not before their first edit. A
  working-tree edit is a draft that `git checkout` reverts, and the commit is the change that lasts.
  This matches `kb-update-domain`'s existing design.
- Additive or bookkeeping writes (`kb-capture`, `kb-init`, `kb-audit`'s queue, the Watcher's queue,
  the personal coaching log) stay ungated, each with a stated reason. Nothing run from a hook or CI
  can prompt.

### The Verifier is tested as built, not as first worded

The plan says a failed check becomes a `contradictions.md` flag. The Verifier as built (§9.13)
reports the failure and leaves the fact untouched. A failure can mean a stale fact, a wrong
assertion or a real contradiction, and choosing among them is a human decision. The fixture test
asserts the built behaviour: a stale, wrong fact is reported and its file stays byte-for-byte
unchanged, with no false-fresh stamp.

### The Watcher is offline and model-free

`kb-watch` compares saved snapshots and never fetches. It imports no network module, and a
regression case enforces that. It is a script, not an agent, so page content never reaches a model,
which is the plan's strongest defence against a spoofed page steering a knowledge change. Live
fetching remains the later, isolated step §5A describes. The monitored-source allowlist ships empty.

### The high-blast gate is enforced for pull requests; direct push is a visible bypass

`check-blast` runs inside the required `guardrails` check, in the engine and in all six libraries,
where it was confirmed running in GitHub Actions on 2026-09-29. A pull request that deletes a fact,
removes a CONFLICTED marker, promotes a scope, or touches CONVENTIONS or the ADRs fails without the
`owner-approved` label.

- **The admin bypass is kept.** Branch protection does not enforce the rule on admins, so the
  owner's direct pushes land. On a push, the step only warns, so the bypass shows in the log.
- **"Owner-only" is conditional.** Anyone with triage access can set a label. The property holds
  only while the owner is the sole collaborator.
- **The 2-reviewer + 24-hour rule is dormant** until a second owner exists (ADR-0002).

### No orchestrator

ADR-0011 records this. A routing sample showed `kb-retrieve` already routes, passes through, and
stays within two libraries.

## Consequences

- **Good:** each control's real strength is written beside it. The two checks the plan most
  worried about, the Verifier and the Watcher, have regression tests with proven traps. The
  one script that could silently reconfigure a machine no longer does so by default.
- **Bad:** least-privilege for skills, owner-only labels, and two-person review all depend on this
  being a one-person system. **Adding a collaborator reopens this ADR:** a second owner, the
  2-reviewer rule, whether admins bypass, and whether triage access can set `owner-approved`.
- **Bad:** the pull-request path of `check-blast` has not yet run in GitHub Actions. Only the push
  path has. It is exercised by local tests until a real PR opens.
