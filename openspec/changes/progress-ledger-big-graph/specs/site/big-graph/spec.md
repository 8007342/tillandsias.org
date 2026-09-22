## Purpose

Big Graph explains the desired Tillandsias architecture using a tillandsias.org checkout inside a forge, while exposing present limits for security review.

## ADDED Requirements

### Requirement: Full system journey and trust boundaries

The map MUST include host and external actors, OS/VM/container boundaries, project and cache filesystem layers, enclave siblings, proxy and git paths, Vault and host key material, certificate and control-wire concerns, website preview, installation through teardown and recovery, and requirements through evidence. Each component MUST provide a goal-state spec link and current-state explanation.

#### Scenario: A reader challenges a boundary

- **WHEN** the reader opens a boundary component
- **THEN** they can inspect its enforcement assumption, known limitation and pinned target specification

### Requirement: Navigable large canvas

The graph MUST scroll horizontally and vertically. Its spacing control MUST alter component coordinates and canvas size without scaling text. More detail MAY appear when the spacing creates room. Readers MUST be able to hide and restore layer groups and open any component with pointer or keyboard.

#### Scenario: A reader spreads the diagram

- **WHEN** the spacing control increases
- **THEN** component text remains the same CSS size while the components move farther apart

### Requirement: Planned features remain visually and verbally distinct

Implemented, partial and goal-only components MUST have distinct styles. The page MUST state that edges show intended relationships and do not prove enforcement; it MUST link the current stable audit. A planned capability MUST NOT be described as already working.

#### Scenario: A goal-only component is inspected

- **WHEN** the reader selects the component
- **THEN** its goal-only status and implementation limit remain visible beside its target spec
