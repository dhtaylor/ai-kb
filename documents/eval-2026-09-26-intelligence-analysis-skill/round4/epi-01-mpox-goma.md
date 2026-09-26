## IA Review — Mpox Clade Ib Cluster — Goma District (memo to Regional Health Director, 14 March 2025)

**Reviewed at:** Medium level — it is a memo addressed to a decision-maker (Regional Health Director); form places it at Medium regardless of the outbreak's stakes (a memo that drives a large decision is still a memo).
**Analytic line (bottom line as written):** "We therefore assess that sustained community transmission beyond the index market cluster is unlikely." (paired with the recommendation: "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time.")

### Strengths
- **Quantified underlying data.** "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached." — this is properly characterized information (Standard #1: describes quality/extent of the data, not just a bare claim).
- **Judgment marked and calibrated, not vague.** "We therefore assess that sustained community transmission … is unlikely" uses a signal phrase ("assess," Standard #3) and a term drawn from the actual estimative-probability ladder ("unlikely") rather than an undefined hedge like "probably" or "might" (Standard #2).

### Weaknesses (most to least threatening to the conclusion)

1. **Confidence not stated, and not aligned to the coverage gap** — Standard #2 (Properly expresses and explains uncertainties) and Standard #8 (Makes accurate judgments; confidence aligned to evidence quality, not overclaimed)
   > "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached. No secondary cases have been identified among reached contacts. We therefore assess that sustained community transmission beyond the index market cluster is unlikely."
   Why it matters: The "unlikely" call is built entirely on the 68% of contacts who *were* reached. The other 32% (48 contacts) are exactly where undetected secondary transmission would live, and their absence from the tally is never factored into how much weight the assessment can bear. This is a textbook case of the **Absence of evidence** bias (Heuer's evidence-evaluation catalog: "the missing piece isn't factored in"); the prescribed mitigation is to explicitly list what you'd expect to see if the hypothesis (contained cluster) were true and treat its absence as data, not silence.
   Fix: State a confidence level as a separate axis from the likelihood term, tied explicitly to the gap — e.g., "We assess sustained transmission beyond the market cluster is unlikely; confidence is moderate, resting on 289/337 (68%) of contacts traced with no secondary cases. The remaining 48 contacts should be closed out before this is treated as settled." A light Key Assumptions Check on the premise "the untraced 32% resembles the traced 68%" would surface this directly.

2. **The load-bearing exposure claim is the one figure left unquantified** — Standard #1 (Properly describes quality and credibility of sources, data, and methods)
   > "Case interviews indicate a majority had contact with a market in Nyiragongo commune."
   Why it matters: Every other figure in the memo is precisely counted (47, 12, 337, 289, 68%), but the claim that actually defines the outbreak's boundary — that this is an "index market cluster" at all — rests on the word "majority," with no case count, no denominator, and no note on how exposure was ascertained (self-report? recall window? corroborated across interviews?). Whatever minority of the 59 cases has no established market link is unaccounted for, and could represent transmission the market-focused contact tracing wouldn't catch.
   Fix: Quantify it ("38 of 59 cases (64%) reported market contact within the relevant exposure window") and characterize how it was collected. This is a Quality-of-Information Check applied to the single claim the conclusion depends on most.

3. **Buried bottom line** — Standard #6 (Uses clear and logical argumentation)
   > "Over the past three weeks, 47 confirmed and 12 probable mpox clade Ib cases have been reported across Goma district. Case interviews indicate a majority had contact with a market in Nyiragongo commune. Laboratory sequencing confirms clade Ib, consistent with the broader eastern DRC outbreak."
   Why it matters: This is the disguised case of a report opening with background numbers instead of the judgment. The reader gets case counts, an exposure claim, and a lab-confirmation detail before reaching the actual assessment in paragraph two — a reader who stops after the first sentence has no answer to the question the Director actually needs answered (is expansion warranted or not).
   Fix: Open with the assessment and recommendation in the first one or two sentences — "We assess mpox transmission in Goma district remains confined to the Nyiragongo market cluster (moderate confidence); no expansion of the response footprint is recommended at this time" — then follow with the case counts, contact-tracing detail, and lab confirmation as supporting evidence.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sourcing quality/credibility | Fair | "Case interviews indicate a majority had contact with a market" — unquantified, uncharacterized, unlike the contact-tracing figures |
| #2 Expresses uncertainty | Fair | "unlikely" is a real calibrated term, but no confidence level is given or tied to the 68% coverage |
| #3 Information vs. assumption vs. judgment | Good | "We therefore assess…" cleanly marks the judgment as distinct from the preceding reported figures |
| #4 Analysis of alternatives | Poor | No competing explanation considered for the untraced 32% or the cases without an established market link — a single hypothesis (contained cluster) stands unchallenged |
| #5 Customer relevance | Good | "Recommendation: Maintain current surveillance posture. No expansion…" directly answers the Director's actual decision |
| #6 Clear/logical argumentation (BLUF) | Poor | Opens with case counts and lab confirmation; the judgment doesn't arrive until paragraph two |
| #8 Accurate, warranted judgments | Fair | Plausible call, but confidence is not aligned to the stated evidence quality (68% coverage) |

Overall: the memo's individual data points are solid and precisely reported, but the connective tissue between the data and the "unlikely"/"no expansion" call is thin — the coverage gap and the unquantified exposure claim are both live enough to flip the recommendation, and neither is surfaced for the reader to weigh.

### If I were the analyst, the one change I'd make first
State an explicit confidence level for the "unlikely" assessment, tied by name to the 48 untraced contacts (32%) — that single addition tells the Regional Health Director exactly how much weight "no expansion warranted" can bear, and whether closing out those contacts should be prioritized before the posture is treated as settled.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md, structured-analytic-techniques.md
