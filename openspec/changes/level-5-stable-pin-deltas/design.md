# Design: level-5-stable-pin-deltas

## The delta discipline

Level 5 is the one page whose owner accepts only tiny, individually justified
deltas, and every change to its text is proposed here before it lands. The
discipline this change follows, and that a reviewer checks it against:

- **One delta per entry.** Each of D1–D7 in `proposal.md` names one change,
  its exact wording, and the evidence path `#L` at the tag it cites. Nothing
  is bundled.
- **The pin does not move.** `scripts/build-matrix.py` keeps level 5 at
  v56.9.2.1. Every ordinary footnote resolves there and every quote is taken
  from there.
- **Daily-channel facts get `@vTAG` footnotes.** A shortcoming fixed only in
  the daily channel stays RED at the stable pin; its PATH says when the fix
  landed and cites it with a footnote carrying `@v56.9.5.1` — the only place a
  footnote may point past the level's pin. Four such footnotes are added
  ([^41]–[^44]); no other footnote carries the tag.
- **Quotes are verbatim.** Each `>` line under a footnote copies contiguous
  characters from the cited range at the footnote's tag, no ellipsis, at most a
  few sentences. The checked build searches for it after collapsing whitespace
  and fails if it is absent. Rust doc-comment leaders (`//!`, `///`) and shell
  `#` leaders are kept in the quote where a quote spans lines, so the match is
  exact.
- **Nothing else moves.** No reflow, no rephrasing, no renumbering. Existing
  footnote targets and labels are unchanged. New footnotes take the next free
  numbers (41 onward). The `# Title` line and the `## Footnotes` section stay.

## How a reviewer checks it

1. `git diff -- docs/matrix/level-5-phd.md` and confirm every hunk is one of
   D1–D7: five one-line prose edits, twenty-eight `    > …` quote lines each
   directly under a `[^n]:` definition, four new `[^41]`–`[^44]` definitions
   with their quotes.
2. For each new PATH sentence, open the cited file at v56.9.5.1 and read the
   quoted lines.
3. For D1, `grep -n "fn the_fold_" crates/tillandsias-plan/src/fragments.rs`
   at v56.9.2.1: commutative and idempotent only.
4. Run the checked build with both checkouts present and read the level-5 line:
   `level-5-phd 44 footnotes, 32 quoted, checked at v56.9.2.1`, no BROKEN
   target, no `!` warning.
5. `openspec validate --changes` passes.
