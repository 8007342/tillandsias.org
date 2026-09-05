## Purpose

The "I'm a power user" page (`docs/matrix/level-3-power.md`) is the anatomy: what
runs where, what survives a teardown, and where the sharp edges are. Its audience
understands containers, networking and CI, and expects the architecture plus its
honest failure list. The rules shared by every level are in `site/level-common`.

## ADDED Requirements

### Requirement: Enclave anatomy matches the documented-membership guard
The page MUST describe the enclave's membership as the documented-membership
guard (`scripts/check-enclave-membership-documented.sh`) records it at the pin,
or MUST label its list explicitly non-exhaustive. The project's own record is
that a hand-maintained prose roster goes stale, so this spec carries no roster
either: the guard is the source, the page cites it, and the single-egress claim
— one dual-homed proxy is the enclave's only way out — stays intact and
footnoted to the network spec at the pin.

#### Scenario: Anatomy matches the live guard
- **WHEN** the page enumerates enclave members
- **THEN** the list matches the guard's roster at the pin or is explicitly
  non-exhaustive, and the single-egress claim is present and sourced

### Requirement: Survivorship claims match the pinned code
The page MUST state what survives a stop, a `podman system reset`, and a
`--reset-guest` per the pinned code, for each artifact it names: the mirror
volume and working copy, the vault's unseal material, the model cache, and the
`--reset-guest` wipe set. Where the code writes an artifact to a place a spec
invariant does not cover (a fallback location), the page MUST say so rather than
state the invariant as observed behaviour.

#### Scenario: Survivorship lines match the pin
- **WHEN** an editor changes a survivorship bullet
- **THEN** each artifact's fate (stop / `podman system reset` / `--reset-guest`)
  matches the pinned code, fallback locations included, and is footnoted

### Requirement: Every RED is true at the pin
Every RED on the page MUST be true of the code at the level's pinned tag, not of
a plan entry the code has outrun. A RED the pinned tag has fixed becomes a
past-tense flag or a GREEN; a RED fixed only in a build newer than the pin stays
RED and its PATH names that build; a RED that holds only for a subset of hosts
(those not re-initialised, one platform) says so.

#### Scenario: A stale RED is caught before publish
- **WHEN** the page is edited and the checked build is run
- **THEN** each RED line traces to the code at the pin or to an open work item
  re-verified at the pin, with no plan entry the code has already outrun

### Requirement: Gate and CI statements
The local-gate description (litmus tests plus traces, the grandfathered
allowlist, and which workflows exist and how each is triggered) MUST stay
accurate at the pin and sourced to `methodology/ci.yaml`,
`openspec/litmus-tests/unbound-grandfathered.txt` and the workflow files. Any
count the page gives for the grandfathered files or the workflows is the count
at the pin.

#### Scenario: Gate claims stay sourced
- **WHEN** the gate or CI section is edited
- **THEN** the grandfathered count and the workflow inventory still match the
  pinned tree, and are footnoted with quotes that pass the checked build
