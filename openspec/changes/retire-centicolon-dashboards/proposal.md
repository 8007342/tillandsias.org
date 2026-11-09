# Retire the site's CentiColon score charts

Status: proposed 2026-11-08, during the refresh to stable `v56.11.7.1`.
Approved 2026-11-09 as proposed; the floor panels stay (the open question
below was not taken up). Applied in the same refresh.

## Why

The site draws its CentiColon score from one runtime file,
`docs/convergence/centicolon-dashboard.json` (`scripts/metrics.py`, series
`cc_residual`). At `v56.11.7.1` that file was last regenerated on 2026-08-08
(`d374eec9e`), and no commit between `v56.10.20.1` and `v56.11.7.1` touches
it. The site's newest score row is dated 2026-08-09. The refresh can rerun the
extract as often as it likes and nothing new arrives: it added 14 rows this
run, none of them scores. The October refresh stalled here, and so would every
later one.

Meanwhile the runtime publishes the same measure itself, kept up to date and
with better provenance:

- `openspec/specs/observatorium-dashboard/spec.md` (runtime, `v56.11.7.1`)
  requires a dashboard that shows "earned count, denominator, residual,
  evidence states and residual reasons", keeps an honest measurement history
  across definition changes, and validates each release's grade.
- `observatorium/history/snapshots.jsonl` holds one observation per release,
  from `v56.10.14.1` (2026-10-14) to `v56.11.6.1` (2026-11-06), each with its
  revision, epoch, definitions and named gaps. The latest records a residual of
  1,571 of 1,571 with the gap "CentiColon population has unregistered, missing
  or unkeyed entries".
- It deploys as its own Worker at `observatorium.tillandsias.org` (this
  repo's `docs/cloudflare-dev.md`, "Sibling Workers on the same zone").

**Restoring was considered and rejected.** The old source is frozen, so the
only way to restore the chart is to switch it to `snapshots.jsonl`. That would
splice a second definition (epochs `repository-observation-v1`/`-v2`, scored by
the scenario grader) onto 1,063 rows scored under the old dashboard. The
observatorium spec itself forbids presenting a definition change as one line
("Honest measurement history"). It would also copy, with a delay, a page the
project already publishes. (The observatorium could not be fetched from the
forge that ran this refresh, so it was not checked live. The evidence above is
from the runtime repository at the pinned tag.)

## What changes

- **Progress → "How much work is still open":** drop the top panel ("Open
  obligations, as measured by each test run") and its row in "The numbers
  behind the chart", plus the stale-gap note. Add one plain sentence pointing
  to the project's own observatorium for the current score.
- **CentiColons → "Where the score stands":** drop the sentence quoting the
  last August score. Keep the clean-up count (scripts still to be rewritten in
  Lua) and add the same pointer to the observatorium.
- **Kept, unchanged:** the whole CentiColons methodology page (what a
  CentiColon counts, the worked example, the path from spec sentence to screen,
  the monotonicity question, what the number does not say). Also kept: the
  research write-up in `docs/audit/2026-09-28-centicolon-guarantee-addendum.md`
  and the Level 5 material it backs.
- **Kept, not drawn:** the 1,063 stored `cc_residual` rows in
  `docs/metrics/series.jsonl`. The series is append-only, so nothing is deleted.
  `metrics.py verify` keeps replaying them, and `extract` keeps reading the
  file, so if the runtime ever regenerates it, nothing is lost.

## Open question for the person deciding

The other Progress panels count ratchet floors and open tasks. The
observatorium now also reports Lua and shell gate targets, which overlap the
floor counts. This proposal keeps those panels, because they come from git with
row-level provenance. Retiring them too is a separate decision.
