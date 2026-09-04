## Purpose

The "Like I'm 5" page (`docs/matrix/level-1-five.md`) is the simplest rendering of
the Tillandsias platform that is still true. Its audience is a non-technical
reader who needs the three core ideas — a private "doll house" compute space, a
single guarded door to the internet, and throw-away-and-rebuild repair — plus the
project's honesty discipline (written-down promises, machine-checked where
possible, known broken things stated out loud).

## ADDED Requirements

### Requirement: Simplest-true framing
The page MUST present the platform in the simplest terms that remain factually
accurate for the pinned release: a tiny cloud inside your own computer; one
"doorman" container with the single external egress; broken pieces are rebuilt,
never hand-glued.

#### Scenario: Reader follows the three ideas
- **WHEN** a non-technical reader finishes the page
- **THEN** they can describe what it is, the one-way-out rule, and the rebuild rule
  in their own words

### Requirement: App-vocabulary promise
The page MUST state the written promise that containers are always presented to
users as "app" and that the waking-up message is machine-checked for banned words.

#### Scenario: Promise attributed to source
- **WHEN** the promise and its machine check are described
- **THEN** they carry a footnote resolving to the pinned tag

### Requirement: Honest flags and RED/PATH pairing
The page MUST use the level's honesty frame. Every `> RED:` MUST be followed by a
`> PATH:` line; a RED that no longer matches the pinned code MUST be corrected or
downgraded rather than left stale.

#### Scenario: A RED is checked against the pin
- **WHEN** a claim is marked RED
- **THEN** it is true of the source at the pinned release tag, and the next
  footnote exists

### Requirement: Known doctoring burden
The audit (2026-09-04) found the doorman-key RED/PATH pair materially false at
the pin: packet 755-qcxh is closed and the CA key now travels as a podman secret
with a 0600 clamp/heal. Any editor MUST resolve this pair (re-source to the
closed packet + `main.rs:3017-3020`/`3378-3382`, or downgrade to a past-tense
flag) before the next publish.

#### Scenario: Audit annotations consulted
- **WHEN** an editor changes this page
- **THEN** they consult `docs/matrix/level-1-five.audit.md` and either fix or
  explicitly carry forward each open finding

## ADDED Artifacts

### Artifact: Level-1 audit annotations
`docs/matrix/level-1-five.audit.md` — agent-facing annotations from the
2026-09-04 audit. Companion to the page; never rendered by the build.