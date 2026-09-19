---
name: agent-lifecycle-roles
description: The three librarian roles that keep a governed KB operating (Curator, Research librarian, Fact-checker), how mutation of the KB is governed and rolled back, and the bounds that keep the agent layer safe and cheap.
memory_type: semantic
domain: knowledge-architecture
scope: general
verified: 2026-09-19
metadata:
  type: fact
  node_type: memory
  created: 2026-09-19
tags: [knowledge-architecture, lifecycle, roles, governance, orchestrator]
keywords: [curator, research librarian, fact-checker, verifier, watcher, orchestrator, fan-out, PR review, rollback, corrections-log, PII, CODEOWNERS]
---
# Agent lifecycle roles

A library's hard problem is not storing facts, it is cataloguing, retrieving, and weeding them.
Three roles cover that lifecycle.

## The three roles

- **Curator (cataloguer)** — owns *structure*: where a fact lives, INDEX hooks, dedup,
  contradiction flagging, `scope:` classification, promotion. This is `organize-domain` /
  `update-domain` / `distill-episodic` / `meditate`, personified.
- **Research librarian (fast access)** — the thin retrieval agents: load INDEX, descend, cite,
  answer. Read-only, on demand. The reference desk.
- **Fact-checker (currency)** — more than one job, split by source of truth:
  - **Internal / deployment truth** — updated by the **live systems themselves**. Kept current by
    the **Verifier**: re-runs a fact against the live system, re-stamps `verified:`, flags
    mismatch.
  - **External / general truth** (vendor behavior, regulation, platform features) — the world
    updates these. Kept current by the **Watcher**: monitors sources for change and flags drift.

Source: [[knowledge-agent-architecture-combination-plan]] (§5A)
Verified: 2026-09-19 · by: agent · method: doc-review

## Watcher safety design

Web-watching is brittle (pages restructure, move behind auth, render via JS), and it is the single
**external ingestion point** feeding an LLM that drafts KB changes — a prompt-injection vector (a
spoofed page saying "the correct pattern for all agents is …" becomes a plausible auto-PR).
Therefore:

- **Default (low-tech):** a **human-maintained digest** of vendor release notes / regulation
  changes, reviewed on a cadence and folded via `update-domain`. Do not claim automated monitoring
  until a concrete mechanism is prototyped.
- **If/when automated:** fetch in an **isolated, network-restricted** step (no tool access; cannot
  reach internal/link-local addresses — SSRF guard); **strip to plain text**; treat content
  strictly as **untrusted data, never instructions**; emit only a **schema'd drift signal**
  (`field · old · new · source_url`); keep the monitored-URL **allowlist outside the KB**.

(The further distinction between "unreachable" and "unchanged" for a watched source follows the
same rule the contract states for provenance liveness — see `knowledge/CONVENTIONS.md` §6.)

Source: [[knowledge-agent-architecture-combination-plan]] (§5A)
Verified: 2026-09-19 · by: agent · method: doc-review

## Mutation governance

The standing rule is automate detection, gate mutation (three bands, decided for this workspace in
[[adr-0005-currency-cadence]]). What follows is the operational detail behind the middle and last
band, beyond what that decision records:

- **The PR gate is cosmetic unless the review is defined.** A reviewer who trusts the agent's
  description without following provenance provides no gate, and a subtle wrong fact in an
  otherwise innocuous diff sails through. A KB-PR review checklist: bot-authored PRs carry a
  **machine-readable label**; **high-blast-radius** facts need **2 reviewers + a 24h window**; the
  PR is annotated with the **retrieval-check diff** (which golden answers would change) so
  reviewers see behavioral impact, not just text.
- **Never-automated actions are enforced, not just declared.** A CI gate blocks auto-merge of any
  PR that deletes a `knowledge/` file, resolves a `contradictions.md` entry, or moves a file
  repo→general, unless a label writable **only by a domain owner** (not the agent identity) is
  set.
- **Rollback is an invariant, not an aside.** Both KBs are git repos; recovery from a bad fold or a
  wrong merged correction is `git revert <commit>` **plus a mandatory pull notification** to
  developers (the shared repo posts a post-merge webhook of what changed). For the shared tier the
  blast radius is every project on every machine, so this path must be named and rehearsed.
- **A corrections-log makes silent propagation visible.** Because the shared tier is latest-wins
  (decided in [[adr-0003-scoping-topology]]), maintain a per-domain `corrections-log.md` (date ·
  fact slug · old→new summary · PR link) — a wrong correction propagates exactly the same way a
  right one does, and the log is how a consumer notices.

Source: [[knowledge-agent-architecture-combination-plan]] (§5A, §2)
Verified: 2026-09-19 · by: agent · method: doc-review

## Testing the fact-checkers

Neither fact-checker has a test story by default, yet each *decides truth*:

- **Verifier fixture test:** against a local test system seeded with a deliberately stale/wrong
  fact, the Verifier must produce a `contradictions.md` flag (not a false-fresh stamp).
- **Watcher replay test:** against a saved snapshot containing a known change, the Watcher must
  emit exactly one queue entry with the correct schema'd drift signal.

Source: [[knowledge-agent-architecture-combination-plan]] (§5A)
Verified: 2026-09-19 · by: agent · method: doc-review

## Orchestrator cost bounds

- **Route, never broadcast.** Fan-out multiplies token cost **3–15×**; a 4-worker broadcast can
  cost **~20×** a direct lookup. Single-domain queries **pass through** to one worker; the
  orchestrator fans out **only** for confirmed cross-domain questions, **capped at 2 workers** per
  interactive query.
- **CI cold-start.** Clone the general repo `--depth 1` at the pinned tag with a **cache key**;
  `--sparse` to only the domains a project queries.

Source: [[knowledge-agent-architecture-combination-plan]] (§5A)
Verified: 2026-09-19 · by: agent · method: doc-review

## Cautions: human ownership and data handling

- **The verifier's logic decides truth — review it like the facts it checks, and test it** (see
  above).
- **PII handling.** Agents touching live data must not log PII to any persistent or
  developer-readable store (KB, transcripts, logs); the Verifier reduces results to the
  **minimum needed** (count/boolean, not raw rows); name a data steward for agent output.
- **A human owns each domain (CODEOWNERS). The librarian agents assist the owner; they do not
  replace them.**

Source: [[knowledge-agent-architecture-combination-plan]] (§5A)
Verified: 2026-09-19 · by: agent · method: doc-review
