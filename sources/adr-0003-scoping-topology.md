---
name: adr-0003-scoping-topology
description: Source stub — ADR-0003, where each tier of knowledge lives and why the project nests inside the general root.
memory_type: reference
domain: meta
scope: general
metadata:
  type: source
  node_type: citation
  created: 2026-09-19
tags: [meta, adr, decision, source]
keywords: [ADR, scoping, topology, three homes, general tier, repo tier, latest-wins, nesting]
---
# Source: ADR-0003: Scoping topology — the three homes

- **Title:** ADR-0003: Scoping topology — the three homes
- **Origin:** Phase 1 decision record, 2026-09-19
- **Date ingested:** 2026-09-19
- **Artifact location:** `documents/decisions/0003-scoping-topology.md`

Records the three homes — general, repo, personal — and the deliberate deviation of nesting the project inside the general root. Safe only because the project is its own git repository and the parent ignores it, which makes cross-root resolution testable on one machine instead of failing first on someone else's. Also carries the latest-wins versioning stance and the risk that nesting invites relative traversal.
