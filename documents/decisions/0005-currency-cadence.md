# ADR-0005: Currency cadence — TTLs, budgets, and the automation gate

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Phase:** 1 (inventory, map & decide)

## Context and problem statement

Provenance says where a fact came from; currency says whether it is still true. A governed KB
gets provenance right and currency wrong by default — facts are cited but unverified, and a
confidently-served stale fact is worse than an absent one, because nothing signals the error.

The naive fix, re-checking everything on a schedule, does not survive contact with a growing
library: cost scales with the whole KB, and a heuristic with no ceiling grows unbounded as
domains multiply.

## Decision drivers

- Being wrong about **detection** costs a glance at a false flag. Being wrong about **mutation**
  poisons the single source of truth everyone cites. These deserve different levels of trust.
- A stamp asserting freshness is worthless if the check behind it was wrong.
- Cost must be **bounded by construction**, not by hoping the heuristic behaves.

## Decision outcome

### 1. Per-domain TTL, never one global interval

Each domain's root `INDEX.md` declares `freshness_horizon` in its frontmatter. Volatile
deployment facts decay in days; fundamentals in years. One interval is wrong for both.

### 2. A hard budget per domain, per cycle

Each domain declares `verifier_budget: N` — the maximum number of facts re-checked per cycle,
highest-priority first. Priority is **volatility × blast radius**, stored as a score rather than
recomputed. The budget exists because no read-frequency signal is available to bound the
heuristic naturally; without a cap the cadence grows without limit as domains multiply.

### 3. Event-driven beats polling

Verify on ingestion, on a related pull request, and on a known system change. The scheduled
sweep is the backstop for what no event covers, not the primary mechanism.

### 4. The standing rule: **automate detection, gate mutation**

| Band | What | Control |
|---|---|---|
| Fully automated, unattended | Retrieval; staleness detection; drift detection; hygiene scanning | Output is a **queue only**, never an edit |
| Automated with approval | The fold, update, supersede | Drafted as a **PR**; a human reviews and merges |
| Never automated | Resolving contradictions; deleting knowledge; promoting repo→general; anything mutating the shared tier | Human, with the guards in [ADR-0004](0004-scope-attribute.md) |

The PR gate is cosmetic unless the review is defined. A reviewer who trusts the agent's
description without following the provenance provides no gate. So: Verifier PRs carry the exact
check run and its raw result; Watcher PRs carry the source URL and diffed excerpt, and **a dead
URL auto-rejects the PR**; the reviewer follows the provenance link and confirms it resolves.

### 5. Trust tiers on the stamp

- **`by:` is derived from the git committer identity**, not a written claim. A field is trivially
  forged; an identity is not. CI rejects a commit writing `by: human` from an agent identity.
- **Agent-verified TTL is one tenth of human-verified.**
- **High-blast-radius facts** — deploy targets, environment routing, credential references —
  require **human** re-verification regardless of any agent stamp.
- **No evidence, no re-stamp.** Every re-stamp records the exact check run, the observed value,
  and the expected value.
- **Absent is not fresh.** An unstamped section is `unknown` and surfaces **first**; a sweep
  cannot flag what was never written.

### 6. The queue is specified, or it becomes noise

`knowledge/needs-attention.md`. Each item carries a **stable ID** (hash of source + fact) so
re-runs deduplicate; a **status** (open / acknowledged / resolved) so an accepted flag is not
re-raised unless its source changes; the affected **CODEOWNERS @-mentioned**; a **maximum depth
per owner**; and **severity triage** — contradiction, then stale-high-blast, then stale-low-read.
Items aging past **14 days** escalate to team triage.

### 7. Defaults for the first domain

`meta` is design and architecture knowledge: slow-moving, and its blast radius is the whole
system. Starting values, to be revised from evidence rather than defended:

```yaml
freshness_horizon: 180d
verifier_budget: 5
```

## Consequences

**Good.** Cost is bounded by construction. Mutation of the single source of truth always passes
a human. Freshness is a property of the section that carries it, not a whole-file average.

**Bad — and this is most of the decision.** **None of this runs.** There are no live systems to
verify against, so the Verifier has nothing to query; the Watcher is speculative by the
architecture's own assessment and starts as a human-maintained digest, not automation. What is
decided here is **policy**, deliberately settled now because Phase 2 writes the INDEX frontmatter
that carries these fields, and retrofitting them across every domain later is the expensive path.

Recording it as decided must not be read as recording it as working. It is dormant until Phase 5
and until there are systems worth verifying against.

**Neutral.** The 1/10 agent TTL ratio and the 14-day escalation are arbitrary starting points.
They are written down so they can be argued with from evidence, which is more than an unstated
assumption offers.

## Open items

- The `verified_by`-from-committer CI check is specified, not built.
- No live systems exist; Verifier and Watcher are both Phase 5 and both currently unbuildable
  in any meaningful form.
- `needs-attention.md` does not exist; per the contract §3, a state leaf is created only when it
  has content.
