## IA Review — Spike Finding: Events Store Selection for Activity-Feed Service

**Reviewed at:** Medium level — a two-day engineering spike recommending an infrastructure choice (Kafka/Confluent Cloud) that the team will act on ("provision a Confluent Cloud Standard cluster... Monday"); not a formal assessment, but consequential enough to warrant more than a one-line check.

**Analytic line (BLUF as written):** "Recommendation: Apache Kafka (Confluent Cloud)"

### Strengths
- **BLUF stated immediately and unambiguously.** The recommendation is the second line of the document, before any supporting narrative — satisfies ATS #6 on position, not just clarity. Most reviews of this kind of memo catch a buried lede; this one doesn't have that problem.
- **Concrete, actionable next step.** "Provision a Confluent Cloud Standard cluster; estimated stand-up 2 days" gives the reader something to execute against immediately, with a real estimate attached rather than a vague "let's proceed" — satisfies ATS #5 (customer relevance/implications).

### Weaknesses (most to least threatening to the conclusion)

1. **Only one option considered, and the evidence given doesn't discriminate between Kafka and a simpler store** — Standard #4 (Analysis of Alternatives)
   > "Our firehose currently produces ~8,000 events/day across all tenants, so Kafka should scale fine as we grow to enterprise tier."
   Why it matters: ~8,000 events/day is ≈0.09 events/sec — roughly seven orders of magnitude below the 1M events/sec/broker figure cited as justification. That headroom doesn't argue *for* Kafka specifically; it's equally consistent with a far simpler and cheaper store (a Postgres append-only table, a managed queue, a basic log) being entirely sufficient. This is satisficing — stopping at the first plausible answer without asking what a competing hypothesis would need to be true. The memo frames itself as a spike "to evaluate an events store" but never names a second candidate or gives a reason for eliminating one, so the reader can't tell whether Kafka's operational complexity is actually earning its keep at this volume.
   Fix: Run a light ACH — put Kafka against at least one simpler alternative on the two things that actually matter here (durable replay, ops/cost burden), not raw throughput capacity nobody needs. If Kafka still wins because of the replay requirement specifically, say that explicitly instead of leaning on the throughput number.

2. **Decisive capacity claim rests on a single, self-interested, uncorroborated source** — Standard #1 (Quality/Credibility of Sources)
   > "Confluent's engineering blog reports throughput exceeding 1 million events/sec per broker at sub-10 ms p99 latency."
   Why it matters: this is the vendor's own promotional benchmark for the product being recommended, cited with no independent corroboration and no statement of the test conditions (message size, replication factor, ack settings, hardware) that would say whether it transfers to this deployment. An uncorroborated, motivated source is being used as the load-bearing evidence for the recommendation's central claim.
   Fix: Run a Quality-of-Information Check — either find an independent benchmark/case study, or explicitly flag the figure as a vendor-reported ceiling rather than an expected number, and note that it isn't actually the binding constraint given the stated 8,000/day load.

### Scorecard (only applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| #6 Clear argumentation | Good | BLUF on line 2, before any supporting detail — position and clarity both met |
| #1 Source quality | Poor | Sole capacity evidence is "Confluent's engineering blog," an uncorroborated vendor source |
| #2 Uncertainty expressed | Fair | "Kafka should scale fine" is asserted flatly with no calibrated likelihood or confidence level, though the register is appropriate for a two-day spike |
| #3 Info vs. assumption vs. judgment | Good | "~8,000 events/day" (reported) is kept distinct from "Kafka is the right choice" (judgment) |
| #4 Analysis of alternatives | Poor | No competing store named or dismissed anywhere in the memo |
| #5 Customer relevance | Good | Concrete next step and timeline given for the team to act on |
| #8 Accuracy of judgment | Fair | Directionally plausible, but confidence is not aligned to evidence quality — the cited evidence overshoots the actual requirement rather than supporting it |

### If I were the analyst, the one change I'd make first
Replace the vendor throughput figure with a one-line comparison against at least one simpler alternative, sized to the actual 8,000/day load and the stated replay requirement — that's the evidence that would actually discriminate whether Kafka is the right call or just the first one considered.
