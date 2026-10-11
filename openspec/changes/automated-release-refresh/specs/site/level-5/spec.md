## Purpose

How Level 5 moves once this change is accepted.

## ADDED Requirements

### Requirement: Mechanical Level 5 moves need no operator review
A Level 5 pin move whose only edits are line ranges re-anchored by
`scripts/anchors.py` (identical lines, or the verbatim quote, found exactly
once at the new tag) MUST NOT require an OpenSpec change or an operator
review. The move MUST be recorded in that run's `refresh.d/` fragment, with
each citation's old target, new target and the rule that found it.

#### Scenario: Lines inserted above a cited span
- **WHEN** a release inserts lines above every changed Level 5 citation and
  changes none of the cited text
- **THEN** the refresh moves the Level 5 pin and its ranges, and no
  `openspec/changes/level-5-*` directory is created

### Requirement: Claims still need the operator
Every Level 5 delta that changes a sentence, label, quote, flag or a
footnote's file MUST still be proposed in an OpenSpec change and reviewed
by the operator before archival.

#### Scenario: A cited script was ported
- **WHEN** a cited file no longer exists at the new tag
- **THEN** the refresh leaves Level 5 at its old pin, reports the citation as
  `path-gone` with candidate files, and a person writes the retarget as a
  proposed delta
