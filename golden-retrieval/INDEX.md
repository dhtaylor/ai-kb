---
name: golden-retrieval-index
description: Flat registry of per-domain golden retrieval sets — the routing and answer-grounding eval cases each domain's fold obliges.
memory_type: reference
domain: meta
scope: general
metadata:
  type: index
  node_type: router
  created: 2026-09-19
tags: [meta, golden-set, index]
keywords: [golden retrieval, eval, index]
---
# Golden retrieval

One `<domain>-golden.md` per domain that has content. Created only once a domain has facts to
test against — an empty domain has nothing to seed a golden case from.

- [knowledge-architecture-golden](knowledge-architecture-golden.md) — routing and answer-grounding cases for the knowledge-architecture domain
