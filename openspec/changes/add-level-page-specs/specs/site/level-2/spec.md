## Purpose

The "I barely understand my phone" page (`docs/matrix/level-2-phone.md`) answers
the practical questions a light user has before trusting software: is my stuff
private, does it cost money, does it need the internet, can it break my computer,
and what is currently broken. It is the privacy-and-assurance page, framed in
straight answers.

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

### Requirement: Credential-store wording accuracy
The claim that login credentials go into "your operating system's own password
store" is overstated: the GitHub token lives in the guest Vault, and Linux/headless
hosts use a keychain-backed file fallback (`vault_bootstrap.rs:1363-1364`). Any
editor MUST reword this clause to "a local secret store" with the fallback noted,
per the audit.

#### Scenario: Credential claim re-sourced
- **WHEN** the page describes where logins are stored
- **THEN** it matches the observed behavior (Vault + keychain fallback file), not
  an OS-password-store-only claim

### Requirement: Known doctoring burden
The "release process refuses to publish the unsigned file" sentence is true but
scoped to the MSIX (the unsigned EXE/ZIP still publish with a warning when
`TILLANDSIAS_SIGNING_ACCOUNT` is unset; `.github/workflows/release.yml:645-658`).
Any editor MUST scope that sentence and, if the footnote stays, add the workflow
line to the span.

#### Scenario: MSIX withholding is scoped
- **WHEN** the page describes the unsigned-Windows-package fix
- **THEN** the sentence names the MSIX specifically and does not imply the whole
  release is withheld

## ADDED Artifacts

### Artifact: Level-2 audit annotations
`docs/matrix/level-2-phone.audit.md` — agent-facing annotations from the
2026-09-04 audit. Companion to the page; never rendered by the build.