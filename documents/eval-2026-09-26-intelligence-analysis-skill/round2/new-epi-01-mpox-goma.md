## IA Review — Mpox Clade Ib Cluster — Goma District (memo, Epidemiological Analysis Cell to Regional Health Director, 14 March 2025)

**Reviewed at:** Medium level — a memo addressed to a named decision-maker, routine operational reporting rather than a formal assessment, forecast, or strategy document.

**Analytic line (bottom line as written):** "We therefore assess that sustained community transmission beyond the index market cluster is unlikely." — paired with the operational recommendation, "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time."

### Strengths
- Uses the ICD 203 calibrated estimative-probability ladder correctly rather than a vague hedge — "unlikely" (20–45% on the ladder) is a defined term, not an ambiguous word like "probably" or "might" that different readers would map differently (Standard #2, *icd-203-tradecraft-standards.md* / *analytic-writing-craft.md*).
- Marks the judgment with a clear signal phrase distinct from the preceding data — "We therefore assess..." — so the reader can tell where reported figures end and the analyst's conclusion begins (Standard #3, Properly distinguishes underlying information from analysts' assumptions and judgments).
- Directly answers the decision-maker's actual question with an actionable recommendation rather than leaving the so-what implicit (Standard #5, Demonstrates customer relevance and addresses implications — applies here because the product is addressed to a named decision-maker).

### Weaknesses (most to least threatening to the conclusion)

1. **Contact-tracing gap not factored into the "unlikely" judgment** — Standard #1, Properly describes quality and credibility of sources, data, and methods, and Standard #2, Properly expresses and explains uncertainties (confidence stated separately from likelihood) — both *icd-203-tradecraft-standards.md*. Bias: **Absence of evidence** — "the missing piece isn't factored in" (*cognitive-biases-and-mitigations.md*).
   > "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached. No secondary cases have been identified among reached contacts. We therefore assess that sustained community transmission beyond the index market cluster is unlikely."
   Why it matters: 48 of 337 contacts (32%) have unknown status. "No secondary cases among reached contacts" is being read as though it clears the whole contact universe, when a third of it was never checked — the containment call rests only on the two-thirds that were traced. No confidence level is stated either, so the reader can't tell whether "unlikely" rests on strong or thin evidence.
   Fix: Run a Quality-of-Information Check on the contact-tracing dataset and state likelihood and confidence as separate axes, per the library's combined form: "We assess sustained transmission beyond the market cluster is unlikely; confidence is moderate, resting on 289 of 337 contacts (68%) traced with no secondary cases — the remaining 48 contacts are of unknown status and are the main threat to this call."

2. **Single hypothesis — the non-market-linked cases are never explained** — Standard #4, Incorporates analysis of alternatives (*icd-203-tradecraft-standards.md*). Technique: "Only one explanation on the table -> Analysis of Competing Hypotheses (even a light pass)" (*structured-analytic-techniques.md*, echoed in the *cognitive-biases-and-mitigations.md* master mapping).
   > "Case interviews indicate a majority had contact with a market in Nyiragongo commune."
   Why it matters: "a majority" concedes that some confirmed/probable cases had no identified market contact. The memo advances only the market-cluster hypothesis and never addresses how the remaining cases were infected or whether they mark a second, unrecognized chain — which is exactly what "sustained community transmission... is unlikely" is supposed to rule out.
   Fix: Run a light ACH pass — name the competing hypothesis explicitly (an undetected parallel chain among the non-market-linked cases) and check whether anything actually discriminates between it and the market-cluster hypothesis, e.g. genomic sequence clustering or spatial/temporal linkage of the non-market cases to the traced network.

3. **Buried bottom line** — Standard #6, Uses clear and logical argumentation (BLUF), *icd-203-tradecraft-standards.md*; position rule in *analytic-writing-craft.md*, which names "a report that opens with background numbers" as a disguised buried-BLUF case.
   > Opens with: "Over the past three weeks, 47 confirmed and 12 probable mpox clade Ib cases have been reported across Goma district." — background case counts and lab confirmation precede either the assessment or the recommendation.
   Why it matters: the decision-relevant line — "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time." — arrives only in the final sentence, after case counts, lab results, contact-tracing figures, and health-worker-risk commentary. A reader who stops early gets data, not the answer.
   Fix: Open with the recommendation and its confidence — e.g. "We assess sustained transmission beyond the Nyiragongo market cluster is unlikely (moderate confidence); recommend maintaining current surveillance posture with no footprint expansion" — then follow with the supporting case and contact-tracing detail.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality/credibility of sources, data, methods | Fair | "Of 337 identified contacts, 289 have been reached" — completeness of the traced base not characterized |
| #2 Properly expresses and explains uncertainties | Fair | "unlikely" is a correctly-used ladder term, but no confidence level is stated anywhere |
| #3 Distinguishes information from assumption/judgment | Good | "We therefore assess that sustained community transmission... is unlikely" clearly signals judgment |
| #4 Incorporates analysis of alternatives | Poor | "a majority had contact with a market" — the minority's transmission route is never addressed |
| #5 Demonstrates customer relevance / addresses implications | Good | "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time." |
| #6 Uses clear and logical argumentation | Fair | Opens with case counts, not with the judgment or recommendation |
| #8 Makes accurate judgments, confidence aligned to evidence | Fair | "unlikely" claim not qualified against the 32% of contacts not yet reached |

### If I were the analyst, the one change I'd make first
State confidence separately from likelihood and caveat the untraced 32% of contacts before committing to "unlikely" — that single figure is what the entire no-expansion recommendation leans on, and right now it's presented as fully resolved when it isn't.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
