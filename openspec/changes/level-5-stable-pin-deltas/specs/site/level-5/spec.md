## Purpose

The delta record for the 2026-09-05 re-verification of the level-5 page
(`docs/matrix/level-5-phd.md`) against the newest daily, with the page kept
pinned to the stable release v56.9.2.1.

## ADDED Requirements

### Requirement: Stable-pin delta record
Every change to the level-5 page MUST be recorded as a list of individually
justified deltas, each naming its exact wording and the evidence `path#L` at
the tag it cites. A shortcoming fixed only in the daily channel MUST stay RED
at the stable pin, with its PATH line saying when the fix landed and citing it
through a footnote carrying that daily's tag (`@v56.9.5.1`). Every in-repo
footnote MUST carry a verbatim, contiguous quote from its cited range at the
footnote's tag. Nothing outside the listed deltas moves.

#### Scenario: A reviewer checks the record
- **WHEN** a reviewer reads `git diff -- docs/matrix/level-5-phd.md` for this change
- **THEN** every hunk is one of the deltas D1–D7 listed in `proposal.md`, and the
  checked build reports the level with no BROKEN target and no `!` warning at
  v56.9.2.1

#### Scenario: A daily-channel fix is acknowledged
- **WHEN** a RED's remedy exists only in the daily channel
- **THEN** the RED text is unchanged, its PATH gains one sentence dated to the
  fix, and that sentence cites an `@v56.9.5.1` footnote whose quote is verbatim
  from the daily checkout
