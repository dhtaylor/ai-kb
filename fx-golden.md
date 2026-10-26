---
name: fx-golden
description: a test fixture.
memory_type: reference
domain: fx
scope: general
metadata:
  type: topic
  node_type: memory
  created: 2026-09-22
tags: [fx]
keywords: [fx]
---
# fx golden set

Unresolved case: not applicable — no CONFLICTED section here.
Cross-root case: not applicable — this fixture links to no other library.

```yaml
- case: positive
  question: How many things does a widget hold?
  expected_file: widgets.md
  expected_excerpt: "up to 12 things"

- case: negative
  question: What is the deploy target?
  expected_file: ""
  expected_excerpt: "fact not found — check KB"

- case: negative
  question: Who owns the widget service?
  expected_file: ""
  expected_excerpt: "fact not found — check KB"
```
