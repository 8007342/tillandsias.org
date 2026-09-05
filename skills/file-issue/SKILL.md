---
name: file-issue
description: Record a defect in the findings ledger under issues.d/, against this website or against the Tillandsias runtime, so it survives the forge and appears on the site's progress page. Also how to move one along the ladder, and how to retract a published claim.
---

# File an issue into the ledger

**Purpose.** A finding that lives in a session's transcript dies with the
forge, and one that lives in prose cannot be triaged or rendered. `issues.d/`
is the durable place. Read [`issues.d/README.md`](../../issues.d/README.md)
first — it defines the fragment shape, the three CRDT primitives and the
monotone ladder — and this skill is how you write into it.

## File a new finding

1. **Look first.** `python3 scripts/issues.py columns` and grep the ledger for
   the file or symptom. The same finding filed twice under two ids is worse
   than not filing it, because two people then work it.
2. **Mint the id from the title**, never by hand:
   `python3 scripts/issues.py mint "<the title you are about to write>"`. It is
   a content hash, so two hosts filing the same finding collide into one
   instead of duplicating.
3. **Write one fragment**, `issues.d/<utc>-<slug>-<host>.yaml`, in the shape the
   ledger README gives. Never edit an existing fragment: a fragment is
   immutable, and a change is another fragment.
4. **Gate it:** `python3 scripts/issues.py validate` must print
   `ok:issues:<n> finding(s)` and exit 0.
5. **Commit and push.** The forge is ephemeral; an unpushed finding is a
   destroyed finding.

### What each field is for

`title` is one line a reader could repeat aloud. `claim` is what the spec, the
site or the code *says*; `code` is what it *does*, with a path and line range;
`why` is the consequence; `fix` is the smallest change that would close it.
`severity` is about reach, not annoyance: **high** where someone can cross a
boundary or a credential can leak, **medium** where a guard or a spec is wrong
without a reachable break, **low** for staleness.

`tag` and `commit` name where the finding was verified — the peeled commit
(`git rev-parse <tag>^{commit}`), never the tag object, which resolves to
nothing on GitHub. For a finding about this website, they name a commit of
*this* repository.

### Quotes are checked; your reading is not

A `quote` must appear verbatim in the range it cites, at the release the
finding names. The gate refuses one that does not, because a citation nobody
checks is a citation that drifts. Your own analysis of what the source means
goes in `note` beside it, which is unchecked precisely because it does not
pretend to be a quotation. Putting analysis in a `quote` is the mistake this
rule exists to catch, and it has already happened here twenty-one times in one
sitting.

## Move a finding along

Append a fragment with an event. Never rewrite history; add to it.

- `triaged`, `filed`, `in_progress`, `blocked` — it is tracked, with a plan.
- `resolved`, `verified` — it is done and the thing meets its own criteria.
- `obsoleted`, `wontfix` — the attempt ended without completing. These are
  lateral, not rungs.

The ladder is monotone: a later event at a lower rung does not drag a finding
back down, so a stale write cannot silently undo a completion.

## Going back down, which is the interesting case

Two events descend, and the difference matters more than it looks.

- **`falsified`** — our own record was wrong. Something recorded as resolved
  was not.
- **`retracted`** — a claim this project *published* has been withdrawn. A
  green flag on a level page that turned out to be false; a measurement that
  did not hold; a verdict this site put in front of a reader and took back.

Both must carry a `note` saying why, and the gate refuses a descent without
one: going down the ladder without a reason is how a record loses the only
part worth keeping.

Retractions are counted and listed on their own. That is deliberate. A
metrics history that cannot show this project being wrong is marketing, and a
period with no retractions is a period in which either nothing was checked or
nothing was published — which is itself worth seeing.

## Findings against the Tillandsias runtime

Record them here the same way, with `repo: tillandsias`. This repository
cannot file into that project: a forge holds no GitHub credential, by the
design the security level describes. So the finding is durable here, and a
credentialed session — a host session, or the operator — files it upstream and
writes the URL back into `upstream` with one more fragment. The progress page
shows which runtime findings are still unfiled, so the gap is visible rather
than forgotten.

See [`file-findings`](../file-findings/SKILL.md) for the issue-body template
and the relay options.
