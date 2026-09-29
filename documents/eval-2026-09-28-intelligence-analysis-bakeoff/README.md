# Bake-off — new `intelligence-analysis` skill against the legacy skill, 2026-09-26 to 2026-09-28

Evidence, not knowledge: nothing here is routed, and nothing here is a fact. It records how the
thin `analysis-tools` skill was compared, head to head, with the legacy skill it would replace, so
the result can be re-examined rather than taken on a paragraph in the plan (§9.17).

The tuning rounds that came before this are archived separately, in
`documents/eval-2026-09-26-intelligence-analysis-skill/`.

## Protocol

- **Corpus:** the legacy skill's graded corpus of 22 cases (`/mnt/c/workspace`, a separate
  repository). Six of those cases were used for tuning, which leaves 16 held out. Round 1 drew 10
  of the 16 by a seeded random draw, stratified by level (2 Light, 5 Medium, 3 Full), with the one
  clean control in the held-out set forced in. Rounds 2 and 3 used the remaining 6.
- **Reviewers:** a fresh agent for each review, which saw only its own skill and its one case file.
  The new skill's reviewers could not read the legacy corpus or any eval archive. The legacy
  skill's reviewers could not read its `evals/` folder, and could not create a coaching log. Every
  reviewer listed the files it opened.
- **Blinding:** `scripts/blind.py` relabelled each pair of reviews as A and B, in a seeded random
  order recorded in `ab-mapping.json`. It removed the tells that identify a skill: `Sources:` lines,
  file names and mentions of the library. Differences in style remained, and no judge said it
  could tell the two reviews apart.
- **Judges:** one fresh agent per case. Each read the product, the gold key and the two blinded
  reviews. It scored each review on level, planted flaws caught, extra findings (each ruled real or
  a nitpick), finding count, fix quality and overall usefulness, then picked a winner.
  `scripts/tally.py` unblinds and totals the verdicts, and re-running it reproduces the figures
  below.
- **Trials:** one review per skill per case and one judge per case. These results show direction,
  not frequency.

## Round 1 — bake-off, 10 held-out cases, new skill at `56ba045`: legacy wins 6–3–1

| | New | Legacy |
|---|---|---|
| Wins | 3 | **6** (1 tie) |
| Mean judge score | 6.9 | **7.4** |
| Planted flaws caught | 17 of 19 | **19 of 19** |
| Right level | 4 of 10 | **5 of 10** |
| Extra findings, real / nitpick | 6 / 9 | 7 / 7 |

The new skill lost mainly on level. Forms that no level list named fell through to the
"consequential or externally read" clause and were promoted to Full. A three-sentence email and a
board memo were also mis-levelled.

## Round 2 — the level fix alone, the 6 remaining held-out cases, new skill at `cc3865a`

The fix: a form no list names now defaults to Medium, and a short message is Light. Only the new
skill ran in this round, graded by hand against the gold key. It rated the level right on **4 of
6**, caught 11 of 13 planted flaws, and had 4 of 6 finding counts in range. Both level misses had
one cause. A case note headed "CASE ASSESSMENT" and a briefing headed "INTELLIGENCE BRIEFING" were
promoted to Full because the exception keyed on the title. `2-fresh-six/new/` holds those reviews.

## Round 3 — head-to-head on the same 6 cases, new skill at `d914718`: new wins 4–2

Between rounds 2 and 3, one rule was added: a title does not set the level, what the document is
does.

| | New | Legacy |
|---|---|---|
| Wins | **4** | 2 |
| Mean judge score | **8.2** | 7.5 |
| Planted flaws caught | **13 of 13** | 11 of 13 |
| Finding count in range | **6 of 6** | 4 of 6 |
| Right level | 4 of 6 | 4 of 6, the same two misses |
| Fix quality (of 30) | 27 | 26 |
| Extra findings, real / nitpick | 4 / 2 | 8 / 3 |

- **The title rule did not work.** Both of the cases it targeted, foren-01 and geo-03, stayed at
  Full under both skills. The reviewers argued around the wording: one read a "99.99%" statistic as
  a stated confidence. On level, the two skills are now identical, and both miss at the same
  boundary, which the gold key places at Medium.
- **The new skill won on coverage and proportion.** The legacy skill missed a planted flaw that the
  new skill caught on geo-03 and on sport-02. The legacy skill found more real extras, but they
  pushed its finding counts past the key's range.

## What this shows and what it doesn't

The fixes made between rounds 1 and 3 moved the new skill from behind to ahead. The two rounds used
different cases and different versions of the skill, so they don't pool into one score. Across all
16 cases the raw tally is 7 wins to 8, with 1 tie, split across those two versions.

Two biases run in opposite directions:

- **The legacy skill has home advantage.** It was built and tuned against this corpus, and its
  instructions name the corpus's own trap cases.
- **The new skill was also tuned.** The round-3 wording was written after seeing two of round 3's
  cases. Without those two cases, the new skill won 3 of the remaining 4.

A test with no home advantage on either side needs fresh cases that neither skill has seen.

## Run integrity

During round 3 the safety classifier was unavailable while six of the reviewer agents ran. Before
judging, a sweep checked for files changed since setup outside the review folders. It found no
changes in either repository and no coaching log. Everything else it found was accounted for: the
two scripts and the session's own housekeeping files. In round 2, one reviewer listed a
scratchpad folder, which showed file names, including `gold.json`, and no file contents. It
reported this itself. The run was counted, since a file name gives away no answer, and round 3's
reviewers were barred from listing folders at all.

## Files

| Path | What |
|---|---|
| `1-bakeoff/`, `3-head-to-head/` | For each round: `cases/`, `gold.json`, `new/` and `legacy/` reviews exactly as written, `ab-mapping.json` (the A/B key), `verdicts/` (the judges' JSON) |
| `2-fresh-six/` | `cases/`, `gold.json`, and the new skill's reviews at `cc3865a` |
| `scripts/blind.py`, `scripts/tally.py` | Blinding and unblinding/tally; run with a round folder as the argument |
