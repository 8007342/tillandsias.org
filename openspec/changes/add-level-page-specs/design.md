# Design: add-level-page-specs

## Overview

One delta spec per explanation page, nothing else. The specs are declarative
contracts for the page's *editors* and *reviewers* — they do not change how the
page is built or rendered. The build pipeline (`scripts/build-matrix.py`)
renders only the files listed in its `LEVELS` table; the new specs and the
`*.audit.md` annotation files live beside the page sources under `docs/matrix/`
and are deliberately ignored by the build.

```
docs/matrix/
├── README.md                     (dialect + editorial rules)
├── level-1-five.md  + level-1-five.audit.md     <- audited 2026-09-04
├── level-2-phone.md + level-2-phone.audit.md    <- audited 2026-09-04
├── level-3-power.md + level-3-power.audit.md    <- audited 2026-09-04
├── level-4-security.md + level-4-security.audit.md <- audited 2026-09-04
└── level-5-phd.md   (no audit file — content owned elsewhere)

openspec/changes/add-level-page-specs/
├── .openspec.yaml
├── proposal.md / design.md / tasks.md
└── specs/site/level-{1,2,3,4,5}/spec.md      <- one per page
```

## Spec shape (per page)

Each `spec.md` follows the file's shape in the existing
`add-container-framework` change:

- `## Purpose` — what the page is for and who reads it.
- `## ADDED Requirements` — a small set of normative requirements, each with
  scenarios, covering:
  - **Audience & frame**: the page targets its named audience and uses the
    level's honesty frame (GREEN/RED/PATH callouts).
  - **Sourcing rule**: every claim carries a footnote resolved against the
    pinned tag `REF` in `scripts/build-matrix.py` (never `main`); a checked
    build (`TILLANDSIAS_CLONE=...`) must pass before publish.
  - **Editorial rules** pulled from `docs/matrix/README.md` (every RED has a
    PATH; no internal identifiers in prose; footnotes are repo-relative or
    external URLs).
  - **Ownership** (level 5 only): the explanation is owned by a separate
    content owner; this spec does not authorize rewriting it.

## Level-5 boundary

Per the audit scope, level 5 is *not owned* by this work. Its spec still
exists (so every page has one, and changes to it can be tracked) but records:
the formal/mathematical content is owned elsewhere; this change neither
rewrites nor annotates it; future edits to that page must be driven by its
owner.

## No output change

The five new specs and four audit files are not inputs to
`scripts/build-matrix.py`, so `var/html/index.html` must rebuild byte-identical.
Verified during implementation (see tasks).