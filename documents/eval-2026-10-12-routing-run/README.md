# Routing run — graded from tool calls, not self-report. 2026-10-12

Evidence, not knowledge. It is the second routing sample; the first (`../eval-2026-09-28-routing-sample/`)
relied on each agent reporting what it had opened. This one reads the tool calls.

## Protocol

- Twelve golden questions, two per library, drawn with seed 20261012 from the positive and
  cross-root cases (`key.json`: question, expected file, case type; the draw produced positive
  cases only).
- One fresh `kb-retrieve` agent per question. Each was given the question and one added
  instruction: do not open golden sets or eval folders.
- Graded by `scripts/grade-routing` from the Read, Grep and Glob calls in each agent's transcript,
  never from what the agent said. A case passes when the expected file was Read, content was read
  only from libraries the case needs, and no golden set or eval folder was touched.

## Results

Q is the key id; the golden-set position (grade-routing's Q<n>) is in the last column.

| Q | Library (expected file) | Routed to expected file | Content-in libraries | Contamination | Golden Q |
|---|---|---|---|---|---|
| Q01 | agile-requirements (acceptance-criteria-and-elicitation) | yes | agile-requirements | none | 7 |
| Q02 | agile-requirements (story-format-and-invest) | yes | agile-requirements | none | 1 |
| Q03 | ai-writing-signals (signal-weighing-and-tiers) | yes | ai-writing-signals | none | 2 |
| Q04 | ai-writing-signals (signal-weighing-and-tiers) | yes | ai-writing-signals | none | 1 |
| Q05 | azure-devops (user-story-work-item) | yes | azure-devops | none | 1 |
| Q06 | azure-devops (user-story-work-item) | yes | azure-devops | none | 9 |
| Q07 | claude-code-runtime (behaviour-loading) | yes | claude-code-runtime | none | 19 |
| Q08 | claude-code-runtime (config-resolution) | yes | claude-code-runtime | none | 3 |
| Q09 | intelligence-analysis (analytic-writing-craft) | yes | intelligence-analysis | none | 4 |
| Q10 | intelligence-analysis (analytic-writing-craft) | yes | intelligence-analysis | none | 7 |
| Q11 | knowledge-architecture (secret-governance) | yes | all six libraries | none | 4 |
| Q12 | knowledge-architecture (agent-lifecycle-roles) | yes | knowledge-architecture | none | 13 |

Expected file Read: 12/12. Contamination: 0/12. Unneeded content reads: 1 case (Q11), below.

## What the grader got wrong, and what it did not

First grading: 6/12 pass. All six failures carried the first bug below; one of them (Q11) has a second, genuine cause.

1. **An exclusion glob counted as contamination.** `kb-retrieve` tells its agent to pass Grep the
   glob `!{**/*-golden.md,**/documents/eval-*/**}`. The grader matched "golden" in Grep and Glob
   arguments, so every compliant agent that followed the instruction failed. A call with a paired
   result is now judged by the result's paths alone; with no result, a `!` glob is never
   contamination and is applied when computing the scope.
2. **Suspected: content attributed to libraries the result never held (Q11).** Investigated;
   not a grader bug. The Grep over `kb/` was capped (`head_limit` 40) and its result had no pagination
   note; its lines were attributed by path, and relative `kb/<library>/...` paths resolve
   against the engine root correctly. The result did contain lines from outside the library:
   two lines from each of the other five libraries' `.github/workflows/guardrails.yml`
   (CI comment lines that matched the search pattern). The attribution was right.

After the fix: 11/12. Q11 still fails, on a true reading of the tool call: the agent saw
content lines from five unneeded libraries' CI files, though it never opened a fact file there.
The grader counts any non-INDEX file under a library as that library's content, so the case
stays failed. The owner decided it counts (2026-10-12): the agent searched every library before
reading a router, which is what the routing check exists to catch, and this time it happened to
hit boilerplate rather than another library's facts. The grader is not changed to exempt `.github/`.

## Not archived

Answer text and transcripts are not archived. Transcripts are private session data. What is
recorded is the measured quantities above, which were derived from them.
