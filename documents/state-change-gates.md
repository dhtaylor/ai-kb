# State-change gates

Phase 4 step 2 (§6). Every entry point in `scripts/`, `plugins/*/commands/` and `plugins/*/skills/`
that changes state, classified against the plan's three bands (§5A, "automate detection, gate
mutation") and checked against what actually gates it today.

## The table

| Entry point | Type | What it changes | Band | Runs non-interactively? | Gate |
|---|---|---|---|---|---|
| `scripts/kb-bootstrap` | script | `~/.claude/settings.json`, `git config --global kb.engineRoot`, a shell rc block, `core.hooksPath` in each installed library — all **outside this repository** | automated-with-approval | No — run once per machine, by a human | **Fixed this pass.** Was apply-by-default with a `--check`/`--dry-run` opt-out — the wrong way round for the highest-blast-radius script here. Now defaults to report-only (prints the plan, exits 1 if anything would change); `--apply` is required to write. `--check`/`--dry-run` remain as an explicit spelling of the default. |
| `scripts/kb-verify` | script | Runs each stale section's `Recheck:` shell command; with `--apply`, rewrites a passed section's `Verified:` stamp; **(Phase 5) a FAILED assertion writes a finding to the owning library's `needs-attention.md` queue** | mutation gated by `--yes`/`--apply`; the queue write itself is fully automated (detection) | Could be scheduled (Phase 5); a scheduled run should pass neither flag, which is exactly the safe default | **Already gated** (existing house model): `--yes` to run the printed commands, `--apply` to restamp a pass. A failure is never applied to the fact, with or without `--apply`. Had no regression test for the `--yes` gate itself — added one this pass. **The queue write added this pass needs no gate of its own**, for the same reason `kb-audit`'s row below needs none: it is detection output, not a fact edit — rule 2 (a failure is never applied) still holds because the finding lands in a queue file, never in the fact. It reuses `kb-watch`'s queue (same file, frontmatter, escaping, dedupe-by-id, imported as a module rather than re-specified) and is gated only by the same `--yes` that already gates running the assertion at all — there is nothing left for a separate flag to opt out of. |
| `scripts/kb-capture` | script | Creates one new file under `<tree>/episodic/`; appends one line to `episodic/INDEX.md` (creating it if absent) and one router line to the tree's own `INDEX.md` (only if missing) | mutation, but additive-only | No | **None — justified.** Every write either creates a brand-new, uniquely-suffixed file or appends to a file it may itself have just created; it never overwrites or deletes anything that existed before the run. Reversible with a single `git checkout` of the tree. |
| `scripts/kb-init` | script | Creates `knowledge/INDEX.md`, `.claude/`, a `CLAUDE.md` stanza, a pre-commit hook (or appends its own marked block to one that exists), `core.hooksPath` | non-destructive idempotent scaffolding | No | **None — justified** (and the skill's own description says so: "Non-destructive and safe to re-run"). Governing rule stated in the script itself: "create what is missing, touch nothing that exists." Every path is create-if-absent or append-to-its-own-marker; a second run changes nothing new. |
| `scripts/kb-owner` | script | Nothing — reads CODEOWNERS, prints an answer | fully automated (detection) | Yes (called from a sweep) | N/A |
| `scripts/kb-session-start` | script | Nothing — reads the engine and libraries, emits SessionStart context | fully automated (detection) | **Yes — SessionStart hook.** Must never prompt. | N/A — never mutates, never asks |
| `scripts/kb-due` | script | Nothing — reads `last_swept`/`sweep_interval`, prints what's due | fully automated (detection) | **Yes — called from `kb-session-start`.** Must never prompt. | N/A |
| `scripts/check-kb`, `check-scope`, `check-golden`, `check-xlinks`, `check-embedded-facts`, `check-exec-bits`, `check-secrets`, `check-stamps`, `check-tool-scope`, `grade-eval` | scripts | Nothing — every one is read-only; confirmed by grepping all ten for any write/mutate call (`write_text`, `open(...'w')`, `git add/commit/config`, `subprocess`, `mkdir`, `shutil`) — none found | fully automated (detection) | **Yes — the engine's own `.githooks/pre-commit` and CI run these on every commit.** Must never prompt, and don't. | N/A |
| `plugins/knowledge-tools/commands/kb-capture.md` | command | Delegates to `scripts/kb-capture` | mutation, additive-only | No | **None — justified**, same reasoning as the script it wraps. |
| `plugins/knowledge-tools/commands/kb-init.md` | command | Delegates to `scripts/kb-init` | non-destructive idempotent scaffolding | No | **None — justified**, same reasoning as the script it wraps. |
| `plugins/knowledge-tools/skills/kb-audit` | skill | Writes `<library>/needs-attention.md` (only if there are findings) and sets `last_swept:` in the tree's own `INDEX.md` | fully automated (detection) | Not yet scheduled (Phase 5), but designed to be, and must stay non-interactive when it is | **None — justified.** The plan's own detection band names "hygiene scanning" as producing "only... a 'needs attention' queue" — that queue file and the sweep-completion stamp are bookkeeping about the sweep having run, not mutation of a fact. The skill's one discipline, stated three times in its own body, is that it never fixes what it finds; it already carries no confirm-before-write step and, being pure reporting, needs none to stay unattended-safe. |
| `plugins/knowledge-tools/skills/kb-create-domain` | skill | `mkdir` + `git init` a new library, writes its `INDEX.md`, pre-commit hook, `CODEOWNERS`, workflow file, and (if seeded) domain content and a golden set | automated-with-approval | No | **Added this pass.** A new Step 2b states the plan (name, location, tier, whether it will be seeded) and requires explicit approval before Step 3 runs a single scaffolding command. Step 7 now stops for approval before `git commit`, mirroring `kb-update-domain`'s existing gate. |
| `plugins/knowledge-tools/skills/kb-distill` | skill | Writes/edits domain files, `<domain>-open-questions.md`, `<domain>-contradictions.md`, the golden set, and marks the episodic note distilled | automated-with-approval | No | **Strengthened this pass.** Step 7 already listed what to present "before committing" but never said to stop; it now explicitly gates the commit on human approval, matching `kb-update-domain`. |
| `plugins/knowledge-tools/skills/kb-organize-domain` | skill | Moves/splits/merges/renames files, rewrites routers and the golden set | automated-with-approval | No | **Added this pass.** Step 7 had a "show the shape change" report but no explicit stop; it now gates the commit on human approval, same wording as the other two curation skills. |
| `plugins/knowledge-tools/skills/kb-update-domain` | skill | Writes a source stub, extracts and places facts, flags contradictions, stamps currency, updates routers and the golden set | automated-with-approval | No | **Already gated — no change needed.** Step 8, "The gate: show your work before committing," already presents every extracted fact against its source and stops: "Only after that review do you commit." This is the model the other three curation skills were brought into line with. |
| `plugins/knowledge-tools/agents/kb-retrieve.md` | agent | Nothing | fully automated (retrieval) | Yes | N/A — `tools: Read, Grep, Glob` is a real, runtime-enforced allowlist (§ tool-scope-matrix); it cannot write regardless of what its body says. |
| `plugins/analysis-tools/skills/intelligence-analysis` | skill | Creates/updates `~/.claude/ia-coaching-log.md` | personal, user-level, outside KB governance | No | **None — judgment call.** Not a KB fact and not subject to the retrieval contract (the skill says so itself); low blast radius (one user's own progress log, trivially edited or deleted by that user); written only at the end of an interactive coaching session the user was present for throughout, never from a hook or schedule. Excluded from the plan's three bands because those bands govern the knowledge base, and this file is deliberately outside it. |
| `.githooks/pre-commit` (engine) and the per-library `.githooks/pre-commit` template (`kb-create-domain` Step 3, `kb-init`'s snippet) | hooks | Nothing themselves — they only run the read-only `check-*` scripts and block the commit on failure | fully automated (detection) + the commit-blocking gate itself | **Yes — git commit time**, every clone, never a prompt (`--no-verify` is the documented, on-the-record bypass) | N/A — the hook *is* a gate on the commit, not something that itself needs one |

## What a skill's gate can and cannot enforce

Per the tool-scope matrix (step 1): a skill's or command's `allowed-tools:` does not restrict
anything at runtime — every tool stays callable, and the frontmatter only pre-approves what would
otherwise prompt for permission on first use. The only two things actually standing between a
mutating skill and an unreviewed write are the **procedure text** (does the skill's body say "stop
and wait for approval before committing," and does it say so *before* the point where a write would
otherwise happen) and the **user's permission mode** (does the session actually prompt on `Write`/
`Edit`/`Bash`, or is it running in an auto-accept mode that would wave every one of those prompts
through). Neither is enforced by the platform the way `tools:` is on a subagent. So the four curation
skills' gates — including the one this pass added or strengthened in three of them — are a **request
the model is trained to honor**, not a wall: a session run with edits auto-accepted, or a model that
simply skips the stop instruction, produces the same unreviewed commit either way. The gate is real
in the sense that it changes what a compliant run does and gives a human something concrete to check
before the mutation becomes durable (a git commit); it is not real in the sense of being able to stop
a run that ignores it. That gap is exactly why `scripts/kb-bootstrap` and `scripts/kb-verify` gate
with a command-line flag instead: a flag is checked by the interpreter, not honored by an agent.

## The high-blast-radius gate (Phase 4 step 6)

`scripts/check-blast` is the one gate in this table enforced by CI rather than by a skill's
procedure text or a `tools:` allowlist — a flag checked by a status check, not a request a model is
trained to honor, which is the same reason `kb-bootstrap` and `kb-verify` gate with a flag instead
of a stop instruction (above).

**What it blocks.** The plan's §5A "Never automated" band, made mechanical: in a domain library, a
PR that deletes or renames away a fact file, removes an inline `status: CONFLICTED` marker
(resolving a contradiction — CONVENTIONS §8), or changes a fact's `scope:` to a strictly wider tier
per ADR-0004 (`repo:` → `{product:, org:}` → `general`); in the engine, a PR touching
`CONVENTIONS.md` or anything under `documents/decisions/`. It runs as part of the existing
`guardrails` job in both `.github/workflows/guardrails.yml` (engine) and
`documents/library-guardrails.yml` (the per-library template), so it is covered by the `guardrails`
required status check already in place on the public engine repository (verified via
`gh api repos/dhtaylor/ai-kb/branches/main/protection`: `contexts: ["guardrails"]`).

**The label.** `owner-approved`, read from the pull request's own labels
(`github.event.pull_request.labels`, via `$GITHUB_EVENT_PATH` — no token added, matching the rest of
this workflow's anonymous-fetch design). Present, a high-blast finding still prints but no longer
fails the check. The `pull_request` trigger includes `labeled`/`unlabeled`, so adding or removing the
label re-runs the check without a new commit.

**Admin push bypasses it, with a warning.** On `push` (the same admin-exemption path ADR-0002
already documents for the rest of this workflow) `check-blast` runs but a nonzero exit is caught and
printed as a `::warning::` rather than failing the job — the push has already landed by the time CI
runs, so failing the build would not have stopped it, only hidden that it happened after the fact.
This is the same asymmetry ADR-0002 already names for every other check in this workflow, not a new
one introduced here.

**The 2-reviewer + 24h rule is dormant, not built.** The plan's paired bullet for high-blast-radius
facts — two reviewers and a 24-hour window — is recorded here as an explicit non-goal for this pass,
for the same reason ADR-0002 gives for deferring CODEOWNERS review generally: a single contributor
cannot constitute two reviewers any more than they can constitute two approvals on their own pull
request, or avoid self-merge. Building it now would be either theatre (nothing to enforce it against)
or an outright block on every change. Revisit together with ADR-0002's own trigger: when a second
contributor joins.

**"Writable only by a domain owner" is a label on the honor system today.** §5A's own wording
requires the label be writable only by a domain owner, not the agent identity. GitHub label
permissions are not that granular: anyone with triage access or above can apply or remove any label,
and on a private repository with one collaborator, that collaborator *is* everyone with triage
access. So today `owner-approved` is exactly as enforceable as CODEOWNERS was before branch
protection (ADR-0002) — real machinery, sitting idle until there is a second collaborator whose
access is *not* triage-or-above on this repository, at which point restricting who may apply the
label becomes a real, checkable claim rather than a name on a gate nobody else can reach.
