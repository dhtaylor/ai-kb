## IA Review — Project Atlas Board Update (Q2 2025)

**Reviewed at:** Medium level — this is a memo (its form names it directly: TO/FROM/RE board memo), and a memo stays Medium even when it drives a large funding decision; audience is the Board of Directors, stakes are a continued-investment decision.

**Analytic line (bottom line as written):** "Project Atlas, our enterprise workflow-automation module, is on track for a Q4 2025 General Availability launch. Beta feedback confirms the product is resonating strongly with target buyers, and we project Atlas will generate $8M in ARR within 12 months of GA."

### Strengths
- **Bottom line up front.** The main judgment (on track for GA, $8M ARR projection) appears in the first two sentences of the Executive Summary, not after throat-clearing background — satisfies the clear-argumentation standard (#6: "Uses clear and logical argumentation... clear main message (BLUF) up front").
- **Concrete, checkable figures for status.** "$2.1M spent against a $3.0M total authorization" and "Development is 82% complete" are falsifiable facts a board member can audit later, not vague reassurance — this is real information, not judgment dressed as information (Standard #3).
- **Flags at least one commitment as non-contractual.** Calling the three converters "verbally committed" (rather than silently folding them in as signed revenue) is a genuine, if incomplete, attempt to separate information from assumption (Standard #3) — see Weakness 2 for where that caveat isn't carried through.

### Weaknesses (most to least threatening to the conclusion)

1. **85% of the $8M ARR figure has no stated method or base rate** — Standard #1: Properly describes quality and credibility of sources, data, and methods
   > "The remaining $6.8M is expected from new logo acquisition through our standard outbound motion."
   Why it matters: The two components the memo does show its work on — $360K from verbal commits and $840K from a stated 50% close rate on 14 prospects — total only $1.2M. The other $6.8M, which is the majority of the headline number the whole recommendation leans on, cites no historical win rate, average deal size, sales capacity, or comparator period. This is base-rate neglect (cognitive-biases-and-mitigations.md, "Biases in estimating probability": "an effort/schedule estimate with no historical-velocity or comparator anchor is base-rate neglect" — the same failure applies to a revenue estimate with no historical-conversion anchor).
   Fix: Run a Quality-of-Information Check (structured-analytic-techniques.md) on this specific line: state the base rate the $6.8M is built from — last year's outbound win rate, average new-logo deal size, and outbound capacity/headcount for the period — the same way the $840K figure at least names its 50%-close-rate assumption.

2. **The recommendation states no downside anywhere** — Standard #4: Incorporates analysis of alternatives
   > "Approve continued development through GA. No course corrections are required at this time."
   Why it matters: This closing judgment is reached without naming a single thing that would make it wrong — not the chance a "verbal" commitment doesn't convert, not the risk that the final 18% of development (often the hardest stretch) slips past the compressed six-week buffer, not competitive risk. A recommendation this confident, with nothing that could flip it, is exactly what Standard #4 exists to catch at this level.
   Fix: Run a Premortem (structured-analytic-techniques.md) before this goes to the Board: assume it's Q1 2026 and Atlas fell short, and write the two-line postmortem now. The likely candidates — a verbal commit not converting, or a slip in the final development stretch — should each get one sentence in the memo naming what would change the "no course corrections" call.

3. **A stated caveat ("verbally committed") isn't carried into the number that uses it** — Standard #2: Properly expresses and explains uncertainties
   > "Three customers — Meridian Logistics, Apex Financial, and Northbrook Health — have verbally committed to conversion at GA... We have three committed beta converters (at our $120K average ACV = $360K)"
   Why it matters: The memo itself flags these as verbal, not signed — then the ARR math counts the full $360K as if it were booked. This is the best-guess/uncertainty-drop bias named in cognitive-biases-and-mitigations.md ("Treating a 75%-likely input as 100% true"): the uncertainty is named in prose and then dropped in the arithmetic.
   Fix: Attach a calibrated likelihood to the verbal commitments using the ICD 203 estimative-probability ladder (analytic-writing-craft.md) — e.g., "likely (55–80%) to convert, based on [stated basis]" — and discount the $360K accordingly rather than counting it at full value.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Source/data/method quality | Poor | "The remaining $6.8M is expected from new logo acquisition through our standard outbound motion" — no method or history given |
| #2 Expresses uncertainty | Poor | "we project Atlas will generate $8M in ARR" — stated as fact throughout; no calibrated term anywhere in the document |
| #3 Info vs. assumption vs. judgment | Fair | "verbally committed" correctly labeled as non-contractual, but "Beta feedback confirms the product is resonating strongly" turns a 4.2/5 satisfaction score into an assured market judgment with no "we assess" |
| #4 Analysis of alternatives | Poor | "No course corrections are required at this time" — no downside scenario anywhere in the product |
| #5 Customer relevance / implications | Good | Memo is addressed to the Board and closes with an explicit ask: "Approve continued development through GA" |
| #6 Clear argumentation / BLUF | Good | Bottom line stated in the first two sentences of the Executive Summary |
| #7 Consistency with prior analytic line | Good | "putting GA in early October — six weeks ahead of our Q4 milestone" explicitly reconciles against the previously communicated Q4 target |
| #8 Accurate, warranted judgments | Poor | The $8M ARR judgment is derived for only ~15% of its own claimed size ($1.2M of $8M shows any arithmetic); the rest is asserted |

Per the library's own note on why a single rolled-up score is unreliable (icd-203-tradecraft-standards.md): the pattern above is a memo that is well-structured and well-labeled at the surface (clear BLUF, one honest "verbal" caveat, hard numbers for status) but whose one truly load-bearing figure — the $8M ARR claim driving the funding ask — is mostly unsourced and stated with no calibrated uncertainty, and whose confident "no course corrections needed" close never engages a single alternative.

### If I were the analyst, the one change I'd make first
Put a real method behind the $6.8M new-logo figure — or, failing that, restate the whole $8M ARR line in calibrated terms ("likely (55–80%) to reach approximately $X–8M, confidence moderate, resting on 3 unconverted verbal commitments and an unvalidated 50% close rate") — since that single number is what the Board's approval decision actually rests on, and right now 85% of it is asserted rather than shown.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
