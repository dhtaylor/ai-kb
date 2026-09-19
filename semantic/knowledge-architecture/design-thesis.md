---
name: design-thesis
description: The core design thesis of a governed-KB-plus-thin-agent architecture — why knowledge and behavior are separated, the anti-pattern this rejects, and the target layering.
memory_type: semantic
domain: knowledge-architecture
scope: general
verified: 2026-09-19
metadata:
  type: fact
  node_type: memory
  created: 2026-09-19
tags: [knowledge-architecture, design, thin-agent, governed-kb]
keywords: [design thesis, knowledge as behavior, knowledge as document, anti-pattern, freshness engine, target architecture, thin agent layer, guardrails]
---
# Design thesis: separate knowledge from behavior

## The separation principle

The core design rule for combining a governed knowledge base with an agent layer:
**separate knowledge from behavior, and let the behavior layer keep the knowledge layer honest.**

- **Knowledge** (facts: schemas, system behavior, documented bugs, topology) lives *only* in the
  governed KB — one canonical home, provenance, dedup, contradiction handling.
- **Behavior** (agents + commands) carries *only* routing, procedure, tool scoping, and
  confirmation gates. It holds **no embedded facts** — it retrieves them from the KB at runtime
  and acts.
- **The loop that makes it more than either half:** because the behavior layer can *act* (query
  live systems), it becomes the KB's freshness engine — agents re-verify facts against the live
  system and re-stamp them. The KB gains currency; the behavior layer gains a single source of
  truth.

Source: [[knowledge-agent-architecture-combination-plan]] (§0)
Verified: 2026-09-19 · by: agent · method: doc-review

## The anti-pattern this rejects: knowledge-as-behavior

Two opposite ways to hold operational knowledge, compared property by property:

| Property | Knowledge-as-behavior (facts frozen in agent prompts) | Knowledge-as-document (a governed KB) |
|---|---|---|
| Single canonical fact | N copies, drift | one home |
| Provenance / auditability | none | per-section backlinks |
| Currency of facts | unmanaged | cited but unverified |
| Executable / operational | it acts | inert |
| Context economy at query time | whole prompt loads | progressive disclosure |
| Maintenance cost | scales with #agents | high ceremony |
| Team shareability | obvious, in-repo | can become bespoke/solo |
| Safety (secrets/leaks) | inlined | inert, nothing to leak |

The governed KB is the superior *knowledge* design; a behavior fleet is the superior *execution*
design. The optimum is the KB as substrate with a thin behavior layer on top of it.
**Knowledge-as-behavior is retained only as the anti-pattern to avoid** — the failure it embodies
(duplicated, unsourced, drifting facts) is exactly what the governed substrate prevents.

Source: [[knowledge-agent-architecture-combination-plan]] (§0)
Verified: 2026-09-19 · by: agent · method: doc-review

## Target layering

The combined architecture has four layers, and the discipline is that facts and secrets are
confined to exactly one of them each:

- **Governed substrate** (`knowledge/`) — the *only* place facts live: per-domain INDEX +
  single-topic files + provenance + contradictions, source citation stubs, currency stamps, and a
  golden-retrieval eval set.
- **Behavior layer** (thin) — domain-worker agents (least-privilege tools, "load knowledge/…,
  descend, cite, act") and procedures/commands with confirmation gates for state-changing
  operations, routed by a thin orchestrator. **No facts, no secrets** live here.
- **Secrets** — vault or env only, referenced by name, never inlined.
- **Guardrails** — a secret scan over *both* trees (the knowledge substrate and the behavior
  layer), plus least-privilege enforcement for production operations.

Source: [[knowledge-agent-architecture-combination-plan]] (§1)
Verified: 2026-09-19 · by: agent · method: doc-review
