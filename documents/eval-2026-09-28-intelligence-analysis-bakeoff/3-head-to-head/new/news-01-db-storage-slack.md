## IA Review — prod DB storage Slack heads-up

**Reviewed at:** Light level — a few-sentence Slack post flagging an ops metric to a team channel; it's a quick heads-up, not a standalone analytic product.
**Analytic line (bottom line as written):** "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month."

### Strengths
- The causal explanation is kept separate from the observed data and explicitly hedged rather than asserted as fact — "prod DB storage hit 78% ... probably a spike from the weekend batch job" — satisfying Standard #3 (properly distinguishes underlying information from analysts' assumptions and judgments): the reported number and the guess about its cause are not blurred together.
- The main point is stated in the opening sentence with no throat-clearing, satisfying Standard #6 (uses clear and logical argumentation — a clear main message up front).
- The stated confidence matches the action requested: "probably" is offered alongside "flagging for @infra-team to investigate" rather than treated as settled — the author isn't overclaiming a conclusion they then act on as certain, consistent with Standard #8/#2 (judgment not overclaimed relative to its basis).

### Weaknesses
None. At Light level the only applicable check is whether the single load-bearing claim (the weekend-batch-job explanation) is stated with more certainty than its basis supports — it is hedged with "probably" and handed off as something to be verified, not asserted as fact. Missing sourcing, missing alternatives, and missing a formal bottom-line statement do not apply at this level and are not findings here.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #6 — clear and logical argumentation | Good | "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month." (lead sentence carries the point) |
| #3 — information vs. assumption vs. judgment | Good | "hit 78% ... probably a spike from the weekend batch job" (reported figure vs. hedged causal judgment kept distinct) |
| #8/#2 — accurate, not-overclaimed judgment / expressed uncertainty | Good | "probably a spike ... flagging for @infra-team to investigate" (hedge matches the investigate-don't-assume action taken) |

### If I were the analyst, the one change I'd make first
Nothing needs to change — this is sound for a quick note.

Sources: icd-203-tradecraft-standards.md
