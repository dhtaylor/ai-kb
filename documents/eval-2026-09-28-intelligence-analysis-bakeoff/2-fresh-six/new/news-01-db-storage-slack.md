## IA Review — news-01-db-storage-slack

**Reviewed at:** Light level — a short Slack heads-up to a channel/@infra-team, not a formal or externally-read product; per the library's product-level mapping, a chat message like this is scored only against standards #6, #3, and #8/#2, and standard #4 (analysis of alternatives) does not apply.

**Analytic line (bottom line as written):** "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month."

### Strengths
- The causal explanation is explicitly flagged as a judgment, not asserted as fact — "probably a spike from the weekend batch job." This satisfies Standard #3 (properly distinguishes underlying information from analysts' assumptions and judgments): the reported number (78%, vs. the ~60% baseline) is kept separate from the inferred cause.
- The bottom line leads the message with no throat-clearing or buried context — "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month" comes first, satisfying Standard #6 (clear and logical argumentation / BLUF up front).
- The hedge word "probably" is proportionate to the evidence offered (an observed spike coinciding with a known weekend batch job) rather than overclaimed as certain — meets the Light-level bar for Standards #8/#2 (judgment not overclaimed).

### Weaknesses (most to least threatening to the conclusion)
None. Running the Light-level check — is the single load-bearing claim (the batch-job explanation) stated with more certainty than its basis supports? — the answer is no: "probably" already calibrates it appropriately for a same-day flag. At Light level, a missing bottom line, missing alternatives, or missing sourcing are not findings; none of those checks apply here, and there is nothing else to raise.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #6 — Uses clear and logical argumentation (BLUF up front) | Good | "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month." |
| #3 — Distinguishes underlying information from assumptions/judgments | Good | "probably a spike from the weekend batch job" kept distinct from the reported 78%/~60% figures |
| #8/#2 — Accurate judgment, not overclaimed / uncertainty expressed | Good | "probably" — hedged, not stated as settled |

### If I were the analyst, the one change I'd make first
Nothing is required for a note at this level — it's sound for a quick note. If anything, naming the batch job explicitly (which one, or a job ID) would make the tip actionable a few seconds faster for @infra-team, but that's a nicety, not a fix to a gap.

Sources: icd-203-tradecraft-standards.md
