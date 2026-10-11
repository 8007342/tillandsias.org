---
name: update-website
description: A Tillandsias release happened, so bring tillandsias.org up to it. One command does every step that needs no judgement: re-pin by content, regenerate Progress and CentiColon data, rebuild the metrics history, checked build, and record the run. It stops only for a claim that may have changed truth value or for a new claim. Run it after a release, or weekly.
---

# Update the website after a release

Every claim on the site is a footnote into the runtime at a pinned release.
When a release lands, line numbers drift but the cited text mostly does not.
Moving the pins is therefore mostly mechanical, and this skill does that part
without a person. A person is needed only where the cited text is gone or
where a claim changes.

## 0. Before you start

- Work in a worktree outside the checkout. Never run this on `main`.
- Checkouts live in `$TILLANDSIAS_CLONE_DIR` (default
  `~/.cache/tillandsias-org/clones`, on real disk, never `/tmp`).
- The metrics step needs a **full** (not shallow) runtime clone:
  `--history DIR` or `TILLANDSIAS_HISTORY_REPO`. The default is
  `$TILLANDSIAS_CLONE_DIR/.history`. Create it once with
  `git clone https://github.com/8007342/tillandsias "$TILLANDSIAS_CLONE_DIR/.history"`.
  After that, `git -C … fetch --tags` keeps it current.
- The command prints the previous run's leftover items and `next_run` notes
  first. Read them.

## 1. Run the one command

```
skills/update-website/scripts/release-refresh.sh                 # stable channel
skills/update-website/scripts/release-refresh.sh --tag v56.10.9.1 --offline
```

| step | what it does | gate |
|---|---|---|
| fetch | checkouts for the target and every pin | `ok:checkouts` |
| anchors | `scripts/anchors.py apply`: re-anchors every runtime citation (level footnotes, Big Graph, CentiColons `rcite(...)`) by identical lines or verbatim quote, then moves each level whose citations all re-anchored | `ok:anchors:<n>` or `ask:anchors:<n>` |
| snapshot | `scripts/snapshot-specs.py` at the site pin (Progress inventory) | snapshot line |
| metrics | `scripts/metrics.py extract`, then `verify`: appends new rows from runtime git and proves every stored row replays | `ok:metrics-verified:<n>` |
| build | `checked-build.sh`: every quote at its release, ledger quotes, no warnings | `ok:checked-build` |
| refine | appends `refresh.d/<utc>-<tag>-<host>.json` | always |

Last line: `ok:refreshed:<tag>` (done; commit), `ask:judgement:<n>` (exit 3:
the mechanical part is done; go to step 2) or `blocked:<why>` (fix the cause
and re-run). Re-running is safe. Every step is idempotent, and the stores only
grow.

## 2. Judgement, and only judgement

`ask:` lines name each item and why it was left. The fragment holds the full
detail: what the range used to say, and candidate files for a moved path.

- **`quote-gone` / `unquoted-text-changed`**: the evidence changed. Follow
  [`audit-site-claims`](../audit-site-claims/SKILL.md) for that one footnote.
  Then either re-cite (new target and new quote) or change the claim, the
  flag or the PATH.
- **`path-gone`**: usually a port or a rename. Check the candidates. A
  retarget gets a new quote, because the old one belongs to a file that no
  longer exists.
- **`daily-fix-reached-stable`**: a PATH said "fixed only in the daily".
  That is now false, so rewrite the flag.
- **`quote-ambiguous` / `block-ambiguous`**: pick the occurrence the claim
  means, and widen the quote until it is unique.
- **Level 5 proposal** (until `openspec/changes/automated-release-refresh`
  is archived): the generated `openspec/changes/level-5-<tag>/` waits for the
  operator. Do not apply it yourself.

Edit only what an item names. Then run the command again: the levels you
fixed now move. Commit when it prints `ok:refreshed:<tag>`.

The `review_queue` lists flags whose cited files changed. It never blocks a
move. Work through it when you have time. When you have re-read a level's
claims, append a `kind: review` fragment with `reviewed: {<slug>: <tag>}`
(see `refresh.d/README.md`), so the page stops saying the claims are older
than the pin.

## 3. Refine: leave the next run better

Every run appends its fragment automatically. Add what you learned, one line
per lesson, naming the page surface it improves:

```
release-refresh.sh --tag vX --learned 'progress:the snapshot now includes …'
```

Or append a `distilled` fragment by hand. Never edit an old fragment: a
correction is a new one. The `learned` entries become the "How this section
has improved" notes on Live progress and CentiColons. A step that needed a
person twice is a missing rule: add the rule to `anchors.py` or `refresh.py`,
and record it with `--learned 'anchors:…'`.

## 4. Commit and publish

The pre-commit hook re-runs the checked build and refuses a stale
`var/html/index.html`. Make one commit per level when a person changed
claims, and one commit for the mechanical refresh. A push to `main` deploys
(Cloudflare publishes `var/html`). Push only when the operator's flow says so.

## What a green run does and does not claim

A green run claims that every cited text exists verbatim at the new pin and
that every metrics row replays from git. It does **not** claim that every RED
is still the whole truth: a fix can land beside an unchanged quoted line. For
that reason the footnote note of a level whose pin moved past its last review
says so, and the dated audit in `docs/audit/` is still written by a person
whenever claims are re-read.
