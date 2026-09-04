## Purpose

The "I'm a Cyber Security expert" page (`docs/matrix/level-4-security.md`) is the
architecture interrogated rather than described: the true boundary (Linux has no
VM), egress as routing not content filtering, the hardening-flags gap (a
`debug_assert!` compiled out in release), secrets and the opt-in control channel,
supply-chain provenance limits, and where ephemerality stops being a control. Its
audience reads threat models for a living.

## ADDED Requirements

### Requirement: The boundary correction stands
The page MUST keep its platform-by-platform correction front and center: Linux
provisions no VM; the enclave is a hypervisor boundary on macOS/Windows and a
namespace boundary on Linux where an escape lands as the invoking user's UID.

#### Scenario: Correction is retained
- **WHEN** the architecture boundary is described
- **THEN** the Linux-no-VM correction is present with its escape-blast-radius
  footnote

### Requirement: Hardening claims are the audited truth
The mandatory four-flag envelope, the `debug_assert!`-only enforcement call in
`container_spec.rs:376-383`, the same-token-on-both-branches litmus file, and the
advisory-only false-pass scanner MUST be stated per the pin. These are the page's
best-verified findings — do not soften them; only the follow-up bar-raise
citation (plan/index.yaml#L14302, order 634-39ik) needs to be added.

#### Scenario: Hardening gap is sourced
- **WHEN** the hardening-flag gap is stated
- **THEN** it cites the `debug_assert!` call site and the same-token litmus file,
  and the bar-raise follow-up points at plan/index.yaml#L14302

### Requirement: Egress and proxy honesty
The page MUST keep the precise egress story: network placement plus proxy env
vars, no packet filter; SslBump where it exists (one bumped host,
release-assets.githubusercontent.com); the RESTRAINT that the proxy does no payload
inspection; and the spec-vs-code CA gap (spec promises a per-launch EC P-256 tmpfs
chain; the code emits one self-signed RSA-2048 30-day cert).

#### Scenario: Egress claims stay exact
- **WHEN** the proxy and egress are described
- **THEN** the one-bumped-host splice, the no-payload-inspection statement, and
  the spec-vs-code CA gap are all present and sourced

### Requirement: RED precision MUST follow the audit
Each RED/PATH claim MUST be accurate against the pinned code. Known doctoring
burden from the 2026-09-04 audit:
- Soften "for the missing hypervisor on Linux nothing is recorded at all" — the
  escape blast radius IS recorded (`podman-idiomatic-patterns/spec.md#L201-L204`).
- "415 litmus files" is a directory-entry count; say 411 litmus files or
  "the litmus corpus".
- Re-point [^21] to `plan/index.yaml#L12087` (order 588-ttex); the cited
  homebrew-research file alone does not carry the claim.
- Scope "nothing validating a push server-side" to what this repo shows (GitHub
  branch protection is external and unverifiable here).

#### Scenario: Precision edits applied
- **WHEN** an editor revises RED/PATH wording on this page
- **THEN** the Linux-boundary record, the corpus count, the [^21] target, and the
  push-validation scope all match the audit findings

### Requirement: Assurance-claim boundary
The page MUST preserve the closing discipline: the convergence argument is not a
security argument; falsifiability and evidence-is-not-proof are the load-bearing
invariants; a passing suite is a bounded signal over defects someone wrote a
failing-capable litmus for.

#### Scenario: Assurance boundary preserved
- **WHEN** the assurance claim is stated
- **THEN** it declines to read a passing suite as a security argument or a
  probability

## ADDED Artifacts

### Artifact: Level-4 audit annotations
`docs/matrix/level-4-security.audit.md` — agent-facing annotations from the
2026-09-04 audit. Companion to the page; never rendered by the build.