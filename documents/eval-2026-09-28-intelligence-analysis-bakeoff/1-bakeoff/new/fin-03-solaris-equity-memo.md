## IA Review — Solaris Energy (SLRE) Equity Initiation

**Reviewed at:** Full level — a formal equity-research initiation report built around a modeled financial forecast (FY2026 revenue, EBITDA margin, price target) and a BUY recommendation, meant for external distribution to investors making a capital decision. This matches the Full-level list by form (a forecast, externally read) rather than by promoting the product for its stakes.

**Analytic line (bottom line as written):** "We initiate coverage with a BUY rating and a $21 price target."

### Strengths
- The industry-growth claim is a genuinely characterized source, not just a citation: "Commercial solar is growing at approximately 22% annually per Wood Mackenzie's Q3 2024 market report" names the issuing body, the specific report, and its vintage — satisfying ATS #1's bar for a source that is more than merely cited.
- The Financial Outlook keeps its modeled judgment separate from the assumptions it rests on rather than asserting the number as fact: "We model FY2026 revenue of $310M... contingent on: (a)... (b)... (c)..." explicitly enumerates the three premises the forecast leans on, which is exactly the information/assumption/judgment separation ATS #3 asks for.

### Weaknesses (most to least threatening to the conclusion)

1. **Single conjunctive scenario presented as the outcome** — ATS #4 (Incorporates analysis of alternatives)
   > "Assuming all three conditions hold, EBITDA margins reach 24% and the stock re-rates to 12× EV/EBITDA, implying a price target of $21 — representing 123% upside from current levels."
   Why it matters: the $21 target and the 123% upside figure require IRA credits surviving intact, 60%+ LOI-to-PPA conversion, AND a 2.1× capacity expansion without cost overruns to *all* hold simultaneously — yet the memo reports this compound outcome as if it were the expected case, with no downside scenario, no probability-weighted target, and no sensitivity to any single condition failing. This is the cognitive-biases library's **Conjunction / scenario inflation** (a multi-step scenario judged by averaging rather than multiplying its steps, so it feels more probable than it is; the stated mitigation is to multiply step probabilities and let the weakest link cap the chain, not present the joint case as the headline number).
   Fix: Retrieve and run **Alternative Futures / Scenarios** — build the forecast around the two biggest driving forces (IRA-credit survival and LOI conversion) into at least a bear/base/bull set of futures, each with its own price target, rather than betting the whole recommendation on one conjunctive path.

2. **The one condition the model can't survive losing is dismissed without support** — ATS #2 (Properly expresses and explains uncertainties)
   > "IRA policy uncertainty is noted but viewed as low probability."
   Why it matters: condition (a) of the FY2026 model is "IRA production tax credits surviving the next congressional cycle intact" — the single largest swing factor in the whole forecast — and the Risks section waves it off with an uncalibrated term and zero evidentiary basis (no cited legislative outlook, no base rate for mid-cycle credit repeal, nothing). This is the library's **Ambiguous probability language** bias ("probably/likely/soon" read differently by every reader; mitigation is the estimative-probability ladder plus a numeric range).
   Fix: Replace "low probability" with a ladder term and range (e.g., "unlikely, 20–45%"), state confidence in that estimate separately, and name what it rests on — or run a **Key Assumptions Check** on condition (a) specifically: what would make it false, and has anything like that already begun (e.g., current congressional posture on the credits)?

3. **Buried bottom line** — ATS #6 (Uses clear and logical argumentation / BLUF)
   > "We initiate coverage with a BUY rating and a $21 price target."
   Why it matters: this is the memo's only sentence stating the actual call, and it is the *last* sentence, arriving after Market Position, the full financial model, and Risks. A reader who stops at any point before the end has no recommendation at all — the classic buried-BLUF failure the library names (the judgment arriving after throat-clearing context rather than in the opening lines).
   Fix: Open with the message: "We initiate SLRE at BUY, $21 price target (123% upside), driven by IRA-credit-dependent margin expansion — see risks on convergence of three conditions below," then let Market Position/Financial Outlook/Risks carry the supporting reasoning in the existing order.

4. **The multiple that turns EBITDA into the price target has no source at all** — ATS #1 (Properly describes quality and credibility of sources, data, and methods)
   > "the stock re-rates to 12× EV/EBITDA"
   Why it matters: this multiple is the final conversion step from the modeled EBITDA into the $21 target, and unlike the Wood Mackenzie growth figure, it cites no comparable-company set, no historical trading range for SLRE or its peers, and no methodology — it is simply asserted. Removing this one unsupported number removes the mechanism that produces the price target.
   Fix: Run a **Quality-of-Information Check** — cite the peer set or historical range the 12× is drawn from (e.g., trading multiples of comparable C&I solar developers) and state whether it is a current, historical-average, or precedent-transaction multiple.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sources/data/methods properly described | Fair | "per Wood Mackenzie's Q3 2024 market report" (good) vs. "re-rates to 12× EV/EBITDA" (no source) |
| #2 Uncertainty properly expressed | Poor | "IRA policy uncertainty is noted but viewed as low probability" |
| #3 Information vs. assumption vs. judgment | Good | "contingent on: (a)... (b)... (c)..." |
| #4 Analysis of alternatives | Poor | "Assuming all three conditions hold... implying a price target of $21" — no bear/base case |
| #5 Customer relevance / implications | Good | "We initiate coverage with a BUY rating and a $21 price target" directly answers the investor's decision |
| #6 Clear, logical argumentation (BLUF) | Poor | Recommendation is the memo's final sentence |
| #7 Change/consistency vs. prior judgments | N/A | Initial coverage — exempt per the calibration table |
| #8 Accurate, warranted judgments | Fair | "representing 123% upside" stated flatly despite resting on three unweighted contingencies |
| #9 Effective visual information | Fair | No sensitivity table or comp table accompanies a three-condition model, though the product is text-first throughout |

### If I were the analyst, the one change I'd make first
Turn the single conjunctive bull case into an explicit bear/base/bull scenario set — each scenario stating which of the three conditions holds, its own probability, and its own price target — then lead the memo with the resulting recommendation instead of the current single unweighted $21 figure buried at the end.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
