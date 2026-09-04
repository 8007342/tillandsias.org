## 1. Change scaffolding

- [x] 1.1 Create change directory `openspec/changes/add-level-page-specs/` with
      `.openspec.yaml` (schema `spec-driven`, created 2026-09-04)
- [x] 1.2 Write `proposal.md`, `design.md`, `tasks.md`
- [x] 1.3 Create delta spec directories `specs/site/level-{1,2,3,4,5}/`

## 2. Page specs (one per level)

- [x] 2.1 `specs/site/level-1/spec.md` — "Like I'm 5" purpose/content contract
- [x] 2.2 `specs/site/level-2/spec.md` — "I barely understand my phone" contract
- [x] 2.3 `specs/site/level-3/spec.md` — "I'm a power user" contract
- [x] 2.4 `specs/site/level-4/spec.md` — "I'm a Cyber Security expert" contract
- [x] 2.5 `specs/site/level-5/spec.md` — "I'm a PhD / MathWiz / Hacker" contract,
      recording that its explanation is owned outside this audit

## 3. Verification

- [x] 3.1 `openspec validate --changes` passes
- [x] 3.2 `var/html/index.html` rebuilds byte-identical (no output change)
- [ ] 3.3 (optional, on adoption) sync specs to `openspec/specs/site/level-<n>/`
      and archive the change