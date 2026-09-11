## Purpose

This delta widens the site's navigation spec from three pages to four. Slides —
a presentation deck about Tillandsias — becomes the fourth menu entry, and the
rules that keep non-level pages honest now cover it. The rest of the navigation
spec is unchanged.

## MODIFIED Requirements

### Requirement: Four pages behind one collapsing menu
The site MUST present exactly four pages, reached from a single menu: a control
at the top of the viewport opens a menu that collapses out of the way when it is
not in use, and that menu MUST list, in this order, **Home**, **What is it?**,
**Live progress** and **Slides**. Exactly one page is visible at a time; the
menu MUST mark which one; choosing an entry MUST close the menu; and the reader
MUST be able to dismiss the menu without choosing anything. The five explanation
levels MUST NOT be promoted into the menu — they are one page's internal
navigation, and a site with two navigations of different depths asks the reader
to hold two maps at once.

#### Scenario: A reader opens the menu
- **WHEN** a reader opens the menu
- **THEN** the four entries appear in that order, and the entry for the page
  they are already on is marked as current

#### Scenario: A reader changes their mind
- **WHEN** a reader opens the menu and decides not to leave the page
- **THEN** dismissing it — by the control, by the surface outside it, or by the
  keyboard — returns them to the page unchanged

#### Scenario: A fifth page is wanted
- **WHEN** someone proposes another page for the site
- **THEN** it becomes a further menu entry through a change to this spec, and is
  not published as a page reachable only from a link inside another page

### Requirement: Neither non-level page makes an uncited claim about the software
Home, Live progress and Slides carry no footnote machinery, so they MUST NOT be
used to say something about the runtime that the site has not established
elsewhere. Any statement they make about what the software does MUST be one a
level page already carries with a footnote resolving at that level's pin, worded
no more strongly than there. Statements about *this site* — what the board
shows, where the columns come from, what is not yet measured, what a slide is
drawn from — belong here, and MUST be checkable against this repository. A slide
MUST name the level page it restates, so the reader can follow a claim to its
footnote.

#### Scenario: A new claim is wanted on a non-level page
- **WHEN** an editor wants to assert something new about the runtime on Home, on
  the board or on a slide
- **THEN** it is made on the level that owns it, with its footnote, before it is
  echoed here

#### Scenario: A level weakens a claim
- **WHEN** a level's claim is narrowed or withdrawn at a pin bump
- **THEN** the echo on the non-level page is narrowed or dropped with it

### Requirement: Home carries nothing that belongs to another page
Home MUST carry the placeholder, the wordmark, the byline and the single fact. It
MAY carry one short line of positioning and direct links onward to the other
three pages; dropping either MUST NOT be treated as a regression. Home MUST NOT
carry: install or quick-start commands; the flag legend or any GREEN, RED or
PATH flag; an explanation of the software beyond that one line; findings, counts,
scores or anything from the ledger; a sign-up, contact block, newsletter, or
tracking beacon; or any call to action other than the links to this site's own
pages.

### Requirement: Sentence shapes these pages must not use
On Home, on Live progress, on Slides and in the menu, a sentence MUST NOT:

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

#### Scenario: A slide promises a transition
- **WHEN** a slide announces an animation or a figure that is not on the page
- **THEN** the visible sentence says it is still to come, and where it will draw
  its claim from