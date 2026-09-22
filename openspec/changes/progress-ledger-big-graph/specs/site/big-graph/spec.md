## Purpose

Big Graph explains the desired Tillandsias architecture using a tillandsias.org checkout inside a forge, while exposing present limits for security review.

## ADDED Requirements

### Requirement: Full system journey and trust boundaries

The map MUST include host and external actors, OS/VM/container boundaries, project and cache filesystem layers, enclave siblings, proxy and git paths, Vault and host key material, certificate and control-wire concerns, website preview, installation through teardown and recovery, and requirements through evidence. Each component MUST provide a goal-state spec link and current-state explanation.

#### Scenario: A reader challenges a boundary

- **WHEN** the reader opens a boundary component
- **THEN** they can inspect its enforcement assumption, known limitation and pinned target specification

### Requirement: Full-screen hierarchical canvas

The graph MUST fill the available viewport below its compact header and scroll horizontally and vertically at its natural size. It MUST arrange the primary build, publish, preview, lifecycle and evidence interactions from left to right, with supporting services and boundaries in labelled rows. It MUST NOT show a zoom or spacing control. Readers MUST be able to hide and restore layer groups and open or dismiss component details with pointer or keyboard. The inspector MUST overlay the canvas rather than reserve a permanent side column.

#### Scenario: A reader follows the push journey

- **WHEN** the reader follows the top row from the operator to the remote
- **THEN** the forge, commit, mirror, proxy and remote appear in that left-to-right order, with off-screen content reachable by scrolling

### Requirement: Planned features remain visually and verbally distinct

Implemented, partial and goal-only components MUST have distinct styles. The page MUST state that edges show intended relationships and do not prove enforcement; it MUST link the current stable audit. A planned capability MUST NOT be described as already working.

#### Scenario: A goal-only component is inspected

- **WHEN** the reader selects the component
- **THEN** its goal-only status and implementation limit remain visible beside its target spec

### Requirement: Inspection distinguishes evidence from aspiration

Each component inspector MUST separate its goal-state role, behavior observed at the pinned release, and incomplete work or scope limits. It MUST link concrete source or archived work records where available, while stating that a checked checklist is historical work evidence rather than current runtime proof. Selecting an already selected component MUST close its inspector; the close control and Escape MUST also close it. If a category hides the selected component, the inspector MUST close.

#### Scenario: A reader clicks the same node twice

- **WHEN** a reader opens a component and then selects that same component again
- **THEN** the panel closes and the node's expanded state returns to false

### Requirement: Filtered layers compact the map

When a category is hidden, its nodes MUST fade before the surviving nodes move to close vacant columns and rows. Connections MUST be redrawn to the new positions. Primary journeys MAY show dotted shortcut connectors across hidden intermediate steps, but the page MUST explain that these shortcuts do not claim a direct connection. A reader who prefers reduced motion MUST receive the same final layout without animation. Restoring a category MUST restore its nodes and layout.

#### Scenario: A reader hides forge components

- **WHEN** the forge category is deselected
- **THEN** forge nodes fade out, the remaining top-row nodes move together, and any shortcut across the hidden stages is labelled as such
