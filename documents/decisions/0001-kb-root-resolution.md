# ADR-0001: Knowledge base root resolution

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Phase:** 0 (guardrails) — this ADR records the Phase 0 acceptance test outcome

## Context and problem statement

The architecture places knowledge in three homes: a general tier shared across projects, a repo tier
travelling with each project, and personal knowledge in user config. Agents must resolve the general tier
without any file containing a literal absolute path, since such a path is correct on exactly one machine
and fails silently everywhere else.

The combination plan flagged this as a **Critical unverified assumption**: it was not established that a
shell environment variable is inherited by an agent's execution context. If it is not, every path resolves
to nothing and agents fall back to model memory — violating the retrieval contract with no error. The plan
required an acceptance test before any agent file is written.

## Decision drivers

- A running agent must demonstrably read a file under the configured root.
- The root is a **trust root**: whoever can write it can repoint every agent at attacker-controlled
  "knowledge" that is then cited as canonical.
- Failure must be loud. A silent fallback to model memory is the worst outcome.
- No literal KB path in any agent, command, or knowledge file.

## Considered options

1. **Shell environment variable via `~/.bashrc`** — conventional, but untested here.
2. **User-level settings entry** (`~/.claude/settings.json` `env`) — the plan's named fallback.
3. **Project-level settings entry** — travels with the repo.
4. **SessionStart hook injecting the resolved path** — the plan's other named fallback.

> **Amended 2026-09-22 by [0008-machine-bootstrap](0008-machine-bootstrap.md).** The mechanism below
> still holds for Claude sessions, with two changes: the variable is `KB_ENGINE_ROOT` (the engine is no
> longer assumed to be `<root>/knowledge`), and the hook script lives in the engine as
> `scripts/kb-session-start` rather than in `~/.claude/hooks/`. Git hooks, which this ADR did not
> consider, resolve the engine through `git config --global kb.engineRoot`, and `kb-bootstrap` writes
> every location from one source.

## Decision outcome

**Chosen: option 2 combined with option 4.** `KB_GENERAL_ROOT` is defined in user-level settings; a
SessionStart hook (`~/.claude/hooks/kb-root.sh`) resolves it and injects the **absolute path** into session
context. Agents consume the resolved path and never handle the variable themselves.

### Test evidence (2026-09-19)

| Test | Route | Result |
|---|---|---|
| A | Inline `export` in a tool call | **Fail** — each call is a new PID; nothing persists |
| B | `~/.bashrc` | **Fail mid-session** — the shell snapshot is taken at session start; needs a restart |
| C | `~/.claude/settings.json` `env` | **Pass** — applied immediately without restart, resolved a real KB file |
| D | Sub-agent reading via the variable (Bash) | **Pass** — independently verified against pre-computed ground truth: sha256 `b89315a05f7a290dbbf5ef8858c220ff7bc18299c7dc9a4286ddb2a4d75eba3d`, 308 lines, matching frontmatter and section title |
| E | Sub-agent reading via the variable (Read tool) | **Fail** — the Read tool does not expand environment variables |
| F | Hook firing at a real session start (2026-09-19, after restart) | **Pass** — the resolved root arrived in session context verbatim; the variable and `core.hooksPath` both survived the restart |

Test E is why the hook is required rather than optional. Given the literal string
`$KB_GENERAL_ROOT/knowledge/CONVENTIONS.md`, the Read tool returns *"File does not exist. Note: your
current working directory is /mnt/c/workspaces/ws_v1."* — an error that invites a relative-path retry which
would succeed by coincidence in this workspace and break on any machine with a different working directory.
That is the same silent-failure class the acceptance test existed to rule out, merely relocated from the
variable to the tool.

### Why user-level rather than project-level

Option 3 was rejected on trust-root grounds. A project file can be overwritten by the repo it lives in, so
a compromised or careless project could repoint the canonical knowledge every agent cites. User-level
settings sit outside any repo's reach.

## Consequences

**Good.** The acceptance criterion is met and evidenced. No file contains a literal KB path. Absence is
graceful and loud: an unset variable, or one pointing at a directory with no `knowledge/`, produces a
session-start warning and an instruction to report the root as unconfigured rather than guess.

**Bad.** The mechanism is Claude Code specific — settings `env` plus a SessionStart hook. Another agent
runtime would need its own equivalent, and this ADR would need revisiting.

**Neutral.** Adds two machine-level artifacts outside version control: the settings entry and the hook
script. Neither is in a repo, so neither is reviewed, and a new machine needs both. That makes them a
**bootstrap requirement** — the one-command setup named in the plan must create both, and until that
bootstrap exists, a new machine is configured by hand.

## Open items this does not settle

- The **commit-SHA divergence warning** for the general root (a plan hardening item) is not implemented.
- The **bootstrap command** that provisions the settings entry and hook on a new machine does not exist.
- ~~The hook has not been observed firing at a real session start.~~ **Closed 2026-09-19**: after a session
  restart the hook fired and injected the resolved root into context (test F). All three of its branches
  were pipe-tested for valid JSON; the configured branch is now confirmed end to end. The two failure
  branches — variable unset, and variable pointing somewhere without a `knowledge/` directory — remain
  verified only by pipe test, since neither has occurred in a real session.
