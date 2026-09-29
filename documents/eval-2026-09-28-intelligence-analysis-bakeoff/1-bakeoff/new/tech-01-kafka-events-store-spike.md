## IA Review — Spike Finding: Events Store Selection for Activity-Feed Service

**Reviewed at:** Medium level — a spike recommendation addressed to the team deciding what to provision; not a formal/consequential assessment, but more than a quick note.
**Analytic line (bottom line as written):** "Recommendation: Apache Kafka (Confluent Cloud)"

### Strengths
- Bottom line stated in the first two lines, before any supporting narrative — satisfies the BLUF position rule (Standard #6): a reader who stops after line 2 already has the answer.
- Concrete, decision-relevant next step with an owner and a timeline — "provision a Confluent Cloud Standard cluster; estimated stand-up 2 days" — addresses Standard #5 (customer relevance / so-what), not just the abstract pick.
- Grounds the recommendation in an actual reported figure rather than a vibe — "Our firehose currently produces ~8,000 events/day across all tenants" is a real, labeled data point (Standard #3's information half).

### Weaknesses (most to least threatening to the conclusion)

1. **No alternatives considered** — Standard #4, incorporates analysis of alternatives
   > "Kafka is the right choice: it provides durable, replayable event logs..."
   Why it matters: the document's own title frames this as a *selection* among event stores, but no other option (a managed queue, a simpler log, a database-backed outbox, etc.) is named or evaluated anywhere — the conclusion is asserted, not compared. This is exactly the pattern the library's master mapping flags: "Only one explanation on the table -> Analysis of Competing Hypotheses." It also matches Pherson's **satisficing** intuitive trap — stopping at the first good-enough explanation.
   Fix: Run a light ACH pass (sufficient for a medium-level product per the library): name at least one credible competing option, then ask whether any cited evidence actually discriminates between Kafka and it, or is merely consistent with both. If nothing discriminates, say so before recommending.

2. **Vendor's own benchmark used as the load-bearing, uncharacterized source** — Standard #1, properly describes quality and credibility of sources
   > "Confluent's engineering blog reports throughput exceeding 1 million events/sec per broker at sub-10 ms p99 latency. Our firehose currently produces ~8,000 events/day across all tenants..."
   Why it matters: the sole piece of evidence cited for the decision is the vendor's own marketing/engineering blog about its own product's benchmark performance — no note on its motivation, independence, or corroboration (Standard #1's bias/motivation and corroboration checks). It is also not diagnostic at this scale: ~8,000 events/day is roughly 0.09 events/sec, about seven orders of magnitude below the cited 1M/sec figure, so the number can't actually discriminate between Kafka and a far simpler store for this workload.
   Fix: Run a Quality-of-Information Check — flag the source's vendor motivation explicitly, and replace or supplement the marketing figure with an independent benchmark or a load test run at the service's actual/projected volume, since that is what would actually support or rule out simpler alternatives.

3. **Uncalibrated growth claim** — Standard #2, properly expresses and explains uncertainties
   > "so Kafka should scale fine as we grow to enterprise tier"
   Why it matters: "should scale fine" and "enterprise tier" are undefined — no likelihood term, no target volume, no timeframe. Per the library's estimative-probability ladder, vague terms like this get silently mapped to whatever the reader already believes, and here it's the only stated justification for provisioning ahead of actual need.
   Fix: State it as a calibrated estimate tied to a number — e.g., "if volume grows to N events/day by <date>, Kafka is very likely (80–95%) to sustain it at <target p99>, based on <specific benchmark or internal projection>" — using the ICD 203 seven-term ladder rather than an unhedged adjective.

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #1 Sourcing quality/credibility | Poor | "Confluent's engineering blog reports throughput exceeding 1 million events/sec per broker" — sole, vendor-authored, uncharacterized, non-diagnostic at stated scale |
| #2 Expresses uncertainty | Fair | "Kafka should scale fine as we grow to enterprise tier" — vague term, no range, no target |
| #3 Information vs. assumption vs. judgment | Fair | "The built-in retention log gives us event replay at no extra implementation cost, which the team has flagged as a future need" — asserted as fact with no source for the team's need or the "no extra cost" claim |
| #4 Analysis of alternatives | Poor | No competing event store named or evaluated anywhere in the product |
| #5 Customer relevance / implications | Good | "provision a Confluent Cloud Standard cluster; estimated stand-up 2 days" |
| #6 Clear, logical argumentation | Fair | BLUF is positioned correctly ("Recommendation: Apache Kafka...") but the reasoning that follows doesn't fully support the exclusivity of the claim, given #1 and #4 |
| #8 Accurate judgments, not overclaimed | Fair | "Kafka is the right choice" is stated with more certainty than the one-sided, non-diagnostic evidence behind it supports |

(#7 — consistency with prior analysis — is N/A: this is initial coverage, no prior position is referenced.)

### If I were the analyst, the one change I'd make first
Name at least one real competing option and run a light ACH pass on it — everything else in the review (the vendor-sourcing gap, the uncalibrated growth claim) is downstream of the fact that only one hypothesis was ever on the table.

Sources: icd-203-tradecraft-standards.md, analytic-writing-craft.md, structured-analytic-techniques.md, cognitive-biases-and-mitigations.md
