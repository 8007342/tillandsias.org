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
- [x] 1.8 D2–D5 wording corrected 2026-09-05, page and `proposal.md` together:
      the fixes landed on trunk on 2026-09-03 and reached the daily channel in
      v56.9.4.1, cut 2026-09-04 — no release was cut on 2026-09-03 (release
      ledger at v56.9.5.1, `README.md`, rows for v56.9.4.1 and v56.9.2.1) — and
      D5's closing clause is again "still no normalisation rule is recorded",
      the wording its delta records

## 2. Verification

- [x] 2.1 Checked build with both checkouts present; level-5 line:
      `level-5-phd        44 footnotes, 32 quoted, checked at v56.9.2.1`
      — no BROKEN target, no `!` warning for this level
- [x] 2.2 `git diff -- docs/matrix/level-5-phd.md` reviewed: every hunk is one
      of D1–D7 or of the 1.8 correction; the title edit that predates this
      record is recorded in the level's audit annotation, not here
- [x] 2.3 `openspec validate --changes` passes (it required a delta spec, so the
      smallest one was added: `specs/site/level-5/spec.md`, one ADDED requirement
      describing the delta record itself) — `✓ change/level-5-stable-pin-deltas`,
      `Totals: 3 passed, 0 failed (3 items)`

## 3. Proposed deltas, not applied (clause-level sourcing)

These two are new deltas, not corrections to a landed one, so they wait for the
operator rather than riding along with this change.

- [ ] 3.1 D8 (proposed) — the D4 PATH sentence makes three daily-channel
      claims and carries one footnote, `[^43]`, whose range
      (`scripts/local-ci.sh#L538-L563 @v56.9.5.1`) covers only the first, the
      scorer handing its weights to the model. Either give the gate clause its
      own `@v56.9.5.1` footnote at
      `scripts/check-scorable-obligation-added.sh#L4-L12`, quoting verbatim
      "check-scorable-obligation-added.sh — refuse a NEWLY FILED packet that
      carries nothing the centicolon scorer can read, and refuse it as a GATE
      rather than asking politely.", and cite the backfill fraction to the same
      file's `#L20-L22` ("MEASURED (977-3dee, same day): of 563 packets, 112
      carry a verifiable_closure and only 25 name a litmus test. Retroactive
      coverage came to 2.6%.") — or drop the parenthetical. Both claims are
      true; what is missing is the citation.
- [ ] 3.2 D9 (proposed) — the D5 PATH's clause "and the script prints that
      label" is the one D5 rests on, and `[^44]`
      (`crates/tillandsias-plan/src/obligation.rs#L620-L638 @v56.9.5.1`) is the
      `Regime` enum: it evidences the labelling, not the printing. Add a fifth
      `@v56.9.5.1` footnote at `scripts/local-ci.sh#L591-L596`, quoting
      verbatim "THE REGIME IS REPORTED, NOT IMPLIED. Outside the monotone band
      a rise or fall must not be read as progress or regress, and a consumer
      that only sees the number has no way to know." — the comment above the
      `if [[ "$cc_regime" != monotone ]]` branch whose `echo` prints
      `note:local-ci:centicolon-regime:… — this score is NOT comparable with
      the previous run`.
