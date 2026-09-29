## IA Review — Slack heads-up: prod DB storage spike

**Reviewed at:** Light level — an informal Slack heads-up to a channel/team, not a decision document or externally-read product; stakes are "get eyes on it," not "commit to a cause."
**Analytic line (BLUF as written):** "heads up — prod DB storage hit 78% this morning, up from our usual ~60% for this time of month. probably a spike from the weekend batch job."

### Strengths
- **Bottom line up front, no burial.** The observation (78%, up from the usual ~60%) and the working hypothesis (weekend batch job) are both in the first sentence — satisfies Standard #6 (clear argumentation) at this level.
- **Fact and judgment are kept separate.** "hit 78%... up from our usual ~60%" is reported as observation; "probably a spike from the weekend batch job" is explicitly marked as inference via "probably," not asserted as established cause. This is exactly the distinction Standard #3 asks for, and it's easy to blur in a one-line message — this one doesn't.
- **Confidence matches the action requested.** The author doesn't overclaim the cause and close the loop — they hedge ("probably") and hand it to @infra-team "to investigate." Standard #2/#8: the certainty expressed is no higher than the evidence (a same-day number jump, no root-cause check yet) supports.

### Weaknesses
None. Running the one Light-level check — is the load-bearing claim ("probably a spike from the weekend batch job") asserted with more certainty than its basis supports? — the answer is no: it's hedged and routed to investigation rather than treated as settled. Standards like analysis-of-alternatives or full sourcing don't apply to a message at this level, so this comes in at zero findings.

### Scorecard (only applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #6 Clear argumentation | Good | Observation + hypothesis + ask all in sentence one |
| #3 Info vs. assumption/judgment | Good | "hit 78%..." (fact) vs. "probably a spike..." (hedged judgment) |
| #2/#8 Uncertainty not overclaimed | Good | "probably" + "investigate" — no premature conclusion |

### If I were the analyst, the one change I'd make first
Nothing required — this is sound for what it is. The only optional upgrade, and it's a freebie rather than a fix for a flaw: note whether 78% is a one-time reading or already trending across the morning, since that's the first thing @infra-team will ask and it costs one clause to pre-empt.
