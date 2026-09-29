## IA Review — CASE ASSESSMENT: State v. Marcus Webb

**Reviewed at:** Full level — a formal case assessment recommending closure of alternative leads and a charging decision; consequential, externally read (prosecution), so all nine ICD 203 standards apply.
**Analytic line (bottom line as written):** "This evidence, combined with Webb's prior convictions for similar offenses and his inability to account for his whereabouts on the night in question, identifies Webb as the most probable perpetrator" — followed by "Recommendation: Close alternative suspect leads and proceed to charging."

### Strengths
- Names an identifiable, institutional source rather than an anonymous claim: "A hair fiber recovered from the victim's apartment was submitted to the state crime lab. The forensic analyst reported a microscopically 'consistent match'" — partially satisfies Standard #1 (source is named and the method is stated, even though reliability/corroboration is not further characterized — see Weakness 1).
- States a concrete, decision-relevant implication rather than leaving the reader to infer one: "Investigative resources should now shift to building the prosecutorial case" — satisfies Standard #5 (addresses the decision-maker's actual next move).

### Weaknesses (most to least threatening to the conclusion)

1. **Base-rate neglect (prosecutor's fallacy) in the headline probability** — Standard #8, Makes accurate judgments and assessments ("are the judgments precise, warranted by the evidence, and is confidence aligned to evidence quality — not overclaimed"); also Standard #2, Properly expresses and explains uncertainties.
   > "The lab estimated the probability of a coincidental match from the general population at approximately 1 in 10,000... Given this match probability, the likelihood that the recovered hair belongs to Webb is approximately 99.99%."
   Why it matters: this is the load-bearing number for the entire recommendation, and it commits exactly the error the library names: "the prosecutor's fallacy... P(match given innocent) is not P(innocent given match)" (cognitive-biases-and-mitigations.md, base-rate neglect row). A 1-in-10,000 coincidental-match rate does not by itself yield 99.99% probability of identity — that conversion also requires the size of the pool of people who could plausibly be the source (family members, local population, anyone with innocent access to the apartment). Without that base rate, the true posterior could be far lower than stated, and the whole case-closing recommendation rests on this inflated figure.
   Fix: Per the library's prescribed mitigation, "state the base rate explicitly; use it as the starting point before case-specific evidence" (master mapping: "Ignored base rate -> state the base rate first"). Concretely: state how many people in the relevant population (city, region, or family line) would be expected to coincidentally match at a 1-in-10,000 rate, and derive the posterior probability from that base rate combined with the match evidence — rather than treating the match-rate denominator as if it were already the answer.

2. **No analysis of alternatives before recommending their closure** — Standard #4, Incorporates analysis of alternatives ("are plausible competing explanations considered and, where dismissed, is the reason given?").
   > "Recommendation: Close alternative suspect leads and proceed to charging."
   Why it matters: no competing explanation is named or weighed anywhere in the product — not an innocent-transfer explanation for the hair, not another suspect, not the possibility the 1-in-10,000 rate leaves room for a different match in the relevant population. At Full level, ATS #4 requires that alternatives be considered and, if dismissed, that the reason be given; here they are dismissed with no reasoning at all. This is the library's "locked onto a favored answer" pattern — "only one explanation on the table."
   Fix: Run at least a Light ACH pass (structured-analytic-techniques.md): step 1, ask whether a real alternative exists (an innocent source of the hair, a different perpetrator) and put it on the table even without full evidentiary support yet; step 5, ask whether the hair evidence, the prior convictions, and the whereabouts gap actually discriminate between Webb and any remaining alternative, or whether they are equally consistent with more than one explanation. Only after that pass has evidence to show should alternative leads be closed.

3. **Buried bottom line** — Standard #6, Uses clear and logical argumentation ("is there a clear main message (BLUF) up front?").
   > The product opens with a "Physical Evidence" section describing the hair fiber and match statistic, and only reaches the judgment ("identifies Webb as the most probable perpetrator") in the following "Investigative Assessment" section.
   Why it matters: this is the disguised buried-BLUF case the library names directly — "a report that opens with background numbers" instead of leading with the judgment (analytic-writing-craft.md). A reader who stops after the first section has evidence but no conclusion. It is ranked last here only because it is a presentation defect, not a defect in the reasoning itself — unlike Weaknesses 1 and 2, fixing it alone would not change whether the conclusion is warranted.
   Fix: Open with the bottom line and the recommendation in the first sentence or two — e.g., "We assess Webb is [calibrated term] the source of the recovered hair and recommend proceeding toward charging, pending resolution of the base-rate and alternative-suspect issues below" — then present the physical evidence as supporting detail, not as the lead.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Source/method quality and credibility | Fair | "was submitted to the state crime lab. The forensic analyst reported a microscopically 'consistent match'" — source and method named, but reliability history and corroboration of the hair match are not addressed |
| #2 Properly expresses uncertainty | Poor | "the likelihood that the recovered hair belongs to Webb is approximately 99.99%" — a precise figure produced by an uncorrected statistical error, not calibrated language |
| #3 Information vs. assumption vs. judgment | Fair | "Given this match probability, the likelihood... is approximately 99.99%" is written as though it follows directly from the lab's reported statistic, rather than flagged as the analyst's own (flawed) inference |
| #4 Analysis of alternatives | Poor | "Close alternative suspect leads and proceed to charging" — no competing explanation is named or weighed anywhere in the product |
| #5 Customer relevance / implications | Good | "Investigative resources should now shift to building the prosecutorial case" — a clear, actionable next step for the decision-maker |
| #6 Clear and logical argumentation | Fair | Judgment exists and is clearly worded once reached, but arrives after the "Physical Evidence" section rather than up front |
| #7 Change/consistency with prior analysis | N/A | Nothing in the product indicates this revises or confirms a prior assessment; treated as initial coverage |
| #8 Accurate judgments and assessments | Poor | "approximately 99.99%" — the central quantitative judgment is a documented statistical fallacy (base-rate neglect / prosecutor's fallacy), so confidence is not warranted by the evidence as presented |
| #9 Effective visual information | N/A | A memo this short carries no data that a graphic would clarify |

### Overall read
No single rolled-up score is given, because the library holds that a rolled-up number across all nine standards is a false-precision aggregate — single-rater grading against this rubric is reliable in aggregate across raters, not from one reviewer (icd-203-tradecraft-standards.md). In prose: the product's real weakness is not tone or structure but substance — its headline certainty figure is derived by a named statistical fallacy, and the recommendation to close every other lead is not supported by any comparison against an alternative. Both defects go directly to whether the conclusion is warranted, which is why they outrank the presentational BLUF issue.

### If I were the analyst, the one change I'd make first
Recompute (or explicitly caveat) the 99.99% figure using the actual reference-population base rate before it drives any recommendation — the base rate, not the match-rate denominator alone, is what the charging decision should rest on.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md, structured-analytic-techniques.md
