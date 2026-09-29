# Routing sample — does kb-retrieve route well enough to need no orchestrator? 2026-09-28

Evidence, not knowledge. It backs ADR-0011.

## Protocol

Two questions per library, drawn by seeded random from each library's golden set
(`key.json`: question, expected file, case type). The draw swapped in azure-devops's cross-root
case. Three `kb-retrieve` agents answered four questions each, with the libraries mixed across the
batches, under their normal contract and forbidden the golden sets and eval folders. Each agent
reported every library it opened for each question, split into router only and content beyond the
router. Graded by hand against `key.json`.

## Results

| Q | Library (expected file) | Answered from | Content beyond routers read in |
|---|---|---|---|
| Q01 | agile-requirements (story-splitting-spidr) | ✅ same file | agile-requirements only |
| Q02 | agile-requirements (elicitation-techniques) | ✅ same file | agile-requirements only |
| Q03 | ai-writing-signals (structural-and-rhetorical-patterns) | ✅ same file | ai-writing-signals only |
| Q04 | ai-writing-signals (punctuation-and-formatting-tells) | ✅ same file | ai-writing-signals only |
| Q05 | azure-devops (user-story-work-item) | ✅ same file | azure-devops only |
| Q06 | cross-root: azure-devops (user-story-work-item) → agile-requirements | ◐ right answer from both libraries; cited azure-devops's INDEX, not the linking file | agile-requirements (content) + azure-devops (router) |
| Q07 | claude-code-runtime (tool-semantics) | ✅ same file | claude-code-runtime only |
| Q08 | claude-code-runtime (behaviour-loading) | ✅ same file | claude-code-runtime only |
| Q09 | intelligence-analysis (structured-analytic-techniques) | ✅ same file | intelligence-analysis only |
| Q10 | intelligence-analysis (analytic-writing-craft) | ✅ same file | intelligence-analysis only |
| Q11 | knowledge-architecture (secret-governance) | ✅ same file | knowledge-architecture only |
| Q12 | knowledge-architecture (guardrail-verification) | ✅ same file, plus its episodic source as corroboration | knowledge-architecture only |

Right library: 12/12. Expected file: 11/12. Unneeded content reads: 0. Two batches read all six
routers up front, and one read only the three it needed. Answer text is not archived. The table
records the measured quantities as each agent reported them.
