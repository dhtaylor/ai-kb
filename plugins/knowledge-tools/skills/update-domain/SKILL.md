---
name: update-domain
description: Fold source material — a spec, vendor page, legacy document, prior agent prompt, or system output — into an existing knowledge domain, with per-section provenance, dedup and supersede handling, and contradictions flagged rather than resolved. Use when new source material needs to become durable knowledge in a domain that already exists. Do NOT use to create a domain (create-domain), reshape a lumpy one (organize-domain), or distill session notes (distill-episodic).
---

# update-domain

The workhorse, and the most dangerous skill in the set. Folding is where facts get corrupted,
and **you are the thing doing the corrupting**. A language model rounds a constant, drops a
qualifier, merges two behaviors into one tidy generalization, and produces a fact that reads
better than the source and is wrong. The result lands in the one place everything else treats
as trustworthy.

Every rule below exists because of that. Follow them even when the paraphrase is obviously better.

**Read the contract first.** Your session context names the general knowledge root; the contract
is `<general-root>/knowledge/CONVENTIONS.md`. If the root is reported unconfigured, stop and say
so — never guess a path.

## Step 1 — Confirm the target

The domain must already exist. If it does not, stop and say `create-domain` is the skill.

Check the domain's `scope:` against the material. If some of the source belongs to a different
tier — a deployment detail inside a vendor document, say — **that part does not go here.** Name
it, say where it belongs, and leave it out of this fold rather than filing it wrongly because it
arrived in the same file.

**A multi-domain source folds once per target domain**, with explicit per-domain fact selection
each time. Never fold the whole document into each domain and let the indexes sort it out.

## Step 2 — Ingest the source before extracting from it

Create a stub at `<root>/knowledge/sources/<slug>.md` recording title, origin (URL, page ID, or
filename), date ingested, and where the artifact itself lives. Provenance backlinks resolve to
this stub, so it must exist before any fact cites it.

If the artifact already has a home in the KB — an episodic note, another KB file — link straight
to it. Do not stub something already present.

## Step 3 — Extract. This is the dangerous step.

For each candidate fact:

- **Load-bearing values are copy-pasted, character for character.** Numbers, identifiers, limits,
  version strings, enum values, error codes, paths, flags. Do not retype them. Do not normalize
  units, round, reformat, or "clean up" a value. If the source says a timeout is 4.7 seconds, the
  KB says 4.7 seconds — not "about 5".
- **Qualifiers are part of the fact.** "Usually", "on Linux", "before version 9", "unless the
  cache is cold" — dropping one converts a conditional truth into a universal falsehood. If you
  cannot keep the qualifier, you cannot keep the fact.
- **Never merge two behaviors into one generalization.** Two cases that look like one pattern are
  two facts until the source says they are one. The tidier sentence is the corrupted one.
- **Never fill a gap.** If the source is silent, incomplete or ambiguous, the KB is silent. Record
  the gap in `<domain>-open-questions.md` rather than inferring the answer. A plausible invented
  fact is indistinguishable from a real one once it is in the KB, and that is the whole failure.
- **Do not promote an example into a rule.** One observed value is an observation, not a default.

If you find yourself improving the source's prose, stop — that is the corruption happening.

## Step 4 — Place each fact

For each extracted fact, in this order:

| The domain already... | Do this |
|---|---|
| states it identically | **Do not duplicate.** Add the new `Source:` backlink to the existing section — dedup merges provenance, and a citation is never dropped in a merge |
| states it less completely | Enrich the existing section in place. Keep **all** contributing source links |
| states something that **contradicts** it | **Stop. Go to Step 5.** Do not pick a winner |
| states a version of it that the source supersedes | Replace the value, keep a one-line note of what it superseded and when, and keep both source links |
| does not state it | Add it — to the file where it belongs, not a new file by reflex |

If a file's content outgrows its frontmatter `description`, either update the description to match
what it now holds, or treat the mismatch as a signal the file is becoming two — that is
`organize-domain`'s call, not a decision to make mid-fold.

**A file is a gestalt.** Right-sized when it can be loaded alone to answer a real question yet
still holds a coherent whole. Add the fact to the file that is already loaded to answer that kind
of question. Create a new file only when the fact is genuinely queried on its own. Over-fragmenting
is as harmful as a monolith — it just fails at a different step.

Crossing to another domain's fact? **Link it with `[[slug]]`, never restate it.** A general-tier
fact referenced from a repo-tier file uses the `[[general:slug]]` form.

## Step 5 — Contradictions: flag, never resolve

When the source disagrees with what the KB already states and you cannot verify which is right:

- **Do not silently pick a winner**, and do not edit the weaker source to match the stronger.
- Mark it **inline** with `status: CONFLICTED`, stating both claims, the risk of each, and how
  someone would verify. Retrieval agents refuse to serve a CONFLICTED section, which is the point —
  a conflict that is merely annotated still gets served with confidence.
- **Mark the narrowest unit that holds the disputed claim.** Refusal is wholesale, so a disputed
  value left sitting in a section full of sound facts withholds all of them. If the claim shares a
  section with undisputed facts, **split it into its own subsection first**, then mark that. Taking
  good knowledge offline as a side effect is a bug, not caution.
- Register a one-line flag and pointer in `<domain>-contradictions.md`. Create that file if this
  is the domain's first contradiction; the canonical note stays in the file owning the topic.
- Say whether it is **blocking** (the fact is actively needed) or informational, and name who
  resolves it and by what means.

Resolving a contradiction is never your call. It is never automated.

## Step 6 — Provenance and currency on every section you touch

- `Source: [[slug]]` on each topic section. A fact whose origin differs from its section gets its
  own inline backlink.
- A currency stamp beneath it where the fact can go stale:

  ```
  Verified: <date> · by: <agent|human> · method: <query|integration-test|doc-review|manual>
  ```

  A fold is `method: doc-review` — you read a document, you did not query a live system. Do not
  stamp it as anything stronger. **No evidence, no stamp**: record what you actually checked.
- Update the file's frontmatter `verified:` floor — the oldest section stamp in that file.

## Step 7 — Routers and golden set

- Update the domain `INDEX.md` for any file you added: one hooked line, disambiguating its
  siblings. A file nothing routes to is invisible.
- If the domain crossed roughly 15 topic files, say so — that is `organize-domain`'s trigger, not
  something to fix mid-fold.
- **Seed or extend `<root>/knowledge/golden-retrieval/<domain>-golden.md` in this same change.** If the
  domain had no golden set because it was empty, it has content now and this is where the
  obligation lands. Every record carries a `case:` label (§10). Include at least two `negative` cases and — if the
  fold produced a contradiction — an `unresolved` case proving the agent surfaces it rather than
  serving a value. A `cross-root` case applies **only if the domain actually links across tiers**;
  where it does not, say so in the file rather than inventing a link to satisfy a count.

## Step 8 — The gate: show your work before committing

**Present every extracted fact side by side with its source excerpt, and stop for review.**

This is the control that catches a fold corrupting a value, and it is not optional or
summarizable. Do not report "folded 12 facts" — show the 12, each against the text it came from,
so a human can see a dropped qualifier or a rounded number. Call out explicitly:

- every value you copied verbatim;
- every qualifier you preserved;
- anything you left out, and why;
- every contradiction flagged;
- every gap recorded rather than filled.

Only after that review do you commit.

## Step 9 — Verify

Run `<root>/knowledge/scripts/check-kb` against the root you wrote to. Report the result, and
state what it does not cover: cross-root `[[general:slug]]` resolution, scope-value validation
and golden-set routing are not built. A clean run means structurally sound within one root — not
verified.

## Refusals

Stop and say so rather than proceeding, if:

- the knowledge root is unconfigured;
- the target domain does not exist — that is `create-domain`;
- the source material is not actually available to you. **Never fold from memory of what a
  document probably says.** A fold with no source is invention wearing a citation;
- you cannot preserve a value or qualifier faithfully;
- the material belongs in a different tier, or in a domain that does not exist yet;
- the user asks you to resolve a contradiction as part of the fold.
