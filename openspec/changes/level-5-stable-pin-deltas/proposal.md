## Why

Level 5 (`docs/matrix/level-5-phd.md`) stays pinned to the stable release
v56.9.2.1. Its mathematics and its RED flags are accurate at that pin, and the
page moves only in tiny, individually justified deltas. The 2026-09-05
re-verification against the newest daily (v56.9.5.1) found: one statement that
was false even at the stable pin (an associativity test that has never existed),
four shortcomings whose fix landed in the daily channel on 2026-09-03 and is
not yet in the stable channel, and no verbatim quotes under any of the page's
in-repo footnotes. The pin does not move; the page records the daily-channel
facts on its PATH lines, citing them with `@v56.9.5.1` footnotes as the
editorial rules require.

## What Changes

- **D1** — the CRDT paragraph's "and the three properties are tested by
  name[^34]" becomes "and two of the three properties — commutativity and
  idempotence — are tested by name[^34]". Evidence at v56.9.2.1:
  `crates/tillandsias-plan/src/fragments.rs#L2648` and `#L2664` are the only
  named property tests; `grep -i associativ` hits only the doc comment at
  `#L31`.
- **D2** — the monotonicity RED stays; its PATH gains one closing sentence:
  the obligation model and its generative property tests landed in the daily
  channel on 2026-09-03 (release v56.9.4.1), over a committed rule set rather
  than the live validators, and are not yet in the stable channel. New
  footnote `[^41]` at `crates/tillandsias-plan/src/obligation_props.rs#L172-L219
  @v56.9.5.1` (the `proptest!` block: monotone, inflationary, idempotent).
- **D3** — the coordinates RED stays; its PATH gains one sentence: in the daily
  channel, on 2026-09-03, every requirement received a stable random identifier
  and a gate check now refuses a missing or duplicated one; nothing yet computes
  the credit term. New footnote `[^42]` at
  `scripts/check-requirement-ids.sh#L5-L35 @v56.9.5.1`.
- **D4** — the scorer RED's PATH gains one sentence: the three parts of the
  ruling were executed the same day in the daily channel — the shell scorer
  hands its weights to the model, completed work was backfilled where the
  ledger pins the evidence (a small fraction of rows), and a gate refuses new
  obligations the score cannot see. New footnote `[^43]` at
  `scripts/local-ci.sh#L538-L563 @v56.9.5.1` ("THE SCORE COMES FROM THE MODEL").
- **D5** — the denominator RED's PATH gains one sentence: in the daily channel
  the ranking function in code now labels a score whose denominator lost a
  tombstoned obligation as not comparable, and the script prints that label;
  still no normalisation rule is recorded. New footnote `[^44]` at
  `crates/tillandsias-plan/src/obligation.rs#L620-L638 @v56.9.5.1` (the
  `Regime` enum).
- **D6** — the strong-law RED, its PATH and the Verdict section are untouched:
  they are accurate at the stable pin (the correction landed after v56.9.2.1
  and the page already says so; `methodology/philosophy.yaml#L8-L31` at
  v56.9.2.1 still carries the withdrawn wording).
- **D7** — a verbatim quote, on `>` lines, under every in-repo footnote
  ([^1], [^2], [^4], [^5], [^8], [^9], [^10], [^11], [^14], [^15], [^16],
  [^19], [^22], [^24], [^27]–[^40]), each taken from its cited range at
  v56.9.2.1. External references get none. No existing target or label
  changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `site/level-5`: the page's delta record — the four PATH-line sentences, the
  one correction, the four `@v56.9.5.1` footnotes and the twenty-eight quotes
  listed above.

## Impact

- `docs/matrix/level-5-phd.md`: five prose hunks (D1–D5), twenty-eight quote
  lines (D7), four new footnote definitions ([^41]–[^44]).
- `openspec/changes/level-5-stable-pin-deltas/specs/site/level-5/spec.md`: one
  ADDED requirement describing the delta record itself (the validator refuses a
  change with no delta spec).
- `scripts/build-matrix.py`: untouched; level 5 stays pinned at v56.9.2.1.
- Checked build for the level: `level-5-phd 44 footnotes, 32 quoted, checked
  at v56.9.2.1`, no BROKEN target, no `!` warning.
- `var/html/index.html` changes only when the site is next published; this
  change does not publish.
