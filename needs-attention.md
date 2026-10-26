---
name: needs-attention
description: Open findings from automated checks (kb-watch, kb-verify) and hygiene sweeps (kb-audit), by severity.
memory_type: reference
domain: fx
scope: general
metadata:
  type: index
  node_type: memory
  created: 2026-10-26
tags: [meta, hygiene, queue, watcher]
keywords: [needs attention, queue, findings, drift, watcher, unreachable]
---
# Needs attention

Findings from automated drift checks and hygiene sweeps. Detection only — nothing here was fixed automatically. See CONVENTIONS.md §3 and plugins/knowledge-tools/skills/kb-audit/SKILL.md for the queue's conventions.

```yaml
- id: c9831635
  category: "stale-recheck"
  status: "open"
  file: "widgets.md"
  section: "Limits"
  assertion: "printf \"SCHED-%s\\n\" CANARY-OUT; false"
  stamp: "2026-01-01 · by: agent · method: manual"
  exit: "exit 1"
  date: "2026-10-26"

```
