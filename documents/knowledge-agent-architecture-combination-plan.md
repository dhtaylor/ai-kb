# Combining the Governed Knowledge Base with a Thin-Agent Fleet — Implementation Plan

**Author:** Dandy Taylor (with Q)
**Date:** 2026-09-18 · **Revised:** 2026-09-19
**Status:** **Partly built.** Phases 0 and 1 complete, the behaviour layer built and tested, Phase 2
half done. Originally hardened by a five-lens adversarial review (findings tagged
`(hardening — <severity>)`); now revised again from **build findings** — see §9, which records what
implementation proved, disproved and cost.

> **Read §9 first if you are picking this up cold.** Three things in the sections below were wrong
> in ways that only appeared when the thing was built, and §1 in particular has been rewritten.

This is the next evolution of a governed knowledge base: turning a passive, well-curated **reference library**
into an **actionable system** — a thin agent layer that retrieves from the KB and acts, plus a lifecycle that
keeps the knowledge current. It is written to be reusable across projects; concrete domains appear as
`<domain-A>`, `<domain-B>`.

---

## 0. Design thesis

**Separate knowledge from behavior, and let the behavior layer keep the knowledge layer honest.**

- **Knowledge** (facts: schemas, system behavior, documented bugs, topology) lives *only* in the governed KB —
  one canonical home, provenance, dedup, contradiction handling.
- **Behavior** (agents + commands) carries *only* routing, procedure, tool scoping, and confirmation gates.
  It holds **no embedded facts** — it retrieves them from the KB at runtime and acts.
- **The loop that makes it more than either half:** because the behavior layer can *act* (query live systems),
  it becomes the KB's freshness engine — agents re-verify facts against the live system and re-stamp them. The
  KB gains currency; the behavior layer gains a single source of truth.

### Two archetypes, and why each alone is insufficient

The design reconciles two opposite ways to hold operational knowledge:

| | Knowledge-as-behavior (facts frozen in agent prompts) | Knowledge-as-document (a governed KB) |
|---|---|---|
| Single canonical fact | ❌ N copies, drift | ✅ one home |
| Provenance / auditability | ❌ none | ✅ per-section backlinks |
| Currency of facts | ⚠️ unmanaged | ⚠️ cited but unverified |
| Executable / operational | ✅ it acts | ❌ inert |
| Context economy at query time | ❌ whole prompt loads | ✅ progressive disclosure |
| Maintenance cost | ❌ scales with #agents | ⚠️ high ceremony |
| Team shareability | ✅ obvious, in-repo | ⚠️ can become bespoke/solo |
| Safety (secrets/leaks) | ❌ inlined | ✅ inert, nothing to leak |

The governed KB is the superior *knowledge* design; a behavior fleet is the superior *execution* design. The
optimum is the KB as substrate with a thin behavior layer on top of it. **Knowledge-as-behavior is retained
only as the anti-pattern to avoid** — the failure it embodies (duplicated, unsourced, drifting facts) is
exactly what the governed substrate prevents.

---

## 1. Target architecture

> **Rewritten 2026-09-19.** The original drew one tree holding both the governed substrate and the
> behaviour layer. Building it showed that arrangement violates §0 in the one place the separation
> most needs to be visible. Three repository kinds, not one tree:

```
engine  (behaviour ONLY — no domains, no facts)
  CONVENTIONS.md        the contract every library conforms to
  scripts/              check-kb, check-scope, check-secrets, embedded-fact lint
  plugins/<tools>/      skills, agents, commands — registered by consumers, never
                        inherited by directory accident
  documents/decisions/  ADRs; reached by relative link, same repo
  kb/                   created by the engine, NEVER tracked by it

domain library  (content ONLY — one repository per domain, portable)
  INDEX.md              the domain router IS the repo root; no tier chain above it
  <topic files>         gestalt-sized, per-section provenance + currency
  sources/              its own citation stubs
  documents/            archived evidence it was folded from
  <domain>-golden.md    its own retrieval oracle

project knowledge  (repo tier — inside each project repo, travels with the clone)

secrets       vault / env only, referenced by name, never inlined
guardrails    secret scan (committer-side AND server-side) + embedded-fact lint over the
              behaviour layer; least-privilege enforcement for prod ops
```

**The rule that makes it hold:** the engine holds no facts, a library holds no behaviour, and a
library is self-contained enough to be cloned onto a machine with neither an engine nor a sibling
library beside it. Anything reaching across a repository boundary uses a **repo-qualified
reference** (`ai-kb:CONVENTIONS.md`), never a relative path — see §9.4.

---

## 2. Knowledge scoping in a shared team environment

Two buckets isn't enough. Knowledge falls into **three tiers of scope**, and getting the middle tier wrong is
how a shared KB fails — over-share and every repo couples to a churning blob; under-share and you get
knowledge-as-behavior's N-copies drift, now across repositories instead of files.

### The three tiers

- **Repo-specific** — true only of *this* deployment: environment topology, deployment quirks, this system's
  known bugs, operational checklists. Lives *with the code it describes* (the project repo KB).
- **Product/org-general, cross-repo** — true wherever a product or concept appears: a vendor product's
  behavior and APIs, domain fundamentals, engine/platform behavior, architecture standards. Needs **one home
  referenced by many**, never a copy per repo.
- **Personal/universal** — an individual's working style and private lessons. User-level config. Deliberately
  *not* team-shared.

### The classification test (applied at capture)

When a fact is written, ask one question: *"Is this true only of this repo/deployment, or true wherever this
product/tool/concept appears?"* That routes it. Bake the test into the capture skills so it is answered every
time, not retrofitted.

### Where each tier lives — three homes, one glue

- **Repo-specific** -> `knowledge/` **inside the project repo**. Travels with the clone, shared with the
  project team for free, reviewed in the same PRs as the code.
- **General (cross-repo)** -> a **standalone shared-knowledge repo**, cloned once by each developer to a
  location *outside* any single project. One copy per machine, shared across every project on it — because
  general knowledge is owned by no single project. Contributions go through that repo's own PR review.
- **Personal** -> user-level config, per developer.

**The make-or-break rule: resolution by configured root, never a hardcoded path.** This is the exact point
where the topology either works or breaks — a hardcoded absolute path (e.g. a specific developer's home
directory) differs on every machine and silently fails elsewhere. The fix is one indirection point: a
configured root (env var, e.g. `KB_GENERAL_ROOT`, or a settings entry) resolved once at setup. Agent bodies
reference `$KB_GENERAL_ROOT/semantic/…`, **never a literal path**.

> **Unverified assumption — prove it first (hardening — Critical).** It is *not* established that a shell env
> var is inherited by an agent's execution context (sandbox / subprocess / OS boundary). If it is not, every
> path silently resolves to nothing and agents fall back to model memory — violating the retrieval contract
> with no error. **Phase 0 must include an acceptance test:** a running agent successfully reads
> `$KB_GENERAL_ROOT/semantic/<domain>/INDEX.md`. If it fails, switch the indirection to a settings entry (or a
> session-start-hook-exported var) before any agent file is written.
>
> **The configured root is a trust root — harden it (hardening — High).** Whoever can write a developer's
> `.env`, shell profile, or bootstrap script can repoint the root at attacker-controlled "knowledge" that
> every agent then cites as canonical. Mitigations: (a) store the root in **user/system-level** settings, not
> a project file a repo can overwrite; (b) pin the general repo's remote to the canonical org URL, not a
> configurable override; (c) the bootstrap records the cloned commit SHA locally and a wrapper warns if HEAD
> diverges unexpectedly before load.

The **behavior layer** has its own matched mechanism: share *general* agents/commands as a plugin/marketplace
across projects; keep *repo-specific* agents in the project repo. General agents travel as plugins; general
knowledge travels as the shared repo.

### Versioning stance: latest-wins for humans, pin only for automation

The shared repo is **pulled latest, not pinned per project** — for a *knowledge* base that is the correct
default. Code dependencies need pinning for reproducible behavior; facts are the opposite. A correction should
propagate immediately, not sit behind a version bump in ten repos. **Exception:** anywhere the general KB
feeds something *automated* (a CI eval, an unattended agent), non-determinism bites — pin there (developers
track HEAD; CI checks out a tagged ref).

> **Silent behavior change — the carve-out's blind spot (hardening — High).** "Pin only for CI" misses the
> most consequential case: latest-wins means a shared-KB correction instantly changes what every
> *developer-facing, state-changing* agent does — with no PR, CI run, or review in any consuming project. Two
> mitigations, pick explicitly: (a) require every shared-KB PR to run the **deterministic retrieval check
> across registered consuming projects** before merge; and (b) maintain a per-domain **`corrections-log.md`**
> (date · fact slug · old→new summary · PR link) so "propagate immediately" is a visible feature, not a silent
> hazard. A wrong correction propagates the same way — the log is how a consumer notices.

### Onboarding & keeping it current

- **Bootstrap:** one setup command clones/updates the general repo to the configured root and sets the root
  variable. Cloning-per-developer only scales if it is one command.
- **Staleness nudge:** latest-wins only works if people actually pull. **Note (hardening):** checking a remote
  for new commits is a *new* mechanism (a memory-hygiene sweep does not do git network ops) — implement it as
  a **session-start hook** that fetches and warns if HEAD is behind by more than N days; prefer pull-at-start
  in high-volatility phases.
- **Residual risk — intra-day corrections (hardening).** The N-day nudge addresses *chronic* staleness, not
  same-day drift. Only a session-start pull (or real-time notification, out of scope) closes it. Document as
  accepted residual risk, not something the nudge solves.

### Query-time connection

An agent inside a project resolves its knowledge root to **both trees** — local `knowledge/` and
`$KB_GENERAL_ROOT` — and progressive disclosure spans both indexes. A project fact that *depends* on a general
fact **links to it (`[[slug]]`), never restates it** (single-canonical-home rule across the KB boundary).

- **Graceful absence (hardening).** A project `[[slug]]` into the general repo is a soft cross-repo
  dependency. If a dev has not cloned the general repo, agents must *warn*, not crash — the project KB must
  stay usable standalone.
- **Cross-link validation is a real tool, not "a small CI step" (hardening — High).** Cross-root `[[slug]]`
  resolution does not exist yet; until it does, every cross-repo link placed during a fold is unvalidated and
  dead links accrue silently. Specify it now and make it a deliverable that blocks broad rollout:
  - **Slug format & precedence.** `slug` = filename without extension. Bare `[[slug]]` resolves within the KB
    root it appears in; cross-tree links use an explicit prefix (`[[general:some-fact]]`). A cross-root
    **uniqueness constraint** (enforced by `check-scope`) prevents ambiguous duplicates. On any residual
    collision: **repo-local wins for repo-scoped queries**; the `general:` prefix is required otherwise.
  - **Performance (hardening).** Naive resolution is O(files) per link × many repos. The general repo
    publishes a generated **slug→path manifest** (single JSON, updated on every merge); consumers fetch that
    one file and resolve O(1) locally.

### Make scope a first-class attribute

Add a **`scope:` frontmatter field** — e.g. `repo:<project>`, `product:<vendor>`, `org:<company>`, `general`.
Scope becomes greppable: audit what is misfiled, and later extract a general layer without re-reading
everything. A KB that grew organically almost always **mixes scopes silently** — vendor-general facts sitting
beside deployment-specific ones in the same domain — so treat scope backfill as real work, not a formality.

### The promotion path (and its guard)

Knowledge usually *starts* repo-specific and later proves general. Provide a lightweight **promotion**: move
the fact repo-KB -> shared-KB, leave a backlink at the origin. **Guard:** one observation ≠ a general truth.
Promote only when confirmed against the product/vendor source, not merely seen once. Two hardening rules:

- **No circular promotion (hardening — High).** The confirming source must be **external to the KB** — a live
  vendor URL with excerpt, a direct system result, or a named human attestation with external citation. If the
  agent's logged evidence is *another KB file*, the promotion is **rejected**. The KB may never be its own
  evidence for general-tier truth.
- **Atomic promotion (hardening — High).** The shared-KB add and the origin-stub update are a **single paired
  commit/PR** — otherwise the dual-root resolver finds both the promoted copy and the full pre-promotion copy
  in the gap, silently undoing the dedup. The origin becomes an **empty redirect stub** that cannot answer
  queries (agents follow the link, never serve stub content).

### Governance

The shared tier needs **owners per domain** (CODEOWNERS) — "everyone's knowledge is no one's knowledge" is how
a shared KB rots. Repo KB is owned by the project team.

> **CODEOWNERS is only a control if enforced (hardening — High/Medium).** As plain text it is advisory.
> Specify in the shared repo's branch protection: (a) **CODEOWNERS review is a required status check**; (b)
> **≥2 approvals** and **self-merge blocked** on `main`; (c) **each domain has ≥2 named owners** so one
> departure doesn't orphan it; (d) **signed commits** for merges; (e) `check-links` + `check-scope` + the
> deterministic retrieval check pass pre-merge. A hygiene sweep flags any domain whose owners are empty or
> departed.

### The tradeoff to keep honest

**Coupling vs. drift.** The two failure modes are copying general facts "just this once" into a repo (→
N-copies drift across repositories) and letting a project silently depend on a general repo it does not have.
The topology above defends against both. The discipline it demands is narrow but absolute: **nobody ever
writes an absolute path, and everybody actually pulls.** Latest-wins only works if both hold.

---

## 3. Weakness -> mechanism map

### Fixing knowledge-as-behavior's weaknesses

| Weakness | Fix in combined design |
|---|---|
| No single source of truth | All facts live in KB canonical homes; agents retrieve, never embed |
| No provenance | KB `Source:` backlinks; external artifacts ingested as `sources/` stubs |
| Drift across copies | One home + `contradictions.md`; conflicts flagged and marked, not duplicated |
| Secrets inlined | Vault-by-reference; secret scan blocks re-entry; rotate any leaked secret |
| Maintenance scales with #agents | Thin agents -> a schema change edits *one* KB file, all agents see it |
| Near-duplicate agents | Collapse variants into one agent that loads per-variant KB files by parameter |
| Over-broad tools | Least-privilege audit; the most sensitive (PII-touching) agent gets the *narrowest* toolset |

### Fixing the governed KB's weaknesses

| Weakness | Fix in combined design |
|---|---|
| Inert / can't act | The thin agents ARE the execution layer — KB becomes operational |
| Silent retrieval failure | **Retrieval contract** (cite the file(s) used; if not found, say so) + a two-tier eval (deterministic routing per-PR; answer-grounding scheduled) + an **embedded-fact lint** (§5.1/§5.2), since the eval alone can't prove a fact wasn't answered from memory |
| Heavy ceremony / bus-factor | Skills are the on-ramp for fact **capture** only; scope classification, target-domain choice, golden-set authoring, TTLs and reviewing librarian PRs still need CONVENTIONS knowledge — so **≥2 devs per domain** learn it before becoming CODEOWNERS; a 1-page contributor guide; shared repo makes it team-owned |
| Provenance ≠ currency | **`verified:` frontmatter** + hygiene sweep flags stale facts + a `verify-domain` command that re-checks against live systems and re-stamps (with evidence, §5.3) |
| Personal, not shared | Move general knowledge to the shared repo; co-reviewed in PRs |

---

## 4. The KB-maintenance skills are the machinery

Built *on* existing KB tooling — no new consolidation machinery invented:

- **`create-domain`** — stand up domains that don't exist yet; seed from source material.
- **`update-domain`** — the workhorse: fold an external/legacy source document (a spec, a prior agent prompt,
  a vendor page) into an existing domain with per-section provenance; it does dedup/merge/supersede.
- **`organize-domain`** — run after a fold on any domain that comes out lumpy.
- **`distill-episodic`** — turn meeting notes / session logs into durable semantic facts.
- **`meditate`** — the acceptance gate after each wave *and* the recurring hygiene sweep (dead links, stale
  `verified:` dates, orphaned facts, index bloat).

---

## 5. New mechanisms to build (only what's missing)

1. **Thin-agent template** — frontmatter (name, description, least-privilege `tools`, `model`) + a fixed body
   preamble: *"Your knowledge lives at `knowledge/semantic/<domain>/`. Load INDEX, descend to the relevant
   file(s), cite them, then act. Do not answer from memory."*
   - **Embedded-fact lint (hardening — Critical).** "Retrieve, don't embed" is unenforceable by the eval
     alone — an inlined schema still routes correctly and passes. Add a **pre-commit + CI lint** over the
     agent/command files that flags embedded-fact patterns (identifiers, numeric constants, env-specific
     values, credential-shaped strings). The golden set is the fire alarm; the lint is the lock.
   - **Prompt caching (hardening — Low).** Put the fixed preamble + INDEX content in the cacheable prefix so
     repeat queries (and cadence-run librarians) don't re-pay for them.
   - **Multi-file / cross-domain retrieval (hardening — High).** "file(s)" is plural deliberately: a question
     can need a general-tier fact *and* a repo-tier fact. The agent loads and cites **all** files used and
     states when an answer is partial; genuinely cross-domain questions route through the orchestrator (§5A).
     Include a cross-domain case in the golden set.
2. **Retrieval contract + golden set** — `knowledge/golden-retrieval/<domain>.md` (YAML: `question:`,
   `expected_file:`, `expected_excerpt:`). **This is not "run like `check-links`"** — `check-links` is
   deterministic; an LLM route is not. Split into two tiers:
   - **Deterministic routing check (per-PR CI, cheap, reliable):** validates INDEX entries and `[[slug]]`
     resolution point to the expected file — no LLM. Gates every commit.
   - **Answer-grounding eval (scheduled/sampled, not per-commit):** runs the actual agent; the answer must
     contain the `expected_excerpt` **verified by grep against the expected file** (not an LLM judge) — this
     catches answering from memory. Define an acceptable pass rate; **sample** N questions rather than all
     `12 × domains` every run (cost otherwise scales with the whole library). Include ≥2 **negative** cases
     per domain (must refuse to guess) and ≥1 **UNRESOLVED** case (must surface the conflict, §5A). The golden
     set updates **in the same PR** as any file rename/split (an `organize-domain` exit criterion), else the
     oracle rots.
3. **Currency stamping** — `verified: YYYY-MM-DD`; a `verify-domain` command re-checks highest-risk facts
   against the live system and re-stamps (or opens a `contradictions.md` flag on mismatch). Hardened:
   - **Verification evidence, not just a date (hardening — High).** A stamp is worthless if the check was
     wrong (queried the wrong source, joined on the wrong key). Every re-stamp records the **exact check run,
     the observed value, and the expected value** (companion record or structured frontmatter). No evidence,
     no re-stamp.
   - **Trust tiers (hardening — Critical).** `verified_by` is **derived from the git committer identity**, not
     a free-form field (a field is trivially forged; identities are not). Agent-verified TTLs are materially
     shorter than human-verified (e.g. 1/10th); **high-blast-radius** facts (deploy targets, env routing,
     credential refs) require **human** re-verification regardless of any agent stamp. CI rejects a commit
     writing `verified_by: human` from the agent identity.
   - **Absent ≠ fresh (hardening — Medium).** A file with no `verified:` is `unknown`, surfaced **first** in
     the queue (a sweep can't flag what's missing). A one-time backfill classifies existing facts; a
     frontmatter lint (date-format) runs in the Phase 0 pre-commit hook.
4. **Secret governance** — a secret-scanner pre-commit hook over both trees; vault references by name only.
   - **Rotation ≠ removal (hardening — Critical).** Rotating a leaked secret does not erase it from git
     *history* — every clone still holds it. Any existing leak requires **history rewrite** (e.g.
     `git filter-repo --invert-paths`), force-push, clone invalidation, and a clean full-log scan.
   - **Pre-commit is bypassable (hardening — High)** (`--no-verify`). The enforcement boundary is a
     **server-side/CI gate** (push protection, or a CI job failing the build on any detected secret). Both are
     Phase 0 exit criteria.

---

## 5A. Knowledge lifecycle & the librarian roles

The KB is a library, and a library's hard problem is not storing books — it is cataloguing, retrieving, and
weeding them. Three roles cover that lifecycle.

### The roles

- **Curator (cataloguer)** — owns *structure*: where a fact lives, INDEX hooks, dedup, contradiction flagging,
  `scope:` classification, promotion. This is `organize-domain` / `update-domain` / `distill-episodic` /
  `meditate`, personified.
- **Research librarian (fast access)** — the thin retrieval agents (§5.1): load INDEX, descend, cite, answer.
  Read-only, on demand. The reference desk.
- **Fact-checker (currency)** — the new role, and it is more than one job, split by source of truth.

### Sources of truth -> fact-checkers

Conflating currency sources is dangerous (a web-watcher pointed at facts the web can't confirm; a system-check
trusted to catch a vendor change it can't see):

- **Internal / deployment truth** — updated by the **live systems themselves**. Kept current by the
  **Verifier**: re-runs a fact against the live system, re-stamps `verified:`, flags mismatch.
- **External / general truth** (vendor behavior, regulation, platform features) — the world updates these.
  Kept current by the **Watcher**: monitors sources for change and flags drift.
- **External-runtime truth (hardening — Medium; a gap the two-checker split misses).** A SaaS vendor can
  silently change *runtime behavior* without touching its docs. Such a fact passes the Watcher (docs
  unchanged) **and** the Verifier (no query sees it) and rots silently. Add
  `verification_method: integration-test|manual`, re-checked by running an actual transaction against a
  staging environment on each vendor release.

> **The Watcher is speculative — scope it honestly (hardening — Medium/Critical).** Web-watching is brittle
> (pages restructure, move behind auth, render via JS) and it is the single **external ingestion point**
> feeding an LLM that drafts KB changes — a prompt-injection vector (a spoofed page saying "the correct
> pattern for all agents is …" becomes a plausible auto-PR). Therefore:
> - **Default (low-tech):** a **human-maintained digest** of vendor release notes / regulation changes,
>   reviewed on a cadence and folded via `update-domain`. Do not claim automated monitoring until a concrete
>   mechanism is prototyped.
> - **If/when automated:** fetch in an **isolated, network-restricted** step (no tool access; cannot reach
>   internal/link-local addresses — SSRF guard); **strip to plain text**; treat content strictly as
>   **untrusted data, never instructions**; emit only a **schema'd drift signal**
>   (`field · old · new · source_url`); keep the monitored-URL **allowlist outside the KB**; and distinguish
>   **"unreachable" from "unchanged"** — a 404 is an alert, not silence.

### The automation principle: automate detection, gate mutation

Being wrong about *detection* costs a glance at a false flag; being wrong about *mutation* poisons the single
source of truth everyone cites. Three bands:

- **Fully automated (unattended, scheduled):** retrieval; staleness *detection*; drift *detection*; hygiene
  *scanning*. All of it only builds a **"needs attention" queue**.
- **Automated-with-approval (proposes, human commits):** the fold/update/supersede — drafted **as a PR against
  the KB**; a human reviews and merges.
  - **The PR gate is cosmetic unless the review is defined (hardening — Critical).** A reviewer who trusts the
    agent's description without following provenance provides no gate, and a subtle wrong fact in an otherwise
    innocuous diff sails through. Require a **KB-PR review checklist**: Verifier PRs include the exact check +
    raw result; Watcher PRs include the source URL + diffed excerpt, and a **dead URL auto-rejects the PR**;
    the reviewer **follows the provenance link and confirms it resolves**. Bot-authored PRs carry a
    machine-readable label; **high-blast-radius** facts need **2 reviewers + a 24h window**, and the PR is
    annotated with the **retrieval-check diff** (which golden answers would change) so reviewers see
    behavioral impact, not just text.
- **Never automated:** resolving contradictions; deleting knowledge; promoting repo→general (external
  evidence, §2); anything mutating the shared tier many projects depend on.
  - **Enforce it, don't just declare it (hardening — Low).** A CI gate blocks auto-merge of any PR that
    deletes a `knowledge/` file, resolves a `contradictions.md` entry, or moves a file repo→general, unless a
    label writable **only by a domain owner** (not the agent identity) is set.
- **Rollback is an invariant, not an aside (hardening — Critical).** Both KBs are git repos; recovery from a
  bad fold or a wrong merged correction is `git revert <commit>` **plus a mandatory pull notification** to
  developers (the shared repo posts a post-merge webhook of what changed). For the shared tier the blast
  radius is every project on every machine, so this path must be named and rehearsed.

### Cadence — do not run fact-checkers over the whole library every night

- **Per-domain TTL, not one interval.** Volatile deployment facts decay in *days*; fundamentals in *years*.
  Set the freshness horizon per domain, in its INDEX.
- **Event-driven beats polling.** Verify on ingestion, on a related PR, on a known system change.
- **Prioritize by volatility × blast radius**, and **cap it (hardening — High):** a heuristic has no ceiling
  and no read-frequency signal exists, so give each domain INDEX a **`verifier_budget: N`** (max facts checked
  per cycle by a stored score). Without a hard cap the cadence grows unbounded as domains multiply.

### Cost & scale bounds (hardening)

- **Orchestrator routes, never broadcasts (Critical).** Fan-out multiplies token cost 3–15×; a 4-worker
  broadcast can cost ~20× a direct lookup. Single-domain queries **pass through** to one worker; the
  orchestrator fans out **only** for confirmed cross-domain questions, **capped at 2 workers** per interactive
  query.
- **Resolve the two roots in parallel (High).** Mandate **parallel** index reads; single-root queries must
  not pay for the second root.
- **Bound INDEX size (Medium).** Enforce the CONVENTIONS threshold (~15 topic files → sub-index); above it,
  split into query-classified sub-indexes so an agent loads only the relevant one.
- **CI cold-start (Medium).** Clone the general repo `--depth 1` at the pinned tag with a **cache key**;
  `--sparse` to only the domains a project queries.

### The "needs attention" queue — specify it or it becomes noise (hardening — High)

It lives as `knowledge/needs-attention.md` (or issues tagged `kb-review`); each item has a **stable ID** (hash
of source+fact) so re-runs **deduplicate**; a **status** (open/acknowledged/resolved) so an accepted flag is
not re-surfaced unless the source changes; the affected **CODEOWNERS are @-mentioned**; a **max depth per
owner** and **severity triage** (contradiction > stale-high-blast > stale-low-read); items aging past **14
days** escalate to team triage.

### Cautions

- **False freshness** — handled by the evidence-record and trust-tier rules in §5.3.
- **The verifier's logic decides truth — review it like the facts it checks**, and **test it** (below).
- **Provenance rot (hardening — High).** `check-links` covers internal `[[slug]]`s, not external `Source:`
  URLs. When a vendor reorganizes, the URL 404s, `check-links` still passes, and the Watcher's "no diff" is
  indistinguishable from "unchanged." Add cheap **HTTP HEAD liveness checks** for external source URLs in CI;
  a dead URL flags dependent facts `provenance: BROKEN` (surfaced by the sweep, treated as unverified).
- **PII handling (hardening — Medium).** Agents touching live data must not log PII to any persistent or
  developer-readable store (KB, transcripts, logs); the Verifier reduces results to the **minimum needed**
  (count/boolean, not raw rows); name a data steward for agent output.
- **A human owns each domain (CODEOWNERS).** The librarian agents assist the owner; they do not replace them.

### Testing the librarian agents (hardening — High)

Neither fact-checker has a test story, yet each *decides truth*. Make these exit criteria:
- **Verifier fixture test:** against a local test system seeded with a deliberately stale/wrong fact, the
  Verifier must produce a `contradictions.md` flag (not a false-fresh stamp).
- **Watcher replay test:** against a saved snapshot containing a known change, the Watcher must emit exactly
  one queue entry with the correct schema'd drift signal.

### Contradictions must become unretrievable, not just annotated (hardening — Critical/High)

`contradictions.md` is an annotation *beside* the live facts — the retrieval path never consults it, so an
agent still serves one of the conflicting values with confidence. Fixes: mark conflicting entries **inline**
with `status: CONFLICTED`; retrieval agents **refuse to serve a CONFLICTED fact** and instead surface the
conflict (with an UNRESOLVED case in the golden set proving this). Distinguish **blocking** contradictions
(fact actively needed) from **informational** ones, with an SLA: a blocking contradiction **must be cleared
before its domain is promoted to the general tier**. Name who resolves and via what artifact — flagging
forever just accretes.

---

## 6. Phased implementation

> **Delivery reality — decouple from deadlines (hardening — Critical).** This is knowledge-architecture work;
> it must not consume a delivery-critical sprint. **Do-now scope: Phase 0 (guardrails) and Phase 1 (inventory
> + decisions) only.** Everything Phase 2+ is scheduled work with its own dates. A phase without a delivery
> date is a wish, not a plan.

> **Least-privilege is a prerequisite, not a late phase (hardening — High).** Gating state-changing commands
> and scoping tools must land **before any agent runs** — otherwise a prompt-injection / KB-poisoning event
> during buildout lands in an agent that can mutate production. `permissions.deny`-style config is
> *client-side*; the **primary** control is the service account each agent authenticates as (retrieval agent =
> read-only, no execute on deploy operations). Name the service-account tiers (retrieval / Verifier / Watcher)
> in Phase 1.

### Phase 0 — Guardrails (do first)
Secret-scan **pre-commit hook AND server-side/CI gate** live; any existing leak rotated **and history
rewritten**; the **configured-root resolution acceptance test** passes (or the settings fallback is adopted);
frontmatter + embedded-fact lints wired.
**Exit:** no secret can be committed *or pushed*; full-log scan is clean; an agent can read a file under the
configured root.

### Phase 1 — Inventory, map & decide
One table: each existing agent/command + any legacy source material -> target KB domain (existing/new/merge),
target thin agent, and **`scope:` tier**. Flag every **multi-domain source** — these fold **once per target
domain**, with explicit per-domain fact selection. Identify near-duplicate collapses. Name the agent
**service-account tiers**. Audit the existing KB for scope misclassification.
**Exit:** signed-off mapping **AND** the scoping topology + shared-repo decision **recorded as ADRs** (§8),
settled *before* the pilot, since they fix every retrieval path the pilot hardcodes.

### Phase 2 — Pilot one representative domain end-to-end
Pick the most mature, information-rich domain. `update-domain` folds source material in with provenance;
`organize-domain` reshapes; write the thin domain agent + one command over it; build the golden set (incl.
negatives + an UNRESOLVED case); `meditate` to verify. **Near-duplicate collapse design:** the variant is a
**required parameter**; the agent loads `…/<variant>.md` and **fails explicitly** if absent rather than
hallucinating.
**Exit:** the thin agent (a) answers real questions citing KB files; (b) passes the **deterministic routing
check** and the **answer-grounding eval**; (c) responds "fact not found — check KB" on a missing file
(graceful absence); (d) surfaces the `verified:` date on freshness-sensitive facts; (e) refuses the
negative/UNRESOLVED cases. **Do not fan out until this is clean.**

### Phase 3 — Roll out remaining domains in waves
Each following the Phase-2 recipe; `create-domain` where new. Contradictions flagged **and marked
`CONFLICTED`** (§5A), not silently resolved. **Blocked on** the cross-root `check-links` resolver existing and
running in CI (§2) — without it, dead cross-repo links accrue.

### Phase 4 — Orchestration + safety hardening
Thin orchestrator (**routes, capped fan-out**, §5A) over the domain workers; full least-privilege tool audit;
state-changing commands armed with confirmation gates.
**Exit:** Verifier fixture test and Watcher replay test pass; high-blast-radius PR policy enforced.

### Phase 5 — Steady state, librarians & team onboarding
1-page contributor guide; stand up the **Verifier** (per-domain TTL over internal facts) and **Watcher**
(general-tier, per its speculative scoping) — detection-only into the queue, mutation via PR; per-domain
freshness horizons in each INDEX; `distill-episodic` on a cadence; `meditate` on a schedule.
**Exit:** a contributor who has read only the 1-page guide can *capture* a fact correctly, and stale or
drifted facts surface as a queue rather than rotting silently.

---

## 7. Risks & accepted residual limitations

- **Folding is where facts get corrupted — and `update-domain` is itself an LLM (hardening — Critical).**
  "Verbatim moves" is *not* guaranteed by an LLM fold: it can round a constant, drop a qualifier, or merge two
  behaviors into one generalization. Mitigation: **require a human diff of each extracted fact against its
  source** before commit (a Phase 2 exit criterion), or restrict `update-domain` to structure and
  **copy-paste** load-bearing values.
- **Retrieval discipline is a behavior, not a guarantee** — the golden set is a fire alarm on fixed questions;
  the **embedded-fact lint** (§5.1) is the actual lock.
- **Scope creep** — the pilot-first gate exists to validate before spending fleet-scale effort.

**Accepted residual limitations (documented, not solved):**
- **Intra-day staleness** — latest-wins + an N-day nudge misses same-day corrections; only a session-start
  pull would (§2).
- **External-runtime facts** — vendor behavior changing without doc or system signal is only caught by
  integration re-test on each release (§5A).
- **The Watcher is speculative** — until a monitoring mechanism is prototyped, external currency is a
  human-maintained digest, not automation (§5A).
- **The PR gate depends on human diligence** — the checklist, dead-URL rejection, and 2-reviewer high-blast
  policy reduce but do not eliminate the risk of a rushed merge.

---

## 8. Open decisions / next actions

1. **Scoping topology** — repo-local KB, standalone general repo, or a split; and the `KB_GENERAL_ROOT`
   convention + bootstrap. **Settle at Phase 1 exit** (the pilot hardcodes retrieval paths against it).
2. **`scope:` frontmatter now**, with `check-scope` rules (cross-root uniqueness; general-tier promotion needs
   a CODEOWNER scope audit). Backfill scope onto existing facts in Phase 1.
3. **Automation cadence, per-domain TTLs & budgets** — freshness horizon and `verifier_budget: N` per domain;
   Verifier event-driven vs. scheduled; confirm detection/mutation gate as the standing rule. `verified_by` is
   **derived from git committer identity**, not a hand-written field (§5.3).
4. **Decisions are ADRs, not in-place edits (hardening — Medium).** Each decision above is recorded as an ADR
   in `documents/decisions/` (MADR template) with alternatives and rationale; this document is the *proposal*,
   the ADRs are the *record*.
5. **Safe to start now (non-destructive):** Phase 0 guardrails (secret scan + history plan + resolution
   acceptance test) and Phase 1 mapping (with `scope:` tiers, multi-domain flags, service-account tiers) plus
   the existing-KB scope audit.

---

## 9. Findings from implementation (2026-09-19)

What building this proved, disproved and cost. Recorded because most of it was invisible from
reading — including from reading this document, which was wrong in three structural ways that only
surfaced on contact.

### 9.1 The pattern, stated once

**Almost nothing important was found by inspection.** Every defect below was found by running
something and checking the result against what it claimed. Code that read correctly exited with the
wrong status; a contract that read consistently contradicted itself; skills that read as complete
were underspecified in ways a fresh reader hit immediately. The single highest-value technique was
handing an artifact to someone who had not written it and asking what was ambiguous.

### 9.2 The Critical assumption was wrong in the way that mattered

§2 flagged as Critical that it was unproven whether a shell environment variable reaches an agent's
execution context, and required an acceptance test. It does reach it — **and that was not the
problem.** The **Read tool does not expand environment variables**, and its failure message
volunteers the working directory, which invites a relative-path retry that succeeds by coincidence
in one workspace and fails silently everywhere else. The same class of failure the test existed to
rule out, relocated from the variable to the tool.

Resolution: the variable lives in user-level settings and a **SessionStart hook injects resolved
absolute paths** into context. No file anywhere holds a literal path; no agent handles the variable.

### 9.3 Behaviour discovery stops at a repository root

Absent from this plan entirely, and it determines where behaviour can live. Claude Code walks **up**
from the working directory for agents, skills and commands, and **stops at the repository root** —
it never descends. So behaviour placed in a workspace is reachable from exactly one directory, and
anything that must reach elsewhere travels by explicit registration. This is why the behaviour layer
is a **plugin**, not a folder: a plugin works identically whether the consumer sits beside the
engine or anywhere else on disk, whereas inheritance-by-nesting works only in the layout that
produced it.

An unexpected dividend: a `directory`-sourced plugin is read **in place**, not copied to a cache. So
behaviour and the facts it operates on are the same working tree by construction and **cannot
drift** — which is the argument for rejecting a git source even after the engine gained a remote.

### 9.4 Cross-repository citation is structural, not incidental

The plan handles cross-root `[[slug]]` resolution but never addresses citing an **artifact** in
another repository. Splitting content into per-domain libraries makes this unavoidable. Two rules,
in order:

- **Evidence travels with the domain it was folded from** — archive it in the library. Not a
  single-canonical-home violation: **the rule is one home per fact, not per document.** A fact
  stated twice drifts because someone edits a copy; an archived artifact does not, because if it
  changes it is a new artifact with a new ingestion date.
- **What cannot travel gets a repo-qualified reference** (`<repo>:<path>`), **never a relative path
  across a boundary** — that resolves only while two repos sit in the expected layout.

Extracting the first library broke eight `[[adr-…]]` links on contact, which is how the rule was
arrived at rather than theorised.

### 9.5 Contract defects found only by running the contract

Each of these read as coherent and was self-contradictory in use:

| Defect | Why it mattered |
|---|---|
| `CONFLICTED` marked at **section** granularity | Refusal is wholesale, so one disputed value took its undisputed neighbours offline — an agent blinded to correct knowledge because something nearby was in doubt |
| Golden set required `≥1 UNRESOLVED` **unconditionally** | A domain with no contradiction could satisfy it only by manufacturing one |
| The golden-set record schema had **no field** marking a case negative/unresolved | The minimum counts it demanded were unenforceable as written |
| `verified:` floor undefined when **no section carries a stamp** | After a fold marked every claim disputed, frontmatter kept a date certifying nothing |
| `CONFLICTED` carried **no date** | Its age drives escalation, and nothing recorded when the dispute began |
| Golden sets named `<domain>.md` | **A folder name is a slug too** — so every golden set collided with its own domain folder. Guaranteed, once per domain |
| `name` must match filename, but every folder has an `INDEX.md` | The contract violated its own rule on day one; path-addressed files needed an explicit exemption |

### 9.6 Guardrail defects found only by running the guardrails

- **A scanner printed every finding and exited 0.** Piping into a function put the counter in a
  subshell. It warned, then waved the commit through — worse than no guardrail, because it reads as
  protection.
- **Scripts were committed non-executable.** `core.fileMode` is false on this mount, so git recorded
  644 despite the disk showing otherwise, and **git skips a non-executable hook silently**. Every
  guardrail was inert for anyone but the authoring working copy. Only cloning and attempting a bad
  commit surfaced it; `ls -l` looked perfect throughout.
- **`meditate`'s own output failed the check `meditate` mandates.** Following it literally produced a
  queue file with no frontmatter, which the next sweep would report as an orphan.

### 9.7 What the plan got right, confirmed under test

- The **fold rules** hold. Against a fixture rigged with nine corruptions a fold is tempted to make,
  all nine were resisted: values verbatim, qualifiers preserved, two behaviours not merged into one
  generalisation, a planted contradiction flagged rather than resolved, a documented gap recorded
  rather than filled, and a deployment fact kept out of the general tier.
- **Detection automated, mutation gated** holds in practice: a sweep found seven planted decay modes
  and fixed none of them, including an empty routed leaf in plain sight.
- **Refusal discipline** holds: a distillation promoted two facts and refused six, including a
  single-session observation it declined to promote to product tier.

### 9.8 What is still not built

The **entire retrieval half**. There are no thin agents, no orchestrator, no routing check and no
answer-grounding eval. The golden set exists and has never been run against anything. **Nothing yet
proves an agent retrieves rather than answering from memory** — which is the one claim this whole
architecture rests on.

Also absent: `check-scope`, cross-library `[[slug]]` resolution, the slug→path manifest, external
`Source:` URL liveness checks, the Verifier, the Watcher, and the bootstrap command that would
provision a new machine. Of §13's six checks, three are built.

### 9.9 On sequence

The topology changed three times in one session — one repository, then three, then engine-plus-
libraries — each time driven by a finding rather than a preference. §6 says to settle the topology
at Phase 1 exit, before the pilot hardcodes paths against it. That was right in spirit and
unachievable in fact: **the topology could not be settled without building enough to discover what
was wrong with it.** The mitigation that actually worked was keeping every decision in an ADR, so
each change amended a recorded position rather than silently contradicting one.
