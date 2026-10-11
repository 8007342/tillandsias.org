# `refresh.d/` — what each release refresh did and learned

One JSON fragment per run of `skills/update-website/scripts/release-refresh.sh`,
named `<utc>-<tag>-<host>.json`, plus `distilled` fragments that summarise older
history. The same rules as `issues.d/`:

- **Append only.** A fragment is never edited. A correction is a new fragment.
- **Fold to read.** Readers sort fragments by `(ts, filename)`. A later
  `reviewed` map wins per level. `learned` entries are a grow-only set.
- **Provenance on every line.** A `learned` entry names its `evidence`: a commit
  of this repository, or a path in it. A `run` fragment records the tags, the
  pins before and after, every citation it moved and how, and every item it
  left for a person.

## Fields

| field | kind | meaning |
|---|---|---|
| `kind` | `run` \| `distilled` \| `review` | a refresh run; a summary distilled from older history; a person's review of a level's claims |
| `ts`, `host` | scalar | when and where |
| `from`, `to` | tags | site pin before; target release |
| `pins_before`, `pins_after`, `pins_moved` | maps / list | the `LEVELS` pins around the run |
| `moved` | list | each re-anchored citation: `from`, `to`, `how` (`block` = identical lines found; `quote` = verbatim quote found) |
| `judgement` | list | citations whose text could not be found again. Their level kept its pin. |
| `review_queue` | list | flags whose cited file changed in a level that moved. This never blocks. |
| `reviewed` | map | level slug → the release a person last reviewed its claims against |
| `learned` | list | `{ts, surfaces, note, evidence}`: one lesson for the next run per entry |
| `next_run` | list | sentences the next run prints before it starts |

This ledger is internal: it is written for the next run and is never shown on
the site. The only part a page reads is the `reviewed` map. A level whose pin
moved past its last review says so in its footnote note. A page's "How this
section has improved" note comes from `docs/progress/improvements.json`
instead. That file holds plain-words outcomes for readers, with no ids and no
process detail, and it only grows (`release-refresh.sh --reader SURFACE:SENTENCE`).
