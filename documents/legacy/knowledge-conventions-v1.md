---
name: knowledge-conventions
description: The contract every knowledge domain conforms to — layout, router, granularity, provenance, contradiction handling. Enforced by organize-domain; conformed to by update-domain, /dump, /distill-episodic.
memory_type: reference
metadata:
  type: reference
  node_type: contract
  created: 2026-07-08
tags: [knowledge, conventions, progressive-disclosure, provenance]
---
# Knowledge Conventions

The single contract for how a semantic knowledge domain is shaped so it can be read by
**progressive disclosure** — an agent starting at an index loads the *minimum* content needed to
answer, never a monolith. `organize-domain` enforces this; `update-domain` (and, later, `/dump` and
`/distill-episodic`) conform to it. When this file and a skill disagree, this file wins.

Memory tiers are described in `memory/memory-system-architecture.md`; this file governs the
**semantic** tier (`knowledge/semantic/<domain>/`).

## 1. Domain layout

- Each domain is a folder `knowledge/semantic/<domain>/` with an **`INDEX.md` router** as its entry
  point — always the first file loaded.
- Content lives in **single-topic files**. A file is right-sized when it can be loaded on its own to
  answer a real question, yet still holds a coherent whole (a gestalt) rather than one fact per file.
- When a domain's topic files exceed **~15**, group the overflow into a sub-folder with its own
  sub-index (the `data-dictionary/` pattern is the reference implementation for this). Below
  that threshold, stay **flat** — every sub-folder adds a routing hop.

## 2. The router (`INDEX.md`)

Every folder — the domain root and each sub-folder — carries an `INDEX.md` that lists **only its
direct children**, one line each, and nothing else. A reader descends the tree one hop at a time,
loading the minimum at each level, never a monolith.

Each record is a hooked pointer:

- a **leaf** file: `- [key](child.md) — one-line hook (what it answers)`;
- a **sub-folder**: `- [key](subfolder/INDEX.md) — what lives under here`.

`key` is the child's slug (its filename without `.md`, or the folder name). The hook must
**disambiguate siblings** — two children must never be distinguishable only by a shared prefix.

**Descent rule:** load a folder's `INDEX.md`, pick the one child whose hook fits the question; if
that child is itself a sub-index, load it and repeat.

The router holds routing signal only — **no stored state**. Cross-cutting material that isn't a
routing decision lives in its own child doc, listed like any other record: unresolved items in
`open-questions.md`, flagged contradictions in `contradictions.md` (see §5). Create these state
leaves **only when they hold content** — a domain with no open questions or no contradictions simply
omits the record; don't route to an empty file.

This recursion extends to the knowledge-base root: `knowledge/INDEX.md` lists the **tier folders**
(`semantic/`, `episodic/`, `procedural/`, `sources/`) as sub-folder pointers, and
`semantic/INDEX.md` lists the domains. The `episodic/` index (newest-first chronological) and the
`sources/` index (a flat `[[slug]]` citation registry — the wiki-link form is load-bearing for
provenance) are direct-children **variants** of this rule, not exceptions: the descent rule still
governs them.

## 3. Granularity & the single-canonical-home rule

- **One fact, one home.** A fact is stated in full in exactly one file. Everywhere else it is
  referenced with a one-line `[[cross-link]]` at the point of use — never restated.
- Don't over-fragment a coherent model to honour the rule: an entity catalog, its relationship
  diagram, its business rules, and its code tables usually belong **together** because they are
  loaded together. Split out only what is genuinely queried alone (e.g. process flows, gotchas).

## 4. Provenance — every fact is traceable

- **Granularity: per-section, per-fact on exception.** Each topic block/heading carries a
  `Source: [[slug]]` backlink. A fact whose origin differs from its section gets its own inline
  `[[slug]]` backlink.
- **Dedup merges provenance.** When two copies of a fact collapse into one canonical home, keep
  **all** contributing `[[source]]` links — never drop a citation in a merge.
- **Sources are `[[slug]]` backlinks.** Episodic notes already *are* sources — link straight to them
  (`[[YYYY-MM-DD-domain-notes]]`). An external artifact with no home in the KB (a spec, vendor PDF,
  Solution Center page) gets a lightweight stub under **`knowledge/sources/`** so its backlink
  resolves. Don't create a stub for something already in the KB.
- A source stub (`knowledge/sources/<slug>.md`) records: title, origin (URL / page-ID / filename),
  date ingested, and where the artifact itself lives.

## 5. Contradictions — flag, don't resolve

When two sources disagree and you cannot verify which is right (e.g. the live system is unreachable):

- do **not** silently pick a winner, and do **not** edit a subordinate source of truth to match;
- write **one** clearly-marked `UNRESOLVED:` note in the file that owns the topic, stating both
  claims, the risk of each, and how to verify;
- leave a one-line pointer at the wrong-looking value (`(UNRESOLVED — see [[owner-file]])`);
- register it in the domain's `contradictions.md` (a one-line flag + pointer per item); the
  canonical `UNRESOLVED:` note stays in the file that owns the topic.

Moves of a load-bearing fact are **verbatim** — paraphrasing during a reshape can manufacture a new
contradiction.

## 6. Frontmatter schema

Every semantic/reference file carries:

```yaml
---
name: <kebab-case-slug — usually the filename; see the uniqueness note below>
description: <one line — what this file answers, disambiguating from siblings>
memory_type: semantic        # or: reference
domain: <domain>
metadata:
  type: <fact | reference | ...>
  node_type: memory
  created: YYYY-MM-DD
tags: [<domain>, <topic>, ...]
keywords: [<retrieval terms an agent might grep for>]
---
```

`tags`/`keywords` exist so retrieval can route by grepping frontmatter — keep them from a shared
vocabulary within a domain, not ad-hoc per file.

**Slug uniqueness.** `name` normally matches the filename, but `check-links` resolves every
`[[slug]]` by `name` across the *whole* tree, so any file whose bare filename repeats across domains
must carry a **globally-unique** slug. This applies to the `open-questions.md` / `contradictions.md`
state leaves (§5) above all: they exist in every domain, so each takes a domain-prefixed slug —
`name: <domain>-open-questions`, `name: <domain>-contradictions`. A non-unique `name` makes the
backlink ambiguous and silently resolves to the wrong file.

## 7. Naming

Files are kebab-case and **self-describing** (`data-model.md`, not `bnp-ontology.md`). The name
should tell a cold reader what's inside without a parenthetical.

## 8. Verifying a domain

Run `knowledge/scripts/check-links <domain-dir>` — it confirms every `[[slug]]` / `Source:` backlink
resolves (to a domain file, a `knowledge/sources/` stub, or an episodic note). A domain is not "done"
until that passes clean.
