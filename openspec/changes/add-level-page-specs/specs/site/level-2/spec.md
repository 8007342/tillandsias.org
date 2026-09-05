## Purpose

The "I barely understand my phone" page (`docs/matrix/level-2-phone.md`) answers
the practical questions a light user has before trusting software: is my stuff
private, does it cost money, does it need the internet, can it break my computer
— and, separately, what is currently broken today. It is the
privacy-and-assurance page, framed in straight answers. The rules shared by
every level are in `site/level-common`.

Its audience is nervous about technology, so its register is reassuring: it
answers the question that was asked, in its first clause, before explaining. But
the reassurance is not a tone applied to the page — it *is* the evidence, stated
plainly, and it stops exactly where the evidence stops. The failure this spec
exists to prevent is comfort bought on credit: a guarantee the source does not
give, a mechanism described as stronger or wider than it is, a cost left out
because naming it would worry the reader. Most of what follows is therefore
stated as sentence shapes the page must not use, each one a shape that has been
written on this page and rejected.

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

#### Scenario: The privacy claim is extended to AI assistants
- **WHEN** the page says the privacy claim survives the AI assistants because
  the models can run on the reader's own machine
- **THEN** that sentence carries its own footnote, because it is load-bearing
  for the page's central claim and is not implied by the no-server footnote

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

### Requirement: Required sections
The page MUST carry, in this order: its own title; a framing section that says
in one paragraph what the software is for, naming the choice it removes —
software the reader did not write, AI assistants among them, has to run
somewhere, and it runs against a folder the reader deliberately opened rather
than against the whole machine; a privacy section answering who could see the
reader's things; a section answering what it costs and whether it needs the
internet; a section answering what happens when it is turned off and whether it
can damage the machine, which MUST also name the ordinary, reversible cost the
reader does pay; a section that sharpens one claim the simpler level makes about
the project checking that nothing got worse, which MUST carry both what the
build gate actually refuses and the two honest limits required above; and a
closing section collecting what falls short today, which MUST be the last
section before the footnotes. The rendered footnote list MUST be present.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists, carries the purpose named for it, and
  the shortcomings section is last before the footnotes

#### Scenario: Nothing falls short at a pin
- **WHEN** no shortcoming holds against the code at the level's pin
- **THEN** the closing section stays and says so in one sentence, rather than
  being deleted

#### Scenario: A question is answered without its cost
- **WHEN** the page tells the reader that turning the software off is safe
- **THEN** the same section says what running it does cost — memory held while
  it runs and given back when it stops, and the disk the cached system image
  occupies — because a reassurance that omits the cost is the kind this page
  does not make

### Requirement: Optional sections and elements
The page MAY carry: at most one figure per section, each carrying that section's
single idea; GREEN callouts where a claim is worth separating from the prose; a
sentence noting that the reader has already paid for the only hardware involved;
a past-tense note inside the closing section about a shortcoming this page
previously carried that has since been fixed; and one closing sentence
summarising the shortcomings and saying which parts of the page they do and do
not touch. None of these is required, and dropping one MUST NOT be treated as a
regression; each, when present, MUST obey every wording and sourcing rule in
this spec.

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence

#### Scenario: The closing summary is present
- **WHEN** the closing section ends with a summarising sentence
- **THEN** it counts the same shortcomings the flags above it state, in the same
  tense, and any claim it makes about what they do not touch is one the page has
  already sourced

### Requirement: Forbidden sections
The page MUST NOT carry: install or quick-start commands, or any other page
furniture the build supplies (its tab title, its blurb, the plant aside) — those
live in the `LEVELS` table of `scripts/build-matrix.py` and MUST NOT be copied
into the level's source; a component roster or anatomy of what runs where; a
threat model, boundary analysis, egress inventory or attack surface; mathematics,
whether inline or display; tables, code blocks or numbered procedures; a
troubleshooting list keyed by error messages; release notes, a changelog or
version history; a comparison with other products or vendors; a section
addressed to developers or contributors; and any call to action, sign-up,
contact or donation block.

#### Scenario: Material belongs to a deeper level
- **WHEN** an editor wants to add anatomy, boundaries or formal argument
- **THEN** it goes to the level whose audience asks for it, and level 2 keeps
  only the answer a light user needs

#### Scenario: A section would restate page furniture
- **WHEN** a proposed section repeats the tab blurb, the install commands or the
  plant aside
- **THEN** it is rejected: the build supplies those, and duplicating them lets
  the two copies drift

### Requirement: Reassurance is bounded by the cited source
A reassuring sentence MUST claim only the outcome its cited range states, and no
consequence the reader would find more comforting. The page MUST NOT: attach to
a mechanism a security property its source does not give it — that material
which escaped is now useless, that anything is rotated, expired, invalidated or
made stale, where the cited requirement's stated purpose is something narrower;
soothe without a mechanism ("don't worry", "perfectly safe", "nothing can go
wrong"); or use "never", "always", "every" or "nothing" where the source names a
tendency, a single case, or one platform. Where the true answer is comforting,
the comfort MUST come from stating the mechanism, not from adding an adjective
to it.

#### Scenario: A mechanism is narrower than the comfort it suggests
- **WHEN** the cited requirement exists to stop one failure (a leftover name
  colliding with the next start, say) and a stronger security reading is
  available
- **THEN** the sentence claims the named failure only, and the stronger reading
  is not written unless a source states it

#### Scenario: A source hedges
- **WHEN** the cited range says something tends to happen, or names one incident
  or one platform
- **THEN** the page says the same and does not generalise it

### Requirement: Verbs match what the code does to the data
Words describing what happens to data MUST match the operation the pinned code
performs. The page MUST NOT say material is issued, reissued, replaced, rotated,
regenerated or made fresh where the code re-registers, reuses or preserves the
material it already had; and MUST NOT say something is cleared, wiped or removed
where the code preserves it. A verb chosen for reassurance rather than for
accuracy is a defect even when the sentence's stated consequence is true.

#### Scenario: Existing material is re-registered
- **WHEN** the code writes the bytes it already holds into a fresh registration
  at each start
- **THEN** the page says they are re-registered, not reissued or replaced, and
  the consequence it draws is the one the cited requirement names

### Requirement: A machine check is described by what it refuses
Where the page describes a gate, a check or a ratchet, the sentence MUST say
what that machine actually reads and what it refuses. It MUST NOT restate the
check as a broader measurement the machine does not compute — a scalar distance,
a coverage figure, a count of untraced or undocumented items — and MUST NOT
describe an objective the project has written down as though it were an enforced
per-release gate. A sentence MUST NOT contradict the label or the quote of the
footnote attached to it, because the reader sees both when hovering.

#### Scenario: An objective and a gate appear in one sentence
- **WHEN** the page reports both what the project aims at and what its build
  refuses
- **THEN** each is named as what it is, and the aim is not presented as the
  refusal

#### Scenario: Prose and tooltip disagree
- **WHEN** the visible sentence describes the check in different terms from the
  footnote label the reader sees on hover
- **THEN** the sentence is corrected to the footnote's terms, or the footnote is
  re-anchored to a source that states the sentence

### Requirement: A flag states the property, not a verdict on a document
A GREEN on this page MUST state the property that holds and say what holds it up
— that it follows from the design, or that a machine checks it — and MUST NOT
compress the two into one clause where the check does not cover the property. A
GREEN MUST NOT certify that code "backs", "matches" or "implements" a written
requirement when the code reaches that requirement's outcome by a different
mechanism from the one the requirement's words describe; such a line either
states the outcome plainly or is dropped. Flag text MUST NOT comment on its own
verdict ("this part works well", "this is still broken"), because the rendering
already labels it. Argument markers are used as `site/level-common` states; a
line that only reports what the software does MUST NOT carry one.

#### Scenario: Spec words and code mechanism differ
- **WHEN** the written requirement says a thing is removed and recreated and the
  code reaches the same outcome by one atomic replacement
- **THEN** the page states the outcome, and does not assert that the code backs
  the requirement's wording

#### Scenario: A GREEN would merge design and check
- **WHEN** one clause would assert both a design property and a machine's
  verification of it, and the machine checks only part
- **THEN** the two are named separately, each at its own strength

### Requirement: Practical instructions hold on every platform the page covers
Where the page tells the reader that an action removes something or reclaims
resources, that statement MUST be true of the pinned code on every platform the
page addresses, or the visible sentence MUST name the exception in the reader's
own words. Two actions MUST NOT be joined by "or" as though either achieves the
effect unless both do, and an action MUST NOT be named for an effect the pinned
code does not give it.

#### Scenario: One platform behaves differently
- **WHEN** the pinned code on one supported platform preserves what the sentence
  says is cleared
- **THEN** the sentence names that platform and what the reader must ask for
  instead, and is footnoted to the code that preserves it

#### Scenario: A remedy is listed that does not apply
- **WHEN** one of two named actions does not produce the stated effect at the pin
- **THEN** it is dropped from the sentence rather than carried by the other

### Requirement: A shortcoming is stated at its actual width
A RED and its PATH MUST name the narrow thing that is wrong or still open. A
pronoun or a bare noun MUST NOT widen an open item from one component to the
whole feature, and a historical defect MUST be described as the record describes
it rather than as the more familiar failure it resembles — a feature that
returned no sources is not one that invented them. Overstating a shortcoming is
a defect of the same kind as overstating a strength, and is corrected the same
way.

#### Scenario: One item remains open on a finished replacement
- **WHEN** the only open item concerns a narrow part of a replacement that has
  otherwise landed
- **THEN** the PATH names that narrow part, in words the reader could repeat, and
  does not leave "it" to mean the whole replacement

#### Scenario: A past defect is described
- **WHEN** the page describes what a feature used to do wrong
- **THEN** the description matches the recorded defect and the quote the reader
  sees on the accompanying footnote

### Requirement: The closing section is current at the pin
The closing section states what falls short today, judged against the code at
the level's pin. A defect that the pinned code has already replaced MUST be
written in the past tense, with the replacement stated and any remaining open
item named, so that a reader does not read a closed defect as a present one. Its
lifecycle across pin bumps is as `site/level-common` states.

#### Scenario: A defect was replaced before the pin
- **WHEN** a shortcoming the page carries has been replaced in the pinned build
- **THEN** the flag says it once did the wrong thing and has since been
  replaced, and what remains open is stated separately

### Requirement: The footnote target carries the claim
Each footnote MUST land on the range that states the claim its sentence makes,
not merely on a range that happens to contain a quotable string. A sentence
joining two claims MUST NOT be footnoted to a range carrying only one of them:
each half is cited, or the sentence is split. Where the sentence says something
happens at every start, on each run, or on every release, the cited range MUST
include the call site or the written requirement that makes it periodic, not
only the helper that performs the work. Where another level cites a source for
the same claim, this page MUST cite the same source, so the levels do not
disagree about where a fact lives.

#### Scenario: A reader clicks to check a claim
- **WHEN** a reader follows a footnote to verify the sentence it is attached to
- **THEN** they land on text that states that claim, not on a related passage
  that merely contains the quoted words

#### Scenario: Two clauses, one footnote
- **WHEN** a PATH line says both that a credential has not been supplied and
  that an enrolment is pending, and the cited range shows only the first
- **THEN** the second clause is given its own footnote, or the sentence is split

#### Scenario: The checked build passes but the target is wrong
- **WHEN** a quote verifies inside a range that does not carry the sentence's
  claim
- **THEN** the footnote is still wrong and is re-anchored, because the build
  checks the quote's presence and not the claim's location
