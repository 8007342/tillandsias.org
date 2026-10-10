## Why

The site explains CentiColons, the measurement, but says nothing about the
other pillar the measurement stands on: the shared plan is an append-only pile
of evidence that many agents on many hosts write to without conflicts, folded
into one readable view. A reader who asks "how can that many agents share one
plan?" currently has no page to be sent to, and the one place the idea appears,
Level 5, is written for a mathematician.

## What Changes

- Two menu entries after CentiColons, in this order: **CRDT ...what?** and
  **Lamport Clocks**. Each is a page in the same generated document, addressed
  by `#crdt` and `#lamport`, built from `scripts/build-matrix.py` like the
  CentiColons page, with no footnote machinery.
- **CRDT ...what?** holds an article of the same title: a shared-notebook
  analogy, the three properties of a grow-only set in everyday words, what git
  gives for free (replication, content addressing, parent links) and what it
  does not (git is not a CRDT; same-line edits still conflict), the project's
  append-and-fold discipline for its plan fragments, the fold's three merge
  rules, provenance on every entry, and the three things a CRDT does not
  promise. It ends by handing the reader to the Lamport page.
- **Lamport Clocks** holds the article "Computers don't understand time":
  discrete time, why clock synchronisation is finicky, happens-before,
  Lamport's three-line rule, and the honest relationship to a git commit graph
  (the graph is the causal order; a Lamport clock is the smallest counter
  consistent with it; git computes one as generation numbers). It states what
  the project ships as it is: UTC-first fragment names and a (timestamp, host)
  register for single-valued fields, with causality carried by git. It links
  back to the CRDT page.
- Three figures in `scripts/figures.py`: `append-fold`, `commit-dag`,
  `lamport-exchange`.
- Delta to `site/navigation`: the menu gains the two entries; the pages carry
  no install commands, legend or level prose, and name no internal work-item,
  pull-request or order identifiers, because the reader is the end user.

## Capabilities

### Modified Capabilities

- `site/navigation`: two further menu entries and their page contracts.
