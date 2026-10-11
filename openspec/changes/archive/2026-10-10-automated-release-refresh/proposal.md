# Pin moves go in automatically; only changed or new claims need the operator

## Why

Every Level 5 pin move so far has waited on an OpenSpec change and an operator
review box. Four boxes are unchecked today: `level-5-v56-9-21-1`,
`level-5-v56-9-27-2`, `level-5-v56-10-9-1` and `level-5-centicolon-guarantee`.
Most of the deltas in them are mechanical. Lines were inserted above a cited
span, and the cited text did not change. A reviewer reading such a delta learns
nothing they could not check with `diff`. Meanwhile the deltas that do change
what the page asserts sit in the same queue and wait just as long.

The release refresh (`skills/update-website/scripts/release-refresh.sh`) now
draws that line by machine. `scripts/anchors.py` finds each cited span again
at the new tag, either as the identical block of lines or as the verbatim
quote. If it finds the span, it rewrites the line range. If it cannot, it
reports the citation and leaves that level's pin where it was. Replayed over
the v56.10.9.1 release, the tool re-anchored 105 of the 121 footnote targets
that had been corrected by hand. 101 of the 105 landed on the exact line the
person chose, and the other 4 differ only in how wide the span is. The tool
left the other 14 for a person, and the person did change every one of them.
For Level 5 alone, it reproduced D1–D4 of `level-5-v56-10-9-1` exactly and
flagged D6 and D7 for a decision.

## What Changes

- **Mechanical moves need no review.** A pin move of any level, Level 5
  included, goes in without an operator review when every change it makes is
  a re-anchored line range whose cited text was found again verbatim at the
  new tag. The same holds for regenerated data: the spec snapshot, the metrics
  series and the site-wide citation ranges. The evidence is the run's fragment
  in `refresh.d/`, which lists every moved citation, how it was found, and the
  tags.
- **Claims still need the operator.** Level 5 deltas that change what the page
  asserts still go through an OpenSpec change and the operator's review. That
  covers a new or changed sentence, label, quote or flag; a retarget to a
  different file; and a footnote whose text was not found again.
- **The page says which is which.** When a level's pin has moved past the last
  human review of its claims, its footnote note says so: "re-anchored to vX
  automatically; a person last reviewed the claims against vY". The
  `reviewed` map in `refresh.d/` records each review.
- **Advisory queue.** A flag whose cited file changed in the release is listed
  in the run's `review_queue`. The list never blocks a move. It is where a fix
  that landed beside an unchanged quoted line would show up.
- **The rule's trigger.** Until this change is archived, `scripts/anchors.py`
  keeps the old rule for Level 5. It writes the mechanical deltas as a
  generated OpenSpec change and does not apply them. Archiving this change
  lifts the gate. Deleting it without archiving keeps the old rule.

## What the four open boxes become under this rule

- `level-5-v56-9-21-1`: all eight deltas are range corrections, so the whole
  change is mechanical. It can be archived without further review.
- `level-5-v56-9-27-2`: six range corrections are mechanical. The added D1
  paragraph is a new claim and still needs review.
- `level-5-v56-10-9-1`: D1–D5 are mechanical. D6–D7 retarget citations to Lua
  ports and change one label, and those still need review.
- `level-5-centicolon-guarantee`: every delta changes what the page asserts,
  so the whole change still needs review.

## Non-goals

This change does not alter any level's prose or flags, and it does not
archive any of the four changes above. It does not change the rule that a
level describes the stable channel.
