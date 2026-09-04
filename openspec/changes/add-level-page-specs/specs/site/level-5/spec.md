## Purpose

The "I'm a PhD / MathWiz / Hacker" page (`docs/matrix/level-5-phd.md`) is the
formal content: obligation-state lattices, fixed points, the finite-iteration
theorem, the strong-law / monotone-convergence floor, and the CRDT material —
stated as claims with hypotheses, sorted into standard theorems invoked, what the
repository asserts, what follows, and what does not.

## ADDED Requirements

### Requirement: Content ownership boundary
The level-5 **explanation is not owned by this project's audit work**. Per the
2026-09-04 audit scope, this page was neither rewritten nor annotated, and no
audit file exists beside it. This spec exists so the page has a stable identity
and a change trail, but it MUST NOT be read as authorization to rewrite the
page's formal claims.

#### Scenario: A proposed edit to level 5
- **WHEN** an editor or agent proposes changing the level-5 explanation
- **THEN** they must be driven by that page's own owner and verification chain,
  not by this spec

### Requirement: Claim-with-hypotheses form
Any change MUST preserve the page's form: assertions are sorted into standard
theorems being invoked, what the repository actually asserts, what follows, and
what does not — with the short verdict that two load-bearing hypotheses are
assumed rather than discharged.

#### Scenario: Form is preserved
- **WHEN** the page is revised
- **THEN** the claim-with-hypotheses structure and the assumed-hypotheses verdict
  remain intact

### Requirement: Sourcing rule
Mathematical and repository claims MUST carry footnotes resolving against the
pinned tag in `scripts/build-matrix.py` (never `main`), consistent with the other
levels.

#### Scenario: Footnotes resolve at the pin
- **WHEN** a checked build is run for this page
- **THEN** every footnote target exists at the pinned tag within its cited line
  range

## ADDED Artifacts

### Artifact: No audit annotations for level 5
Deliberately absent. The 2026-09-04 audit did not annotate `level-5-phd.md`; its
content is owned elsewhere. Do not create an audit file for it under this change.

---
*Ownership note: this spec is the only artifact this change contributes to level
5 — a declaration of purpose, form and sourcing. The explanation itself is frozen
with respect to this work.*