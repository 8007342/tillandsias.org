## Purpose

The delta record for the 2026-09-05 re-verification of the level-5 page
(`docs/matrix/level-5-phd.md`) against the newest daily, with the page kept
pinned to the stable release v56.9.2.1.

## ADDED Requirements

### Requirement: The record and the diff match
Every change to the level-5 page MUST be recorded as one individually justified
delta, each naming its exact wording and the evidence `path#L` at the tag it
cites, and the page's diff MUST contain no hunk the record does not list. A
shortcoming fixed only in the daily channel MUST stay RED at the stable pin,
with its PATH line saying when the fix landed and citing it through a footnote
carrying that build's tag (`@vTAG`). Every in-repo footnote MUST carry a
verbatim, contiguous quote from its cited range at the footnote's tag. Nothing
outside the listed deltas moves.

#### Scenario: A reviewer checks the record
- **WHEN** a reviewer reads `git diff -- docs/matrix/level-5-phd.md` for this change
- **THEN** every hunk is one of the deltas the change's `proposal.md` lists,
  and the checked build reports the level with no BROKEN target and no `!`
  warning at the level's pin

#### Scenario: A daily-channel fix is acknowledged
- **WHEN** a RED's remedy exists only in the daily channel
- **THEN** the RED text is unchanged, its PATH gains one sentence dated to the
  fix, and that sentence cites an `@vTAG` footnote for that build, whose quote
  is verbatim from that build's checkout
