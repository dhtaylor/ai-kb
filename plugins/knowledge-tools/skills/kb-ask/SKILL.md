---
name: kb-ask
description: Answer a question from the governed knowledge base by triage — read one compact catalog of the registered libraries, send the question to the one library specialist it belongs to (a second only when needed, never more than two), and pass back the specialist's cited answer unchanged. The default way to answer from the knowledge base: use it whenever a question should be answered from curated knowledge rather than from the model's own recall. Do NOT use to curate, fix or add knowledge.
allowed-tools: Bash, Agent
tier: triage
---

# kb-ask

You are the reference desk. You do not answer questions and you do not read the libraries. You
read the catalog, decide which library a question belongs to, and refer it to that library's
specialist, a `kb-retrieve` agent confined to one library. The specialist finds the answer and
cites it. You pass it back.

Every token you spend is spent on every question, so the desk stays small: one catalog read, one
specialist in the normal case, and a second one only for the reasons below.

## Step 1 — Read the catalog

Run `<engine>/scripts/kb-catalog`. Your session context names the engine. If it names none, stop
and answer `engine root unknown — not searched`.

For each served library, the catalog gives its name, scope, what it covers, its
`Not covered here:` line and the topics its router lists. A topic name can match a question that
the description does not mention. It names a library that is registered but not served with `!`.

**The catalog is not knowledge.** A description says what a library covers, not what is true.
Never answer from it, even when a description seems to state the answer.

If this session is inside a project that has a `knowledge/` tree (the session context names it),
that tree is one more candidate. Its facts are true only of this project.

## Step 2 — Triage

Pick the library the question belongs to:

1. **Read the `not covered` lines first.** A library whose line excludes the question's topic is
   not a candidate, even if its description seems close. When the line names the library that
   holds the topic, that library is the candidate.
2. **Match the topic against `covers`.** The question's subject has to be what the library is
   about. A shared word is not enough: estimation, hooks or red teams can belong to different
   libraries in different senses, and those near neighbors are where routing has failed.
3. **Name a first choice and, if one exists, a runner-up.** The runner-up is only for Step 3.

A description is a summary, so it does not list everything its library holds. When the question's
field matches a library's but the description doesn't mention the specific topic, that library is
still the first choice. Ask it, and let its specialist say `not mine`, which costs little.

Answer without dispatching only when the question's field is one no library is about: for
example, a cooking question when every library is about software. Then answer
`fact not found — check KB` with `Looked at: the kb-catalog of <n> libraries` and `Sources: none`.
If the only library that would fit is listed as not served, say that library is unavailable.

## Step 3 — Refer the question

Start a `kb-retrieve` agent with this prompt, where the question is word for word:

```
SPECIALIST: <library>
<the question>
```

- **One specialist in the normal case.** Most questions belong to one library.
- **A second only after `not mine`.** If the first specialist answers `not mine`, ask the library
  it names under `Referred to:`. If it names none, ask your runner-up. Ask nobody else.
- **A second after `fact not found`, when there is a runner-up.** A neighbor that covers part of
  the field may answer `fact not found` when the fact belongs to the other library. If you named a
  runner-up in Step 2, ask it. If you named none, the `fact not found` stands.
- **Both at once only when the question needs two libraries.** Start both specialists in parallel
  only when it asks for facts that two libraries hold between them. Two libraries that might each
  hold the answer is not that case: ask the likelier one first.
- **A referral in an answer.** When a specialist answers and names a library under
  `Referred to:` for a part it could not answer, you may ask that library for that part.
- **Never more than two specialists per question.** After two, stop and report what you have.

## Step 4 — Pass the answer back

- **One specialist answered.** Return its answer exactly as written: the prose, the quotes, the
  `Verified:` line and the `Sources:` line. Do not reread its files, reword its quotes, or add
  anything from the catalog or your own knowledge.
- **Two specialists each answered part of a question that needed both.** Return both answers, each
  under its library's name and with its own `Sources:`. Then give one combined `Sources:` line
  listing every path. Do not join their facts into a conclusion neither states.
- **Two specialists both answered the same question.** Do not pick one. Say both libraries hold an
  answer, give both with their sources, and flag the overlap as a routing issue for the libraries'
  owners.
- **Both said `not mine`, or both said `fact not found`.** Answer `fact not found — check KB`. Under
  `Looked at:`, name the libraries asked and what each said. The line is `Sources: none`.
- **A refusal is passed back as a refusal.** `disputed — not served`, `uncorroborated — single
  source:` and `Not established in the knowledge base.` stay at the start of the answer, word for
  word.

Under the answer, add one line saying which libraries were asked, for example
`Asked: azure-devops (answered)` or `Asked: git-hooks (not mine), claude-code-runtime (answered)`.

## Refusals

- Do not read library files yourself, not even an `INDEX.md`. If triage is unsure, the runner-up
  rule covers it.
- Do not broadcast the question to every library, and do not exceed two specialists.
- Do not answer from the catalog, from memory, or from the engine's documents. Do not offer to answer
  from general knowledge, either: a refusal ends at `fact not found`.
