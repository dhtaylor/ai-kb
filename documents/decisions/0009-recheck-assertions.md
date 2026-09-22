# ADR-0009: Facts defend themselves with an assertion; the verifier reports and does not repair

- **Status:** Accepted
- **Date:** 2026-09-22
- **Deciders:** Dandy Taylor

## Context and problem statement

Every check built so far proves **structure** — frontmatter, links, scope, orphans, a well-formed
golden set. None asks whether a fact is still *true*. §7 has always required a re-check cadence and
"no evidence, no re-stamp", with nothing to run and nothing to record the evidence in, so `Verified:`
dates could only ever get older or be refreshed on somebody's word.

The Verifier was deferred as unbuildable because the plan imagined it querying live systems, and
there are none here. That framing hid the buildable part: a claim about a shell, a config file or
git is decidable by a command, and the honest answer for everything else is to say so rather than
imply verification nobody performed.

## Considered options

1. **An agent re-derives each fact from its source.** Flexible, expensive, and non-deterministic —
   the check that certifies freshness would itself be the least reproducible thing in the system.
2. **A registry of checks, keyed by fact.** Central, and instantly stale: the fact and its check
   drift apart because nothing in the diff that changes one shows the other.
3. **The assertion lives beside the fact it defends.** Reviewed in the same diff as the claim, moves
   with the library, and is trivially auditable — you read the command under the sentence.

## Decision outcome

**Chosen: option 3.** A section may carry `Recheck:` beneath its stamp — an **assertion**, not a
query: exit 0 means the fact still holds. `kb-verify` selects sections whose stamps are past the
domain horizon (a tenth of it for agent stamps), oldest first, capped by `verifier_budget`.

Three rules, and they are the whole design:

- **A pass restamps only with `--apply`.** Default is report-only. An assertion nobody re-reads,
  restamping on a schedule, is a freshness machine rather than a verifier.
- **A failure is never applied**, with or without `--apply`. The fact is not edited, not marked
  `CONFLICTED`, not deleted. A failure means the fact is stale, or the assertion is wrong, or the
  world changed and this is now a contradiction (§8) — three different repairs, and automating the
  choice destroys the evidence that a choice was needed.
- **Commands print, and run only with `--yes`.** A library is content that travels between people;
  running its assertions executes its author's shell as you. Cloning a repository for its facts is a
  different trust decision from executing it, so the second one is asked out loud.

**Most facts get no assertion, and the report names them.** "The Read tool does not expand
environment variables" cannot be settled by a shell. `kb-verify` lists every stale section without
an assertion as needing a human or an agent — a verifier that reported only what it could check
would read as though everything else had passed.

**An assertion must be able to fail.** Drafting these produced one that could not: the
interactive-vs-login shell check compared a login shell that never reads `~/.bashrc` anyway, so half
of it was vacuously true and it would have passed forever. It was caught by running the negative
control — breaking the world on purpose and requiring the assertion to notice. **Every assertion is
authored with its negative control run, or it is not an assertion.**

### Test evidence (2026-09-22)

| Test | Route | Result |
|---|---|---|
| A | Three real assertions, hermetic (each builds a temp `HOME`) | Pass on this machine |
| B | Negative control for each | Two failed as required; the third passed and was rewritten until it failed |
| C | Fixture: stale-pass, stale-fail, stale-no-assertion, fresh-with-assertion, budget 2 | Oldest two selected, fresh one skipped, unverifiable one named |
| D | `--yes` without `--apply` | PASS and FAIL reported, no file touched, exit 1 |
| E | `--yes --apply` | Only the passing section restamped, to today, `by: agent`; the failing section left at its old date; exit 1 |

## Consequences

- `Verified:` can now move forward on evidence rather than on assertion, for the narrow set of facts
  where that is meaningful — and the evidence is in the file, in the diff, reviewable.
- A human-verified fact restamped by `kb-verify` becomes `by: agent`, so its TTL drops to a tenth.
  Correct: a machine re-ran a command, a person did not re-examine the claim.
- The set of assertable facts is small and always will be. This does not make the knowledge base
  verified; it makes three facts verified and the rest honestly labelled.
- `kb-verify` is not in any commit hook. It runs commands, it is not instant, and a guardrail that
  executes repository content on every commit is a different risk from one that reads it.
