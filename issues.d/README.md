# `issues.d/` — the findings ledger

Every defect this project finds lives here, in the runtime's own fragment shape,
so that findings survive an ephemeral forge, merge without a coordinator, and
can be read by a page rather than by a person grepping prose.

## The design in one paragraph

A read is `fold(fragments)`. `issues.d/*.yaml` are **fragments**: append-only,
immutable once written, each named `<utc>-<slug>-<host>.yaml`. Nothing edits a
fragment; a change is another fragment. Compaction may later fold fragments into
a base and delete exactly the ones it folded — the fold is idempotent, so a
half-finished compaction is safe.

## The three primitives, and why each field uses the one it does

- **`issues:`** — a grow-only set keyed by `id`. Union is commutative,
  associative and idempotent, so two hosts declaring different findings both win
  and declaring the same one twice yields one finding.
- **`events:`** — a grow-only set keyed by `(id, event identity)`. An event is
  an immutable fact. You never edit one; you add another.
- **`upstream:`, `severity:`, `title:` and the other scalars** — last-writer-wins
  registers per `(id, field)`, the winner chosen by `(ts, host)`, never by
  arrival order.

Applying last-writer-wins to a **list** would silently discard the loser's
entries, which is why events are a set and not a register. That distinction is
the whole correctness argument and must not be blurred.

## Determinism rules that are easy to break

Fragments fold in `(ts, filename)` order, never directory order: the filesystem
promises no order, and two hosts folding differently would compute different
states from identical inputs, which presents as corruption rather than as a
sorting bug.

The fold is **idempotent**. Folding a fragment whose contents already reached the
state must be a no-op.

## The ladder, which is what the three columns show

`state` is not written directly. It is the join of the finding's events over a
monotone ladder — you climb up freely, and descend only through a `falsified`
event:

| rung | events | column |
|---|---|---|
| 0 | `found` | 🔴 **red** — found, not yet tracked; uncertainty still high |
| 1 | `triaged`, `filed`, `in_progress`, `blocked` | 🟡 **yellow** — documented and tracked, with a plan and low uncertainty |
| 2 | `resolved`, `verified` | 🟢 **green** — done, and the thing meets its own criteria |

`obsoleted` and `wontfix` are **lateral terminals**, not rungs: they end an
attempt without claiming completion, and are decided by plain last-writer-wins.
Every finding is in exactly one column at any time, which is what the site's
progress page requires.

Descent needs a `falsified` event carrying a reason. That is the only way a
green finding goes back to red, and it leaves a permanent record of why.

## A fragment

```yaml
issues:
  - id: 7f3a9c21                     # stable, minted once, never reused
    repo: tillandsias                # tillandsias | tillandsias.org
    title: <one line, what is wrong>
    area: <spec name / crate / script>
    class: spec-vs-code | defect | doc-drift | stale-record | site | process
    severity: high | medium | low
    tag: v56.9.5.1                   # the release the finding was verified at
    commit: b528680d…                # peeled, never the tag object
    claim: <what the spec or the site says>
    code: <what the code does, with path#Lx-Ly>
    why: <why it matters>
    fix: <the smallest fix>
    evidence:
      - path: crates/…/main.rs#L10-L20
        quote: <verbatim, from that range at this finding's tag — checked>
        note: <our reading of it, in our words — not checked, because it does
               not pretend to be a quotation>
    depends_on: [<other id>, …]
    upstream: ""                     # the filed issue URL, once a credentialed
                                     # session files it; LWW, so the filer wins
events:
  - id: 7f3a9c21
    ts: "2026-09-05T19:40:00Z"
    host: calmecacpilli
    type: found
    note: <what happened>
```

A `quote` is verified the way the site's footnotes are: it must appear in the
range it cites, at the release the finding names, or the gate refuses it. Where
no checkout is present the quote is reported unchecked rather than passed over.
Analysis in a `quote` field is the failure this rule exists to catch — it reads
as though the source said it. Put it in `note`.

`scripts/issues.py fold` prints the folded state, `validate` refuses a malformed
or non-idempotent fragment, and `columns` prints the three-column view the site
renders. The build reads the same fold, so the page and the ledger cannot
disagree.

## Filing

Use the [`file-issue`](../skills/file-issue/SKILL.md) skill. It mints the id,
writes one fragment, and never edits an existing one.

Findings against the **runtime** are recorded here too. This repository cannot
file into that project — a forge holds no credential by design — so a
credentialed session files them there and writes the URL back into `upstream:`
with one more fragment. Until then the finding is durable here, which is the
point.
