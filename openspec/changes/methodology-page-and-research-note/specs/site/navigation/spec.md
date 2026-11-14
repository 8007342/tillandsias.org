## MODIFIED Requirements

### Requirement: The explanation levels live inside one page
The menu entry that holds the five explanation levels MUST be named
**Methodology** and MUST sit where **What is it?** sat, directly after Home.
The page MUST present three sections, exactly one visible at a time, in this
order: **How it is built**, **What it is, five ways**, and **Research note**.
All five levels, their tab strip, the flag legend and the per-level footnote
lists MUST live inside the second section and nowhere else. The levels MUST
NOT be promoted into the menu.

#### Scenario: An address from before the rename
- **WHEN** a reader opens the site at `#what`, at a level's address, or at the
  address of one footnote of a level
- **THEN** the Methodology page opens on the five levels, with that level
  selected, and the menu marks Methodology as current

#### Scenario: A deep link to a section
- **WHEN** a reader opens the site at `#methodology` or `#research-note`
- **THEN** that section is shown and the address stays shareable

#### Scenario: Home's question
- **WHEN** a reader presses **What is it?** on Home
- **THEN** they land on the five levels, not on the method

## ADDED Requirements

### Requirement: The method is stated with its source and without a score
Every rule in **How it is built** MUST link to the lines of the runtime
repository that state it, at the release the site was last checked against,
in the citation form the release refresh re-anchors. The section MUST say
what the rules are and MUST NOT claim how often they are followed or how well
they work.

#### Scenario: A rule moves in the runtime
- **WHEN** a release moves or rewrites a cited rule
- **THEN** the refresh re-anchors the link or hands the citation to a person,
  as it does for any other citation on the site

### Requirement: The research note publishes no unverified number
Until the note is published, its section MUST be labelled as in progress with
its target date, and each idea MUST carry a thesis, the rules it comes from
and a list of evidence still to gather. The section MUST NOT state a count, a
rate, a dated incident, or the name of a machine, a session or a person.
A figure MAY appear only after it has been re-counted from the public
runtime repository by a recorded command, and the finished argument MUST be
the operator's own writing.

#### Scenario: An agent has a number ready
- **WHEN** an agent has counted something that supports one of the ideas
- **THEN** it goes into the tracking document with its command and source,
  and not onto the page

#### Scenario: A draft paragraph is offered as the operator's
- **WHEN** an agent writes finished prose for the argument
- **THEN** it is kept as an edit suggestion in the tracking document, and the
  page keeps the stub until the operator has written and passed the text
