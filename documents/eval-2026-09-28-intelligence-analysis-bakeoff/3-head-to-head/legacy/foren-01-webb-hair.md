## IA Review — CASE ASSESSMENT: State v. Marcus Webb

**Reviewed at:** Full level — a criminal case assessment that recommends closing alternative suspect leads and proceeding to charging; consequential, externally read (investigators/prosecutors), liberty-affecting.

**Analytic line (BLUF as written):** "This evidence, combined with Webb's prior convictions for similar offenses and his inability to account for his whereabouts on the night in question, identifies Webb as the most probable perpetrator." (followed by: "Recommendation: Close alternative suspect leads and proceed to charging.")

### Strengths
- Gives a concrete, quantified match statistic ("approximately 1 in 10,000") rather than a vague hedge like "very likely" — the right instinct for Standard #2, even though what's done with the number afterward is the report's central problem.
- Transparent about its inputs: the assessment names the specific factors it is weighing (hair match, prior convictions, unaccounted-for whereabouts) rather than asserting the conclusion with no visible basis — a reader can at least see what is driving the judgment (Standard #3, partially).

### Weaknesses (most to least threatening to the conclusion)

1. **Prosecutor's fallacy** — Standard #8 (Makes accurate judgments and assessments)
   > "Given this match probability, the likelihood that the recovered hair belongs to Webb is approximately 99.99%."
   Why it matters: this inverts the statistic. The lab's 1-in-10,000 figure is P(microscopic match | hair is NOT Webb's) — the chance a random person's hair would also match. It is not P(hair is NOT Webb's | match), and the two are only equal by coincidence if the prior probability Webb is the source was already 50%. In a population where thousands of people could in principle match by chance, this single number cannot by itself yield "99.99%." The entire recommendation to charge rests on this one miscalculated figure.
   Fix: Recompute properly — state the match frequency as what it is (a source-attribution statistic, not a guilt probability), and combine it with an actual prior/base rate (e.g., size of the suspect pool with plausible access to the scene) via a likelihood-ratio framing: "the hair evidence increases the likelihood Webb is the source relative to a random member of the population by a factor of ~10,000, but does not by itself establish 99.99% probability of guilt." This is the single highest-leverage fix — see below.

2. **Buried BLUF** — Standard #6 (Clear and logical argumentation)
   > "Physical Evidence / A hair fiber recovered from the victim's apartment was submitted to the state crime lab..." (opens the memo) — the actual assessment and recommendation do not appear until the second and third sections.
   Why it matters: this is the "opens with raw evidence before the bottom-line assessment" pattern — a reader has to get through the lab-report paragraph before learning what the memo concludes. On a document that will route to a charging decision, the recommendation and its confidence should be stated in the first 1–2 sentences, evidence following as support.
   Fix: Lead with the assessment: "We assess Webb is [likely/probable — calibrated term] the source of the recovered hair and recommend [specific next step], based on the following evidence," then present the hair, priors, and alibi gap as support underneath.

3. **Method reliability uncharacterized** — Standard #1 (Properly describes quality and credibility of sources, data, and methods)
   > "The forensic analyst reported a microscopically 'consistent match'... The lab estimated the probability of a coincidental match from the general population at approximately 1 in 10,000."
   Why it matters: microscopic hair comparison is a subjective, examiner-dependent method with a documented history of overstated certainty in court testimony (it does not individualize the way DNA does), and the "1 in 10,000" figure's own derivation — what reference population, what validation study — is never given. Treating the match as a solid input to a near-certain probability without flagging the method's known limits or the statistic's provenance overstates the evidence's actual weight.
   Fix: Add a source/method-quality line: state the basis for the 1-in-10,000 estimate (reference population, validation study) and note that microscopic hair comparison, unlike DNA, cannot individualize to a single person — the "match" narrows a population, it does not identify.

4. **Premature closure — no alternative weighed** — Standard #4 (Incorporates analysis of alternatives)
   > "Recommendation: Close alternative suspect leads and proceed to charging."
   Why it matters: no competing explanation is considered or ruled out with evidence — not an alternate source for the hair (transfer, prior visit, cohabitant), not another individual within the population the 1-in-10,000 figure implies could also match. Prior convictions for similar offenses are propensity, not evidence tying Webb to this scene, and "inability to account for whereabouts" is common among innocent people too; both are used here to close the case rather than weighed against alternatives that would produce the same facts.
   Fix: Run a brief Analysis of Competing Hypotheses before recommending closure — list at least one genuine alternative (e.g., "hair transferred via an earlier, non-criminal visit") and state what evidence would discriminate between it and the leading hypothesis, before recommending alternative leads be closed.

### Scorecard (applicable standards — Full level)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Source/method quality | Poor | Hair-microscopy method and the 1-in-10,000 figure's derivation are never characterized. |
| #2 Expresses uncertainty | Poor | "approximately 99.99%" — false precision derived from a misapplied statistic. |
| #3 Info vs. assumption vs. judgment | Fair | Report structurally separates "Physical Evidence" from "Investigative Assessment," but the assessment restates the flawed 99.99% figure as though it were a factual derivation rather than a judgment. |
| #4 Analysis of alternatives | Poor | "Close alternative suspect leads" — no competing hypothesis considered. |
| #5 Customer relevance | Good | Gives investigators/prosecutors a direct, actionable recommendation on the actual decision before them (charge or not). |
| #6 Clear argumentation | Fair | BLUF appears in paragraph 2–3, after a full paragraph of raw evidence. |
| #7 Change/consistency of judgments | N/A | No prior analytic coverage to compare against — initial case assessment. |
| #8 Accurate judgments | Poor | "99.99%" — the prosecutor's fallacy; the central numeric judgment is not warranted by the evidence as presented. |
| #9 Effective visual information | N/A | Not needed at this length/complexity. |

### If I were the analyst, the one change I'd make first
Fix the probability claim itself: the 1-in-10,000 figure is a match-frequency statistic, not a probability of guilt, and treating it as the latter (99.99%) is the load-bearing error the rest of the memo — including the recommendation to close all other leads and charge — is built on. Restate it correctly (as a likelihood ratio against a stated population/prior) before any downstream recommendation is made.
