---
name: adr-0002-governance-without-enforcement
description: Source stub — ADR-0002, which controls are enforced today, which are dormant, and which are absent.
memory_type: reference
domain: meta
scope: general
metadata:
  type: source
  node_type: citation
  created: 2026-09-19
tags: [meta, adr, governance, source]
keywords: [ADR, governance, CODEOWNERS, branch protection, push protection, accepted risk, pre-commit]
---
# Source: ADR-0002 — Governance structure without enforcement

- **Title:** ADR-0002: Governance structure without enforcement
- **Origin:** Phase 0 close-out decision, 2026-09-19
- **Date ingested:** 2026-09-19
- **Artifact location:** `documents/decisions/0002-governance-without-enforcement.md`

Records that the full team governance structure is written now but only partly enforceable by
one contributor. Carries the table of what is enforced, what is dormant, and what is absent —
including that the pre-commit hook is bypassable and that `core.hooksPath` is local config a
fresh clone must set by hand or have no guardrails at all.
