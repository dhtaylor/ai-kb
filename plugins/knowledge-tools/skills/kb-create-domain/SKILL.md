---
name: kb-create-domain
description: Stand up a new semantic knowledge domain that does not exist yet, in the correct knowledge tier, conforming to the knowledge conventions — folder, INDEX router, frontmatter, provenance, golden set, and the router chain above it. Use when a fact needs a home and no domain covers it, or when seeding a domain from source material. Do NOT use to add facts to a domain that already exists (that is kb-update-domain) or to reshape a lumpy one (kb-organize-domain).
---

# kb-create-domain

Stands up a domain that does not exist yet. Structure only — you are building the shelf, and
seeding it if source material was supplied. You are not inventing facts.

**Two kinds of repository.** Your session context names the **engine** (the contract, the tooling,
the skills) and the **libraries** installed under it at `kb/`. Behaviour and content are
separate repositories: the engine holds no domains, and each library is its own repository
holding exactly one. Write facts into a library, never into the engine.

**Read the contract first.** Your session context names the engine; the contract
is `<engine>/CONVENTIONS.md`. Load it before you create anything. If the root is
reported unconfigured, stop and say so — never guess a path, never fall back to a relative one.

When the contract and this skill disagree, **the contract wins** and this skill is the thing
that gets fixed.

## Step 1 — Decide the tier. Ask, do not assume.

Apply the classification test to the knowledge the domain will hold:

> *Is this true only of this repo/deployment, or true wherever this product/tool/concept appears?*

| Answer | `scope:` | Root |
|---|---|---|
| Only this deployment — topology, deploy quirks, this system's bugs | `repo:<project>` | the project repository's `knowledge/` |
| Wherever this vendor's product appears | `product:<vendor>` | the general root |
| Across the organization — standards, architecture rules | `org:<company>` | the general root |
| Domain fundamentals, engine or platform behavior | `general` | the general root |

**`product:<vendor>` and `general` look alike and are not.** For a single-vendor engine, "that
vendor's product behavior" and "engine fundamentals" describe the same sentence, so the words do
not separate them. Use this instead:

> *Would this fact stop being true if you swapped the vendor or product?*

- **Yes → `product:<vendor>`.** How a specific database implements snapshot isolation is that
  product's behavior; replace the product and the fact dies with it.
- **No → `general`.** What serializable isolation *means*, or what a standard requires, survives
  the swap.

The two are not interchangeable: they carry different promotion guards, and a vendor fact filed as
`general` is a claim about the whole world made from one product's behavior. **Do not decide this
from whichever word the user happened to use** — they are describing their need, not classifying.

If the answer is "both", it is **two domains, or one domain and a cross-link** — never one domain
straddling two tiers. If you cannot tell, **ask the user**. Guessing here is the failure this
whole test exists to prevent, and it is far cheaper to fix now than after facts accumulate.

Personal knowledge belongs in neither repository. Say so and stop.

## Step 2 — Name it

Kebab-case, self-describing, tells a cold reader what is inside without a parenthetical. The
filename is the slug, so the domain folder name must not collide with an existing domain in
**either** root.

When several names fit equally, name the domain for **the question it answers**, not the mechanism
it happens to use, and prefer the shorter. If two names are genuinely equivalent, **ask the user
rather than coin one**: renaming later rots the golden set and every `[[slug]]` pointing at the
domain, so a cheap question now beats a migration later.

## Step 3 — Scaffold the library. It is a repository, not a folder.

A domain library is its **own git repository**, installed under the engine at
`<engine>/kb/<domain>/`. Create and initialise it:

```
mkdir -p <engine>/kb/<domain> && cd <engine>/kb/<domain> && git init
```

The engine **ignores** `kb/` — it creates the space, it never tracks what lives there. That is the
separation this whole design rests on: the engine is behaviour, a library is content, and neither
is allowed to smuggle the other into its history.

Give the library a pre-commit hook at `.githooks/pre-commit`, then
`chmod +x` it, `git add` it and `git config core.hooksPath .githooks`.

**Check the mode git actually recorded** — `git ls-files -s .githooks/pre-commit` must start
`100755` <!-- lint-allow: a git file mode, not an embedded fact -->. On a filesystem where
`core.fileMode` is false, git ignores the on-disk bit and records
644, and then **git skips the hook silently**: the library looks guarded and is not. If it recorded
644, fix it with `git update-index --chmod=+x .githooks/pre-commit`. This bug has occurred twice.

```bash
#!/usr/bin/env bash
# Domain library guardrail. The checkers live in the engine, which this library
# does NOT depend on — it is portable and may be cloned anywhere. Absence is
# graceful: warn, never crash, never guess.
set -uo pipefail

find_engine() {
  [ -n "${KB_ENGINE_ROOT:-}" ] && [ -x "$KB_ENGINE_ROOT/scripts/check-kb" ] && { echo "$KB_ENGINE_ROOT"; return; }
  local g; g=$(git config --get kb.engineRoot 2>/dev/null)   # set by kb-bootstrap; git reads it in every context
  [ -n "$g" ] && [ -x "$g/scripts/check-kb" ] && { echo "$g"; return; }
  [ -x ../../scripts/check-kb ] && { echo "../.."; return; }   # designed layout: <engine>/kb/<library>
}

ENGINE=$(find_engine)
if [ -z "$ENGINE" ]; then
  echo "domain pre-commit: engine not found — structural checks SKIPPED."
  echo "  Run kb-bootstrap on this machine, or clone this library under an engine's kb/."
  exit 0
fi

fail=0
echo "domain pre-commit (engine: $ENGINE):"
"$ENGINE/scripts/check-exec-bits" .  || fail=1
"$ENGINE/scripts/check-secrets"      || fail=1
"$ENGINE/scripts/check-kb"     .     || fail=1
"$ENGINE/scripts/check-scope"  .     || fail=1
"$ENGINE/scripts/check-golden" .     || fail=1   # once the library has a golden set
[ "$fail" -ne 0 ] && { echo; echo "Commit blocked."; exit 1; }
echo "domain pre-commit: clean"
```

A library must not depend on an engine it is designed to outlive, which is why absence skips rather
than fails.

Then create `INDEX.md` **at the library root**. It is the domain router, the entry point, and the
only file carrying the domain's currency configuration:

```yaml
---
name: <domain>-index
description: <one line — what this domain answers>
memory_type: reference
domain: <domain>
scope: <the value from step 1>
freshness_horizon: <e.g. 30d — how fast this domain's facts decay>
verifier_budget: <N — max facts re-checked per cycle>
metadata:
  type: index
  node_type: router
  created: <today>
tags: [<domain>]
keywords: [<terms an agent would grep for>]
---
```

`name` is `<domain>-index`, which deliberately does **not** match the filename. `INDEX.md` is a
path-addressed file: it is reached by relative path and is never a `[[slug]]` target, so the
contract exempts it from the name-matches-filename rule and asks for a descriptive name instead.
This is not a mistake to correct.

Choose `freshness_horizon` from the domain's actual volatility. There is no correct global
default — picking per domain is the point of the field — but "days to years" is too wide to choose
against, so start from these bands and say which you picked and why:

| The domain holds | Band | Because |
|---|---|---|
| Deployment topology, endpoints, environment config | **7–30d** | changes without announcement, and wrongness is immediately load-bearing |
| A vendor product's behavior (`product:<vendor>`) | **90–180d** | tracks that product's release cadence |
| Domain fundamentals, standards, protocol semantics (`general`) | **365d+** | changes on the timescale of specifications |

These are starting points to be revised from evidence, not thresholds to defend. If a domain's
facts keep going stale before its horizon, the horizon is wrong.

`verifier_budget` is a **cost ceiling, not a target** — the most facts a cycle may re-check, not
how many it should. Start at **5** and raise it only when the attention queue shows the cap is
actually binding. A new domain with no facts still declares it, so the cadence has a bound the
moment content arrives rather than needing one retrofitted.

The router body lists **only direct children**, one hooked line each, and nothing else:

- a leaf: `- [key](child.md) — one-line hook (what it answers)`
- a sub-folder: `- [key](subfolder/INDEX.md) — what lives under here`

The hook must disambiguate siblings. Two children must never be distinguishable only by a shared
prefix.

**An empty domain still needs a body.** "Nothing else" forbids stored *facts* in a router, not
prose. A domain with no children yet carries its title, one line on what it will hold, and one line
saying it is empty and why — so a reader who routes here learns the shelf is bare rather than
assuming the index is broken. Add the hooked child lines as content arrives.

**Do not create empty state leaves.** `<domain>-open-questions.md` and
`<domain>-contradictions.md` exist only once they hold content. Routing to an empty file wastes
a hop and teaches the reader the index lies.

## Step 4 — Seed, if source material was supplied

Only if the user gave you source material. Otherwise the domain is an empty shelf and that is a
valid result — say so.

- **Load-bearing values are copy-pasted, never retyped or paraphrased.** An LLM fold can round a
  constant, drop a qualifier, or merge two behaviors into one generalization. Copy them.
- Each topic section carries `Source: [[slug]]`. If the source is an artifact with no home in the
  KB, create a stub under the library's own `sources/` first, so the backlink resolves.
- A file is a **gestalt**, not one fact per file: right-sized when it can be loaded alone to
  answer a real question yet still holds a coherent whole. Do not over-fragment a model whose
  parts are always loaded together.
- **Present each extracted fact to the user against its source before committing.** This is the
  step that catches a fold corrupting a value, and it is not optional.

## Step 5 — Nothing to wire above it

There is no router chain above a library and no registry to update. A library is discovered by
**being present** under the engine's `kb/`, and the session-start hook enumerates what is installed.

This is deliberate. A registry listing the libraries would live in the engine, which does not track
`kb/` — so it would be either untracked state that drifts, or tracked state that lies on every
machine with a different set of libraries installed. Presence is the registry.

What you **do** wire is inside the library: every file you create gets a hooked line in the
library's own `INDEX.md`.

## Step 6 — Seed the golden set

Create `<domain>-golden.md` **at the library root** — the oracle travels with the domain it tests.
Records carry `case:`, `question:`, `expected_file:`, `expected_excerpt:`. A domain with no golden set has no oracle, and a later
rename will rot it silently.

Include from the start:

- at least **two negative cases** — questions this domain must refuse to guess at;
- at least **one UNRESOLVED case** — a conflict the agent must surface rather than serve;
- at least **one cross-root case**, if the domain links across tiers.

If the domain has no content yet, the golden set is **deferred and no file is created** — not a
placeholder. An empty golden-set file is an empty state leaf by another name, and an oracle with no
records reads as coverage that does not exist.

Say in your report that the golden set is deferred, and say who picks it up: **`kb-update-domain`
seeds it when the domain gains its first facts, in the same change.** A domain that gains content
without gaining a golden set has no oracle, and nobody will notice until a rename rots something
silently.

## Step 7 — Verify. The domain is not done until this is clean.

Run the engine's `scripts/check-kb` **against the library path** — the target is required, because
the engine holds no knowledge of its own and a silent default would report a clean run over zero
files. It checks frontmatter,
link resolution and slug uniqueness. Then run `scripts/check-scope <library>`. Report both
results verbatim.

State plainly what is **not** covered: a new domain has no facts yet, so nothing about currency,
contradictions or retrieval has been tested. A domain passing these checks is structurally sound —
it is not verified, and should not be described as if it were.

## Refusals

Stop and say so rather than proceeding, if:

- the knowledge root is unconfigured — never guess a path;
- the domain already exists — that is `kb-update-domain`;
- a library of that name is already installed under `kb/`;
- the tier is genuinely ambiguous and the user has not decided;
- you would have to invent a fact to fill the domain. An empty, well-formed domain is a good
  outcome. A domain full of plausible guesses is contamination of the one place facts are
  supposed to be trustworthy.
