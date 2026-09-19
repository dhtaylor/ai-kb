---
name: knowledge-index
description: Root router for the general knowledge base — routes to the contract and the tier folders.
memory_type: reference
domain: meta
scope: general
metadata:
  type: index
  node_type: router
  created: 2026-09-19
tags: [meta, index, root]
keywords: [knowledge, root, index, router, tiers]
---
# Knowledge — general root

The general tier of the knowledge base (`$KB_GENERAL_ROOT/knowledge/`). Repo-specific knowledge lives in
its own project repo; personal knowledge lives in user-level config. See the contract for the scope test.

- [CONVENTIONS](CONVENTIONS.md) — the contract every domain conforms to: scope, layout, slugs, provenance, currency, contradictions
- [sources](sources/INDEX.md) — citation registry for external artifacts

Tier folders are listed here as they come into existence — `semantic/`, `episodic/`, `procedural/` and
`golden-retrieval/` are not yet created. Do not route to an empty folder.
