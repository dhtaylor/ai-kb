---
name: adr-0006-behaviour-distribution
description: Source stub — ADR-0006, why the knowledge base is its own repository and its behaviour travels as a registered plugin.
memory_type: reference
domain: meta
scope: general
metadata:
  type: source
  node_type: citation
  created: 2026-09-19
tags: [meta, adr, decision, source]
keywords: [ADR, plugin, marketplace, repository, behaviour distribution, discovery, registration]
---
# Source: ADR-0006 — The knowledge base is its own repository

- **Title:** ADR-0006: The knowledge base is its own repository, and its behaviour travels as a plugin
- **Origin:** restructure decision, 2026-09-19
- **Date ingested:** 2026-09-19
- **Artifact location:** `documents/decisions/0006-behaviour-distribution.md`

Records that behaviour discovery walks up and stops at a repository root, so behaviour placed in a
workspace is reachable from exactly one directory and anything else must travel explicitly. Carries
what moved into the knowledge repository and why, the rejection of the maintenance-stays /
retrieval-travels split, the `check-kb` exclusion list, and the two open items: the workspace now
has no CI, and the relative marketplace path is untested.
