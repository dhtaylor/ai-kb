# ai-kb

A governed knowledge base for AI coding agents, with the tooling that keeps it honest.

The idea: an agent should **retrieve** what a team knows, rather than **recall** it from training
data or re-derive it from scratch every session. That only works if the knowledge is trustworthy,
so every fact here carries where it came from, when it was last verified and how. Contradictions
are made unretrievable instead of quietly resolved. A retrieval agent answers only from what it
read, cites every file, and says "fact not found" when the knowledge base is silent.

It is built for [Claude Code](https://claude.com/claude-code) and ships as a Claude Code plugin,
but the knowledge itself is plain Markdown in git.

## What is in this repository

This repository is the **engine**. It holds the contract, the tooling and the behavior, and **no
facts**:

| Path | What it is |
|---|---|
| [`CONVENTIONS.md`](CONVENTIONS.md) | The contract: scope tiers, provenance, currency stamps, slugs and cross-links, contradictions, the retrieval rules. It settles any question this README leaves open. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | The working guide: setting up a machine, the daily loop, curating. |
| `plugins/knowledge-tools/` | The Claude Code plugin: five curation skills and the `kb-retrieve` agent. |
| `scripts/` | Setup commands (`kb-bootstrap`, `kb-init`, `kb-capture`) and the checks that guard the contract. |
| `documents/decisions/` | Architecture decision records (ADR-0001 to ADR-0010). Each one explains why a rule exists. |
| `tests/run-checks` | A regression suite that breaks each check on purpose and requires it to notice. |

The facts live elsewhere, in two kinds of home:

- **Domain libraries.** Each library is its own git repository, one per subject domain, cloned into
  the engine's `kb/` directory. A library holds facts that are true wherever its subject appears,
  plus their sources and a golden set of test questions. Libraries are usually private: the engine
  is public, and the knowledge doesn't have to be.
- **Project trees.** A `knowledge/` directory inside an ordinary project repository holds facts
  that are true only of that deployment.

Keeping behavior and knowledge in separate repositories is deliberate. Libraries stay portable,
and the engine can be shared without sharing anything it has learned. See
[ADR-0007](documents/decisions/0007-engine-content-separation.md).

## Getting started

Requirements: git, bash, Python 3 (standard library only) and Claude Code.

```bash
git clone https://github.com/dhtaylor/ai-kb.git ~/kb-engine
mkdir -p ~/kb-engine/kb
git clone <library-url> ~/kb-engine/kb/<library-name>     # each library you have access to
~/kb-engine/scripts/kb-bootstrap                          # register the engine on this machine
```

Then restart your terminal and any open Claude Code session. Run `kb-bootstrap --check` at any time
to confirm the setup without changing anything.

In each project where you want knowledge captured, run `kb-init`. Do this in every clone, because
git does not clone hook configuration.

If you have no library yet, the `kb-create-domain` skill stands one up. [CONTRIBUTING.md](CONTRIBUTING.md)
covers all of this in full, including what `kb-bootstrap` writes and where.

## How it is used

1. **Capture.** `/kb-capture` in a session, or `kb-capture` in a terminal, writes a dated note of
   what was done and seen. A capture records; it does not decide.
2. **Distill.** `kb-distill` turns notes into durable facts. Observations become facts with a
   source and a verification stamp. Speculation stays in the note.
3. **Curate.** `kb-update-domain` folds in documents and specs. `kb-create-domain` and
   `kb-organize-domain` build and reshape domains. `kb-audit` sweeps for decay and reports without
   fixing anything.
4. **Retrieve.** The `kb-retrieve` agent answers questions from the knowledge base, with citations,
   and refuses to guess or to serve a disputed fact.

## Guardrails

Every rule in the contract that can be checked is checked at commit time by git hooks, and all but
one again in CI, where a hook can't be skipped:

- structure, routing and links within a library (`check-kb`)
- links between libraries (`check-xlinks`, at commit time only; see ADR-0010)
- scope tiers (`check-scope`)
- golden-set integrity (`check-golden`)
- credential-shaped strings, across full history (`check-secrets`)
- facts pasted into agent prompts instead of retrieved (`check-embedded-facts`)
- verification stamps that claim more than the commit supports (`check-stamps`)

`kb-verify` re-runs the assertions that defend stale facts, and `kb-due` reports which trees are
due for a sweep. Both report rather than repair.

## Status

This is early, working software, version 0.1.0, with one author so far.

- **Built and tested:** the contract, ADRs 1 to 10, the five skills, the retrieval agent, both
  halves of the retrieval eval, and the guardrails above.
- **Evidenced, not guaranteed:** that an agent retrieves rather than recalls has been tested on four
  libraries by agents that never saw the answer key. The latest recorded runs scored 15/16, 16/16
  and 14/17 on the three newest, each of which keeps its runs' answers and grades as evidence. The
  first library's single run survives only as a note in the plan. The protocol changed between runs as defects in the eval itself were found; the plan's
  §9.14–9.15 records which.
- **Next:** rolling out further domains, then orchestration across domain agents, then
  steady-state upkeep. The full plan, including what building it proved and disproved, is in
  [`documents/knowledge-agent-architecture-combination-plan.md`](documents/knowledge-agent-architecture-combination-plan.md).

Known gaps are recorded, not hidden. CI checks are required on `main`, but pull-request and
code-owner review wait for a second contributor, since an author can't approve their own pull request
([ADR-0002](documents/decisions/0002-governance-without-enforcement.md)). Cross-library links are
checked at commit time rather than in CI
([ADR-0010](documents/decisions/0010-cross-library-links-checked-at-commit.md)).

## Feedback

Issues and pull requests are welcome. Read [CONVENTIONS.md](CONVENTIONS.md) before proposing a
change to the contract, and run `tests/run-checks` before proposing a change to a check.

## License

[MIT](LICENSE). The license covers this engine only. Each domain library is its own repository,
with its own terms.
