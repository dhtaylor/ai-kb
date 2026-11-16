"""In-process tests of the fact-file reader (scripts/kbengine/factfiles.py, #200, #201).

Run by tests/run-checks with scripts/ on PYTHONPATH:
    PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py'
They reach the reader through files() and sections() only: markdown in, sections out.
"""
import pathlib, tempfile, unittest

from kbengine import factfiles


def read(text):
    return factfiles.sections(text)


class Fences(unittest.TestCase):
    def test_heading_stamp_and_source_in_a_backtick_fence_are_examples(self):
        secs = read("## Real\n\n```\n## Fake\nSource: x\nVerified: 2026-01-01 · by: a · method: m\n"
                    "Recheck: true\n```\n")
        self.assertEqual([s.title for s in secs], ["", "Real"])
        self.assertEqual(secs[1].sources, [])
        self.assertEqual(secs[1].stamps, [])
        self.assertEqual(secs[1].orphan_rechecks, [])

    def test_a_tilde_fence_hides_the_same_things(self):
        secs = read("## Real\n~~~\n## Fake\nSource: x\n~~~\nSource: y\n")
        self.assertEqual([s.title for s in secs], ["", "Real"])
        self.assertEqual([x.text for x in secs[1].sources], ["Source: y"])

    def test_any_fence_line_toggles_as_check_kb_reads_it(self):
        secs = read("## A\n~~~\n```\n## Fake\n~~~\n")
        self.assertEqual([s.title for s in secs], ["", "A", "Fake"])

    def test_an_indented_fence_still_fences(self):
        secs = read("## A\n  ```\n## Fake\n  ```\n")
        self.assertEqual([s.title for s in secs], ["", "A"])

    def test_a_status_marker_in_a_fence_marks_nothing(self):
        secs = read("## A\n```\nstatus: CONFLICTED\nstatus: UNCORROBORATED\n```\n")
        self.assertEqual(secs[1].status, "served")


class Sections(unittest.TestCase):
    def test_text_before_the_first_heading_is_a_section_of_its_own(self):
        secs = read("intro\nSource: a\n## One\n")
        self.assertEqual((secs[0].level, secs[0].line, secs[0].title), (0, 0, ""))
        self.assertEqual(len(secs[0].sources), 1)

    def test_heading_level_title_line_and_text(self):
        secs = read("# T\n\n###   Deep dive  \nbody\n")
        deep = secs[2]
        self.assertEqual((deep.level, deep.line, deep.title, deep.heading),
                         (3, 3, "Deep dive", "###   Deep dive"))
        self.assertEqual(deep.text, "###   Deep dive  \nbody\n")

    def test_seven_hashes_and_a_missing_space_are_not_headings(self):
        self.assertEqual(len(read("####### x\n#x\n")), 1)

    def test_has_content_ignores_blanks_source_lines_and_the_conflicted_marker(self):
        secs = read("## A\n\nSource: s\n\n## B\ntext\n## C\nstatus: CONFLICTED\n")
        self.assertEqual([s.has_content for s in secs], [False, False, True, False])


class Status(unittest.TestCase):
    def test_served_conflicted_and_uncorroborated(self):
        secs = read("## A\nx\n## B\nstatus: CONFLICTED\n## C\n  status: UNCORROBORATED\n")
        self.assertEqual([s.status for s in secs[1:]], ["served", "CONFLICTED", "UNCORROBORATED"])

    def test_conflicted_wins_but_both_flags_are_kept(self):
        sec = read("## A\nstatus: UNCORROBORATED\nstatus: CONFLICTED\n")[1]
        self.assertEqual(sec.status, "CONFLICTED")
        self.assertTrue(sec.uncorroborated)

    def test_a_marker_applies_to_the_heading_it_sits_under(self):
        secs = read("## Outer\n### Inner\nstatus: UNCORROBORATED\n")
        self.assertEqual([s.status for s in secs[1:]], ["served", "UNCORROBORATED"])


class Stamps(unittest.TestCase):
    def test_stamp_with_by_and_method(self):
        st = read("## A\nSource: s\nVerified: 2026-09-22 · by: agent · method: manual\n")[1].stamps[0]
        self.assertEqual((st.line, st.date, st.by, st.method), (3, "2026-09-22", "agent", "manual"))

    def test_missing_by_and_method_are_none_but_the_stamp_is_seen(self):
        st = read("## A\nVerified: 2026-09-22\n")[1].stamps
        self.assertEqual([(s.date, s.by, s.method) for s in st], [("2026-09-22", None, None)])

    def test_method_without_by(self):
        st = read("## A\nVerified: 2026-09-22 · method: query\n")[1].stamps[0]
        self.assertEqual((st.by, st.method), (None, "query"))

    def test_an_indented_stamp_is_ignored_and_reported(self):
        sec = read("## A\nSource: s\n  Verified: 2026-09-22 · by: agent · method: m\n  Recheck: true\n")[1]
        self.assertEqual(sec.stamps, [])
        self.assertEqual(sec.sources[0].stamp, None)
        self.assertEqual(sec.indented, [(3, "Verified"), (4, "Recheck")])
        self.assertEqual(sec.orphan_rechecks, [])

    def test_stacked_sources_each_take_their_own_stamp(self):
        sec = read("## A\nSource: one\nVerified: 2026-01-01 · by: agent · method: m\n"
                   "Source: two\nVerified: 2026-02-02 · by: human · method: m\n")[1]
        self.assertEqual([(s.text, s.stamp.date) for s in sec.sources],
                         [("Source: one", "2026-01-01"), ("Source: two", "2026-02-02")])
        self.assertEqual(len(sec.stamps), 2)

    def test_a_second_source_with_no_stamp_of_its_own_is_unstamped(self):
        sec = read("## A\nSource: one\nSource: two\nVerified: 2026-01-01 · by: agent · method: m\n")[1]
        self.assertEqual([s.stamp is not None for s in sec.sources], [False, True])

    def test_a_stamp_before_any_source_is_listed_and_pairs_with_nothing(self):
        sec = read("## A\nVerified: 2026-01-01 · by: agent · method: m\nSource: one\n")[1]
        self.assertEqual(len(sec.stamps), 1)
        self.assertIsNone(sec.sources[0].stamp)

    def test_a_stamp_does_not_cross_a_heading(self):
        secs = read("## A\nSource: one\n## B\nVerified: 2026-01-01 · by: agent · method: m\n")
        self.assertIsNone(secs[1].sources[0].stamp)


class MultiLineSources(unittest.TestCase):
    def test_a_citation_runs_over_the_lines_it_wraps_onto(self):
        sec = read("## A\nSource: [[a]],\n  [[b]] and\n[[c]]\n\nprose\n")[1]
        src = sec.sources[0]
        self.assertEqual(src.text, "Source: [[a]],")
        self.assertEqual(src.cite, "Source: [[a]],\n  [[b]] and\n[[c]]")

    def test_a_citation_stops_at_the_next_marker(self):
        for nxt in ("Source: [[b]]", "Verified: 2026-01-01", "Recheck: true",
                    "Recheck (attended): true", "## Next"):
            sec = read(f"## A\nSource: [[a]]\n{nxt}\n")[1]
            self.assertEqual(sec.sources[0].cite, "Source: [[a]]", nxt)

    def test_wrapped_lines_are_still_read_as_lines(self):
        sec = read("## A\nSource: [[a]]\nstatus: CONFLICTED\n")[1]
        self.assertEqual(sec.status, "CONFLICTED")


class Rechecks(unittest.TestCase):
    STAMP = "Verified: 2026-01-01 · by: agent · method: manual\n"

    def stamp_of(self, body):
        return read("## A\nSource: s\n" + self.STAMP + body)[1]

    def test_on_the_next_line(self):
        sec = self.stamp_of("Recheck: test -f x\n")
        rc = sec.stamps[0].recheck
        self.assertEqual((rc.line, rc.cmd, rc.attended), (4, "test -f x", False))
        self.assertEqual(sec.orphan_rechecks, [])

    def test_after_one_blank_line(self):
        sec = self.stamp_of("\nRecheck: test -f x\n")
        self.assertEqual(sec.stamps[0].recheck.cmd, "test -f x")

    def test_after_two_blank_lines_it_is_not_attached(self):
        sec = self.stamp_of("\n\nRecheck: test -f x\n")
        self.assertIsNone(sec.stamps[0].recheck)
        self.assertEqual([r.cmd for r in sec.orphan_rechecks], ["test -f x"])

    def test_text_between_stamp_and_recheck_detaches_it(self):
        sec = self.stamp_of("note\nRecheck: true\n")
        self.assertIsNone(sec.stamps[0].recheck)
        self.assertEqual(len(sec.orphan_rechecks), 1)

    def test_attended(self):
        sec = self.stamp_of("Recheck (attended): gh auth status\n")
        rc = sec.stamps[0].recheck
        self.assertEqual((rc.cmd, rc.attended), ("gh auth status", True))

    def test_a_recheck_with_no_stamp_is_an_orphan(self):
        sec = read("## A\nRecheck: true\n")[1]
        self.assertEqual([(r.line, r.cmd) for r in sec.orphan_rechecks], [(2, "true")])

    def test_a_recheck_without_a_command_is_not_one(self):
        sec = self.stamp_of("Recheck:\n")
        self.assertIsNone(sec.stamps[0].recheck)
        self.assertEqual(sec.orphan_rechecks, [])

    def test_the_stamp_with_no_recheck_below_it_at_the_end_of_the_file(self):
        sec = read("## A\n" + self.STAMP.rstrip("\n"))[1]
        self.assertIsNone(sec.stamps[0].recheck)

    def test_each_stamp_keeps_its_own_recheck(self):
        sec = read("## A\nSource: a\n" + self.STAMP + "Recheck: one\nSource: b\n" + self.STAMP
                   + "Recheck: two\n")[1]
        self.assertEqual([s.recheck.cmd for s in sec.stamps], ["one", "two"])

    def test_an_indented_recheck_attaches_to_nothing(self):
        sec = self.stamp_of("  Recheck: true\n")
        self.assertIsNone(sec.stamps[0].recheck)
        self.assertEqual(sec.orphan_rechecks, [])


class Files(unittest.TestCase):
    def tree(self, *paths):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = pathlib.Path(tmp.name)
        for p in paths:
            f = root / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n")
        return root

    def kinds(self, *paths):
        root = self.tree(*paths)
        return {str(p.relative_to(root)): k for p, k in factfiles.files(root)}

    def test_every_kind(self):
        got = self.kinds("INDEX.md", "CONVENTIONS.md", "widgets.md", "fx-golden.md", "needs-attention.md",
                         "widgets-open-questions.md", "widgets-contradictions.md",
                         "episodic/2026-01-01-note.md", "sources/stub.md", "sub/INDEX.md", "sub/leaf.md")
        self.assertEqual(got, {
            "INDEX.md": "router", "CONVENTIONS.md": "path_addressed", "widgets.md": "fact",
            "fx-golden.md": "golden", "needs-attention.md": "queue",
            "widgets-open-questions.md": "state_leaf", "widgets-contradictions.md": "state_leaf",
            "episodic/2026-01-01-note.md": "episodic", "sources/stub.md": "source_stub",
            "sub/INDEX.md": "router", "sub/leaf.md": "fact"})

    def test_excluded_folders_are_pruned_at_any_depth(self):
        got = self.kinds("a.md", "documents/d.md", "plugins/p.md", "scripts/s.md", ".github/g.md",
                         ".githooks/h.md", ".claude-plugin/c.md", ".claude/c.md", ".git/x.md",
                         "sub/documents/deep.md", "sub/.claude/deep.md", "sub/keep.md")
        self.assertEqual(set(got), {"a.md", "sub/keep.md"})

    def test_pruned_folders_are_not_walked(self):
        root = self.tree("a.md", ".git/objects/x.md")
        walked = []
        import os
        real = os.walk
        def spy(top, *a, **k):
            for dirpath, dirnames, filenames in real(top, *a, **k):
                walked.append(dirpath)
                yield dirpath, dirnames, filenames
        os.walk = spy
        try:
            list(factfiles.files(root))
        finally:
            os.walk = real
        self.assertEqual(walked, [str(root)])

    def test_a_directory_may_be_named_like_a_kind_without_being_one(self):
        got = self.kinds("sources/INDEX.md", "sources/a-golden.md", "episodic/INDEX.md",
                         "sources/deep/stub.md", "x/episodic/note.md")
        self.assertEqual(got, {"sources/INDEX.md": "router", "sources/a-golden.md": "golden",
                               "episodic/INDEX.md": "episodic", "sources/deep/stub.md": "source_stub",
                               "x/episodic/note.md": "episodic"})

    def test_only_markdown_files_are_listed_and_the_order_is_by_path(self):
        root = self.tree("b.md", "a.md", "a/z.md", "notes.txt", "c.markdown")
        self.assertEqual([str(p.relative_to(root)) for p, _ in factfiles.files(root)],
                         ["a/z.md", "a.md", "b.md"])

    def test_kind_of_classifies_a_path_that_is_not_on_disk(self):
        self.assertEqual(factfiles.kind_of(("a", "b.md")), "fact")
        self.assertEqual(factfiles.kind_of(("INDEX.md",)), "router")
        self.assertIsNone(factfiles.kind_of((".git", "x.md")))


if __name__ == "__main__":
    unittest.main()
