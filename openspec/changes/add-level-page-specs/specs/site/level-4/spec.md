## Purpose

The "I'm a Cyber Security expert" page (`docs/matrix/level-4-security.md`) is the
architecture interrogated rather than described: the true boundary (Linux has no
VM), egress as routing not content filtering, the hardening-flags question
(whether the launch policy is enforced in the build a reader gets, and whether
the tests for it can fail), secrets and the opt-in control channel, supply-chain
provenance limits, and where ephemerality stops being a control. Its audience
reads threat models for a living. The rules shared by every level are in
`site/level-common`.

Its register is adversarial and unflattering by design. Each layer makes its own
case — what the design promised, why the choice was defensible, what it cost,
what it bought — and then keeps every shortcoming that survives the case; the
page argues *for* the architecture and *against* it in the same breath, and a
reader who finds only one of those halves has been sold something. That reader
tests the page by clicking its footnotes, so the failure this spec exists to
prevent is a sentence that is broader in scope, more confident, or newer in
evidence than the range it cites. Most of what follows is therefore stated as
sentence shapes the page MUST NOT use, because each of them has been written on
this page and corrected.

## ADDED Requirements

### Requirement: Required sections
The page MUST carry, in this order: its own title; a boundary section that poses
the security question — when an agent does something unintended, how far does it
get — and answers it platform by platform, carrying the launch-hardening
envelope and the mandatory-access-control state of the containers; then one
section per defended surface, each of which MUST be present: egress and where
TLS is intercepted rather than passed through; secrets and the channel that
guards them; supply chain and provenance; where ephemerality stops being a
control; and blast radius, autonomy and auditability, which MUST say what an
agent reaches, what it does not, and what the audit trail's own provenance rests
on. The page MUST close with a section stating what the project's assurance
claim actually is, and that section MUST be the last before the footnotes. The
rendered footnote list MUST be present. The surface sections MAY be reordered
among themselves; the boundary section MUST be first.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists, carries the purpose named for it, the
  boundary section is first, and the assurance section is last before the
  footnotes

#### Scenario: A surface has nothing wrong in it at a pin
- **WHEN** no shortcoming holds against a defended surface at the level's pin
- **THEN** its section stays and states what the design gives and what it cost,
  rather than being dropped for having no RED

### Requirement: Optional sections and elements
The page MAY carry: one figure in the egress section showing the interception
decision; a NOTE aside that bounds a defect the page has just described, saying
how far it reaches and therefore how large the remedy is; sub-headings inside a
surface section; and the argument markers PROVEN, PLAUSIBLE and REFUTED as
`site/level-common` governs them. None of these is required, and dropping one
MUST NOT be treated as a regression; each, when present, MUST obey every wording
and sourcing rule in this spec.

#### Scenario: An aside bounds a defect
- **WHEN** a NOTE says a defect is contained rather than systemic
- **THEN** the bound is a statement a reader could re-run against the pinned
  source, and the aside says what remedy the bound implies

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence

### Requirement: Forbidden sections
The page MUST NOT carry: install or quick-start commands, or any other page
furniture the build supplies (its tab title, its blurb, the plant aside) — those
live in the `LEVELS` table of `scripts/build-matrix.py`; a component roster or
anatomy of what runs where, which belongs to the power-user level and MUST NOT
be duplicated here; the earlier levels' metaphors or reassurance framing;
mathematics, whether inline or display, and formal argument, which belong to the
deepest level; a hardening guide, remediation checklist or configuration recipe
telling the reader what to change on their own machine; a compliance-framework
mapping, a risk matrix, a severity ranking or an exploitability score that the
repository does not itself carry; a comparison with another product; release
notes, a changelog or a version history; and any disclosure block, contact block
or call to action. The page MUST NOT give a step-by-step exploitation procedure:
it names the reachable weakness, states its blast radius, and cites the
evidence, which is what its audience needs.

#### Scenario: Material belongs to another level
- **WHEN** an editor wants to add the component anatomy, the beginner framing or
  the formal argument
- **THEN** it goes to the level whose audience asks for it, and this page keeps
  only the boundary consequence its own reader needs

#### Scenario: A number would be invented for the page
- **WHEN** a section would rate a finding's severity or exploitability
- **THEN** the rating is rejected, and the page states reachability, precondition
  and blast radius in sourced prose instead

### Requirement: Each layer makes its own case
For each defended surface the page MUST state, before its flags, what the design
promises, why the choice is defensible on its own terms, what it costs, and what
that cost buys. It MUST NOT present a surface as a list of defects with no
account of the design, and it MUST NOT present a design with its costs omitted.
A cost MUST be named in the same breath as the property it purchased, and a
mitigation MUST be criticised without the criticism being softened.

#### Scenario: A layer is introduced
- **WHEN** a surface section opens
- **THEN** the reader is told the promise, the reason, the price and the
  purchase before the first flag

#### Scenario: A choice is criticised
- **WHEN** the page attacks a design choice
- **THEN** the sentence also says what the choice was buying, so the reader can
  weigh it, and the attack itself is not weakened to make room

### Requirement: The boundary is stated platform by platform
The page MUST state, platform by platform and at the level's pin, which boundary
the enclave actually is on each supported platform and where an escape lands,
correcting rather than inheriting any impression that every platform gets the
same boundary; the statement is footnoted at the pin.

#### Scenario: Correction is retained
- **WHEN** the architecture boundary is described
- **THEN** the boundary named for each supported platform is the one the pinned
  code provisions, and the escape's blast radius is stated and footnoted

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

### Requirement: A control is described with its default and its reach
Where the page describes a control — a hardening envelope, an authenticated
channel, a signature check, a wipe — it MUST say whether it is on in the build
the level pins, what it actually authenticates or refuses, and which components
or platforms it does not cover. It MUST NOT describe an opt-in control in the
plain present as though it were active; it MUST NOT call a default an invariant,
a guarantee or an immutable property; and it MUST NOT let an elegant mechanism
stand on its elegance without saying what it proves and whether it is switched
on.

#### Scenario: A control is off unless enabled
- **WHEN** a control is gated on a setting the shipped build leaves off
- **THEN** the visible sentence states the default posture, and any description
  of the mechanism is subordinate to it

#### Scenario: A control covers some call paths
- **WHEN** a check is reached by some launch or release paths and not others
- **THEN** the page names the paths it does not reach, or says plainly that the
  coverage is partial and what decides it

### Requirement: Claims are no stronger than their source
Every claim MUST carry a footnote resolving at the level's pin and MUST be no
stronger than the cited range. In particular the page MUST NOT: widen a
conditional rationale into a universal one, describing something bought for
hosts that enforce a particular policy as bought for every host; state a
property of some release lanes, platforms or code paths as a property of all of
them; write an absolute — "every", "always", "nothing", "never", "no one" —
that a search of the pinned source refutes, where naming the single instance and
saying why the conclusion survives is the stronger sentence; deny that a control
exists anywhere when the repository applies it to another component, instead of
scoping the denial to the component and naming the counter-example; say that
nothing is recorded about a gap when the repository records something adjacent,
instead of naming precisely which record is missing; or let the visible sentence
and its own footnote label state different scopes for the same claim.

#### Scenario: An absolute is proposed
- **WHEN** a sentence would say that nothing in the source does some thing
- **THEN** it is checked across the pinned tree, and if one instance exists the
  sentence names it and says why the posture still holds

#### Scenario: Prose and label disagree
- **WHEN** a footnote label scopes a claim more narrowly than the sentence it
  supports
- **THEN** the sentence is narrowed to the label's scope, because a reader sees
  both and reads the difference as a contradiction

### Requirement: Absence claims are bounded by the repository
An assertion that a control is missing MUST be bounded by what the checked-out
source can show. Where the control would live outside the repository — a hosting
platform's branch protection, a fleet's installed versions, an operator's own
configuration — the page MUST say that the repository evidences none rather than
that none exists, and MUST NOT present the absence of evidence as evidence of
absence. A claim about the state of machines rather than of code MUST be
attributed to the dated observation that recorded it and written in the past
tense.

#### Scenario: The control lives outside the repository
- **WHEN** the page wants to say a server-side or operator-side protection is
  absent
- **THEN** the sentence is scoped to what this repository evidences, and the
  conclusion it draws is scoped the same way

#### Scenario: A fleet state is reported
- **WHEN** the page reports what machines were found to be running or holding
- **THEN** it reports the observation, in the past tense, attributed to the
  record that made it, and does not generalise it to a current state

### Requirement: The pin is the tense the page speaks in
Running prose, GREEN lines and RED lines describe the release the level pins.
Evidence that exists only in a newer build MUST appear only on PATH lines, and a
footnote carrying an `@vTAG` suffix MUST NOT be reachable from running prose,
from a GREEN or from a RED; where such evidence is wanted, the clause moves to
the PATH rather than the footnote being retagged. A sentence naming a newer
channel MUST say so in its visible text and MUST NOT rely on a footnote label to
carry the qualification.

#### Scenario: A gap closes in a newer build
- **WHEN** something the page marks RED is remedied only in a build newer than
  the pin
- **THEN** the RED states what remains true at the pin, and the clause reporting
  the remedy sits in the PATH with the newer build's `@vTAG` footnote

#### Scenario: A newer-build footnote is cited from a flag
- **WHEN** a `@vTAG` footnote is referenced from a RED, a GREEN or ordinary prose
- **THEN** it is a defect: the reader of a stable-channel claim would be sent to
  a document that release never shipped, and the clause is moved to the PATH

### Requirement: The footnote target carries the claim
Each footnote MUST land on the range that states the claim its sentence makes,
in the direction the sentence asserts it. A range that presupposes the property
as a given, or that states its converse, MUST NOT be cited for a sentence
asserting it as a purchase, a cause or a consequence. A range carrying the
object of a claim — a list of flags, a command line — MUST NOT be cited for a
sentence about what a checker does with that object. A sentence joining two
claims MUST carry a citation for each, or be split. A paragraph of running prose
that makes a factual claim about the project's own record MUST carry a footnote:
being prose rather than a flag is not an exemption, and the paragraphs a
security reader is most likely to test are the ones about the project's
integrity.

#### Scenario: A reader clicks through to test causality
- **WHEN** the sentence says a choice was made in order to achieve something
- **THEN** the cited range states that rationale, not merely the relationship in
  the opposite direction

#### Scenario: A paragraph makes a quotable claim without a flag
- **WHEN** ordinary prose asserts something about the project's own audit trail,
  incidents or process
- **THEN** it carries a footnote whose quote verifies at the pin, exactly as a
  flag would

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

### Requirement: Rejected arguments stay on the page
Where an argument about this page's own subject has been tried and has failed,
the page MUST keep it as a REFUTED line, stated in the words someone would use
to propose it, so that a later reader does not re-propose it and the page does
not oscillate between verdicts. Where an argument is asserted but not
demonstrated — that the layers compose to bound an escape, for instance — it
MUST be marked at its actual strength and MUST NOT be written as a bound.

#### Scenario: An argument is refuted
- **WHEN** a plausible-sounding argument for a control is shown not to hold at
  the pin
- **THEN** the page keeps it as a REFUTED line naming the argument and the reason
  it fails, rather than deleting the subject

#### Scenario: Defence in depth is invoked
- **WHEN** the page relies on layers compensating for a missing boundary
- **THEN** the composition is marked as undemonstrated, and the page does not
  claim the layers bound an escape

### Requirement: An audit's rewrite is evidence, not an instruction
Audits of this page are run against a build newer than the level's pin, so a
suggested rewrite can state as present fact something true only of that newer
build, and can carry line numbers, counts and targets that have drifted. An
editor MUST re-derive every suggestion against the pinned source before adopting
it. A RED MUST NOT be promoted to a GREEN, and a flag MUST NOT be dropped, on
evidence that exists only in a newer build.

#### Scenario: An audit proposes turning a RED green
- **WHEN** an audit reports that the defect behind a RED is fixed
- **THEN** the editor checks the pinned source, and if the fix is not there the
  RED stays and the PATH names the channel the fix landed in

#### Scenario: An audit supplies a target
- **WHEN** an audit's finding carries a path, a line range or a count
- **THEN** it is re-resolved at the level's pin before it enters the page,
  because ranges shift between releases

### Requirement: Assurance-claim boundary
The page MUST preserve the closing discipline: the convergence argument is not a
security argument; falsifiability and evidence-is-not-proof are the load-bearing
invariants; a passing suite is a bounded signal over defects someone wrote a
failing-capable litmus for.

#### Scenario: Assurance boundary preserved
- **WHEN** the assurance claim is stated
- **THEN** it declines to read a passing suite as a security argument or a
  probability
