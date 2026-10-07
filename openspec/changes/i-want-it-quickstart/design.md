# Design: i-want-it-quickstart

## Overview

Everything lives inside the existing `view-install` section, built by
`install_view()` in `scripts/build-matrix.py`. The page is static and generated,
so every per-OS variant ships in the markup; the browser only chooses which one
to show. One piece of state, a radio group, drives both the highlighted install
row and the visible storyboard images. The script's only job is to tick the
right radio for the visitor; without it the page is complete, just not
personalised.

```
scripts/build-matrix.py      EDITED  — QUICKSTART table, quickstart_shot()
                                       resolver, install_view() markup,
                                       CSS (.qs-*), one small JS block
var/html/index.html          REGENERATED
var/html/assets/screenshots/quickstart/   NEW dir — <os>-<step>.<ext>
```

## The story, and what it rests on

Four steps, fixed by the owner's brief (three in the first brief; the owner
added **Authorize** on 2026-10-07 after the first implementation landed in
c80c0a1). Each sentence is an instruction, and every runtime fact inside it was
checked against the stable pin (`~/.cache/tillandsias-org/clones/v56.9.27.2`)
on 2026-10-07:

| # | Headline | Sentence (max one) | Rests on (v56.9.27.2) |
|---|---|---|---|
| 1 | **Paste** | Run the line above. When it finishes, a Tillandsias icon sits in your tray. | Runtime `README.md:154-156`: "The installer launches the tray automatically. A tray icon appears in your system menu bar / notification area." |
| 2 | **Scan** | Choose GitHub login from that icon, point your phone at the QR code in the terminal and confirm the code at github.com/login/device. | `openspec/specs/tray-ux/spec.md:92` lists the `GitHub login` item when not authenticated; `crates/tillandsias-headless/src/main.rs:10829-10836` renders a terminal QR of `{verification_uri}?user_code={code}` and prints "Scan this QR code with your mobile phone to complete GitHub login" / "Or in any browser, visit: …" (`render_terminal_qr` at `:10600`); `openspec/specs/gh-auth-script/spec.md:152` requires the QR to contain `https://github.com/login/device?user_code=<user_code>`; the Windows tray's wrapper launches `tillandsias-headless --github-login` (`crates/tillandsias-windows-tray/src/main.rs:848`); macOS drives the same guest flow via `tillandsias-tray --github-login` (`crates/tillandsias-macos-tray/src/diagnose.rs:1918-1926`). "Confirm the code" is chosen because the URL already carries it: the visitor confirms on GitHub's page rather than types. |
| 3 | **Authorize** | Install the [Tillandsias GitHub App](https://github.com/apps/tillandsias) and choose which repositories it can use. | Owner's decision (2026-10-07): the device flow logs the person in as the App but does not install the App or pick repositories, so that is the step the page must show. `crates/tillandsias-headless/src/main.rs:10591-10592` names the App the flow belongs to ("GitHub App Client ID for Tillandsias … App ID: 5081125"). The install page is GitHub's own, not in the release, so the sentence says only what GitHub's App install page offers (choose repositories) and nothing about the App's permissions. |
| 4 | **Prompt** | Pick a project from the same icon and start typing. | `openspec/specs/simplified-tray-ux/spec.md:108`: OpenCode "opens an interactive session inside the forge container" from a project's submenu; runtime `README.md:175` shows `--prompt`. |

Step 3 is the one sentence allowed a link (to the App's page on GitHub); it is
rendered by `qs_text()` from a single `[label](https://…)` in the step data, so
the sentence stays a string and the escaping stays in one place.

Wording rules the copy obeys (from the brief and the site's own rules): no
internals vocabulary (VM, WSL, container, vault, forge) in the visitor-facing
sentence; no present-tense statement of a plan; nothing stronger than the cited
line. The citations are kept in the generator as a non-rendered `source` field
on each step (the same pattern as Slides' `draws_on`), so the weekly
`update-website` re-verification has something to check against the next pin.

Honesty note. The `site/navigation` delta says non-level pages may not state
something about the runtime a level page has not established. Level 3 already
establishes GitHub Login on the host (`docs/matrix/level-3-power.md:85`); the QR
specifics are not on any level. The storyboard sentences are imperative
instructions whose facts are cited above and in the source, which is the
weakest form of claim the page can make while still being useful; the spec for
`site/install` writes that rule down explicitly rather than borrowing the level
machinery (footnote lists would defeat the "look how small this is" purpose).
Step 3 is the one sentence whose fact lives outside the release (GitHub's App
install page); it rests on the owner's recorded decision and claims nothing
about permissions, only that repositories are chosen there.

## Markup

Inside `view-install`'s `.wrap`, after the `view-h`/`view-lede`:

```html
<div class="qs" id="quickstart">
  <input class="sr" type="radio" name="qs-os" id="qs-linux"   value="linux" checked>
  <input class="sr" type="radio" name="qs-os" id="qs-macos"   value="macos">
  <input class="sr" type="radio" name="qs-os" id="qs-windows" value="windows">
  <div class="qs-os" role="group" aria-label="Your system">
    <label for="qs-linux">Linux</label>
    <label for="qs-macos">macOS</label>
    <label for="qs-windows">Windows</label>
  </div>
  <div class="install-strip"><div class="install" aria-label="Install">
    <div class="ins-row" data-os="linux">…existing row…</div>
    <div class="ins-row" data-os="macos">…</div>
    <div class="ins-row" data-os="windows">…</div>
    <p class="ins-note">…unchanged…</p>
  </div></div>
  <ol class="qs-steps">
    <li class="qs-step">
      <h3 class="qs-h"><span class="qs-n" aria-hidden="true">1</span>Paste</h3>
      <p class="qs-t">Run the line above. When it finishes, a Tillandsias icon sits in your tray.</p>
      <figure class="qs-shot" data-os="linux"><img src="assets/screenshots/quickstart/linux-install.png" alt="A Linux terminal after the installer finished, with the Tillandsias icon in the top bar" loading="lazy"></figure>
      <figure class="qs-shot" data-os="macos"><div class="qs-ph" role="img" aria-label="Screenshot to come: macOS menu bar with the Tillandsias icon"><span class="qs-ph-k">screenshot to come</span><span class="qs-ph-t">macOS menu bar</span></div></figure>
      <figure class="qs-shot" data-os="windows">…</figure>
    </li>
    …steps 2, 3 and 4 (step 3's sentence carries the one <a> to github.com/apps/tillandsias)…
  </ol>
</div>
…existing gallery (<h3 class="shots-h">On your desktop</h3> …) unchanged…
```

Why this shape:

- The three radios are **direct children of `.qs`** so the general-sibling
  combinator reaches everything that depends on them: `#qs-macos:checked ~
  .install-strip .ins-row[data-os=macos]` and `#qs-macos:checked ~ .qs-steps
  .qs-shot[data-os=macos]`. No `:has()`, so it works on every browser the site
  already supports.
- Radios are `.sr` (the site's existing visually-hidden class), not
  `display:none`, so they stay focusable: the group is operable with arrow keys
  and the labels are the visible segmented control. Focus is drawn on the
  label: `.qs > input:focus-visible ~ .qs-os label[for=<id>]`, three one-line
  rules.
- Steps are an `<ol>` so a screen reader announces "list, four items" and the
  numbers are real; the visible `.qs-n` numeral is `aria-hidden`.
- Hidden variants are `display:none`, so assistive tech reads exactly one image
  or placeholder per step. `loading="lazy"` on every `<img>` keeps the twelve
  possible images from loading eagerly.
- The install rows gain `data-os` and nothing else changes about them; the copy
  buttons keep working unmodified.

Linux is the no-script default (`checked` in the markup): it is the first row
today and the audience the levels are written for. Nothing is unreachable in
that state — the other two commands are visible, and the switcher is plain
radios.

## CSS

New rules, kept near the `ins-*` block (~40 lines):

- `.qs-os`: inline segmented control; labels in `var(--mono)` 11px uppercase
  like `.ins-os`, border `var(--line)`, radius 7px like `.ins-box`; the checked
  state is drawn with `#qs-linux:checked ~ .qs-os label[for=qs-linux]{…}` × 3
  (color `var(--ink)`, border-color `var(--leaf-dim)`).
- Install row emphasis: the matching row's `.ins-box` gets
  `border-color:var(--leaf-dim)` and its `.ins-os` gets `color:var(--leaf)`; the
  other rows are left as they are (not dimmed, all three remain readable).
- `.qs-steps`: `display:grid; grid-template-columns:repeat(4,1fr); gap:18px;
  margin:28px 0 8px; padding:0; list-style:none` — two columns in the existing
  `@media (max-width:900px)` block, one column under `@media (max-width:760px)`.
- `.qs-h`: 15px/600 with the numeral in `var(--leaf)` mono; `.qs-t`: 14px
  `var(--ink-dim)`, `max-width:36ch`; `.qs-t a{color:inherit}` like `.ins-note a`.
- `.qs-shot`: `margin:10px 0 0; display:none`, shown by the radio rule; `img`
  `display:block;width:100%;height:auto;border:1px solid var(--line);
  border-radius:9px;background:var(--bg-2)`.
- `.qs-ph`: the placeholder — same recipe as `.s-ph` (dashed `var(--line-2)`
  border, radius 9px, faint background, `var(--ink-faint)`), plus
  `aspect-ratio:16/10; display:flex; flex-direction:column; align-items:center;
  justify-content:center; text-align:center`, so it occupies the space the
  screenshot will. `.qs-ph-k` reuses `.s-ph-k`'s look (10.5px mono uppercase
  kicker); `.qs-ph-t` is the human label ("macOS menu bar").
- `body.is-accessible` additions: `.qs-t` joins the enlarged-body selector
  list; the focus ring already applies via the global `:focus-visible` rule.

## Script

One IIFE next to the copy-button block (~10 lines), no dependencies:

```js
(function(){
  var p = ((navigator.userAgentData && navigator.userAgentData.platform) || navigator.userAgent || '').toLowerCase();
  var os = /mac|iphone|ipad|ipod/.test(p) ? 'macos'
         : /win/.test(p) ? 'windows'
         : /linux|android|x11|cros/.test(p) ? 'linux' : null;
  var r = os && document.getElementById('qs-' + os);
  if (r) r.checked = true;
})();
```

Decisions baked in: mac/iOS is tested before `win` (nothing in a Mac or Windows
string collides, but order makes the intent plain); iOS visitors get the macOS
story and Android visitors the Linux one, which is a guess the page never states
(it does not say "you can install this on your phone"); an unrecognised platform
leaves the markup default alone. The choice is not persisted anywhere, so there
is no storage to reason about; a manual switch lasts for the page view. Nothing
runs if the elements are absent, so other views are unaffected.

## Placeholder and asset convention

Directory: `var/html/assets/screenshots/quickstart/`. File name:
`<os>-<step>.<ext>`, with `<os>` ∈ `linux | macos | windows`, `<step>` ∈
`install | scan | authorize | prompt`, `<ext>` tried in the order `png, webp,
jpg` (the same order the gallery uses). The `authorize` scene is GitHub's page
in a browser and so OS-independent; `any-authorize.<ext>` is its expected form.

Resolution at build time, per (os, step), first hit wins:

1. `<os>-<step>` — the exact shot.
2. For `linux` only: `gnome-<step>`, `kde-<step>`, `cosmic-<step>` — a
   desktop-specific Linux shot stands in for the generic one, since a browser
   cannot tell the visitor's desktop environment. The gallery below the
   storyboard still shows all three desktops.
3. `any-<step>` — a system-neutral shot (steps 2 to 4 may genuinely look the
   same everywhere: a phone over a QR code, GitHub's install page, a prompt
   being typed).
4. The labelled placeholder.

The resolver is a small function, `quickstart_shot(os, step) -> (src, alt) |
None`, driven by a `QUICKSTART_FALLBACK = {"linux": ("gnome", "kde", "cosmic")}`
table and `QUICKSTART_ANY = "any"`. Alt text comes from the step's per-OS label
table (`"macOS menu bar with the Tillandsias icon"`), prefixed by the step's
scene, so a real image and its placeholder describe the same thing.

Placeholders on the live site are **acceptable**, decided here: the owner asked
for them, they are labelled as placeholders in the site's own placeholder idiom
(`.s-ph` on Slides already does this in production), and they make no claim.
The gallery's hide-when-empty rule is unchanged; the storyboard is the one
place a frame is shown before its picture exists, because the frame itself
carries the point (four beats).

## Data in the generator

```python
QUICKSTART_OS = [("linux", "Linux"), ("macos", "macOS"), ("windows", "Windows")]
QUICKSTART = [
    # step, headline, sentence, {os: scene label}, source (not rendered)
    ("install", "Paste",
     "Run the line above. When it finishes, a Tillandsias icon sits in your tray.",
     {"linux": "Linux top bar with the Tillandsias icon",
      "macos": "macOS menu bar with the Tillandsias icon",
      "windows": "Windows notification area with the Tillandsias icon"},
     "v56.9.27.2 README.md:154-156"),
    ("scan", "Scan",
     "Choose GitHub login from that icon, point your phone at the QR code in the "
     "terminal and confirm the code at github.com/login/device.",
     {...}, "v56.9.27.2 tray-ux/spec.md:92; headless main.rs:10829-10836; gh-auth-script/spec.md:152"),
    ("authorize", "Authorize",
     "Install the [Tillandsias GitHub App](https://github.com/apps/tillandsias) and "
     "choose which repositories it can use.",
     {...}, "owner decision 2026-10-07; headless main.rs:10591-10592 (App ID 5081125)"),
    ("prompt", "Prompt",
     "Pick a project from the same icon and start typing.",
     {...}, "v56.9.27.2 simplified-tray-ux/spec.md:108; README.md:175"),
]
```

`INSTALL` gains a slug as its first element, `("linux", "Linux", "curl …")`, so
the rows and the switcher share one key; `build()`'s row template reads it.
`install_view()` receives the rows as now and wraps them as shown above.

## Determinism and the hook

The build stays a pure function of the sources plus the asset directory, as the
gallery already is: rebuild with the same files and the bytes match. The
pre-commit hook rebuilds and refuses a stale `var/html/index.html`, so the
implementer commits the generator and the page together.

## Open questions (recorded, not blocking)

1. **Where the QR code appears on each OS.** RESOLVED 2026-10-07 by the owner:
   the QR code is shown in a terminal and points at
   `https://github.com/login/device` (GitHub device flow), on every OS. The
   step-2 sentence and scene labels name the terminal; the code agrees
   (`main.rs:10829-10836`, `gh-auth-script/spec.md:152`).
   `simplified-tray-ux/spec.md:191` ("opens the GitHub OAuth flow in the
   system's default browser") describes a different surface and is not what
   the page shows.
2. **Does the stable installer always leave the tray running** (step 1's
   sentence)? Cited from the runtime README, not from a level page; the
   `update-website` pass should confirm against the installer source at the
   next pin and the sentence should weaken to "open Tillandsias" if not.
3. **Navigation spec drift.** The four-page `site/navigation` delta does not
   describe the seven-entry menu that ships. Out of scope; noted in
   `plan/i-want-it-page.md`.
