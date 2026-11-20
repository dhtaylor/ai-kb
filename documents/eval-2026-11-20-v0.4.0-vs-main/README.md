# Release comparison — v0.4.0 against main (f556a32). 2026-11-20

Evidence, not knowledge. This run compares the v0.4.0 release with `main` at f556a32, the candidate
for the next release, before the 2026-11-28 freeze. It measures four things: correctness, retrieval,
maintenance and the upgrade path. The question it answers is whether anything regressed and what a
v0.4.0 user will see change.

## What changed, by surface

- **Retrieval prompts are unchanged.** The `kb-ask` skill and the `kb-retrieve` agent are
  byte-identical between the two. The scripts on the retrieval path did change: `kb-session-start`,
  `kb-catalog` and `kb-libraries` (#210).
- **The contract is unchanged at 2.6.** `CONVENTIONS.md` changed in prose only (#212).
- **Five maintenance skills changed wording:** library paths, and running `check-golden` at the
  gate.
- **Most of the change is in `scripts/` and `scripts/kbengine/`:** 56 files in all.

## Setup

- **Engines.** Two worktrees, one at `v0.4.0` (a318c28) and one at f556a32. A third took main's code
  with v0.4.0's `tests/` checked out over it.
- **Libraries.**
  - Retrieval read the six real libraries through the real registry. That is read-only, and both
    arms read the same commits (agile 5a2da32, ai-writing e6a0476, azure-devops 9c70057, ccr 7b8cdc2,
    intel 5e10b4f, knowledge-architecture 1358df0).
  - Maintenance ran on per-version clones of those commits on ext4, with pushes disabled, under a
    sandbox `HOME` for each version.
  - The real registry and `schedule.conf` were sha256-checked before and after.
- **Isolation.**
  - Each `claude -p` run loaded no user settings (`--setting-sources project,local`).
  - Each run took the version's own SessionStart and SubagentStart hooks, exactly as `kb-bootstrap`
    registers them, plus the version's plugin through `--plugin-dir`.
  - `kb-prepare` ran through a `KB_CLAUDE` wrapper that adds the same isolation.
- **Model.** `claude -p --model sonnet`, Claude Code 2.1.329.

## A. Correctness

| Suite | Result | Wall |
|---|---|---|
| v0.4.0 tests on v0.4.0 | 918/918 | 77 s |
| main tests on main | 1060/1060 | 101 s |
| v0.4.0 tests on main's code | 886/918 | 86 s |

All 32 cross-run failures were classified in `cross-run-classification.md`:

- **31 are fixture artifacts.** The old fixtures copy single scripts without `scripts/kbengine/`.
  With only that added, the cross-run passes 917/918.
- **1 is intended (#203).** `kb-due` now gives its recheck count without `check-kb`.
- **None are unintended.**

One user-reachable effect follows from the fixtures: see finding 2.

## B. Retrieval (control)

- **Cases.** The 24 cases of the 2026-11-05 subsample (`../eval-2026-11-05-triage-specialists/key.json`),
  all positive. The golden indices were re-checked against that run.
- **Runs.** Each case ran through `kb-ask`, two trials per version: 96 fresh sessions, with the two
  versions of a case run side by side.
- **Grading.** `grade-routing` graded the main transcript joined with its subagents' transcripts.
  `grade-eval --transcripts` graded agent grounding, and `grade-eval` graded the delivered answer.
- **Tokens.** Input + cache creation + output, each message counted once. Raw data is in `runs.tsv`.

| Version | Routing | Agent grounding | Delivered grounding | Tokens/question | Cost/question | Wall (median) | Session time (median) |
|---|---|---|---|---|---|---|---|
| v0.4.0 | 40/48 | 46/48 | 46/48 | 22.6k | $0.103 | 24.0 s | 13.0 s |
| main | 44/48 | 45/48 | 45/48 | 22.5k | $0.102 | 15.6 s | 12.9 s |

Both versions read 1.00 specialists per question. Reads are 3.8 per question on v0.4.0 and 4.0 on
main, and no run strayed into another library.

### Misses, case by case

- **Missed on both versions** (miss runs shown as v0.4.0, then main):

  | Case | Grader | v0.4.0 | main | Cause |
  |---|---|---|---|---|
  | ai-writing-signals Q17 | routing | 2/2 | 2/2 | expected file never read |
  | ccr Q21 | routing | 2/2 | 1/2 | |
  | knowledge-architecture Q16 | routing | 2/2 | 1/2 | |

- **Missed on v0.4.0 only:** azure-devops Q1, routing, 2/2.
- **Missed on main only:** ccr Q13, agent and delivered grounding, 2/2.
  - Routing passed and the right file is cited.
  - The answer quotes the excerpt's final clause but drops its first half, so the exact-excerpt
    check fails.
  - The prompts and the library are identical across the two arms, so no engine change accounts for
    it. It is recorded as a phrasing miss, not a regression. A rerun should check that it stays at
    two in two.

### Time to first answer

- The sessions take the same time (13.0 s and 12.9 s). The 8.4 s gap in wall time is all startup.
- On the real libraries on `/mnt/c`, v0.4.0's SessionStart hook took **7.0–9.7 s**; main's took
  0.54–0.56 s, three runs each.
- The hook's timeout is 10 s. On v0.4.0, a slower disk or one more library would kill the hook, and
  the session would start without the engine context.
- Main removes that risk (#210, the in-process registry).
- The `--subagent` hook is 0.20 s on v0.4.0 and 0.17 s on main.

## C. Maintenance

### Same snapshots, every script

All 37 commands give the same exit codes on both versions. These are the differences in output, and
every one is intended:

| Output | v0.4.0 | main | Issue |
|---|---|---|---|
| Nudge, rechecks due (ai-writing-signals / azure-devops) | 5 / 5 | 35, "5 a run" / 15, "5 a run" | #211 |
| Nudge, "sweep due" where a kb-audit packet is pending | shown (4 items) | hidden | #204 |
| `kb-verify`, knowledge-architecture stamped sections | 112 | 100 (12 were in the open-questions record) | #201 |
| `kb-verify`, WEAK warning on "Versions 2.4 to 2.6" | shown | not judged (it greps a local script's output) | #185 |
| `kb-report` | — | identical apart from its timestamp | — |

### Script wall-clock

10 runs each, the two versions interleaved, on ext4. Raw times are in `script-timing.txt`.

| Script | v0.4.0 median | main median | Change |
|---|---|---|---|
| `kb-report` | 0.514 s | 0.139 s | −73% |
| `kb-due --nudge --summary` | 0.226 s | 0.114 s | −50% |
| `kb-session-start` | 0.404 s | 0.274 s | −32% |
| `kb-catalog` | 0.069 s | 0.055 s | −21% |

### `kb-verify --yes --all`

- Every library gives the same result on both versions, except knowledge-architecture.
- There, main fails one Recheck: "The request timeout" in `agent-lifecycle-roles.md`. See finding 1.

### `kb-prepare audit`, headless, $1 cap

One run per library on four libraries: agile-requirements, ai-writing-signals, azure-devops and
intelligence-analysis.

| Version | Total cost | Wall per library | Packets |
|---|---|---|---|
| v0.4.0 | $2.06 | 70–118 s | 4 |
| main | $1.80 | 64–106 s | 4 |

- The Step 1 check results in the packets match on both versions.
- What the model proposed varied. For intelligence-analysis, v0.4.0 proposed nothing; main proposed
  six unstamped-fact records for the open-questions file.
- With one run per library, neither difference is attributed to the version.

## D. Upgrade path (ADR-0021)

The scenario ran in a sandbox `HOME` with `XDG_CONFIG_HOME` and `XDG_STATE_HOME` set, and with
`systemctl` stubbed:

1. v0.4.0 installs `kb-schedule`, writes a report and holds a packet, all under the XDG folders.
2. After the switch to main, with nothing moved, the packet is gone from the nudge and from
   `kb-apply list`, and `kb-schedule status` says "not installed". That is the symptom the CHANGELOG
   describes.
3. The CHANGELOG's steps, followed word for word, bring everything back: the packet in `kb-apply`,
   the report found by session start, the schedule installed. Nothing is deleted.

The registry was already at a fixed path in v0.4.0, so the steps do not need to mention it. See
finding 3.

## Findings

1. **A Recheck in knowledge-architecture no longer runs on main.**
   - "The request timeout" in `agent-lifecycle-roles.md` loads `kb-sources` with `python3 -I`, so
     its `from kbengine import …` fails with `ModuleNotFoundError`.
   - The behavior the fact describes is unchanged. The assertion is what broke.
   - Left alone, the weekly job will queue a false failure. The fix belongs in the library's
     pre-release fold.
2. **A script copied out of the engine on its own now fails at import.**
   - In v0.4.0, `kb-due` copied alone still ran, with the `check-kb` counts missing. On main it stops
     with `ModuleNotFoundError: No module named 'kbengine'`.
   - The same goes for every script that imports `kbengine`. A symlink to the script in the engine
     still works.
   - Nothing in the README or the CHANGELOG says `scripts/kbengine/` must travel with the scripts.
     The release notes should say so.
3. **The ADR-0021 steps leave the old files behind.** `schedule.conf` and the systemd units stay
   under `$XDG_CONFIG_HOME`. With the engine path unchanged they are identical copies, so they do no
   harm, but the release notes could say they may be deleted.

## Versioning

- **Engine.** ADR-0015 makes this a minor bump while the major is 0. Every behavior change a v0.4.0
  user will see is listed above, and all of them are intended.
- **Contract.** It stays at 2.6. ADR-0016 reserves a contract major for a change in what existing
  library content means, and nothing here changes that.

## Cost

$14.16 in all:

| Part | Cost |
|---|---|
| Retrieval, 96 runs | $9.84 |
| Smoke tests | $0.46 |
| Headless preparation | $3.86 |

The first 48 trial-2 runs hit a usage limit and were run again in full. The 24 runs of each trial
were graded together.
