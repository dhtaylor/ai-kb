## IA Review — Dengue Transmission Risk, Andean Region, Q3 2025 (WHO/PAHO Regional Surveillance Unit, 01 June 2025)

**Reviewed at:** Full level — the product is an epidemiological forecast prepared by a regional surveillance unit for health-ministry decision-makers: explicitly named in the "formal assessment, forecast, threat/risk analysis" list, so all nine ICD 203 standards apply, with #4 (alternatives) and #7 (change to prior judgments) explicitly evaluated.

**Analytic line (bottom line as written):** "Dengue transmission across Colombia, Peru, and Ecuador will likely remain above the 10-year seasonal median through August 2025 (assessed probability: ~60–70%), driven by residual DENV-3 serotype circulation and above-average precipitation in lowland endemic zones."

### Strengths
- **BLUF placed correctly and expressed in calibrated language.** The judgment leads the product in the first sentence, not buried after context, and "likely" is used with a numeric range (~60–70%) that matches the ICD 203 ladder's own "likely/probable" band (55–80%) rather than being left as an undefined hedge — satisfies Standard #6 (clear and logical argumentation) and the calibrated half of Standard #2.
- **Confidence kept as a separate axis from likelihood.** "Overall analytic confidence is moderate, reflecting El Niño–La Niña transition uncertainty" does not collapse into the probability statement — it states a distinct evidence-quality judgment, which is exactly what Standard #2 requires and a common point of failure elsewhere.
- **Standard #7 (change to analytic judgments) is handled explicitly, not left implicit.** "This updates and revises upward our March 2025 assessment (50–60%)... reflecting a confirmed serotype shift and April precipitation anomalies" names the prior coverage and the reason for the change, which is exactly the move Standard #7 asks for.

### Weaknesses (most to least threatening to the conclusion)

1. **Unsourced primary driver** — Standard #1 (properly describes quality and credibility of sources, data, and methods)
   > "driven by residual DENV-3 serotype circulation" ... "reflecting a confirmed serotype shift"
   Why it matters: the BASIS AND SOURCE RELIABILITY section characterizes exactly two inputs — PAHO/Ministry case reports and ECMWF precipitation forecasts — and gives each a reliability figure. The serotype-circulation claim is one of only two named drivers of the bottom line, and it is the specific reason given for revising the probability upward, yet no surveillance system, lab network, or reliability note is attached to it anywhere in the product. This is not a general "sourcing could be better" complaint — it is a single, identifiable factual assertion (DENV-3 is "confirmed" circulating) carrying real weight in the judgment with no source behind it at all.
   Fix: add a source descriptor for the serotype-surveillance data the same way the case reports and ECMWF data are treated — who confirmed the shift, over what sample/sites, and with what lag or coverage limitation — using the library's source-characterization dimensions (access, reliability history, corroboration, currency).

2. **Possible anchoring on the prior estimate** — cognitive bias: Anchoring (mitigation: re-estimate from scratch; treat the prior judgment as a suspect anchor rather than a starting point)
   > "This updates and revises upward our March 2025 assessment (50–60%), reflecting a confirmed serotype shift and April precipitation anomalies."
   Why it matters: the two cited reasons for the revision are not incremental — a *confirmed* serotype shift (epidemiologically significant, since a serotype's return after absence typically meets a population with little immunity to it) stacked on a *newly observed* precipitation anomaly. Against that, the estimate moved by exactly one band-width, from 50–60% to a directly adjacent 60–70%, with no overlap and no signal that the number was rebuilt from the new evidence rather than nudged off the old one. The library names this exact pattern as the tell-tale for anchoring in a revision — an update that moves only as far as the old estimate, not as far as the new evidence would independently support.
   Fix: show the re-estimate was built from scratch — state what probability the serotype shift and precipitation anomaly would each independently imply, and let the combined number fall out of that, rather than presenting only the delta from March.

3. **The alternative scenario doesn't contend with the forecast's own second driver** — Standard #4 (incorporates analysis of alternatives); the underlying gap is a hidden premise, so the fix is the Key Assumptions Check
   > "Transmission returns to seasonal baseline by July if La Niña onset occurs earlier than the ECMWF June median projection (~30% probability)."
   Why it matters: the bottom line names two co-equal drivers — serotype circulation and precipitation. The alternative scenario is built entirely on the precipitation driver reversing (early La Niña onset) and is silent on what happens to the serotype-circulation driver in that world. It implicitly assumes early rainfall relief is sufficient to return transmission to baseline even with DENV-3 still circulating — a load-bearing premise that is never stated or tested.
   Fix: run a Key Assumptions Check on the alternative scenario specifically — state the assumption that reduced precipitation dominates over residual serotype effects, and say what would falsify it (e.g., case counts staying elevated even after an early La Niña onset).

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality and credibility of sources, data, and methods | Fair | Case reports and ECMWF data are both characterized with a reliability figure; "residual DENV-3 serotype circulation" carries none |
| #2 Properly expresses and explains uncertainties | Good | "assessed probability: ~60–70%... Overall analytic confidence is moderate" — likelihood and confidence stated separately, both calibrated |
| #3 Distinguishes information from assumption and judgment | Good | "assessed probability" / "driven by" mark judgment; case-report and forecast data are kept as separately cited inputs |
| #4 Incorporates analysis of alternatives | Fair | One alternative is offered with a trigger and probability, but it addresses only the precipitation driver, not the serotype driver (Weakness 3) |
| #5 Demonstrates customer relevance and addresses implications | Good | "Health ministries should pre-position vector control supplies no later than mid-July... low-regret under either scenario" |
| #6 Uses clear and logical argumentation | Good | Bottom line is the first sentence, with reasoning following it, not preceding it |
| #7 Explains change to or consistency of analytic judgments | Good | "This updates and revises upward our March 2025 assessment (50–60%)... reflecting a confirmed serotype shift and April precipitation anomalies" — names the prior call and the reason (magnitude concern is scored under #8, not here) |
| #8 Makes accurate judgments and assessments | Fair | Revision magnitude may be anchored to the prior estimate rather than independently rebuilt from the newly cited evidence (Weakness 2) |
| #9 Incorporates effective visual information where appropriate | N/A | Short-form text forecast; no data set here calls for a graphic |

### If I were the analyst, the one change I'd make first
Attach a source descriptor to the DENV-3 serotype-shift claim — who confirmed it, from what surveillance sites, at what lag — the same way the case-report and ECMWF inputs are already characterized. It is one of only two named drivers of the entire forecast and the stated reason for revising the number upward, and right now it is the only material claim in the product with no evidentiary basis attached at all.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
