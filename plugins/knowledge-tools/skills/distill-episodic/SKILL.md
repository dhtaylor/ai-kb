---
name: distill-episodic
description: Turn episodic material — session logs, meeting notes, debugging transcripts, dump records — into durable semantic facts, separating what was observed from what was concluded or merely speculated, and citing the episodic note as the source. Use when session notes contain knowledge worth keeping. Do NOT use to fold external documents (update-domain), create a domain (create-domain), or delete the episodic record.
---

# distill-episodic

Episodic notes are a record of *what happened*. Semantic facts are claims about *what is true*.
Distilling is the act of deciding which of the former have earned the latter, and the whole
difficulty is that a session log does not mark the difference.

A transcript contains observations, working hypotheses, things tried and abandoned, decisions made
on partial information, and frustrated guesses — all in the same voice, often the same paragraph.
Promote the wrong one and you have installed a guess in the place everything else treats as
authoritative, wearing a citation that makes it look checked.

**Two roots, not one.** Your session context names the **engine** (the contract, the tooling,
the skills) and the **libraries** installed under it at `kb/`. Behaviour and content are
separate repositories: the engine holds no domains, and each library is its own repository
holding exactly one. Write facts into a library, never into the engine.

**Read the contract first.** Your session context names the engine; the contract is
`<engine>/CONVENTIONS.md`. If the root is unconfigured, stop and say so.

## Step 1 — Classify every candidate before promoting any

For each statement in the episodic material, decide which it is. Say so explicitly in your report;
do not skip to the extraction.

| In the notes | Is it a fact? |
|---|---|
| **Observed** — a command was run and this was the output; the system did this | **Yes**, and the observation is the evidence |
| **Concluded** — a diagnosis reached from observations | **Only if** the reasoning is recorded and the observations support it. Record the reasoning with it |
| **Decided** — "we will do X" | Not a semantic fact. It is a decision — it belongs in an ADR, not the KB |
| **Speculated** — "probably", "I think", "it might be" | **No.** This is the one that looks most like knowledge and is not |
| **Documented** — an authoritative source says so, but nobody here ran it | **Yes, at lower evidence.** Stamp `method: doc-review`, never `query` or `manual`, and say in the prose that it was not independently verified. It sounds like fact because the source is confident; the confidence is the source's, not yours |
| **Tried and abandoned** — an approach that did not work | Only as a documented negative result, stated as such |

**One observation is not a general truth.** A thing seen once, in one environment, is an
observation about that environment. It may become a repo-tier fact. It does not become a
product-tier or general-tier fact without evidence external to this session — see the contract §9.

If you cannot tell which category a statement falls into, it stays in the episodic note. That is
not a failure; that is the note doing its job.

## Step 2 — Scope each surviving fact

Apply the classification test per fact, not per note. A single session commonly produces facts at
two tiers: what *this system* did, and what the *product* does.

> *Is this true only of this repo/deployment, or true wherever this product/tool/concept appears?*

And for the tier that traps people — would the fact **stop being true if you swapped the vendor or
product**? Yes means `product:<vendor>`; no means `general`.

Facts of different scope go to different roots. Do not file them together because they came from
one session.

**If the correct tier's home is not reachable from the root you are working in** — a repo-tier fact
surfaced while you are in the general root, with no project repo in reach — **do not file it
anywhere.** Not in the nearest domain, not "temporarily" in the general tier. Leave it in the
episodic note, name it in your report as a fact awaiting a home, and say which tier it belongs to.
A repo fact parked in the general tier is a claim about every deployment made from one.

## Step 3 — Episodic notes are already sources. Link, do not stub.

The note has a home in the KB, so cite it directly: `Source: [[YYYY-MM-DD-domain-notes]]`. Creating
a `sources/` stub for something already in the KB is duplication.

Currency on a distilled fact reflects **when it was observed**, not when you distilled it:

```
Verified: <the date of the observation> · by: <agent|human> · method: manual
```

Do not stamp today's date on a thing observed weeks ago. That is manufacturing freshness.

## Step 4 — Place the facts

Placement follows the same rules as a fold, and the same decision table:

- the domain already states it identically → **do not duplicate**; add the episodic backlink to the
  existing section, because dedup merges provenance;
- states it less completely → enrich in place, keep all source links;
- **contradicts** it → `status: CONFLICTED`, marked on the **narrowest unit** holding the disputed
  claim so neighbouring sound facts stay retrievable. Never pick a winner;
- does not state it → add it to the file where it belongs.

If no domain covers the fact, **stop and say a domain must be created first** — that is
`create-domain`. Do not improvise a home. An **installed library that simply has no topic files yet is
already covered** — seeding it is this skill's job, not a reason to stop.

A fact whose correct home exists in **no library at all** is reported, not filed: name it, name the
tier it belongs to, and leave it in the episodic note. The note is its home until a library exists —
an open-questions file belongs to a domain, and this fact belongs to none.

## Step 5 — The episodic note stays

Distilling does not consume the note. The note remains the evidence the fact points at, and
deleting it orphans every backlink that cites it. Deletion is never automated and is not this
skill's business.

Note in the episodic file that it has been distilled, and where the facts went.

## Step 6 — Golden set and routers

- Any file you added gets a router line in the domain `INDEX.md`.
- Extend `<library>/<domain>-golden.md` for facts you added, records carrying a
  `case:` label. Include an `unresolved` case if you flagged a contradiction.
- **Repair any existing record your own change invalidated, in this same change.** Marking a section
  `CONFLICTED` turns every `positive` case pointing at it into a case a correctly-behaving agent must
  now fail — the agent refuses a CONFLICTED section, so the oracle is testing the opposite of the
  contract. Convert it rather than leave a known-wrong record beside a fresh one.
- Non-compliance you merely *notice* while passing — an older contradiction never registered, a
  missing stamp elsewhere — is **reported, not repaired**. Fixing it silently expands an unreviewed
  change into adjacent files.

## Step 7 — Show your work, then verify

Present, before committing:

- every statement you classified and the category you put it in — **including the ones you refused
  to promote, and why.** The refusals are the valuable half of this report;
- every fact promoted, against the exact line in the episodic note it came from;
- every scope decision, with the tier test that drove it.

Then run the engine's `scripts/check-kb <library>` and report the result and its limits.

## Refusals

Stop rather than proceed, if:

- the knowledge root is unconfigured;
- the episodic material is not actually available to you — never distil from memory of a session;
- no domain exists for the facts, and you would have to invent one on the fly;
- you would have to promote a speculation, a decision, or a single observation into a general
  truth to make the distillation look productive. **An episodic note that yields two facts and
  eight refusals is a good outcome.**
