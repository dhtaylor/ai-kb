## IA Review: Pacific Northwest Wildfire Season Outlook (clim-02)

**Reviewed at:** Full level. It is a seasonal forecast built to be relied on, with numbered key judgments, stated probabilities and a confidence caveat. It is a standalone analytic product, not a message or memo.

**Analytic line (bottom line as written):** "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."

### Strengths
- **Main message first, with the alternative named.** The bottom line is the opening sentence and gives drivers and a competing scenario. This meets standard 6, "present a clear main analytic message up front", and standard 4, "identify and assess plausible alternative hypotheses". The product says "a wet June–July pattern analogous to 2011 — would suppress fire activity regardless of snowpack deficit; we assign this scenario roughly 25% probability". The 25% wet scenario also bounds the 60–75% figure on the upper side, so the two numbers are not inconsistent.
- **Sources characterized, including their limits.** The snowpack source is named and described: "NRCS SNOTEL network, observation-grade, 800+ sensor stations". The UW ensemble is flagged as "research-grade, single institution… no independent corroboration cited here". This meets standard 1. Under the Full-level already-addressed gate, the single-institution weakness is a strength, not a finding.
- **Uncertainty handled candidly.** "r ≈ 0.61… the relationship is not deterministic", "less than 15%", and "Seasonal fire forecast skill degrades substantially beyond six weeks… Reassess when June precipitation data are available" give a limit, a tail probability and a trigger for revisiting the call. This meets standard 2.

### Weaknesses (most to least threatening to the conclusion)
1. **Confidence and likelihood fused in one sentence, with no stated basis for the confidence** — Standard 2 (uncertainties explained), as the library states it under "Confidence is a separate axis, and never shares a sentence with likelihood".
   > "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."
   
   The library says a product using a "confidence level" "must not combine a confidence level and a degree of likelihood… in the same sentence." Here "moderate confidence" is attached to a probability range, so the number reads as the confidence level. The product also never explains why confidence is moderate. The library asks products to "explain the basis for the uncertainties… the likelihood… and the analyst's confidence in the basis for this judgment".
   
   Why it matters: the headline judgment is the one a reader will act on, and it cannot be read cleanly as likelihood versus confidence.
   
   Fix: split the axes and use one of ICD 203's term sets. The 60–75% range falls in the "likely" row (55–80%). For example: "It is likely (60–75%) that the 2024 burned area will exceed the 10-year average." Then, in a separate sentence: "Confidence in this judgment is moderate: it rests on one observation-grade snowpack series, a correlation of about 0.6, and a single-institution ridge projection with no independent corroboration." The numeric range alongside the term is fine; the products' other probabilities (25%, <15%) should be checked against the same row set.

2. **Two quantitative anchors have no identified source** — Standard 1 (identify underlying sources and methodologies).
   > "Snowpack deficit correlates with regional burned area at r ≈ 0.61 over 1990–2023"
   > "we assign this scenario roughly 25% probability based on current ensemble guidance"
   
   The correlation has a date range but names no study, dataset or issuing body for burned-area records. That is the costume-of-sourcing case: the SNOTEL attribution covers the snowpack reading, not the correlation or the burned-area series. "Current ensemble guidance" does not say whose ensemble, so the 25% cannot be checked. The "10-year average" baseline is also unsourced.
   
   Why it matters: the correlation is the main evidence tying snowpack to burned area, and the 25% is the only weighting of the alternative. Neither can be verified.
   
   Fix: name the burned-area dataset and the analysis behind r ≈ 0.61, and name the ensemble system (and its issuing institution) behind the 25%. If the 25% is the analyst's own judgment, say so and give the reasoning.

3. **Key judgments 1 and 2 are information, and the step from them to 60–75% is not shown** — Standard 3 (distinguish information from assumptions and judgments) and standard 6 (clear and logical argumentation).
   > "1. Cascades snowpack measured 68% of April 1 median…" / "2. Blocking ridge projections rest on NOAA operational seasonal outlooks…"
   
   Only item 3 is a judgment. Items 1 and 2 are reported data and source descriptions placed under "KEY JUDGMENTS". The product never says how the ridge projection is judged (a probability for the blocking ridge is absent). It also does not state the assumption that a historical snowpack–burned-area relationship carries into 2024. Standard 3 says to "state assumptions explicitly when they serve as the linchpin of an argument".
   
   Why it matters: the reader cannot trace how a roughly 0.6 correlation and an uncorroborated ridge projection become "60–75%".
   
   Fix: re-label items 1 and 2 as supporting information. Add judgments that follow from them, such as "We judge a persistent August ridge to be [term/range]". State the linchpin assumption and what follows for the judgment if it fails (for example, "if June–July precipitation is near normal, the probability falls to…").

### Scorecard
| Standard | Rating | Anchor |
|----------|--------|--------|
| 1. Describes quality and credibility of sources, data, methodologies | Fair | Strong on SNOTEL and UW; "r ≈ 0.61 over 1990–2023" and "current ensemble guidance" have no identified basis |
| 2. Expresses and explains uncertainties | Fair | Good caveats ("not deterministic", "skill degrades… beyond six weeks"), but "moderate confidence (60–75%)" fuses the two axes and the basis is not explained |
| 3. Distinguishes information from assumptions and judgments | Fair | "KEY JUDGMENTS" 1–2 are data and source notes; no explicit linchpin assumption |
| 4. Analysis of alternatives | Good | "wet June–July pattern analogous to 2011… roughly 25% probability" |
| 5. Customer relevance and implications | Fair | No stated customer or implications; this is a Full-level forecast, but the weakness does not threaten the conclusion, so it is not raised as a finding |
| 6. Clear and logical argumentation | Good | BLUF in the first sentence; the link from evidence to the 60–75% is thin (see weakness 3) |
| 7. Change or consistency of judgments | Fair | Product does not state whether it is initial coverage or consistent with an earlier outlook. Low impact, so no finding. |
| 8. Accurate judgments | Good | Commits to a direction and a tail probability ("less than 15%") rather than avoiding the call |
| 9. Visual information | Good | None present, and none is needed for a short outlook |

Overall read: this is a careful forecast. Its structure is sound, with a clear bottom line, a weighted alternative, sources graded by quality and honest limits stated. The weaknesses are in how the headline probability is worded and in unsourced numbers. They are fixable without changing the conclusion.

### If I were the analyst, the one change I'd make first
Rewrite the headline so likelihood and confidence sit in separate sentences, and add a one-line basis for the moderate confidence: "It is likely (60–75%) that… Confidence is moderate because…".

Sources: /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/INDEX.md, /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/icd-203-tradecraft-standards.md, /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/analytic-writing-craft.md

Library files read: /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/INDEX.md, /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/icd-203-tradecraft-standards.md, /mnt/c/workspaces/ws_v1/knowledge/kb/intelligence-analysis/analytic-writing-craft.md
