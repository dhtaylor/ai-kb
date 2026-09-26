## IA Review — PNW Wildfire Season Outlook (FORECAST)

**Reviewed at:** Full level — its own header names it a "FORECAST," which the calibration ladder places at Full (forecasts, threat/risk products, anything consequential or externally read) regardless of its short length.
**Analytic line (bottom line as written):** "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."

### Strengths
- **BLUF density.** The judgment, its two named drivers, and a competing scenario with its own probability all land in the opening paragraph — no throat-clearing, no buried lede. This satisfies ATS #6 ("a clear main message up front, with transparent reasoning that actually supports it") about as tightly as a three-sentence lead can.
- **Source characterization on the ridge driver.** "University of Washington ensemble runs (research-grade, single institution — treat with commensurate caution; no independent corroboration cited here)" is a real source descriptor, not a bare citation — it flags access, corroboration, and reliability exactly as ATS #1 requires, and it does so about a source that supports the conclusion rather than only hedging the weak ones.
- **Alternatives with reasons, not just mentions.** The wet-2011 analog (25%) and the dismissal of a 2020-style catastrophic season (<15%, "requires specific ignition-timing and wind conditions not captured in seasonal outlooks") both name *why* the scenario is weighted as it is, satisfying ATS #4's requirement that a dismissed alternative carry a reason.

### Weaknesses (most to least threatening to the conclusion)

1. **Uncited correlation statistic carrying the primary driver** — Standard #1, "Properly describes quality and credibility of sources, data, and methods"
   > "Snowpack deficit correlates with regional burned area at r ≈ 0.61 over 1990–2023"
   Why it matters: this is the statistical bridge between the one directly-measured fact in the product (68% of April 1 median snowpack, sourced to NRCS SNOTEL) and the forecast's core causal claim (deficit → above-average burn). It carries a precise value and a specific 34-year window — the trappings of a real dataset — but names no study, agency, or burned-area dataset (e.g., NIFC/MTBS) behind it. A reader cannot tell whether this is a published regression or the analyst's own back-of-envelope figure, and the whole primary-driver argument leans on it.
   Fix: attach a source descriptor to the correlation the same way judgment 2 does for the ensemble runs — name the burned-area dataset and who ran the regression, or state plainly "author's calculation against [X]" with the method. Per analytic-writing-craft.md, a one-line source descriptor is exactly the construct for a key figure like this.

2. **Confidence and likelihood conflated in the bottom line** — Standard #2, "Properly expresses and explains uncertainties"
   > "We assess with moderate confidence (60–75%) that the 2024 Pacific Northwest wildfire season will exceed the 10-year average burned area."
   Why it matters: confidence (how good the evidence base is) and likelihood (how probable the outcome is) are a separate axis each, per the library's own worked pattern, and the parenthetical here sits directly against "confidence" — as written, a reader cannot tell whether 60–75% quantifies the *probability* the season exceeds average or is meant as a numeric gloss on "moderate" (which the library defines as a qualitative three-level bucket, not a percentage). This ambiguity sits in the single most load-bearing sentence in the product, even though the rest of the document (25%, <15% elsewhere) shows the author can use probability language correctly.
   Fix: split the two axes explicitly, following the library's combined form: "We assess it is likely (60–75%) that the season will exceed the 10-year average burned area; confidence is moderate, resting on [the SNOTEL-measured deficit and the single-institution ensemble noted above]." That both anchors the percentage to a ladder term ("likely" = 55–80%, which 60–75 sits inside) and ties "moderate confidence" to a named evidence basis instead of leaving it a free-floating adjective.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Source/data quality | Fair | Strong for the ridge driver ("research-grade, single institution — treat with commensurate caution"); uncited for the driver-linking statistic ("r ≈ 0.61 over 1990–2023") |
| #2 Expresses uncertainty | Fair | "moderate confidence (60–75%)" conflates the two axes in the BLUF, though "25%" and "less than 15%" elsewhere are used cleanly |
| #3 Information vs. assumption vs. judgment | Good | "We assess... We do not assess a catastrophic single-event season... as likely" — signal phrases mark judgment; measured snowpack figure is kept separate from it |
| #4 Analysis of alternatives | Good | wet-2011 analog and the 2020-style dismissal both carry a stated reason |
| #5 Customer relevance | Good | the BLUF directly answers the implicit planning question ("will this season exceed the 10-year average") that a seasonal outlook of this form exists to answer |
| #6 Clear argumentation / BLUF | Excellent | opening paragraph carries judgment, both drivers, and the competing scenario together |
| #7 Change/consistency with prior analysis | N/A | routine seasonal forecast, no prior analytic coverage cited to compare against |
| #8 Accurate, appropriately confident judgments | Good | "Seasonal fire forecast skill degrades substantially beyond six weeks. This assessment describes a probability distribution, not a point prediction." |
| #9 Effective visual information | Good | a short bulletin conveying three quantities in prose loses nothing a table or chart would add here |

### If I were the analyst, the one change I'd make first
Source the r ≈ 0.61 correlation. It is the only load-bearing number in the product with no traceable dataset or study behind it, and it is what turns a directly-measured fact (68% snowpack) into the forecast's central causal claim — right now that step is asserted, not shown.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md
