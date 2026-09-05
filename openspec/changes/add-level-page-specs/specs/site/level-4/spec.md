## Purpose

The "I'm a Cyber Security expert" page (`docs/matrix/level-4-security.md`) is the
architecture interrogated rather than described: the true boundary (Linux has no
VM), egress as routing not content filtering, the hardening-flags question
(whether the launch policy is enforced in the build a reader gets, and whether
the tests for it can fail), secrets and the opt-in control channel, supply-chain
provenance limits, and where ephemerality stops being a control. Its audience
reads threat models for a living. The rules shared by every level are in
`site/level-common`.

## ADDED Requirements

### Requirement: The boundary correction stands
The page MUST keep its platform-by-platform correction front and center: Linux
provisions no VM; the enclave is a hypervisor boundary on macOS/Windows and a
namespace boundary on Linux where an escape lands as the invoking user's UID.

#### Scenario: Correction is retained
- **WHEN** the architecture boundary is described
- **THEN** the Linux-no-VM correction is present with its escape-blast-radius
  footnote

### Requirement: Hardening claims are stated per the pin
The hardening section MUST state, per the pinned tag: which flags the launch
envelope mandates; whether the launch-argv policy is enforced in release builds
or only in debug ones; whether the hardening litmus can fail; and what the
false-pass scanner gates. Each statement carries a footnote with a verbatim
quote, and any follow-up the PATH describes carries a footnote whose quote
verifies at the pin.

#### Scenario: Hardening state is sourced
- **WHEN** the hardening section is read
- **THEN** the enforcement question and the can-it-fail question each have an
  answer that is true at the pin, footnoted, and any follow-up a PATH describes
  is cited with a quote that verifies at the pin

### Requirement: Egress and proxy honesty
The page MUST keep the egress story exact as the pinned code has it: how egress
is enforced (network placement plus proxy environment variables, and whether any
packet filter exists); where TLS interception exists, exactly which hosts are
bumped and that everything else is spliced; whether the proxy inspects payloads;
and whether the certificate material the code emits matches what the proxy spec
promises, stated as the gap or its closure at the pin.

#### Scenario: Egress claims stay exact
- **WHEN** the proxy and egress are described
- **THEN** the bumped-host set, the payload-inspection statement, and the
  spec-versus-code certificate comparison are all present and sourced at the pin

### Requirement: RED precision and scope
Each RED/PATH claim MUST be accurate against the pinned code and scoped to what
the repository shows. Where the repository records a mitigation, the PATH says
what is recorded rather than that nothing is; a corpus count is the count at the
pin or is replaced by "the litmus corpus"; a claim about what happens outside
the repository (server-side branch protection) is scoped to what the repository
itself validates; and the provenance-research claim carries a footnote whose
quote verifies at the pin.

#### Scenario: A PATH describes the record
- **WHEN** a PATH says what the repository records about a gap
- **THEN** the statement matches what is recorded at the pin, including any
  mitigation, and is footnoted

#### Scenario: A count appears in prose
- **WHEN** the page gives a number of litmus files
- **THEN** it is the count at the pin, or the sentence says "the litmus corpus"

### Requirement: Assurance-claim boundary
The page MUST preserve the closing discipline: the convergence argument is not a
security argument; falsifiability and evidence-is-not-proof are the load-bearing
invariants; a passing suite is a bounded signal over defects someone wrote a
failing-capable litmus for.

#### Scenario: Assurance boundary preserved
- **WHEN** the assurance claim is stated
- **THEN** it declines to read a passing suite as a security argument or a
  probability
