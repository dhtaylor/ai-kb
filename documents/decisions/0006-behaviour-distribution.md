# ADR-0006: The knowledge base is its own repository, and its behaviour travels as a plugin

- **Status:** Accepted
- **Date:** 2026-09-19
- **Deciders:** Dandy Taylor
- **Amends:** [ADR-0003](0003-scoping-topology.md)

## Context and problem statement

[ADR-0003](0003-scoping-topology.md) placed the general knowledge tier at `ws_v1/knowledge/`, a
directory inside the workspace repository, and accepted a project nesting inside that same
workspace because it made cross-root resolution testable on one machine.

That settled where *facts* live. It did not settle where the *behaviour* that curates and queries
them lives, and the answer is not symmetric with the facts, because behaviour is discovered
differently.

**The discovery fact that decides this.** Claude Code discovers `.claude/agents/`, `.claude/skills/`
and `.claude/commands/` by walking **up** from the working directory, and the walk **stops at the
repository root**. It never descends. Two consequences follow:

- A session started in `code/test_project` — its own repository — cannot see the workspace's
  behaviour, because the walk stops at `test_project`'s own root.
- A session started in the workspace cannot see a *nested* repository's behaviour either, because
  the walk goes the wrong way.

So behaviour placed in the workspace's `.claude/` is reachable from exactly one directory, and
behaviour reachable anywhere else must travel by some explicit mechanism.

> **Documented, not verified here.** This behaviour is taken from Claude Code's documentation. It
> has **not** been observed in this environment — confirming it requires a session actually started
> in `code/test_project`. Treat it as unconfirmed until Phase 3 tests it. Several things in this
> build have read correctly and behaved otherwise.

## Decision drivers

- **A repository should guard itself.** Guardrails that live in a repo they no longer belong to are
  guardrails in name only.
- **Nothing should work by directory accident.** Behaviour inherited because of where a folder
  happens to sit is behaviour that vanishes when the folder moves, with no error.
- **A citation should resolve inside the repository that makes it.** A provenance link pointing over
  a repo boundary resolves only where both repos happen to be checked out together.

## Decision outcome

**The knowledge base is its own git repository, holding everything that belongs to it, and it is
also a plugin marketplace. Consumers register it explicitly.**

History was carried with `git subtree split`, not restarted: all prior commits are intact.

### What lives in the knowledge repository, and why

| Moved in | Reason |
|---|---|
| `documents/decisions/` (these ADRs) | Their source stubs cite them by relative path. Split across repos, those citations point over a boundary that need not exist elsewhere. |
| `documents/` source artifacts | Same: the artifact a domain was folded from belongs with the domain. |
| `.githooks/`, `.github/` | A repo guards itself. The workspace would otherwise have gone on checking scripts its checkout no longer contains, and this repo would have had none at all. |
| The five maintenance skills | Now in `plugins/knowledge-tools/`, so they can be registered by any project rather than being reachable only from one directory. |

### Both kinds of behaviour travel

An earlier reading split maintenance behaviour ("stays home") from retrieval behaviour ("travels").
That split is rejected: it assumed a session would always be started inside the knowledge base to
curate it, which is false as soon as a project's own knowledge needs curating from elsewhere.
**All knowledge behaviour travels in one plugin**, and the knowledge base is the single home for it.

### Registration is explicit, deliberately

A consumer declares the marketplace in its settings:

```json
{
  "extraKnownMarketplaces": {
    "governed-knowledge": { "source": { "source": "directory", "path": "./knowledge" } }
  },
  "enabledPlugins": { "knowledge-tools@governed-knowledge": true }
}
```

Explicit registration is the feature. It works identically for a knowledge base sitting beside the
project and one living anywhere else on disk, whereas inheritance-by-nesting works only in the one
layout that produced it.

### `check-kb` gained an exclusion list

The knowledge repository's root now holds decision records, plugin manifests, CI configuration and
tooling alongside the knowledge base. None carry the frontmatter contract. Without an exclusion list
`check-kb` would lint 11 non-KB files and fail on every one. KB tier folders are checked; everything
else is explicitly not — and "explicitly" matters, because a checker that silently skips things is
the failure this whole design guards against.

## Consequences

**Good.** Each repository guards itself. Every provenance citation resolves inside the repo that
makes it. Behaviour reaches a consumer the same way regardless of where that consumer sits. The
knowledge base can be cloned, moved or shared without dragging a workspace with it.

**Bad.** The workspace has **no CI**: the workflow moved with the scripts it runs, and the workspace
cannot check out a repository it no longer tracks. Its pre-commit hook degrades gracefully —
announcing plainly that nothing is guarding the commit when the knowledge repo is absent — but
between that and the absent CI, the workspace is guarded by convention rather than enforcement. It
holds a settings file, a gitignore and a hook, so the exposure is small; it is not zero, and it is
recorded rather than papered over.

**Open, and genuinely unknown.** The marketplace path is written relative (`./knowledge`). If Claude
Code resolves it against the settings file's own root, the workspace is machine-independent. If it
demands an absolute path, this becomes another hardcoded path of exactly the kind the contract §1
forbids everywhere else, and it joins the bootstrap command that still does not exist. **Not
tested** — it needs a session restart.

**A hazard worth naming.** Project `.claude/agents/` **shadow** same-named plugin agents. That is a
feature — a project can override a general retrieval agent with its own — and a silent-divergence
risk, because nothing announces that the general one has been replaced.

## Amended 2026-09-19 — the repository gained a remote, and the directory source stays

`github.com/dhtaylor/ai-kb` now exists (private; anonymous read denied and verified), the history is
pushed, and CI can finally run where the workflow lives. That fires this ADR's own review trigger:
should the marketplace now be sourced from the git remote rather than from a local path?

**No. The `directory` source stays, and the reason is not inertia.**

A `git` source would give each consumer its own cached copy of the *behaviour*, fetched from whatever
ref the marketplace names. But the *facts* are read from the local clone at
`$KB_GENERAL_ROOT/knowledge/`. Those are then two independently-versioned things, and nothing keeps
them in step: an agent could run skills from one revision against a contract and domains from
another. Given how much of this contract has moved — v2 plus six amendments — that is not a remote
possibility, it is the expected case.

The `directory` source points at the same working tree the facts are read from, so behaviour and the
knowledge it operates on are the same checkout by construction. They cannot drift, because there is
only one of them.

A git source becomes right for a consumer that holds **no local clone** and queries the knowledge
base some other way. That is not this topology, and when it is, the drift problem has to be solved
explicitly rather than inherited.

The "workspace has no CI" consequence above stands unchanged — that is `ws_v1`, which still tracks
only three files. The knowledge repository now has both a remote and a working CI.

## Review trigger

Revisit if: the relative marketplace path proves unsupported; a consumer needs a pinned version of
the behaviour rather than whatever the directory currently holds; or a consumer appears that holds
no local clone of the knowledge base, at which point the behaviour/facts lockstep argued above must
be re-established by other means.
