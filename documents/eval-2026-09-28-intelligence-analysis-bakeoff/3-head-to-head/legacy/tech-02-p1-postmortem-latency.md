## IA Review — P1 Postmortem: API Latency Spike (2026-06-14, DRAFT)

**Reviewed at:** Medium level — an internal engineering postmortem/memo read by the on-call team and stakeholders to drive follow-up action; not a two-line note, but not a formal externally-read assessment either.
**Analytic line (BLUF as written):** "The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load." (appears as item 3 of the document, after the full timeline)

### Strengths
- The timeline is precise, timestamped, and quantified — "p99 API latency crossed 4,000 ms; SLA alert triggered" and "Incident duration: ~23 minutes" give a verifiable chronology a reader could audit against the alerting system. Satisfies ATS #1 for the chronology itself.
- The action items don't stop at the point-fix: alongside backfilling the index, they add "an EXPLAIN-based slow-query check to the CI pipeline" and a review of "tables added in the last three sprints for missing indexes." That's a systemic safeguard, not just a patch — good handling of "so what" (ATS #5).

### Weaknesses (most to least threatening to the conclusion)

1. **Buried BLUF** — Standard #6 (clear and logical argumentation)
   > "Root cause: The v3.9.1 release introduced a missing index on the `events` table, causing full-table scans under concurrent write load."
   This is the document's one load-bearing judgment, but it only appears after a four-line timeline block. This is the classic postmortem case: opening with chronology before impact and root cause. A reader (or an on-call engineer triaging at 2am) has to read the whole timeline before reaching the one sentence that matters.
   Fix: Lead with a two-line BLUF: "Impact: p99 latency exceeded 4,000ms for ~23 minutes (14:32–14:55 UTC). Cause: a missing index on `events`, introduced in v3.9.1, causing full-table scans under load; resolved by rollback." Move the timeline below it as supporting detail.

2. **Causal mechanism asserted as fact, not distinguished from what was observed** — Standard #3 (information vs. assumption vs. judgment)
   > "v3.9.1 rolled back after logs showed elevated query times on the /user-events endpoint." → "Root cause: ... causing full-table scans under concurrent write load."
   The observed fact is "elevated query times." The specific mechanism — full-table scans caused by a missing index — is a judgment stated with no separating language and no cited confirming evidence (no query plan, no scan-count metric). If the real mechanism differs (e.g., lock contention or another change in the same release), the prescribed fix won't fully prevent recurrence.
   Fix: Split observed from judged: "Observed: elevated query times on /user-events (14:32–14:51, per [log source]). Judged: caused by a missing index producing full-table scans — confirmed via [EXPLAIN plan / scan-count metric]." If that confirmation step wasn't actually run, say so as an open item rather than stating the mechanism as settled fact.

3. **No alternative explanation considered** — Standard #4 (analysis of alternatives)
   > "14:51 UTC: v3.9.1 rolled back ... 14:55 UTC: Latency returned to baseline."
   Rolling back the entire v3.9.1 release and seeing recovery shows something in that release caused the regression — it doesn't by itself isolate the missing index specifically, especially if the release shipped other changes. Nothing here rules out a competing explanation (another schema/query change in the same release, a coincident load spike).
   Fix: Name what else shipped in v3.9.1 and briefly state why it's ruled out, or note which piece of evidence is consistent with the missing-index hypothesis and not with the alternatives.

### Scorecard (only applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sourcing/data quality | Fair | "logs showed elevated query times" is cited but not characterized — no log excerpt or query-plan evidence for the specific full-table-scan claim |
| #2 Expresses uncertainty | Poor | No likelihood or confidence language anywhere; the causal claim is stated as unqualified fact |
| #3 Info vs. assumption vs. judgment | Fair | "elevated query times" (observed) and "causing full-table scans" (inferred mechanism) are not distinguished |
| #4 Analysis of alternatives | Poor | No competing explanation named or ruled out for what v3.9.1's rollback actually fixed |
| #5 Customer relevance | Good | Action items are concrete and scoped to the audience, and extend to systemic prevention (CI check, sprint audit) |
| #6 Clear argumentation | Fair | Root cause appears in item 3 of the document, after the full timeline block, rather than leading |
| #8 Accurate/warranted judgment | Fair | Plausible and consistent with symptom resolution, but stated with full certainty despite an unconfirmed causal mechanism |

### If I were the analyst, the one change I'd make first
Move the root cause and impact to a two-line BLUF at the top, before the timeline — that's the single fix that makes the rest of the document usable, and it's the change the other findings hang off of.
