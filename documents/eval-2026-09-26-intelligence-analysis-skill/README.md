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

## Round 3: 3/6, all six cases against `90979d4`

The same six cases went to fresh agents under the same separation. Each agent was also told to
stay out of this folder.

| Case | Level | Expected | Result |
|---|---|---|---|
| fin-01 | Light | 0–1 | **Pass.** 1 finding, the gold flaw; rated Light because of its form |
| geo-02 | Full | 3–5 | **Pass.** 3 findings; the conflation is now under the gold key's standard. Mirror-imaging was found in substance but not named |
| epi-01 | Medium | 2–3 | **Pass.** Medium, 3 findings; buried bottom line ranked second, behind the missing alternative |
| biz-02 (control) | Medium | 0–1 | **Fail.** Medium, 2 findings |
| epi-02 (control) | Full | 0–1 | **Fail.** 3 findings; the gold flaw was missed |
| clim-02 (control) | Full | 0–1 | **Fail.** 2 findings. Round 1 passed this case |

- **Flawed products 3/3, clean controls 0/3.** The skill finds real weaknesses at the right level,
  and it cannot leave clean work alone.
- **Editing the rule text did not converge.** The sourcing rule caught epi-02's flaw in round 2 and
  missed it here once narrowed. Its "issuing body" exemption was read as covering PAHO. On clim-02,
  the same rule produced a new false positive on an unattributed correlation. Each wording change
  moved the false positives rather than removing them.
- **A defect in the corpus.** The epi-01 snippet gives contact-tracing coverage as 68%, but "289 of
  337" is 86%. The gold key's own reasoning uses the 68% figure. Round 3's epi-01 reviewer found the
  inconsistency, and nobody had noticed it before.

## Round 4: 3/6, library files loaded on need (`56ba045`)

This round tested a structural hypothesis: that over-reviewing came from reading all four library
files before judging. Review mode was changed to load only the router and the standards file up
front, and to open another file only to confirm and name a finding that had already survived the
gates. The six cases re-ran under the same separation.

| Case | Library files read | Result |
|---|---|---|
| fin-01 | 2 | **Pass.** 1 finding, the gold flaw |
| geo-02 | 4 | **Pass.** 3 findings, all gold flaws in substance; mirror-imaging named |
| epi-01 | 4 | **Pass.** Medium, 3 findings; absence of evidence named |
| biz-02 (control) | 3 | **Fail.** 2 findings |
| epi-02 (control) | 3 | **Fail.** 3 findings; the gold flaw was credited as sourcing |
| clim-02 (control) | 2 | **Fail.** 2 findings |

- **The hypothesis is disconfirmed.** Reviewers did load less. The clim-02 reviewer read two files
  and still wrote the same two findings as round 3.
- **Control findings recur across rounds.** Independent reviewers under three versions of the skill
  converged on the same specific issues in the controls:
  - biz-02: the unsourced regulatory comparison with Vietnam, and the small-sample surveys
  - epi-02: anchoring on the prior estimate, the unsourced serotype shift, and the carrying-cost
    assumption
  - clim-02: the unattributed r ≈ 0.61, and likelihood conflated with confidence in the bottom line

  A checklist effect would not produce that consistency. Either the reviewers' threshold for a
  finding sits below the corpus author's, or these controls are less clean than their gold keys
  say. Only a human reading of those recurring findings can settle which.
- **The load-on-need change is kept.** It cost nothing on the flawed cases, it matches the legacy
  skill's own "read as you need them" rule, and reviewers used somewhat less context.

## The gold key was amended after results were seen

After round 4, the owner read the seven findings that had recurred on the three controls, each
with its quoted passage and the case for and against it, and judged **all seven to be real
weaknesses**. The three "clean" controls were not clean, and the gold key undercounted them.
`gold-amended.json` adds those seven flaws, sets the expected finding counts to match, and marks
all three cases as no longer controls. `gold.json` is unchanged.

This amendment is **post hoc**, made after the results were seen. It is recorded here for that
reason. There was one adjudicator, reading findings framed by the agent that ran the eval, so a
second reader would make it sturdier. The recorded grades in the rounds above stay as they were,
against the original key. The grades below are for comparison.

| Case | Amended expectation | Round 3 | Round 4 | Legacy baseline |
|---|---|---|---|---|
| biz-02 | 2–3, two flaws | Pass: both | Pass: both | Pass: 3 findings, both flaws present |
| epi-02 | 3–5, four flaws | Pass: 4 findings, all four flaws; one overreach on the ECMWF score | Pass on count: 3 findings, 3 of 4 flaws; the planted benchmark flaw missed | **Fail**: 1 finding; 3 of 4 flaws missed |
| clim-02 | 2–3, two flaws | Pass: both | Pass: both | not run |

Against the amended key, rounds 3 and 4 each score **6/6**. The legacy skill's one passing
control, epi-02, becomes an under-review: it found the planted flaw and none of the other three.
One genuine weakness in the port survives the amendment. It **missed epi-02's planted
benchmark flaw in three of four rounds**, crediting a number that looks sourced but isn't as
characterized sourcing.

## Round 5: the rebuilt library (2026-10-23)

The intelligence-analysis library was rebuilt on primary sources on 2026-10-16 (library commit
`5097aa0`: ICD 203, the CIA Tradecraft Primer, Heuer, the UK MOD Red Teaming Handbook), and the
review skill took over the calibration and the rating scale (engine `6f62059`, #73). Round 5 tests
both, at engine `61c17d0`. The same six cases went to fresh agents under the same separation: each
saw the skill file, the library and one case file copied outside this folder, and was told to open
no golden set, eval folder or gold key. The `analysis-tools` plugin was not installed on the machine,
so each agent read the skill file and followed it, rather than loading it as a plugin.

| Case | Level | Library files read | Original key | Amended key |
|---|---|---|---|---|
| fin-01 | Light | 3 | **Pass.** 1 finding, the gold flaw | Pass |
| epi-01 | Medium | 3 | **Pass.** 3 findings, all three gold flaws; the 68%/86% corpus defect found again | Pass |
| geo-02 | **Medium** (key: Full) | 5 | **Pass on findings.** 3 findings, all three gold flaws; mirror-imaging named | Pass on findings; level one below the key |
| biz-02 | Medium | 3 | **Fail.** Control, 3 findings | **Pass.** Both flaws |
| epi-02 | Full | 3 | **Fail.** Control, 3 findings | **Pass on count**, 2 of 4 flaws. The planted benchmark flaw was caught ("a figure dressed as sourcing"); anchoring on the prior estimate and the carrying-cost premise were missed, both credited as strengths |
| clim-02 | Full | 3 | **Fail.** Control, 3 findings | **Pass.** Both flaws |

- **No regression from the rebuild.** 3/6 against the original key and 6/6 against the amended key,
  graded as round 4 was, the same as rounds 3 and 4. Every review cited only library files.
- **geo-02 was reviewed one level low**, where rounds 1, 3 and 4 all reviewed it at Full. The reviewer read it as a
  short serialed assessment whose "KEY JUDGMENT" and "CONFIDENCE" headers do not make it a Full
  product, applying the rule that the product's form sets its level. Its findings still matched the
  key. One trial cannot say whether this is a shift or noise.
- **epi-02's flaw coverage keeps moving:** four of four in round 3, three of four in round 4, two of
  four here. The benchmark flaw, missed in three of the first four rounds, was caught.
- **A known gap was reported, not filled.** The epi-01 reviewer said the library does not define
  confidence levels. The library records exactly that as an open question, and the reviewer did not
  supply the legacy definitions from memory.

## Files

| Path | What |
|---|---|
| `cases/*.txt` | The six snippets, exactly as reviewed |
| `gold.json` | Level, expected finding count, planted flaws and control flag per case, as copied from the legacy corpus |
| `gold-amended.json` | The same, plus the seven flaws the owner adjudicated real after round 4 (post hoc) |
| `round1/*.md` | Round 1 reviews by the first build, exactly as written |
| `round2/new-*.md` | Round 2 reviews by the revised port |
| `round2/legacy-*.md` | Round 2 reviews by the legacy skill (baseline) |
| `round3/*.md` | Round 3 reviews at `90979d4` |
| `round4/*.md` | Round 4 reviews at `56ba045` |
| `round5/*.md` | Round 5 reviews against the rebuilt library, engine `61c17d0` |
