## IA Review — THREAT ASSESSMENT: Eastside Organized Retail Crime Network

**Reviewed at:** Full level — the product self-presents as a formal threat assessment feeding a stand-down decision on deployed protective security resources; "threat/risk analysis" is named explicitly on the Full-level list, so stakes don't need to promote it — its own form already places it there.
**Analytic line (bottom line as written):** "The Eastside retail crime network has likely ceased operations following the August arrests."

### Strengths
- The bottom line is in the first sentence of the Executive Summary, not buried behind chronology or background — satisfies ATS #6's clear-argumentation/BLUF requirement on position, not just wording.
- The so-what for the decision-maker is explicit and actionable: "Protective security resources deployed to district retailers may be stood down" — satisfies ATS #5 (customer relevance/implications).
- The negative indicator tracked is specific and checkable rather than vague: "commercial burglaries matching the network's known signature methods — glass-cut entry, cargo-van staging" names the exact signature being monitored, which is good indicator design (in the spirit of the Indicators/Signposts technique) even though, as below, its interpretation overreaches.

### Weaknesses (most to least threatening to the conclusion)

1. **Uncharacterized, potentially motivated single source** — ATS #1, "Properly describes quality and credibility of sources, data, and methods"
   > "Confidential informant CI-7, an embedded member of the network, reported on 22 August that the primary organizer ('Ramos') fled the jurisdiction... CI-7 stated that remaining members were 'spooked' and had suspended activities indefinitely."
   Why it matters: The entire human-source case for "ceased operations" rests on one informant who is a member of the network being assessed, with no reliability history, no corroboration, and no consideration of bias/motivation or deception — despite this being exactly the circumstance (a network absorbing arrests) where a source close to the organizer has reason to feed a story that gets security relaxed.
   Fix: Run a Quality-of-Information Check on CI-7 specifically — access, reliability history, corroboration (is there any second source, or does everything trace back to CI-7 alone?), motivation, and deception potential — and add a one-line source descriptor per ICD 206 before this report is allowed to carry the conclusion. This also matches Pherson's "favoring first-hand information" intuitive trap: CI-7's embedded (firsthand) access is being credited as if firsthand access were the same thing as verified reliability.

2. **Absence of evidence treated as confirming, with no competing explanation considered** — ATS #4, "Incorporates analysis of alternatives"
   > "The six-week absence of signature incidents, combined with CI-7's reporting, confirms that the network is dormant and no longer poses an operational threat."
   Why it matters: A six-week gap in signature burglaries is exactly what you would also see under a "lying low pending less scrutiny" or "relocated to another district" hypothesis, or if the informant's account is itself a deliberate lull narrative. The product never states the alternative or asks whether the absence of incidents actually discriminates between "ceased" and "paused" — it treats non-diagnostic evidence as if it settled the question. This is the library's named "absence of evidence" bias: the missing piece (why the gap could exist under either hypothesis) isn't factored in.
   Fix: A light Analysis of Competing Hypotheses pass — step 1 (state the deception/lull hypothesis explicitly, not just "dormant") and step 5 (ask whether the six-week silence and CI-7's report actually discriminate between "ceased" and "paused/deceptive lull," or are equally consistent with both). Mitigation for the underlying bias: explicitly list what evidence would exist under each hypothesis and treat continued absence as data to keep testing, not as proof already in hand.

3. **A source's raw report is presented as a confirmed conclusion** — ATS #3, "Properly distinguishes underlying information from analysts' assumptions and judgments"
   > CI-7 "stated that remaining members were 'spooked' and had suspended activities indefinitely" becomes, two sentences later, "the network is dormant and no longer poses an operational threat."
   Why it matters: This is the library's specifically named failure mode for this standard — a source's raw statement is walked directly to a confirmed judgment with no visible reliability/evaluation step in between, and no signal phrase ("we assess," "we judge") marking where reported information ends and analytic conclusion begins. A reader cannot tell whether "dormant" is CI-7's characterization or the analyst's independent assessment.
   Fix: Insert the missing evaluative step: state what was reported (CI-7's account, dated and sourced), state the assumption it rests on (that CI-7's access and account are accurate and current), and only then state the judgment, marked with a signal phrase — e.g., "We assess the network is likely dormant, based on CI-7's account (unconfirmed by other sources) and the absence of matching incidents."

4. **Confidence is rounded up from "likely" to "confirms" with no stated confidence level** — ATS #2, "Properly expresses and explains uncertainties"
   > "has likely ceased operations" (Executive Summary) ... "confirms that the network is dormant" (Analysis)
   Why it matters: "Likely" (per the estimative-probability ladder, roughly 55–80%) and "confirms" are not the same claim, and the product silently moves from the first to the second without new evidence or any stated confidence level tied to the evidence base — which, given finding 1, is a single uncorroborated source. This is the library's "best-guess/uncertainty-drop" bias: treating a likely (not certain) input as if it were 100% true.
   Fix: Carry the original "likely" estimate through to the final judgment instead of upgrading it, and state confidence separately from likelihood — e.g., "We assess it is likely (~60–70%) that the network has ceased operations; confidence is low, resting on a single, uncorroborated informant report and a six-week absence of incidents that would also be consistent with a deliberate pause."

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| ATS #1 — source quality/credibility | Poor | "Confidential informant CI-7, an embedded member of the network, reported..." — no reliability, corroboration, or motive/deception characterization |
| ATS #2 — expresses uncertainty | Poor | "has likely ceased operations" vs. "confirms that the network is dormant" — no stated confidence level |
| ATS #3 — info vs. assumption vs. judgment | Poor | CI-7's "'spooked'... suspended activities" becomes "confirms... dormant" with no evaluative step shown |
| ATS #4 — analysis of alternatives | Poor | No competing hypothesis (lull, relocation, deception) stated anywhere in the product |
| ATS #5 — customer relevance/implications | Good | "Protective security resources deployed to district retailers may be stood down" |
| ATS #6 — clear/logical argumentation (BLUF position) | Good | Bottom line opens the Executive Summary's first sentence |
| ATS #7 — consistency with prior analytic judgments | Cannot fully assess | The product never states whether this revises a prior threat determination, though "protective security resources deployed" implies one existed; not enough is shown to rate this standard on its own evidence |
| ATS #8 — accurate, evidence-aligned judgments | Poor | Same anchor as #2/#3 — confidence in the final judgment exceeds what a single uncorroborated source and a short observation window support |
| ATS #9 — effective visual information | N/A | No data in this product would be better shown as a graphic or table |

### If I were the analyst, the one change I'd make first
Run a light Analysis of Competing Hypotheses pass that puts "the network has deliberately gone quiet to get security stood down, then will resume" on the table as an explicit second hypothesis alongside "the network has ceased operations," and ask whether CI-7's report and the six-week silence actually discriminate between the two. That single check forces the source-reliability gap, the alternative-explanation gap, and the overclaimed confidence to all get fixed together, because none of the current evidence survives being asked "does this distinguish ceased from paused?"

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
