## 1. Deltas (each verified against the checkouts before applying)

- [x] 1.1 D1 — "two of the three properties — commutativity and idempotence —
      are tested by name[^34]" (fragments.rs at v56.9.2.1 has no associativity test)
- [x] 1.2 D2 — monotonicity PATH sentence + `[^41]`
      obligation_props.rs#L172-L219 @v56.9.5.1
- [x] 1.3 D3 — coordinates PATH sentence + `[^42]`
      check-requirement-ids.sh#L5-L35 @v56.9.5.1
- [x] 1.4 D4 — scorer PATH sentence + `[^43]` local-ci.sh#L538-L563 @v56.9.5.1
- [x] 1.5 D5 — denominator PATH sentence + `[^44]` obligation.rs#L620-L638 @v56.9.5.1
- [x] 1.6 D6 — strong-law RED/PATH and Verdict left untouched (checked, no edit)
- [x] 1.7 D7 — verbatim quote under each of the 28 in-repo footnotes, from v56.9.2.1

## 2. Verification

- [x] 2.1 Checked build with both checkouts present; level-5 line:
      `level-5-phd        44 footnotes, 32 quoted, checked at v56.9.2.1`
      — no BROKEN target, no `!` warning for this level
- [x] 2.2 `git diff -- docs/matrix/level-5-phd.md` reviewed: every hunk is one of D1–D7
- [x] 2.3 `openspec validate --changes` passes (it required a delta spec, so the
      smallest one was added: `specs/site/level-5/spec.md`, one ADDED requirement
      describing the delta record itself) — `✓ change/level-5-stable-pin-deltas`,
      `Totals: 3 passed, 0 failed (3 items)`
