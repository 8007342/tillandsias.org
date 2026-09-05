<!-- ============================================================ -->
<!-- level-5-phd.audit.md — AGENT ANNOTATIONS, NOT PAGE CONTENT. -->
<!-- Build pipeline does NOT read this file (only level-*.md      -->
<!-- slugs listed in scripts/build-matrix.py LEVELS are rendered). -->
<!-- Audit scope: tillandsias runtime repo at v56.9.2.1 (stable)   -->
<!-- and v56.9.5.1 (newest daily). Run 2026-09-05.                 -->
<!-- ============================================================ -->
Valid for pin v56.9.2.1 only; superseded by the next record under `docs/audit/`.

# Agent audit annotations — level 5 ("MathWiz / Hacker")

Level 5 had no annotation file until now, because the 2026-09-04 page specs
declared its explanation "owned elsewhere" and forbade one. That declaration was
retired on 2026-09-05: the page is edited here, under the delta discipline, and
annotations are the input to the next delta proposal rather than something to
avoid.

## One text change with no delta record

The title line changed on 2026-09-05 in commit `dac63c1`:

    - # Level 5 — For the PhD / MathWiz / Hacker
    + # Level 5 — For the MathWiz / Hacker

It landed on its own commit at 06:25, hours before the delta discipline existed
in the tree (`607b5cf`), so it broke no rule that was in force. It is recorded
here because the page's change trail should be complete, and because the rule
now in force would require a record for the same edit today.

It was not grafted onto `openspec/changes/level-5-stable-pin-deltas`. That
change's virtue is that its record and its diff match exactly, and listing a
delta whose hunk is not in the diff would cost a reviewer that check.

Evidence that the page and the generated site agree on the new title: the tab
label is `I'm a MathWiz / Hacker` in the `LEVELS` table of
`scripts/build-matrix.py`, and the page's body never used the dropped word.

## Two clause-level sourcing gaps, proposed rather than applied

Both are recorded as unchecked tasks in
`openspec/changes/level-5-stable-pin-deltas/tasks.md` §3, with their verbatim
quotes. They are new deltas on landed ones, so they wait for the operator:

1. The scorer path-to-green makes three daily-channel claims and carries one
   footnote covering the first. The gate clause and the backfill fraction have
   no citation.
2. The denominator path-to-green rests on "the script prints that label", and
   its footnote evidences the labelling rather than the printing.

## What was checked, and what was left alone

Every hunk of `git diff bb09c7a^ bb09c7a -- docs/matrix/level-5-phd.md` was
confirmed to be one of the deltas D1 to D7 the change lists. The mathematics
itself was not re-argued: this run checked only what the deltas touched, the
footnote targets and the quotes.

Two dates were wrong and were corrected on 2026-09-05 in both the page and the
change record: the fixes landed on trunk on 2026-09-03 and reached the daily
channel in v56.9.4.1, cut 2026-09-04. No release was cut on 2026-09-03.

## Known burden for the next pin bump

Moving level 5 off v56.9.2.1 will break the strong-law footnotes: the
methodology block they quote was rewritten after the stable release, so the
quotes will no longer be found in their cited ranges and the checked build will
say so. Re-sourcing them, and re-deriving the flags they support, belongs to
that bump and is not scheduled here.
