---
description: Scaffold a project knowledge tree — creates knowledge/INDEX.md, and .claude/ and CLAUDE.md only if they are absent. Non-destructive and safe to re-run.
argument-hint: "[project-name] (defaults to the directory name)"
allowed-tools: Read, Write, Edit, Bash, Glob
---

# kb-init

Stand up a **project** knowledge tree in the current project, in seconds, with no decisions to make.

This is a command rather than a skill because there is no judgment in it. Every question
`create-domain` asks has exactly one answer for a project tree: the tier is `repo:<project>` because
it is a project, the location is `knowledge/` because that is where the contract puts it, the
horizon is the deployment band because deployment facts are the most volatile, and the golden set is
deferred because there is no content yet. A procedure with no judgment is a command.

**Standing up a shared library is a different act** — there the tier, the name and the horizon are
genuinely open, and that is `create-domain`.

## The governing rule: create what is missing, touch nothing that exists

Most projects already have a `CLAUDE.md` and a `.claude/`. **Never overwrite either.** A tool that is
destructive on its second run is a tool nobody runs twice. Every step below is conditional, and the
report says what was created versus what was left alone.

## Step 1 — Locate the project and name it

The project root is the repository root (`git rev-parse --show-toplevel`), not the current
directory — running this from a subdirectory must still scaffold at the top.

If it is not a git repository, say so and continue: the tree still works, but the guardrail wiring in
step 5 has nothing to attach to, and you must say that rather than pretend it succeeded.

The project name is `$ARGUMENTS` if given, else the repository directory's name, **transformed to
kebab-case** — lowercase, non-alphanumerics to hyphens, runs collapsed (`Alpha_Service` →
`alpha-service`). It becomes the `repo:<name>` scope and a slug, so this is a transformation you
perform, not a request to the invoker.

## Step 2 — Refuse if a tree is already there

If `knowledge/` exists but has **no `INDEX.md`**, that is not an initialised tree — it is an
unrouted directory. Create the router (step 3), say that you did and that the existing contents are
unrouted, and recommend `meditate`, which reports orphans.

If `knowledge/INDEX.md` exists, **stop**. The project is already initialised, and re-scaffolding
would overwrite a router that may list real content. Report what is there and exit — adding a domain
to an existing tree is `update-domain`'s job, not this one.

## Step 3 — Create `knowledge/INDEX.md`

Only this one file. No `sources/`, no `episodic/`, no golden set: the contract forbids empty state
leaves and routing to empty folders, and each appears the moment it holds something.

```yaml
---
name: <project>-index
description: <one line — what this project's knowledge covers>
memory_type: reference
domain: <project>
scope: repo:<project>
freshness_horizon: 14d
verifier_budget: 5
metadata:
  type: index
  node_type: router
  created: <today>
tags: [<project>]
keywords: [<project>, deployment, operations, known issues]
---
```

The `description` says what this tree is **for**, not what it contains — "operational knowledge
specific to the <project> deployment" is right for an empty tree and stays right once it fills. That
is not inventing a fact; describing an empty shelf is not describing books.

`freshness_horizon: 14d` sits in the deployment band (7–30d). Deployment facts change without
announcement and are load-bearing when wrong, which is the whole reason that band is the shortest.

The body states what the tree is for, that it is empty, and that facts true beyond this deployment
belong in a shared library rather than here.

## Step 4 — `.claude/` and `CLAUDE.md`, only if absent

- **`.claude/`** — create the directory if it does not exist. Do not put skills, agents or commands
  in it: curation and capture behaviour comes from the engine plugin, registered once per machine.
  Copying it here would create one drifting copy per project, which is the failure the architecture
  exists to prevent, applied to behaviour instead of facts.
- **`CLAUDE.md`** — if absent, create it with the stanza below. If present, **append** the stanza,
  and only when it is not already there. Never rewrite a line you did not add.

```markdown
## Knowledge base

This project has a knowledge tree at `knowledge/`, scoped `repo:<project>`.

Facts true **only of this deployment** go here — topology, deploy quirks, this system's known bugs,
operational gotchas. Anything true wherever a product or concept appears belongs in a shared domain
library, not here; putting it here makes N copies that drift.

Curation and capture come from the `knowledge-tools` plugin, registered once per machine. If it is
not installed, say so rather than editing the tree by hand.
```

That stanza is also how a session **discovers** this tree: `CLAUDE.md` is read from the project root
at session start, so the project announces its own knowledge without any hook, scan or configuration.

## Step 5 — Wire the guardrails, if there is a hook to wire

**Find an existing hook in this order**, and append to the first one you find:

1. `git config core.hooksPath` is set and a `pre-commit` exists there — that is the project's choice;
2. `.githooks/pre-commit` exists — the same convention, not yet activated; activate it;
3. `.git/hooks/pre-commit` exists as a real file (not a `.sample`).

If the project uses **Husky** (`.husky/`) or the **pre-commit framework**
(`.pre-commit-config.yaml`), do **not** hand-edit their hooks. Say which you found and print the
snippet for the user to add through that tool. Fighting another hook manager is how both break.

**If there is no hook at all, create `.githooks/pre-commit` and set `core.hooksPath .githooks`.**
Not `.git/hooks/` — **git does not track it**, so a hook written there dies at the next clone and no
teammate ever gets it, which for a shared project is the same as having written no guardrail. Then
`chmod +x` it and **confirm git recorded `100755` <!-- lint-allow: a git file mode, not an embedded fact --> (`git ls-files -s .githooks/pre-commit`); on a
filesystem where `core.fileMode` is false git records 644 and then **skips the hook silently**. Fix
with `git update-index --chmod=+x`. That bug has occurred three times in this system.

Either way the hook must **degrade gracefully**: the engine lives elsewhere and may not be installed,
and a guardrail that fails a commit because a *different* repository is absent is worse than none.

```bash
ENGINE="${KB_ENGINE_ROOT:-}"
if [ -n "$ENGINE" ] && [ -x "$ENGINE/scripts/check-kb" ]; then
  "$ENGINE/scripts/check-kb" knowledge && "$ENGINE/scripts/check-scope" knowledge || exit 1
else
  echo "knowledge: engine not found — structural checks skipped"
fi
```

## Step 6 — Report exactly what happened

List every path, marked **created** or **already existed, left alone**. Then say plainly what to do
next: capture findings as they happen, and distil them periodically — the tree fills from real work,
not from an upfront sitting.

## Refusals

- `knowledge/INDEX.md` already exists — the project is initialised; say so and stop.
- You would have to overwrite a `CLAUDE.md` line you did not write, or replace anything under
  `.claude/`. Append or skip; never clobber.
- You would have to invent facts to fill the tree. **An empty, well-formed tree is the correct
  outcome** — it fills as the project is built, and a tree seeded with plausible guesses is worse
  than an empty one.
