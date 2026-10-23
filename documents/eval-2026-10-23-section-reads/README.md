# Retrieval run — section reads (#78). 2026-10-23

Evidence, not knowledge. It is the third routing sample, and the first since `kb-retrieve` was told
to read the section that answers rather than the whole file (#78, engine `61c17d0`). It asks whether
that change kept routing and grounding intact. It cannot measure the token saving: these six
libraries have small files, and the large-file library the issue measured is on another machine.

## Protocol

- Thirteen golden questions drawn with seed 20261023: per library one positive and one negative
  case, plus every unresolved and uncorroborated case (one unresolved, in ai-writing-signals; no
  library holds an uncorroborated case). `key.json` lists them.
- One fresh `kb-retrieve` agent per question, in a session started after #78 merged, so the agent
  ran the new definition. Each was given the question and one added instruction: do not open golden
  sets or eval folders.
- Graded by `scripts/grade-routing` from the Read, Grep and Glob calls in each transcript, and by
  `scripts/grade-eval --transcripts` from the answer and its `Sources:` line. Neither grades what
  the agent said about its own reads.

## Results

| Case | Library (golden Q, type) | Routing | Grounding | How the answering file was read |
|---|---|---|---|---|
| E01 | agile-requirements (Q5, positive) | pass | pass | outline, then one section |
| E02 | agile-requirements (Q15, negative) | pass | pass | no fact file read |
| E03 | ai-writing-signals (Q7, positive) | pass | pass | outline, then one section |
| E04 | ai-writing-signals (Q12, unresolved) | pass | pass | outline, then the CONFLICTED section; the contradictions register whole |
| E05 | ai-writing-signals (Q21, negative) | pass | pass | outline, then one section |
| E06 | azure-devops (Q6, positive) | pass | pass | outline, then one section |
| E07 | azure-devops (Q15, negative) | pass | pass | no fact file read |
| E08 | claude-code-runtime (Q10, negative) | pass | pass | no fact file read |
| E09 | claude-code-runtime (Q21, positive) | pass | pass | keyword search, then two sections |
| E10 | intelligence-analysis (Q1, positive) | pass | pass | outline, then one section |
| E11 | intelligence-analysis (Q17, negative) | pass | pass | no fact file read |
| E12 | knowledge-architecture (Q8, positive) | pass | pass | search across `kb/` first, then one section |
| E13 | knowledge-architecture (Q44, negative) | pass | **fail** | search across `kb/` first, then a section of a library file and a section of an engine ADR |

Routing 13/13. Contamination 0/13. Grounding 12/13.

- **The section reads did what #78 asked.** Every answer that rested on a file was read as a section,
  never the whole file. The dispute case still refused: the section read held the `status:
  CONFLICTED` marker, as CONVENTIONS §8 places it, and the agent served neither claim.
- **E13 answered from outside the knowledge base.** Asked whether push protection is on for "the
  library's repository", the library holds no answer, and the golden case expects `fact not found`.
  The agent read `documents/decisions/0002-governance-without-enforcement.md`, an engine decision
  record, and answered from it. Rule 3 of `kb-retrieve` forbids answering from what surrounds the
  knowledge base. `grade-eval` failed the case; `grade-routing` passed it, because it does not count a
  read outside every registered library against a case. Not caused by #78.
- **E12 and E13 searched across `kb/` before reading a router.** Both searches matched only the needed
  library, so neither case fails on it. It is the pattern the owner ruled a failure on 2026-10-12, when
  the matches reached other libraries.

## Not archived

Answer text and transcripts are not archived, as in the 2026-10-12 run: transcripts are private
session data. What is recorded is what was measured from them.
