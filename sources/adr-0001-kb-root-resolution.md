---
name: adr-0001-kb-root-resolution
description: Source stub — ADR-0001, the decision record for how agents resolve the general knowledge root.
memory_type: reference
domain: meta
scope: general
metadata:
  type: source
  node_type: citation
  created: 2026-09-19
tags: [meta, adr, decision, source]
keywords: [ADR, root resolution, KB_GENERAL_ROOT, session start hook, settings]
---
# Source: ADR-0001 — Knowledge base root resolution

- **Title:** ADR-0001: Knowledge base root resolution
- **Origin:** decision record produced by the Phase 0 acceptance test, 2026-09-19
- **Date ingested:** 2026-09-19
- **Artifact location:** `documents/decisions/0001-kb-root-resolution.md`

Records the tested decision that `KB_GENERAL_ROOT` lives in user-level settings and a SessionStart hook
injects the resolved absolute path, because the Read tool does not expand environment variables. Carries
the test evidence table and the open items the decision does not settle.
