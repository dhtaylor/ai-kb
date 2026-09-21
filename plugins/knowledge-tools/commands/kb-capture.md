---
description: Capture what this session learned as an episodic note in the nearest knowledge tree. Records; does not classify.
argument-hint: "[title] [--into TREE]"
allowed-tools: Bash, Write
---

Write an episodic note about what this session established, then file it with the engine's
`kb-capture` script. **Your only job is the body. Filing is the script's.**

## Write the body — the one rule

**Keep what was observed separate from what was believed, and never upgrade one into the other.**

Use two sections:

```markdown
## What happened

What was run and what was seen. Exact commands, exact values, exact error text — copied, not
paraphrased. A rounded number here becomes a rounded fact later.

## What we believe but did not check

Inferences, assumptions, things read in documentation, things nobody tested. Keep the hedges in the
words that show them: "probably", "we didn't test that", "the docs say", "I think". Omit the section
if it is genuinely empty.
```

This matters more than it looks. Distillation decides what becomes a fact by reading these words — it
refuses a speculation *because the note says it was not tested*. Tidy a hedge into confident prose and
the next step promotes a guess it can no longer recognise as one. **A capture that reads well and has
lost its hedges is worse than no capture.**

Do **not**:
- decide what is a fact, what tier it is, or which domain it belongs to — that is distillation;
- add a currency stamp or a `Source:` line;
- summarise away the failed attempts. What did not work is often the most reusable part.

## The title obeys the same rule — and matters more

The title becomes the filename, the `description`, and **the router hook: the line a retrieval agent
reads first, before it opens anything**. It is the most-read sentence in the note. So it describes
what was **done and seen**, never what was concluded.

- Right: `Checkout 504s in staging; 47 idle-in-transaction connections; terminating them restored service`
- Wrong: `Checkout 504s traced to idle connections exhausting the pool`

The second reads better and asserts a cause nobody checked — and here the numbers do not even support
it, since 47 connections against a pool of 50 is not exhaustion. A hedge preserved in the body and
upgraded in the title is still upgraded, in the one place everyone reads.

## File it

Write the body to a temporary file, then:

```bash
"$KB_ENGINE_ROOT/scripts/kb-capture" --title "<what was done and seen>" --from <tmpfile> [--into <tree>]
```

**Handling what the user typed after `/kb-capture`:**
- `--into <tree>` — pass it through to the script unchanged.
- Any other text is a **hint for the title**, not an argument. Use it to steer the title, which still
  follows the rule above. **Never pass free text to the script as a positional argument**: the script's
  positional is a directory, so `checkout timeouts` would be read as a path and fail.

The script finds the nearest tree, names and dates the note, adds frontmatter and routes it newest
first. If it reports there is no tree, say so and relay its suggestion — do not create one yourself,
and do not file the note somewhere improvised.

If `KB_ENGINE_ROOT` is unset, say so and stop.

Report the path it printed.
