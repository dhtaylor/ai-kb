## IA Review — P1 Postmortem — API Latency Spike, 2026-06-14 (DRAFT)

**Reviewed at:** Medium level — an internal engineering incident memo read by engineering stakeholders to confirm cause and track remediation, not a finished, standalone assessment built for external reliance; a postmortem is a form the calibration ladder doesn't name, so the default rule ("a form no list names is Medium") applies.

**Analytic line (bottom line as written):** "The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."

### Strengths
- The timeline is quantified and precise, not vague — exact timestamps, an exact p99 figure ("crossed 4,000 ms"), and a stated duration ("~23 minutes") — which is exactly the kind of crisp, checkable information Standard #3 ("Properly distinguishes underlying information from analysts' assumptions and judgments") wants on the information side of the ledger.
- The action items demonstrate real customer/implication relevance (Standard #5, "Demonstrates customer relevance and addresses implications") — they don't stop at fixing this one table; item 3 ("Review tables added in the last three sprints for missing indexes") generalizes the fix to the systemic risk, which is the "so what" a reader needs.

### Weaknesses (most to least threatening to the conclusion)

1. **A reported recovery is written up as a confirmed cause** — Standard #3, "Properly distinguishes underlying information from analysts' assumptions and judgments"
   > "14:55 UTC: Latency returned to baseline." ... "Root cause: The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."
   Why it matters: what's actually reported is that latency recovered after the rollback — that's consistent with the missing-index theory, but it doesn't by itself establish that full-table scans were occurring, only that something about v3.9.1 was implicated. The document takes the reliability/evaluation step for granted and states the specific mechanism as settled fact rather than as a judgment resting on that correlation.
   Fix: Add the missing evaluative move — either cite the confirming evidence (e.g., an EXPLAIN/query-plan showing the scan) or mark it as a judgment with a signal phrase and confidence: "We assess (moderate confidence) that a missing index on `events` caused full-table scans; this rests on the query-time spike and the rollback-linked recovery, not yet on a confirmed query plan."

2. **No competing explanation is named or ruled out** — Standard #4, "Incorporates analysis of alternatives"
   > "Root cause: The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."
   Why it matters: only one hypothesis is on the page. A latency spike coinciding with a release is also consistent with other causes (a concurrent write-volume surge, a downstream dependency degrading, resource contention unrelated to the schema) that the rollback-fixed-it correlation doesn't by itself exclude. If the real driver were something else, the proposed fixes (backfill the index, add an EXPLAIN gate) would miss it.
   Fix: Run a light Analysis of Competing Hypotheses — just step 1 and step 5 of the method: name at least one other plausible explanation, and ask whether any evidence actually discriminates between it and the missing-index theory or is merely consistent with both.

3. **The bottom line is buried behind the chronology** — Standard #6, "Uses clear and logical argumentation"
   > "Timeline:\n- 14:32 UTC: p99 API latency crossed 4,000 ms; SLA alert triggered."
   Why it matters: this is the disguised case the BLUF standard specifically calls out — a postmortem that opens with the clock instead of leading with impact, confirmed cause, and remediation. A reader who stops after the first line gets no answer, only a timestamp.
   Fix: Open with a one- to two-sentence BLUF before the timeline: "A missing index on `events` caused a 23-minute P1 latency spike (14:32–14:55 UTC); rollback resolved it, and the index will be backfilled by [date]." Let the timeline follow as supporting detail, not the lead.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 — quality/credibility of sources, data, methods | Fair | "logs showed elevated query times on the /user-events endpoint" — a source is named but not characterized (which tool/dashboard, how corroborated) |
| #2 — properly expresses and explains uncertainties | Poor | The root cause sentence carries no calibrated likelihood term and no separately stated confidence anywhere in the document |
| #3 — distinguishes information from assumption/judgment | Fair | "Root cause: ... causing full-table scans" is headed separately from the timeline (a real structural cue) but still states the specific mechanism as flat fact rather than a labeled judgment |
| #4 — incorporates analysis of alternatives | Poor | No alternative explanation appears anywhere in the document |
| #5 — customer relevance and implications | Good | "3. Review tables added in the last three sprints for missing indexes." — generalizes beyond the single incident |
| #6 — clear and logical argumentation (BLUF) | Poor | Document opens with "Timeline:" rather than the judgment |
| #8 — accurate judgments, confidence aligned to evidence | Fair | "causing full-table scans" asserts a specific mechanism the cited evidence ("elevated query times") doesn't fully establish on its own |

### If I were the analyst, the one change I'd make first
Before shipping the backfill and the CI gate, close the gap between what was observed (query times spiked, rollback fixed it) and what was concluded (full-table scans from a missing index): either attach the confirming query-plan evidence or state the root cause as a judgment with a confidence level. Everything downstream — the action items, the CI check — is only as good as that one causal claim, so it's the fix with the most leverage.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md
