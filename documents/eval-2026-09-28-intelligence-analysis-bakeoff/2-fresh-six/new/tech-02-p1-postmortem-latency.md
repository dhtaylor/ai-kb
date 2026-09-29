## IA Review — P1 Postmortem — API Latency Spike, 2026-06-14 (DRAFT)

**Reviewed at:** Medium level — an internal incident postmortem/memo addressed to engineering stakeholders deciding whether the fix and follow-ups are sufficient; not a formal published risk/threat assessment (Full), and too substantive to be an offhand note (Light).
**Analytic line (bottom line as written):** "Root cause: The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."

### Strengths
- The timeline entries are stated as plain reported fact with no overclaiming — "14:32 UTC: p99 API latency crossed 4,000 ms; SLA alert triggered" — which is exactly the information/judgment separation Standard #3 ("Properly distinguishes underlying information from analysts' assumptions and judgments") asks for, at least for the chronology itself.
- The action items are concrete and scoped rather than generic — "Add an EXPLAIN-based slow-query check to the CI pipeline to catch missing indexes pre-deploy" names a specific mechanism and a specific failure mode, satisfying Standard #5's call to address implications with real specificity rather than "improve monitoring."

### Weaknesses (most to least threatening to the conclusion)

1. **Root cause stated as confirmed fact from only correlational evidence** — Standard #3: "Properly distinguishes underlying information from analysts' assumptions and judgments"
   > "Root cause: The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."
   Why it matters: The only evidence offered is that logs showed elevated query times and that latency recovered after the v3.9.1 rollback (14:51 → 14:55) — a temporal correlation between the rollback and recovery, not a confirmed causal mechanism. No EXPLAIN plan, schema diff, or other check is cited as having verified that a missing index existed or that full-table scans actually occurred. Reading "rolled back and it got better" as proof of a specific mechanism is the **illusory correlation** bias (cognitive-biases-and-mitigations.md: "seeing a relationship that isn't there from co-occurring cases... correlation is not cause") — the recovery is equally consistent with the rollback having reverted something else in the same release. If the real mechanism differs, both prescribed fixes (backfill the index, add an EXPLAIN check) may miss the actual problem.
   Fix: State the cause as a judgment with a confidence level, e.g., "We assess (moderate confidence) that a missing index on `events` caused full-table scans; this is inferred from the log pattern and the timing of recovery after rollback, not yet confirmed by an EXPLAIN plan against the affected queries." Then either report that confirming check as already done, or add it as an action item before backfilling.

2. **Bottom line arrives after a full chronology** — Standard #6: "Uses clear and logical argumentation"
   > The product opens with "Timeline:" and four chronological, timestamped bullets before "Root cause:" appears at all.
   Why it matters: This is the disguised buried-BLUF case named in the library's writing-craft guidance — "a postmortem or timeline that opens with a chronology... instead of leading with impact, confirmed cause, and remediation." A reader who stops after the first section has timestamps but no cause, no fix, and no status. For a P1 report, the reader deciding whether the incident is closed and the fix validated has to read past the whole timeline to find out.
   Fix: Lead with a one- or two-sentence BLUF stating impact, cause (with confidence per finding 1), and current status — e.g., "P1 resolved: 23-minute p99 latency spike (>4,000ms) on 2026-06-14, likely caused by a missing index on `events`; mitigated by rolling back v3.9.1." Move the timeline below it as supporting detail.

3. **No competing explanation considered** — Standard #4: "Incorporates analysis of alternatives"
   > absent: no alternative explanation for the latency spike appears anywhere in the product.
   Why it matters: The postmortem stops at the first explanation that fit once the rollback worked — Pherson's "satisficing" trap (cognitive-biases-and-mitigations.md: "stopping at the first good-enough explanation"). It never asks whether the elevated query times on `/user-events` could have another driver — a concurrent traffic spike, a downstream dependency slowdown, connection-pool exhaustion — that the rollback also happened to relieve. Without ruling out at least one alternative, the confidence implicitly placed in the stated root cause is unearned.
   Fix: Run a light Analysis of Competing Hypotheses (per the library's weakness-to-technique mapping: "only one explanation on the table -> Analysis of Competing Hypotheses, even a light pass"): name at least one plausible alternative and the one piece of evidence — a query plan, resource metrics during the window — that actually discriminates between it and the missing-index explanation.

### Scorecard (only the applicable standards)

| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Properly describes quality and credibility of sources, data, and methods | Fair | "logs showed elevated query times on the /user-events endpoint" — a source is cited but not characterized (which logs, corroborated by APM/metrics, how confirmed) |
| #2 Properly expresses and explains uncertainties | Poor | "Root cause: ... causing full-table scans under concurrent write load" stated with no hedge or confidence level |
| #3 Properly distinguishes underlying information from analysts' assumptions and judgments | Poor | same root-cause line — a judgment presented as established fact (finding 1) |
| #4 Incorporates analysis of alternatives | Poor | absent — no competing explanation anywhere (finding 3) |
| #5 Demonstrates customer relevance and addresses implications | Good | "Add an EXPLAIN-based slow-query check to the CI pipeline to catch missing indexes pre-deploy" — specific, actionable implication |
| #6 Uses clear and logical argumentation | Poor | opens with "Timeline:" rather than the bottom line (finding 2) |
| #8 Makes accurate judgments and assessments | Fair | root cause is plausible and the action items are reasonable, but confidence is not aligned to the evidence actually shown |

### If I were the analyst, the one change I'd make first
Rewrite the opening as a hedged, confidence-stated bottom line instead of an unhedged causal claim buried after the timeline: state impact, the likely (not confirmed) cause, and status in the first two sentences, then move the chronology below it as support.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, cognitive-biases-and-mitigations.md
