## Purpose

The "Like I'm 5" page (`docs/matrix/level-1-five.md`) is the simplest rendering of
the Tillandsias platform that is still true. Its audience is a non-technical
reader who needs the three core ideas — a private "doll house" compute space, a
single guarded door to the internet, and throw-away-and-rebuild repair — plus the
project's honesty discipline (written-down promises, machine-checked where
possible, known broken things stated out loud). The rules shared by every level
are in `site/level-common`.

## ADDED Requirements

### Requirement: Simplest-true framing
The page MUST present the platform in the simplest terms that remain factually
accurate at the level's pinned release: a tiny cloud inside your own computer;
one "doorman" container with the single external egress; broken pieces are
rebuilt, never hand-glued.

#### Scenario: Reader follows the three ideas
- **WHEN** a non-technical reader finishes the page
- **THEN** they can describe what it is, the one-way-out rule, and the rebuild rule
  in their own words

### Requirement: App-vocabulary promise
The page MUST state the written promise that containers are presented to users
as "app" and how that promise is machine-checked, as the pinned source records
both.

#### Scenario: Promise attributed to source
- **WHEN** the promise and its machine check are described
- **THEN** each carries a footnote resolving at the pinned tag, with a verbatim
  quote that passes the checked build

### Requirement: Honest flags and RED/PATH pairing
The page MUST use the level's honesty frame in words its reader can repeat.
Every `> RED:` MUST be followed by a `> PATH:` line; a RED that no longer
matches the code at the pin MUST be corrected or downgraded rather than left
stale, and a PATH MUST NOT say that nothing has been done when the repository
records that something has.

#### Scenario: A RED is checked against the pin
- **WHEN** a claim is marked RED
- **THEN** it is true of the source at the pinned release tag, and the next line
  is its PATH

#### Scenario: A PATH describes the remedy's state
- **WHEN** a PATH says whether the remedy has been carried out
- **THEN** that statement matches the pinned code and the closed or open state
  of the recorded work, and is footnoted
