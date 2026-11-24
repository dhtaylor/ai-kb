"""In-process tests of reading an answer from a subagent transcript (scripts/kbengine/transcripts.py, #252).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
Transcripts are built in a temp dir, one JSON record per line, in the shape Claude Code writes.
"""
import json, pathlib, tempfile, unittest

from kbengine import transcripts


def text(t):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}}


def handback(t):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "h", "name": "SubagentHandback", "input": {"message": t}}]}}


class Answer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = pathlib.Path(self.tmp.name) / "t.jsonl"

    def read(self, *records, raw=""):
        self.path.write_text("".join(json.dumps(r) + "\n" for r in records) + raw)
        return transcripts.transcript_answer(self.path)

    def test_the_hand_back_is_the_answer_and_the_preamble_is_not(self):
        got = self.read(text("Let me look. Sources: wrong.md"),
                        handback("The flag is on.\nSources: widgets.md"), text("Done."))
        self.assertEqual(got, ("widgets.md", "The flag is on.\n"))

    def test_with_no_hand_back_the_last_text_block_is_the_answer(self):
        got = self.read(text("Let me look. Sources: wrong.md"), text("The flag is on.\nSources: widgets.md"))
        self.assertEqual(got, ("widgets.md", "The flag is on.\n"))

    def test_the_last_sources_line_is_the_citation(self):
        self.assertEqual(self.read(text("Sources: a.md\nmore\nSources: b.md, c.md"))[0], "b.md, c.md")

    def test_sources_none_or_no_line_cites_nothing(self):
        self.assertEqual(self.read(text("x\nSources: none"))[0], "")
        self.assertEqual(self.read(text("x\nSources: None"))[0], "")
        self.assertEqual(self.read(text("x"))[0], "")

    def test_a_parenthetical_note_and_backticks_name_no_file(self):
        self.assertEqual(self.read(text("x\nSources: `a.md` (reached via INDEX.md), b.md"))[0], "a.md , b.md")

    def test_no_assistant_text_is_no_answer(self):
        self.assertIsNone(self.read({"type": "user", "message": {"content": [{"type": "text", "text": "q"}]}}))
        self.assertIsNone(self.read(text("   ")))

    def test_a_request_record_is_not_an_answer(self):
        user = {"type": "user", "message": {"content": [{"type": "text", "text": "Sources: x.md"}]}}
        self.assertIsNone(self.read(user))

    def test_a_line_that_is_not_json_is_skipped(self):
        self.assertEqual(self.read(text("x\nSources: a.md"), raw="not json\n")[0], "a.md")


if __name__ == "__main__":
    unittest.main()
