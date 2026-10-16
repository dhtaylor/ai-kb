# ADR-0014: Libraries are registered per machine, and can live anywhere

- **Status:** Proposed
- **Date:** 2026-10-15
- **Deciders:** Dandy Taylor
- **Amends:** [0007](0007-engine-content-separation.md) (supersedes its "no registry" point)
- **Issue:** [#25](https://github.com/dhtaylor/ai-kb/issues/25)

## Context and problem statement

A domain library can only live at `<engine>/kb/<name>/`. That location is hardcoded in about fifteen
places: session start, `kb-due`, `check-xlinks`, `kb-bootstrap`'s hook wiring, `grade-eval`,
`grade-routing`, `check-golden`, the engine's and `kb-init`'s hooks, the hook template every library
carries, and the kb-retrieve agent. So where the knowledge lives is tied to where the tool is
installed, although ADR-0007 made them separate repositories with separate lifecycles.

The case that raised it: on WSL2 the engine belongs on the Linux filesystem, because executable bits
do not survive on a Windows drive. A user who keeps all their work in one Windows folder, reachable
from both sides, then cannot keep their libraries there. A data disk, a team share and several
engine worktrees sharing one set of libraries have the same shape.

Two facts about today's design matter here:

- **A library that disappears fails silently.** If a library folder is moved or deleted, it is
  simply no longer enumerated. Retrieval then answers `fact not found` for everything it held, which
  looks exactly like a correct refusal. This is the failure the whole system exists to prevent.
- **ADR-0007 rejected a registry for a specific reason.** The registry would have had to live in
  the engine, which does not track `kb/`. It would then be "untracked state that drifts, or tracked
  state that lies on every machine with a different set installed". That objection is about *where*
  a registry would be stored, not about having one.

## Considered options

1. **Keep `kb/`, and symlink libraries into it from elsewhere.** No code change. But kb-retrieve
   finds libraries with Claude Code's Glob tool, which is ripgrep-based and does not follow
   symlinked directories by default, so a symlinked library may be invisible to retrieval. That
   would show up as `fact not found`, not as an error. Nothing would show the user that a library
   is a symlink onto another filesystem.
2. **Search roots** (the issue's proposal): `KB_LIBRARY_ROOTS`, a list of folders, each scanned for
   `*/INDEX.md`, with `<engine>/kb` as the default. This keeps ADR-0007's discovery by presence. But
   any library-shaped folder under a root is installed, including a stray backup copy. A moved
   library still vanishes silently, and the list has nowhere to record where a library came from.
3. **A registry, plus discovery under `kb/`.** Explicit for libraries elsewhere, zero setup for
   those under `kb/`. But it leaves two ways to be installed, and both have to be explained and
   tested.
4. **A registry only.** Every library is installed by being registered, wherever it is.

## Decision outcome

**Chosen: option 4.** A library is installed on a machine when it is registered there, and only
then. `<engine>/kb/` stops being special: it is the default folder new libraries are cloned into,
and nothing scans it.

### The registry is a per-machine file

**`~/.config/ai-kb/libraries`, in git-config format, read and written with `git config --file`.**

```ini
[kb]
	libraryHome = /mnt/c/workspace/kb
[library "azure-devops"]
	path = /mnt/c/workspace/kb/azure-devops
	origin = https://github.com/dhtaylor/azure-devops.git
```

- **Per machine, outside every repository.** It describes the machine it is on, so it cannot lie
  about another one. That is the answer to ADR-0007's objection.
- **Git-config format,** because it is the one format every consumer can already read, in every
  context, with no new dependency. Git handles quoting and locking. ADR-0008 chose git config for
  the engine's location for the same reason: git reads it where no shell startup file runs.
- **Not in `~/.gitconfig`.** Many people sync that file across machines in a dotfiles repository.
  That would carry one machine's paths onto another, the same failure ADR-0007 warned about, by a
  different route. A separate file also keeps a list a tool rewrites away from a person's name,
  aliases and signing keys. `kb.engineRoot` stays in global git config, where ADR-0008 put it. It
  is one value, and syncing it between machines with the same layout is harmless.
- **A fixed path.** It deliberately does not follow `XDG_CONFIG_HOME`. That variable is often set
  only in an interactive shell's startup file, which would put a hook and the terminal on two
  different registries. This is the trap ADR-0008 documents.

### A library declares its own name

**The name is the `domain:` value in the library's root `INDEX.md`.** Every library already
declares it, and in all six installed today it matches the folder name, so nothing has to be
migrated. The folder can then be called anything: a clone into `azure-devops-main/` is still
`azure-devops`, and every `[[azure-devops:…]]` link still resolves.

- `kb-library add` refuses a library whose root `INDEX.md` has no `domain:`.
- The registry key always equals the declared name. Two libraries cannot share a name, because a
  name can be registered once. `[[library:slug]]` is unambiguous by construction.
- A library that renames itself after registration is reported as a mismatch until it is
  re-registered.

### The library home

**`KB_LIBRARY_HOME` is where new libraries are cloned. It defaults to `<engine>/kb/`.**

- `kb-bootstrap` sets it on install, as `kb.libraryHome` in the registry file. The environment
  variable overrides the file when it is set. An environment variable alone is not enough, because
  hooks, cron and IDEs often do not see it (ADR-0008).
- It is a default for `kb-library add` and `kb-library import`, both of which take `--into DIR`. It
  is never a place libraries are discovered.

### One resolver, and states instead of silence

**`scripts/kb-libraries` is the only code that reads the registry.** Shell scripts call it, and
Python scripts import it. Every place that today assumes `<engine>/kb/` goes through it. For each
registered library it reports one state:

| State | Meaning |
|---|---|
| `ok` | the path exists and its root `INDEX.md` declares the registered name |
| `missing` | nothing is at the registered path |
| `not-a-library` | the path exists but has no root `INDEX.md` |
| `name-mismatch` | the root `INDEX.md` declares a different name |

Only `ok` libraries are served. **Every other state is reported at session start, by name and
path, and never dropped silently.** A moved library goes from a silent `fact not found` to
"registered library X is missing at /path".

### Commands

`scripts/kb-library` manages the registry:

- **`add <path | git-url> [--into DIR]`**: register a library already on disk, or clone it into the
  library home (or `DIR`) and register it, recording its `origin`.
- **`remove <name>`**: unregister. It never deletes files.
- **`list`**: every registered library, with its state and path.
- **`export`**: write each library's name and `origin` to standard output, never its path, because
  paths differ between machines. A library with no remote is written as a comment, saying it
  cannot be reproduced elsewhere.
- **`import <file> [--into DIR]`**: clone every listed library that is not registered yet, and
  register it. A name already registered with a different origin is reported and skipped, never
  overwritten.

`kb-create-domain` registers a new library as its last step.

### Registering never writes to the library

**A library is shareable: one repository, cloned by any number of people who do not own it.**
Registering it, moving it or upgrading the engine therefore can never require a commit to it. The
pre-commit hook is the one place today's design breaks that rule. Every library carries a copy of
the hook template in `.githooks/pre-commit`, and the template hardcodes the engine's layout, so a
layout change would mean a commit to every library.

**The hook moves into the engine.** `<engine>/library-hooks/pre-commit` holds what the template does
today. It finds the library's name and the other libraries through the registry. `kb-library add`,
and `kb-bootstrap` when it migrates or repairs, set the clone's `core.hooksPath` to that folder.
This is local git configuration. Git never commits or clones it, so every clone carries its own, and
`kb-bootstrap --check` reports a clone whose setting has drifted, as it does now for `.githooks`.

- A library carries no hook logic. The `.githooks/pre-commit` already in a library goes unused once
  its clone is wired to the engine. Its author can delete it at any time, and nothing depends on
  that happening.
- `kb-create-domain` stops writing a hook into new libraries.
- A library's CI is unchanged. It already fetches the engine and checks the library on its own.

### Migration

**`kb-bootstrap --apply` registers every library under `<engine>/kb/` once.** It is idempotent: a
second run changes nothing. After that, a library put into `kb/` by hand is not installed until it is
registered. That is the cost of having one way to be installed, and it was chosen on purpose.

### What changes for the consumers

- **Session start** injects the absolute path of every `ok` library, as it does now, and reports
  every other state.
- **kb-retrieve treats the injected list as the complete set of libraries.** The fallback Glob over
  `<engine>/kb/*/INDEX.md` is removed: once libraries can live anywhere, it would find only some of
  them, and a partial list that looks complete is worse than none. With no injected list, the agent
  answers `library list unknown — not searched`, in the same way it answers
  `engine root unknown — not searched` today.
- **`check-xlinks --installed`** resolves `[[library:slug]]` against the registry. A library that
  is not registered is not installed, which warns, as an absent library does today.
- **`check-golden`, `grade-eval` and `grade-routing`** resolve a cross-root `library:path`, and
  decide which reads are inside a library, through the registry instead of `lib.parent`.
- **The engine owns the library pre-commit hook** (see below).
- **`kb-due`, `kb-bootstrap`'s hook wiring, and the engine's and `kb-init`'s hooks** iterate over
  the registry.

## Consequences

**Good.**

- Libraries can live anywhere: another filesystem, a data disk, a share.
- There is exactly one way to be installed.
- A missing or renamed library is reported instead of silently answering `fact not found`.
- A library's name stays fixed wherever it is cloned.
- Moving to a new machine is an export and an import.

**Bad.**

- A registered path goes stale when its folder is moved. The difference from today is that this is
  now caught and named.
- A library cloned by hand needs `kb-library add <path>`. Through `kb-library add <git-url>` it is
  one step.
- The engine now depends on one more file outside any repository. `kb-bootstrap --check` reports on
  it, as it does for the other places it writes.
- All engines and worktrees on a machine share one registry, because it belongs to the user. A
  per-engine override can be added if a real case needs one.
- A library author can no longer add a library-specific step to the pre-commit hook, because the
  clone's hook folder is the engine's. No library has one today.

**Not covered.**

- **Executable bits on a `core.fileMode=false` mount** such as `/mnt/c` are tracked in
  [#50](https://github.com/dhtaylor/ai-kb/issues/50). Moving the hook into the engine removes most
  of that risk, because a library no longer holds an executable file. What remains is the engine's
  own placement.
- **Windows and WSL have separate home folders,** so a tool running on the Windows side does not see
  a registry in the WSL home. This is true of anything kept in the WSL home.

### Delivery

1. **The resolver and its consumers.** `kb-libraries`, `kb-library add/remove/list`, the
   migration in `kb-bootstrap`, the engine-owned library hook, and every consumer above. Tests
   first:
   - a fixture registry under a throwaway `HOME`, as the suite already does for `kb-init`, never the
     real file;
   - two libraries in different folders, one reached through a symlink;
   - every non-`ok` state reported;
   - a duplicate registration refused;
   - with only migrated `kb/` libraries registered, behaviour identical to today;
   - registering, moving and re-registering a library leaves its working tree and history
     untouched (`git status` clean, no new commit).
2. **The library home, export/import, and the documentation:** `KB_LIBRARY_HOME`,
   `kb-library export/import`, `kb-create-domain` registering its library and no longer writing a
   hook,
   CONVENTIONS §2/§3, and this ADR moved to Accepted.

A live check closes it: kb-retrieve answers a golden-set question from a library registered
outside `<engine>/kb/`, and `grade-routing` passes with no reads outside the routed library.

## Review trigger

Revisit if a second person needs a different set of libraries per engine on one machine, or if
libraries need to be shared between the Windows and WSL sides.
