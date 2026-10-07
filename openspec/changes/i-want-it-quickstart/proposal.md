## Why

The **I want it!** page (`#install`, landed in d73d0e5) shows the three one-line
installers and, once screenshots exist, a desktop gallery. It does not show what
happens *after* the line is pasted. The owner's ask is to make the smallness of
the ramp-up visible rather than to document it: after a curl install, someone
points a phone at a QR code in the terminal, installs the Tillandsias GitHub App
on the repositories it may use, then prompts. Four beats, one picture each, as
little copy as a caption. The point of the section is "this is all it takes",
so thoroughness is the failure mode here, not the goal.

A visitor on a Mac should see the Mac installer and the Mac menu bar; a visitor
on Windows the Windows installer and the notification area; a visitor on Linux a
Linux tray. The page already carries all three commands; what is missing is
picking the visitor's own and showing the matching pictures.

## What Changes

- A **quickstart storyboard** on the I want it! page, under the install strip:
  exactly four steps, **Paste → Scan → Authorize → Prompt**, each a tiny
  headline, one short sentence, and one image. Scan is the GitHub device flow
  (a QR code in the terminal pointing at `https://github.com/login/device`);
  Authorize is installing the [Tillandsias GitHub App](https://github.com/apps/tillandsias)
  and choosing its repositories, which the device flow alone does not do
  (owner's decision, 2026-10-07). The copy is instructions, not claims, and every
  runtime fact in it is verified against the stable pin (recorded in
  `design.md`).
- An **OS switcher** (Linux · macOS · Windows) above the install strip. It is a
  radio group, so it works with no script; CSS shows the chosen system's install
  row as the highlighted one and the storyboard images for that system. All
  three install commands stay visible and copyable regardless of the choice.
- **Visitor OS detection** in the browser (`navigator.userAgentData.platform`,
  falling back to `navigator.userAgent`) pre-selects the switcher. With no
  script, Linux is pre-selected and nothing is hidden that a reader needs.
- A **placeholder convention** for the storyboard's images: files under
  `var/html/assets/screenshots/quickstart/<os>-<step>.(png|webp|jpg)`, resolved
  at build time with a small fallback chain; an absent file renders a labelled,
  dashed placeholder frame ("screenshot to come · macOS menu bar") in the site's
  own placeholder style. Placeholders are allowed on the live site: the owner
  asked for them, they say what they are, and screenshots land one file at a
  time without a code change (the same contract the gallery already has).
- The page's lede is reworded to name the four beats.

## Capabilities

### New Capabilities

- `site/install`: the I want it! page — the install strip, the OS switcher and
  visitor-OS pre-selection, the four-step storyboard with its honesty rule and
  placeholder convention, and the file-driven gallery that d73d0e5 added without
  a spec. The page existed before this change; the spec is written to cover it
  as it will be after this change.

### Modified Capabilities

- None. The `site/navigation` spec (delta in `slides-presentation`) still says
  four pages in a fixed order and is already stale against the seven-entry menu
  on the built page; reconciling it is a separate change and is recorded as a
  finding in `plan/i-want-it-page.md`, not fixed here.

## Impact

- `scripts/build-matrix.py`: a `QUICKSTART` data table beside `SCREENSHOTS`, a
  resolver for the per-OS image files, markup changes inside `install_view()`
  (the install rows gain an OS slug), ~40 lines of CSS reusing the `.s-ph`
  placeholder look and the `ins-*` tokens, and ~10 lines of JS for detection.
- `var/html/index.html`: regenerated (committed alongside, as always).
- `var/html/assets/screenshots/quickstart/`: a new directory the owner fills
  with up to twelve screenshots (three systems × four steps; the `authorize`
  step is GitHub's page and will normally be one `any-authorize` file); none
  are required for the build to pass.
- No new external fetch, no new library, no change to the menu, the levels, the
  footnote machinery or the gallery's behaviour.
- Non-goals: a full tutorial, troubleshooting, the `--channel`/reset notes
  (already covered by the existing install note), detecting the Linux desktop
  environment (not available to a browser), video or animation.
