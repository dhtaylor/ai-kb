# ADR-0022: Evidence, not identity, sets a stamp's lease

- **Status:** Accepted
- **Date:** 2026-11-23
- **Deciders:** Dandy Taylor
- **Amends:** [0005](0005-currency-cadence.md) (supersedes §5 "Trust tiers on the stamp" and the
  `agent_ttl` amendment; TTLs, budgets and the automation gate stand)
- **Target:** v0.6.0 ([0016](0016-versioned-library-contract.md))

## Context and problem statement

ADR-0005 made a stamp's lease depend on who wrote it: an agent stamp stays fresh for a tenth of the
horizon, a human one for all of it. That ranks the evidence backwards. A `Recheck:` assertion is in the
file, replayable by anyone and reviewable in the diff that introduced it. A `by: human · method: manual`
stamp is someone's word. The weaker evidence got the longer lease.

The identity it rests on cannot be checked. Deriving `by:` from the committer proved unimplementable,
because an agent commits under the human's own git identity; `check-stamps` catches the accident, not the
determined author (CONVENTIONS §7). And published libraries ([0020](0020-published-libraries-and-consumers.md))
are read by consumers who do not know the author, to whom "a human checked this" means a stranger's word.

The data shows the cost. On 2026-11-23 the six registered libraries held 397 stamps, every one `by: agent`
and none `by: human`. 234 sat under a `Recheck:` assertion. All 397 ran on the short lease, so the facts
the engine could prove were the ones it kept asking a person to re-check.

## Considered options

- **A. The lease is set by the evidence behind the stamp; `by:` is recorded, not weighed** (chosen).
- **B. Keep identity tiers and enforce `by:` properly.** No mechanism tells agent from human under one git
  identity, and an enforced identity would still mean nothing to a consumer.
- **C. A four-rung evidence ladder** (integration-test, query, fragment-backed doc-review, manual), each with
  its own multiplier. Nothing yet justifies four numbers; every decision below only separates two cases.
- **D. An Arbiter-approval marker on each assertion** to stop an agent from earning the full lease with a
  toothless assertion. Unenforceable for the same reason `by:` is; it rebuilds the identity claim elsewhere.

## Decision outcome

1. **Two leases.** A stamp is **asserted** when a passing `Recheck:` backs it, attended or not and whatever
   its `method:`; it gets the full horizon. Every other stamp is **unasserted** (`manual`, `doc-review`
   without an assertion, or an assertion `kb-verify` flags) and gets the short lease, a tenth of the horizon
   by default. `by:` and `method:` stay on the stamp as a record for the reader and no longer feed the lease.
2. **Lint costs tier.** The assertion-quality findings `kb-verify` already reports (a fetched fragment of four
   words or fewer, one (url, fragment) pair backing several sections, a path outside the library) demote the stamp to
   unasserted, rather than only being reported. Defense against toothless assertions is mechanical and in the
   diff, not a signature. Parsing is not part of the lint: `check-kb` owns it, and an assertion that does not
   parse never passes, so it never earns the full horizon.
3. **The Arbiter reviews checks, not facts.** A person's work is writing and approving assertions, deciding
   failed checks and contradictions (§8), and owning attended decisions ([0017](0017-unattended-preparation-attended-decisions.md)).
   A person's stamp buys no longer lease than an agent's.
4. **High-blast-radius facts are gated by consequence.** Evidence rules apply to them as to any fact. Any
   change to one, and any restamp after a failed check, is an attended decision.
5. **`agent_ttl` becomes `unasserted_ttl`** at contract 2.7, which carries only that field; `agent_ttl` is
   still read at earlier versions and rejected from 2.7. The lease change itself applies to every library,
   whatever its declared contract.
6. **`check-stamps` is retired.** It stopped a false `by: human` from buying a tenfold lease; once `by:`
   buys nothing, there is nothing to stop.
7. **Retrieval states the tier.** `kb-retrieve` names the evidence behind each cited fact in plain words
   ("carries a check", "someone's word", "unstamped") and flags an unasserted one before the answer. It
   cannot run the lint, so it never says "asserted"; a lint demotion shows in the reports. It refuses on dispute only, never on tier.
8. **Assertion coverage is the headline health number.** The session-start nudge and weekly report lead with
   each library's share of sourced sections that are asserted; due rechecks become background work.
9. **No coverage gate on publishing.** A library whose facts cannot be decided by a command stays honestly
   unasserted. A gate would reward assertions that cannot fail, which §7 already calls worse than none.

## Consequences

- **No library file is rewritten.** The tier is derived; the 234 asserted stamps move to the full horizon on
  upgrade, with no contract bump, and the due-recheck queue shrinks accordingly.
- **The risk moves.** It was a false `by: human`; it is now a weak assertion that slips past lint. The lint
  set is the thing to strengthen when one is found.
- **Coverage becomes visible work.** intelligence-analysis (0 of 24 asserted) and claude-code-runtime
  (3 of 15) will lead the report until their facts are asserted or accepted as someone's word.
- **The two-lease split is a starting point.** Revisit option C if evidence shows asserted stamps differ
  materially by method.

## What changed at implementation (2026-11-23)

- **The lease change shipped without a contract bump.** This ADR proposed shipping it behind one.
  [§14](../../CONVENTIONS.md) versions the contract only when what a library must or may hold changes,
  and a stamp line holds what it always did; only the engine's reading of it changed. The lease applies
  to every library, whatever `kb_contract:` it declares.
- **Contract 2.7 carries only `unasserted_ttl:`** (decision 5).
- **A parse failure is not a lint finding.** The proposal listed one under decision 2. `kb-verify`'s lint
  has no parse kind: `check-kb` owns parsing, and an assertion that does not parse never passes.
- **"Passing" means no open failed-recheck record (2026-11-24, #264).** Decision 1 said a passing
  `Recheck:` makes a stamp asserted, but the lease only asked whether the lint flagged the assertion, so
  a check that had failed kept the full horizon and its place in assertion coverage. An open
  `stale-recheck` record in the library's `needs-attention.md` for the section's file and heading now
  demotes the stamp to unasserted, reported as the lint kind `failed-recheck`, for as long as the record
  was raised against the section's current stamp (its `stamp:` equals the stamp's content after
  `Verified:`). A newer stamp, such as a passing attended `kb-verify --apply`, makes the section asserted
  again at once, with the record still open as the Arbiter's decision; the engine closes no record. A record
  with no `stamp:` covers a stamp dated on or before its `date:`. A `stale-recheck-error` does not demote. `kbengine.lease` reads the queue itself, so
  `kb-verify`, the nudge, the weekly report and `--summary` follow from the one sweep, and `kb-retrieve`
  says the section's check last failed and flags the fact as someone's word, without refusing it. No
  contract version changes.
