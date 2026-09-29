# Tool-scope matrix

Phase 4 step 1 (§6). Every file in the behaviour layer (`plugins/*/agents/*.md`,
`plugins/*/commands/*.md`, `plugins/*/skills/*/SKILL.md`) now declares a tool-scope field and a
`tier:`. This is the matrix that justifies each one, and what `scripts/check-tool-scope` checks
against it.

## What the scope fields actually enforce

Checked against `kb/claude-code-runtime` first — it does not cover this — then
code.claude.com/docs/en/sub-agents and code.claude.com/docs/en/skills:

- **A subagent's `tools:`** (`plugins/*/agents/*.md`) is a **real allowlist**. Per the docs: *"To
  restrict tools, use the `tools` field as an allowlist... The subagent can't edit files, write
  files, or use any MCP tools"* when they are omitted. This is the one field here that actually
  restricts what the file can do.
- **A skill's or command's `allowed-tools:`** (`plugins/*/skills/*/SKILL.md`,
  `plugins/*/commands/*.md` — commands are skills under the hood, per the docs) **only
  pre-approves**. Per the docs: *"It does not restrict which tools are available: every tool
  remains callable, and your permission settings still govern tools that are not listed."* It
  grants the listed tools for the turn that invokes the skill, skipping a permission prompt; the
  grant clears on the next message. A skill or command can call any tool the session already
  permits, declared or not.

So for the five `kb-*` maintenance skills and `intelligence-analysis`, `allowed-tools:` is a
**declaration of intent that the runtime does not enforce** — not least-privilege in the sense §5A
means it (the architecture names the *service account* as the primary control, and this
environment has none to name: no deploy target, no live system, nothing to authenticate against
beyond this checkout). `scripts/check-tool-scope` checks that the declaration exists, is
well-formed, and agrees with a stated tier. It cannot check that a skill is incapable of calling an
undeclared tool, because nothing in the runtime makes that true for a skill or a command — only
`tools:` on a subagent does.

## The matrix

| File | Type | Tier | Declared tools | Why these and no more |
|---|---|---|---|---|
| `plugins/knowledge-tools/agents/kb-retrieve.md` | agent | retrieval | `Read, Grep, Glob` | Loads INDEX files, descends, greps for slugs and golden-set exclusions. Never writes — curation is "a separate job with separate skills and a human in the loop" (its own body). Enforced: real restriction. |
| `plugins/knowledge-tools/commands/kb-capture.md` | command | curation | `Bash, Write` | `Write`s the episodic-note body to a temp file, then `Bash`es the engine's `kb-capture` script, which does the filing. No `Read` in its procedure; no `Edit` (it only ever creates a new note). |
| `plugins/knowledge-tools/commands/kb-init.md` | command | curation | `Bash` | Runs the engine's `kb-init` script and reports its output verbatim — "the logic lives in the script, not here." No `Write`: the script does the writing, not the command. |
| `plugins/knowledge-tools/skills/kb-audit/SKILL.md` | skill | curation | `Read, Grep, Glob, Bash, Write, Edit` | Runs `check-kb`/`check-scope`/`check-golden`/`check-xlinks`/`kb-owner` and computes stable IDs with `sha1sum` (`Bash`); reads and greps library content to find rot the scripts can't see (`Read, Grep, Glob`); creates `needs-attention.md` when there are findings (`Write`); adds its router line and sets `last_swept:` in the library's own `INDEX.md` (`Edit`). Its own rule is "detects, never fixes" *facts* — the queue file and the `last_swept:` stamp are bookkeeping about the sweep, not mutation of knowledge, but they are still a `Write`/`Edit` a tool-scope lint has to account for. |
| `plugins/knowledge-tools/skills/kb-create-domain/SKILL.md` | skill | curation | `Read, Grep, Glob, Bash, Write` | `Bash` for `mkdir`, `git init`, `chmod`, `git config`, `git add`, `git ls-files -s`, and copying the guardrails workflow; `Write` for `INDEX.md`, the pre-commit hook, `CODEOWNERS`, source stubs, domain files and the golden set; `Read`/`Grep`/`Glob` to load the contract and check for domain/slug collisions. No `Edit`: everything it touches is new — the domain does not exist yet by definition. |
| `plugins/knowledge-tools/skills/kb-distill/SKILL.md` | skill | curation | `Read, Grep, Glob, Bash, Write, Edit` | `Read`/`Grep`/`Glob` the episodic note and the target domain; `Edit` existing domain files to enrich or flag them, extend the golden set, and mark the episodic note as distilled; `Write` for a domain's first topic file or `open-questions.md` when neither exists yet; `Bash` to run `check-kb`. |
| `plugins/knowledge-tools/skills/kb-organize-domain/SKILL.md` | skill | curation | `Read, Grep, Glob, Bash, Write, Edit` | `Read`/`Grep`/`Glob` to diagnose and to search every installed library for a stale slug; `Bash` for the file moves themselves and for `check-kb`/`check-golden`/`check-xlinks`/`check-scope`; `Write` for a new file produced by a split; `Edit` for routers, the golden set and merged files. |
| `plugins/knowledge-tools/skills/kb-update-domain/SKILL.md` | skill | curation | `Read, Grep, Glob, Bash, Write, Edit` | `Write` for the source stub, a new `contradictions.md`, or a golden set seeded for the first time; `Edit` for the domain file(s) being folded into and an existing golden set; `Read`/`Grep`/`Glob` for the source material and the target domain; `Bash` for `check-kb`/`check-scope`/`check-golden`/`check-xlinks`. |
| `plugins/analysis-tools/skills/intelligence-analysis/SKILL.md` | skill | analysis | `Read, Grep, Glob, Write` | `Read`/`Grep`/`Glob` retrieve tradecraft from the `intelligence-analysis` library, load-on-need. `Write` is for exactly one file, `~/.claude/ia-coaching-log.md`, "a user-level file outside every repository" — no `Edit`, since the skill's own template shows it rewriting the log's sections wholesale rather than patching them, and no `Bash`. Confining the `Write` to that one path is the skill body's job; this lint can only see that the tool is declared, per the honesty note above. |

Every file's tier matches the base tools its own tier line prescribes, so none needed tightening —
none of the nine declared a tool beyond what its actual procedure calls for going in.
