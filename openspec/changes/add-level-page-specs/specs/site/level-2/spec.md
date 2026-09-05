## Purpose

The "I barely understand my phone" page (`docs/matrix/level-2-phone.md`) answers
the practical questions a light user has before trusting software: is my stuff
private, does it cost money, does it need the internet, can it break my computer,
and what is currently broken. It is the privacy-and-assurance page, framed in
straight answers. The rules shared by every level are in `site/level-common`.

## ADDED Requirements

### Requirement: Straight-answer structure
The page MUST answer the practical questions directly (privacy, cost, internet
dependence, shutdown/damage) in plain language, with figures and flags where they
carry meaning.

#### Scenario: Reader's questions answered
- **WHEN** a non-expert reader asks the page's four questions
- **THEN** each has a direct, sourced answer

### Requirement: Privacy claim is structural, not intentional
The page MUST present the privacy story as structural (no server operated by the
project, nothing to send and no decision to trust), including its scope limit:
a service the user signs into themselves still sees what it is told.

#### Scenario: Privacy claim scoped
- **WHEN** the privacy claim is read
- **THEN** it covers the project's side only and names that boundary

### Requirement: Sourcing and honest limits
Every claim MUST carry a footnote resolving against the pinned tag. The page MUST
state the two honest limits in the project's own philosophy: passing tests are
evidence, not proof; convergence is not a promise of a zero floor.

#### Scenario: Limits are stated
- **WHEN** the page explains the verification discipline
- **THEN** both honest limits are present and footnoted to the pinned tag

### Requirement: Credential and release statements match the pin
Statements about where credentials live and about what the release process
withholds MUST match the pinned code and be scoped to the artifact they
describe: a secret store is named by what it is on each platform the page
covers, including any fallback the code has; a withholding is attributed to the
exact artifact withheld, never to the release as a whole.

#### Scenario: Credential store described
- **WHEN** the page says where a login is kept
- **THEN** the statement matches the pinned code on every platform it covers,
  fallback included, and is footnoted

#### Scenario: Release gate described
- **WHEN** the page says the release process refuses to publish something unsigned
- **THEN** the sentence names the artifact withheld and does not imply that the
  whole release is withheld
