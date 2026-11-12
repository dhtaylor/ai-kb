# ADR-0020: A library says where the libraries it links to come from, and a consumer's copy is read-only

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** Dandy Taylor
- **Amends:** [0014](0014-library-registry.md) (a registered name can now be checked against the
  origin a link expects); answers part of [0015](0015-releases-and-pinning.md)'s review trigger
- **Issue:** [#148](https://github.com/dhtaylor/ai-kb/issues/148)

## Context and problem statement

ADR-0015 said to revisit its decisions "when a library is maintained by someone who is not the
engine's maintainer". That has happened. A library someone else publishes is installed with
`kb-library add` on a machine that already holds a library of its own under a name the published one
links into. Three things then go wrong.

1. **A link names a library, and a name means something only on one machine.** `[[azure-devops:slug]]`
   was written against the publisher's azure-devops. ADR-0014 makes the registered name the only key,
   and lets a name be registered once, so on this machine it resolves to the consumer's own
   azure-devops. A slug missing there is a dead link, and `check-xlinks` fails the commit. The
   consumer cannot fix the published library, and a "fix" in their own library would hide the
   problem. Nothing tells "the library is absent" (a warning today) from "a different library holds
   this name" (a failure today, reported as an ordinary dead link).
2. **A library states no dependencies.** Its release does not say which other libraries it links
   into, or from where, so `kb-library add` cannot warn before anything breaks. It already warns
   about keyword overlap (#124).
3. **Every registered library is treated as the machine's own.** The nudge, `kb-audit`,
   `kb-distill`, `kb-capture`, the weekly job and the commit hook all assume the machine curates every
   library it has. A consumer of a published library wants it read-only. What they learn about it
   belongs upstream as an issue, not in local commits that drift from the release they installed.

## Considered options

**For identity:**

1. **Globally unique names** (`owner/name`). Every `[[library:slug]]` link in every library would
   change: a major contract version for a problem only some machines have. Rejected.
2. **An alias on registration** (`kb-library add --as theirs-azure-devops`), rewriting names when a
   link is resolved. The consumer could then hold both libraries. But ADR-0014's rule that the
   registered name is the name a library declares would end, and every reader of the registry would
   need to learn the mapping. Deferred: see "Not covered".
3. **A declared origin for each library a library links into**, compared with the origin the registry
   already records. Links are unchanged. A mismatch can be named for what it is. **Chosen.**

**For dependencies:** a block that also lists every slug relied on was rejected. The links already
say which slugs a library relies on, and a second list would drift from them. Only the
library-to-origin map is new.

**For the consumer role:** a read-only flag on the registration was chosen over making files
read-only on disk. A file mode doesn't survive a `/mnt/c` mount (#50), and it would stop `git pull`
too.

## Decision outcome

### A library declares where each library it links to comes from (contract 2.6)

The root `INDEX.md` gains an optional field, required from contract 2.6 by any library that links
across libraries:

```yaml
links_to:
  azure-devops: https://github.com/dhtaylor/azure-devops.git
  claude-code-runtime: https://github.com/dhtaylor/claude-code-runtime.git
```

- **Every library a `[[library:slug]]` link names is a key,** and its value is the origin the author
  linked against: the git remote they cloned it from. `check-kb` fails, from 2.6, a link whose
  library isn't listed, and warns about a key no link uses. Below 2.6 both are warnings (§14).
- **The slugs are not listed.** They are read from the links.
- **Origins are compared by host and path.** Scheme, user, case of the host and a trailing `.git`
  don't matter, so `https://example.com/x/y.git` and `git@example.com:x/y` are the same origin. Today
  `kb-library import`'s `same_origin` ignores only a trailing `.git` and slashes. It is extended to
  this, so that import and these checks share one comparison.

### A mismatch is named, and warns rather than fails

When library A links into B, `check-xlinks` reads A's `links_to` entry for B and B's registered
origin:

| B on this machine | Reported as | Fails? |
|---|---|---|
| registered, same origin | resolved as today: a missing slug is a dead link | yes, as today |
| registered, **different origin** | **dependency mismatch:** A expects B from `<origin>`, this machine's B is from `<other>`. The A→B links aren't resolved, and the slugs they name are listed | no, warns |
| registered with no origin recorded | resolved as today, plus one note that the origin can't be confirmed | as today |
| not registered | absent, as today, naming the origin to `kb-library add` | no, warns |
| A declares no `links_to` (below 2.6) | as today | as today |

A mismatch warns because the person who sees it can't fix it. They can't edit a published library,
and editing their own would make the warning go away without changing what is wrong.

**`kb-library add` checks both directions:**
- **For the library being added,** it checks each `links_to` entry: a mismatch or an unregistered
  dependency is a warning, with the number of links affected.
- **For each library already registered** whose `links_to` names the newcomer, it compares origins.

Like the overlap warning, this is advice: it never refuses and never changes the exit status.

### A consumer's copy is registered read-only

`kb-library add <path | git-url> --read-only` records `readOnly = true` for the library in the
registry. Re-adding the same path with or without the flag changes it. A read-only library is
**served exactly as any other**, by `kb-ask` and `kb-retrieve`. What changes is that this machine
doesn't curate it:

- **The commit hook refuses a commit in the clone.** The hook is the engine's (ADR-0014), so this
  needs no change to the library. It names the origin to file the correction with, and the command
  that makes the library curated here. `--no-verify` still gets past it: governance, not enforcement
  (ADR-0002).
- **Nothing that writes into a library runs on it:**
  - `kb-verify`, `kb-sources` and `kb-watch` refuse it, whether run by hand or by the weekly job, and
    the job skips it. They write stamps and queue items into the library. The publisher verifies
    their library; a consumer verifying it would change a copy no one else reads.
  - `kb-prepare` drafts no packet for it.
- **Nothing asks this machine to curate it.** The nudge, `kb-due` and `kb-report` leave it out. Plain
  `kb-due` lists it as `read-only`.
- **The curation skills refuse to write to it:** `kb-update-domain`, `kb-distill`,
  `kb-organize-domain`, `kb-audit` and `kb-capture` into it. They say to file the finding with its
  origin. Session start marks each read-only library `(read-only)` in the list it gives the model,
  which is how a skill knows. A skill never files the issue itself: posting to another person's
  tracker is a person's decision.
- **Its outbound links never fail this machine's commits.** A dead link in a read-only library is a
  warning that names the library's origin. Its publisher's CI is where it fails.

### Pinning a consumer's copy

`kb-library add <git-url> --read-only --ref <tag>` clones at a tag. The registry records the `ref`,
and `kb-library list` shows it, so a consumer can see which release they are on. Moving to a newer
release is a person's step. This ADR sets the shape; it is delivered in the steps below.

## Consequences

**Good.**

- A link into a same-named library from somewhere else is reported for what it is, with the slugs
  affected, and no longer blocks the consumer's own commits.
- A release states what it links to, so a consumer is warned when they install it, not when they next
  commit.
- A consumer can install someone else's library without the machine nagging them to curate it, and
  without local edits drifting from the release.

**Bad.**

- Contract 2.6 means a pull request in every library that links across libraries, to declare
  `links_to`, and one in every library to declare 2.6.
- `links_to` is a second place an origin is written. If a dependency moves its repository, every
  library linking to it needs a pull request. That cost lands rarely and on the right person, the one
  who chose the dependency.
- A read-only library's facts go unverified on this machine. That is deliberate: the stamps a
  consumer reads are the publisher's.

**Not covered.**

- **Holding both same-named libraries on one machine.** A consumer whose own azure-devops collides
  with a dependency's still can't install the dependency. This ADR makes the collision visible; it
  does not resolve it. Aliasing (option 2) is the way, if a real case needs it.
- **Filing upstream issues automatically.** A skill names where to file; a person files.
- **A dependency's version.** `links_to` names a repository, not a release. A slug the publisher's
  dependency gained after the consumer's copy is still a dead link, reported with the origin.

### Delivery

1. **The read-only role** (v0.4.0): the registry flag, `kb-library add --read-only`, the hook
   refusal, the writers' refusals and the weekly job's skips, the nudge, `kb-due` and `kb-report`,
   the session-start marker, and the skills' refusals.
2. **`links_to` and dependency mismatches** (v0.4.0): contract 2.6, `check-kb`, `check-xlinks`,
   the wider `same_origin`, `kb-library add`'s warnings, outbound links from a read-only library as warnings, and the library
   pull requests declaring 2.6.
3. **`--ref` pinning** (after v0.4.0): the registry `ref`, `kb-library add --read-only --ref <tag>`
   for a URL and a path, and `kb-library list` showing the ref and a checkout that has moved off it.

Tests first for each, with a fixture registry under a throwaway `HOME`, never the real one.
