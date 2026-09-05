## Purpose

The "Like I'm 5" page (`docs/matrix/level-1-five.md`) is the simplest rendering of
the Tillandsias platform that is still true. Its audience is a non-technical
reader who needs the three core ideas — a private "doll house" compute space, a
single guarded door to the internet, and throw-away-and-rebuild repair — plus the
project's honesty discipline (written-down promises, machine-checked where
possible, known broken things stated out loud). The rules shared by every level
are in `site/level-common`.

Its register is warm and concrete: a child could follow it, and so could an adult
who wants the friendly version first. It is the site's front door and reads like
one, but it is not marketing copy — every sentence on it is a claim footnoted
into the runtime source at the level's pin, and the page is held to that at
exactly the strength its sources carry. Simplifying is allowed; overclaiming
while simplifying is the failure this spec exists to prevent, so most of what
follows is stated as sentence shapes the page must not use.

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

#### Scenario: The machine checks a different list
- **WHEN** the word list a machine enforces is not the same list as the written
  promise the page has just shown
- **THEN** the sentence says what the machine actually reads, or names the
  second written promise the machine enforces, and MUST NOT present the check as
  proof of the promise the reader was shown

### Requirement: Honest flags and RED/PATH pairing
The page MUST use the level's honesty frame in words its reader can repeat. The
RED/PATH pairing and the RED lifecycle are as `site/level-common` states them;
in addition, a PATH MUST NOT say that nothing has been done when the repository
records that something has.

#### Scenario: A RED is checked against the pin
- **WHEN** a claim is marked RED
- **THEN** it is true of the source at the pinned release tag, and the next line
  is its PATH

#### Scenario: A PATH describes the remedy's state
- **WHEN** a PATH says whether the remedy has been carried out
- **THEN** that statement matches the pinned code and the closed or open state
  of the recorded work, and is footnoted

### Requirement: Required sections
The page MUST carry, in this order: its own title; a framing section that says
what the thing is with the metaphor the rest of the page reuses; a section on
the single way out and who may use it; a section on disposability — broken
pieces are replaced rather than repaired — which MUST also say what of the
reader's own is never swept away; a section on how the project works and
improves, which MUST carry both the discipline (promises written down first,
then machine-pressed, with a check that nothing already working got worse) and
its honest limit (getting less broken is not the same as ending up perfect); and
a closing section that collects what is still broken, which MUST be the last
section before the footnotes. The rendered footnote list MUST be present.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists, carries the purpose named for it, and
  the shortcomings section is last before the footnotes

#### Scenario: Nothing is broken at a pin
- **WHEN** no shortcoming holds against the code at the level's pin
- **THEN** the closing section stays and says so in one sentence, rather than
  being deleted

### Requirement: Optional sections and elements
The page MAY carry: one figure in the disposability section; a one-sentence
statement of the licence freedoms; a sentence placing automated helpers inside
the enclosure; and, inside the closing section, a past-tense note about a
shortcoming this page previously carried that has since been fixed. None of these
is required, and dropping one MUST NOT be treated as a regression; each, when
present, MUST obey every wording and sourcing rule in this spec.

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence

#### Scenario: A fixed shortcoming is celebrated
- **WHEN** the closing section carries a past-tense note
- **THEN** the note says what was wrong, that it was fixed, and what the fix was,
  and any RED that follows it says only what remains

### Requirement: Forbidden sections
The page MUST NOT carry: install or quick-start commands, or any other page
furniture the build supplies (its tab title, its blurb, the plant aside) — those
live in the `LEVELS` table of `scripts/build-matrix.py` and MUST NOT be copied
into the level's source; a component roster or anatomy of what runs where; a
threat model, boundary analysis or attack surface; mathematics, whether inline or
display; tables, code blocks or numbered procedures; release notes, a changelog
or version history; a comparison with other products; a glossary of the machine
words the page has promised the reader will never see; and any call to action,
sign-up or contact block.

#### Scenario: Material belongs to a deeper level
- **WHEN** an editor wants to add anatomy, boundaries or formal argument
- **THEN** it goes to the level whose audience asks for it, and level 1 keeps
  only the sentence a non-technical reader needs

#### Scenario: A section would restate page furniture
- **WHEN** a proposed section repeats the tab blurb, the install commands or the
  plant aside
- **THEN** it is rejected: the build supplies those, and duplicating them lets
  the two copies drift

### Requirement: Register, metaphor and vocabulary
The page MUST hold one metaphor family across its whole length and map each
object in it to exactly one real thing, so a reader can carry the mapping from
section to section. It MUST NOT introduce a second metaphor for an object that
already has one. Its own prose MUST NOT use machine vocabulary; the machine words
MAY appear only inside a user-visible string the page is quoting in order to
report it as a defect, where the quotation is the evidence. The prose MUST NOT
contain internal identifiers, file paths, crate or function names, spec names,
command lines or release tags: every sentence MUST be one the reader could repeat
out loud, with the identifiers living in the footnote label and target.

#### Scenario: Two metaphors for one object
- **WHEN** a fix and a remaining shortcoming both describe the same object
- **THEN** they MUST NOT be distinguished only by two metaphors on the same axis
  — one place versus another place — because the reader reads that as
  self-contradiction; either they name different aspects in plainly different
  words, or the page reports only one aspect

#### Scenario: A machine word is the subject of the claim
- **WHEN** the page reports that a screen shows a word the project promised never
  to show
- **THEN** it MAY quote that text verbatim, and MUST NOT otherwise adopt the
  vocabulary

### Requirement: Claims are no stronger than their source
Every claim MUST carry a footnote resolving at the level's pin, and MUST be no
stronger than the cited range. In particular the page MUST NOT: turn a source's
hedge into a universal, using "every", "always" or "never" where the source says
that something tends to happen or names a single incident; add a property the
source does not claim, such as an identical, deterministic or instant result,
because it makes the sentence tidier; describe a rule as the opposite kind of
rule — a prohibition rendered as a curated vocabulary or an allow-list, or the
reverse — instead of saying what the rule does; state a reassurance more strongly
than the code enforces, rather than naming what is protected and leaving what is
not protected unclaimed; or use promotional superlatives, or comparisons with an
unnamed alternative, in place of a checkable statement.

#### Scenario: The source hedges
- **WHEN** the cited range says a failure tends to follow, or records one dated
  incident
- **THEN** the page says the same, and does not generalise it to all cases

#### Scenario: Simplification would add a property
- **WHEN** simplifying a source sentence would make the page assert something the
  range does not carry
- **THEN** the simpler wording is rejected in favour of one the range supports

#### Scenario: A sentence would reassure beyond the code
- **WHEN** the page tells the reader that some kind of breakage cannot hurt them
- **THEN** the sentence is bounded by what the pinned code actually enforces, and
  the boundary is footnoted

### Requirement: A verified claim names what holds it up
A GREEN on this page MUST say, for each thing it asserts, whether it holds by
design or because a machine checks it, and MUST NOT compress a design property
and a machine check into one clause where the check does not cover the property.
A flag's text MUST state the property; it MUST NOT comment on its own verdict
("this part works great", "this part is still broken"), because the rendering
already labels the flag.

#### Scenario: A guard checks less than the sentence implies
- **WHEN** the machine cited checks one aspect and the paragraph describes two
- **THEN** the GREEN is narrowed to the aspect the machine checks, plus whatever
  the design gives, each named separately

#### Scenario: Flag text is written
- **WHEN** a GREEN or RED is written
- **THEN** it reads as a statement about the thing, with no preamble about how
  good or bad the news is

### Requirement: The pin is the tense the page speaks in
The page speaks in the present about the release it pins — the build a reader who
copies the install commands receives. A statement whose evidence exists only in a
build newer than the pin MUST name that channel in the visible sentence, in the
reader's own words, and MUST NOT rely on a footnote label to carry the
qualification; such a statement MUST NOT be written flatly in the present tense
as though it were true of the pinned release. The page MUST NOT use a phrase that
reads as a contrast between releases where it means that something has not yet
changed.

#### Scenario: A change exists only in a newer build
- **WHEN** the page reports something established only in a build newer than its
  pin
- **THEN** the visible sentence says so — that it happened in the newer builds —
  and its footnote carries that build's tag

#### Scenario: A shortcoming persists
- **WHEN** the page says a shortcoming has not been resolved
- **THEN** it says "still", and does not imply a difference between releases that
  does not exist

### Requirement: The footnote target carries the claim
Each footnote MUST land on the range that states the claim its sentence makes,
not merely on a range that happens to contain a quotable string. Where the page
calls a source a rule or a written promise, the target MUST be the unconditional
statement of it, not a branch of a scenario, a heading listing proposed remedies,
or a document's title block. A sentence that joins two claims MUST NOT be
footnoted to a range that carries only one of them; each half is cited, or the
sentence is split. Where another level cites a source for the same claim, this
page MUST cite the same source, so the levels do not disagree about where a fact
lives.

#### Scenario: A reader clicks to check a claim
- **WHEN** a reader follows a footnote to verify the sentence it is attached to
- **THEN** they land on text that states that claim, not on a related passage
  that merely contains the quoted words

#### Scenario: The checked build passes but the target is wrong
- **WHEN** a quote verifies inside a range that does not carry the sentence's
  claim
- **THEN** the footnote is still wrong and is re-anchored, because the build
  checks the quote's presence and not the claim's location

### Requirement: Borrowed arguments keep the project's own strength
Where the page passes on an argument the project makes about its own way of
working, it MUST report that argument at the strength the project currently gives
it. When the project has qualified or withdrawn its own proof, the page MUST say
that the idea stands and the proof is owed, rather than repeating the withdrawn
claim or silently dropping the subject.

#### Scenario: The project withdraws a proof
- **WHEN** the project retracts the formal justification for a practice it keeps
- **THEN** the page keeps the practice, marks the argument at its actual
  strength, and says what is now owed

### Requirement: Enumerated violations are complete or labelled
Where the page lists the instances of a violation — the words a screen shows that
it promised not to show, for example — the list MUST be complete against the
code at the pin, or the sentence MUST say that it is showing examples.

#### Scenario: A violation has more instances than the page names
- **WHEN** the pinned code produces further instances of the same violation
- **THEN** the page names them all, or says it is naming some
