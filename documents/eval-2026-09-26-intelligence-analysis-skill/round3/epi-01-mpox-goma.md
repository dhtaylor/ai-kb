## IA Review — Mpox Clade Ib Cluster — Goma District (memo, 14 March 2025)

**Reviewed at:** Medium level — a memo to a decision-maker (Regional Health Director); form sets the level regardless of the outbreak's real-world stakes.
**Analytic line (bottom line as written):** "We therefore assess that sustained community transmission beyond the index market cluster is unlikely" — feeding the recommendation, "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time."

### Strengths
- Uses a calibrated estimative term rather than a vague hedge: "unlikely" is one of the seven ICD 203 ladder terms (20–45%), not an undefined word like "probably" — satisfies part of Standard #2 (Properly expresses and explains uncertainties).
- Marks the judgment as a judgment rather than presenting it as fact: "No secondary cases have been identified among reached contacts. We therefore assess…" — the signal phrase "we therefore assess" keeps the reported contact-tracing result separate from the analyst's conclusion, per Standard #3 (Properly distinguishes underlying information from analysts' assumptions and judgments).
- Answers the decision-maker's actual question with a concrete, actionable call — "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time" — satisfying Standard #5 (Demonstrates customer relevance and addresses implications) in substance, even though (see below) it is poorly positioned.

### Weaknesses (most to least threatening to the conclusion)

1. **Single hypothesis, no alternative examined** — Standard #4, Incorporates analysis of alternatives
   > "No secondary cases have been identified among reached contacts. We therefore assess that sustained community transmission beyond the index market cluster is unlikely."
   Why it matters: The entire recommendation rests on one data point — zero secondary cases among the 289 *traced* contacts — with no consideration of the live alternative that transmission is occurring outside that traced network: contact tracing by construction only follows people already linked to a known case, so it cannot surface an unlinked chain, an asymptomatic/unreported case, or spread among the roughly one-third of identified contacts not yet reached (see finding 3). Nothing in the memo weighs this possibility or explains why it's discounted.
   Fix: Run a light pass of Analysis of Competing Hypotheses (per the library's guidance for medium-level products: force step 1 — "is there a real alternative?" — and step 5 — "does any evidence actually discriminate, or is it all equally consistent with both?"). Put "no sustained community transmission" against "an unlinked/undetected chain is active" and ask whether the traced-contact result actually discriminates between them, given the tracing gap.

2. **Buried bottom line** — Standard #6, Uses clear and logical argumentation (BLUF)
   > Opens with: "Over the past three weeks, 47 confirmed and 12 probable mpox clade Ib cases have been reported across Goma district." The actual decision — "Recommendation: Maintain current surveillance posture. No expansion of the response footprint is warranted at this time." — appears only as the memo's final sentence.
   Why it matters: A reader who stops after the first sentence gets case counts, not the answer. This is the disguised case the library names directly — a report that opens with background numbers instead of the judgment — and it buries the one line the Regional Health Director actually needs first.
   Fix: Lead with the assessment and recommendation together: "We assess sustained community transmission beyond the index market cluster is unlikely and recommend maintaining the current surveillance posture without expanding the response." Follow with the supporting case, contact-tracing, and HCW data in order of importance, not chronology.

3. **Uncited internal inconsistency in the coverage figure** — Standard #1, Properly describes quality and credibility of sources, data, and methods
   > "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached."
   Why it matters: 289 of 337 is approximately 86%, not 68% — the two figures in the same sentence contradict each other, and the memo never reconciles them. This is the number that directly supports "no secondary cases have been identified," so a reader cannot tell how much of the contact pool was actually checked, which undercuts confidence in the central judgment either way the discrepancy resolves.
   Fix: Apply a Quality-of-Information Check to this figure specifically — state which number is correct, or, if 68% has a different (larger) denominator than the 337 "identified" contacts, say what that denominator is, before citing the coverage rate as support for the transmission judgment.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality and credibility of sources, data, and methods | Fair | "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached." — unreconciled internal contradiction |
| #2 Properly expresses and explains uncertainties | Fair | "…is unlikely" — calibrated term used, but no confidence level (evidence-base quality) stated separately |
| #3 Properly distinguishes information from assumptions and judgments | Good | "No secondary cases have been identified among reached contacts. We therefore assess…" |
| #4 Incorporates analysis of alternatives | Poor | Whole assessment paragraph — no competing explanation considered anywhere in the memo |
| #5 Demonstrates customer relevance and addresses implications | Good | "Recommendation: Maintain current surveillance posture. No expansion of the response footprint is warranted at this time." |
| #6 Uses clear and logical argumentation | Poor | Opens with case-count background; recommendation arrives only in the final sentence |
| #8 Makes accurate judgments and assessments | Fair | "…sustained community transmission beyond the index market cluster is unlikely" — plausible but not fully warranted given #1 and #4 |

Overall: this memo reaches a plausible operational call, but the case for it is thinner than its confident, well-worded final line suggests. The judgment leans on a single, internally inconsistent statistic and never tests the one alternative that would actually undercut "no expansion needed" — and the reader has to reach the last sentence to find out what's being recommended at all.

### If I were the analyst, the one change I'd make first
Before writing "unlikely," run the light Analysis of Competing Hypotheses in finding 1: name the alternative (an unlinked or undetected transmission chain outside the traced-contact network) and check whether the traced-contact result actually discriminates against it, given that roughly a third of identified contacts haven't been reached. If it survives that check, say so explicitly and lead the memo with it; if it doesn't fully survive, the recommendation needs a confidence caveat, not a flat "unlikely."

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md
