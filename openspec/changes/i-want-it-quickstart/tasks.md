## 1. Change scaffolding

- [x] 1.1 Create `openspec/changes/i-want-it-quickstart/` with `.openspec.yaml`
      (schema `spec-driven`, created `"2026-10-07"` quoted, as the other changes do)
- [x] 1.2 Write `proposal.md`, `design.md`, `tasks.md`
- [x] 1.3 Write the new capability delta `specs/site/install/spec.md`
- [x] 1.4 Open `plan/i-want-it-page.md` and point to it from `plan/README.md`

## 2. Generator data (`scripts/build-matrix.py`)

- [ ] 2.1 Give each `INSTALL` entry a slug as its first element:
      `("linux", "Linux", …)`, `("macos", "macOS", …)`, `("windows", "Windows", …)`;
      update the row template in `build()` to emit `data-os="<slug>"` on each
      `.ins-row` and keep the copy button markup unchanged
- [ ] 2.2 Add `QUICKSTART_OS`, `QUICKSTART` (three steps: `install`/Paste,
      `scan`/Scan, `prompt`/Prompt, each with the headline, the one sentence,
      a per-OS scene-label dict and a non-rendered `source` string) exactly as
      worded in `design.md`'s table; add `QUICKSTART_DIR = SHOTS / "quickstart"`,
      `QUICKSTART_FALLBACK = {"linux": ("gnome", "kde", "cosmic")}` and
      `QUICKSTART_ANY = "any"`
- [ ] 2.3 Add `quickstart_shot(os, step)` implementing the resolution order
      `<os>-<step>` → Linux desktop fallbacks → `any-<step>` → `None`, trying
      extensions `png, webp, jpg` in that order, returning `(relative src, alt)`

## 3. Markup (`install_view()`)

- [ ] 3.1 Wrap the install strip in `<div class="qs" id="quickstart">` whose
      first children are the three `.sr` radios (`name="qs-os"`,
      ids `qs-linux`/`qs-macos`/`qs-windows`, Linux `checked`), then the
      `.qs-os` label group (`role="group" aria-label="Your system"`)
- [ ] 3.2 Render `<ol class="qs-steps">` with one `<li class="qs-step">` per
      `QUICKSTART` step: `<h3 class="qs-h">` with an `aria-hidden` numeral,
      `<p class="qs-t">`, then three `<figure class="qs-shot" data-os=…>`
      holding either `<img … loading="lazy" alt=…>` or the `.qs-ph` placeholder
      (`role="img"`, `aria-label="Screenshot to come: <scene>"`, kicker
      `screenshot to come`, text = scene label)
- [ ] 3.3 Reword the lede to name the three beats (e.g. "One line in a
      terminal, one photo, one prompt."); leave `INSTALL_NOTE` and the gallery
      untouched
- [ ] 3.4 Escape every string with `html.escape`; no raw user text reaches the
      page

## 4. CSS

- [ ] 4.1 Add the `.qs-os` segmented control, the per-OS `:checked ~` rules
      for label state, install-row emphasis and `.qs-shot` visibility (3 × 3
      rules), and the `input:focus-visible ~ .qs-os label[for=…]` focus ring,
      next to the `ins-*` block
- [ ] 4.2 Add `.qs-steps` (3-column grid), `.qs-h`, `.qs-n`, `.qs-t`,
      `.qs-shot img`, and `.qs-ph`/`.qs-ph-k`/`.qs-ph-t` (same dashed look as
      `.s-ph`, `aspect-ratio:16/10`, centred label)
- [ ] 4.3 In the existing `@media (max-width:760px)` block, stack `.qs-steps`
      to one column and let `.qs-os` wrap
- [ ] 4.4 Add `.qs-t` to the `body.is-accessible` enlarged-copy selector lists

## 5. Script

- [ ] 5.1 Add the detection IIFE from `design.md` beside the copy-button block:
      `navigator.userAgentData.platform` first, `navigator.userAgent` fallback,
      mac/iOS → `macos`, `win` → `windows`, linux/android/x11/cros → `linux`,
      else leave the default; tick `#qs-<os>` if present; no storage

## 6. Assets

- [ ] 6.1 Create `var/html/assets/screenshots/quickstart/` (a `.gitkeep` is
      enough; the build must pass with the directory empty or absent)
- [ ] 6.2 Hand the asset checklist in `plan/i-want-it-page.md` to the owner;
      no screenshot is required for this change to ship

## 7. Build and verification

- [ ] 7.1 `python3 scripts/build-matrix.py` succeeds; then
      `skills/update-website/scripts/checked-build.sh` ends in
      `ok:checked-build`
- [ ] 7.2 Determinism: `sha256sum var/html/index.html`, rebuild, compare —
      equal with unchanged sources and assets
- [ ] 7.3 Placeholder path: with the quickstart directory empty, the page shows
      nine `.qs-ph` frames in the markup and exactly three visible at a time;
      drop one test file (e.g. `macos-scan.png`), rebuild, and only that frame
      becomes an `<img>`; remove the file and rebuild afterwards
- [ ] 7.4 Fallback path: a `gnome-install.png` alone is used for the Linux
      step 1; an `any-scan.png` alone is used for all three systems' step 2
- [ ] 7.5 No-script smoke (`./serve-locally.sh`, JavaScript disabled): Linux is
      selected, all three install commands are visible, the switcher changes
      the highlighted row and the images, the menu's `#install` link still
      opens the view via the hash
- [ ] 7.6 Detection smoke: with devtools device/UA emulation for a Mac and for
      Windows, the matching radio is ticked on load and the matching row is
      emphasised; a manual click overrides it; copy buttons still copy
- [ ] 7.7 Keyboard and screen reader: Tab reaches the radio group, arrow keys
      move the selection with a visible ring on the label; each step reads as
      one list item with one image or one "Screenshot to come" graphic
- [ ] 7.8 Phone width (~400px): steps stack, the switcher wraps, no horizontal
      scroll, images and placeholders fit the column
- [ ] 7.9 Accessible mode (`body.is-accessible`): step copy enlarges with the
      rest of the page; contrast of the placeholder label stays readable
- [ ] 7.10 `openspec validate i-want-it-quickstart --no-interactive` passes
      (record it here if the CLI is unavailable on the host)

## 8. Commit

- [ ] 8.1 Stage `scripts/build-matrix.py`, `var/html/index.html` and the new
      assets directory together on `work/site-tweaks`; commit with the
      agent-commit convention (`git commit -F -` with a quoted heredoc,
      `Agent-Context` trailer with a real `why`, `Co-Authored-By` in the same
      trailer block); the pre-commit hook's rebuild must leave the page unchanged
- [ ] 8.2 Tick the tasks above as they land and append a session-log line to
      `plan/i-want-it-page.md`
