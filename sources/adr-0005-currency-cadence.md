---
name: adr-0005-currency-cadence
description: Source stub — ADR-0005, per-domain freshness horizons, verifier budgets, and the detection-automated mutation-gated rule.
memory_type: reference
domain: meta
scope: general
metadata:
  type: source
  node_type: citation
  created: 2026-09-19
tags: [meta, adr, decision, source]
keywords: [ADR, currency, TTL, freshness horizon, verifier budget, automation gate, trust tiers, needs-attention queue]
---
# Source: ADR-0005: Currency cadence — TTLs, budgets, and the automation gate

- **Title:** ADR-0005: Currency cadence — TTLs, budgets, and the automation gate
- **Origin:** Phase 1 decision record, 2026-09-19
- **Date ingested:** 2026-09-19
- **Artifact location:** `documents/decisions/0005-currency-cadence.md`

Records per-domain TTLs over one global interval, a hard verifier_budget per cycle, and the standing rule that detection is automated while mutation is gated behind a human. Carries the trust tiers — committer-derived identity, one-tenth TTL for agent stamps, human-only for high-blast-radius facts — and states plainly that none of it runs yet.
