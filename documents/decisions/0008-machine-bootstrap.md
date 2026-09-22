# ADR-0008: One command registers the engine on a machine, and git config carries it to hooks

- **Status:** Accepted
- **Date:** 2026-09-22
- **Deciders:** Dandy Taylor
- **Amends:** [0001](0001-kb-root-resolution.md)

## Context and problem statement

Setting a machine up meant hand-editing four things: the `env` block and the marketplace and plugin
entries in `~/.claude/settings.json`, a SessionStart hook copied into `~/.claude/hooks/`, a block in
`~/.bashrc`, and `core.hooksPath` in each repository. Nothing checked that they agreed, and nothing
but memory said what the list was. That is tolerable for the person who built it and a wall for the
second developer, who is the entire point of the exercise.

Worse, one of the four was quietly wrong. `~/.bashrc` exported `KB_ENGINE_ROOT` *below* the stock
guard that returns early for non-interactive shells. Observed 2026-09-21: `bash -ic` saw the
variable; `bash -lc` and `bash -c` did not. A pre-commit hook fired by anything that does not run an
interactive shell — an IDE, a GUI git client, cron — therefore found no engine and **skipped its
checks while exiting 0**. The guardrail was strongest for the developer least likely to need it.

## Considered options

1. **Document the four steps in a contributor guide.** No new code. But a list of manual steps has no
   single source, drifts the first time the engine moves, and cannot be verified.
2. **Move the shell export above the interactivity guard, or into `~/.profile`.** Fixes login shells;
   still nothing for a GUI client that inherits neither, and still four hand-edited places.
3. **A global `core.hooksPath` dispatcher.** One setting for every repository on the machine. It also
   hijacks hooks in every unrelated repository and collides with Husky and the pre-commit framework.
4. **One idempotent command, with git's own config as the hooks' channel.**

## Decision outcome

**Chosen: option 4.** `kb-bootstrap` writes every location from one source — its own path, so the
engine is wherever the script is and there is nothing to type. It merges into existing settings,
backs a file up before its first change, and has a `--check` mode that reports drift and changes
nothing.

**Git hooks resolve the engine through `git config --global kb.engineRoot`, after the environment.**
Git reads its global config in every context that can produce a commit. That is the property no
shell startup file has, and it is why this is not merely a tidier `~/.bashrc`. The shell block
survives for `PATH`, so a human can type `kb-init` — a convenience, not a dependency.

**The SessionStart hook moves into the engine** (`scripts/kb-session-start`). A copy in
`~/.claude/hooks/` is an unversioned fork of a file that describes the contract; in the engine it
travels with the contract it announces. It also stops deriving the engine as `$KB_GENERAL_ROOT/knowledge`
— it is simply the directory it lives in — so `KB_GENERAL_ROOT` is retired.

**Clones are wired by `kb-init`, not from here.** `core.hooksPath` is local config that git does not
clone, so a fresh clone runs no hook at all (observed 2026-09-21: a misnamed, misscoped, unrouted
file committed with exit 0 and no output). A machine-level command cannot wire a repository that has
not been cloned yet, so `kb-init` in an already-initialised project now wires the hook instead of
refusing. The team instruction is two steps: `kb-bootstrap` once per machine, `kb-init` once per
clone.

### Test evidence (2026-09-22)

| Test | Route | Result |
|---|---|---|
| A | `--check` on a throwaway `HOME` | Reports every item as would-set; exit 1; nothing written |
| B | Apply on that `HOME` | settings.json, `.gitconfig` and `.bashrc` written as specified |
| C | `--check` after apply | All ok; exit 0 |
| D | Second apply | No file changed, no backup written — idempotent |
| E | Apply over a copy of a real configured `HOME` | Retires `KB_GENERAL_ROOT`, repoints the hook, rewrites the shell block; unrelated keys, plugins and hook events preserved; both files backed up |
| F | Clone + `kb-init` | `core.hooksPath` set, old hook snippet refreshed to the current one |
| G | **Commit from a non-interactive shell** (`env -i … bash -c`) in that clone | Hook ran and **refused** a bad file (exit 1) — the case that silently passed before |

## Consequences

- One command to run, one to verify, and a second developer's setup is two steps with no list to
  follow.
- `git config --global kb.engineRoot` is now load-bearing. A machine that has it unset gets hooks
  that skip rather than fail — deliberate, since a hook that hard-fails on an unconfigured machine
  blocks work it cannot fix, but it does mean an unbootstrapped clone is unguarded and says so.
- The engine's location lives in four places still; the difference is that one command owns all four
  and `--check` proves they agree.
- Not covered: a GUI git client or IDE has still never been tested against a hook, only reasoned
  about — it is an open question in `claude-code-runtime`, and the git-config channel exists to make
  the answer not matter.
