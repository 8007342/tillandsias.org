## ADDED Requirements

### Requirement: The reader-first record and the diff match
The level 5 hunks of this change MUST be exactly the deltas D1 to D3 that its
`proposal.md` lists. The new flag labels change how level 5 is rendered, not
its source text, and no flag on the page changes state.

#### Scenario: A reviewer checks the record
- **WHEN** a reviewer reads `git diff -- docs/matrix/level-5-phd.md` for this
  change
- **THEN** every hunk is one of D1 to D3, and the checked build reports level 5
  with no broken target and no warning at its pin
