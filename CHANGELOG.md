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
- ADR-0016: the library contract gets its own version (`MAJOR.MINOR`, today 2.0), a library declares
  the version it was built to (`kb_contract:`, read as 2.0 when absent), and rules apply by that
  version, so upgrading the engine never makes an older library unusable. Pinning becomes the library
  owner's choice; ADR-0015's pinning section is superseded. Decision only: the implementation follows,
  and this release waits for #71's rejection to be gated to contract 2.1.
- `kb-sources` retries with GET when HEAD answers any HTTP error except 429, and GET's answer
  decides. A server that answers HEAD with 400 (or 404, or 500) but serves GET is no longer queued as
  `source-unreachable`, and a source is `dead` only when GET also answers 404 or 410 (#74).

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
