# A Methodology page, and a research note tracked to publication

Status: implemented 2026-11-13 on branch `work/methodology-page`, on the
operator's direction of the same day. Awaiting operator review; not archived.

## Why

The site explains what Tillandsias is (five levels, under **What is it?**) and
three pieces of how it is built (CentiColons, CRDT, Lamport Clocks), but it has
no page for the method as a whole. The operator also wants a short research
note, with numbers, finished before the end of 2026, on three ideas from the
methodology. The note doubles as a writing sample for research programmes and
grants, so it needs a stable public home and a tracked path to get there.

## What changes

- The menu entry **What is it?** becomes **Methodology** (`#methodology`), in
  the same position. It is one page in three sections, one shown at a time:
  1. **How it is built** (`#methodology`): five rules, each linked to the lines
     of the runtime's methodology that state it at the site's checked release.
  2. **What it is, five ways** (`#what`): the five levels, unchanged, with
     their tab strip and footnotes.
  3. **Research note (in progress)** (`#research-note`): three headed stubs
     (`#note-peer-falsification`, `#note-fail-closed-gates`,
     `#note-refusals-as-interfaces`), each a one-paragraph thesis, the rules it
     comes from, and an "Evidence to gather" checklist.
- Old addresses keep working: `#what` opens the five levels, `#level-…` opens
  that level, and a footnote address (`#rlevel-…-n`, `#flevel-…-n`) opened
  cold now opens its level too. Home's **What is it?** button lands on the
  five levels.
- The research note's evidence and milestones are tracked in
  `plan/research-note.md` and `plan/research-note-evidence.md`, not on the page.

## What does not change

- The level sources in `docs/matrix/`, their pins and their footnotes. Level 5
  is not touched.
- The page-level rules in `docs/matrix/README.md`. The Methodology page is the
  one place where "how the project runs" is the reader's subject, so that rule's
  ban on process text does not apply to it; the bans on anecdote, internal
  identifiers and named machines or people do.

## Rules this page is held to

- **No number before it is verified.** The public stubs carry no count, date
  of an incident, machine or person. Evidence reaches the page only after the
  "numbers verified" milestone in `plan/research-note.md`.
- **The argument is the operator's.** Agents outline, gather evidence and
  edit. Stubs and theses are allowed; finished prose presented as the
  operator's is not.
- **Fleet-agnostic.** No host names, session details or private
  infrastructure, in the page or in what it links to by label.
- **Citations are `rcite("path#Lx-Ly", "label")` literals**, so the release
  refresh re-anchors them (`scripts/anchors.py`).

## Considered and rejected

- *A new menu entry beside What is it?* Rejected: the direction was to turn
  the existing content into the Methodology entry, and two entries would split
  one subject across two maps.
- *One long scrolling page.* Rejected: a level runs to thousands of words, so
  the research note would sit under whichever level was open and never be seen.
- *Renaming `#what`.* Rejected: it is the address already shared in links.
