## Purpose

The one-command refresh that runs when a Tillandsias release happens. It does
the work that needs no judgement and stops for the work that does.

## ADDED Requirements

### Requirement: One entry command does the mechanical work
`skills/update-website/scripts/release-refresh.sh` MUST, in one run: resolve
the target release; ensure checkouts; re-anchor every runtime citation by
content; move the pin of each level whose citations all re-anchored;
regenerate the Progress spec snapshot at the site pin; append new metrics rows
from runtime git history and verify that every stored row replays; run the
checked build; and append one fragment to `refresh.d/`. Its last line MUST be
`ok:refreshed:<tag>`, `ask:judgement:<n>` or `blocked:<why>`.

#### Scenario: A release with only shifted lines
- **WHEN** every cited text is found again at the new tag
- **THEN** every level moves its pin, the checked build is green, and the run
  ends `ok:refreshed:<tag>` without asking anyone

#### Scenario: A cited text disappeared
- **WHEN** a footnote's quote is not found anywhere in its file at the new tag
- **THEN** that level keeps its pin, the item is listed with what the range
  used to say, the other levels move, and the run ends `ask:judgement:<n>`

#### Scenario: Re-running at the current pin
- **WHEN** the command runs against the release the site already pins
- **THEN** `var/html/index.html` is unchanged and the only new file is the
  run's fragment in `refresh.d/`

### Requirement: Evidence is appended, never rewritten
`refresh.d/*.json` and `docs/metrics/series.jsonl` MUST only grow. A wrong
metrics row is withdrawn by an appended `retract` row with a reason. Every
metrics row MUST name the runtime commit and path it was read from, and
`metrics.py verify` MUST reproduce it from git.

#### Scenario: Provenance replays
- **WHEN** `metrics.py verify --repo <full runtime clone> --ref <pin>` runs
- **THEN** every unretracted row whose source commit is reachable from the
  pin is reproduced exactly, or the command prints
  `blocked:metrics-not-reproducible:<n>`
