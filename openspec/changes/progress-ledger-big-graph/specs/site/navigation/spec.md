## Purpose

Add the system map to the site's existing single-menu navigation.

## ADDED Requirements

### Requirement: Five pages behind one collapsing menu

The menu MUST list Home, What is it?, Live progress, Slides and Big Graph in that order. Exactly one page is visible at a time and the active entry is marked. Big Graph MUST have a direct hash link and slide 6 MUST offer a link to it. The five explanation levels remain internal to What is it?.

#### Scenario: A reader opens Big Graph directly

- **WHEN** the URL has `#big-graph`
- **THEN** the graph page is visible and its menu entry is current

### Requirement: Non-level claims retain source and status

Home, Progress, Slides and Big Graph MUST make no runtime claim stronger than the release-pinned explanation levels and linked source records support. Big Graph MUST mark intended behavior and current limits visibly instead of relying on a caption or tooltip.

#### Scenario: A runtime status changes at a pin bump

- **WHEN** the site's pinned release changes
- **THEN** the source snapshot and the graph's current-state labels are reviewed with the audit before publish
