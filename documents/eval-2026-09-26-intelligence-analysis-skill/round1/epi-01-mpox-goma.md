## IA Review — Mpox Clade Ib Cluster — Goma District (memo, 14 March 2025)

**Reviewed at:** Full level — addressed to a Regional Health Director and driving an active resource/response decision (whether to expand the outbreak-response footprint) during a live mpox clade Ib cluster; consequential and externally read.
**Analytic line (bottom line as written):** "We therefore assess that sustained community transmission beyond the index market cluster is unlikely" — paired with the recommendation "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time."

### Strengths
- "Contact-tracing coverage stands at 68%. Of 337 identified contacts, 289 have been reached." — quantified, verifiable tracing data rather than a vague claim, partially satisfying ATS #1 (properly describes sources/data/methods).
- "We therefore assess that sustained community transmission beyond the index market cluster is unlikely" — uses "unlikely," a real term off the ICD 203 estimative-probability ladder (20–45%), rather than an undefined hedge like "probably" or "might" (ATS #2).
- "Maintain current surveillance posture. No expansion of the response footprint is warranted at this time." — a clear, actionable recommendation directly tied to the judgment, satisfying ATS #5 (customer relevance/implications).

### Weaknesses (most to least threatening to the conclusion)

1. **Single hypothesis resting on incomplete negative evidence** — ATS #4, "Incorporates analysis of alternatives"
   > "No secondary cases have been identified among reached contacts. We therefore assess that sustained community transmission beyond the index market cluster is unlikely."
   Why it matters: this judgment underwrites the entire recommendation, but only one hypothesis — containment — is ever tested against the evidence. Tracing covers 68% of identified contacts (289/337); the remaining 48 are exactly where undetected onward transmission would hide, and three weeks into the cluster is not long enough to be confident every traced contact has cleared mpox's full incubation window. Zero secondary cases among the *reached* fraction is not the same as zero secondary cases overall. This is the "Absence of evidence" bias named in the library's cognitive-bias catalog ("the missing piece isn't factored in") — the untraced 32% simply doesn't appear in the reasoning.
   Fix: run a light Analysis of Competing Hypotheses (or a Key Assumptions Check) against the two live hypotheses — "cluster contained" vs. "transmission ongoing but not yet detected" — and state what evidence would distinguish them (e.g., cases surfacing among the unreached 48 once traced, cases with no market linkage, secondary cases appearing after the incubation window closes). Until that check is run, the current absence of secondary cases should be reported as incomplete evidence, not as confirmation.

2. **Buried bottom line** — ATS #6, "Uses clear and logical argumentation"
   > Opens: "Over the past three weeks, 47 confirmed and 12 probable mpox clade Ib cases have been reported across Goma district..." — the judgment and recommendation don't appear until paragraph 2 and the closing line.
   Why it matters: a reader who stops after the first sentence has no idea what the Cell concluded or is recommending — the classic buried-BLUF failure, and the exact audience this rule protects (a director scanning a stack of situation reports).
   Fix: lead with the judgment and recommendation in the first 1–2 sentences — e.g., "We assess sustained transmission beyond the Nyiragongo market cluster is unlikely; no expansion of the response footprint is recommended" — then follow with the case counts and tracing data as supporting detail.

3. **Likelihood stated without a confidence level** — ATS #2, "Properly expresses and explains uncertainties"
   > "We therefore assess that sustained community transmission beyond the index market cluster is unlikely."
   Why it matters: "unlikely" is a calibrated ladder term, which is good, but likelihood and confidence are separate axes, and confidence (how good the evidence base is) is never stated. Given the judgment rests on only 68% tracing coverage and a cluster still young relative to the incubation window, a reader can't tell whether this is a well-corroborated call or a fragile one — and a bare assessment like this invites the reader to assume high confidence by default.
   Fix: state confidence separately and tie it to the evidence, e.g., "...unlikely; confidence is low-to-moderate, resting on 68% contact-tracing coverage to date and a cluster still inside its incubation window."

4. **Unquantified and uncharacterized sourcing** — ATS #1, "Properly describes quality and credibility of sources, data, and methods"
   > "Case interviews indicate a majority had contact with a market in Nyiragongo commune."
   Why it matters: "a majority" of the 59 cases is never given a number or percentage, and the interviews behind it aren't characterized (self-report? recall window? who conducted them?). The same gap applies to "laboratory sequencing confirms clade Ib" — it doesn't say how many of the 59 cases were actually sequenced versus assumed to match. These two claims — the market link and the outbreak-attribution — are exactly the facts the whole cluster narrative depends on, and both are carried on vague sourcing.
   Fix: give the actual count/percentage (e.g., "38 of 47 confirmed cases, 81%, reported market contact") and a one-line source descriptor for the interview data and the sequencing sample (how many specimens sequenced, timing relative to symptom onset).

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality/credibility of sources, data, methods | Fair | "68%... 289 have been reached" is quantified; "a majority had contact with a market" and sequencing extent are not |
| #2 Properly expresses and explains uncertainties | Fair | "unlikely" is a calibrated term, but no confidence level is ever stated |
| #3 Distinguishes information from assumption/judgment | Good | "We therefore assess" correctly signals judgment, kept separate from the reported case/tracing figures |
| #4 Incorporates analysis of alternatives | Poor | no competing explanation to "unlikely" is entertained despite 32% of contacts untraced |
| #5 Demonstrates customer relevance / implications | Good | "Maintain current surveillance posture. No expansion... warranted" directly answers the decision the director faces |
| #6 Uses clear and logical argumentation | Fair | judgment and recommendation arrive after a full paragraph of background case counts |
| #7 Explains change/consistency of analytic judgments | N/A | memo names no prior analytic product to compare against |
| #8 Makes accurate judgments warranted by evidence | Poor | "assess... unlikely" is not warranted to the confidence a bare assessment implies, given only 68% coverage and an early-stage cluster |
| #9 Incorporates effective visual information where appropriate | N/A | short-form memo; a table is not clearly warranted at this length |

### If I were the analyst, the one change I'd make first
Run the alternatives check on the core judgment (finding 1): explicitly weigh "contained" against "transmission ongoing but undetected," using the 32% of contacts never reached and the cluster's incubation-window status as the discriminating evidence — before recommending no change to the response footprint.

Sources: kb/intelligence-analysis/INDEX.md, kb/intelligence-analysis/icd-203-tradecraft-standards.md, kb/intelligence-analysis/analytic-writing-craft.md, kb/intelligence-analysis/structured-analytic-techniques.md, kb/intelligence-analysis/cognitive-biases-and-mitigations.md
