# Capturing a fact

One page. For everything this leaves out, read [CONTRIBUTING.md](CONTRIBUTING.md) next.

## Is it worth capturing?

If you'd want to know this the next time someone touches this area — a surprising result, a fix, a
gotcha, something that didn't work — capture it. If nothing happened worth repeating, don't: an
empty note is noise.

## Which tier does it belong to?

Capture doesn't decide what's true — that's distillation's job, later, with a human in the loop. But
it does decide where the note lands, and that follows the same test the contract uses for facts:

> Is this true only of this repo/deployment, or true wherever this product/tool/concept appears?

Working inside a project, capturing files into that project's own tree by default — right for
anything repo-specific. If what you saw is true of a product or tool in general, not just this
deployment, pass `--into <library>` instead of taking the default. A general observation left to
default into a project tree becomes one of many copies that will drift.

## How to capture

In a Claude session: `/kb-capture`. From a terminal: `kb-capture`. Either way it writes a dated note
under `episodic/` in the nearest knowledge tree and routes it — **never** straight into a domain's
semantic fact files. Hand-writing a fact there skips the review this whole path exists to provide.

## What a correct note contains

Two sections, kept separate:

- **What happened** — what you ran and what you saw. Exact commands, exact values, exact error text.
  When the exact value is a secret, redact it in place and keep the rest: `DB_PASSWORD=<redacted>`.
- **What you believe but did not check** — inferences, assumptions, things the docs said but nobody
  tested. Keep the hedge words: "probably", "we didn't test that", "the docs say". Omit if empty.

If a claim came from somewhere — a doc, a teammate, a vendor page — say so in the sentence itself.
Without that, it can never earn a real source link later and stays an unsourced guess forever.
Something you were told but did not check (a teammate's claim, say) goes in the second section,
attributed to whoever said it.

The title matters most: it becomes the filename and the first line a retrieval agent reads, so keep it
short. Describe what was done and seen, never what you concluded: "Checkout 504s cleared after a
container restart", not "Restart fixed the checkout timeouts".

**Example:**

> ## What happened
> Ran the nightly import against staging. It failed twice with `connection reset` around record
> 40,000, both times at the same offset. Retrying from scratch succeeded both times.
>
> ## What we believe but did not check
> Probably a connection-pool timeout — the import holds one long-lived connection, and 40,000
> records took about as long as the pool's idle-timeout window. Didn't check the pool config.

## Common wrong moves

- Writing a fact straight into a library's semantic files instead of capturing it.
- Inventing a fact from memory because you're confident — if you didn't check it this session, it's
  a belief, not an observation.
- Stating an untested belief as fact — write "probably", not a flat claim.
- Leaving out where a claim came from, so it can never get a real source later.
- Putting a secret — a token, a password, a key — in a note. It gets committed; secrets don't belong
  in git at all.

## What happens next

Later, `kb-distill` reads the note, decides what is a fact and what stays speculation, and a human
approves before anything becomes durable knowledge. Full detail: [CONTRIBUTING.md](CONTRIBUTING.md).
