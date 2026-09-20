---
name: organize-domain
description: Reshape a lumpy knowledge domain — split an overgrown file, merge over-fragmented ones, introduce a sub-index when a domain exceeds the flat threshold, and keep every router, backlink and golden-set record in step. Structure only, never meaning. Use after a fold leaves a domain misshapen or when a domain has outgrown a flat layout. Do NOT use to add facts (update-domain), create a domain (create-domain), or resolve contradictions.
---

# organize-domain

Moves knowledge; never changes it. Every fact that comes out must be the same fact that went in,
character for character where it is load-bearing.

**The failure mode is subtle and expensive.** A reshape is an editing pass, and editing prose is
what a language model does by reflex. Rewrite a sentence while moving it and you have manufactured
a contradiction with a source that still says the original thing — and the provenance link will
still look perfectly valid.

**Two roots, not one.** Your session context names the **engine** (the contract, the tooling,
the skills) and the **libraries** installed under it at `kb/`. Behaviour and content are
separate repositories: the engine holds no domains, and each library is its own repository
holding exactly one. Write facts into a library, never into the engine.

**Read the contract first.** Your session context names the engine; the contract is
`<engine>/CONVENTIONS.md`. If the root is unconfigured, stop and say so.

## Step 1 — Diagnose before touching anything

Report what is actually wrong before proposing a fix. Valid reasons to reshape:

| Symptom | Reshape |
|---|---|
| A file holds several topics that are never loaded together | **Split** along the query boundary |
| Several files are always loaded together to answer one question | **Merge** into the gestalt they already are |
| The domain exceeds roughly **15** topic files | **Sub-index**: group the overflow into a sub-folder with its own router |
| A file's content no longer matches its `description` | Update the description, or split if it has become two |
| A file's name no longer says what is inside | **Rename** — but see Step 4, renames are the expensive move |

If none of these hold, **say the domain is fine and stop.** A domain that is merely large is not
lumpy. Reshaping for tidiness costs golden-set churn and buys nothing.

## Step 2 — Split and merge along how the knowledge is *queried*

A file is right-sized when it can be loaded alone to answer a real question yet still holds a
coherent whole. The boundary is the **question**, not the subject heading.

- Do not split an entity catalog from its relationship diagram, its business rules and its code
  tables — those are loaded together, so they are one gestalt.
- Do split out what is genuinely asked alone: process flows, gotchas, a deprecated variant.
- Over-fragmenting is not the safe direction. It fails at retrieval instead of at load, which is
  harder to notice.

## Step 3 — Moves are verbatim

- **Copy, do not retype.** Load-bearing values, qualifiers, and the exact wording of any claim move
  unchanged. Paraphrasing during a reshape manufactures a contradiction.
- Move `Source:` backlinks **with** their sections. A section that arrives in a new file without
  its provenance has been silently stripped of its evidence.
- Move currency stamps with their sections too, unchanged. A move is not a re-verification — do not
  re-date a stamp because you touched the file.
- `status: CONFLICTED` markers move intact. Reshaping does not resolve anything.

## Step 4 — Renames are the expensive move. Pay for them in the same change.

A rename changes the slug, because the filename **is** the slug. That breaks, all at once:

1. the file's own frontmatter `name:`, which must equal the new filename;
2. every `[[slug]]` pointing at the file, in **both** roots;
3. every router line pointing at it;
4. every `expected_file:` in the golden set.

**All four are fixed in the same change as the rename.** The first is easy to miss because Step 3
says moves are verbatim — but *verbatim governs facts, not structural identifiers*. `name:` is an
identifier that must track the filename; leaving it stale fails `check-kb` and makes the file's own
metadata lie about what it is. A golden set left pointing at the old
filename is an oracle that has quietly stopped testing anything — it will pass or fail for reasons
unrelated to what it was written to check.

**Choosing the new name:** take it from what the file already says it is — its `# ` heading and
its frontmatter `description` usually agree, and a name drawn from them needs no invention. If the
heading, the description and the actual content disagree about what the file is, that is not a
naming problem: it is a signal the file has become two, so reconsider Step 2 before renaming. If
two names are genuinely equal, **ask rather than coin one** — a rename is the expensive move and
doing it twice is worse than doing it late.

Before renaming, confirm the new slug collides with nothing in **either** root — including folder
names, which are slugs too. If only one root is present, checking that one satisfies the clause;
say which roots you checked rather than implying you checked more than exist. After renaming,
grep both roots for the old slug and show that nothing still references it.

## Step 5 — Keep the routers honest

- Every folder you create gets an `INDEX.md` listing **only its direct children**, one hooked line
  each, hooks disambiguating siblings.
- Every file you moved, split, merged or renamed gets its router line updated.
- A sub-index means the parent router now points at the sub-folder, not at the files inside it.
- Do not route to an empty file or folder.
- **Leave the domain router's `freshness_horizon` and `verifier_budget` alone.** Those are currency
  policy, not structure, and nothing about moving a file changes how fast its facts decay. If a
  reshape makes you believe the horizon is wrong, say so in your report — do not change it here.

## Step 6 — Update the golden set in this same change

This is an **exit criterion**, not a follow-up. Any rename, split or merge changes which file must
answer a question:

- `expected_file:` updated for every affected record;
- `expected_excerpt:` still present in the file it now names — check, do not assume;
- records whose question is now answered by a different file **moved**, not deleted.

If the golden set does not exist for this domain, say so rather than silently proceeding — it means
the domain has no oracle at all.

## Step 7 — Verify, then show the shape change

Run the engine's `scripts/check-kb <library>`. Then report:

- the before and after file layout;
- every rename, old slug to new;
- proof no reference to an old slug survives, in either root;
- every golden-set record touched;
- confirmation that no fact's wording changed — and if any did, which and why.

State what `check-kb` does not cover: cross-root resolution, scope validation, golden-set routing.

## Refusals

Stop rather than proceed, if:

- the knowledge root is unconfigured;
- the domain does not exist, or holds no content to organize;
- you would have to change a fact's meaning to make the structure nicer. **The structure loses**;
- the reshape would resolve a contradiction, drop a `Source:` link, or delete knowledge. None of
  those are this skill's business, and deletion is never automated;
- the domain is simply fine. Say so.
