## IA Review — Recommendation on APAC Expansion — Thailand Entry Decision

**Reviewed at:** Full level — addressed to management as a capital-approval decision ($1.2M budget cap) with a formal go/no-go gate; a strategy/entry decision like this is explicitly "consequential" under the library's own level definition, so all nine ICD 203 standards apply.

**Analytic line (bottom line as written):** "We judge, with moderate confidence, that Thailand is the right first APAC market for a FY2026 entry."

### Strengths
- The BLUF is genuinely up front, labeled, and carries the judgment plus its confidence in the first sentence — satisfies Standard #6 (clear and logical argumentation) and the position rule (no throat-clearing background before the judgment).
- Confidence is stated as a separate axis from likelihood and tied to the actual evidence base, not asserted in the abstract: "Confidence is moderate: the Indonesia analogy is directionally sound but subject to Thai-specific channel dynamics we have not yet fully mapped" — this is exactly the pattern Standard #2 requires (likelihood/estimate + confidence + the named weak link).
- The recommendation closes with predefined, observable go/no-go indicators ("pipeline coverage ratio ≥3× and partner NPS ≥40") rather than leaving the call unfalsifiable — this satisfies Standard #5 (addresses implications for the decision-maker) and functions as the library's Indicators/Signposts technique, which prevents later rationalization of the call either way.

### Weaknesses (most to least threatening to the conclusion)

1. **Incomplete, asymmetric analysis of alternatives** — Standard #4, Incorporates analysis of alternatives
   > "The strongest alternative is a Philippines-first entry... Philippine enterprise buying cycles run approximately 20% longer per our regional partner survey" / "its lower regulatory complexity relative to Vietnam make it the leading candidate."
   Why it matters: Malaysia — the second-largest market in the memo's own cited data ($510M, 14% growth, ahead of Vietnam) — is never named as a candidate or ruled out anywhere in the ALTERNATIVE CONSIDERED section. Vietnam is dismissed with a bare comparative phrase carrying no evidence, in sharp contrast to the Philippines comparison, which is backed by a cited survey. The conclusion is explicitly comparative ("the leading candidate," "outweighs the alternatives reviewed"), so a gap in which alternatives were actually tested is a gap in the support for the conclusion itself, not a side issue.
   Fix: Run Analysis of Competing Hypotheses (at least a light pass, per the library: force step 1 — is there a real alternative? — and step 5 — does any evidence actually discriminate?) across all four markets already in the memo's own dataset (Thailand, Philippines, Vietnam, Malaysia), not just Thailand vs. Philippines. If Malaysia and a fuller Vietnam case were deliberately scoped out before this memo, say so and why.

2. **Confidence expressed inconsistently across two comparably-uncertain estimates** — Standard #2, Properly expresses and explains uncertainties (bias: Oversensitivity to consistency / law of small numbers)
   > "Philippine enterprise buying cycles run approximately 20% longer per our regional partner survey (Q4 2024, n=12 resellers), which delays breakeven by roughly one quarter and reduces NPV at our 12% hurdle rate."
   Why it matters: This figure rests on a smaller, single-wave sample (n=12) than the Indonesia CAC-to-LTV analogy (n=200), yet the Indonesia estimate gets an explicit confidence caveat ("moderate... not yet fully mapped") while this one is stated flatly and used to produce the memo's most quantitatively precise downstream claims (a specific breakeven delay, a directional NPV/hurdle-rate conclusion). This is the library's "law of small numbers" pattern — a short, single-source result read as a stable fact — and it feeds directly into ranking Thailand over the strongest named alternative.
   Fix: Apply the same treatment used for the CAC/LTV estimate: state a calibrated confidence level for the 20%-longer-cycle figure and flag the small, single-wave sample before using it to size an NPV effect.

3. **Source motivation/bias never characterized for the two most decision-driving sources** — Standard #1, Properly describes quality and credibility of sources, data, and methods
   > "Our own customer-discovery interviews (n=18 Thai enterprise buyers, Q1 2025, conducted by our regional BD team)" / "our regional partner survey (Q4 2024, n=12 resellers)"
   Why it matters: Both sources are internal to the team proposing the entry (the regional BD team) or drawn from parties with a stake in which market gets the investment (resellers). Standard #1 calls for bias/motivation to be assessed for any source that materially drives a judgment. The memo characterizes sample size, date, and method for both, but never addresses motivation — and these are precisely the two sources carrying the willingness-to-pay claim and the case against Philippines.
   Fix: Run a Quality-of-Information Check on both sources — add a one-line source descriptor on whether the BD team or the surveyed resellers had an interest in the outcome, and whether either finding has been corroborated by a source without that interest.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sourcing quality/credibility | Fair | Sample size/date/method given throughout; bias/motivation never addressed for the BD-team interviews or partner survey |
| #2 Expresses uncertainty | Fair | Strong hedge on the CAC/LTV estimate ("Confidence is moderate...") vs. no hedge on the n=12 buying-cycle figure |
| #3 Information vs. assumption vs. judgment | Good | "We assess that Thailand's favorable CAC-to-LTV profile — estimated 2.8× based on our Indonesia cohort (nearest proxy...)" clearly separates reported data, the analogy/assumption, and the judgment |
| #4 Analysis of alternatives | Poor | Malaysia absent from ALTERNATIVE CONSIDERED entirely; Vietnam dismissed via unevidenced "lower regulatory complexity" |
| #5 Customer relevance/implications | Good | "Approve a Thailand pilot with a $1.2M budget cap... Formal go/no-go review at month six against two leading indicators" |
| #6 Clear, logical argumentation (BLUF) | Good | Judgment and confidence stated in sentence one, ahead of all background |
| #7 Consistency with prior judgments | N/A | No prior APAC-entry analytic coverage referenced; treated as initial coverage, which the library exempts from this standard |
| #8 Accurate, warranted judgments | Fair | Warranted for Thailand-vs-Philippines; under-warranted for Thailand-vs-Vietnam/Malaysia given the evidence gap in finding 1 |
| #9 Effective visual information | Fair | Three-market quantitative comparison (spend, growth, regulatory complexity) given only in prose; a table would aid but does not change the conclusion |

### If I were the analyst, the one change I'd make first
Run the Analysis of Competing Hypotheses light pass across all four markets in the memo's own dataset (Thailand, Philippines, Vietnam, Malaysia) before the recommendation goes to management — everything else in the memo is well-built on top of a comparative claim that, as written, was only actually tested against one alternative.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md, structured-analytic-techniques.md
