# ADR-0004: `scope:` as a first-class attribute, and what `check-scope` enforces

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Phase:** 1 (inventory, map & decide)

## Context and problem statement

[ADR-0003](0003-scoping-topology.md) establishes three homes. Homes alone do not keep facts in
the right one: a knowledge base that grows organically **mixes scopes silently** — a
vendor-general fact sitting beside a deployment-specific one in the same domain, indistinguishable
until someone tries to extract a shared tier and has to re-read everything.

The classification must therefore be recorded per fact, answered at capture, and machine-checkable.

## Decision drivers

- Misfiling must be **greppable**, not archaeological.
- The question must be answered **when the fact is written**, not retrofitted.
- A rule with no checker is a preference.

## Decision outcome

### 1. `scope:` is required frontmatter on every semantic and reference file

| Value | Means | Home |
|---|---|---|
| `repo:<project>` | True only of this deployment | project repository |
| `product:<vendor>` | True wherever that vendor's product appears | general |
| `org:<company>` | True across the organization | general |
| `general` | Domain fundamentals, engine/platform behavior | general |

Personal knowledge carries no `scope:` because it is never in either repository.

**Amended 2026-09-19.** The four values above are not separable by their descriptions alone. The
first live use of `create-domain` misclassified PostgreSQL MVCC as `general` when it is
`product:postgresql`, because "engine behavior" and "that vendor's product behavior" are the same
sentence for a single-vendor engine. The tie-break, now in the contract §1 and in the skill:

> *Would this fact stop being true if you swapped the vendor or product?* Yes → `product:<vendor>`.
> No → `general`.

This matters beyond tidiness: the two tiers carry different promotion guards, and a vendor fact
filed as `general` asserts about every product what was observed of one.

### 2. The classification test, asked at capture

> *Is this true only of this repo/deployment, or true wherever this product/tool/concept appears?*

This goes into the capture skills so it is answered every time. A fact whose answer is "both"
is two facts, and is split.

### 3. What `check-scope` must enforce

Specified now; **not yet built**. `check-kb` implements the third rule only.

| Rule | Why | Status |
|---|---|---|
| `scope:` present and a valid value | The attribute is useless if optional | to build |
| Scope agrees with the root the file sits in — a general-root file may not be `repo:*` | Catches a fact written into the wrong tier | to build |
| Slug uniqueness **within** a root; `INDEX.md` and `CONVENTIONS.md` exempt as path-addressed | Bare `[[slug]]` must resolve unambiguously | **built** (`check-kb`) |
| Slug uniqueness **across** roots | `[[general:slug]]` must resolve unambiguously | to build (Phase 3) |
| No `[[slug]]` targets a path-addressed file | Routers are reached by path; a link to one is a mistake | **built** (`check-kb`) |
| No relative traversal out of a root (`../../knowledge/`) | The nested layout of ADR-0003 makes this reachable and it would bypass the configured root | to build |
| Promotion to the general tier carries a CODEOWNER scope audit | The general tier is what every project depends on | to build (dormant, one owner) |

### 4. Promotion guards

A fact promoted from repo to general tier must satisfy both, per the contract §9:

- **Evidence external to the KB.** A vendor URL with excerpt, a direct system result, or a named
  human attestation with external citation. If the evidence is another KB file, the promotion is
  rejected — the KB may never be its own evidence for general-tier truth. One observation is not
  a general truth.
- **Atomic paired commit.** The general-tier add and the origin redirect stub land together, or
  the dual-root resolver finds both the promoted copy and the full pre-promotion copy in the gap
  and silently undoes the dedup.

Promotion is never automated.

## Consequences

**Good.** Scope backfill — which the architecture warns is real work on a grown KB — is trivial
here: six files, all `general`. Starting with the attribute enforced means the silent mixing
never happens rather than being cleaned up later. This is the cheapest this decision will ever be.

**Bad.** Most of `check-scope` does not exist, so most of the table above is currently honored by
discipline alone. The two rules that *are* built are the ones `check-kb` enforces on every commit;
the rest are a backlog, and the table says which is which rather than implying coverage.

**Neutral.** `scope:` is redundant with the file's location today, since one root means one
possible value. It earns its keep when the second root has content — and it must be present
before then, because retrofitting it is the thing this decision exists to avoid.

## Open items

- Build `check-scope` and wire it into the pre-commit hook and CI beside `check-kb`.
- Cross-root uniqueness needs the second root populated (Phase 3).
- The CODEOWNER scope audit is dormant until there is more than one owner ([ADR-0002](0002-governance-without-enforcement.md)).
