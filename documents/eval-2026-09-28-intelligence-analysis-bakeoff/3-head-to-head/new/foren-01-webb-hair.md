## IA Review — CASE ASSESSMENT: State v. Marcus Webb

**Reviewed at:** Full level — a finished, standalone case assessment stating a numeric confidence (99.99%) and a recommendation to close leads and charge; a consequential, externally-actionable judgment, not a quick note or routine memo.
**Analytic line (bottom line as written):** "Recommendation: Close alternative suspect leads and proceed to charging." (the operative judgment — "identifies Webb as the most probable perpetrator" — appears in paragraph 2, not the opening)

### Strengths
- The lab's random-match statistic is attributed to a named, specific source rather than left as an unsourced number or a vague hedge — "The lab estimated the probability of a coincidental match from the general population at approximately 1 in 10,000" is a source's own verification, stated with a concrete figure. This partially satisfies ATS #1 (properly describing sources) for that one input, even though what is done with the number afterward is not sound.

### Weaknesses (most to least threatening to the conclusion)

1. **Transposed conditional probability (prosecutor's fallacy)** — Base-rate neglect, per the library's biases-in-estimating-probability table: "The prosecutor's fallacy is another [form of base-rate neglect]: P(match given innocent) is not P(innocent given match)."
   > "The lab estimated the probability of a coincidental match from the general population at approximately 1 in 10,000. ... the likelihood that the recovered hair belongs to Webb is approximately 99.99%."
   Why it matters: The 1-in-10,000 figure is the chance a random, innocent person would also match — it says nothing on its own about the chance Webb is guilty given the match. That depends on how many people could plausibly have left the hair (the relevant population/base rate), which the assessment never states. This single inversion is what manufactures the 99.99% figure that the entire recommendation rests on.
   Fix: State the base rate first, per the library's prescribed mitigation — estimate the size of the population who plausibly could have left the hair, then show that P(guilty | match) requires that figure, not just the lab's P(match | innocent). Until that population estimate is stated, the 99.99% claim cannot stand.

2. **No alternative explanation considered before recommending case closure** — ATS #4 (incorporates analysis of alternatives); the library's problem-to-technique table maps "only one explanation on the table" to Analysis of Competing Hypotheses.
   > "Recommendation: Close alternative suspect leads and proceed to charging."
   Why it matters: The assessment moves straight from one item of physical evidence to foreclosing every other suspect, without weighing competing explanations a match statistic is equally consistent with (secondary/innocent transfer, an unindicted relative or other individual within the relevant population, lab or sampling error). Because finding 1 shows the population size is unaddressed, this is exactly the situation where alternatives are most likely to survive scrutiny, not least.
   Fix: Run at least a light ACH pass (the library's abbreviated form for this level): enumerate the plausible alternative explanations, and check whether any piece of evidence here actually discriminates between them and Webb-as-perpetrator, or is equally consistent with both — prior convictions and an unaccounted-for alibi are consistent with many people, not diagnostic of this crime specifically.

3. **Buried bottom line** — ATS #6 (clear and logical argumentation), via the library's BLUF position rule and its named disguised case, "a report that opens with background numbers."
   > "A hair fiber recovered from the victim's apartment was submitted to the state crime lab. The forensic analyst reported a microscopically 'consistent match'..." (opens the document; the judgment and the recommendation do not appear until the final two lines)
   Why it matters: A reader stopping after the opening has no idea what the analyst concluded or is recommending; the structure reads as a chronology of lab steps before arriving at the actionable call, which is the standard disguised failure of this rule.
   Fix: Open with the judgment and recommendation in the first sentence — e.g., "We recommend proceeding to charging Webb, based on [contingent on fix #1] a hair match" — then follow with the supporting lab detail and priors as evidence, not as the lead.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality and credibility of sources | Fair | "The lab estimated the probability... at approximately 1 in 10,000" — named source, but no characterization of method reliability or examiner corroboration |
| #2 Properly expresses and explains uncertainties | Poor | "the likelihood that the recovered hair belongs to Webb is approximately 99.99%" — likelihood and confidence conflated, and derived from a transposed statistic |
| #3 Distinguishes information from assumption/judgment | Fair | "combined with Webb's prior convictions... and his inability to account for his whereabouts" — rolled into the identification with no signal of their lower diagnostic weight |
| #4 Incorporates analysis of alternatives | Poor | "Close alternative suspect leads" — no competing explanation named or weighed |
| #5 Demonstrates customer relevance | Good | The recommendation directly answers the decision-maker's actual question (what to do next), even though the answer is unsound |
| #6 Uses clear and logical argumentation | Poor | Bottom line arrives only in the closing line, after lab background; the statistical step from 1-in-10,000 to 99.99% does not follow |
| #7 Explains change to/consistency of analytic judgments | N/A | No prior analytic coverage referenced to compare against |
| #8 Makes accurate judgments and assessments | Poor | "approximately 99.99%" overclaims certainty the underlying statistic does not support |
| #9 Incorporates effective visual information | N/A | A two-paragraph case note of this kind does not need one; not a material gap |

### If I were the analyst, the one change I'd make first
Fix the transposed-probability error first: state the size of the population that could plausibly have left the hair, and recompute (or explicitly caveat) the probability of guilt from that base rate rather than quoting the lab's random-match statistic as if it already were that probability. Every other weakness here — the premature closure of alternatives, the buried recommendation — is easier to fix once the number driving the whole case isn't wrong.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md, structured-analytic-techniques.md
