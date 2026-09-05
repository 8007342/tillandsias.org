---
name: update-website
description: Re-verify the five tillandsias.org explanation levels against the newest Tillandsias release, fix what drifted, move the pins, and publish. Run weekly or after a release.
---

# Update the website against the latest release

**Purpose.** Every claim on tillandsias.org is a footnote into the Tillandsias
source at a pinned release. Releases land daily; footnotes drift, fixes land,
and a page that still calls something broken is lying. This skill is the loop
that keeps the pages true. It is also the manual run behind the automation
candidates listed at the end.

**Where you are.** Usually a Tillandsias forge for this repository. There you
can `git push` (through the enclave mirror), clone the runtime repo from GitHub
through the proxy, run the build, and nothing else: no `gh`, no browser, no
access to the runtime repo's mirror. Read `.forge-startup-context.md` and
`plan/README.md` first if this is your first session here.

## Which release the pages describe

The runtime publishes two channels out of one stream. Every daily build is a
GitHub *prerelease*; `/releases/latest`, which the site's three install
commands resolve, moves only when a vetted daily is promoted with the
runtime's `scripts/promote-stable.sh`. The prerelease bit is the channel.

The pages pin the **stable** tag: it is the binary a reader who copies the
install line actually gets, so a RED that is fixed only in a daily is still
true for that reader. The PATH line is where the daily-channel fix is
acknowledged ("fixed in the daily channel on <date>; not yet promoted"), and
the drift report shows exactly which cited files a daily has changed so those
PATH lines can be written from evidence rather than hope.

## The loop

Every step's script prints a verdict on its last line.

1. **Find the channel tags.**
   `skills/update-website/scripts/latest-release.sh` → the stable tag (from
   `/releases/latest` with cache-busting headers, because the enclave proxy
   caches API responses; cross-checked against the newest non-prerelease and
   the runtime's `stable` git tag, warning on stderr when they disagree).
   `latest-release.sh --channel unstable` → the newest daily, over git alone.
2. **Read the pins.** `skills/update-website/scripts/pinned-refs.sh` → one line
   per level, `slug<TAB>tag`.
3. **Fetch checkouts.** `skills/update-website/scripts/fetch-checkouts.sh [tags…]`
   → creates `$TILLANDSIAS_CLONE_DIR/<tag>` for every pinned tag, the stable
   tag and the newest daily (shallow, one worktree per tag, shared object
   store so tags can be diffed). Default dir: `$HOME/.cache/tillandsias-org/clones`,
   on real disk; the forge's `/tmp` is a 256 MB tmpfs and fills at two checkouts.
4. **See what breaks.** `skills/update-website/scripts/drift-report.sh` → for
   each level: which cited files changed between its pin and the stable tag,
   the exact broken-target list (missing path, line range outside the file,
   quote not found) from a trial build pinned to the stable tag, and, for
   information, how many cited files the newest daily has changed. If every
   level already pins the stable tag and nothing is broken it prints
   `ok:up-to-date`; the daily-channel counts still tell you whether any PATH
   lines can be updated. Nothing is edited.
5. **Re-verify and fix, one level at a time.** Follow
   [`audit-site-claims`](../audit-site-claims/SKILL.md) for each level whose
   report is not empty: every broken footnote, every footnote whose cited file
   changed, and every GREEN/RED/PATH in the affected sections. Correct targets,
   quotes and prose in `docs/matrix/<level>.md`. Respect the rules in
   `docs/matrix/README.md`. A RED that the stable code has outrun becomes a
   past-tense flag or a GREEN; a RED fixed only in a daily stays RED and its
   PATH says so; a partial fix says what remains.
6. **Move the pin.** Levels 1–4: edit the level's tag in the `LEVELS` table of
   `scripts/build-matrix.py` to the stable tag. Level 5: do not edit it
   directly; write an OpenSpec change under `openspec/changes/` listing each
   delta with its evidence and wait for the owner. See the level 5 rule in
   `docs/matrix/README.md`.
7. **Checked build must pass.** `skills/update-website/scripts/checked-build.sh`
   → exit 0 and `ok:checked-build`. It fails on any unresolved target or drifted
   quote of any level whose checkout is present.
8. **Record and file.** Write `docs/audit/<YYYY-MM-DD>-<tag>.md` (see
   `docs/audit/README.md`) and follow [`file-findings`](../file-findings/SKILL.md)
   for anything that belongs to the runtime project.
9. **Commit per level, then push.** One commit per level so the change trail
   reads. A push to `main` is a deploy: Cloudflare publishes `var/html` on
   commit. Confirm with `git log origin/main..main` empty before you exit; the
   forge is ephemeral and an unpushed commit is destroyed with it.

## What "complete" means

The audit's product is a table per level: footnotes total, re-verified, drifted
and corrected, flags confirmed, flags flipped (with evidence), and the pin
moved. The spec-versus-code question the operator actually asks — how much of
what the pages advertise is implemented at this release — is answered by the
feature and security tables in the dated audit record, one row per capability
with `implemented | partial | spec-only | absent` and a citation.

## Automation candidates

Ordered by value over effort. All shell, all already exercised by hand once.

1. **Weekly drift check (no edits).** Steps 1–4 as a scheduled run that opens
   a report when the newest tag differs from any pin: which levels, how many
   cited files changed, how many footnotes break. Cheap, zero risk, and it
   turns "we should look at the site" into a number.
2. **Post-release trigger.** Same report, fired when the runtime publishes a
   release (the release workflow could ping this repo, or a cron polls tags).
3. **Checked build as a pre-push gate.** Step 7 refusing the push when a quote
   or target does not resolve for the pinned tag. This is the one that stops a
   lie from deploying.
4. **Agent-driven re-verification (steps 5–6).** An agent per level with the
   `audit-site-claims` procedure, then a skeptic per level, then a human or a
   second agent reads the diff. Needs a model; not free; the part that should
   stay reviewed.
5. **Level 5 proposal generator.** Step 6 for level 5 only: produce the
   OpenSpec change with the exact deltas and evidence, never the edit.
