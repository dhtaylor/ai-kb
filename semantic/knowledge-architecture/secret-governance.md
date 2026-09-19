---
name: secret-governance
description: Why a leaked secret is not remediated by rotation alone, and why a committer-side secret scan is not the enforcement boundary.
memory_type: semantic
domain: knowledge-architecture
scope: general
verified: 2026-09-19
metadata:
  type: fact
  node_type: memory
  created: 2026-09-19
tags: [knowledge-architecture, secrets, governance]
keywords: [secret scan, pre-commit, rotation, history rewrite, git filter-repo, push protection, server-side gate]
---
# Secret governance

The architecture keeps secrets out of both KB trees by reference (vault or env, never inlined),
guarded by a secret-scanner pre-commit hook over both trees. Two properties of that guard are
easy to get wrong:

## Rotation is not removal

Rotating a leaked secret does not erase it from git *history* — every clone still holds it. Any
existing leak requires **history rewrite** (e.g. `git filter-repo --invert-paths`), force-push,
clone invalidation, and a clean full-log scan.

Source: [[knowledge-agent-architecture-combination-plan]] (§5.4)
Verified: 2026-09-19 · by: agent · method: doc-review

## A pre-commit hook is not the enforcement boundary

A pre-commit hook is bypassable (`--no-verify`). The enforcement boundary is a **server-side/CI
gate** (push protection, or a CI job failing the build on any detected secret).

Source: [[knowledge-agent-architecture-combination-plan]] (§5.4)
Verified: 2026-09-19 · by: agent · method: doc-review

This workspace's current, concrete standing on both points — what is enforced, dormant, or
absent here specifically — is recorded in [[adr-0002-governance-without-enforcement]], not
restated here.
