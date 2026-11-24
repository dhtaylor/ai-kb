"""What an agent answered, read from its subagent transcript (#252). Stdlib only.

transcript_answer(transcript)   (cited, answer) of the agent's final answer, or None if it holds none.

The answer is the message of the agent's SubagentHandback call or, in a transcript with none, its last
text block: text written before a hand-back is preamble, and grading it fails a correct answer
(issue #32). The cited files are the answer's last `Sources:` line, comma-separated; `Sources: none`,
or no such line, cites nothing, and a note in parentheses on that line names no file. grade-eval,
kb-telemetry and kb-eval-sample read answers through this.
"""
import json, pathlib, re

SOURCES = re.compile(r"^\s*Sources:\s*(.*?)\s*$", re.M)


def transcript_answer(transcript: pathlib.Path):
    """(cited, answer) from a subagent transcript, or None if it holds no answer. Only
    assistant records count: Claude Code also logs the requests it sent, which carry copies
    of earlier blocks."""
    handback, text = None, None
    for line in transcript.read_text().splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        content = rec.get("message", {}).get("content") if isinstance(rec, dict) else None
        if rec.get("type") != "assistant" or not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                handback = (b.get("input") or {}).get("message")
            elif b.get("type") == "text" and b.get("text", "").strip():
                text = b["text"]
    ans = handback if isinstance(handback, str) else text
    if not ans:
        return None
    found = SOURCES.findall(ans)
    cited = found[-1] if found else ""
    cited = "" if cited.lower() == "none" else re.sub(r"\([^)]*\)", "", cited.replace("`", ""))
    return cited, SOURCES.sub("", ans)
