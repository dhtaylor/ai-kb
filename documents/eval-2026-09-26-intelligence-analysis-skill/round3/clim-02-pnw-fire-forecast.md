## IA Review — Pacific Northwest Wildfire Season Outlook

**Reviewed at:** Full level — its form is a formal forecast (BLUF, key judgments, confidence caveats), which the calibration table places at Full regardless of its short length; all nine ATS apply, with #4 and #7 explicitly evaluated (#7 is exempt here — this reads as a routine seasonal outlook with no prior analytic coverage cited to compare against).

**Analytic line (bottom line as written):** "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."

### Strengths
- **Bottom line stated first and clearly, not buried.** The BLUF is labeled and appears in sentence one, satisfying the position rule for Standard #6 ("Uses clear and logical argumentation") — a reader who stops after the first sentence still has the answer.
- **Honest, differentiated source characterization, including a self-imposed downgrade.** "University of Washington ensemble runs (research-grade, single institution — treat with commensurate caution; no independent corroboration cited here)" does exactly what Standard #1 asks: it states access/reliability and flags the corroboration gap on a source that materially drives the second judgment, rather than just citing it.
- **A genuine alternative scenario, weighted and reasoned, with a built-in reassessment trigger.** "An alternative scenario — a wet June–July pattern analogous to 2011 — would suppress fire activity regardless of snowpack deficit; we assign this scenario roughly 25% probability" satisfies Standard #4's analysis-of-alternatives requirement with a real competing outcome, not a token one, and "Reassess when June precipitation data are available" gives the reader an observable signpost rather than a static, unfalsifiable call.

### Weaknesses (most to least threatening to the conclusion)

1. **Uncited correlation statistic** — Standard #1, "Properly describes quality and credibility of sources, data, and methods"
   > "Snowpack deficit correlates with regional burned area at r ≈ 0.61 over 1990–2023"
   Why it matters: this is the quantitative link tying the forecast's lead driver (snowpack deficit) to the actual outcome being forecast (burned area) — it is the load-bearing statistic behind judgment 1. It carries the coefficient-plus-date-range costume of a hard finding, but unlike the SNOTEL figure ("NRCS SNOTEL network, observation-grade, 800+ sensor stations") and the NOAA/UW sourcing in judgment 2, it names no dataset, study, or issuing body that computed it. A reader cannot tell if this is a peer-reviewed climatological result or an unverified in-house regression.
   Fix: run a Quality-of-Information Check on this specific figure — name the dataset or study behind r ≈ 0.61 (e.g., the specific burned-area and SNOTEL series used and who computed the correlation), and give it the same one-line source descriptor the product already uses elsewhere. If no such source exists, say so and reflect that in the confidence statement.

2. **Confidence and likelihood conflated in the bottom line** — Standard #2, "Properly expresses and explains uncertainties" (likelihood and confidence are separate axes and must not be conflated)
   > "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."
   Why it matters: the 60–75% range is placed immediately after "confidence," which reads as quantifying confidence itself rather than the event's likelihood — the same category error the library's own worked example calls out ("we're confident it's likely" says nothing). Later probabilities in the product (25% for the wet scenario, <15% for the catastrophic scenario) suggest 60–75% is meant as likelihood, but the sentence as written doesn't say so, so the headline judgment is more ambiguous than the analysis behind it actually is.
   Fix: split the two clauses using the library's combined form: "We assess it is likely (60–75%) that the 2024 PNW wildfire season will exceed the 10-year average burned area; confidence is moderate, resting on strong observational snowpack data but a single, uncorroborated ensemble source for the ridge-persistence driver."

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality and credibility of sources, data, and methods | Fair | "r ≈ 0.61 over 1990–2023" — uncited, against otherwise strong sourcing elsewhere in the product |
| #2 Properly expresses and explains uncertainties | Fair | "moderate confidence (60–75%)" — likelihood and confidence not clearly separated |
| #3 Distinguishes information from assumption and judgment | Good | "We assess..." / "We do not assess..." consistently mark judgments; SNOTEL figures stand as plain reported data |
| #4 Incorporates analysis of alternatives | Good | "An alternative scenario — a wet June–July pattern analogous to 2011 — would suppress fire activity... roughly 25% probability" |
| #5 Demonstrates customer relevance and addresses implications | Fair | absent: no statement anywhere of what the assessed risk means operationally for the reader |
| #6 Uses clear and logical argumentation | Good | "BOTTOM LINE UP FRONT: We assess..." — leads with the judgment, not context |
| #7 Explains change to or consistency of analytic judgments | N/A | routine seasonal forecast; no prior analytic coverage cited to compare against |
| #8 Makes accurate judgments and assessments | Good | "research-grade, single institution — treat with commensurate caution; no independent corroboration cited here" — confidence downgraded to match evidence, not overclaimed |
| #9 Incorporates effective visual information where appropriate | N/A | a short probabilistic note; no graphic is clearly needed at this length |

### If I were the analyst, the one change I'd make first
Name the dataset or study behind the r ≈ 0.61 snowpack/burned-area correlation (or drop/hedge it if none exists) — it's the quantitative spine connecting the lead driver to the forecast outcome, and right now it's the one number in the product that isn't sourced the way everything else here is.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
