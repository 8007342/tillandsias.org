---
name: audit-site-claims
description: Re-verify one explanation level's footnotes, quotes and flags against a Tillandsias checkout at a given release tag, then have a skeptic try to refute every finding. Harness-agnostic; any agent can follow it.
---

# Audit a level's claims against a release

**Input.** A level source `docs/matrix/<level>.md`, its pinned tag `OLD`, a
target tag `NEW`, and checkouts at both under `$TILLANDSIAS_CLONE_DIR/<tag>`
(from `update-website/scripts/fetch-checkouts.sh`). The `.repo` directory
beside them holds both tags, so `git -C .repo diff OLD NEW -- <path>` shows
what changed in a cited file.

**Stance.** Read-only until the findings are verified. Every claim you make
carries a repo-relative `path#Lstart-Lend` at `NEW` whose lines you have
actually read. Never cite from memory, from a previous audit file, or from a
plan entry without reading the code it describes: the plan records intent,
the code records fact, and the 900 commits between two dailies routinely
close what the plan still lists as open. "I could not find it" beats a guess.

## Pass 1: verify

For each footnote `[^n]` of the level:

1. Resolve the target at `NEW`: path exists; the line range is inside the file.
2. Read the range at `NEW` and at `OLD`. Does the range at `NEW` still carry
   what the label and the referencing sentence claim? If the text moved, find
   it (search for distinctive words from the `OLD` range) and record the new
   range. If the claim is no longer true at `NEW`, say so and say why.
3. Record a **quote**: a verbatim, contiguous span from the `NEW` range, at
   most a few sentences, exact characters, no ellipsis, no paraphrase. The
   checked build searches for it inside the cited lines after collapsing
   whitespace and fails if it is absent. External references get no quote.
4. Verdict: `OK` | `DRIFT` (claim true, target or quote must change) |
   `FALSE` (claim no longer true) | `EXTERNAL`.

For each callout (`GREEN`, `RED`, `PATH`, `PROVEN`, `PLAUSIBLE`, `REFUTED`):

5. Is it still true at `NEW`? Check the code first, then the plan ledger
   (`plan/index.yaml`, `plan/archive/`, `plan/issues/`) and the README release
   rows for the order ids the flag's footnotes point at. Record
   `true | fixed | partial | false | unverifiable` with evidence, and for
   anything but `true` a minimal rewrite in the page's voice. A fixed RED
   becomes a past-tense flag or a GREEN; a partial fix says what remains; a
   PATH that landed says so.

6. List prose the cited source does not support.

Output shape (JSON, one object per level):

```
{ "level": "level-3-power", "old": "v56.9.2.1", "new": "v56.9.5.1",
  "footnotes": [ { "n": 3, "verdict": "DRIFT", "old_target": "…", "new_target": "…", "quote": "…", "notes": "…" } ],
  "flags": [ { "kind": "RED", "excerpt": "first twelve words", "status_at_new": "fixed", "evidence": "path#L1-L2 + quote", "suggested_rewrite": "…" } ],
  "prose_overreach": [ { "excerpt": "…", "why": "…", "suggested": "…", "evidence": "…" } ] }
```

## Pass 2: refute

A second agent (or the same one in a fresh session) takes the JSON and, for
every footnote not `OK`, every flag status, and every "fixed" or "false" claim,
tries to prove it wrong from the checkout: opens the path, reads the lines,
searches for the text, diffs the tags when the claim is about change. Default
to refuted when the evidence cannot be found. It also confirms every quote
appears verbatim in its range and lists what pass 1 missed. Only claims that
survive this pass may change the page.

## Then edit

Apply the surviving corrections to `docs/matrix/<level>.md` following
`docs/matrix/README.md`: targets, quotes, flags, prose. Move the level's pin
in `scripts/build-matrix.py` (levels 1–4) or write an OpenSpec change (level
5). Run `update-website/scripts/checked-build.sh`; it must print
`ok:checked-build`. Record the audit under `docs/audit/` and file the runtime
findings with `file-findings`.

## Running it with several agents at once

This was first run on 2026-09-05 as a fleet of agents (one auditor and one
skeptic per level slice and per capability, then one writer, one reviewer and
one fixer per level). What made it work:

- **Two checkouts, real disk.** The stable tag and the newest daily under
  `$TILLANDSIAS_CLONE_DIR`, never in the forge's 256 MB `/tmp`.
- **Private builds.** Every agent builds with `TILLANDSIAS_OUT` pointing at
  its own file and reads only the lines about its level; concurrent edits to
  other levels would otherwise look like its own failures. Only the final,
  serial `checked-build.sh` writes `var/html/index.html`.
- **One file per agent.** A writer edits its level and nothing else; the
  OpenSpec and audit-record agents edit their own directories. No agent runs
  `git add`, `commit`, `stash` or `checkout`; the operator commits per level.
- **Guides, not prompts.** The audience rules and the required changes for a
  level live in a short guide file the writer, the reviewer and the fixer all
  read, so the three agree on what "done" means.
- **The skeptic's word wins.** Where a skeptic's `refuted` or `missed` entry
  contradicts the audit it reviewed, the writer follows the skeptic; a second
  skeptic reviews the written page against the code again.
- **Quotes from comments.** A quote that spans lines of a shell, YAML or Rust
  comment is written without the comment leaders; the build strips them before
  matching.
- **Concurrency is small.** A forge with four cores runs two agents at a time
  per workflow; budget hours, not minutes, and run independent phases as
  separate workflows so they overlap.
