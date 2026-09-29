## IA Review — THREAT ASSESSMENT: Eastside Organized Retail Crime Network

**Reviewed at:** Full level — this is a named threat/risk analysis (a form the calibration table lists
directly under Full) with the actual structure of a standalone product built to be relied on: a stated
judgment, sourced reasoning, and an operational recommendation (standing down protective security
resources) that district retailers' security depends on.

**Analytic line (bottom line as written):** "The network no longer represents an active threat to
district retailers."

### Strengths
- The bottom line is in the opening sentence of the Executive Summary, not buried after
  background — satisfies the BLUF requirement behind Standard #6 (clear and logical argumentation):
  "The Eastside retail crime network has likely ceased operations following the August arrests."
- It states an implication tied to a concrete customer action rather than stopping at the finding,
  satisfying Standard #5 (customer relevance): "Protective security resources deployed to district
  retailers may be stood down."

### Weaknesses (most to least threatening to the conclusion)

1. **No competing hypothesis considered for the "absence of incidents"** — Standard #4, Incorporates
   analysis of alternatives
   > "The six-week absence of signature incidents, combined with CI-7's reporting, confirms that the
   network is dormant and no longer poses an operational threat."
   Why it matters: a six-week gap in signature-method burglaries is equally consistent with a network
   that has deliberately gone quiet to wait out heightened scrutiny after losing three members to
   arrest — a standard denial posture for organized crime, not just genuine dissolution. The product
   never puts that alternative on the table, so "confirms" is doing work the evidence can't support.
   This is also the named **absence-of-evidence bias** (cognitive-biases-and-mitigations.md: "the
   missing piece isn't factored in... treat its absence as data, especially re: deception") —
   naming the bias alone fixes nothing; the mitigation is a technique, not vigilance.
   Fix: run a light Analysis of Competing Hypotheses (structured-analytic-techniques.md) — enumerate
   "genuinely dormant" against "lying low pending reduced scrutiny," then ask whether the six-week
   silence actually discriminates between them. It doesn't: both hypotheses predict the same observed
   absence in the short term, so the absence carries zero diagnostic value as written.

2. **CI-7 is never characterized beyond access** — Standard #1, Properly describes quality and
   credibility of sources, data, and methods
   > "Confidential informant CI-7, an embedded member of the network, reported on 22 August that the
   primary organizer ('Ramos') fled the jurisdiction..."
   Why it matters: CI-7 is the sole human source behind the entire judgment, and the recommendation to
   stand down security rests on it. "Embedded member" states access only — reliability history,
   corroboration, and motive/bias are absent entirely (does CI-7 gain from the analyst believing the
   network has collapsed — e.g., self-preservation after the arrests?). The "no incidents" data point
   doesn't independently corroborate CI-7 specifically, since (per finding 1) it's consistent with more
   than one story.
   Fix: run a Quality-of-Information Check and add a source descriptor for CI-7 — reporting history,
   track record of accuracy, and any motive to overstate the network's collapse — plus a note on
   whether any second source corroborates the fled/suspended account.

3. **A raw report is presented as a settled conclusion** — Standard #3, Properly distinguishes
   underlying information from analysts' assumptions and judgments
   > "CI-7 stated that remaining members were 'spooked' and had suspended activities indefinitely."
   → carried forward as → "the network is dormant and no longer poses an operational threat."
   Why it matters: this is the specific structural defect the library calls out by name — a source's
   raw account becoming a confirmed conclusion with no visible evaluative step in between. A reader
   can't tell where CI-7's report ends and the analyst's judgment begins, or what assumption bridges
   them (e.g., that CI-7's account is current and accurate).
   Fix: mark the inferential step explicitly — "CI-7 reports members are spooked and activity has
   stopped (information). We judge this indicates suspended operations (judgment), assuming CI-7's
   account remains current (assumption, unverified)" — using signal phrases ("we assess/we judge") to
   flag the judgment as a judgment.

4. **Certainty escalates past what the evidence supports, with no confidence level stated** —
   Standard #2, Properly expresses and explains uncertainties
   > "has likely ceased operations" (Executive Summary) → "confirms that the network is dormant"
   (Analysis)
   Why it matters: the product opens with a calibrated hedge ("likely") and then abandons it for an
   unhedged certainty word ("confirms") in the very sentence that drives the stand-down recommendation,
   without ever stating confidence (in the evidence base) separately from likelihood, as Standard #2
   requires.
   Fix: use the ICD 203 estimative-probability ladder consistently and state confidence apart from
   likelihood: "We assess it is likely (55–80%) the network has ceased operations; confidence is low,
   resting on a single embedded source and an absence-based indicator that would look identical if the
   network were merely lying low."

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 — Source quality/credibility | Poor | "Confidential informant CI-7, an embedded member of the network" — access given, reliability/corroboration/motive never addressed |
| #2 — Expresses uncertainty | Fair | "likely" (hedged) collapses into "confirms" (unhedged), no confidence level stated |
| #3 — Info vs. assumption vs. judgment | Poor | CI-7's "spooked... suspended activities" becomes "the network is dormant" with no visible evaluative step |
| #4 — Analysis of alternatives | Poor | "confirms that the network is dormant" — no competing explanation for the incident-free window is named or ruled out |
| #5 — Customer relevance | Good | "Protective security resources... may be stood down" |
| #6 — Clear argumentation (BLUF) | Good | Bottom line in the opening sentence of the Executive Summary |
| #7 — Change/consistency vs. prior line | N/A | No prior analytic coverage is referenced; exempt as initial coverage |
| #8 — Accurate, non-overclaimed judgments | Poor | "confirms" claims more certainty than one uncorroborated source plus a non-diagnostic absence can support |
| #9 — Effective visual information | N/A | A two-paragraph text product; no omitted graphic is evident |

### If I were the analyst, the one change I'd make first
Run the light Analysis of Competing Hypotheses on the "dormant" call before anything else: put "lying
low pending reduced scrutiny" on the table next to "genuinely ceased," and check whether the six-week
incident gap actually discriminates between them. It doesn't on the evidence given — which means the
stand-down recommendation is currently resting on a single uncorroborated source's account, dressed up
as confirmation. Fixing that one gap forces the source-characterization and calibrated-language fixes
to follow naturally.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
