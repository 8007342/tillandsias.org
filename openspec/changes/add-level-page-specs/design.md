# Design: add-level-page-specs

## Overview

One delta spec per explanation page plus one shared spec, nothing else. The
specs are declarative contracts for the page's *editors* and *reviewers* — they
do not change how the page is built or rendered. The build pipeline
(`scripts/build-matrix.py`) renders only the files listed in its `LEVELS`
table; the new specs and the `*.audit.md` annotation files live beside the page
sources and are deliberately ignored by the build.

```
docs/matrix/
├── README.md                     (dialect + editorial rules)
├── level-1-five.md  + level-1-five.audit.md        <- dated notes at v56.9.2.1
├── level-2-phone.md + level-2-phone.audit.md       <- dated notes at v56.9.2.1
├── level-3-power.md + level-3-power.audit.md       <- dated notes at v56.9.2.1
├── level-4-security.md + level-4-security.audit.md <- dated notes at v56.9.2.1
└── level-5-phd.md   (no audit file yet; one is allowed and expected)

docs/audit/
└── <YYYY-MM-DD>-<tag>.md         (one record per update-website run;
                                   supersedes the *.audit.md notes for that pin)

openspec/changes/add-level-page-specs/
├── .openspec.yaml
├── proposal.md / design.md / tasks.md
├── specs/site/level-common/spec.md           <- rules shared by every level
└── specs/site/level-{1,2,3,4,5}/spec.md      <- one per page
```

## Spec shape (per page)

Each `spec.md` follows the file's shape in the existing
`add-container-framework` change:

- `## Purpose` — what the page is for and who reads it.
- `## ADDED Requirements` — a small set of normative requirements, each with
  scenarios, covering:
  - **Audience & frame**: the page targets its named audience and uses the
    level's honesty frame (GREEN/RED/PATH callouts).
  - **Content properties**: what the page must state, expressed as properties
    that hold at the level's pin — "the survivorship of each artifact matches
    the pinned code" — never as a verdict on a particular flag.
  - **Level 5 only**: the delta discipline (own pin, every change through an
    OpenSpec change, verdicts re-derived at each pin bump).
- The rules every level shares — per-level pin, checked build with verbatim
  quotes, RED lifecycle, audit records, argument markers — live once in
  `site/level-common` and are not repeated per level.

What a requirement never contains: a dated finding, an order or packet
identifier, a ledger line number, a file count, or a mandated verdict on a
specific flag. Those are work items in `tasks.md` (paths only, no line numbers)
and notes in the dated audit record. A finding is an instance of a property;
the spec states the property.

## Pins are per level

There is no global pin. Each row of the `LEVELS` table in
`scripts/build-matrix.py` carries its own release tag (the row's last field),
and the footnotes of that level resolve against that tag, never `main`. The
page header shows the newest pin across the levels (`SITE_REF`) as the release
the site was last checked against, so a level whose pin lags is visible by
comparing its row with the header. A footnote may point past its own level's
pin only with an explicit `@vTAG` suffix, used on a PATH line that acknowledges
a fix present only in a newer build.

Trial builds: `TILLANDSIAS_PIN_OVERRIDE=vX.Y.Z.B` builds every level as if it
were pinned to that tag without editing `LEVELS`, and `TILLANDSIAS_OUT=<file>`
redirects the output so the published `var/html/index.html` is not
overwritten. With `TILLANDSIAS_CLONE_DIR` holding one checkout per tag, the
broken-target list such a build prints is the exact work list for moving the
levels to that release.

## Pin lifecycle

A summary of steps 4 to 7 of `skills/update-website/SKILL.md`, which is the
procedure; this section only says what the specs assume about it.

1. **See what breaks.** `skills/update-website/scripts/drift-report.sh` prints,
   per level, which cited files changed between its pin and the stable tag, the
   exact broken-target list from a trial build pinned to the stable tag, and how
   many cited files the newest daily has changed. Nothing is edited.
2. **Re-verify and fix, one level at a time.** Following the `audit-site-claims`
   procedure: every broken footnote, every footnote whose cited file changed,
   and every GREEN/RED/PATH in the affected sections. A RED the stable code has
   outrun becomes a past-tense flag or a GREEN; a RED fixed only in a daily
   stays RED and its PATH names the daily; a partial fix says what remains.
3. **Move the pin.** Levels 1 to 4: edit the level's tag in `LEVELS`. Level 5:
   write an OpenSpec change under `openspec/changes/` listing each delta with
   its evidence, and land it only when the operator has approved it
   (see `site/level-5`).
4. **Checked build must pass.** `skills/update-website/scripts/checked-build.sh`
   exits 0 with `ok:checked-build`; it fails on any unresolved target or
   drifted quote of any level whose checkout is present.

The run is then recorded in `docs/audit/<YYYY-MM-DD>-<tag>.md` (step 8), which
supersedes any `*.audit.md` notes written for that pin.

## Level 5

Level 5 is edited in this repository, by the same rules as the other levels
plus the delta discipline `docs/matrix/README.md` already states: its pin is
bumped separately from the others, every change to its text is proposed in an
OpenSpec change under `openspec/changes/` before it lands, and each proposed
delta carries `path#Lstart-Lend` evidence and a verbatim quote at the target
tag. Its verdicts are re-derived at each pin bump, never frozen. Audit
annotations for level 5 are allowed and expected — they are the input to the
proposal. The owner is this repository's operator, who approves each change.

## No output change

The specs and the audit files are not inputs to `scripts/build-matrix.py`, so a
rebuild of `var/html/index.html` from an unchanged `docs/matrix/` produces the
same bytes. The check, the command and its result are recorded in `tasks.md`
3.2.
