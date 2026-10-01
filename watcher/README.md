# Watcher

`kb-watch` compares a saved snapshot of an external source against a baseline and queues a drift
signal in the owning library's `needs-attention.md`. It never fetches. Snapshots are saved by hand
(ADR-0012), and they stay local, because this repository is public and they are copies of other
people's pages. `snapshots/` is gitignored, and only `allowlist.json` is tracked.

## Watched sources

| Source | Watched field | Why |
|---|---|---|
| `ms-learn-titles-ids-descriptions` (azure-devops) | Acceptance Criteria's work item types | Claim B of the azure-devops CONFLICTED fact. User Story appearing here would bear on resolving it. |

## Checking a source

1. Save the page's current HTML over its `current` snapshot (the path is in `allowlist.json`), with
   a browser's "save page" or `curl -sSL -o <current-snapshot> '<url>'`.
2. Run `kb-watch watcher/allowlist.json`. "0 new" means the watched field is unchanged.
3. A drift or unreachable entry lands in the library's queue. A human reads the source and decides
   what changes in the library. When the change is accepted, copy `current` over `baseline`.

A fresh clone has no snapshots, so every source reports `unreachable` until its baseline and
current files are saved. That is the correct answer for "nothing to compare", not a fault.
