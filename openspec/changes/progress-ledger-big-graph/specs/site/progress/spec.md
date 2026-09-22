## Purpose

The website's accountability ledger presents its complete pinned source record without turning task counts into an application score.

## ADDED Requirements

### Requirement: Complete pinned inventory

Progress MUST show every folded website finding, every canonical runtime spec at the site's pinned release, every archived runtime change including those without task records, and local website change records. The build MUST reject a runtime snapshot from a different release. Each source record MUST link to its source.

#### Scenario: A spec is obsolete or an archive has open tasks

- **WHEN** a source record is obsolete, deprecated or has unchecked tasks
- **THEN** it remains in the inventory and its status is visible

### Requirement: Summary first, full record on demand

Each record MUST begin collapsed with a title, identifier or source type, and concise status. Expanding a finding MUST reveal its claim, code or observed behavior, rationale, proposed remedy, evidence, dependencies, chronology and upstream link when those fields exist. A search MUST filter rendered records without dropping them from the built page.

#### Scenario: JavaScript is unavailable

- **WHEN** scripts do not run
- **THEN** native disclosure controls still open every record

### Requirement: Status axes stay separate

The page MUST say that a canonical spec's status describes its document lifecycle and that a fully checked archived task list records work, not current verified implementation. Findings remain the website's audit record, not a complete defect inventory or application score.

#### Scenario: A reader sees a complete checklist

- **WHEN** all tasks in an archived change are checked
- **THEN** the page labels the checklist complete and does not claim that the runtime capability is verified now
