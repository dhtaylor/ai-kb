# Retrieval run — triage and specialists (#130). 2026-11-05 to 2026-11-06

Evidence, not knowledge. This run compares the single `kb-retrieve` agent with `kb-ask`. In `kb-ask`,
a triage desk in the main session reads `kb-catalog` and sends each question to a `kb-retrieve`
specialist confined to one library. The evidence is for [ADR-0018](../decisions/0018-triage-and-specialists.md).

## Protocol

- **Cases.** The 24-case subsample of the 2026-10-26 retest (seed 20261026), listed in `key.json`.
  Every question still matched its golden set.
- **Libraries.** The 6 real libraries, and the same 6 plus 42 decoy libraries (48 in all). The
  decoys were rebuilt from the 2026-10-26 builder. They include the three near neighbors that pulled
  before: agile-estimation, git-hooks and red-team-analysis. They sit on a neutral path and carry no
  `Not covered here:` line. The registry was backed up and restored byte-identical after every run
  (sha256 `5079533f…`).
- **Runs.** Each case ran as a fresh `claude -p --model sonnet` session from an empty directory.
  - **Arm A**, today's route: "Use the knowledge-tools:kb-retrieve agent to answer this question: …".
  - **Arm B:** `/knowledge-tools:kb-ask …`.
- **Grading.** Every grade comes from transcripts and the answer, never from what an agent said
  about its own reads.
  - **Routing:** `scripts/grade-routing` on the main session's transcript joined with its
    subagents' transcripts.
  - **Agent grounding:** `scripts/grade-eval --transcripts` on the specialist's own answer.
  - **Delivered grounding:** `grade-eval` on the answer the main session returned to the person.
- **Tokens.** Input plus cache creation plus output, each message counted once (as
  `kb-telemetry` counts them). "Specialist" means the subagents only. Means cover valid runs only.
  Runs that returned only a usage-limit message were run again.

**This differs from the 10-26 protocol** (several questions per subagent, sent from one session) in
two ways. Each case is now its own session. Delivered grounding is new: it grades what the person
actually receives.

## Results

| Run | Routing | Agent grounding | Delivered grounding | Strayed into another library | Answered from the wrong library | Tokens/question (total) | Specialist tokens | Cost/question |
|---|---|---|---|---|---|---|---|---|
| A, 6 libraries | 23/24 | 24/24 | 4/24 | 1 | 0 | 40.7k | 19.0k | $0.161 |
| B, 6 libraries (first skill) | 21/24 (23*) | 23/24 | 23/24 | 0 | 0 | 31.4k | 7.1k | $0.137 |
| A, 48 libraries | 19/24 | 21/24 | 3/24 | 4 | 0 | 51.1k | 25.5k | $0.196 |
| B, 48 libraries (fixes 1–2) | 19/24 (20*) | 20/24 | 21/24 | 3 | 1 | 42.2k | 9.5k | $0.181 |
| B, 48 libraries (fixes 1–3) | 20/24 | 20/24 | 21/24 | 4 | 2 | 45.4k | 10.4k | $0.193 |

\* The specialist read the expected file only through a one-file content Grep, which
`grade-routing` does not count as reading it.

**The skill changed during the run.** After the first B runs, three fixes went in:
1. **Ask a library even when its description doesn't mention the topic.** Triage had refused KA Q4
   ("Does rotating a leaked secret remove it from git history?") without asking any library.
2. **After a `fact not found`, ask the runner-up.** At 48 libraries, the agile-estimation decoy said
   `fact not found` for az Q6, and the desk stopped there.
3. **List each library's router topics in `kb-catalog`.** knowledge-architecture's description
   doesn't mention secrets, but its router lists `secret-governance`.

At 6 libraries, the final skill was rerun on KA Q4 only, and it passed.

## Failures in the last B run at 48 libraries

- **az Q6:** the agile-estimation decoy said `fact not found` and pointed to azure-devops, which
  answered. The delivered answer passes. Routing fails on the read into the decoy.
- **ccr Q21:** git-hooks said `fact not found`, then claude-code-runtime answered from
  `config-resolution.md` instead of the open-questions file the case expects. Arm A failed it too.
- **IA Q11 and IA Q12:** triage sent both to the red-team-analysis decoy, which holds devil's
  advocacy and pre-mortem material and answered them. The topics catalog (fix 3) caused IA Q11,
  since the decoy's router lists `devils-advocacy-and-pre-mortems`.

Arm A at 48 libraries failed az Q6, ccr Q13, ccr Q21, IA Q11, IA Q12 and KA Q4. On both IA cases it
strayed into red-team-analysis but answered from intelligence-analysis.

## What this run cannot show

- **No decoy has a `Not covered here:` line.** Every real library has one (contract 2.3), so a real
  near neighbor may separate better. That is untested.
- **One trial per case, 24 cases.** A one-case difference is within noise.
- **The final skill has not been rerun on all 24 cases at 6 libraries.**
- **Triage ran on Sonnet throughout.** The cost of triage on another main-session model is not
  measured.
