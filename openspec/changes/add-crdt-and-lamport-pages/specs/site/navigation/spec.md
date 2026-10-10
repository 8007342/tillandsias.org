## MODIFIED Requirements

### Requirement: Two explainer pages after CentiColons
The menu MUST list, immediately after **CentiColons** and in this order,
**CRDT ...what?** and **Lamport Clocks**. Each MUST be a page of the one
generated document, addressable by a fragment (`#crdt`, `#lamport`) and built
from the renderer's source, never edited in the rendered output. The two pages
MUST link to each other in the body, so a reader can follow the operator's
journey (non-conflict, then distillation, then logical time) without the menu.

#### Scenario: A reader follows the journey
- **WHEN** a reader reaches the end of CRDT ...what?
- **THEN** a control in the article opens Lamport Clocks, and the end of
  Lamport Clocks offers the way back

#### Scenario: A deep link
- **WHEN** a reader opens the site at `#crdt` or `#lamport`
- **THEN** that page is shown and the menu marks it as current

### Requirement: The explainer pages are accurate before they are enthusiastic
Both pages MUST NOT state that git is a CRDT, that git runs Lamport
timestamps, or that the plan ledger is conflict-free by virtue of git alone.
They MUST attribute replication, content addressing and causal history to git,
and conflict-freedom to the project's append-only fragments and deterministic
fold. They MUST describe the ledger's ordering as it is shipped: UTC-first
fragment names and a timestamp-then-host rule for single-valued fields. They
MUST NOT name internal work-item, order or pull-request identifiers.

#### Scenario: A stronger claim is proposed
- **WHEN** an edit would present git, or the ledger, as "a CRDT out of the box"
- **THEN** it is refused: the page keeps the split between what git gives and
  what the discipline adds

#### Scenario: The ledger's merge rule changes
- **WHEN** the runtime replaces its timestamp-and-host tie-break with a logical
  counter
- **THEN** the Lamport page is corrected through a change to this spec, with
  the source span cited in the change
