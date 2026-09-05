## Purpose

The "I'm a power user" page (`docs/matrix/level-3-power.md`) is the anatomy: what
runs where, what survives a teardown, and where the sharp edges are. Its audience
understands containers, networking and CI, and expects the architecture plus its
honest failure list. The rules shared by every level are in `site/level-common`.

Its register is the one thing this page advertises: what a forge hands a reader
with **zero configuration**, subsystem by subsystem, and exactly where each of
those subsystems stops short at the pinned release. The reader is assumed to
know what a container, a proxy, a bare repository and a CI gate are, so the page
names mechanisms rather than explaining them. It is not the trust page: the
threat model, the per-platform boundary and the assurance argument belong to
level 4, and the mathematics to level 5. The failure this spec exists to prevent
is a promise that reads bigger than its source — a spec invariant reported as
shipped behaviour, a partial list offered as a roster, a footnote that resolves
but does not carry the claim, a defect written in the past tense because someone
patched a running system. Most of what follows is therefore stated as sentence
shapes the page must not use, each one a shape that has been written on this
page and rejected.

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
a plan entry the code has outrun; the lifecycle at a pin bump is as
`site/level-common` states it. A RED that holds only for a subset of hosts
(those not re-initialised, one platform) MUST say so.

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

### Requirement: Required sections
The page MUST carry, in this order: its own title; an opening section stating
what a launch hands the reader with no configuration, which MUST carry the one
launch command, the zero-configuration statement attributed to the context file
the agent reads first, and the channel contract required below; one subsection
per subsystem that a launch brings up unconfigured, each saying what the reader
gets and what falls short at the pin; an anatomy section naming what runs where,
the single-egress rule, how the enclave's membership is recorded, and how a
reader starts one; a mounts-and-boundary section saying what is addressable from
inside a forge and what is not, that agent tooling exists only inside the image,
whether the working tree is touched by default, and the push-or-lose rule; a
survivorship section stating what crosses a stop, a `podman system reset` and a
`--reset-guest`; and a workflow section placing the verification gate on the
reader's own machine. The rendered footnote list MUST be present and MUST be
last.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists in the stated order, carries the purpose
  named for it, and the footnote list is last

#### Scenario: A subsystem is added or removed upstream
- **WHEN** the runtime gains a subsystem a launch brings up with no
  configuration, or drops one
- **THEN** the opening section gains or loses that subsection, and losing one
  whose subsystem no longer ships is not a regression

#### Scenario: A subsystem has nothing wrong with it at the pin
- **WHEN** no shortcoming holds for a subsystem against the code at the pin
- **THEN** its subsection stays and says what it gives, rather than being
  deleted for having no RED

### Requirement: Optional sections and elements
The page MAY carry: figures, at most one per section, each carrying that
section's single idea; a GREEN in a subsystem subsection where the
zero-configuration result is worth separating from the prose; a sentence naming
the per-platform way a reader starts the software; and a past-tense sentence
recording that something this page previously flagged has since been fixed.
None of these is required, and dropping one MUST NOT be treated as a regression;
each, when present, MUST obey every wording and sourcing rule in this spec.

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence

#### Scenario: A fixed shortcoming is recorded
- **WHEN** the page keeps a past-tense sentence about something now fixed
- **THEN** it says what was wrong, that it was fixed, and what remains, and any
  flag beside it claims only the remainder

### Requirement: Forbidden sections and constructs
The page MUST NOT carry: a threat model, adversary analysis, attack-surface
inventory, per-platform boundary analysis or assurance argument — those are
level 4's subject and this page MUST NOT re-argue them; mathematics, whether
inline or display, and any formal or convergence argument — that is level 5's;
a lay explanation of what a container, a proxy or a repository is, or the
metaphors the simpler levels use; install or quick-start command blocks and any
other page furniture the build supplies (its tab title, its blurb, the plant
aside), which live in the `LEVELS` table of `scripts/build-matrix.py` and MUST
NOT be copied into the level's source; release notes, a changelog or version
history; a roadmap or a promise about a future release beyond what a PATH line
records; a comparison with other products or vendors; benchmark numbers; and any
call to action, sign-up, contact or donation block. It MUST NOT use any
construct outside the dialect in `docs/matrix/README.md` — in particular no
tables and no fenced code blocks — and MUST NOT use the PROVEN, PLAUSIBLE or
REFUTED markers, which belong to the levels that argue rather than report.
Internal identifiers — order or packet identifiers, ledger ids, slugs — MUST NOT
appear in the prose; they MAY appear in a footnote label or target, and inside a
verbatim quote.

#### Scenario: Material belongs to a neighbouring level
- **WHEN** an editor wants to add a threat model, a boundary analysis or a
  formal argument
- **THEN** it goes to level 4 or level 5, and level 3 keeps only the mechanism
  and the sentence naming its limit

#### Scenario: A section would restate page furniture
- **WHEN** a proposed section repeats the tab blurb, the install commands or the
  plant aside
- **THEN** it is rejected: the build supplies those, and duplicating them lets
  the two copies drift

#### Scenario: An identifier is the shortest way to say it
- **WHEN** naming a work item or a defect would be easiest with its identifier
- **THEN** the prose states the substance in a sentence a reader could repeat,
  and the identifier stays in the footnote label or target

### Requirement: The zero-configuration promise is scoped subsystem by subsystem
Each subsystem subsection MUST state what the reader gets without configuring
anything, and, in the same sentence, any condition that result depends on — a
prior host-side step, a platform, an environment variable, a vendor stack. A
"works out of the box" statement MUST NOT be made unconditionally where the
pinned code makes it conditional, and MUST NOT be repaired by a qualification
placed in a different flag or a later paragraph. The page's global
zero-configuration claim MUST be attributed to the artifact that makes it — the
startup context file the agent reads — and MUST NOT be restated by the page in
its own voice as a promise wider than that artifact's.

#### Scenario: A subsystem works only under a condition
- **WHEN** a subsystem needs a host-side step, a display, a vendor driver or a
  flag before it works
- **THEN** the condition is named in the sentence that makes the claim, not
  deferred to the section's RED

#### Scenario: The context file is quoted for the promise
- **WHEN** the page says nothing needs configuring
- **THEN** the claim is attributed to the context file that says so and
  footnoted at the pin, and the page does not extend it to subsystems that file
  does not cover

### Requirement: Mechanism, not threat model — but the limit is named once
The page describes mechanisms and their limits; it MUST NOT argue about trust,
adversaries or residual risk. Where a mechanism's guarantee stops, the
subsection that describes that mechanism MUST say so plainly, in one sentence,
and MUST NOT leave the limit to be supplied by another level. The page MUST NOT
present placement or configuration as a stronger kind of control than it is: an
internal network is not client authentication, a read-only mount is not an
access-control decision, and an allowlist is not inspection. A sentence naming
such a limit MUST state the limit and stop, without reasoning about what an
attacker could do with it.

#### Scenario: A write path inside the enclave is unauthenticated
- **WHEN** the page describes a service any enclave peer can write to
- **THEN** the same subsection says that placement on an internal network is not
  client authentication, footnoted at the pin, and does not develop the point
  into a threat model

#### Scenario: An editor wants to weigh a risk
- **WHEN** a sentence would compare two risks or estimate a likelihood
- **THEN** it is cut from this page and left to level 4

### Requirement: A spec's wording and the shipped code are distinguished
Where a spec requires one thing and the pinned code does another, the page MUST
say which it is describing. A spec invariant MUST NOT be written in the
indicative as observed behaviour ("the share only ever lands on tmpfs") when the
shipped code has a fallback, a wider set or a different order; the sentence
either states what the code does, or names the requirement as a requirement and
then says what ships. A spec's shorthand for an ordering or a fallback chain
MUST NOT be reproduced as the behaviour when the code's order or extent differs;
where the page does not want the full list, it says so loosely rather than
giving a wrong order.

#### Scenario: The code has a fallback the invariant does not cover
- **WHEN** an artifact the page names is also written to a fallback location by
  the shipped code
- **THEN** the sentence says so, and any invariant it quotes is attributed to
  the spec that requires it

#### Scenario: A fallback chain is described
- **WHEN** the page gives the order in which the code tries something
- **THEN** the order is the code's order at the pin, or the sentence describes
  it loosely — a default with fallbacks — without asserting a sequence

### Requirement: Enumerations, counts and orderings are complete or marked
Any list the page gives — members, mounts, RAM-backed roots, wipe sets,
allowlisted hosts, code paths that destroy an artifact — MUST be complete
against the pinned code, or MUST be marked as partial in the sentence itself
("among the members", "for example"). A partial list MUST NOT be presented as
the roster. Any count in prose MUST be the count at the pin, MUST be recomputed
whenever the level's pin moves, and MUST NOT be carried forward from the repo's
own prose, which may itself be stale. Where a magnitude the repository records
is marked unverified or has been contradicted by a later measurement, the page
MUST NOT state it as fact.

#### Scenario: The full list is long
- **WHEN** the complete list would crowd the sentence
- **THEN** the page names the members that matter to the story and marks the
  list partial, rather than trimming silently

#### Scenario: A recorded figure is unverified
- **WHEN** the repository's own record calls a figure unverified in magnitude,
  or a later measurement disagrees with it
- **THEN** the page does not assert the figure, and if the cost matters it says
  that the magnitude is unverified

### Requirement: The footnote target carries the claim
Each footnote MUST land on the range that states the claim its sentence makes,
not merely on a range that happens to contain a quotable string. A sentence
naming several things — several ecosystems, several behaviours, a count and an
example — MUST NOT be footnoted to a range carrying only one of them: the range
is widened to cover them all, a second footnote is added, or the sentence is
split. Where the page names a count or an example drawn from a list, the cited
range MUST contain that list, not a comment describing it. Where the page says a
test pins something, the footnote MUST target the test. A footnote's label MUST
NOT promise more than its range carries.

#### Scenario: A reader clicks to check the claim
- **WHEN** a reader follows a footnote to verify the sentence it is attached to
- **THEN** they land on text that states that claim, not on a related passage
  that merely contains the quoted words

#### Scenario: The checked build passes but the target is wrong
- **WHEN** a quote verifies inside a range that does not carry the sentence's
  claim
- **THEN** the footnote is still wrong and is re-anchored, because the build
  checks the quote's presence and never the claim's location

#### Scenario: A range drifts under a re-pin
- **WHEN** a level's pin moves and inserted lines push the sentence the label
  promises outside the cited range
- **THEN** the range is widened or moved so that it still carries the claim,
  even though the quote alone would still verify

### Requirement: A verified claim names what holds it up
A GREEN MUST say, for each thing it asserts, whether it holds by design, by
configuration, or because a machine checks it, and MUST NOT compress a design
property and a machine check into one clause where the check does not cover the
property. Where a GREEN says a test pins something, what it says the test pins
MUST be what the test asserts — not a stronger property, such as a cardinality
or an exclusivity, that the code happens to satisfy but nothing verifies. Where
a guard runs only under a condition (a flag, a mode, a build profile), a claim
that it runs MUST be true of that condition as the page states it.

#### Scenario: A guard checks less than the sentence implies
- **WHEN** the machine cited checks one aspect and the paragraph describes two
- **THEN** the GREEN is narrowed to the aspect the machine checks, plus whatever
  the design gives, each named separately

#### Scenario: A cardinality is asserted
- **WHEN** the page says exactly one of something is mounted, created or set
- **THEN** either a cited check asserts that cardinality, or the sentence says
  only what is asserted and drops the count

### Requirement: The page speaks in the present about its pin
The page MUST open by stating its channel contract: every claim is at the stable
release the level pins, and where the daily channel has moved on, the PATH line
says so. A fact established only in a build newer than the pin MUST NOT appear
in the body of a GREEN or a RED, nor anywhere else the page speaks in the
present; it belongs in a PATH line, whose visible sentence names the daily
channel and the date the change landed, and whose footnote carries that build's
`@vTAG` suffix as `site/level-common` requires. The date MUST be in the visible
sentence, not only in a footnote label, and every daily-channel sentence on the
page MUST use the same shape.

#### Scenario: A daily-only fact is offered for a RED
- **WHEN** a measurement, a fix or a record exists only in a build newer than
  the pin
- **THEN** it is moved to the PATH line, and the RED states only what is true of
  the pinned release

#### Scenario: A daily-channel landing is reported
- **WHEN** a PATH says something landed in the daily channel
- **THEN** the sentence gives the date, and its footnote carries the daily's tag

### Requirement: Every item of a RED is answered by a PATH
A RED that states several shortcomings MUST be answered item by item: each item
either gets its remedy, or is named in a scoped no-path clause. No item may be
silently dropped because another item in the same RED has a recorded remedy.
Where the repository records no remedy for an item, the PATH MUST use the
sentence `No path to green is recorded in the repo.` verbatim, optionally with a
scoping prefix or suffix naming which item it answers; paraphrases of it are
forbidden. That sentence MUST NOT be written without looking: where the
repository does record a remedy, however partial, the PATH says what is
recorded.

#### Scenario: A RED carries three shortcomings
- **WHEN** a RED names three shortcomings and only one has a recorded remedy
- **THEN** the PATH gives that remedy and names the other two in a scoped
  no-path clause

#### Scenario: A remedy exists after all
- **WHEN** the repository records a work item that would close the gap
- **THEN** the PATH describes it and footnotes it, instead of claiming that
  nothing is recorded

### Requirement: A mitigation outside the shipped artifact is not a fix
A defect present in the artifact the pinned release produces MUST be stated in
the present tense. A mitigation applied by hand to a running instance, held in
an operator's configuration, or existing only as a recorded intention MUST NOT
be reported as a fix, and MUST NOT move the sentence into the past tense; where
the page mentions such a mitigation, it MUST name its scope — that it was
applied to a running system and that the artifact the code generates still lacks
it.

#### Scenario: A running system was patched
- **WHEN** an operator closed an exposure on a live instance while the generator
  at the pin still emits the exposed configuration
- **THEN** the page states the defect in the present tense and says the
  mitigation was applied by hand to a running system

#### Scenario: A fix landed in the artifact
- **WHEN** the pinned code itself no longer produces the defect
- **THEN** the flag is rewritten per the RED lifecycle in `site/level-common`
