---
name: sources-index
description: Citation registry — stubs for external artifacts so their [[slug]] backlinks resolve.
memory_type: reference
domain: meta
scope: general
metadata:
  type: index
  node_type: router
  created: 2026-09-19
tags: [meta, sources, index]
keywords: [sources, citations, stubs, provenance]
---
# Sources

Flat `[[slug]]` citation registry. A stub exists here only for an external artifact with no home in the
KB; anything already in the KB is linked directly.

- [conventions-v1](conventions-v1.md) — the inherited work-system knowledge conventions, ancestor of the current contract
- [adr-0001-kb-root-resolution](adr-0001-kb-root-resolution.md) — decision record for how agents resolve the general knowledge root
- [adr-0002-governance-without-enforcement](adr-0002-governance-without-enforcement.md) — which guardrails are enforced, dormant, or absent, and the accepted risk
- [adr-0003-scoping-topology](adr-0003-scoping-topology.md) — where each tier of knowledge lives, and why the project nests inside the general root
- [adr-0004-scope-attribute](adr-0004-scope-attribute.md) — the scope: values, the capture-time classification test, and the check-scope rules
- [adr-0005-currency-cadence](adr-0005-currency-cadence.md) — per-domain TTLs, verifier budgets, and the detection-vs-mutation automation gate
- [knowledge-agent-architecture-combination-plan](knowledge-agent-architecture-combination-plan.md) — the advisory reference-design proposal the five ADRs above decided from
