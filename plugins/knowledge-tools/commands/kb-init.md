---
description: Scaffold a project knowledge tree — knowledge/INDEX.md, plus .claude/ and CLAUDE.md only if absent. Non-destructive and safe to re-run.
argument-hint: "[--name NAME] [DIR]"
allowed-tools: Bash
---

Run the engine's `kb-init` script and report its output verbatim:

```bash
"$KB_ENGINE_ROOT/scripts/kb-init" $ARGUMENTS
```

That is the whole command. The logic lives in the script, not here, because scaffolding a project
tree involves no judgment and therefore needs no model — and because a developer must be able to run
the identical thing from a terminal with no Claude session at all. Two implementations would drift.

If `KB_ENGINE_ROOT` is unset, say so and stop. Do not reconstruct the scaffold by hand: an agent
improvising the steps is exactly what the script exists to replace.

Pass `DIR` when the target is not the current project — the script resolves the enclosing git
repository from wherever it is pointed, so a path anywhere inside the project is enough.
