## IA Review — Congestion-Pricing Campaign Op-Ed

**Reviewed at:** Full level — an externally published opinion piece urging specific candidates how to campaign ahead of a November election; its form (a published op-ed aimed at the public) isn't named in the Light or Medium lists, so it falls to Full's "anything consequential or externally read" catch-all, and all nine ATS apply (standard #7 exempt — no prior analytic coverage is referenced; this is initial coverage).

**Analytic line (bottom line as written):** "Every council member who backed the plan should make it the centerpiece of their November campaign: constituents across the board want less traffic and are willing to pay for it." (the product's actual recommendation — but it is the final clause of the last sentence, not the opening one; see Weakness 3)

### Strengths
- The two factual claims are kept as distinct, specific, dated data points rather than blended into one vague assertion — "downtown commute times have fallen 11%" and "the mayor's approval rating has climbed 8 points" are each stated as a discrete figure over a named window ("three months," "the same window"). This satisfies the information half of ATS Standard #3 ("properly distinguishes underlying information from analysts' assumptions and judgments") — the reported numbers themselves are not what's blurred; it's the judgment drawn from them that overreaches (see Weakness 1).

### Weaknesses (most to least threatening to the conclusion)

1. **Illusory correlation presented as established causation** — ATS Standard #4 (incorporates analysis of alternatives) and #8 (judgments warranted by evidence)
   > "voters clearly reward bold infrastructure decisions"
   Why it matters: this clause is the load-bearing hinge of the whole piece — it's what turns two co-occurring metrics into a campaign strategy. No competing explanation for the approval-rating rise (economic conditions, an unrelated local event, normal quarter-to-quarter drift) is considered or ruled out anywhere in the product, and "clearly" asserts certainty the single data point can't support.
   Bias: this is **Illusory correlation** (cognitive-biases-and-mitigations.md: "seeing a relationship that isn't there from co-occurring cases"; prescribed mitigation: "check all four cells (present/absent x present/absent), not just the hits; correlation is not cause").
   Fix: Run a light Analysis of Competing Hypotheses (structured-analytic-techniques.md: "only one explanation on the table -> ACH, even a light pass" — force step 1, is there a real alternative, and step 5, does the evidence actually discriminate between them). Concretely: name at least one other plausible driver of the approval bump and say whether the approval data can distinguish it from the congestion-pricing effect — or admit it can't.

2. **Overgeneralization beyond what the evidence measures** — ATS Standard #8 (accurate judgments warranted by evidence)
   > "constituents across the board want less traffic and are willing to pay for it"
   Why it matters: an 8-point aggregate approval shift measures overall sentiment toward the mayor, not a specific, individually-held preference for paying a congestion charge, and "across the board" claims a uniform constituent view the piece has no polling to support. This unsupported claim is exactly what candidates are being told to run their campaigns on.
   Fix: Either cite polling that actually asks constituents about the tradeoff (support level, willingness to pay), or scale the claim back to what the data shows: correlated timing between the policy and an approval increase, not a measured mandate.

3. **Buried bottom line** — ATS Standard #6 (clear and logical argumentation)
   > "Three months after launch, downtown commute times have fallen 11% since the city's congestion-pricing zone took effect."
   Why it matters: this is the opening sentence, and it's background data, not the judgment — a disguised buried-BLUF case the library names directly ("a report that opens with background numbers"). The actual recommendation ("council members... should make it the centerpiece...") doesn't appear until the final clause of the last sentence. A reader who stops after sentence one has a statistic, not the argument.
   Fix: Open with the recommendation, then support it: "Council members who backed congestion pricing should campaign on it — three months in, commute times are down 11% and mayoral approval is up 8 points in the same window."

4. **Unsourced statistics** — ATS Standard #1 (properly describes quality and credibility of sources, data, and methods)
   > "downtown commute times have fallen 11%" ... "the mayor's approval rating has climbed 8 points"
   Why it matters: neither figure names a publication, dataset, or polling organization — no city transportation report, no named poll with sample size or dates. These two uncharacterized numbers are the entire evidentiary base for a campaign recommendation.
   Fix: Attach a source descriptor to each: name the transportation dataset/report behind the 11% figure and the pollster (with sample size and field dates) behind the 8-point figure, so a reader can judge reliability and corroboration.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sourcing/data quality | Poor | "commute times have fallen 11%... approval rating has climbed 8 points" — neither figure is attributed to a source |
| #2 Properly expresses uncertainty | Poor | "voters clearly reward bold infrastructure decisions" — a causal inference stated with total certainty, no calibrated language, no alternative flagged |
| #3 Info vs. assumption vs. judgment | Fair | the two data points are kept clean as information (strength, above), but the judgment "voters clearly reward..." is asserted with the same flat certainty as the facts before it, with no signal phrase separating it out |
| #4 Analysis of alternatives | Poor | no competing explanation for the approval-rating shift appears anywhere in the product |
| #5 Customer relevance / implications | Good | the piece does answer "so what" for its audience directly: "make it the centerpiece of their November campaign" |
| #6 Clear and logical argumentation | Poor | opens with background data ("Three months after launch, downtown commute times have fallen 11%...") before the recommendation, which arrives only in the final clause |
| #7 Consistency with prior analysis | N/A | initial coverage — no prior analytic position is referenced or compared against |
| #8 Accurate, evidence-warranted judgments | Poor | "constituents across the board want less traffic and are willing to pay for it" — claims a uniform preference the cited metrics don't measure |
| #9 Effective visual information | N/A | a three-sentence opinion paragraph; no graphic would materially aid comprehension here |

### If I were the analyst, the one change I'd make first
Fix the causal claim first (Weakness 1): before telling anyone to campaign on it, name at least one alternative explanation for the approval-rating rise and check whether the evidence actually discriminates between it and the congestion-pricing effect. Everything else in the piece — the campaign recommendation, the "constituents across the board" claim, even the buried-lede structure — is downstream of that one unexamined causal leap.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
