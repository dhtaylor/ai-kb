# Changelog

What changed in each release of the engine. What a version number means, and how libraries pin the
engine, is [ADR-0015](documents/decisions/0015-releases-and-pinning.md). A domain library records the
engine release it was last verified against in its own release notes.

## Unreleased

Changes on `main` since v0.2.0. A contract or check change, so the next release is a minor bump
(ADR-0015).

- `sources/` holds only `.md` citation stubs, and raw artifacts are archived under `documents/`: now
  stated in CONVENTIONS §6, with the missing case for a local file or export, and in CONTRIBUTING.
  `check-kb` fails a non-`.md` file under `sources/` (#71).
- `analysis-tools`: the review skill owns its product-level calibration (which standards apply at
  Light, Medium and Full) and its five-point rating scale, which had lived in the intelligence-analysis
  library but are review procedure with no primary source. Bias remedies are retrieved from the rebuilt
  library, which states only the remedies its sources give.
- ADR-0016: the library contract gets its own version (`MAJOR.MINOR`, today 2.0), and a library
  declares the version it was built to (`kb_contract:`, read as 2.0 when absent). Rules apply by that
  version, and an engine supports the last two contract majors, so upgrading the engine does not make
  an older library unusable. Pinning becomes the library owner's choice; ADR-0015's pinning section is
  superseded. Decision only: the implementation follows, and this release waits for #71's rejection
  to be gated to contract 2.1.
- Contract version 2.0 (ADR-0016, step 1): CONVENTIONS states its version and gains §14, the
  contract's own changelog. A root `INDEX.md` may declare `kb_contract: "MAJOR.MINOR"`; absent is read
  as 2.0, and `check-kb` fails a malformed or unquoted value (a YAML reader turns a bare 2.10 into
  2.1). `kb-init` and `kb-create-domain` write the field into new trees.
- Contract 2.1 and version gating (ADR-0016, step 2). Rules apply by a library's declared
  `kb_contract`: #71's rejection of a raw file under `sources/` is contract 2.1, and only a warning
  for a library on 2.0. `check-kb` notes a library behind the newest version (with what the newer
  versions add, read from CONVENTIONS §14) and one ahead by a minor (checked by the newest rules
  known). A library on an unsupported major, or with an unreadable version, fails `check-kb` and is
  not served: `kb-libraries` gives it the state `unsupported-contract`. The session-start nudge names
  libraries behind or ahead. `kb-init` writes 2.1.
- `kb-sources` retries with GET when HEAD answers any HTTP error except 429, and GET's answer
  decides. A server that answers HEAD with 400 (or 404, or 500) but serves GET is no longer queued as
  `source-unreachable`, and a source is `dead` only when GET also answers 404 or 410 (#74).
- The session-start nudge reaches the person, not only the model (#79). `kb-due --nudge --summary`
  adds the nudge condensed to one line, which `kb-session-start` shows as its `systemMessage`, after
  any error message; the full nudge still goes to the model. A failing `kb-due` gives neither.
  ADR-0013 amended.
- Engine CI: the stamp-honesty step checks a pull request's base..head and no longer breaks after a
  force-push, whose `before` commit no longer exists; a push with an unresolvable `before` falls back
  to the merge-base with the default branch. Library CI already handled this.
- `kb-retrieve` reads the section that answers, not the whole file (#78). After routing picks the
  file, it outlines the file's headings with Grep and reads from the matching heading to the next one
  at the same level or higher, falling back to a whole-file read when no heading fits, two do, or the
  answer spans sections. Status markers and stamps sit inside the section read (CONVENTIONS §7, §8).
  `grade-routing` already counted a partial read; a regression case now pins it.
- `__pycache__/` is ignored, so an ad-hoc import of an engine script no longer leaves the engine
  checkout looking modified (#80).
- `kb-retrieve` rule 3 says what the knowledge base is: the registered libraries and a project's
  `knowledge/` tree, and not the engine repository, its decision records included. `grade-routing`
  fails a case with an off-KB read, meaning a Read, or a content-mode Grep result, of a file in no
  registered library. The engine's `CONVENTIONS.md` is exempt. A read in an unregistered library is
  now off-KB too, where before it was only "not in the KB" (#88).
- `check-kb`'s slug check, which stops a file sharing a folder's name, no longer looks in folders
  that are not the knowledge base, such as `.git/` and `documents/`. A library could not hold
  `hooks.md`, `refs.md` or `info.md`, because its own `.git/` has folders by those names. This is an
  engine fix, not a contract change (#90).
- `kb-create-domain` and `kb-audit` now ask the question CONVENTIONS §1 leaves to review: would a
  reader pick one of a comparative library's vendors instead of another, for the same job? Tools
  used together are not a category, and `check-scope`, which checks only the `vendors:` list's
  form, passes them. `kb-create-domain` asks it before writing `vendors:`; `kb-audit` files a
  scope misfiling on the root `INDEX.md` when a vendor fails it (#91).
- ADR-0017 amends ADR-0013: libraries may be kept current on an opt-in weekly schedule. The schedule
  runs detection and the preparation half of `kb-distill` and `kb-audit`, which drafts review packets
  in a headless run that has only read tools. A person decides each packet, and only then is a fact
  edited. A weekly report lists the decisions waiting. Decision only: the implementation is #95, #96,
  #97, #99–#103 (#98).
- Commands you can schedule (#95): CONTRIBUTING defines the property and lists `kb-verify --yes`,
  `kb-sources --yes`, `kb-watch`, `check-xlinks` and `kb-due`. Each is tested from `/` with a
  stripped environment. To meet it, `kb-watch` now exits 1 when a source drifted or was
  unreachable, where it exited 0 before. A wrapper that read 0 as "ran" should accept 1. `kb-verify`
  shows a failed assertion's output, and `kb-watch` shows old and new values, only at a terminal or
  with `--dry-run`. Queue and router writes replace the file in one rename, so a scheduled run never
  leaves a half-written queue beside a working session.

## v0.2.0 — 2026-10-16

The first tagged release. It covers everything from the first commit (2026-09-19) to this date;
`0.1.0`, the version the manifests carried until now, was never released.

### The contract and its decisions

- `CONVENTIONS.md` version 2: scope tiers, per-section provenance and currency, contradictions, the
  retrieval contract and the golden set, with a table of which rules are built and which are not.
- ADR-0001 to ADR-0015. Recent: a per-machine library registry (ADR-0014); what a release is and how
  library CI pins the engine (ADR-0015).
- `status: UNCORROBORATED · since:` for a one-source claim, served caveat first (#33).
- Comparative product libraries: `scope: product:<category>` with a `vendors:` list (#37).
- A domain may declare `agent_ttl`, so agent stamps can outlast a sweep (#30).

### Installing and running

- Libraries are installed by registration in `~/.config/ai-kb/libraries`, wherever they live, and
  can be moved between machines with `kb-library export` and `import` (ADR-0014; #25).
- The engine owns the library pre-commit hook (`library-hooks/`), wired through each clone's local
  `core.hooksPath`; registering never writes to a library.
- `kb-bootstrap` reports by default and changes nothing without `--apply`.

### Retrieval

- `kb-retrieve` treats the libraries its context lists as the complete set, refuses without an engine
  root or a library list, scopes every search to the library the routers chose, and quotes word for
  word what an answer rests on (#23, #26, #28, #32).
- The retrieval eval: `check-golden` on every commit (including reachability through the routers),
  and `grade-eval` and `grade-routing` for sampled agent runs, graded from tool calls and transcripts
  (#21, #22, #32, #36, #40).

### Currency

- `kb-verify` re-runs `Recheck:` assertions, reports and never repairs; it sets `KB_ENGINE_ROOT` for
  the assertions it runs, and warns about assertions that cannot fail (`WEAK`) or that reach outside
  their library (`OUTSIDE`) (#16, #20, #34, #41, #60, #65).
- `kb-sources` checks that external `Source:` URLs still resolve, fetching only with `--yes` (#24).
- `kb-due --nudge`, at session start, reports sweeps, rechecks, queue items, episodic notes, unstamped
  sources and stale facts with no assertion, and prints nothing when nothing is due (#29, #63, #64).
- `check-kb` derives and lints each file's `verified:` floor (#27).

### Guardrails

- `check-secrets`: credential patterns, an entropy pass and a personal-identifier pass, in staged,
  worktree, file and full-history modes. Raw artifacts archived in a library skip only the bare-entropy
  rule, and UTF-16 text is blocked as unscanned (#56).
- `kb-capture` refuses a note that holds a credential or a personal identifier.
- `check-blast` gates high-blast-radius changes behind an `owner-approved` label;
  `kb-create-domain` now creates that label in a new library's repository (#68).
- A regression suite of 498 cases runs in every commit hook and in CI.

### Plugins

- `knowledge-tools` 0.2.0: five curation skills (`kb-create-domain`, `kb-update-domain`,
  `kb-organize-domain`, `kb-distill`, `kb-audit`) and the `kb-retrieve` agent.
- `analysis-tools` 0.2.0: analytic-rigor review and intelligence-analysis coaching over the
  intelligence-analysis library.
