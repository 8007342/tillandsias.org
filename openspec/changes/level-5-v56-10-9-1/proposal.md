# Refresh level 5 citations for stable v56.10.9.1

## Why

Stable `v56.10.9.1` changed eight of the files level 5 cites:
`crates/tillandsias-plan/src/fragments.rs`,
`crates/tillandsias-plan/src/lua_predicate.rs`, `methodology/convergence.yaml`,
`methodology/proximity.yaml`, `methodology/versioning.yaml`,
`scripts/check-centicolon-ratchet.sh`, `scripts/check-requirement-ids.sh` and
`scripts/local-ci.sh`. Sixteen footnotes cite those files. Two of the files
were deleted: each shell gate was ported to Lua under `scripts/lua/`. Five
cited spans moved without any change to their text. One footnote label
describes something the new file no longer says.

No GREEN, RED, PATH, PROVEN, PLAUSIBLE or REFUTED flag changes state. No
argument on the page changes. The changes are the seven footnote deltas below
and the pin move. All prose and every other footnote stay as they are.

## What Changes

The pin for `level-5-phd` in `scripts/build-matrix.py` moves from `v56.9.27.2`
to `v56.10.9.1`.

### Mechanical deltas: the span shifted and its text is unchanged

For each of these, `diff` of the old span at `v56.9.27.2` against the new span
at `v56.10.9.1` is empty. Lines were inserted above the span, and nothing
inside it changed.

- **D1 — [^8]** `methodology/convergence.yaml#L470-L472` → `#L502-L504`.
  The `status_channel_policy` block (32 lines) was inserted at L339. Evidence
  `methodology/convergence.yaml#L502-L504 @v56.10.9.1`:
  > is a one-off scope expansion that The Tlatoāni MUST approve every time. Recurring automation (the meta-orchestration loop) MUST NOT self-escalate the bar.
- **D2 — [^30]** `methodology/convergence.yaml#L388-L392` → `#L420-L424`.
  Same insertion. Evidence `methodology/convergence.yaml#L420-L424 @v56.10.9.1`:
  > ratio_constraint: "methodology_complexity / codebase_complexity < 0.15" anti_pattern: > A validation system that requires more code to understand than the code being validated. Red flag: CI validators exceed 5000 lines or require specialized training to understand.
- **D3 — [^34]** `crates/tillandsias-plan/src/fragments.rs#L3086-L3087` →
  `#L3229-L3230`. `inert_fragments`, `with_claim_story`,
  `with_replace_acknowledgement` and a test fixture were added above the span.
  The idempotence test still follows it, at L3245
  (`the_fold_is_idempotent_so_a_half_finished_compaction_is_safe`). Evidence
  `crates/tillandsias-plan/src/fragments.rs#L3229-L3230 @v56.10.9.1`:
  > fn the_fold_is_commutative_the_defining_crdt_property() { Order of arrival must not change the result.
- **D4 — [^35]** `crates/tillandsias-plan/src/fragments.rs#L339-L353` →
  `#L386-L400`. `inert_fragments` (47 lines) was inserted at L218.
  `status_entry_wins` has no hunk in the diff. Evidence
  `crates/tillandsias-plan/src/fragments.rs#L386-L400 @v56.10.9.1`:
  > The closure ladder implemented<completed<verified<done is a monotone lattice: you climb UP freely and move DOWN only through a `falsified` event.
- **D5 — [^46]** `crates/tillandsias-plan/src/lua_predicate.rs#L69-L90` →
  `#L74-L95`. A `#[path = "lua_process.rs"] mod script_process;` (5 lines) was
  inserted at L70. `PredicateClass` and its two verb sets are unchanged.
  Without this delta the old range would still contain the quote, but it would
  also take in the module lines and cut off the `Observing` verb set. Evidence
  `crates/tillandsias-plan/src/lua_predicate.rs#L74-L95 @v56.10.9.1`:
  > Pure: no shell, no clock. Results MAY be cached.

### Retargets: the cited file was ported to Lua

- **D6 — [^48]** `scripts/check-centicolon-ratchet.sh#L4-L115` →
  `scripts/lua/check-centicolon-ratchet.lua#L4-L138`, with a new quote. The
  shell file does not exist at `v56.10.9.1`; the port is order 1528-gxzf. The
  claim still holds, and the label is unchanged:
  - Advisory: the R line goes out through `verdict.advisory`. Per
    `crates/tillandsias-plan/src/script_run.rs#L13 @v56.10.9.1`, that prints
    `<line> (advisory)` and exits 0.
  - Regression comparison: `lost = vanished + down` at L121, and the
    `warn:centicolon-ratchet:lost=` line at L129.
  - Local, untracked snapshot advanced even after a loss: L135 is
    `if snapshot then fs.write(OUT .. "/last.txt", ...)`. It does not depend on
    `lost`. `OUT` defaults to `target/centicolon`, and `/target/` is in
    `.gitignore`.
  - Still wired: `build.sh#L4089` and `scripts/cycle-metrics.sh#L1277`
    (`--no-snapshot`) run the Lua port.

  Old quote, which is gone:
  `ADVISORY (operator ruling 2026-09-26, recorded on 1395-ue3i): it WARNS and never refuses; it always exits 0.`
  New quote, `scripts/lua/check-centicolon-ratchet.lua#L4-L5 @v56.10.9.1`:
  > the advisory CentiColon R line, ported from check-centicolon-ratchet.sh without changing its protocol stdout or status.
- **D7 — [^42]** `scripts/check-requirement-ids.sh#L5-L6` →
  `scripts/lua/check-requirement-ids.lua#L5-L10`, with a new quote and a
  **corrected label**. This one is substantive, but only in the footnote label.
  The shell file does not exist at `v56.10.9.1`; the port is order 1527-v7cy,
  and it runs in `./build.sh --check` (`build.sh#L5183`). The port still
  refuses a missing identifier (`violation:requirement-ids-missing`, L98) and a
  duplicated one (`violation:requirement-ids-duplicated`, L135), and it still
  checks tombstoned specs (L9).

  What changed: the old shell header had a `WHAT IT CANNOT CHECK` paragraph.
  The Lua header does not. For its rationale it says "see the .sh's header",
  and that file no longer exists at this tag. The current label says "and
  states what it cannot check", which is no longer true of the cited file. The
  label becomes: "The gate that refuses a missing or duplicated requirement
  identifier, tombstoned specifications included". The GREEN at the footnote's
  call site keeps its wording: "the guard cannot decide that" is this page's
  own claim, and the port still checks only presence and uniqueness. The
  repository still states the limit, in
  `methodology/proximity.yaml#L58-L65 @v56.10.9.1`:
  "`scripts/lua/check-requirement-ids.lua` enforces presence and uniqueness
  and nothing else". This change does not cite it. Adding a citation is not a
  delta this change proposes.

  Old quote, which is gone:
  `Every spec requirement carries a stable identifier, and no two carry the same one.`
  New quote, `scripts/lua/check-requirement-ids.lua#L8-L9 @v56.10.9.1`:
  > and no identifier appears twice anywhere in the corpus. Tombstoned specs are checked too

### Re-verified, no delta

Each of these cites a changed file. The cited span is byte-identical at both
tags, and the claim it supports still holds at `v56.10.9.1`.

- **[^10]** `methodology/proximity.yaml#L88-L97`. The proximity diff renames
  `scripts/check-requirement-ids.sh` to the `.lua` path at L61 and L82, both
  outside this span. `requirement_has_stable_id: 0.10` is unchanged.
- **[^15]** `methodology/proximity.yaml#L100-L135`. The span is identical, and
  the cap/penalty rollup is unchanged.
- **[^27]** `scripts/local-ci.sh#L413-L418`. Every local-ci hunk is at L1218
  or later. `check_weight` is still at L413 and is still called at L549 and
  L606.
- **[^31]** `crates/tillandsias-plan/src/fragments.rs#L28-L39` and
- **[^33]** `crates/tillandsias-plan/src/fragments.rs#L41-L49`. The module
  header L25–L50 is identical at both tags.
- **[^37]** `methodology/versioning.yaml#L104-L124` and
- **[^39]** `methodology/versioning.yaml#L9-L20`. The versioning diff is at L135
  and later: it amends `main_only_bumps` and adds `monotonic_build_bump`.
  L9–L20 still define Major as "Contract version — breaking changes only".
  The RED at [^39] therefore stands. The new rule does name the live
  `YEAR_FROM_EPOCH.MONTH.DAY.BUILD` counter, so the document now contradicts
  itself rather than only the scheme. That makes the RED sharper, not
  different, and it needs no text.
- **[^43]** `scripts/local-ci.sh#L571-L573` and
- **[^45]** `scripts/local-ci.sh#L624-L624`. Both spans are identical. The
  shell still pipes into `tillandsias-plan score-checks` (L609).

These also still hold at `v56.10.9.1`, checked by grep over `scripts/`,
`build.sh` and `crates/`:

- The complexity-constraint RED still stands. No script or crate references
  `methodology_complexity`, `codebase_complexity` or `ratio_constraint`.
- The CentiColon scorer's RED/PATH pair stands as it is.

## Out of scope

- Footnotes that cite files which did not change. The checked build re-checks
  them at the new pin.
- The external scholarly references, which are unchanged.
- Any change to the page's mathematical claims. No PLAUSIBLE claim is
  upgraded: nothing in `v56.10.9.1` adds a test or argument for a property the
  page marks as unproven. The `lua_predicate.rs` diff hardens the environment
  that cacheable predicates run in. It does not test what an assertion
  asserts, so the paragraph at [^46] stands.

These are checks of source and quotes in the tagged tree. They are not a live
validation of the mathematical model.
