# Behavioural eval — `intelligence-analysis` skill, 2026-09-26

Evidence, not knowledge: nothing here is routed, and nothing here is a fact. It records how the
`analysis-tools` skill's review mode was tested against the legacy skill it replaces, and what the
test found, so the result can be re-examined rather than taken on a paragraph in the plan (§9.17).

## Protocol

- **Corpus:** six cases from the legacy skill's own graded corpus (the `intelligence-analysis`
  skill's `evals/evals.json`, workspace `/mnt/c/workspace`, a separate repository). The six are one
  flawed case at each level (Light, Medium and Full) and all three clean controls. `cases/` holds the
  snippets exactly as reviewed. `gold.json` holds each case's level, expected finding count and
  planted flaws, copied from that corpus.
- **Separation:** the gold key and the snippets were split into separate files before any review.
  Each review ran in a fresh agent that saw only the skill and its one case file. Each was told not
  to open the gold key, the legacy corpus, the golden set or any `documents/eval-*/` folder. Every
  agent listed the files it opened, and none opened a forbidden one.
- **Grading:** by hand against the gold key, not by script. A review passes when its finding count
  is within the case's expected range and it names the planted flaws. For a control, the count
  alone decides it. Standard labels that differ from the gold key while the substance matches are
  noted, not failed.
- **Trials:** one per case per round. These results show direction, not frequency.

## Round 1: 3/6, first build

The skill as first built. Retrieval was sound in every review: all six cited real library files.

| Case | Level | Expected | Result |
|---|---|---|---|
| fin-01 | Light | 0–1 | **Pass.** 1 finding, the gold flaw |
| geo-02 | Full | 3–5 | **Pass.** 3 findings; one gold flaw under a different standard |
| clim-02 (control) | Full | 0–1 | **Pass.** 1 finding |
| epi-01 | Medium | 2–3 | **Fail.** Promoted to Full, 4 findings, gold flaws present |
| biz-02 (control) | Medium | 0–1 | **Fail.** Promoted to Full, 3 findings |
| epi-02 (control) | Full | 0–1 | **Fail.** 2 findings; it credited the gold flaw as a strength |

All three failures were over-reviewing. The cause: the fold had rightly left the legacy review rules
out of the library as behaviour, and the first build restored only some of them.

## Round 2: the three failures re-run, plus a legacy baseline

Between rounds, the missing rules were restored, and one new rule was added: **the product's form
sets its level**. The legacy skill ran the same three cases as a baseline, under the same
separation, fenced off from its own `evals/` folder.

| Case | Legacy baseline | Port |
|---|---|---|
| epi-01 | **Fail.** Promoted to Full, 4 findings | **Pass.** Medium, 3 findings, all gold flaws; buried bottom line ranked last |
| biz-02 (control) | **Fail.** Promoted to Full, 3 findings | **Fail.** Medium, 2 findings |
| epi-02 (control) | **Pass.** 1 finding, the gold flaw | **Fail.** 4 findings; gold flaw caught, and the sourcing rule stretched to a verified metric |

- **The legacy skill promoted memos because of what was at stake**, just as the first build did. The
  form rule fixed that, so it goes beyond parity.
- **On these three hard cases, each skill passed one, but not the same one.**
- **A likely structural cause of the remaining over-reviewing:** legacy reviewers read one or two
  reference files, while port reviewers read all four library files.

After round 2, two fixes went in with commit `90979d4`: a buried bottom line ranks first, and the
sourcing trap applies only to numbers whose basis names no study, dataset or issuing body. Round 3
tests that commit.

## Files

| Path | What |
|---|---|
| `cases/*.txt` | The six snippets, exactly as reviewed |
| `gold.json` | Level, expected finding count, planted flaws and control flag per case |
| `round1/*.md` | Round 1 reviews by the first build, exactly as written |
| `round2/new-*.md` | Round 2 reviews by the revised port |
| `round2/legacy-*.md` | Round 2 reviews by the legacy skill (baseline) |
