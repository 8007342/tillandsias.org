# Workstream: the "I want it!" page and its quickstart storyboard

**Status:** 🟢 **IMPLEMENTED, AWAITING SCREENSHOTS AND A BROWSER PASS** —
OpenSpec change
[`openspec/changes/i-want-it-quickstart/`](../openspec/changes/i-want-it-quickstart/)
designed and implemented 2026-10-07 on branch `work/site-tweaks`; the nine
storyboard frames are placeholders until the owner captures the files in §4;
the browser smoke tests (`tasks.md` §7.5–7.9) still need a real browser.
**Opened:** 2026-10-07
**Owner:** operator (`bulloncito`); design by a forge session, 2026-10-07

---

## 1. What this is

The page at `#install` (menu entry **I want it!**, `install_view()` in
`scripts/build-matrix.py`) landed in d73d0e5 with the three installer lines and
a file-driven desktop gallery. The owner then asked for bare, minimalistic
instructions that *show how small the ramp-up is*: after the curl line, someone
photographs a QR code, then prompts. Three steps, placeholders, and per-OS
variants chosen by the visitor's browser.

The design is in the change's `design.md`; this file holds what must survive a
session: status, open questions, and the asset checklist for the owner.

## 2. Verified facts (how each was checked)

- The QR code is real in the stable pin. `crates/tillandsias-headless/src/main.rs:10832`
  in `~/.cache/tillandsias-org/clones/v56.9.27.2` prints "Scan this QR code
  with your mobile phone to complete GitHub login" (GitHub device flow;
  `render_terminal_qr` at `:10600`). Read 2026-10-07.
- The tray exposes it: `openspec/specs/tray-ux/spec.md:92` (`GitHub login` item
  when not authenticated); Windows wrapper launches
  `tillandsias-headless --github-login` (`crates/tillandsias-windows-tray/src/main.rs:848`);
  macOS `tillandsias-tray --github-login` (`crates/tillandsias-macos-tray/src/diagnose.rs:1918-1926`).
  Same checkout, same date.
- "The installer launches the tray automatically" is the runtime README
  (`README.md:154-156` at the pin), not a level page.
- GitHub Login is already named on a level: `docs/matrix/level-3-power.md:85`.
- The site's installer wrappers (`var/html/install.sh`, `install-macos.sh`,
  `install.ps1`) only dispatch to the release's installer; they print no
  next-step text of their own. Read 2026-10-07.

## 3. Open questions

1. **Which surface shows the QR code on each OS?** Code says a terminal;
   `simplified-tray-ux/spec.md:191` says a browser. The step-2 sentence avoids
   naming either. The screenshots below settle it; adjust the alt text and scene
   labels in `QUICKSTART` once known.
2. **Does the stable installer always leave the tray running?** Cited from the
   runtime README only. Confirm against the installer source at the next
   `update-website` pass; weaken step 1 to "open Tillandsias" if not.
3. **Navigation spec drift (finding, out of scope here).** The `site/navigation`
   delta in `slides-presentation` says four pages in a fixed order; the built
   menu has seven entries (Home, What is it?, I want it!, Live progress,
   CentiColons, Slides, Big Graph). Needs its own change.

## 4. Asset checklist for the owner

Drop files into `var/html/assets/screenshots/quickstart/` and rebuild; no code
change. Names are `<os>-<step>.png` (or `.webp`/`.jpg`). Until a file exists its
frame shows a labelled "screenshot to come" placeholder, which is acceptable on
the live site (decided in the design).

| Step | Scene to capture | linux | macos | windows |
|---|---|---|---|---|
| 1 `install` | Terminal right after the installer finished, with the Tillandsias icon visible in the tray / menu bar / notification area | `linux-install` (or `gnome-`/`kde-`/`cosmic-install`) | `macos-install` | `windows-install` |
| 2 `scan` | A phone held up to the screen, camera on the QR code the GitHub login shows | `linux-scan` | `macos-scan` | `windows-scan` |
| 3 `prompt` | A project opened from the tray, a prompt being typed | `linux-prompt` | `macos-prompt` | `windows-prompt` |

Shortcuts: `any-scan.png` / `any-prompt.png` serve all three systems when the
scene is not OS-specific; a desktop-specific Linux shot (`gnome-…`, `kde-…`,
`cosmic-…`) stands in for `linux-…` when that is absent. Landscape, roughly
16:10, under ~400 KB each (the page is one file; the existing gallery images
are 2–3 MB and should also be shrunk at some point).

The separate desktop gallery still takes `var/html/assets/screenshots/<slug>.png`
for `windows`, `macos`, `gnome`, `kde`, `cosmic` and stays hidden until the
first one lands.

## 5. Session log (append only)

- **2026-10-07** — Design session. Read `install_view`, the gallery, CSS/JS;
  grepped the v56.9.27.2 checkout for QR/pairing/tray and found the GitHub
  device-flow QR (facts in §2). Wrote the OpenSpec change
  `i-want-it-quickstart` (proposal, design, tasks, `site/install` spec) and
  this file. Chose: radio-group switcher so OS selection works without script
  (CSS `:checked ~` rules, no `:has()`); Linux as the no-script default;
  `quickstart/<os>-<step>.<ext>` naming with Linux-desktop and `any-` fallbacks;
  placeholders allowed live. Nothing implemented; committed on
  `work/site-tweaks`, not pushed.
- **2026-10-07** — Implementation session. Built the change as designed:
  `INSTALL` rows keyed by slug (`data-os`), `QUICKSTART`/`QUICKSTART_OS`
  tables with the non-rendered `source` citations, `quickstart_shot()`
  resolver (`<os>-<step>` → `gnome/kde/cosmic-<step>` for Linux → `any-<step>`
  → placeholder; png, webp, jpg), the radio-group switcher and `<ol
  class="qs-steps">` storyboard in `install_view()`, ~45 lines of `.qs-*` CSS
  (reusing the `.s-ph` placeholder recipe, `aspect-ratio:16/10`), the
  10-line detection IIFE, and `var/html/assets/screenshots/quickstart/.gitkeep`.
  Lede now "One line in a terminal, one photo, one prompt." Verified:
  `checked-build.sh` ok, deterministic rebuild, placeholder/fallback paths
  exercised with temporary copies of `fedora-up.png` under each naming
  variant (exact beats desktop stand-in beats `any-`, png beats webp), inline
  JS passes `node --check`, detection regexes checked against sample UA
  strings. Not visually checked: no headless browser on the host. Open for the
  owner: capture the files in §4, run `tasks.md` §7.5–7.9 in a browser.
  Noted: `navigator.userAgentData.platform` reports "Chrome OS" (not "cros"),
  which the regex misses; the outcome is the Linux default either way.
