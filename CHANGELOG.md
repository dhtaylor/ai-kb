# Changelog

What changed in each release of the engine. What a version number means, and how libraries pin the
engine, is [ADR-0015](documents/decisions/0015-releases-and-pinning.md). A domain library records the
engine release it was last verified against in its own release notes.

## Unreleased

- ADR-0020 (#148): a library says where each library it links to comes from, and a consumer's copy
  of someone else's library can be registered read-only. A link into a same-named library from a
  different origin is reported as a dependency mismatch and warns, rather than failing as a dead
  link the consumer can't fix. A read-only library is served as usual, but this machine doesn't
  curate it: the hook refuses commits, nothing writes into it, and nothing nudges about it.
  Delivered in steps: the read-only role, then `links_to` (contract 2.6), then `--ref` pinning.

- A project's `knowledge/` tree kept as a read-only archive can drop out of the session-start nudge
  (#141). Declare `archived: <date or reason>` in its root `INDEX.md`. The nudge then skips it, and
  plain `kb-due` lists it as `archived`. Before, it was nudged every session to sweep, stamp and
  declare a contract, none of which a frozen tree can do. A registered library is served whatever
  it declares, so it is nudged as usual and told to use `kb-library remove`. This is a `kb-due`
  setting, not a contract change.

- The session-start nudge names only the unstamped sources that are new since a library's last
  sweep (#142). It used to give the whole standing count at every session start. In a large install
  that is hundreds of sources that only an owner can stamp, and the same line every day hid the
  ones that were new.
  - The sweep is the commit that last changed `last_swept` in the library's `INDEX.md`, read from
    git, so kb-audit records nothing new. A sweep not yet committed leaves nothing new.
  - A source is matched by its section heading and `Source:` line, not by its file, so a section
    that kb-organize-domain moved isn't new.
  - A library never swept, or not in git, still gets the full count. Plain `kb-due` now shows the
    full count per library too.

- The secret scanner no longer blocks a fully qualified SQL name such as
  `catalog.dbo.table.TermConfig` (#140). A mixed-case column at the end made the whole name read
  as a random string. A dotted name of three or more identifier segments is now judged segment by
  segment, and passes when no segment would be flagged on its own. A JWT is three dot-separated
  segments too, but each one is random-looking, so it is still caught.

- A topic a library never holds is now found for you (#147, P1). In a field A/B, naming such a
  topic in the root `Not covered here:` line cut the same question from 16–23 turns to 3, but
  nothing told a librarian which topics those were.
  - `kb-telemetry` counts the kb-retrieve runs that answered `fact not found`. `--not-found` lists
    them by library, costliest first, with each run's question and whether it hit the search
    limit. A specialist's `not mine` is a routing miss and isn't listed. Only `--not-found` prints
    a question, and nothing prints an answer or a file's text.
  - The weekly report (`kb-report`) gives each library's not-found runs from the past 7 days, with
    their count, their cost and the command that lists them. A person decides what each one is:
    an absent topic for the line, or a fact the library should hold. The report holds no question
    text.

- `kb-retrieve` bounds the search for a fact that isn't there (#147). A search across a whole
  library now lists matching files first (`files_with_matches`), then reads or searches inside the
  likeliest one to three. A content search across a large library overflowed and was read back
  whole. And it stops after 8 file reads or 5 library-wide searches with nothing that answers: it
  answers `fact not found`, and ends its `Looked at:` line with `(search limit reached)`. Field
  runs on a ~440K-word library took 16–33 turns to reach the same `fact not found`.
  The limits are per question, counted across every library searched. In a field test a question
  across three libraries made 10–12 library-wide searches without reaching 5 in any one.

- CONVENTIONS §5: a `[[slug]]` names a file, never a folder. The old "(or the folder name)" said
  otherwise, but no check ever resolved a folder. A folder name is still reserved, so no file may
  share it. kb-organize-domain now says to repoint inbound links when a split turns `foo.md` into
  `foo/` (#151). No contract version change: nothing a library may hold changes.
- kb-audit, kb-update-domain and kb-organize-domain run `check-xlinks --installed`, as the hooks
  do, in place of `check-xlinks <kb-root>`. That missed libraries registered outside `kb/`, and
  invited the library-folder mistake #151 reported.

- `check-xlinks` no longer passes a library's own folder given as `<kb-root>` (#151). It read the
  library's sub-indexes as libraries, scanned none of its files, and exited 0 over dead links. A
  `<kb-root>` with an `INDEX.md` is now a usage error (exit 2) that names
  `check-xlinks --installed <path>`, which checks an unregistered library against the registered
  ones.

- Contract 2.5 (#154): every section with content in a fact file carries a `Source:` line.
  Before this, nothing checked for one. A section with no `Source:` was never counted as
  unstamped, so the `verified:` floor ignored it, and one stamped section could date a file whose
  other sections were never sourced. `check-kb` fails such a section from 2.5 and warns below it.
  The intro under the `#` title, a heading with only subheadings under it, and a `CONFLICTED`
  section are exempt. `kb-due` counts unsourced sections, and `kb-audit` queues them at severity 4
  beside unstamped facts. `kb-init` writes 2.5. Library PRs follow.

- Contract 2.4 (#120): a source stub may carry `- **Liveness:** manual` for a source a script cannot
  check, such as a page behind a sign-in wall. `kb-sources` doesn't fetch it, and lists and counts it
  instead of queuing it. `kb-report` lists these stubs while the library's sweep is due, so a person
  checks them once per sweep interval. `check-kb` fails a `Liveness:` value other than `manual` from
  2.4, and warns below it. `kb-init` writes 2.4. Library PRs follow.

- `kb-sources` no longer calls a source alive when its URL redirects to a sign-in page. A final
  URL whose path has a `login`, `signin`, `sso` or `UserLogin` segment, or `/oauth2/authorize`, is
  `unreachable` and queued as `source-unreachable`. A login page answers 200, but it is not the
  source. Before this, a page behind single sign-on passed every run (#120).

- ADR-0019: ai-kb-architecture, the engine's reference library, takes the engine's release tag.
  From v0.4.0 both repositories are tagged `vX.Y.Z` on release day, so the library goes from v0.2.0
  to v0.4.0. Published tags are not moved. The ADR lists the release-day steps for both repositories.

- Retrieval by triage and specialists, proposed in ADR-0018 (#130):
  - `scripts/kb-catalog` prints one compact catalog of the registered libraries: each one's name,
    scope, description, `Not covered here:` line and router topics. A library that is registered
    but not served is named.
  - `kb-retrieve` has a specialist mode. When a prompt begins `SPECIALIST: <library>`, the agent
    reads only that library. It answers `not mine` after reading the root router if the topic is
    outside the library, and it reports links into other libraries without following them.
  - The new `kb-ask` skill is the default way to retrieve. It reads the catalog, sends the
    question to one specialist (a second only when needed, never more than two), and passes the
    answer back word for word. `kb-retrieve`'s description now names it as the specialist, to be
    called directly only when the library is already known.
  - `check-tool-scope` has a `triage` tier (Bash, Agent) for the desk, which reads no library
    itself.

- `scripts/check-transient` reports fact-file headings that carry a date (`YYYY-MM` or
  `YYYY-MM-DD`) or a change or work-item id (`PR`, `MR`, `WI` and a number): the shapes a
  changelog or a snapshot takes in a file that should state current state. It is detection only and
  never a commit gate. `kb-audit` runs it in Step 1 and queues each hit as `transient content` at
  severity 7. `kb-prepare audit` passes its output to the packet (#136).

- `kb-distill` writes current state, not a changelog (#134, #135):
  - A reading, such as a count or a list of what is offline, stays in the note. The library keeps
    the method that produces it.
  - Behavior seen only on a branch or in an open pull request stays in the note until it merges.
  - A new supersede outcome rewrites a section that is no longer true to what is true now and
    removes a dropped row. A first-hand change is a supersede, not a contradiction.
  - Sections are named after their subject, never an event, date or change. Nothing is added to
    an existing `## Update <date>` section.
  - Step 7 runs `check-transient` on the library.

## v0.3.0 — 2026-10-31

Changes since v0.2.0. A minor release: it changes the contract and the checks (ADR-0015). This engine
serves libraries that declare `kb_contract` 2.0 to 2.3 (ADR-0016); a library that declares none is
read as 2.0.

- `kb-library add` warns when the new library's root `keywords:` and `tags:` overlap a registered
  library's: at least 3 shared terms that are at least a quarter of the smaller library's terms. The
  warning names the neighbour and the shared terms and suggests `Not covered here` lines and a rerun
  of the routing sample. It never refuses and writes nothing (#124).
- `tests/run-checks` clears git's repository environment (`git rev-parse --local-env-vars`) before
  building fixtures. Run from the pre-commit hook of a linked worktree, it had inherited `GIT_DIR`
  and `GIT_INDEX_FILE`, so fixture commands set the committing repository's `core.bare` and
  `core.hooksPath` and staged the deletion of every file. A case now fails if any such variable
  survives into the suite (#127).
- `grade-routing`: contamination is what the retrieval contract forbids, a `*-golden.md` file or a
  path under `documents/eval-*/`, so a routed `sources/eval-*.md` citation stub no longer fails a
  case (#122). A content-mode Grep whose `path` is a single file is attributed to that file, since
  ripgrep omits the file name there (#121); it is content from that library, not a Read of the file.
  Content-mode lines are split at the first `.ext` followed by a line number, so a `-<digits>-` directory
  segment in the path (a session UUID in a checkout path) no longer truncates it.
- Contract 2.3 (#123, engine half): a library's root `INDEX.md` may carry a `Not covered here:` line
  naming the neighbouring topics it does not hold and, where known, the library that does, so routing
  can tell apart libraries whose topics overlap. Optional; `check-kb` fails an empty one from 2.3 and
  warns below it. `kb-retrieve` reads each candidate library's line and does not descend into one that
  excludes the question (no multi-library fan-out, which is #125). `kb-create-domain` asks for the
  line. `kb-init` writes 2.3. Library PRs follow.
- The library CI template (`documents/library-guardrails.yml`) clones the engine at `v0.2.0` instead
  of `main`, so a library's CI no longer changes with the engine's `main` (ADR-0015). ADR-0016 later
  made pinning the library owner's choice; the template keeps its pin.
- ADR-0015 amended: a release has a two-day code freeze. From two days before the release date,
  `main` takes release work only (the release section here, version numbers, the fresh-clone check
  and the tag). A defect found in that window is the owner's call: move the date, or ship and fix it
  in the next release.
- `sources/` holds only `.md` citation stubs, and raw artifacts are archived under `documents/`: now
  stated in CONVENTIONS §6, with the missing case for a local file or export, and in CONTRIBUTING.
  `check-kb` fails a non-`.md` file under `sources/` (#71).
- `analysis-tools`: the review skill owns its product-level calibration (which standards apply at
  Light, Medium and Full) and its five-point rating scale, which had lived in the intelligence-analysis
  library but are review procedure with no primary source. Bias remedies are retrieved from the rebuilt
  library, which states only the remedies its sources give.
- ADR-0016: the library contract gets its own version (`MAJOR.MINOR`, now 2.3), and a library
  declares the version it was built to (`kb_contract:`, read as 2.0 when absent). Rules apply by that
  version, and an engine supports the last two contract majors, so upgrading the engine does not make
  an older library unusable. Pinning becomes the library owner's choice; ADR-0015's pinning section is
  superseded. The next two entries and the contract entries below are the implementation.
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
  libraries behind or ahead.
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
- Contract 2.2 and `kb-verify --unattended` (#100). `Recheck (attended):` marks an assertion that
  needs a login, a credential or a live system. `kb-verify --yes --unattended` skips those with a
  count, and runs every other assertion with an empty `HOME` and only `PATH`, `KB_ENGINE_ROOT` and
  proxy settings, so no cached login or exported credential is reachable. It refuses `--apply`.
  A library on 2.1 is told it is behind, and moves by changing only its
  declaration unless it holds an assertion that needs a person.
- `check-secrets --redact` (#101): a filter from stdin to stdout. Every line any of the three passes
  flags becomes `[redacted: secret]` or `[redacted: personal identifier]`, with a count on stderr and
  the matched text nowhere. `lint-allow` exempts nothing in filtered text. It exits 2 with no output
  when the input cannot be scanned (UTF-16, binary, or a pass that failed), so a caller holds the
  input rather than passing it through unscanned. The gate modes are unchanged.
- Review packets: `kb-prepare` and `kb-apply` (#99, ADR-0017). `kb-prepare distill|audit <library>`
  drafts the half of a skill before its review gate, unattended. It runs only when notes await
  distillation or a sweep is due. It runs `claude -p` with Read, Grep and Glob only: no MCP servers,
  no session persistence, a dollar cap. The header (library, the commit drafted against, date) is
  written by the script, not the model. The body is redacted, and the packet is saved outside the
  library. `kb-apply list|show|done` lists packets, marks one STALE when its library has moved, and
  closes one. In a session, `kb-distill` and `kb-audit` resume from a packet at their own gate. The
  person decides each item, and only then does the skill write and commit. `kb-due --nudge` names the
  packets waiting. Tested with a stub `claude` that records its arguments. Run once for real on a
  scratch clone: $0.55, an injected instruction in the note not acted on, and the library unchanged.
- `kb-report` (#102): the weekly report of decisions. One file per ISO week, written outside every
  library (`${XDG_STATE_HOME:-~/.local/state}/ai-kb/reports/`). It lists, per library, only what needs
  a person: packets waiting, open queue items (category and location), attended rechecks due, a sweep
  or notes that no packet covers, and a contract behind or unsupported. A quiet week is one line. It
  holds paths, counts, headings and ids, never a fact's, source's or packet's text. `kb-due --nudge`
  names the latest report while it is under eight days old and lists decisions.
- `kb-schedule install | status | remove | run` (#103): the opt-in weekly job. `install` writes a
  systemd user timer (Mondays 07:00, `Persistent=true` so a missed week runs at the next start), or a
  crontab line where there is no systemd. `remove` leaves no trace. `run`, for every registered
  library:
  - runs `kb-verify --yes --unattended` and `kb-sources --yes`;
  - with `--prepare`, also runs `kb-prepare distill` and `kb-prepare audit` under a dollar cap;
  - then `check-xlinks --installed`, `kb-watch` on the chosen allowlist, and `kb-report`.
  It holds a lock, so runs never overlap, and logs only each step's exit code. It never edits a fact.
  On a systemd machine where the user is not set to linger, `install` says the timer then runs only
  while they are logged in, and names the command that changes it.
- Golden-set values are read as YAML scalars (#111). A single-quoted excerpt, the natural way to
  write one holding `"` or `: `, was searched for with its quotes still on and could never match.
  Now `'…'` loses its quotes and reads `''` as `'`, `"…"` reads its escapes, and a plain value keeps
  a closing quote of its own. `grade-eval` imports `check-golden`'s reader instead of keeping a copy.
  An engine fix, not a contract change: every existing golden set reads the same.
- `kb-backup DEST [--keep N] [--restore-test]` and `kb-backup verify RUN` (#96): a dated run of git
  bundles of the engine and every registered library, each with its recorded refs, plus SHA256SUMS.
  A bundle is verified by restoring it into a scratch repository and comparing its refs, not by
  `git bundle verify`, which passes a truncated bundle. `--restore-test` also clones and runs
  `git fsck --full`. A library with no commits is skipped with a note. A destination inside a backed-up
  repository is refused. `--keep` prunes only directories this command wrote.
- Retrieval cost (#97). `kb-telemetry` reads the `kb-retrieve` runs Claude Code already records
  (`~/.claude/projects/*/*/subagents/agent-*.jsonl` and `.meta.json`). Per library and window it
  reports medians of five measures:
  - new tokens, counted once per message id, since one message is logged in several records;
  - seconds from the first API response to the first read of a cited file;
  - steps to that read;
  - uncited content reads (wasted);
  - INDEX, contradictions, open-questions and queue reads (protocol).
  Eval runs are left out by description. `kb-eval-sample prepare | grade` draws a seeded (or
  `--cases`) sample of positive and cross-root cases. `prepare` writes prompts for fresh agents
  described `kb-eval <sample> Q<n>`. `grade` finds those transcripts, writes the mapping, runs
  `grade-routing` and `grade-eval --transcripts`, and joins each case with its cost. Both are
  read-only and print paths and counts only.
- `kb-sources` retries a 403 to its own User-Agent once with Python's default User-Agent, and that
  answer decides (#117). dni.gov served ICD-203 and ICD-206 to every client but refused one that
  named itself `kb-sources`, so two live sources were queued as unreachable on the first scheduled
  run. Nothing impersonates a browser, and a server that refuses every client (science.org behind
  a DOI) is still unreachable.

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
