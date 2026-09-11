## 1. Change scaffolding

- [x] 1.1 Create change directory `openspec/changes/slides-presentation/` with
      `.openspec.yaml` (schema `spec-driven`, created 2026-09-11; the date is
      quoted so the push hook's YAML `safe_load` accepts it)
- [x] 1.2 Write `proposal.md`, `design.md`, `tasks.md`
- [x] 1.3 Create delta spec directory `specs/site/navigation/` (modified
      capability) and new capability directory `specs/site/slides/`

## 2. Specs

- [x] 2.1 `specs/site/slides/spec.md` — new capability: the deck page's
      purpose, the one-slide-at-a-time mechanism with counter and deep links,
      the ship-inline contract, the drawing-on honesty line, labelled
      placeholders, and the three-slide story ordering
- [x] 2.2 `specs/site/navigation/spec.md` — delta: three pages → four, Slides in
      the menu order after Live progress, the uncited-claim and sentence-shape
      rules widened to Slides, Home's onward links gain Slides

## 3. Deck source

- [ ] 3.1 `scripts/slides.py` — the deck as data: three slides (thesis,
      pillars, mechanism), each with label, eyebrow, title, blocks, and a
      `draws_on` line where substantive; placeholder helpers for un-written
      regions
- [ ] 3.2 Placeholders in the deck draw no uncited claim: every block not yet
      established on a level is labelled "content to come" and makes no claim
      itself

## 4. Generator

- [ ] 4.1 `scripts/build-matrix.py` — `slides_view()` renderer (deck frame +
      controls + header), `__SLIDES__` placeholder in the `TEMPLATE`, and the
      `build()` insertion
- [ ] 4.2 Drawer gains the fourth entry `<button class="nav" data-go="view-slides">`
      after Live progress; `fromHash()` gains `slides` and `slides-N`
- [ ] 4.3 Deck CSS in the `TEMPLATE` `<style>` block: `.deck`, `.deck-frame`,
      `.slide`, counter, rail, prev/next controls, labelled-placeholder chip;
      responsive stacking of the pillars cards in the deck
- [ ] 4.4 Deck JS IIFE `deck()`: one slide on, counter/rail update, prev/next
      disabled at the ends (no wrap), arrow/space/home/end keys when the slides
      view is active, deep links `#slides` / `#slides-N` with clamping and URL
      correction, and back-button behaviour via `hashchange`
- [ ] 4.5 No regressions: copy-to-clipboard, footnotes, menu and tabs still
      behave; keyboard focus and the `#slides-N` hash never collide with level
      hashes

## 5. Verification

- [ ] 5.1 `python3 scripts/build-matrix.py` succeeds and writes
      `var/html/index.html`
- [ ] 5.2 Determinism check: `sha256sum` the committed page, rebuild, and the
      two hashes are equal when the deck source is unmodified
- [ ] 5.3 Manual smoke test, recorded here: menu shows five control surfaces
      unchanged behaviour, Slides lists fourth and marks current; deck shows one
      slide at a time; prev/next and arrow keys walk the deck; the counter reads
      N / 3; `#slides-2` opens slide two; a link past the last slide clamps;
      back button undoes a change; each slide carries its "drawing on" line
      where substantive and a labelled placeholder where content is to come
- [ ] 5.4 `openspec validate --changes` passes for this change (run with the
      CLI; if the CLI is absent on this host, record that and note it as a
      finding)

## 6. After this change

- [ ] 6.1 The pretty content — figures, transitions, animations inside each
      slide — is a later change on top of this mechanism, gated by the same
      honesty rules
- [ ] 6.2 Balance the drawer capsule: nothing about Slides leaks into the level
      tabs or the footer