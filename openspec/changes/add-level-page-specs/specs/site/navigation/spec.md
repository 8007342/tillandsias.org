## Purpose

The site as a whole. `tillandsias.org` is one generated document presenting
three pages behind a collapsing menu: a **Home** placeholder, the **"What is
it?"** explanation — the five levels, whose content is specified in
`site/level-common` and `site/level-1` through `site/level-5` — and **Live
progress**, the board that renders this project's own findings ledger.

This spec states what the site is: the menu and its entries, which page a reader
lands on, what Home carries, and the contract of the progress board — that every
finding in the ledger appears in exactly one of three columns, that those columns
are derived from the ledger's own monotone ladder rather than curated by hand,
and that a measurement the project cannot yet compute is never displayed as
though it could. It does not restate the level rules; the five levels' content
belongs to their own specs, and the rules they share to `site/level-common`.

The two pages that are not explanation levels have no footnote machinery, and
that is the hazard this spec exists to contain. They are the only surfaces where
the site can say something without a citation under it, and the only ones that
report on work in flight, where the temptation is to describe an intention in the
present tense and a proxy as a measurement. Much of what follows is therefore
written as sentence shapes these pages must not use.

## ADDED Requirements

### Requirement: Three pages behind one collapsing menu
The site MUST present exactly three pages, reached from a single menu: a control
at the top of the viewport opens a menu that collapses out of the way when it is
not in use, and that menu MUST list, in this order, **Home**, **What is it?** and
**Live progress**. Exactly one page is visible at a time; the menu MUST mark
which one; choosing an entry MUST close the menu; and the reader MUST be able to
dismiss the menu without choosing anything. The five explanation levels MUST NOT
be promoted into the menu — they are one page's internal navigation, and a site
with two navigations of different depths asks the reader to hold two maps at once.

#### Scenario: A reader opens the menu
- **WHEN** a reader opens the menu
- **THEN** the three entries appear in that order, and the entry for the page
  they are already on is marked as current

#### Scenario: A reader changes their mind
- **WHEN** a reader opens the menu and decides not to leave the page
- **THEN** dismissing it — by the control, by the surface outside it, or by the
  keyboard — returns them to the page unchanged

#### Scenario: A fourth page is wanted
- **WHEN** someone proposes another page for the site
- **THEN** it becomes a further menu entry through a change to this spec, and is
  not published as a page reachable only from a link inside another page

### Requirement: The landing page is "What is it?"
A reader arriving at the site's root MUST land on **What is it?** without
touching the menu. Home is the first menu entry and is deliberately not the
landing page; that arrangement MUST NOT be treated as an inconsistency to be
tidied away. Which page is the landing page is a property of this spec: moving it
is a change to this requirement, not an editorial decision. Every page MUST also
be addressable directly, and the address of the landing page MUST NOT require a
fragment.

#### Scenario: Arriving at the root
- **WHEN** a reader opens the site with no fragment
- **THEN** the explanation page is shown and the menu marks it as current

#### Scenario: A link into a level
- **WHEN** a reader follows a link that names one explanation level
- **THEN** the site opens the explanation page and that level within it

#### Scenario: Landing on Home is proposed
- **WHEN** someone wants the site to land on Home instead
- **THEN** the change is made to this requirement first, so the landing page is
  never a matter of which page happened to be marked active in the markup

### Requirement: The explanation levels live inside one page
All five levels, their tab strip, the install commands, the flag legend and the
per-level footnote lists MUST live inside "What is it?" and nowhere else. The
other two pages MUST NOT duplicate the install commands, the legend, or any of a
level's prose: a second copy drifts from the first, and only the copy the build
checks against the pinned source is verified.

#### Scenario: Install commands are wanted on Home
- **WHEN** an editor wants the install commands in front of a reader sooner
- **THEN** Home links to the explanation page, which carries the one copy the
  build checks

#### Scenario: A level's claim is wanted elsewhere
- **WHEN** another page wants to state something a level already states
- **THEN** it links to that level rather than restating the claim without its
  footnote

### Requirement: The site is generated, and the menu with it
The published HTML is a build product. The menu, the Home page and the progress
board MUST be emitted by the build from sources kept beside it — the level prose,
the fact pool, the ledger fragments — and MUST NOT be edited in the rendered
output. A rebuild from unchanged sources MUST produce the same bytes, so that a
diff of the published page shows only what an editor actually changed.

#### Scenario: A word on Home changes
- **WHEN** someone wants to reword the home page
- **THEN** they edit the build's source and rebuild, and the rendered file is
  never the thing that was edited

#### Scenario: Two builds of one tree
- **WHEN** the same sources are built twice
- **THEN** the two outputs are identical, including the order the findings appear
  in on the board

### Requirement: Home is a placeholder, and says so
Until the artwork exists, Home MUST hold its place with a visible placeholder
that is labelled as one and drawn in the site's own dark theme rather than as a
blank light panel, and MUST NOT present a stand-in as the finished artwork. The
placeholder, and whatever eventually replaces it, MUST ship with the document —
an inline drawing or an asset this project publishes — and MUST NOT be fetched
from a third party; the site loads no external images.

#### Scenario: The artwork arrives
- **WHEN** the intended image is ready
- **THEN** it replaces the placeholder and the label saying an image is still to
  come is removed with it

#### Scenario: A stand-in image is offered
- **WHEN** an editor wants to fill the space with a photograph from elsewhere
- **THEN** it is refused: the page keeps a placeholder that admits what it is
  rather than an image the project does not ship

### Requirement: The wordmark and the byline
Home MUST carry the word **Tillandsias** as the largest text on the page and,
beneath it, the byline **by Tlatoāni**, spelled with a macron over the first *a*.
Both MUST be text the reader can select and a search engine can read, never a
picture of text. The unaccented spellings MUST NOT appear: the macron is part of
the name, not decoration on it.

#### Scenario: The byline is rendered
- **WHEN** the home page is built
- **THEN** the byline carries the macron, as characters rather than as an image

#### Scenario: A font lacks the glyph
- **WHEN** the chosen face has no macron form
- **THEN** the remedy is another face in the fallback stack, never a respelling
  of the name

### Requirement: Exactly one fun fact, drawn from a pool
Home MUST show exactly one fact about *Tillandsia*, the genus the project is
named after, drawn from a pool large enough that repeat visits differ. The pool
MUST ship inside the page, so choosing costs no request, and MUST NOT be rendered
to the reader as a list — one fact is the whole idea. A reader whose browser runs
no script MUST still see exactly one. Each fact obeys the rules the levels' plant
asides obey: one sentence, botanically true, at most a half-clause tying it to
the software, and no footnote, because it is not a claim about the software.

#### Scenario: Two visits
- **WHEN** a reader loads Home twice
- **THEN** the fact may differ between the visits, and exactly one is shown either
  time

#### Scenario: Scripting is unavailable
- **WHEN** the page runs no script
- **THEN** one fact from the pool is still on the page, and the pool is still not
  shown as a list

#### Scenario: A fact is disputed
- **WHEN** a fact in the pool turns out to be doubtful
- **THEN** it is cut rather than hedged, qualified or dressed up

### Requirement: Home carries nothing that belongs to another page
Home MUST carry the placeholder, the wordmark, the byline and the single fact. It
MAY carry one short line of positioning and direct links onward to the other two
pages; dropping either MUST NOT be treated as a regression. Home MUST NOT carry:
install or quick-start commands; the flag legend or any GREEN, RED or PATH flag;
an explanation of the software beyond that one line; findings, counts, scores or
anything from the ledger; a sign-up, contact block, newsletter, or tracking
beacon; or any call to action other than the links to this site's own pages.

#### Scenario: The positioning line makes a claim
- **WHEN** the one line of positioning says anything about what the software does
- **THEN** it says only what a level page already carries with a footnote, in
  words no stronger, and short enough that the two can be compared at a glance

#### Scenario: Home starts to explain
- **WHEN** the positioning line grows into a paragraph, or an argument follows it
- **THEN** the material moves to the level whose audience asks for it, and Home
  keeps the one line

### Requirement: The progress page shows the board and what backs it
The **Live progress** page MUST carry: a heading; a lede saying what the board is
and that its contents come from the ledger rather than from anyone's judgement;
the three columns, left to right, each with a heading, a sentence saying what
belongs in it, and its own count; a tally of the whole board computed from the
same fold that fills the columns, never counted separately; and a statement of
what is and is not measured. It MAY also carry a bar visualising that same tally,
per-finding detail such as severity, area and originating repository, and a link
to the ledger's own description of its shape. It MUST NOT carry a hand-written
status narrative, a burndown or velocity claim, a completion percentage presented
as a score, a delivery date or estimate for work nothing has scheduled, or any
finding shown outside the three columns.

#### Scenario: The tally and the columns disagree
- **WHEN** a tally is computed from a different read of the ledger than the columns
- **THEN** the page can contradict itself, so one fold feeds both

#### Scenario: A schedule is wanted
- **WHEN** a reader asks when the remaining findings will be closed
- **THEN** the page does not answer with a date, because nothing in the ledger
  records one

### Requirement: Every finding is in exactly one column
Every finding in the ledger MUST appear on the board, in exactly one of the three
columns, and nowhere else. No finding may be withheld because it is old, of low
severity, belongs to the other repository, or is embarrassing; none may appear
twice; and there MUST NOT be a fourth place — no "other", no archive, no drawer.
A finding whose attempt ended without its criteria being met MUST NOT be shown in
the right-hand column, and MUST NOT be dropped from the board either.

#### Scenario: A finding is only declared
- **WHEN** the ledger carries a finding and nothing has happened to it since
- **THEN** it appears in the left-hand column

#### Scenario: An attempt ends without completion
- **WHEN** a finding is abandoned, or made irrelevant by later work
- **THEN** it stays on the board and is not shown as completed work

#### Scenario: A reader counts the cards
- **WHEN** a reader adds up the three column counts
- **THEN** the sum equals the number of findings in the ledger

### Requirement: What each column means
The board's columns MUST mean, and MUST say on the page:

- **Left**: found and not yet tracked — undocumented, unfiled or newly
  discovered — where uncertainty about the finding is still high.
- **Middle**: documented and tracked — triaged, filed, being worked, or blocked
  with the reason recorded — where a plan of work exists and uncertainty is low
  enough to act on.
- **Right**: completed, and the component the finding was about now meets its own
  written criteria.

Each heading and blurb MUST state its meaning in words a reader who has never
opened the ledger can apply to a finding of their own. The right-hand column MUST
NOT be described as, or used for, work that is merely no longer being worked on:
stopping is not the same as meeting the criteria, and a board that blurs the two
reports progress that did not happen.

#### Scenario: A reader classifies a finding
- **WHEN** a reader with a defect of their own reads the column headings
- **THEN** they can tell which column it would go in without reading the ledger's
  own documentation

#### Scenario: Work stops short
- **WHEN** work on a finding stops before its criteria are met
- **THEN** the board does not move it to the right-hand column

### Requirement: The columns are derived from the ledger's ladder, not maintained by hand
Column membership MUST be computed at build time by folding the ledger's
fragments and joining each finding's events over the ledger's monotone ladder, as
the ledger itself defines it. The page MUST NOT carry a hand-written list of
findings, and no editor may set a finding's column directly: a finding moves by
an event appended to the ledger, and returns to the left-hand column only through
the ledger's falsification event, which carries its reason. The page and the
ledger therefore cannot disagree, and that — rather than editorial care — is what
keeps the board true.

A failure to read the ledger MUST NOT be rendered as an empty or a finished
board. If the fold fails, the page says so or is not published; silence there
reads as "nothing has ever been found", which is the one statement this board
must never make.

#### Scenario: A finding is triaged
- **WHEN** someone triages a finding
- **THEN** they append a fragment to the ledger and the next build moves the card;
  the rendered page is not edited

#### Scenario: A completed finding turns out to be wrong
- **WHEN** a finding in the right-hand column is falsified
- **THEN** the ledger records the falsification with its reason, and the next
  build returns the card to the left-hand column with that reason available

#### Scenario: The ledger will not fold
- **WHEN** a malformed fragment makes the fold fail
- **THEN** the board is not published showing three empty columns as though the
  project had found nothing

### Requirement: Dependencies and chronology are visible
Each finding on the board MUST show its dependencies where it has any, naming
them by the same handle the depended-on finding's own card carries, so a reader
can find it; and MUST show when it was first recorded and when it last moved, so
that the board reads as a chronology and a finding that has not moved in a long
time is visible as one. Within a column, findings MUST be ordered by a rule the
build states rather than by whatever order the fragments happen to be read in:
the fold is deterministic, and the rendering MUST be too.

#### Scenario: One finding waits on another
- **WHEN** a finding cannot proceed until another is resolved
- **THEN** its card names the other, and the other is on the board

#### Scenario: A finding has not moved
- **WHEN** a finding has sat in one column since it was recorded
- **THEN** both dates are visible and a reader can see the gap between them

#### Scenario: The same ledger is built twice
- **WHEN** two builds run over an unchanged ledger
- **THEN** each column lists its findings in the same order both times

### Requirement: Follow-through is visible, including what has not happened
The board exists so that no finding is quietly dropped, so it MUST show, per
finding, whether it has been carried where it has to go. A finding against
another project MUST show whether it has been filed there, and link the filing
once one exists; an unfiled finding MUST NOT be displayed in a way that lets it
read as filed. This repository holds no credential for the other project by
design, so the board states the gap rather than hiding it.

#### Scenario: A finding against the runtime is not yet filed
- **WHEN** a finding belongs to another project and no filing exists
- **THEN** the card says so plainly, rather than leaving the space blank

#### Scenario: The filing lands
- **WHEN** a credentialed session files the finding and writes the location back
  into the ledger
- **THEN** the next build shows the card linking it

### Requirement: Measurement is named as an intention, never presented as measured
The page MAY state the intention to grade this project's components the way the
runtime grades itself, with its CentiColon score, and to plot convergence over
time. It MUST NOT show a number as this project's score while nothing computes
one. It MUST NOT present the runtime's published figure as a measured score while
that figure is produced by a weight table over continuous-integration check names
rather than by the arithmetic the runtime's own methodology defines — its base
weights, multipliers, cap rules and penalties. A figure that is a pass rate is
called a pass rate, in the visible sentence.

Every number the page does show MUST say what it counts. A count of findings by
column is a real measurement of a small thing and is allowed; it MUST NOT be
labelled, coloured or captioned as a score, a completion percentage, a confidence
or a proportion of the work.

#### Scenario: The page shows its own tally
- **WHEN** the board displays a bar or a set of counts
- **THEN** they are labelled as counts of findings by column, and as nothing else

#### Scenario: A published figure is repeated
- **WHEN** the page wants to quote a figure another project publishes
- **THEN** it says how that figure is computed before repeating it, or does not
  repeat it

#### Scenario: The specified arithmetic starts computing the score
- **WHEN** the score is computed by the arithmetic its own specification names
- **THEN** the page may present it as a score, saying which release first computed
  it that way

### Requirement: Convergence graphs, when there is something to plot
When the page plots progress it MUST plot recorded values, per component, against
a logarithmic time axis, so that the most recent work occupies the widest part of
the graph and older work compresses towards the origin. A gap in the record MUST
be drawn as a gap, never interpolated across or back-filled from a later value. A
claim that scores rise monotonically between releases, or between spec changes,
MUST NOT be drawn across a boundary at which the score's denominator changed:
two scores over different denominators are not comparable, and a line joining
them shows a rise or a fall that did not happen. Such a boundary MUST be marked
as a change of scope, and the reader told the comparison does not hold there.

#### Scenario: The denominator changes between two releases
- **WHEN** a release changes what the score is computed over
- **THEN** the graph marks that boundary rather than drawing a slope across it

#### Scenario: Nothing has been recorded yet
- **WHEN** no component has a recorded score
- **THEN** the page says what is missing and why, and draws no axes waiting to be
  filled

#### Scenario: A component goes unmeasured for a while
- **WHEN** a component has no recorded score for part of the plotted span
- **THEN** that part is left blank rather than joined up

### Requirement: Neither non-level page makes an uncited claim about the software
Home and Live progress carry no footnote machinery, so they MUST NOT be used to
say something about the runtime that the site has not established elsewhere. Any
statement they make about what the software does MUST be one a level page already
carries with a footnote resolving at that level's pin, worded no more strongly
than there. Statements about *this site* — what the board shows, where the columns
come from, what is not yet measured — belong here, and MUST be checkable against
this repository.

#### Scenario: A new claim is wanted on a non-level page
- **WHEN** an editor wants to assert something new about the runtime on Home or on
  the board
- **THEN** it is made on the level that owns it, with its footnote, before it is
  echoed here

#### Scenario: A level weakens a claim
- **WHEN** a level's claim is narrowed or withdrawn at a pin bump
- **THEN** the echo on the non-level page is narrowed or dropped with it

### Requirement: Sentence shapes these pages must not use
On Home, on Live progress and in the menu, a sentence MUST NOT:

- state a planned capability in the present tense, or leave the plan's status to
  a caption, a heading or a tooltip — the visible sentence names it as a plan and
  says what is missing;
- present a proxy as the thing it stands for: a pass rate as a score, a count of
  findings as a measure of quality, a proportion of cards as a proportion of the
  work;
- promise what people will do — that every finding will be triaged, that nothing
  will be dropped — where the machinery guarantees only what it computes; the
  page states the property the fold enforces and names the rest as an intention;
- describe a rule as the opposite kind of rule: the board's contract is a
  derivation from the ledger, and MUST NOT be described as a curation policy, an
  editorial choice about what to show, or a list of what is left out;
- reassure beyond what the code supports — that nothing can be lost, that the
  ledger cannot be corrupted — instead of saying what the fold guarantees and
  stopping there;
- use a superlative, or a comparison with an unnamed alternative, in place of a
  checkable statement;
- carry an internal identifier as its subject: a finding's handle belongs on its
  card, and the prose states substance a reader could repeat out loud;
- give a number without its unit or its denominator;
- comment on its own verdict — that something is good news, or still bad — when
  the column, the flag or the count already carries it.

#### Scenario: A planned graph is described
- **WHEN** the page describes a graph it intends to draw
- **THEN** the visible sentence says it is a plan and what is missing, rather than
  describing the graph as though it were on the page

#### Scenario: A sentence needs the ledger's vocabulary
- **WHEN** a proposed sentence can only be checked by a reader who already knows
  the ledger's own terms
- **THEN** it is rewritten in words the page itself defines, or the term is
  defined on the page
