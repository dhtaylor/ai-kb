# Changelog

What changed in each release of the engine. What a version number means, and how libraries pin the
engine, is [ADR-0015](documents/decisions/0015-releases-and-pinning.md). A domain library records the
engine release it was last verified against in its own release notes.

## Unreleased

## v0.6.1 — 2026-11-25

Changes since v0.6.0. A patch release: no script, skill, agent or contract changes. This engine
still serves libraries that declare `kb_contract` 2.0 to 2.7 (ADR-0016).

**Before you upgrade:** nothing in the engine needs action. A library that pins engine v0.6.0 in CI
can move its pin to v0.6.1 or leave it. Use ai-kb-architecture v0.6.1 with this release, not v0.6.0:
the library's v0.6.0 tag still pins engine v0.5.0 in its CI and declares contract 2.6, because it
was tagged before its move to v0.6.0 merged.

- ADR-0019's release day gains a step, now step 4: after the engine is tagged, the reference
  library's release pull request pins its CI to the new tag and merges once that CI passes, and the
  library is tagged at that commit. The library's CI clones the engine by tag, so the commit tagged
  at v0.6.0 could not yet pin it. Preflight also checks that the library's release pull request
  differs from the checked commit only by its pin and what moves with it.

## v0.6.0 — 2026-11-25

Changes since v0.5.0. A minor release: stamps' leases follow evidence (ADR-0022), and contract 2.7 is
added. This engine still serves libraries that declare `kb_contract` 2.0 to 2.7 (ADR-0016).

**Before you upgrade:**
- **Coming from v0.4.0 or earlier?** Read v0.5.0's upgrade note below too: it moves the folders the
  engine reads if `XDG_STATE_HOME` or `XDG_CONFIG_HOME` was set (ADR-0021).
- **What you will see.** Asserted stamps get the full horizon, so due rechecks drop sharply (#238).
  The session-start nudge and the weekly report lead with assertion coverage (#239). A failed check
  demotes its stamp to the short lease until a passing restamp (#264). That includes a check that
  failed only because a site was unreachable: a `curl | grep` assertion cannot tell a fetch failure
  from a changed page, so one bad hour costs those facts their coverage until the next attended run.
- **Each library: move its CI engine pin to v0.6.0 and delete its "Stamp honesty" step, in the same
  change.** `check-stamps` is retired (#240), so a library pinned to v0.6.0 that keeps the step fails
  CI there. A library that copied `documents/library-guardrails.yml` has the step; the template
  no longer does.
- **Contract 2.7 is optional.** A library on 2.6 or earlier is still served and is not something to
  decide (#263). A library that raises `kb_contract` to "2.7" must rename `agent_ttl:` to
  `unasserted_ttl:`, or `check-kb` fails it (#236).
- **Nothing else needs action.** The `kb-due` and `kb-session-start` changes (#253) move the nudge
  schedule into `kb-due --session`, with no change to settings or output; `kb.nudge` works as before.

- A library behind on a supported contract is no longer something that needs attention (#263). The engine
  serves every minor of a supported major (ADR-0016), so a library built to 2.6 on an engine that knows 2.7
  has nothing to decide, yet it counted as a decision in `kb-report` and added a clause to its line in the
  `kb-due` nudge and `kb-due --summary`: on six registered libraries the weekly report went from 5 decisions
  to 11. `Attention.items` yields no contract item for the `behind` state, and the wording for it is removed
  from `kb-due` and `kb-report`. `ahead`, `unsupported` and `malformed` are unchanged, because each changes
  what the engine serves or checks, and `check-kb` still tells a library behind what the newer versions add.
  No contract version changes: what a library must hold is as before (CONVENTIONS §14).
- Documentation fixes where the docs disagreed with the code, with no behaviour or contract change.
  CONVENTIONS §10 now says `expected_evidence: word` is a stamp with no `Recheck:`, and that an unstamped
  section is its own tier `check-golden` rejects `word` on; §13 counts its checks as twenty-seven, not
  twenty-eight; the `kb-due` docstring no longer says "the six" categories and its "silence" sentence says
  one thing; README no longer states an ADR range that goes stale; ADR-0017 carries a dated note that
  since ADR-0022 a stamp's author sets no lease, while attended decisions stay unautomated.
- A failed recheck makes a stamp unasserted until it is settled (#264, ADR-0022 decision 1). A section
  with an open `stale-recheck` record in its library's `needs-attention.md` takes the short lease and
  leaves assertion coverage. `kbengine.lease` reads that queue itself, in the sweep (Attention still
  reads it separately for its own counts). `kb-verify` (the lease label reads `short lease:
  failed-recheck`), the nudge, `--summary` and the weekly report all take the demotion from the sweep's
  result, and none re-derives it. The demotion lasts only while the record was raised against the
  section's current stamp: its `stamp:` must equal the stamp's content after `Verified:`. A passing
  attended `kb-verify --apply` restamps the section, which is then asserted again at once while the
  record stays open for the Arbiter. Nothing in the engine closes a record. A record with no `stamp:`
  covers a stamp dated on or before its date. A `stale-recheck-error` (a timeout, or a command that
  could not run) demotes nothing, nor does an unreadable queue or an unreadable record date.
  `kb-retrieve` says a cited section's check last failed by the same rule, flags the fact as someone's
  word before the answer, and still refuses on dispute only. CONVENTIONS §7 defines "passing". No
  contract version changes: a library holds what it always did. Output is unchanged for a library with
  no open `stale-recheck` record. On one that has one, only that section's lease and the coverage count
  change.
- What needs a person's attention is decided in one place (#253, part of #254). `Attention.items` is a
  frozen, ordered list per library: coverage first, then review packets, a sweep due (unless a kb-audit
  packet covers it), rechecks, stale facts, the queue and the records the reader could not read, notes to
  distil (unless a kb-distill packet covers them), unstamped sources, unsourced sections, the contract
  state and an archived library that is still registered. Each item says whether it is a decision, and a
  field that failed is an item. `kb-due` and `kb-report` word the items and no longer test conditions to
  find them, and `kb-due --summary` is counted from them. `kbengine.reports` owns where reports live, the
  latest and whether it is current, so `kb-due` no longer loads the `kb-report` script. The `kb.nudge`
  schedule moves out of `kb-session-start` into `kb-due --session`, and `--summary-out FILE` hands the
  summary to the hook in a file, so the hook no longer matches `KB due — ` or works out the reports
  folder; `kb-report` filters on `shelved` as `kb-due` does, before anything else about the library is read.
  `manual_stubs` (the `Liveness: manual` source stubs, listed while a sweep is due) is a kind only the weekly
  report says. GLOSSARY.md defines **Nudge** and **Decision**. If `kb-due` fails during the session hook,
  the hook now says so in one line, with its exit code, to the model and the person, where it showed no nudge
  (under `off` or a held-back `weekly:<day>`, only that setting's note). Otherwise the output is unchanged: `kb-due` (plain, `--quiet`, `--nudge`, `--summary`), the weekly
  report and `kb-session-start` print what they printed, on the real registry and on fixtures for each
  contract state, a contract that cannot be read, packet suppression, a read-only and an archived library,
  a library below full coverage, a stray non-report `.md` in the reports folder, and each `kb.nudge`
  setting. The other behavior that differs is a malformed `KB_TODAY` in the hook: `kb-due` refuses it, so
  the hook now shows that line, where it showed no nudge with `always` and read the word as a date with
  `weekly:<day>`.
- A library is parsed once per sweep (#251, part of #254). `factfiles.tree(root)` returns the library's
  files, each read and parsed the first time it is asked for and never again, and `factfiles.tree_from(blobs)`
  builds the same value from git blobs, so the sweep baseline uses the same parser. `lease.sweep` now takes
  that parsed library instead of `root` (it returns what it returned), and Attention (`kb-due`, `kb-report`)
  reads each fact file once for the lease, the unstamped sources (now and at the last sweep) and the
  unsourced count, where it read it three times. `check-kb`'s `kb_files`, `unsourced`, `unstamped_keys`,
  `marked_sections` and `reachable` move into `factfiles`; no engine module and no golden-set script loads
  `check-kb` any more, which closes the pointer #252 left in `check-golden`. `check-xlinks`, `check-scope`,
  `check-blast` and `kb-library` use `factfiles.EXCLUDED_DIRS`, so one rule names the folders that are not
  the knowledge base. The output is unchanged for valid UTF-8: `check-kb`, `check-golden`, `check-xlinks`,
  `check-scope`, `check-blast`, `kb-verify`, `kb-due`, `kb-report` and `kb-library` print byte-for-byte what
  they printed, on all six libraries and on a library whose last sweep differs from its working tree. One
  difference: a router that is not valid UTF-8 is read with replacement characters, so it no longer crashes
  `check-kb` or `check-golden`.
- `check-kb` no longer reports a `[[slug]]` inside a code fence as a dead link, nor a fenced `[[...]]`
  naming a path-addressed file (#257, part of #254). A fence is an example. One fence definition,
  `factfiles.FENCE`, now serves `check-kb`, `check-xlinks` and the stamp checks, and the dead-link check
  reads links through `check-xlinks`' reader. This loosens a check and rejects nothing new, so no
  contract version changes (CONVENTIONS §14); both checks print the same output on all six libraries.
- The lease rule gets one module, `kbengine.lease` (#250, ADR-0022). `sweep(root, horizon=, unasserted_ttl=)`
  reads each fact file once, lints the library once and returns immutable stamps: asserted or not, their
  lease, due, stale, and the library's assertion coverage. `kb-verify` and Attention (`kb-due`, `kb-report`)
  both take their due list, stale list, lease labels, warnings and coverage from it, and `kb-verify`'s own
  `asserted`, `is_due`, `due_sections` and `sections` are gone. `check-kb`'s "not CONFLICTED" section rule is
  named `served` in `factfiles`, beside `in_scope`. Behaviour and output are unchanged: `kb-verify`, `kb-due`
  and `kb-report` print byte-for-byte what they printed, except that a fact file that cannot be read now
  reports its real exception type where it reported `RuntimeError`.
- The golden set and citation resolution move out of the command-line scripts into three engine
  modules, `kbengine.golden`, `kbengine.citations` and `kbengine.transcripts` (#252, part of #254),
  ending the load cycle in which `check-golden` and `grade-eval` each loaded the other.
  `grade-routing`, `kb-telemetry` and `kb-eval-sample` no longer load `grade-eval`. Behaviour and
  output are unchanged: the five scripts print the same reports and exit with the same codes.
  `check-golden` still loads `check-kb` for reachability, pending #251. `GLOSSARY.md` now defines
  **Golden set** and **Citation**.
- The assertion lint moves out of `scripts/kb-verify` into the engine module `kbengine.lint` (#249), the
  groundwork for the lease module. Behaviour is unchanged: `kb-verify` imports the lint and prints the
  same report. `GLOSSARY.md` now defines **Sourced section**.
- A stamp's lease now follows its evidence, not who wrote it (ADR-0022, #233): an asserted stamp
  stays fresh for the full horizon, every other stamp for the short lease, whoever wrote it.
  **Due counts drop sharply on upgrade**: asserted stamps that sat on the short lease only because
  they were `by: agent` are no longer due. **Before moving its engine pin past the release that
  removes `check-stamps`, each library must delete the "Stamp honesty" step from its CI workflow**,
  or its CI fails. The entries below give each change.
- The session-start nudge and the weekly report lead with assertion coverage (#239, ADR-0022):
  per library, the sections with an asserted stamp over the sections that cite a source, as
  "assertion coverage 2 of 5 sourced sections". A lint-flagged assertion counts as unasserted. A
  library with no assertions reads "0 of N" and is never a failure or a reason to withhold it.
  Coverage is a measure, not something due, but a library below full coverage is named in the
  nudge even when nothing is due; one with every sourced section asserted stays silent. The report
  lists coverage for every library, including those with nothing to decide.
- Retrieval states what backs each cited fact, not who stamped it (#237, ADR-0022). `kb-retrieve`
  says "carries a check, last passed <date>" for a section with a `Recheck:` and "someone's word,
  <date>" for one without, and flags the latter before the answer. It never says "asserted", because
  it cannot run the lint. Nothing is refused for lacking a check; a disputed fact is still refused.
  The `by:` stamp is no longer reported, and the answer's `Verified:` line becomes `Evidence:`. Golden
  records take an optional `expected_evidence: check|word`, graded by `grade-eval` and checked against
  the file by `check-golden`.
- Contract 2.7: `unasserted_ttl:` replaces `agent_ttl:` (#236, ADR-0022). A library declaring
  `kb_contract: "2.7"` names the short lease of an unasserted stamp `unasserted_ttl:`, still a tenth of
  the horizon by default and at least one day, and `check-kb` still fails one not shorter than the
  horizon. `check-kb` fails `agent_ttl:` from 2.7, and the message names the new field; below 2.7
  `agent_ttl:` is read as before and a declared `unasserted_ttl:` is a warning. The library model
  exposes one value, `unasserted_ttl`, whichever field supplied it, and `kb-verify`'s header now
  reads `short lease Nd` where it read `agent TTL Nd`. To adopt it, rename the field and declare
  2.7 (CONVENTIONS §14); `kb-init` now writes 2.7.
- `check-stamps` is retired (#240, ADR-0022). It refused an agent-co-authored commit that added a
  `by: human` stamp, to stop a false claim buying a tenfold lease. The lease now follows the
  stamp's evidence, so a false `by: human` buys nothing. The script, the engine's guardrails
  step, the library guardrails template's "Stamp honesty" step and their cases in `run-checks` are
  removed. A library that copied the template must delete its "Stamp honesty" step before it moves
  its engine pin to the first release without `scripts/check-stamps`, or its CI fails.
- A stamp's lease follows its evidence, not its `by:` (#238, ADR-0022). An asserted stamp (a
  `Recheck:` the assertion lint does not flag, attended or not) stays fresh for the full
  `freshness_horizon`. Every unasserted stamp, `by: human` included, falls due after the short
  lease (`unasserted_ttl:` from contract 2.7, `agent_ttl` before it; a tenth of the horizon by default), as does a lint-flagged assertion.
  `kb-verify` names the lease of each due command and each stale fact, and the finding behind a
  short one. On upgrade, expect far fewer facts due for recheck: asserted stamps that were on the
  short lease only because they were `by: agent` are no longer due. A `by: human` stamp with no
  `Recheck:` now goes stale after the short lease instead of the full horizon.
- `kb-verify`'s assertion lint reports which sections each finding covers (#235): `lint_findings`
  returns them by section, as `short-fragment`, `reused-fragment` or `outside`, for the
  evidence-based lease and assertion coverage to come (ADR-0022). The printed warnings are
  unchanged.
- The `kb-libraries` docstring for `declared_terms` states the plural rule the code applies (#230): a
  trailing `s` is dropped only from a term longer than 3 characters that does not end in `ss`, so
  `bus`, `gas` and `process` keep theirs. It said "a trailing plural `s` dropped". Behavior is
  unchanged.
- `kb-bootstrap --check` exits 1 when `kb-libraries` fails, instead of 0 (#229). With
  `scripts/kbengine/` missing, as in a partial copy of the engine, `kb-libraries` failed at import and
  `--check` printed the traceback and exited 0, which reads as no drift. It now reports
  `FAILED kb-libraries`, does not print `(none registered)`, and says that `--apply` cannot fix it:
  restore the engine, then run it again. The library list is read before its loop rather than through
  `< <(...)`, whose exit status bash discards.

## v0.5.0 — 2026-11-23

Changes since v0.4.0. A minor release: CONVENTIONS §2 and §5 change for local-only libraries (#212),
with no change to the contract version (ADR-0015). This engine still serves libraries that declare
`kb_contract` 2.0 to 2.6 (ADR-0016); a library that declares none is read as 2.0.

**Before you upgrade:**
- **If you had `XDG_STATE_HOME` or `XDG_CONFIG_HOME` set**, the engine no longer reads the old folders
  (ADR-0021, entry below). Move your packets, reports, log and backups from `$XDG_STATE_HOME/ai-kb/`
  to `~/.local/state/ai-kb/`, and run `kb-schedule install` again. After reinstalling, the old
  `ai-kb/schedule.conf` and `systemd/user/ai-kb-schedule.{service,timer}` under `$XDG_CONFIG_HOME` may
  be deleted, after `systemctl --user daemon-reload` (#227). The reinstall writes the same units under
  `~/.config`, so the leftovers do no harm, but `kb-schedule status` does not mention them.
- **Keep `scripts/kbengine/` beside the scripts** (#226). Most engine scripts now import the
  `kbengine` package from the folder beside them. Run in place or through a symlink, they work; a
  script copied on its own fails at import (`ModuleNotFoundError: No module named 'kbengine'`). In
  v0.4.0, `kb-due` copied on its own still ran. A normal install is not affected.

- A library may be local-only: a git repository with no remote, never pushed (#212). CONVENTIONS
  §2 names it as a supported mode and what differs (no origin to export, the commit hook as its only
  gate, a remote added later recorded by registering again); §5 makes its absolute path its
  `links_to:` origin, which `check-xlinks` resolves as before and reports as a dependency mismatch
  once the library is registered with a remote. `library-guardrails.yml` and `state-change-gates.md`
  say that `--no-verify` is unguarded there, and to run the library hook by hand. No change to
  `scripts/` or to the contract version.
- `kb-due --nudge` counts every recheck that is due, not the `verifier_budget`'s worth (#211). It
  said "5 facts due for recheck" for a library with 35 due; it now says "35 facts due for recheck,
  5 a run (kb-verify … --yes)", and the summary line's "to recheck" counts all 35. Within the budget
  the wording is unchanged. `kb-verify` itself, and what it runs, are unchanged.
- The unit tests run on the suite's frozen clock too (#217): `tests/test_attention.py` dates its
  fixtures from `clock.today()` rather than the real date, so they pass whatever `KB_TODAY` says, and
  `run-checks` no longer unsets `KB_TODAY` for them. No change to `scripts/`.
- `tests/run-checks` runs on a frozen clock (#205): it exports `KB_TODAY=2026-10-10` and builds every
  fixture date from it, where it used the real date, so no case changes result as the calendar moves.
  Cases that check what the real clock does (the weekly nudge's weekday, `kb-report`'s ISO-week
  filename, a library stamped and swept today) run with it unset. No change to `scripts/`.
- `tests/run-checks` compares the paths `kb-session-start` and `kb-bootstrap` resolve in bash (the
  reports folder, the backup folder, the registry) with `kbengine.env`'s, with and without
  `KB_REPORTS` and with `XDG_*` pointing elsewhere (#205). A change to one that the other does not
  follow fails a case. Neither script reads `XDG_STATE_HOME` any longer (ADR-0021).
- `KB_TODAY` (YYYY-MM-DD) now sets the date for the engine's Python as well as session start (#205).
  `check-kb`, `kb-verify`, `kb-due`, `kb-report`, `kb-prepare`, `kb-watch` and `kb-sources` read it
  through `kbengine.clock.today()` at the moment they need it, where each had frozen the real date at
  start; `kb-init` and `kb-capture` use it for the date they write. Timestamps (a report's `generated`
  and ISO week, logs, backups) stay on the real clock. A malformed value exits 2 and names the
  variable; it never falls back to the real date. It is documented in CONTRIBUTING as an injection
  point. Nothing changes when it is unset.
- `kb-telemetry` and `kb-eval-sample` honour `CLAUDE_CONFIG_DIR` (#205). They read transcripts from
  `~/.claude/projects` only, though Claude Code writes them under that variable's folder when it is
  set, and `kb-bootstrap` already followed it. `kb-report`'s count of fact-not-found runs reads the
  same folder. `--projects` still wins. `kb-schedule install` now saves `CLAUDE_CONFIG_DIR` in
  `schedule.conf`, and `run` restores it, as it does PATH; reinstall to record it.
- **The engine no longer reads `XDG_STATE_HOME` or `XDG_CONFIG_HOME` (#205, ADR-0021).** Its files are
  at fixed paths: packets, reports, `schedule.log`, `schedule.lock` and backups under
  `~/.local/state/ai-kb/`, and `schedule.conf` and the systemd user unit folder under `~/.config/`.
  This fixes a silent failure: with `XDG_CONFIG_HOME` set only in a terminal, `kb-schedule install`
  wrote `schedule.conf` under it, and the cron or systemd run, which does not have it, read
  `~/.config`, so it ran with preparation off and without the saved PATH. `KB_PACKETS` and
  `KB_REPORTS` still override. **If you had either variable set, the engine no longer reads the old
  folders: move your packets, reports, log and backups from `$XDG_STATE_HOME/ai-kb/` to
  `~/.local/state/ai-kb/`, and run `kb-schedule install` again** (its conf and units were under
  `$XDG_CONFIG_HOME`). Nothing is deleted. Git's own lookup of `$XDG_CONFIG_HOME/git/config` in
  `kb-bootstrap` is unchanged.
- `kbengine.env` declares every variable the engine reads, with its default and effect, and resolves
  its locations in one place (#205). It replaces five copies of the state-folder rule and two of the
  `KB_CLAUDE` fallback. `python3 -m kbengine.env --names` lists the variables.
- `kb-report` lists the queue records it cannot read (#204). `kb-due` has counted them since #168,
  but the report skipped them in silence, so an unreadable record was missing from both the queue
  items and the decisions. It now says how many there are, and that `check-kb` names the lines.
- `kb-due --nudge` no longer names a sweep that a pending `kb-audit` packet already covers, or the
  episodic notes a pending `kb-distill` packet covers (#204). It named both the packet and the work
  inside it, so the same decision showed twice; `kb-report` already left the second out. A packet
  covers only what its skill does: an audit packet does not hide the notes, nor a distill packet the
  sweep. `--quiet` and the plain listing still show a due sweep.
- `kb-report` goes on when the library registry cannot be read (#204), as `kb-due` does. It stopped
  with exit 2 and "could not load the engine's readers". It now warns on stderr that the registry is
  unreadable, reports any library named on the command line, and finds none to report otherwise.
- `kb-report` no longer stops at the first library it cannot read (#204). A malformed `agent_ttl:`
  or an unreadable `needs-attention.md` ended the whole run with exit 2 and no report. It now writes
  "Could not compute …" as an item under that library and reports the others. Exit 2 stays for an
  engine that cannot load its readers, or a report folder inside a library.
- `kb-report` lists a library whose contract is newer than the engine's (#204). It named a library
  behind the contract, or on one the engine cannot serve, but said nothing about one ahead, which
  `kb-due` already told to upgrade the engine.
- `kb-report` leaves out a library that declares `archived:` and is not registered (#204), as
  `kb-due` already did (#141). It listed that library's sweep and anything else due, though a
  read-only archive cannot act on a decision. A registered library is still reported: it is served
  whatever it declares.
- Two edge cases in a library's root `INDEX.md` frontmatter read differently (#203). On a repeated
  key the first occurrence now wins; `check-kb` and `kb-catalog` kept the last. `kb-libraries` now
  treats a `domain:` value outside `[\w-]+` (such as `foo#bar`) as a name mismatch.
- `kb-due --nudge` no longer crashes on a library whose `kb_contract:` is malformed (#203). It
  stopped with a traceback; it now says the contract cannot be read and goes on to the next tree.
- `kb-due`'s recheck count no longer needs `check-kb` beside it (#203). It read the horizon and agent
  TTL through `check-kb`, so a `kb-due` copied without it printed "could not compute facts due for
  recheck"; it now reads them through `kbengine`, as `kb-report` does, and prints the count.
- A trailing ` # comment` after a value in a library's root `INDEX.md` is no part of the value, and
  a quoted value is read without its quotes (#203). `check-kb` failed `name: "widgets"  # note`
  against the filename `widgets`; `kb-prepare` named a library `"fx"`, quotes and all; `kb-catalog`
  listed a scope as `general  # note`; `kb-verify` ignored a quoted `freshness_horizon`, and
  `kb-due` read a quoted `last_swept` as never swept; a new queue file copied a scope's comment into
  its frontmatter. One rule now reads every value: drop a ` #` comment outside quotes, then one
  pair of matching quotes. It only relaxes what a library may write, so it needs no contract version.
- `kb-due`, `kb-verify`, `kb-prepare` and the queue module read a library's root `INDEX.md` fields
  from its frontmatter only (#203). They searched the whole file, so a `last_swept:`, `archived:`,
  `freshness_horizon:`, `verifier_budget:`, `agent_ttl:` or `domain:` line in the body, which is
  prose, could be read as a declaration when the frontmatter had none. One reader of that file now
  serves every script (`kbengine/library.py`), as `kbengine/contract.py` does for the contract
  versions.
- `check-transient` no longer reads `.claude/` or `.claude-plugin/` (#201). It listed its own excluded
  folders, which lacked those two, so a dated or ticket-titled heading in a library's Claude Code
  settings or plugin folder was reported as a fact file's. It now prunes the same folders as
  `check-kb`, `kb-verify`, `kb-due` and `kb-sources`, and reads fact files by the rule they share, so
  a `CONVENTIONS.md` inside a library is not read either.
- `kb-due` no longer counts a stamp-less `Source:` line in an `INDEX.md` as an unstamped source
  (#201). It took every file that was not a record by name, so a router counted; it now counts fact
  files only, by the same rule `check-kb` applies, which a router is not (§6). A `CONVENTIONS.md`
  inside a library is not counted either.
- `kb-verify` reads a stamp that names no `by:` or `method:` (#201). It read only a stamp with both,
  so a bare `Verified: 2026-09-22` was invisible to it: never listed, never due, never rechecked. It
  now sees one, and a missing `by:` counts as an agent's, so the shorter agent TTL applies. It also
  reads Rechecks in fact files only: a `Recheck:` in an episodic note, a source stub, an `INDEX.md`
  or another record is no longer listed or run under `--yes`.
- `kb-verify` no longer treats a `Verified:` stamp and `Recheck:` inside a code fence as an
  assertion (#199). It read every column-0 stamp, so an example in a fence was listed as due and
  ran under `--yes`, including the weekly job's `--yes --unattended`. `check-kb` already read a
  fenced stamp as an example; `kb-verify` now does too. `kb-sources` no longer counts a fenced
  heading or `Source:` line when it lists a stub's dependants.
- `kb-capture` no longer refuses a note as empty because of a one-line `<!-- … -->` comment (#194),
  such as an inline `<!-- lint-allow: … -->`. The empty-note check removed comments by line range,
  so a comment opened and closed on one line ran on to the next `-->` or the end of the note. It now
  removes them by content. A note of only headings and comments, and the template saved unchanged,
  are still refused. The filed note was never truncated; only the check was wrong.
- `tests/run-checks` no longer depends on the caller's environment for the engine's own variables
  (#181). It clears `KB_LIBRARY_HOME`, `KB_ENGINE_ROOT`, `KB_SYSTEMCTL`, `KB_CRONTAB` and git's
  `GIT_CONFIG_GLOBAL`/`SYSTEM`/`NOSYSTEM` and author and committer variables at start, as it clears
  git's repository environment (#127), and a case fails if one survives. With `KB_LIBRARY_HOME`
  exported, five `kb-library` cases had failed.
- `kb-distill` Step 7 and its "Resuming from a review packet" now name `check-kb`'s argument as the
  library's path (a bare name finds no files), and run `check-golden` before the approval gate and
  again after any edit the reviewer makes there, so a golden case quoting removed text is caught
  before approval, not at the commit hook (#177). The same two fixes, where the defect was present,
  in `kb-update-domain`, `kb-create-domain`, `kb-organize-domain` and `kb-audit`.

- `check-kb` fails a `Recheck:` or `Recheck (attended):` command that `/bin/sh` cannot parse (#182),
  naming the file, the line and the shell's error. A command with a quoted string split across lines
  stopped at an unterminated quote and never ran. It checks with `sh -n -c`, the shell `kb-verify`
  runs it under, using `kb-verify`'s own `RECHECK` pattern. It fails at every contract version, like
  an indented stamp: no contract bump, because such an assertion was broken under all of them.
- CONVENTIONS §6 says a source may appear on more than one `Source:` line in a section when each line
  backs a different claim, each with its own `Verified:` stamp (#175). The stale and unstamped-fact
  locus `<heading>|<source>` gives those stamps one ID, so one queue record covers them and resolving
  it means re-checking each one. `kb-audit` Step 3 says the same. No check changed.
- Session start can show the librarian's nudge less often (#174). `kb.nudge` in
  `~/.config/ai-kb/libraries` (or `$KB_NUDGE` over it) is `always` (default, output unchanged),
  `weekly:<day>` or `off`. On the days it is not shown, the block and the `KB due —` line are replaced
  by one line to the model saying so, with the path of the latest `kb-report`. A value that is not
  one of these warns in the session-start message and acts as `always`. A library that is not served,
  an unreadable registry and an unmigrated machine are reported whatever the setting; `kb-due --nudge`
  by hand, `kb-schedule` and `kb-report` ignore it.
- `kb-library export` and `import` carry a library's read-only mode and pinned tag (#178). Export
  writes `readOnly` and `ref` for each library that has them; import clones such a library at its
  tag and registers it read-only and pinned. A tag the remote no longer has refuses that library
  alone and the rest are still imported, with exit 1 as for any library not imported. An export
  without the keys imports as before.
- `check-secrets` no longer flags a plain slug in a frontmatter flow list (#183). The `]` closing
  `keywords: [a2a-setup-external]` was counted as a symbol, so a lowercase hyphenated slug with a digit
  looked like a mixed-class token. A trailing `]` on a lowercase slug is now ignored; a credential in
  `keywords:` or `tags:` is still caught. `--file` now resolves its path against the enclosing library,
  so a non-`.md` file under `documents/` gets the same raw-artifact exemption as `--worktree`; a file
  outside any library is still checked strictly. `--file PATH --strict` switches the exemption off,
  and `kb-capture` uses it, so `--from` a library's `documents/` file cannot borrow the exemption for
  a note filed elsewhere.
- `kb-verify`'s `WEAK` check no longer judges an assertion that only contains a URL (#185). It judges
  one that fetches it: `curl`, `wget`, `http`, `xh`, or a python `urllib`, `requests` or `httpx` call.
  A fixture origin written into a temp library, with the grep run on a local script's output, is
  left alone. A fetch is still judged against the URL it fetches, not a fixture URL beside it.

## v0.4.0 — 2026-11-12

Changes since v0.3.0. A minor release: it adds contract 2.6 and the checks that go with it (ADR-0015).
This engine serves libraries that declare `kb_contract` 2.0 to 2.6 (ADR-0016); a library that declares
none is read as 2.0. ADR-0020 ships whole: the read-only role, `links_to` (contract 2.6) and `--ref`
pinning.

- A consumer's read-only copy can be pinned to a release (ADR-0020 step 3, #148):
  `kb-library add <git-url> --read-only --ref <tag>` clones at the tag and records it as `ref` in
  the registry. It refuses, and clones nothing, if the remote has no such tag.
  - `kb-library list` shows `read-only @<tag>`, and says `(checkout moved: HEAD <sha>)` on the row
    if the clone is no longer at that tag. `kb-libraries` reads `ref` too.
  - To move to a newer release, check the tag out in the clone, then run
    `kb-library add <path> --read-only --ref <tag>`. It checks HEAD is at the tag and changes
    nothing if not. Re-adding without `--ref` clears the pin.
  - `--ref` goes with `--read-only`; without it, `add` is a usage error. `export` and `import` do
    not carry the ref.

- A section that cites one source on two `Source:` lines no longer queues the same finding twice
  (#172). Both stale (or unstamped) stamps hash to one ID, and a sweep wrote a record for each, so
  `needs-attention.md` held two identical records and the session nudge counted the item twice.
  Now a sweep writes one record per ID, covering every `Source:` line of that source in the section;
  kb-audit Step 3 says so. For a queue that already holds duplicates, `check-kb` warns, naming the id
  and each line, and `kb-due` and `kb-report` count and list the id once. A warning at every contract
  version, never a failure. IDs are unchanged: no ordinal was added to the locus.

- A queue record the readers can't parse is no longer silent (#168). `kb-due` and `kb-report` read
  one shape, `- id: <8 hex>` with two-space-indented `key: value` lines; a record in another, such as
  a bare mapping a sweep once wrote, was missing from the nudge and the weekly report, and `check-kb`
  passed the file. Now `check-kb` warns, naming each such record's line, the nudge and its one-line
  summary count them, and kb-audit Step 3 shows the exact shape to write. A warning at every contract
  version: the contract never defined the shape. The parser itself is unchanged.

- An unattended recheck finds a tool installed per user, such as `claude` in `~/.local/bin` (#165).
  Two things hid it: `kb-verify --unattended` ran every assertion with a fixed `/usr/bin:/bin`, and
  a systemd unit or crontab line starts with a bare system `PATH` anyway. Such an assertion failed
  with `command not found` and was queued as stale although the fact held. Now `kb-verify
  --unattended` keeps the caller's `PATH` (`HOME` stays empty, and nothing else is inherited, as
  CONVENTIONS §7 says), and `kb-schedule install` records the `PATH` it ran with in `schedule.conf`,
  which `kb-schedule run` uses for every step. Reinstall to change it.

- A home directory whose dotfiles are links into a shared repository, as GNU Stow makes them (#138).
  The engine's writes go through such a link, so this machine's paths land in the shared copy and
  reach every machine it syncs to. `kb-bootstrap` now names each target that is a link, or sits under
  a linked folder, every run; `kb-library` says so when it writes a linked registry, and
  `kb-schedule install` when its units or config are linked. Notes only: nothing is refused and no
  exit status changes. A `HOME` that is itself a link is not reported. `kb-libraries --linked` holds
  the rule.
- `kb-bootstrap` keeps its backups of `settings.json` and the shell rc in
  `${XDG_STATE_HOME:-~/.local/state}/ai-kb/backups/`, and says where. They used to sit beside the
  file, which put an untracked backup into a dotfiles repository whenever `~/.claude` was a link.

- The contract's header says version 2.6. It had said 2.3 since 2.4 was added; `tests/run-checks`
  now fails when the header and the newest version in §14 disagree.

- Contract 2.6: a link says where its library comes from (ADR-0020 step 2, #148). A tree that links
  across libraries lists each one under `links_to:` in its root `INDEX.md`, with the git remote it
  was linked against. `check-kb` fails a link whose library isn't listed, from 2.6, and warns below
  it. A link in a code span, which explains the form, needs no entry.
  - `check-xlinks --installed` compares that origin with the registry. A same-named library from
    another origin is a **dependency mismatch**: its links aren't resolved, and it warns with both
    origins and the slugs, where it used to fail as dead links the consumer couldn't fix. A library
    with no recorded origin resolves as before, with a note. An unregistered dependency's warning
    names the origin to add.
  - A dead link in a library registered read-only warns on this machine instead of failing.
  - `kb-library add` warns, never refuses, both ways: when the new library's dependency here is
    from elsewhere or absent, and when a registered library expects the new one from elsewhere.
  - Origins compare by host and path, so `https://` and `git@` forms of one repository are the
    same. `kb-library import` uses the same comparison; it used to tell those forms apart.
  - kb-init declares 2.6. kb-create-domain and kb-update-domain say to list a linked library.

- A consumer's copy of someone else's library can be registered read-only (ADR-0020 step 1, #148):
  `kb-library add <path | git-url> --read-only`. It is served as usual, and session start marks it
  `(read-only)`. Nothing on this machine curates it:
  - The engine's library hook refuses commits in it, naming the origin to file with.
  - `kb-verify --yes/--apply`, `kb-sources --yes`, `kb-prepare` and `kb-capture --into` refuse it,
    and `kb-watch` skips its sources. A dry run of `kb-verify` or `kb-sources`, which writes nothing,
    still works.
  - The weekly job, the nudge and `kb-report` leave it out. Plain `kb-due` lists it as `read-only`.
  - kb-update-domain, kb-distill, kb-organize-domain, kb-audit and /kb-capture refuse to write to it.

  `kb-library list` shows the mode, and `kb-libraries --read-only` lists each read-only library with
  its origin. Re-adding the same path without the flag makes it curated again.

- ADR-0020 (#148): a library says where each library it links to comes from, and a consumer's copy
  of someone else's library can be registered read-only. A link into a same-named library from a
  different origin is reported as a dependency mismatch and warns, rather than failing as a dead
  link the consumer can't fix. A read-only library is served as usual, but this machine doesn't
  curate it: the hook refuses commits, nothing writes into it, and nothing nudges about it.
  Delivered in three steps, all in this release: the read-only role, then `links_to` (contract 2.6),
  then `--ref` pinning.

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
