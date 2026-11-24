"""In-process tests that kb-due and kb-report word the same items (#253): each takes what needs saying
from Attention.items, and neither decides it. The scripts are loaded as the engine loads them.

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
"""
import pathlib, unittest

from kbengine import attention

from test_attention import Fixture, ago, section

due = attention.script("kb-due")
report = attention.script("kb-report")

# What each command says of a kind, as a phrase found in its words. A kind absent from a table is one
# that command does not say: the nudge leaves out the manual stubs, the report everything that is no decision.
NUDGE = {"packets": "review packet", "sweep": "sweep due", "recheck": "due for recheck", "stale": "stale fact",
         "queue": "open queue item", "queue_unreadable": "unreadable queue record", "distill": "awaiting distillation",
         "unstamped": "unstamped source", "unsourced": "unsourced section", "contract": "contract",
         "archived": "declares archived"}
REPORT = {"packets": "Review packet", "queue": "Queue item", "queue_unreadable": "unreadable queue record",
          "recheck": "attended recheck", "sweep": "Sweep due", "manual_stubs": "Liveness: manual",
          "distill": "awaiting distillation", "contract": "ontract"}


class Same(Fixture):
    def said(self, att):
        """({kinds the nudge says}, {kinds the report says}) for one library."""
        line, _warnings, _counts = due.nudge_for(att, "fx")
        text = "\n".join(report.decisions_for(att, {}))
        return ({k for k, w in NUDGE.items() if line and w in line.split(": ", 1)[1]},
                {k for k, w in REPORT.items() if w in text})

    def expected(self, att):
        items = att.items
        return ({i.kind for i in items if i.says and i.kind in NUDGE},
                {i.kind for i in items if i.decision and not i.failed and i.kind in REPORT})

    def check(self, att):
        got, want = self.said(att), self.expected(att)
        self.assertEqual(got[0], want[0], "the nudge")
        self.assertEqual(got[1], want[1], "the report")
        return got

    def test_every_kind_is_said_by_the_nudge_and_every_decision_by_the_report(self):
        nudge, rep = self.check(self.everything())
        self.assertEqual(nudge, set(NUDGE))
        self.assertEqual(rep, {"packets", "queue", "queue_unreadable", "recheck", "sweep", "manual_stubs", "contract"} | {"distill"})

    def test_the_two_agree_on_what_a_packet_suppresses(self):
        self.everything()
        for kinds in ((), ("kb-audit",), ("kb-distill",), ("kb-audit", "kb-distill")):
            a = self.att(self.packet(*kinds), registered={self.root.resolve()})
            nudge, rep = self.check(a)
            self.assertEqual("sweep" in nudge, "kb-audit" not in kinds, kinds)
            self.assertEqual("sweep" in rep, "kb-audit" not in kinds, kinds)
            self.assertEqual("distill" in nudge, "kb-distill" not in kinds, kinds)
            self.assertEqual("distill" in rep, "kb-distill" not in kinds, kinds)
            self.assertEqual("manual_stubs" in rep, True)    # it waits on the sweep being due, not on a packet

    def test_the_two_agree_on_each_contract_state(self):
        for declared in ("2.1", "2.99", "7.0", "x.y", "2.7"):
            self.make(declared=declared, swept=ago(1))
            nudge, rep = self.check(self.att())
            self.assertEqual(("contract" in nudge, "contract" in rep), (declared != "2.7",) * 2, declared)

    def test_the_two_agree_when_a_field_failed(self):
        self.make(section("Old", 200, recheck="true"), swept=ago(1), extra="unasserted_ttl: 90d\n")
        a = self.att()
        line, warnings, _ = due.nudge_for(a)
        self.assertEqual(len(warnings), 2)                                  # the recheck and the stale fact
        self.assertTrue(all("unasserted_ttl" in w for w in warnings))
        self.assertEqual(report.decisions_for(a, {}),
                         ["Could not compute the facts due for recheck (ValueError). Run check-kb on the library to see why."])
        self.assertIsNone(line)

    def test_the_summary_is_counted_from_the_items(self):
        a = self.everything()
        _line, _w, counts = due.nudge_for(a, "fx")
        self.assertEqual(counts, {"packets": 1, "sweep": " ", "recheck": 2, "stale": 1, "queue": 1, "queue_unreadable": 1,
                                  "distill": 1, "unstamped": 1, "unsourced": 1, "contract": "2.1 (behind)"})
        self.assertEqual(due.summary_line([("fx", counts), ("report", {"report": 3})]).split(" · ")[0],
                         "KB due — weekly report: report 3")

    def test_the_nudge_leads_with_coverage_only_when_it_has_a_line(self):
        self.make(section("A", 1, recheck="true") + section("P", 1), swept=ago(1))
        self.assertEqual(due.nudge_for(self.att())[0], "fx: assertion coverage 1 of 2 sourced sections")
        self.make(section("A", 1, recheck="true"), swept=ago(1))
        self.assertIsNone(due.nudge_for(self.att())[0])


if __name__ == "__main__":
    unittest.main()
