# ai-kb

A governed knowledge base: libraries of facts that each carry their source, their evidence and their currency, so an agent can serve them with known confidence.

## Trust

**Stamp**:
A dated record, attached to one section, that the section's claim was checked. It certifies the evidence behind the check, not the identity of whoever ran it.
_Avoid_: verification, sign-off, human approval

**Evidence tier**:
How strongly a stamp's evidence supports its claim, judged by what backs it (a replayable assertion, a cited excerpt, someone's word), never by who wrote it.
_Avoid_: trust tier, human tier, agent tier

**Asserted stamp**:
A stamp backed by a passing check that anyone can rerun, kept beside the claim it defends. Every other stamp is an **unasserted stamp**: someone's word, whoever gave it.
_Avoid_: verified stamp, human stamp

**Sourced section**:
A section a library serves that cites its source; the unit assertion coverage counts.
_Avoid_: cited section, sourced fact

**Assertion coverage**:
The share of a library's sourced sections that carry asserted stamps; the measure of how far that library can be trusted by a stranger.
_Avoid_: freshness, verification rate

**Horizon**:
How long a domain's facts can be expected to stay true, set by how fast that domain's world changes. A property of the domain, not of any stamp.
_Avoid_: TTL (when the domain's rate of change is meant)

**Arbiter**:
The person who approves the checks behind stamps, settles failed checks and contradictions, and owns attended decisions. An Arbiter gates consequences; they do not confer truth.
_Avoid_: validator, human verifier, approver

**High-blast-radius fact**:
A fact whose being wrong causes damage that is expensive or impossible to undo, such as a deploy target or a credential reference. Changing one is always an attended decision.
_Avoid_: sensitive fact, critical fact

**Consumer**:
Anyone who uses a published library without knowing its author, so they can trust only evidence they could check for themselves.
_Avoid_: user, reader (when a stranger to the author is meant)
