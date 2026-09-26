## IA Review — @portfolio-risk Slack message (Fed / rotation call)

**Reviewed at:** Light level — a chat message to a risk-desk channel, not a memo or formal assessment. Standard #4 (analysis of alternatives) and any missing-bottom-line/missing-sourcing check do not apply at this level; the review is limited to the one calibrated-certainty check Light warrants.

**Analytic line (bottom line as written):** "Tech multiples will compress and small-caps will underperform large-caps through year-end." (with the resulting action: "Rotating: +5% TLT, −10% QQQ.")

### Strengths
- The call is concrete and falsifiable rather than a vague hand-wave: a stated trigger (Powell's remarks), a stated market judgment, and a specific, sized action (+5% TLT, −10% QQQ) that follows visibly from the judgment — this satisfies Standard #6 ("Uses clear and logical argumentation" — a clear main message with reasoning that actually supports it), which is one of the three standards that apply at this level.

### Weaknesses (most to least threatening to the conclusion)
1. **Certain-language forecast built on a single, undated-range input** — Standard #2 ("Properly expresses and explains uncertainties" — is likelihood stated in calibrated estimative language?) and Standard #8 ("Makes accurate judgments and assessments" — confidence aligned to evidence quality, not overclaimed).
   > "Tech multiples will compress and small-caps will underperform large-caps through year-end."
   Why it matters: this is the load-bearing claim the whole trade rests on, and it is stated in flat, unhedged "will" language for a multi-month, two-part market outcome (multiple compression *and* a size-factor rotation) derived from one Fed statement. Nothing in the message carries the uncertainty in either step — whether "no cuts before December" is itself durable, or whether it actually transmits to tech multiples and small-cap relative performance the way assumed. This is the bias the library names **best-guess / uncertainty-drop** (cognitive-biases-and-mitigations.md: "treating a 75%-likely input as 100% true"); its prescribed mitigation is to carry the uncertainty through rather than rounding to certain.
   Fix: restate with the ICD 203 estimative-probability ladder and a confidence level kept separate from it, e.g. "We assess it is likely (~60–70%) that tech multiples compress and small-caps underperform through year-end if the no-cuts stance holds; confidence is moderate, resting on one Fed statement not yet corroborated by rate-futures pricing." Before sizing further, run a **Premortem / Structured Self-Critique** (the library's prescribed technique for an overconfident forecast) — write the two-line postmortem for "the rotation was wrong" now, and name what evidence would change the call.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #6 — Clear and logical argumentation | Good | "Rotating: +5% TLT, −10% QQQ" follows transparently from the stated judgment |
| #3 — Information vs. assumption vs. judgment | Fair | "Powell just confirmed no cuts before December" (reported) slides directly into "Tech multiples will compress…" (judgment) with no signal phrase ("we assess/judge") marking the shift |
| #2 / #8 — Uncertainty expressed and judgments not overclaimed | Poor | "will compress," "will underperform" — no calibrated probability term, no confidence statement, for a multi-month call resting on one input |

### If I were the analyst, the one change I'd make first
Replace both "will" clauses with a calibrated probability term and a separately-stated confidence level, tied explicitly to how much the call leans on the single Fed data point.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md, structured-analytic-techniques.md
