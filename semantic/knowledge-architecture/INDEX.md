---
name: knowledge-architecture-index
description: Router for how this governed knowledge base and its thin-agent layer are designed to work — conventions, scoping, lifecycle, guardrails and agent contracts.
memory_type: reference
domain: knowledge-architecture
scope: general
freshness_horizon: 90d
verifier_budget: 5
metadata:
  type: index
  node_type: router
  created: 2026-09-19
tags: [knowledge-architecture]
keywords: [knowledge base, architecture, thin agent, retrieval contract, scoping, provenance, currency, lifecycle, guardrails, librarian]
---
# Knowledge architecture

How this knowledge base and the agent layer over it are designed to work: the separation of
knowledge from behavior, the scope tiers and their homes, provenance and currency, the retrieval
contract agents are held to, the lifecycle roles that keep facts current, and the guardrails that
keep the whole thing honest.

Scope tiers, provenance, currency, contradictions, the retrieval contract and frontmatter schema
are the operative contract — see `knowledge/CONVENTIONS.md`, not duplicated here.

- [design-thesis](design-thesis.md) — why knowledge and behavior are separated, the
  knowledge-as-behavior anti-pattern, and the target layering
- [agent-lifecycle-roles](agent-lifecycle-roles.md) — the Curator/Research-librarian/Fact-checker
  roles, PR-review and rollback governance for KB mutation, and the orchestrator's cost bounds
- [secret-governance](secret-governance.md) — why rotating a leaked secret isn't removal, and why
  a pre-commit scan isn't the enforcement boundary
