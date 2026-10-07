## Purpose

**I want it!** is the page a visitor opens when they want Tillandsias on their
own machine. It carries the three one-line installers, a four-step storyboard
showing how little comes after the line, and a gallery of the desktop once
screenshots exist. Its job is to make the ramp-up look as small as it is: the
page is a storyboard, not a manual. Thoroughness belongs on the levels; here a
sentence that can be cut should be.

## ADDED Requirements

### Requirement: The install strip carries all three commands at all times
The page MUST show the Linux, macOS and Windows install commands, each copyable
with one control, and MUST NOT hide any of them for any visitor or selection.
Selecting a system MUST emphasise that system's command without removing or
reordering the others.

#### Scenario: A visitor on one system wants another system's command
- **WHEN** macOS is selected and the visitor wants the Windows line
- **THEN** the Windows line is on the page, readable and copyable, without
  changing the selection

### Requirement: A system is selected, by the visitor's browser or by hand
The page MUST offer a visible switcher with exactly the choices **Linux**,
**macOS** and **Windows**, operable by pointer and by keyboard, and MUST
pre-select the visitor's system when the browser can tell it: the user-agent
client hints platform first, the user-agent string otherwise. With no script the
page MUST still be complete: one system is selected in the markup, the switcher
still works, and every command and every step is present. The selection MUST
NOT be stored anywhere, and the page MUST NOT state what it detected as a fact
about the visitor.

#### Scenario: A Mac visitor opens the page
- **WHEN** a browser reporting a Macintosh platform opens the page with script
- **THEN** macOS is selected, the macOS command is emphasised and the storyboard
  shows the macOS pictures

#### Scenario: The browser says nothing useful
- **WHEN** neither client hints nor the user-agent string names a known system
- **THEN** the markup's default selection stands and nothing else changes

#### Scenario: No script runs
- **WHEN** a browser without script opens the page
- **THEN** the default system is selected, the three commands are visible, and
  the switcher changes the emphasised command and the pictures

#### Scenario: The visitor overrides the guess
- **WHEN** the visitor picks a different system in the switcher
- **THEN** the page follows that choice for the rest of the view and does not
  revert

### Requirement: Four steps, one picture each, almost no words
The page MUST show the ramp-up as an ordered storyboard of exactly four steps,
**Paste**, **Scan**, **Authorize**, **Prompt**, in that order: paste the
install line; scan the QR code the GitHub login shows in the terminal, which
leads to `https://github.com/login/device`; install the Tillandsias GitHub App
(`https://github.com/apps/tillandsias`) and choose the repositories it may use,
since the device flow alone does not do that; prompt. Each step MUST carry a
headline of one word, at most one sentence, and exactly one picture for the
selected system. Only the Authorize sentence MAY carry a link, and only to the
App's page on GitHub. The sentences MUST be instructions, MUST NOT use
internals vocabulary (virtual machine, WSL, container, vault, forge, enclave),
MUST NOT state a planned capability in the present tense, and MUST NOT describe
the App's permissions beyond that repositories are chosen. The storyboard MUST
NOT grow a fifth step, a troubleshooting note or a sub-list without a change to
this spec.

#### Scenario: A reader scans the page
- **WHEN** the page is shown on a desktop width
- **THEN** the four steps sit side by side under the install strip, each with
  its number, its one word, its one sentence and one picture or placeholder

#### Scenario: A reader is on a phone
- **WHEN** the viewport is about 400px wide
- **THEN** the steps stack in order, nothing scrolls sideways, and each
  picture fits its column

#### Scenario: Someone wants to add a caveat
- **WHEN** an editor wants a note about channels, resets or a failure mode in
  the storyboard
- **THEN** it goes in the existing install note or on a level, not in a step

### Requirement: Every storyboard sentence is backed by the stable release
Each step's sentence MUST rest on a cited location in the Tillandsias release
the site currently pins, or, where the fact lives outside the release (GitHub's
own App install page), on a decision recorded in the change's design, and that
citation MUST be recorded in the generator's step data (not rendered). A sentence whose citation no longer holds at a pin
bump MUST be weakened or removed with the bump. The storyboard MUST NOT carry
footnote machinery; the citation lives in the source.

#### Scenario: The pin moves
- **WHEN** the site's stable pin is bumped and a step's cited line is gone or
  says something weaker
- **THEN** the sentence is reworded to what the new pin supports, or the step
  shows only its headline and picture

### Requirement: Pictures are files, placeholders are labelled
The storyboard's pictures MUST be read at build time from
`var/html/assets/screenshots/quickstart/<os>-<step>.<ext>` (`<os>` one of
`linux`, `macos`, `windows`; `<step>` one of `install`, `scan`, `authorize`,
`prompt`; `<ext>` tried as `png`, `webp`, `jpg` in that order). When the exact file is
absent the build MUST try, in order, a Linux desktop-specific file
(`gnome-`, `kde-`, `cosmic-<step>`, Linux only), then a system-neutral
`any-<step>`, and otherwise MUST render a placeholder frame that says it is a
placeholder and names the scene it holds room for, in the site's own
placeholder idiom. A placeholder MUST be acceptable on the published site and
MUST NOT look like a broken image. Adding a picture MUST require no code change,
only the file and a rebuild. Every picture MUST carry alternative text that
describes the scene, and a placeholder MUST be announced as a graphic with the
same description.

#### Scenario: A screenshot lands
- **WHEN** `macos-scan.png` is added to the directory and the page is rebuilt
- **THEN** the macOS step-2 placeholder is replaced by that image and nothing
  else on the page changes

#### Scenario: Only a desktop-specific Linux shot exists
- **WHEN** `kde-install.png` exists and `linux-install.*` does not
- **THEN** the Linux step 1 shows the KDE picture

#### Scenario: Nothing has been captured yet
- **WHEN** the directory is empty or absent
- **THEN** the build succeeds and every step shows a labelled placeholder for
  the selected system

### Requirement: The desktop gallery is file-driven and hidden when empty
Below the storyboard the page MAY show a gallery of the running desktop, one
figure per file found at `var/html/assets/screenshots/<slug>.<ext>` for the
slugs `windows`, `macos`, `gnome`, `kde`, `cosmic`, captioned with the platform
name. The gallery MUST be absent while no such file exists, and MUST NOT show
placeholders.

#### Scenario: The first desktop screenshot lands
- **WHEN** one of the five files is added and the page rebuilt
- **THEN** the gallery heading appears with that one figure

### Requirement: Nothing new is fetched
The page MUST load its pictures from this site's own assets and MUST NOT add a
script, stylesheet, font or image from any other origin; detection MUST use
only what the browser already exposes to the page.

#### Scenario: The page is audited for requests
- **WHEN** the install view is opened and the network log is read
- **THEN** only this site's page and its own asset files appear beyond what the
  other views already load
