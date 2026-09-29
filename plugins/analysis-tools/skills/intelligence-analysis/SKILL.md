---
name: intelligence-analysis
description: |
  Use this skill to review a work product for analytic rigor, or to coach the user in
  intelligence-analysis (IA) tradecraft. It applies the discipline of professional
  intelligence analysis — structured analytic techniques, a bias-mitigation catalog, and
  an analytic-standards rubric — to *any* reasoned product: an email, a user story, a
  spike recommendation, a forecast, a strategy memo, a formal assessment. Every standard,
  technique, and bias it uses is retrieved at run time from the `intelligence-analysis`
  knowledge library, never recalled from this file. Review mode tells the user where the
  thinking is strong and where it is weak, anchored to specific passages, with a concrete
  fix for each weakness. Coach mode trains the user to think better by teaching one
  technique at a time against their own real work.

  Trigger whenever the user wants their reasoning or an analytic product checked,
  critiqued, pressure-tested, or graded — "review this assessment," "critique my
  analysis," "how sound is this argument," "poke holes in my reasoning," "is my
  conclusion supported," "what am I missing here," "did I consider the alternatives" —
  and whenever they want to get better at analysis, forecasting, or structured thinking:
  "coach me on intelligence analysis," "help me reason like an analyst," "drill me on
  this." Fire even when they don't say the words "intelligence analysis," as long as the
  request is about the quality of *thinking* in a product rather than its prose or its
  code.

  Do NOT use for: cleaning up prose or removing AI-writing tells (that's the `humanizer`
  skill); reviewing code for correctness, bugs, or style (that's `code-review`); or
  writing a user story from scratch (that's `create-user-story` — though this skill
  pairs well as a review pass over a finished story).
---

# Intelligence Analysis

## This skill holds no tradecraft — it retrieves it

Every standard, technique, and bias named below lives in the `intelligence-analysis` knowledge
library, not in this file. This file is the *procedure*: how to calibrate, what order to work in,
what a finding must contain, how to run a coaching session. Whenever the procedure calls for a piece
of tradecraft — a standard's exact wording, a probability term, a technique's steps, a bias's name and
its mitigation — go get it. Do not answer from what you already know about intelligence analysis:
recalled tradecraft is exactly the failure mode this split exists to prevent, and it is
indistinguishable from the retrieved kind right up until it is subtly wrong.

### Finding the library

Your session context may already name the installed knowledge libraries. If it does, use that. If it
does not, locate the engine root your session context provides (never write a literal path for it —
see the engine's `CONVENTIONS.md` §1) and glob `<engine>/kb/*/INDEX.md`. Do not infer the library set
from a bare directory listing of `kb/`. Find the library whose `INDEX.md` describes
intelligence-analysis tradecraft, and load it first — always the router, never a guess at a filename.

If no such library is found: **say so plainly** — "the intelligence-analysis knowledge library isn't
installed, so I can't run a grounded review or coaching session" — and stop. Do not fall back to
reviewing from memory. A review that sounds authoritative but cites nothing is worse than no review.

### The retrieval rules that apply here (from the library's own retrieval contract)

- **Descend one hop at a time.** Read the library's `INDEX.md`, pick the child file(s) the current
  step needs, load only those.
- **Cite every file you used**, by name, in the output (see `Sources:` below). A refusal cites
  nothing.
- **Never read or search a file named `*-golden.md`, or anything under a `documents/eval-*/` folder.**
  Those are the library's own answer key and evidence trail — reading them turns your citations into
  recitation and makes them worthless as evidence that you actually retrieved anything.
- **Refuse a `CONFLICTED` section.** If the fact you need is marked disputed, say so — name both
  claims and who holds them — and do not pick one, average them, or hedge around the conflict.
- **Say when a fact isn't there.** If the library doesn't cover something you need (a technique, a
  bias, a standard), say `fact not found in the intelligence-analysis library` and proceed with what
  you do have, naming the gap. Do not fill it from memory.
- **Surface currency when it's stamped.** If the fact you're citing carries a `verified:` date, you
  may mention it; if it carries none, don't imply it's current.

## Two modes

Infer the mode from the request. A product handed over with "what do you think / is this sound / poke
holes" is **Review**. "Help me get better / teach me / drill me" is **Coach**. A request that's
genuinely ambiguous ("let's work on my analysis") gets **one** clarifying question, then proceed —
don't interrogate.

The modes share a spine (the same retrieved techniques, the same retrieved standards) and feed each
other: a review surfaces the weaknesses coaching then targets, and the coaching log tells a review
which weaknesses this user repeats.

---

## Review mode

The goal is a review the user can act on: honest about strengths, specific about weaknesses, and
prescriptive — never a vague "consider more alternatives," always "here is the passage, here is the
standard it misses, here is the fix."

### Retrieval economy: load on need, not up front

In review mode, load the library's `INDEX.md` and its tradecraft-standards file, and **nothing else up
front**. Read the product against those standards and form your candidate weaknesses from the product
itself, then run the gates below on each candidate. Open another library file only when **a candidate
that has already survived the gates** needs something from it: the exact position rule for a buried
bottom line, a technique for its fix, or the precise name of a bias. Never open a file to look for more
to find. A catalog of techniques and biases read in advance becomes a checklist, and a checklist
applied to clean work manufactures findings. The library is where you confirm and name a finding, not
where you go hunting for one.

### 1. Calibrate to the product — do this first, always

Before judging anything, decide *how much rigor this product warrants*. Misjudging this is the most
common way a review goes wrong, and in practice the failure is almost always the same direction:
**over-reviewing.** Piling several findings onto a clean two-line note doesn't look thorough, it looks
like you can't tell what matters. Restraint is the skill.

Place the product on this ladder and hold it to that bar *only*. The levels and their finding caps are
this skill's own behavior (they are not in the library — calibrating *this* skill's output volume is
not a tradecraft fact):

- **Light** (a tweet, a chat message, a quick email, a flash or alert note, an offhand claim). **Cap: 0–1 finding.** Ask
  only: is the single load-bearing claim stated with more certainty than its basis supports? If yes,
  that's your one finding. If not, say "sound for a quick note" and stop. Do not flag a missing bottom
  line, missing alternatives, or missing sourcing at this level — those checks do not apply here, and
  raising them is a false positive, not diligence.
- **Medium** (a user story, a spike recommendation, a design decision, a memo, a PR description). **Cap:
  ~2–3 findings.** The working range for most products. Check: is the main judgment up front and
  supported; is information kept separate from assumption and from judgment; are the key assumptions
  surfaced; is at least one serious alternative weighed; is uncertainty expressed in calibrated
  language rather than a vague hedge; are the sources that carry the conclusion characterized.
- **Full** (a formal assessment, forecast, estimate, threat/risk analysis, or strategy document).
  **Cap: ~3–5 findings.** The complete rubric applies — retrieve it
  (below) — including analysis of alternatives, an explicit statement of how this relates to prior
  analysis, and calibrated language throughout, but still prioritized and capped.

**The product's form sets its level.** If its form is named in a level's list above, that is its
level — stakes and audience do not promote a listed form. A memo that drives a large decision is still
a memo: review it at Medium. Two defaults cover the rest:

- **A short message is Light**, whoever sent it and whatever it concerns. A few sentences sent as an
  email, a chat post or a flash note is a message, even when a headquarters sends it about a serious
  subject.
- **A form no list names is Medium.** A news item, an op-ed, an equity note or a board update is
  Medium unless it actually is a formal assessment, forecast, estimate, threat/risk analysis or
  strategy document. Only then is it Full.
- **A title does not set the level. What the document is does.** A Full product is a finished,
  standalone analytic product built to be relied on: key judgments stated as judgments, a stated
  confidence, the reasoning and sourcing laid out to be checked. A short briefing, case note or update
  headed "ASSESSMENT" or "INTELLIGENCE BRIEFING" is still a briefing, note or update. Review it at
  Medium unless it has that structure.

Promoting a product because it matters is the usual route to over-reviewing it.

**Retrieve which checks actually apply at each level** from the library's tradecraft-standards file
before scoring — the mapping above is this skill's plain-language paraphrase for calibrating quickly.
The library's calibration table governs *which standards apply* at a level, and is the one you cite
from; the form rule above governs *which level* a product is at.

The caps are ceilings on a *prioritized* list, not quotas — come in under them freely, and a genuinely
clean product at any level gets **zero** findings and a plain "this is sound." When the level is
unclear, ask what the product is for and who reads it. State the level you're reviewing at, so the
user can push back.

**The already-addressed gate (run before writing any finding).** For each candidate weakness, first
check whether the product *already handles it* — states the uncertainty, names the alternative,
characterizes the source, flags the caveat. If it does, it is **not** a finding; it is probably a
strength. Most false positives come from flagging a concern the author already met. Read what's on the
page before faulting it for what isn't.

### 2. Find the analytic line

Locate the product's main judgment (its bottom line) and the reasoning offered for it. If you can't
find a single clear claim, that is itself the first and often most important finding — retrieve the
library's argumentation standard and cite it: a product with no locatable bottom line fails it before
any subtler check matters.

**But finding is not enough — also check position.** If the judgment is not in the product's opening
sentences, retrieve the library's writing-craft file for the exact position rule and the disguised cases it names (a chronology-first postmortem, a report that
opens with background numbers, a brief where the conclusion appears only in the final sentence). A
judgment that arrives after throat-clearing context, background data, or a timeline fails that
position rule even when the judgment itself, once you reach it, is clear and well-stated. A buried
bottom line is usually the highest-priority weakness: rank it first, above subtler findings about
language or sourcing, unless something threatens the conclusion itself more. Do not credit
argumentation clarity until you've confirmed *position*, not just *existence* — a common false strength
is crediting a well-worded conclusion that simply arrives too late.

### 3. Select and run the techniques the product's level calls for

Run these checks on the product itself first. When a candidate weakness has survived the gates and its
fix calls for a technique, retrieve the library's technique catalog and its problem-to-technique table
to name the right one. Pick technique(s) that fit the weaknesses you're actually seeing — do not run the
whole catalog on a product that needs one check.
A medium product typically needs: the assumptions behind the conclusion surfaced, the sourcing behind
it examined, and — only if a genuine competing explanation exists — a light pass at weighing it against
the evidence (does anything actually discriminate between them, or is the evidence equally consistent
with both?). A full-level product may warrant the full method for weighing competing hypotheses; get
its exact steps from the library rather than paraphrasing them here — a step count or a named step
stated in this file would itself be an embedded fact.

### 4. Score against the rubric

Retrieve the library's tradecraft-standards file and its rating scale. Rate the product against the
standards that apply at the calibrated level — no more. Anchor every rating to the text: quote the
passage that justifies it. Give an overall read in prose, never a single rolled-up score across
standards — the library explains why that's unreliable; retrieve and, if useful, echo that reasoning
rather than restating it from memory.

### 5. Deliver findings — strengths first, then prioritized weaknesses

Use this output shape (this template is this skill's own behavior — it is deliberately not stored in
the library, which holds facts about tradecraft, not this skill's formatting choices):

```
## IA Review — <product name>

**Reviewed at:** <Light | Medium | Full> level — <one line on why: audience + stakes>
**Analytic line (bottom line as written):** "<the product's main judgment, quoted — or: none locatable>"

### Strengths
- <specific thing done well> — <which standard it satisfies, quoted passage>
  (1–3 items; genuine, not filler)

### Weaknesses (most to least threatening to the conclusion)
1. **<short label>** — <standard, exactly as the library names it>
   > "<exact quoted passage, or 'absent: no ___ anywhere in the product'>"
   Why it matters: <one line — how it threatens the conclusion>
   Fix: <concrete rewrite, or the technique to run, named as the library names it>

### Scorecard (only the applicable standards)
| Standard | Rating | Anchor |
|----------|--------|--------|
| <as the library names it> | <as the library's scale names it> | <quoted text> |

### If I were the analyst, the one change I'd make first
<the single highest-leverage fix>

Sources: <library file>, <library file>
```

Rules on top of the format:

- **Every weakness is a triple:** the *quoted passage*, the *standard or technique it misses* — cited
  exactly as the library states it, numbering and name included — and a *concrete rewrite or fix*. No
  floating criticisms.
- **Name a bias or fallacy precisely when one applies to a finding that has already survived the
  gates**, using the library's own name for it and its own prescribed mitigation from its
  bias-to-technique mapping — never "watch out for bias" on its own,
  and never a bias name you're recalling rather than retrieving. Getting the substance right but
  reaching for the wrong retrieved label sends the user to the wrong fix, so if you're not sure which
  entry in the mapping fits, say so rather than guessing.
- **Prioritize and cap.** Order weaknesses by how much they threaten the conclusion, and stop at the
  level's cap. Coming in under the cap is good, not lazy.
- **Expected count tracks quality, not level.** The caps are ceilings for products *with several real
  weaknesses*, not output targets. A careful analyst's Full-level product may legitimately yield zero
  to two findings — if triage leaves you two, output two; don't inflate toward the range. Conversely,
  four or more candidates on a Medium product (or two or more on a Light one) after triage means you
  are over-reading it.
- **Match fix elaboration to the level.** Light: one sentence, one concrete substitution — no
  frameworks, no multi-step procedures. Medium: two or three sentences naming the technique or the
  rewrite. Full: a short paragraph with the technique and an example. Prescribing a formal multi-step
  technique for a Light product is itself a proportionality failure.
- **A sourcing finding names the specific unsupported claim**, not the general area. "This estimate
  cites no publication" is a finding; "sources could be better characterized" is not. Before writing
  one, ask: *which specific factual assertion here has no identified source?* **False-strength trap:**
  a number wearing the *costume* of sourcing — a percentage with a date range or a method label but no
  actual publication or dataset behind it — is still uncited. Do not credit it as well-characterized
  sourcing; the unattributed study behind it is the finding. The trap is narrow: it applies only when
  the number's basis names no study, dataset or issuing body. A metric attributed to a named source's
  own verification or output is characterized sourcing, not costume — don't demand a bibliography for it.
- **Per-finding gate before writing.** For each candidate weakness, run three checks in order:
  1. *Already-addressed?* — does the product state the uncertainty, name the alternative,
     characterize the source, or flag the caveat *anywhere* — including a footnote, a limitations
     line, a later qualifier, or informal wording? Handling need not use a dedicated section or formal
     terminology. If it's handled, it is at most a strength, never a finding.
  2. *Audience-appropriate?* — is the "gap" just standard background the intended audience already
     has? A reader with the expected domain training wouldn't need it spelled out, so its absence is
     not a finding. Don't demand a product explain its own field to its own experts.
  3. *Conclusion-threatening?* — does removing this finding leave the product's conclusion intact? If
     yes, cut it. If your candidate list still exceeds the cap after this triage, assume you are
     over-reading the product and cut further — never raise the cap.
- **Prescribe process, not vigilance.** "Run the assumptions-check technique on the two premises
  below," not "be careful about your assumptions." A finding that only tells the user to be more
  careful has not done its job — it must point at a retrievable technique or a concrete rewrite.
- **Consult the coaching log** (below) if it exists, and weight findings toward the patterns this user
  repeats — those are the ones worth their attention. Note in the review when a weakness is a repeat.
- **A clean product gets zero findings**, stated plainly. Manufacturing weaknesses to look thorough is
  the single biggest way a review loses the user's trust.
- **Always end with the `Sources:` line**, naming every library file the review actually drew on. A
  review that cites nothing has not shown its work.

---

## Coach mode

The aim is a reflex the user keeps, not a lecture they nod at and forget — retrieve the library's
governing note on why merely naming a weakness doesn't fix it, and let that shape the session: it
means this mode never just describes a weakness, it makes the user practice the technique that
counteracts it. Coaching is active: one technique at a time, applied to the user's own real work, with
the user doing the thinking.

### Session shape

1. **Read the coaching log** (below). What's been taught? Which weakness recurs? Target a recurring
   gap over a random topic, or the one from a product the user just brought.
2. **Anchor to real work.** Ask for (or reuse) an actual product of theirs. A live example beats an
   invented one — it's their reasoning on the line, which is what builds the reflex.
3. **Diagnose and isolate one technique.** Retrieve the library's technique catalog and its
   problem-to-technique table; pick the single technique that fixes the diagnosed weakness. Working
   more than one technique in a session fixes none of them well.
4. **Teach adaptively:**
   - **First exposure** (the technique isn't in the log yet): *Explain → Demonstrate → Apply.*
     Retrieve the technique's definition and worked shape from the library, give it in a few
     sentences, show one short worked example, then hand the user a piece of their own work to try it
     on. Confirm and correct.
   - **Seen before** (it's in the log): go *Socratic* instead of re-explaining — pose the situation
     and make the user produce the move ("here's your conclusion — what's the first thing this
     technique has you do?"). Only confirm after they've tried. Raise the difficulty as they get
     fluent: fewer scaffolds, harder cases, and eventually ask them to pick which technique applies
     unprompted.
5. **Make them apply it** to their own material, and pressure-test with a question from the prompt
   bank below.
6. **Update the coaching log** with what was taught, how it went, and one open drill for next time.

### The Socratic discipline (non-negotiable)

When you pose a question meant to make the user think, **that question ends your turn.** Emit nothing
after it — no self-answer, no "you'd probably say…", no stacked second question. Wait for the human. A
fabricated answer teaches nothing; the whole value is their real attempt. This is the same discipline
the `create-user-story` skill lives by.

### The prompt bank

Reusable challenges to pull from once you've diagnosed the weakness. Each targets a specific reasoning
gap; when you use one, name the pattern it's exposing using the library's own term for it (retrieve the
bias-to-technique mapping or the technique catalog rather than labeling it from memory) — don't invent
or recall a label here.

- "What would change your mind?" — if they can't answer, something is closed off from evidence.
- "If the opposite had happened, would you have been surprised?" — if no, the confidence is unearned.
- "Which single piece of evidence is your conclusion most dependent on? What if it's wrong?"
- "What's the strongest case *against* your conclusion?"
- "How would [the adversary / the user / the other team] tell this story?"
- "What should you be seeing if you're right — and are you?"
- "Put a number on it." — pushes a vague hedge toward the library's calibrated scale.
- "Is that reported, assumed, or judged?"
- "What's the base rate?"

### Deliberate-practice drills

Short exercises to leave as homework or run live — pick the one matching the diagnosed weakness, and
prefer drills on the user's real, current work over invented scenarios:

- **Conflating what was reported with what was concluded** — hand them a paragraph of their own
  writing; have them tag every clause as reported, assumed, or judged.
- **Single hypothesis** — give them their conclusion; require two more competing explanations and one
  piece of evidence that actually favors one over the others.
- **Vague uncertainty** — rewrite each hedge word in a document using the library's calibrated scale
  plus a range, and a confidence statement kept separate from it.
- **Unexamined assumptions** — list the premises a conclusion rests on; mark which are verified and
  which are load-bearing and not.
- **Overconfidence** — premortem: "it's six months later and this call was wrong — write the two-line
  postmortem now."

## The coaching log (cross-session memory)

Persistence lives at `~/.claude/ia-coaching-log.md` — a user-level file outside every repository, never
inside the engine, a library, or a project. It records: recurring weaknesses (with a count), techniques
taught and when, the user's demonstrated strengths, and any open drill.

- **Read it** at the start of both modes, if it exists.
- **Update it** at the end of a coaching session, and after a review that confirms a recurring pattern
  in a log that already exists.
- **Only a coaching session creates it.** A review never creates the file — if there is no log, the
  review simply proceeds without one. When a coaching session finds no log, create it from this
  template:

  ```markdown
  ---
  name: ia-coaching-log
  description: Per-user IA coaching progress — recurring weaknesses, techniques taught, open drills.
  memory_type: procedural
  metadata:
    type: progress-log
    created: <YYYY-MM-DD>
  tags: [intelligence-analysis, coaching, progress]
  ---
  # IA Coaching Log

  ## Recurring weaknesses (with count)
  - <weakness> — seen <n>x — last <YYYY-MM-DD> — status: <working | improving | resolved>

  ## Techniques taught
  - <technique> — introduced <YYYY-MM-DD> — level reached: <explained | applied | fluent>

  ## Demonstrated strengths
  - <what the user reliably does well>

  ## Open drill
  - <the exercise left for next session>

  ## Session notes (most recent first)
  - <YYYY-MM-DD>: <what was worked, how it went, next step>
  ```

- **Update rules:** increment a weakness's count when a review or session confirms it again; advance a
  technique's level as the user demonstrates it; record one open drill per session so the next session
  has a starting point.
- This file is plain user-level state, not a knowledge library — it carries no router entry and no
  `INDEX.md` line anywhere, and nothing here is subject to the retrieval contract above (it is not
  tradecraft; it is a record of one user's sessions).
