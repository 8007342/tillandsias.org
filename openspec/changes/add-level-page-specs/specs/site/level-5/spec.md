## Purpose

The "I'm a MathWiz / Hacker" page (`docs/matrix/level-5-phd.md`) is the formal
content: obligation-state lattices, fixed points, the finite-iteration theorem,
the strong-law / monotone-convergence floor, and the CRDT material — stated as
claims with hypotheses, sorted into standard theorems invoked, what the
repository asserts, what follows, and what does not. It is edited in this
repository, by this repository's operator, under the delta discipline
`docs/matrix/README.md` states: tiny, individually justified changes, each
proposed before it lands. The rules shared by every level are in
`site/level-common`.

Because the page moves only in deltas, its history — not its latest revision —
is the thing an editor needs and the thing an editor cannot see. This spec is
therefore written to be sufficient on its own: it enumerates the sections the
page carries and what each is for, and it records as MUST NOT rules the shapes
of sentence that have been written on this page, found wrong, and corrected. An
editor or a reviewing agent that has never read the page's history should be
able to work from this document alone, and should not re-propose a wording the
page has already rejected.

## ADDED Requirements

### Requirement: Own pin, which may lag
Level 5 MUST pin its own tag in the `LEVELS` table of `scripts/build-matrix.py`.
Its pin MAY lag the other levels' pins, and the lag MUST be visible: the page
header shows the newest pin across levels, the level's own row shows its tag,
and the current audit record names the lag. A pin bump for level 5 is itself an
OpenSpec change.

#### Scenario: Other levels move first
- **WHEN** levels 1 to 4 are moved to a new stable tag and level 5 is not
- **THEN** level 5's footnotes still resolve at its own tag, the header shows the
  newer pin, and the audit record names level 5 as lagging and why

### Requirement: Delta discipline
Every change to the page's text and every bump of its pin MUST land through an
OpenSpec change under `openspec/changes/` that lists one delta per requirement,
flag or footnote it touches, each with `path#Lstart-Lend` evidence and a
verbatim quote at the target tag. An editor MAY apply the deltas it lists, and
MUST apply no others: the record and the diff are checked against each other,
and the operator reviews the change before it is archived. A structural rewrite
is out of scope for a delta and needs its own change with a `design.md`.

#### Scenario: Pin bump proposed
- **WHEN** a pin bump for level 5 is proposed
- **THEN** the change lists one delta per footnote whose target or quote drifted
  between the tags, each with evidence at the target tag, and the change is not
  archived until the operator has reviewed it

#### Scenario: The diff exceeds the record
- **WHEN** the page's diff contains a hunk that no delta in the change lists
- **THEN** that hunk is a defect: it is reverted, or the change is amended to
  list it with its evidence before the change is archived

#### Scenario: Agent proposes a rewrite
- **WHEN** an agent proposes reorganising or rewriting the page rather than a
  set of deltas
- **THEN** the proposal is refused as exceeding delta scope

### Requirement: The page's sections, and what each is for
The page MUST carry the following sections, in this order. The first two precede
the first heading; the rest each sit under their own `##` heading.

1. **The opening frame** — what the page contains and what it excludes: the
   formal content, stated as claims with hypotheses and sorted into the four
   bins; and the boundary with the security level, whose findings are not
   repeated here and enter only where a mathematical hypothesis depends on one.
2. **The short verdict** — the conclusion before the argument, in a few
   sentences: how large the theory is, how candid it is about what it declines
   to claim, and which of its load-bearing hypotheses are assumed rather than
   discharged.
3. **The order-theoretic object** — the obligation, its state chain, the product
   order, the completeness-and-height proposition with its proof sketch, the
   convention any quoted bound depends on, the limit the repository itself puts
   on the result, and the hypotheses the order quietly needs.
4. **The fixed point** — the refinement operator; the existence theorem invoked;
   the finite-iteration theorem that supplies termination, stated with its
   hypotheses and the step most treatments skip; the continuity question and why
   it is or is not free here; the governance hypothesis that keeps the operator
   fixed within a release; and the gap between the property the repository
   asserts of the operator and the properties the theorem needs.
5. **The moving target** — the release-boundary inequality; the convergence
   result that does follow; the zero-floor corollary that does not, and the
   repository's own refusal of it; the extra hypothesis that would force it; the
   itemised debt a contraction claim would owe, with the binding item named; and
   whether the compared quantity is comparable across the boundary.
6. **Iteration** — the law-of-large-numbers family the doctrine invokes, which
   member the situation actually needs, the bias-versus-variance distinction and
   which of the two defeats iteration, the hypothesis the architecture violates
   by design, and the substitutes that would repair the invocation.
7. **What is renounced** — each structure the repository declines to claim, the
   object a future claim would have to construct, and what the renunciation
   costs in conclusions no longer available.
8. **The replicated-state algebra** — the carriers, the join and the order it
   induces, exactly what convergence buys and what it does not, and where the
   design deliberately steps outside the algebra and why.
9. **Verdict** — what the formal core is, and what stops it being finished
   mathematics.
10. **Footnotes** — every footnote definition, in one list at the foot of the
    page.

A claim MUST sit in the section whose object it is about, and a section's
subject MUST NOT be split across the page. A heading MAY be reworded. Merging,
reordering, dropping or adding a `##` section is a structural change, not a
delta, and needs its own change with a `design.md`.

#### Scenario: A new claim is proposed
- **WHEN** a delta proposes a claim the page does not yet make
- **THEN** it is placed in the section whose object it concerns, or the proposal
  is refused as a structural change needing its own `design.md`

#### Scenario: The opening frame is edited
- **WHEN** the opening frame is revised
- **THEN** it still states the sorting into the four bins and still states that
  the security level's findings are not repeated except where a mathematical
  hypothesis depends on one

### Requirement: What the page MUST NOT carry
The page MUST NOT carry:

- an introduction to the product, install or usage instructions, or any
  restatement of what the software does for a user — the object and its defects
  belong to the lower levels, and this page begins where they end;
- the security level's findings, except the hypothesis of one where a
  mathematical claim depends on it;
- a version history, a changelog, or a "what changed since the last release"
  section: the page's change trail lives in its OpenSpec changes and its audit
  annotation, and what a newer build established appears only on a PATH line;
- a roadmap, a schedule, or a promise of future work outside a PATH line;
- a bibliography or further-reading section separate from the footnotes;
- a score, dashboard figure or percentage offered as a measurement of quality
  rather than as an object under examination;
- an executive summary, a "key takeaways" list, or any second restatement of the
  argument pitched at a different audience.

#### Scenario: An agent proposes an onboarding paragraph
- **WHEN** a proposal adds a paragraph explaining what the software is, or how
  to install or run it
- **THEN** the proposal is refused: that material belongs to the lower levels

#### Scenario: A newer build's fix is proposed as prose
- **WHEN** a proposal adds a section or paragraph narrating what a build newer
  than the pin fixed
- **THEN** the proposal is refused, and the fact is proposed instead as one
  sentence on the PATH line of the flag it answers, with an `@vTAG` footnote

### Requirement: Flags close the section they judge
Each argument section MUST end with the flags that judge it, and the prose above
them MUST carry the argument. A flag MUST NOT be the only place a claim is made
or sourced, and MUST NOT introduce an object the prose above it has not defined.
Figures are optional; each carries one idea, and a figure MUST NOT be the only
statement of a claim. The argument markers of `site/level-common` are optional
on this page, which MAY carry none.

#### Scenario: A flag introduces a new object
- **WHEN** a proposed RED or GREEN names an object the section's prose has not
  defined
- **THEN** the delta either defines the object in the prose or restates the flag
  in the terms the section already established

#### Scenario: A figure is proposed
- **WHEN** a figure is proposed for a section
- **THEN** it illustrates a claim the prose already makes and sources, and the
  claim survives with the figure removed

### Requirement: Claim-with-hypotheses form
Every mathematical claim on the page MUST name the theorem it invokes and the
hypotheses it needs, and MUST be sorted into the page's four bins: the standard
theorem invoked, what the repository asserts, what follows, and what does not.
The strength of the page's own arguments is marked PROVEN, PLAUSIBLE or REFUTED
per `docs/matrix/README.md`, sparingly; every RED has a PATH.

#### Scenario: Form is preserved
- **WHEN** the page is revised
- **THEN** each claim still names its theorem and hypotheses and sits in one of
  the four bins, and the markers are used where the page reasons, not
  everywhere

### Requirement: Numbered statements are stated in full before they are used
Every theorem or proposition the page relies on MUST appear as a numbered
statement, with its hypotheses and its conclusion written out, before any later
sentence rests on it, and MUST be referred to afterwards by that number. A
statement that is the page's own MUST NOT be titled with another author's name:
a named theorem is the statement its author proved, and where a reader would
otherwise assume the famous theorem the page MUST distinguish the two. Any
convention a quoted bound depends on MUST be fixed in the text at first use,
because authors differ and an unfixed convention makes the bound meaningless.

#### Scenario: A bound is quoted
- **WHEN** the page states a numerical bound on a chain, a height, or a number
  of steps
- **THEN** the convention that gives that bound its value is fixed in the text
  before the bound is used

#### Scenario: A statement is the page's own
- **WHEN** the page states a result it assembled rather than one its cited
  author proved
- **THEN** the statement is titled by what it says, and the neighbouring famous
  theorem is named separately, with the difference in hypotheses stated

### Requirement: A shortcoming is the missing property, never the absent artifact
Every RED MUST state the property that fails or is undischarged. It MUST NOT be
worded as the absence of a named artifact — a manifest dependency, a file, a
crate, a module, a test name, a symbol, or a count of occurrences — because the
artifact can appear without the property being discharged, at which point the
sentence is false while the finding it stood for is still true. Where naming the
artifact makes the finding concrete, it belongs beneath the property claim as
evidence, in a footnote, not as the claim itself.

#### Scenario: The named artifact appears
- **WHEN** a build adds the dependency, file or test a RED named as absent
- **THEN** a RED worded as the property is still true and only its PATH gains the
  acknowledgement; a RED worded as the artifact's absence is now false and is a
  defect to be corrected in the next change

#### Scenario: A discharge procedure lands over a model
- **WHEN** the procedure a RED asks for is implemented over a committed fixture
  or model rather than over the objects that actually run
- **THEN** the RED states which of the two the procedure covers, rather than
  saying the procedure is absent or that it is done

### Requirement: Tense is fixed by the pin
Present-tense prose on this page describes the pinned release and nothing else. A
fact established only in a build newer than the pin MUST NOT appear as
present-tense prose; it appears on a PATH line, saying when it landed and which
build carried it, with an `@vTAG` footnote. Claims of repository *silence* —
that something is not addressed, not run, not argued, not recorded, does not
exist, or is nowhere in the tree — MUST be re-checked at every pin bump and at
every delta that touches them, because they are the sentences that rot first: an
addition anywhere in the tree falsifies them without touching the range the page
cites. A sentence that describes the relation between the page's pin and a fix —
that the quoted passage is the pre-fix text, that the correction came after the
release the page cites, that a citation is deliberately left pinned — is itself a
claim about the pin, and MUST be listed for re-derivation in any change that
moves the pin.

#### Scenario: A silence claim is outrun
- **WHEN** a build newer than the pin supplies the thing the page says is absent,
  unaddressed or not run
- **THEN** the present-tense sentence stays true only if it is true at the pin,
  and the newer build is acknowledged on the PATH line rather than in the prose;
  when the pin moves onto that build the sentence is rewritten, not re-pointed

#### Scenario: The pin moves onto the corrected source
- **WHEN** a pin bump reaches a tag whose text is the corrected text a flag
  describes as pre-fix
- **THEN** the change lists every pin-relative sentence — the flag, its PATH, and
  the prose that frames the citation — as deltas re-derived at the new tag

### Requirement: A landing date is not a release
Where the page dates a fix it MUST keep three things distinct: the day the work
landed on trunk, the build that first carried it, and the day that build was
cut. A dated sentence MUST NOT attach a build's tag to the landing date, and
MUST NOT name a channel against a date on which no build of that channel
existed. Dates MUST be checked against the runtime's own release ledger, not
against its work record, which dates landings rather than releases.

#### Scenario: A fix lands one day and ships the next
- **WHEN** work lands on trunk and first reaches a channel in a build cut later
- **THEN** the PATH says the fix landed on the landing date and reached that
  channel in the named build, with that build's own cut date

#### Scenario: Page and record are corrected together
- **WHEN** a dated sentence on the page is found to misattribute a date or a
  channel
- **THEN** the correction is a delta, and the wording in the change record that
  the page copies is corrected in the same change, so record and page agree

### Requirement: A negative result states its scope
Where the page concludes that a structure is absent — no metric, no adjunction,
no measure, no probability — the conclusion MUST be about the object the
repository documents today, and MUST NOT be generalised into an impossibility.
Wordings that assert no such object could exist, that it cannot be made into
one, or that a route is closed, are forbidden. Each negative result MUST name the
object a future positive claim would have to construct and MUST say that
building it is open work rather than blocked; where the repository itself cites
the layer that would license the claim, the page MUST read that citation as an
admission that the layer is buildable.

#### Scenario: A structure is shown absent
- **WHEN** the page shows that today's object does not carry a structure
- **THEN** it says the claim is the narrow one — this object, as defined — and
  names what a future construction would have to supply

#### Scenario: An impossibility is proposed
- **WHEN** a proposed sentence says no such object can exist, or that a classical
  route is permanently closed
- **THEN** the proposal is refused unless it carries a proof of impossibility at
  the pin

### Requirement: No superlative, exhaustiveness or count the source does not carry
The page MUST NOT use an exhaustive or superlative quantifier — every, all,
always, never, only, none, exactly once, the whole — unless the cited range
supports it at the pin; where the source hedges, the page carries the hedge at
the source's own strength rather than sharpening it. A statement that a set of
properties, tests or coordinates is covered MUST name the members that are
covered unless every member is. Any count in the prose — of lines, files,
occurrences, tests, table arms, or members of a set — MUST be re-measured at the
pin whenever the sentence carrying it is touched, and MUST be replaced by the
property it stood in for when it cannot be re-measured; implementation trivia
earns its place only when the claim collapses without it.

#### Scenario: A repository-wide sweep is claimed
- **WHEN** the page says a term occurs a given number of times across the
  repository
- **THEN** the sweep is re-run at the pin and the number corrected, or the
  sentence is recast as the property it was evidence for

#### Scenario: A family of properties is called tested
- **WHEN** the page says the properties of an algebraic structure are tested by
  name
- **THEN** it names the ones that are, and does not let the count of the family
  stand for the count of the tests

### Requirement: One claim, one citation
A sentence making several claims MUST carry evidence for each, or be split until
it does. A footnote MUST evidence the clause it is attached to, and MUST NOT be
borrowed for a neighbouring clause whose evidence lives in another file. A GREEN
MUST NOT compress a design property and a machine check into one sentence: what
the design intends and what a test or a gate actually verifies are separate
claims with separate evidence, and where the check covers only part of the
claim, the page says which part.

#### Scenario: A PATH makes several claims under one footnote
- **WHEN** a PATH sentence asserts several things a newer build did and carries
  one footnote covering the first
- **THEN** each uncited clause gains its own footnote at the tag it speaks about,
  or the clause is dropped

#### Scenario: A mechanism and its report
- **WHEN** a claim says a value is computed and also that it is reported or
  printed
- **THEN** the footnote evidencing the computation does not stand for the
  reporting, which is cited where it lives

### Requirement: Quotation inside the prose is verbatim at the pin
Where the page quotes the repository inside its own sentences — in quotation
marks or italics, not only in a footnote's quote block — the quoted characters
MUST appear in the cited range at the pin, under the same verbatim rule the
checked build applies to footnote quotes. At a pin bump every in-prose quotation
MUST be re-taken at the new tag. Where the upstream passage was rewritten, the
page MUST NOT simply re-point the quotation at whatever replaced it: the flag the
quotation supported is re-derived first and re-sourced second, because a
rewritten source usually means the finding has moved. A quotation that exists at
no tag the page may cite MUST be recast as indirect speech or dropped.

#### Scenario: The quoted passage was rewritten upstream
- **WHEN** a pin bump reaches a tag where the sentence the page quotes no longer
  exists
- **THEN** the change re-derives the claim the quotation supported before
  choosing a new target, and the checked build's failure is treated as the
  finding rather than as a broken link

#### Scenario: A quotation is carried across a bump unchecked
- **WHEN** a delta moves the pin and leaves an in-prose quotation untouched
- **THEN** that is a defect: every in-prose quotation is listed and re-verified
  in the change that moves the pin

### Requirement: An objection says what it does not kill
Where the page shows a theorem invoked outside its hypotheses, or an argument
resting on an undischarged premise, it MUST state what the objection establishes
and what it does not: that the conclusion is unearned rather than false, that the
design is not thereby shown wrong, and what the cheapest repair would be. An
objection to an argument MUST NOT be left standing as a verdict on the thing
argued about.

#### Scenario: A hypothesis is violated
- **WHEN** the page shows that a cited theorem's hypothesis fails for the process
  it is applied to
- **THEN** the same passage states that the conclusion is unearned rather than
  refuted, and names the theorem or the argument that would cover the case

### Requirement: The Verdict is derived, never written independently
Every sentence of the Verdict MUST restate a claim the sections above
established. It MUST NOT introduce a claim, a number or an object no section
carries, and MUST NOT stand unchanged when a flag it summarises changes. A change
that rewrites a flag — into the past tense, into a GREEN, or into a narrower
claim — MUST list the Verdict sentence covering that flag as a delta in the same
change, or record that the Verdict does not summarise it. The Verdict is the last
place a corrected claim survives in its old tense, which is where it has survived
before.

#### Scenario: A flag is corrected
- **WHEN** a delta rewrites a RED or its PATH
- **THEN** the same change lists the Verdict sentence that summarises it, or
  records that the Verdict does not summarise that flag

#### Scenario: The Verdict outruns the sections
- **WHEN** a proposed Verdict sentence names an object or a number no section
  above it establishes and sources
- **THEN** the proposal is refused until the claim is made and sourced where it
  belongs

### Requirement: Work is named by what it did
The page MUST refer to work in the runtime by what it changed and when it landed,
never by the identifier the runtime's ledger, its work record or an audit note
uses for it, per `docs/matrix/README.md`. A delta proposal MAY carry those
identifiers in its own evidence, and MUST strip them from the wording it proposes
for the page; an audit's suggested rewrite MUST NOT be pasted into the page with
its identifiers intact.

#### Scenario: An audit suggests a rewrite carrying identifiers
- **WHEN** an audit note proposes page wording that names an order or packet
  identifier
- **THEN** the delta restates it as what the work did and when it landed, and
  keeps the identifier only in the change's evidence

### Requirement: Verdicts are re-derived, never frozen
At each pin bump the proposal MUST re-examine every RED and every PLAUSIBLE
against the target tag and propose past-tense or GREEN wording where the code
has moved, while a fix present only in a build newer than the pin stays RED with
that build named in its PATH. This spec requires the form of the verdicts and
never a particular verdict: which hypotheses are discharged and which are
assumed is a fact of the pin, restated at each bump.

#### Scenario: A daily fixes a RED
- **WHEN** a RED on the page is fixed only in a build newer than level 5's pin
- **THEN** the RED stays, and its PATH names that build with an `@vTAG` footnote

#### Scenario: The pin outruns a hypothesis flag
- **WHEN** a pin bump reaches a tag whose code discharges a hypothesis the page
  called assumed
- **THEN** the change proposes the past-tense or GREEN wording for that flag with
  evidence at the new tag

### Requirement: Sourcing
Repository claims MUST cite `methodology/` or `crates/` (or another repository
path) at the pin with verbatim quotes that pass the checked build. External
references MUST cite a DOI or a stable URL and carry no quote. Measured numbers
in the prose (line counts, dashboard figures) MUST be re-measured at every pin
bump.

#### Scenario: Footnotes resolve at the pin
- **WHEN** a checked build is run for this page
- **THEN** every footnote target exists at the pinned tag within its cited line
  range and every quote is found inside that range

#### Scenario: A measured number is carried across a bump
- **WHEN** a pin bump is proposed and the prose contains a measured number
- **THEN** the change re-measures it at the target tag or lists it as a delta

### Requirement: Audit annotations are the proposal's input
Audit annotations for level 5 MUST be accepted as dated notes valid for the pin
they name; they are allowed and expected, they are the input to the next delta
proposal, and they are superseded per pin as `site/level-common` says.

#### Scenario: An audit annotates level 5
- **WHEN** an audit at a tag finds a level-5 claim drifted or outrun
- **THEN** the finding is recorded as a dated note and becomes a listed delta in
  the next OpenSpec change for the page; the page itself is not edited by the
  auditor
