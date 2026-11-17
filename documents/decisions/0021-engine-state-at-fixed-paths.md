# ADR-0021: The engine keeps its state and config at fixed paths

- **Status:** Accepted
- **Date:** 2026-11-17
- **Deciders:** Dandy Taylor
- **Amends:** [0014](0014-library-registry.md) (extends its "fixed path" rule for the registry to
  every file the engine writes under HOME)
- **Issue:** [#205](https://github.com/dhtaylor/ai-kb/issues/205)

## Context and problem statement

ADR-0008 documents a trap: a variable set only in an interactive shell's startup file is seen by the
terminal and not by a git hook, cron or an IDE, so two parts of one machine disagree about where
something is. ADR-0014 avoided it for the registry (`~/.config/ai-kb/libraries` ignores
`XDG_CONFIG_HOME`) and said why. It did not look at the engine's other files, which followed
`XDG_STATE_HOME` or `XDG_CONFIG_HOME` in six places: packets (`kb-apply`), reports (`kb-report`, and
again in `kb-session-start`'s bash), the schedule's log and lock and its config and unit folder
(`kb-schedule`), and backups (`kb-bootstrap`).

That is the same trap, and it has a victim. With `XDG_CONFIG_HOME` set only in a terminal,
`kb-schedule install` wrote `schedule.conf` under it. The cron or systemd run did not have the
variable, read `~/.config/ai-kb/schedule.conf`, found nothing, and ran with preparation off and
without the PATH install had saved (#165). Nothing failed; the job did less than the person had asked
for. Packets, reports and backups split the same way between a terminal and the session hook or the
schedule: a report written by the schedule was not the one the nudge named.

## Considered options

1. **Keep honouring XDG, and tell people to set it everywhere.** Not something the engine can check,
   and the failure is silent. It is the instruction ADR-0008 retired for `KB_ENGINE_ROOT`.
2. **Honour XDG, and record the resolved path where every reader can find it.** A second file that
   says where the first is. It moves the problem, and adds a file that can disagree with the variable.
3. **Fixed paths, with an explicit override where one is wanted.** **Chosen.**

## Decision outcome

**The engine does not read `XDG_STATE_HOME` or `XDG_CONFIG_HOME`.** Its own files are at:

| What | Where |
|---|---|
| Packets, reports, `schedule.log`, `schedule.lock`, backups | `~/.local/state/ai-kb/` |
| `schedule.conf`, the systemd user unit folder | `~/.config/` (`ai-kb/schedule.conf`, `systemd/user/`) |
| The library registry | `~/.config/ai-kb/libraries` (unchanged, ADR-0014) |

`KB_PACKETS` and `KB_REPORTS` stay. They are explicit, named overrides for one purpose, and a person
who sets one chose it; the trap is a variable that moves many things as a side effect.

**One module reads the environment.** `scripts/kbengine/env.py` declares every variable the engine
reads, with its default and what it changes, and gives the locations as functions. Python readers
call it. `kb-session-start` and `kb-bootstrap` are bash and stay one-liners; a test compares what
they resolve with what `env.py` resolves, so the two cannot drift unseen.

**`CLAUDE_CONFIG_DIR` is honoured** where the engine reads Claude Code's own files
(`kb-telemetry`, `kb-eval-sample`), as `kb-bootstrap` already did. Claude Code owns that variable, and
the engine follows where Claude Code puts its transcripts. `kb-schedule install` saves it in
`schedule.conf`, as it does PATH, and `run` restores it, because a timer does not have it.

**Out of scope: git's own use of `XDG_CONFIG_HOME`.** `kb-bootstrap` looks for `$XDG_CONFIG_HOME/git/config`
only to find the file `git config --global` writes when `~/.gitconfig` is absent. That is git's
convention, and git itself reads the variable in every context where it runs. The engine is
predicting git, not choosing a location.

## Consequences

- A terminal, a git hook, cron and a systemd timer agree about every file the engine writes, with no
  variable to set in the right place.
- **A person who set `XDG_STATE_HOME` or `XDG_CONFIG_HOME` has files the engine no longer reads.**
  Their packets, reports, schedule log and backups under the old state folder, and their
  `schedule.conf` and units under the old config folder, are not found. The CHANGELOG says to move
  them, or to reinstall the schedule. Nothing is deleted.
- A person who wants state elsewhere sets `KB_PACKETS` or `KB_REPORTS` for those two, or links
  `~/.local/state/ai-kb` to where they want it. Backups, the log and the lock have no override.
- A variable the engine reads is added in one place, and the test suite can clear the declared list
  instead of learning each one from the bug that it caused.

## Review trigger

Revisit if a platform where `~/.local/state` is wrong for a user (not Linux, macOS or WSL) needs the
engine.
