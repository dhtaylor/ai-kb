---
name: knowledge-conventions
description: The contract every knowledge domain conforms to — scope tiers, layout, router, granularity, slugs, provenance, currency, contradictions. Enforced by kb-organize-domain; conformed to by kb-update-domain, kb-distill, and every retrieval agent.
memory_type: reference
domain: meta
scope: general
metadata:
  type: reference
  node_type: contract
  created: 2026-07-08
  revised: 2026-09-19
tags: [knowledge, conventions, progressive-disclosure, provenance, currency]
keywords: [conventions, INDEX, router, slug, scope, verified, CONFLICTED, provenance, gestalt]
---
# Knowledge Conventions

**Version 2.** Supersedes [knowledge-conventions-v1](documents/legacy/knowledge-conventions-v1.md) (the inherited work-system contract, preserved at
`documents/legacy/knowledge-conventions-v1.md`). v1 governed a single-root, annotation-only KB; v2 folds in
the scope tiers, cross-root resolution, currency stamping, and retrieval contract required by the
knowledge-agent architecture.

**Precedence:** the combination plan is the design authority; this file is the operative contract derived
from it; skills conform to this file. When a skill and this file disagree, **this file wins**. When this
file and the plan disagree, the plan wins and this file is amended — not worked around.

This file governs the **semantic** tier. Three conflicts between v1 and the plan were decided explicitly:
slug resolution is now **root-scoped by filename** (§5, was name-field-global); contradictions become
**unretrievable, not merely annotated** (§8, was flag-in-place); and a file remains a **gestalt** while
**currency moves to the section** (§4, §7) — because one verification date cannot honestly cover twelve
facts of differing volatility.

**Skill names changed on 2026-09-21.** Every skill now carries the `kb-` prefix, so the working set
reads as one family. Records written earlier — ADRs, session notes, archived evidence — keep the names
that were true when they were written, because a record is evidence and evidence is not rewritten:

| Former | Current |
|---|---|
| `create-domain` | `kb-create-domain` |
| `update-domain` | `kb-update-domain` |
| `organize-domain` | `kb-organize-domain` |
| `distill-episodic` | `kb-distill` |
| `meditate` | `kb-audit` |

`meditate` became `kb-audit` rather than `kb-sweep` deliberately: an audit inspects and reports, and
nobody expects an auditor to fix the books. The name reinforces the one rule it is most tempted to break.

## 1. Scope tiers — answered at capture, never retrofitted

*Rationale: [0003-scoping-topology](documents/decisions/0003-scoping-topology.md) for the three homes and why the project nests inside the general root; [0004-scope-attribute](documents/decisions/0004-scope-attribute.md) for the values and what enforces them.*

Every fact carries a `scope:`. The classification test, asked when the fact is written:

> *Is this true only of this repo/deployment, or true wherever this product/tool/concept appears?*

| `scope:` value | Meaning | Home |
|---|---|---|
| `repo:<project>` | True only of this deployment — topology, deploy quirks, this system's bugs | `<project>/knowledge/` |
| `product:<vendor>` | True wherever that vendor's product appears | general root |
| `org:<company>` | True across the organization — standards, architecture rules | general root |
| `general` | Domain fundamentals, engine/platform behavior | general root |
| *(personal)* | An individual's working style and private lessons | `~/.claude/` — **not** team-shared, never in either KB |

**`product:<vendor>` and `general` are not separated by the words above.** For a single-vendor
engine, "that vendor's product behavior" and "domain fundamentals" describe the same sentence. The
test that does separate them:

> *Would this fact stop being true if you swapped the vendor or product?*

**Yes → `product:<vendor>`** — how a specific database implements snapshot isolation.
**No → `general`** — what serializable isolation means, or what the standard requires.

They are not interchangeable: §9 applies different promotion guards, and a vendor fact filed as
`general` is a claim about the whole world inferred from one product. Never classify from the
vocabulary a requester happened to use.

**The three homes, and the one rule that makes them work:**

- **General** — a **domain library**, installed under the engine at `<engine>/kb/<domain>/`. Each
  library is its own repository holding exactly one domain, and is self-contained: its facts, its
  sources, its archived evidence and its golden set travel together, so it can be cloned onto a
  machine with no engine and no sibling libraries and still make sense.
- **Repo** — `knowledge/` inside the project repo, travelling with the clone.
- **Personal** — user-level config.

**A library is one domain, and a domain is one tier.** Every file in a library carries the same
`scope:` as the library itself. A `repo:` fact filed in a general-tier library is a claim about every
deployment inferred from one; a `product:` fact filed as `general` is a claim about every product
inferred from one. Both read as ordinary facts and neither announces itself, which is why
`check-scope` enforces the agreement rather than trusting it.

**A project tree obeys the mirror rule.** A library is its own repository and a general-tier home, so
`repo:` is wrong there. A project tree sits inside the project's repository and is the repo-tier home,
so **anything but `repo:` is wrong there** — a fact true beyond one deployment, filed into one project,
is one of N copies that will drift. `check-scope` tells the two apart by structure (does the tree have
its own `.git`?), not by name or path.

**Behaviour is not one of the homes.** The engine (this contract, the tooling, the skills) holds no
domains at all. Mixing them would be the very thing §0 of the design forbids — knowledge and
behaviour in one place — and the engine is where the separation has to be observed most visibly,
because everything else follows its example.

**Never write a literal path.** A hardcoded absolute path is correct on exactly one machine and fails
silently everywhere else. But agent bodies do **not** write `$KB_ENGINE_ROOT/...` either — see below.

**Resolution mechanism — settled by the Phase 0 acceptance test (2026-09-19), see
[0001-kb-root-resolution](documents/decisions/0001-kb-root-resolution.md), and extended to every
consumer by [0008-machine-bootstrap](documents/decisions/0008-machine-bootstrap.md):**

1. **One command writes every location: `kb-bootstrap`.** The engine is wherever that script lives, so
   nothing is typed and nothing is typed twice. Run once per machine, and again if the engine moves.
   Hand-editing any of the locations below is how two of them come to disagree.
2. `KB_ENGINE_ROOT` is set in **user-level settings** (`~/.claude/settings.json` `env`), not a project
   file — a project file is a trust-root hazard, since a repo could repoint every agent's canonical
   knowledge.
3. A **SessionStart hook, which lives in the engine** (`scripts/kb-session-start`, so it is versioned
   with the contract it announces), injects the **absolute path** into session context. Agents use
   *that* path. This is required, not cosmetic: **the Read tool does not expand environment variables.**
   Handed `$KB_ENGINE_ROOT/...` it fails with "File does not exist" and helpfully reports the working
   directory — inviting a relative-path retry that succeeds by coincidence in one workspace and breaks
   in every other. The hook removes the variable from the path-handling path entirely.
4. **Git hooks resolve the engine through `git config --global kb.engineRoot`**, after the environment.
   Git reads its global config in every context — terminal, IDE, GUI client, cron — and no shell startup
   file does: a stock `~/.bashrc` returns before its exports for any non-interactive shell, so a hook
   fired by anything but a human's own terminal would silently skip its checks.
5. **Absence is graceful and loud.** Unset or pointing nowhere: the session hook warns at session start
   and instructs agents to report the engine as unconfigured — never to guess a path, never to fall back
   to a relative one. A git hook says which command fixes it.

So: no file anywhere contains a literal KB path, no agent ever handles the variable itself, and every
place that needs the location is written by one command from one source.

A project fact that depends on a general fact **links to it** (§5), never restates it. The
single-canonical-home rule (§4) spans the KB boundary.

## 2. Domain layout

- **A domain library is a repository, and its root is the domain.** There is no `semantic/` tier
  folder and no chain of routers above it: `INDEX.md` at the library root is the domain router and
  the entry point, always the first file loaded. Libraries are discovered by their presence under
  the engine's `kb/`, not by a registry that would need maintaining.
- Content lives in **single-topic files** sized as described in §4.
- When a domain's topic files exceed **~15**, group the overflow into a sub-folder with its own
  sub-index. Below that threshold, stay **flat** — every sub-folder adds a routing hop.

## 3. The router (`INDEX.md`)

Every folder — the domain root and each sub-folder — carries an `INDEX.md` that lists **only its
direct children**, one line each, and nothing else. A reader descends the tree one hop at a time,
loading the minimum at each level, never a monolith.

Each record is a hooked pointer:

- a **leaf** file: `- [key](child.md) — one-line hook (what it answers)`;
- a **sub-folder**: `- [key](subfolder/INDEX.md) — what lives under here`.

`key` is the child's slug (§5). The hook must **disambiguate siblings** — two children must never be
distinguishable only by a shared prefix.

**Descent rule:** load a folder's `INDEX.md`, pick the one child whose hook fits the question; if
that child is itself a sub-index, load it and repeat.

The router holds routing signal and **domain configuration** only — no stored facts. A domain root
`INDEX.md` additionally declares, in its frontmatter:

```yaml
freshness_horizon: <N days>   # the domain's TTL floor; volatile deployment facts decay in days,
                              # fundamentals in years. One interval for the whole library is wrong.
verifier_budget: <N>          # max facts re-checked per verification cycle, highest score first.
                              # Without a cap the cadence grows unbounded as domains multiply.
```

Cross-cutting material that isn't a routing decision lives in its own child doc, listed like any other
record: unresolved items in `<domain>-open-questions.md`, the contradiction register in
`<domain>-contradictions.md` (§8). Create these state leaves **only when they hold content** — don't
route to an empty file.

The knowledge base carries one root-level state leaf, `needs-attention.md` — the queue a sweep builds.
It is **a file like any other**: full frontmatter (§11) carrying the library's own `domain:` and
`scope:`, routed from the library's own `INDEX.md`,
because a queue that is itself an orphan is the first thing the next sweep will report. It belongs to
the library it describes, not to the engine. Like every state leaf it
exists only when it has content.

Within a library the recursion is the same at every level: a sub-folder's `INDEX.md` lists its own
direct children. There is no router **above** the library root — no tier folders, no
`semantic/INDEX.md`, no registry of libraries. A library is discovered by being installed under the
engine's `kb/`, and the session-start hook enumerates what is present (§2).

Two things inside a library are deliberately **not routed**: the golden set (§10) and archived
evidence under `documents/` (§6). They are apparatus and provenance, not knowledge — and routing the
golden set would let a retrieval agent read the answers it is being tested on. A sweep must not
report either as an orphan.

**Bound the index.** Above the ~15 threshold, split into sub-indexes so an agent loads only the relevant
one. The fixed agent preamble plus the INDEX belong in the cacheable prefix so repeat queries don't re-pay
for them.

## 4. Granularity — a file is a gestalt

- **One fact, one home.** A fact is stated in full in exactly one file. Everywhere else it is
  referenced with a one-line `[[cross-link]]` at the point of use — never restated.
- A file is right-sized when it can be loaded on its own to answer a real question, yet still holds a
  **coherent whole** rather than one fact per file. Don't over-fragment a coherent model to honour the
  rule: an entity catalog, its relationship diagram, its business rules, and its code tables usually
  belong **together** because they are loaded together. Split out only what is genuinely queried alone
  (e.g. process flows, gotchas).
- **Consequence:** a file holds several facts of differing volatility and differing provenance.
  Therefore provenance (§6) and currency (§7) attach to the **section**, not the file.

## 5. Slugs & cross-root links

- **`slug` = the filename without `.md`** (or the folder name). Not a frontmatter field.
- **Bare `[[slug]]`** resolves within the KB root it appears in. Filenames are therefore **unique within
  a root** — which is why per-domain state leaves take a domain-prefixed *filename*
  (`<domain>-contradictions.md`), not a prefixed frontmatter name.
- **Path-addressed files are exempt.** Two kinds of file are reached by **relative path**, never by
  `[[slug]]`: the `INDEX.md` routers (every folder carries one, §3, so the basename necessarily repeats)
  and this contract at the KB root. Because nothing resolves *to* them, nothing can resolve ambiguously,
  so they keep their conventional discoverable filenames and carry a descriptive `name:` instead of one
  matching the filename (`<domain>-index`, `sources-index`, `knowledge-conventions`). `check-scope`
  exempts them from the within-root uniqueness check and **fails any `[[slug]]` that targets one** — cite
  the contract by path, or cite the specific fact that restates its rule.
- **Cross-library links name the library:** `[[<library>:<slug>]]`, e.g.
  `[[claude-code-runtime:behaviour-loading]]`. The prefix names the **library**, not a tier — the older
  `[[general:slug]]` form came from a two-root model where "general" identified a single tree; with N
  libraries installed it identifies nothing.
- **Slugs need be unique only *within* a library.** Cross-library uniqueness is **not** required, and
  the rule that once demanded it is obsolete: an explicit prefix is mandatory for every cross-library
  reference, so `[[a:foo]]` and `[[b:foo]]` cannot be confused. A bare `[[slug]]` never leaves the
  library it is written in, so there is nothing left to collide.
- **No manifest.** A generated slug→path manifest was specified so a consumer could resolve against a
  *remote* root without scanning it. Every installed library is local, under the engine's `kb/`, so
  resolution is a directory scan and a manifest would be committed state that can go stale for a
  problem that no longer exists. Add one when a remote library exists to justify it.
- **Resolution runs one level up.** A library cannot see its siblings, so `check-kb` skips prefixed
  links by design and `check-xlinks` resolves them across the whole `kb/` directory. That split is not
  an implementation detail: it is why a library remains checkable on its own.
- **Graceful absence is a distinction, not a leniency.** A link into a library that is **not installed**
  is a *soft dependency*: it warns, and agents continue. A link into a library that **is** installed but
  lacks the slug is **dead** and fails. Collapsing the two would punish portability — a machine need not
  hold every library — while treating both as warnings would let real rot accumulate unseen.

## 6. Provenance — every fact is traceable

- **Granularity: per-section, per-fact on exception.** Each topic block/heading carries a
  `Source: [[slug]]` backlink. A fact whose origin differs from its section gets its own inline
  `[[slug]]` backlink.
- **Dedup merges provenance.** When two copies of a fact collapse into one canonical home, keep
  **all** contributing `[[source]]` links — never drop a citation in a merge.
- **Corroboration keeps its own stamp.** When a second source confirms a claim the KB already holds,
  it is recorded as its own `Source:` line with its own `Verified:` line beneath it — the pairs
  stack, they do not merge. Two sources checked on different dates by different methods are two
  pieces of evidence, and flattening them into one stamp discards which was verified when.
  (Conflicting sources are a different case entirely — §8.)
- **Sources are `[[slug]]` backlinks.** Episodic notes already *are* sources — link straight to them
  (`[[YYYY-MM-DD-domain-notes]]`). An external artifact with no home in the KB (a spec, vendor page, PDF)
  gets a lightweight stub under **`knowledge/sources/`** so its backlink resolves. Don't create a stub for
  something already in the KB.
- A source stub (`sources/<slug>.md`, inside the library) records: title, origin (URL / page-ID /
  filename), date ingested, and where the artifact itself lives.

**Citing an artifact — three cases, and only one is hard.**

1. **Inside this library.** A `[[slug]]` or a relative path. Nothing special.
2. **Never in any repository** — a vendor page, a spec, a PDF. The stub records *origin* (URL,
   page ID, publisher, date ingested) and no filesystem path, because there is not one.
3. **In another repository.** Two rules, in this order:
   - **Evidence travels with the domain it was folded from.** Archive the artifact inside the
     library, under `documents/`. This is **not** a single-canonical-home violation: the rule is
     one home per *fact*, not per *document*. A fact stated twice drifts because someone edits a
     copy; an archived artifact does not, because if it changes it is a new artifact with a new
     ingestion date. A library that carries its own evidence resolves every citation on any machine.
   - **What genuinely cannot travel gets a repo-qualified reference** — `ai-kb:CONVENTIONS.md`,
     `<repo>:<path-within-repo>`. **Never a relative path across a repository boundary**: that
     resolves only while two repositories happen to sit in the expected layout, and fails silently
     everywhere else. The qualified form degrades honestly — without the other repository you still
     know exactly what was cited and where it lives, you simply cannot open it from here.
- **Provenance rots.** `check-links` covers internal `[[slug]]`s, not external `Source:` URLs. External
  URLs get cheap **HTTP HEAD liveness checks**; a dead URL marks dependent sections
  `provenance: BROKEN`, which the hygiene sweep treats as **unverified**. A 404 is an alert, not silence —
  "unreachable" and "unchanged" are never conflated.

## 7. Currency — stamped per section, with evidence

*Cadence policy — per-domain TTLs, verifier budgets, trust tiers and the detection-vs-mutation gate: [0005-currency-cadence](documents/decisions/0005-currency-cadence.md). None of it runs yet.*

Provenance says where a fact came from. Currency says whether it is still true. They are different
questions and they attach at the same granularity (§4).

Each section that carries a `Source:` may carry a stamp directly beneath it:

```
Verified: 2026-09-19 · by: agent · method: query
```

- **`method:`** is one of `query` (re-run against the live system), `integration-test` (a real transaction
  against staging — the only thing that catches a vendor changing runtime behavior without touching its
  docs), `doc-review` (external source re-read), or `manual`.
- **Evidence, not just a date.** Every re-stamp records the **exact check run, the observed value, and the
  expected value** in a companion record. A stamp whose check queried the wrong source is worse than no
  stamp. **No evidence, no re-stamp.**
- **`by:` is derived from the git committer identity**, not a free-form claim — a field is trivially
  forged, an identity is not. CI rejects a commit writing `by: human` from the agent identity.
- **A section may carry a re-check assertion**, directly beneath its stamp:

  ```
  Recheck: env -i HOME=$HOME PATH=/usr/bin:/bin bash -lc '[ -z "${KB_ENGINE_ROOT:-}" ]'
  ```

  It is an **assertion, not a query**: exit 0 means the fact still holds, non-zero means it no longer
  does. `kb-verify` runs these, so the evidence rule above is satisfied mechanically — the exact check
  is *in the file*, beside the claim it defends, and is reviewable in the diff that introduced it.
  Write one only where a command can actually decide the claim; most facts cannot be settled by a
  shell and should carry none. **An assertion that cannot fail is worse than none**: it manufactures
  freshness on a schedule.

  Two rules make this safe to run. **A failing assertion is reported, never applied** — a verifier
  that rewrites a fact it has just contradicted destroys the evidence that something changed; a human
  decides between a stale fact, a wrong assertion and a real contradiction (§8). And **the commands
  are printed and approved per run**, because a library is content that travels between people:
  running one executes its author's shell on your machine.
- **Trust tiers.** Agent-verified TTL is materially shorter than human-verified (**1/10th**).
  **High-blast-radius** facts — deploy targets, environment routing, credential references — require
  **human** re-verification regardless of any agent stamp.
- **Absent ≠ fresh.** A section with no stamp is `unknown`, and ranks **ahead of a merely stale one**
  in the attention queue — absence hides more easily than age. "Ahead of stale" is the claim, not
  "ahead of everything": a contradiction being actively served outranks both, and the full ordering
  belongs to the sweep that builds the queue.
  a sweep cannot flag what was never written.
- **A floor over nothing is `unknown`.** If no section in the file carries a stamp — every claim in
  it became `CONFLICTED`, or none was ever stamped — the frontmatter reads `verified: unknown`. It
  never keeps a date inherited from before the stamps went away: that date now certifies nothing and
  reads as freshness the file does not have.
- **File frontmatter carries `verified:` as the floor** — the oldest stamp among the file's sections
  that are not `CONFLICTED` (a disputed section is not served, so its stamp certifies nothing a reader
  can get), derived and lint-checked. Sweeps grep one field; the sections hold the truth.

## 8. Contradictions — make them unretrievable, not merely annotated

A register beside the facts is not a control: **the retrieval path never reads it**, so an agent still
serves one of the conflicting values with confidence. When two sources disagree and you cannot verify
which is right:

- do **not** silently pick a winner, and do **not** edit a subordinate source of truth to match;
- mark the conflicting section **inline** with `status: CONFLICTED`, **dated on the line it is raised**
  (`status: CONFLICTED · since: YYYY-MM-DD`), stating both claims, the risk of each, and how to
  verify. The date is not decoration: a contradiction's age drives its escalation, and nothing else
  in the file records when the dispute began;
- **retrieval agents refuse to serve a `CONFLICTED` section** — they surface the conflict instead. The
  golden set (§10) carries an UNRESOLVED case proving this behavior;
- **mark the narrowest unit that holds the disputed claim.** A `CONFLICTED` section is refused
  *wholesale*, so a single disputed value sitting among sound facts takes its neighbours down with
  it — an agent goes blind to correct knowledge because something nearby is in doubt. If a disputed
  claim shares a section with undisputed ones, **split it into its own subsection** so only the
  claim in doubt is withheld. Collateral refusal is a bug, not an abundance of caution;
- **a status marker applies to the heading it sits directly under — never to the headings enclosing
  it.** A marker under `### Default sample size` withholds that subsection; the rest of the `##`
  section above it stays retrievable. When you split a claim out, add a `positive` golden case for a
  sibling fact left behind, so the eval proves the neighbours are still served;
- register a one-line flag + pointer in `<domain>-contradictions.md`, routed from the library's
  `INDEX.md` like any state leaf (§3); the canonical note stays in the file that owns the topic.

**Blocking vs. informational.** A contradiction on a fact actively needed is *blocking* and names who
resolves it and via what artifact. A blocking contradiction **must be cleared before its domain is
promoted to the general tier** (§9). Flagging forever just accretes.

**Moves of a load-bearing fact are verbatim** — paraphrasing during a reshape can manufacture a new
contradiction. An LLM fold can round a constant, drop a qualifier, or merge two behaviors into one
generalization: load-bearing values are **copy-pasted**, and each extracted fact is **human-diffed against
its source** before commit.

## 9. Promotion — repo tier to general tier

Knowledge usually *starts* repo-specific and later proves general. Promotion moves the fact to the general
root and leaves a backlink at the origin. Two guards:

- **No circular promotion.** The confirming evidence must be **external to the KB** — a live vendor URL
  with excerpt, a direct system result, or a named human attestation with external citation. If the
  evidence is *another KB file*, the promotion is **rejected**. The KB may never be its own evidence for
  general-tier truth. One observation is not a general truth.
- **Atomic promotion.** The general-root add and the origin-stub update are a **single paired commit** —
  otherwise the dual-root resolver finds both the promoted copy and the full pre-promotion copy in the
  gap, silently undoing the dedup. The origin becomes an **empty redirect stub** that cannot answer
  queries: agents follow the link, never serve stub content.

Promotion is **never automated**. Neither is resolving a contradiction, nor deleting knowledge.

## 10. The retrieval contract

Every retrieval agent's body states, and every agent is held to:

> *Your knowledge lives in the libraries installed under `<engine>/kb/`, and in the project's own
> `knowledge/` tree. Load INDEX, descend to the relevant file(s), cite them, then act. Do not answer
> from memory.*

- **Cite every file used.** "file(s)" is plural deliberately: an answer may need a general-tier fact *and*
  a repo-tier fact. State when an answer is **partial**.
- **Load only the libraries the question touches.** A question about one domain must not pay for
  every installed library; a question spanning a project fact and a library fact loads both.
- **On absence:** answer *"fact not found — check KB"*. Never fill the gap from model memory — nor from
  the code, config or scripts around the knowledge base. Reading the source is the caller's job; a
  retrieval agent that reads it answers correctly and hides the gap.
- **On a fact held only in an episodic note:** the answer begins *"Not established in the knowledge
  base"*, never with yes or no, and reports observed and believed-but-untested material as such.
  A session note is a record; distillation decides what in it is a fact, and retrieval must not
  promote what distillation refused.
- **On a hedge in any file:** a claim the file itself marks untested, inferred or probable is reported
  as such and never leads the answer — a `Verified:` stamp beside it dates what was checked, not what
  was inferred. **Never chain facts from two files into a conclusion neither states.**
- **On `CONFLICTED`:** surface the conflict, serve nothing (§8).
- **Surface the `verified:` date** on freshness-sensitive facts.

**The golden set** lives at the library root, `<domain>-golden.md`, and travels with the domain it
tests. The `-golden` suffix is load-bearing: a **folder name is a slug too** (§5), so a file named
`<domain>.md` would collide with the library's own directory name. It is **not routed from the
library's `INDEX.md`** — an agent that can descend to the oracle can read the answers, and its
refusals then prove nothing. Each record carries:

```yaml
- case: positive | negative | unresolved | cross-root
  question: <what is asked>
  expected_file: <the file that must answer it>
  expected_excerpt: <text that must appear, grep-verifiable against expected_file>
```

`case:` is required — a minimum of "≥2 negative cases" is unenforceable if nothing marks a case as
negative. For a `negative` case, `expected_file` may be empty and `expected_excerpt` holds the
refusal the agent must produce.

Every domain carries **≥2 negative cases** — a knowledge base that never refuses is one that guesses.

An **`unresolved` case is required only where the domain actually holds a `CONFLICTED` section**, and a
**cross-root case only where the domain actually links across libraries** — a domain with no contradiction and no
cross-library link cannot have either without fabricating one, and a golden case invented to satisfy a
count is worse than an absent one — it tests a fiction and reports success. Where either does not
apply, say so in the file, with the reason.

**Excerpts are matched with whitespace normalised**, so an excerpt may span a hard-wrapped line in the
source. It may **not** contain markdown markup: emphasis exists in the file and never in a spoken
answer, so an excerpt carrying it tests formatting rather than grounding. The golden set updates **in the same commit** as any
file rename or split — an `kb-organize-domain` exit criterion — or the oracle rots.

Two tiers test it, and they are not interchangeable:

- **Deterministic routing check** (every commit, no LLM): INDEX entries and `[[slug]]`s resolve to the
  expected file.
- **Answer-grounding eval** (scheduled, sampled): the agent runs; its answer must contain the
  `expected_excerpt`, **verified by grep against the expected file** — not by an LLM judge. This is what
  catches answering from memory.

The golden set is a fire alarm on fixed questions. The **embedded-fact lint** over agent and command
files — flagging identifiers, numeric constants, environment-specific values and credential-shaped
strings — is the actual lock. An inlined schema routes correctly and passes every eval.

## 11. Frontmatter schema

Every semantic/reference file carries:

```yaml
---
name: <kebab-case — matches the filename; path-addressed files excepted, see §5>
description: <one line — what this file answers, disambiguating from siblings>
memory_type: semantic        # or: reference
domain: <domain>
scope: <repo:<project> | product:<vendor> | org:<company> | general>
verified: YYYY-MM-DD         # the floor: oldest section stamp in this file (§7)
metadata:
  type: <fact | reference | ...>
  node_type: memory
  created: YYYY-MM-DD
tags: [<domain>, <topic>, ...]
keywords: [<retrieval terms an agent might grep for>]
---
```

Section-level `status: CONFLICTED` (§8) and `provenance: BROKEN` (§6) are written **inline at the
section**, not in frontmatter — they describe a claim, not a document.

`tags`/`keywords` exist so retrieval can route by grepping frontmatter — keep them from a shared
vocabulary within a domain, not ad-hoc per file.

## 12. Naming

Files are kebab-case and **self-describing** (`data-model.md`, not `bnp-ontology.md`). The name should
tell a cold reader what's inside without a parenthetical. Since the filename *is* the slug (§5), it must
be unique within its root — per-domain state leaves take a domain prefix. The path-addressed files of §5
(`INDEX.md`, `CONVENTIONS.md`) keep their conventional names and are exempt.

## 13. Verifying a domain

A domain is not "done" until these pass clean. The full rule set `check-scope` owes, marked built or
to-build, is in [0004-scope-attribute](documents/decisions/0004-scope-attribute.md).

| Check | What it proves | Status |
|---|---|---|
| frontmatter lint | required fields present, `name` matches filename | **built** — `check-kb` |
| `check-links` | `[[slug]]` and router links resolve **within one library** | **built** — `check-kb` |
| slug uniqueness | no filename collision, and no file colliding with a folder name | **built** — `check-kb` |
| orphans | every file reachable from the root `INDEX.md` by router links; golden set and `documents/` exempt (§3) | **built** — `check-kb` |
| embedded-fact lint | no facts inlined in the behaviour layer | **built** — `check-embedded-facts` |
| secret scan | staged, worktree, or every blob in full history | **built** — `check-secrets` |
| executable bits | hooks and scripts recorded 100755, so a clone is not silently unguarded | **built** — `check-exec-bits` |
| hygiene sweep | stale and missing stamps, ageing contradictions, golden-set rot, doubly-routed files | **built** — the `kb-audit` skill |
| `check-scope` | `scope:` values well-formed; every file agrees with its library's tier; no relative link climbing out of a library | **built** |
| `check-xlinks` | `[[library:slug]]` resolution from any tree — the installed libraries and each project tree passed to it — into the installed libraries; dead links fail, absent libraries warn | **built** |
| routing check | golden-set questions actually route to `expected_file` | **to build** |
| answer-grounding eval | the agent's answer contains `expected_excerpt`, grep-verified | **to build** |
| re-check assertions | a stale section's `Recheck:` still exits 0; failures reported, never applied | **built** — `kb-verify` |
| external `Source:` liveness | cited URLs still resolve; a dead one marks dependants `provenance: BROKEN` | **to build** |

Eleven of fourteen are built. A library passing the built checks is **structurally sound within itself**
— it is not verified. Nothing yet proves an agent retrieves rather than answering from memory, which
is what the last two rows are for.
