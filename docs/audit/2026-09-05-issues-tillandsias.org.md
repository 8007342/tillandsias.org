# Findings for tillandsias.org — 2026-09-05

What the 2026-09-05 audit found **about this website** and did **not** fix, plus
the automation the update loop should grow. The runtime findings from the same
run are in [`2026-09-05-issues-tillandsias.md`](2026-09-05-issues-tillandsias.md);
the run's own record — pins, per-level tables, capability and security tables —
is [`2026-09-05-v56.9.2.1.md`](2026-09-05-v56.9.2.1.md).

- **Site commit:** `c00622b` (`c00622bf82b1935b2189ee6af8f8c2980ab04337`), working
  tree clean apart from the records in this directory.
- **Runtime tags cited:** `v56.9.2.1` (stable, the tag every level pins) and
  `v56.9.5.1` (newest daily). Every runtime line quoted below was read in the
  checkout for the tag named beside it.
- **Baseline for "before today":** `bf5bde3`, the last commit of 2026-09-04.

Entries keep the shape of the [`file-findings`](../../skills/file-findings/SKILL.md)
issue template. Two adaptations, because these are site issues rather than
runtime ones: the **Tag** line names the site commit (and the runtime tag when a
runtime file is the evidence), and the automation entries in section G carry two
extra fields — **What it would take** and **What it would catch** — because a
missing capability has no "smallest fix" that is honest at one sentence.

Nothing in this file was fixed today. Nothing here edits `docs/matrix/`,
`scripts/`, `skills/` or `openspec/`; those are the owner's to move.

| § | Area | Entries |
|---|---|---|
| A | Level 5 and the delta discipline | A1–A3 |
| B | Page length and the editorial rules | B1–B3 |
| C | Build and toolchain | C1 |
| D | What the forge hands an agent | D1 |
| E | Figures | E1 |
| F | Audit records and file layout | F1 |
| G | Automation the update loop should grow (ranked) | G1–G6 |

---

# A. Level 5 and the delta discipline

## A1. The level-5 deltas are live on the site while their OpenSpec change is still unapproved, and `openspec/specs/` holds no site spec at all

- Tag: tillandsias.org @ c00622b
- Area: `openspec/changes/level-5-stable-pin-deltas/`, `openspec/specs/`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim on the site / in the spec.** The record of the change says the deltas
are pending: `openspec/changes/add-level-page-specs/tasks.md`, task 4.17 — "the
pin stays at v56.9.2.1, one statement false at the pin is corrected" — and the
same task records "Filed 2026-09-05; lands when the operator approves it." The
governing requirement is
`openspec/changes/add-level-page-specs/specs/site/level-5/spec.md#L27-L34`:

> An editor MAY apply the deltas it lists, and MUST apply no others: the record
> and the diff are checked against each other, and the operator reviews the
> change before it is archived.

**What the code does.** All seven deltas are applied and published. Every task
box in `openspec/changes/level-5-stable-pin-deltas/tasks.md` is `[x]`;
`docs/matrix/level-5-phd.md#L326` carries D1 ("two of the three properties —
commutativity and idempotence — are tested by name[^34]"), `#L429-L436` carry
the four new `@v56.9.5.1` footnotes `[^41]`–`[^44]`, and commit `ed40f8b`
("Publish levels 1, 2 and 5") wrote the result into `var/html/index.html`, which
Cloudflare serves on commit. Meanwhile `openspec/specs/` contains only
`.gitkeep`: no site capability has ever been promoted out of `changes/`, so the
current contract for every level lives in an unarchived change directory.

**Why it matters.** The applied-before-approved state is permitted by the spec
(an editor MAY apply), so this is not a violation — it is an unclosed loop. The
loop matters because the reviewable artifact and the published artifact have
drifted apart in *status*, not in content: a reader of `openspec/` cannot tell
which of the three open changes describe the live site and which are proposals,
and `openspec/specs/site/level-5/` — the place the next editor would look for
the page's contract — does not exist. The longer the change sits, the more the
next audit's deltas pile onto an unreviewed base.

**Smallest fix.** The operator reviews `level-5-stable-pin-deltas`, then
`openspec-archive-change` it (and `add-level-page-specs`, whose task 3.3 names
the same sync), so `openspec/specs/site/level-{common,1..5}/` become the current
contract and `changes/` holds only what is genuinely proposed.

## A2. Ten of level 5's forty-four footnotes need re-anchoring whenever its pin moves, and one quote no longer exists at the daily

- Tag: tillandsias.org @ c00622b; runtime evidence at v56.9.2.1 and v56.9.5.1
- Area: `docs/matrix/level-5-phd.md`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim on the site / in the spec.** `docs/matrix/README.md`: "When you bump a
level's tag, re-verify its line ranges — they drift — and rebuild with the
checkout present so the quotes are re-checked too." The level-5 spec adds
(`.../specs/site/level-5/spec.md#L36-L40`) that a pin-bump change "lists one
delta per footnote whose target or quote drifted between the tags".

**What the code does.** A trial build pinned to the newest daily
(`TILLANDSIAS_PIN_OVERRIDE=v56.9.5.1 TILLANDSIAS_OUT=<scratch> python3
scripts/build-matrix.py`, run 2026-09-05, nothing in the repo written) reports
six broken level-5 targets — every one a quote that is no longer inside its
cited range:

| Footnote | Target | At v56.9.5.1 |
|---|---|---|
| `[^10]`, `[^15]` | `methodology/proximity.yaml#L47-L57`, `#L60-L97` | quote not found in range |
| `[^11]`, `[^16]`, `[^19]` | `methodology/philosophy.yaml#L103-L121`, `#L8-L31`, `#L32-L39` | quote not found in range |
| `[^34]` | `crates/tillandsias-plan/src/fragments.rs#L2648-L2668` | quote not found in range |

`[^16]` is the hard one. Its quote at v56.9.2.1
(`methodology/philosophy.yaml#L8-L31`) is "then iterate — the STRONG LLN
(almost-sure convergence) makes the stream of iterations converge hard"; at
v56.9.5.1 that sentence is deleted, not moved — `weak_vs_strong` now reads
"then iterate. The hazard is uncontrolled skew sneaking in at the END of every
individual prompt" and continues "CITATION WITHDRAWN (order 976-bd3n, external
review 2026-09-03)" (`methodology/philosophy.yaml#L17-L38` @ v56.9.5.1). The
four `@v56.9.5.1` footnotes `[^41]`–`[^44]` are the other half: each resolves
cleanly at the daily today (verified individually), but once the pin *is*
v56.9.5.1 the `@vTAG` suffix is redundant and, worse, the REDs those PATH lines
hang from are fixed at that tag — the flags themselves have to be re-derived,
not just the anchors.

**Why it matters.** Ten of forty-four footnotes is a quarter of the page, and
the level-5 rule forbids doing that work as an ordinary edit: each is a delta
with evidence and a verbatim quote at the target tag, in a change the operator
reviews. Written down now, at the tags where both sides were read, the next pin
bump is a mechanical exercise; discovered at bump time it is a re-derivation of
the strong-law argument under time pressure.

**Smallest fix.** Add the table above to the next level-5 change's `tasks.md` as
its work list, with `[^16]` flagged as needing new prose rather than a new
anchor.

## A3. The next level-5 delta change is unwritten while two of its REDs are already outrun in the daily channel

- Tag: tillandsias.org @ c00622b; runtime evidence at v56.9.5.1
- Area: `openspec/changes/` (no change exists), `docs/matrix/level-5-phd.md`
- Class: stale-plan-entry
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim on the site / in the spec.** `openspec/changes/add-level-page-specs/tasks.md`
task 4.18 is unchecked and names the work: "the REDs on property tests and on
requirement identifiers are outrun in the daily channel …; the footnotes into
`crates/tillandsias-plan/src/fragments.rs`, `scripts/local-ci.sh` and
`methodology/proximity.yaml` drift between the tags; the measured numbers in the
prose are re-measured. One delta per item with `path#L` evidence and a verbatim
quote at the target tag."

**What the code does.** The fixes are real at the daily and were read there:
`crates/tillandsias-plan/src/obligation_props.rs#L172-L219` @ v56.9.5.1 carries
the `proptest!` block with `refine_is_monotone_on_the_real_rules`,
`refine_is_inflationary` and `refine_is_idempotent`;
`scripts/check-requirement-ids.sh#L5-L35` @ v56.9.5.1 is the gate for stable
requirement identifiers. Of the seven cited files whose content differs between
the tags — `fragments.rs`, `obligation.rs`, `obligation_props.rs`,
`philosophy.yaml`, `proximity.yaml`, `local-ci.sh`, `check-requirement-ids.sh`
(`git -C clones/.repo diff v56.9.2.1 v56.9.5.1 -- <path>`) — only the four the
D2–D5 footnotes name are acknowledged on the page today.

**Why it matters.** Level 5 is the page that may lag, and lag is legitimate
(`.../level-5/spec.md#L15-L21`) — but only while the lag is *recorded*. Task
4.18 is the only record, it is a paragraph inside another change's task list,
and it will be read by whoever bumps the pin rather than by whoever reviews the
site next week.

**Smallest fix.** Open `openspec/changes/level-5-pin-bump-<tag>/` now, empty
except `proposal.md` carrying task 4.18's list and this record's table (A2), so
the deltas accumulate against a change instead of a checkbox.

---

# B. Page length and the editorial rules

## B1. The pages are 46% longer in prose than yesterday, and the "roughly the same length" expectation is written down nowhere

- Tag: tillandsias.org @ c00622b (before: `bf5bde3`)
- Area: `docs/matrix/`, `openspec/changes/add-level-page-specs/specs/site/level-common/spec.md`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, levels 1–5

**Claim on the site / in the spec.** The editorial rules that *are* written down
are in `docs/matrix/README.md` — "One file per explanation level. Each is a
single merged narrative", "Implementation trivia is not substance", "a page that
is all flags has stopped being prose" — and in the level specs. **None of them
constrains length.** A grep for `length`, `shorter`, `longer`, `concise` and
`brev` across `docs/`, `openspec/`, `skills/` and `scripts/` returns no rule.
The expectation that the five levels stay roughly comparable in size is real —
it is what the tabbed layout and the "picks up where the previous level left
off" subtitles in `scripts/build-matrix.py#L45-L78` @ 08262da imply — but it lives only in
the operator's head and in this session's instructions.

**What the code does.** Prose words per level, counted as every word outside the
footnote definitions (`^[^n]:`) and their indented quote lines, `git show
bf5bde3:docs/matrix/<file>` versus the working tree:

| Level | Prose words before | after | × | Footnotes before → after |
|---|---:|---:|---:|---|
| 1 — Like I'm 5 | 613 | 618 | 1.0 | 9 → 22 |
| 2 — I barely understand my phone | 785 | 940 | 1.2 | 15 → 29 |
| 3 — I'm a power user | 1,034 | 3,548 | 3.4 | 15 → 141 |
| 4 — I'm a Cyber Security expert | 1,794 | 2,753 | 1.5 | 26 → 93 |
| 5 — I'm a MathWiz / Hacker | 4,051 | 4,204 | 1.0 | 40 → 44 |
| **Total** | **8,277** | **12,063** | **1.46** | **105 → 329** |

The spread was 6.6× before (613…4,051) and is 6.8× now (618…4,204), so it is
essentially unchanged — level 3 moved from the middle of the five to the second
largest, and the tail is where it was. Level 3's growth is almost entirely the new
capability inventory: "What you get the moment a forge opens" and its eight
subsections are 2,002 of the page's 3,548 prose words, 56%, with 42
GREEN/RED/PATH callouts across the page against 13 before.

**Why it matters.** The operator asked for a full capability inventory on the
power-user page, and the audit record delivers exactly that as a table — nine
capabilities with `implemented | partial | spec-only | absent`
(`docs/audit/2026-09-05-v56.9.2.1.md`, its table "What the power-user page
advertises, at v56.9.2.1"). An inventory is a completeness claim: it is worth
having *because* it enumerates, and it cannot be cut in half without becoming a
sample. The unwritten length norm has no such
justification recorded, and it is the one of the two that no artifact checks.

**Recommendation — the length rule gives, but not silently.** Write the norm
down as a shape rule rather than a word budget, in `level-common`: levels 1 and
2 are *arguments* and stay readable in one sitting (they are 618 and 940 words
and should stay near that); levels 3, 4 and 5 are *references* and are as long
as their subject, provided every section earns its place under the rules that
already exist. Then give level 3 the navigation a reference page needs — its
eight capability subsections already exist as `###` headings — rather than
trimming the inventory the operator asked for. If instead the norm wins, the
honest move is not to delete evidence but to split: the inventory becomes its
own level, and that is a structural change needing its own OpenSpec change.

**Smallest fix.** One requirement in
`openspec/changes/add-level-page-specs/specs/site/level-common/spec.md` stating
the argument/reference split above, so the next editing agent is bound by a
written rule instead of guessing at an unwritten one.

## B2. Level 3's capability inventory has no requirement in its spec

- Tag: tillandsias.org @ c00622b
- Area: `openspec/changes/add-level-page-specs/specs/site/level-3/spec.md`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 3

**Claim on the site / in the spec.** The level-3 spec's Purpose says the page
"is the anatomy: what runs where, what survives a teardown, and where the sharp
edges are", and it carries four requirements: enclave anatomy matches the
membership guard, survivorship claims match the pinned code, every RED is true
at the pin, gate and CI statements (`#L10`, `#L24`, `#L37`, `#L49`).

**What the code does.** `docs/matrix/level-3-power.md#L3-L77` is a section the
spec does not mention — "What you get the moment a forge opens", eight
subsections (forge container, HTTPS proxy and cache, local inference, git mirror
and push relay, vault, experts and project index, sibling web containers,
Chromium), each ending in a GREEN or RED with its PATH. It is 56% of the page
and it is the part a reader arrives for.

**Why it matters.** A requirement is what survives the next rewrite. The
anatomy, survivorship and gate requirements will hold the next editor to those
three sections; nothing holds them to keeping the inventory complete, matching
the audit record's capability table, or marking a capability `spec-only` when
the code does not carry it. The page and its contract now disagree about what
the page is *for*.

**Smallest fix.** Add one requirement to the level-3 spec: the page enumerates
the capabilities a forge provides on launch, one flag per capability, with the
status at the pin matching the current audit record's capability table.

## B3. The byte-identical rebuild check (task 3.2) now passes and is still recorded as unrun

- Tag: tillandsias.org @ c00622b
- Area: `openspec/changes/add-level-page-specs/tasks.md`, task 3.2
- Class: stale-plan-entry
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** Task 3.2 records the 2026-09-05 attempt as
inconclusive: committed page `79a9b2e8…`, private build `36c97e6c…` — "not
comparable, because levels 1, 2 and 5 were being edited in the same working tree
at the time. Left unchecked; re-run on a clean tree."

**What the code does.** Re-run on the clean tree at `c00622b`:
`sha256sum var/html/index.html` and a private build
(`TILLANDSIAS_OUT=<scratch> TILLANDSIAS_CLONE_DIR=<clones> python3
scripts/build-matrix.py`) both give
`baab0e512b737f8467646dfc2688b4da609bc680b1b13c631dae2e7913cc3714`. The same run
prints `all checked footnote targets resolve` with 22 / 29 / 141 / 93 / 44
footnotes per level, exit 0.

**Why it matters.** That hash is the guarantee that the committed artifact
Cloudflare serves is the one the sources produce — the assumption
`docs/cloudflare-dev.md#L90-L96` rests on when it leaves the build command
empty. An unchecked box says the guarantee is untested when it is not.

**Smallest fix.** Tick task 3.2 and record the hash and the date beside it.

---

# C. Build and toolchain

## C1. The only build is Python, which the runtime methodology forbids for committed automation

- Tag: tillandsias.org @ c00622b; runtime evidence at v56.9.2.1 and v56.9.5.1
- Area: `scripts/build-matrix.py`, `scripts/figures.py`, `skills/update-website/scripts/`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** `methodology.yaml#L170-L182` (identical at
both tags):

> Python is not allowed for Tillandsias runtime, harness, or repository
> scripts. One-off interactive use is still discouraged and must not be copied
> into committed scripts, skills, litmus tests, or runbooks.

with `approved_default_languages` of Rust, POSIX shell "only when it dispatches
existing binaries or Rust tools", and PowerShell for Windows hosts; the
`exception_process` is "explicit approval from The Tlatoani before it is
committed or used by recurring automation".

**What the code does.** This repository's page generator is 847 lines of Python
(`scripts/build-matrix.py`) plus 316 more of inline-SVG figures
(`scripts/figures.py`); `package.json#L6` wires it to `npm run build`; and two
committed skill scripts invoke it on every run of the loop —
`skills/update-website/scripts/checked-build.sh#L22` and
`drift-report.sh#L66-L67`. That is recurring automation, which is exactly what the
exception process names.

**The exception this repository relies on.** Two things, and only one of them is
written down. (1) `skills/README.md#L16-L19` states the convention: "no new
Python (the runtime methodology forbids it for committed automation, and this
repository's only Python is the page build it inherited)" — an inheritance
argument, not an approval. (2) The rule's own checker,
`scripts/check-no-python-scripts.sh` @ v56.9.5.1, does `ROOT="$(git rev-parse
--show-toplevel)"` and then execs `tillandsias-policy check-no-python-scripts`
against that root — so it scans the runtime repository and has never scanned
this one. Compliance here is convention plus the checker's blind spot: no
recorded approval was found in either repository — this one grep-searched in
full, the runtime's ledger (`plan/index.yaml` @ v56.9.5.1) searched for a Python
approval, exception or waiver.

**Why it matters.** The site is the project's public argument that it says what
is true about itself, and level 4's whole case is that promises are
machine-checked. A methodology rule that this repository quietly does not follow
is the kind of thing a reader of the security page is entitled to know about, and
it is also a live risk: the day the checker learns about sibling repositories,
the build breaks and the page cannot be regenerated.

**What a replacement would cost.** A Rust rewrite is the approved path and is
not small: 1,163 lines producing a 583,099-byte artifact, covering the markdown
dialect in `docs/matrix/README.md` (headings, lists, inline emphasis, seven
callout kinds, `$…$` and `$$…$$` passthrough for KaTeX, `@fig:` inlining), the
footnote parser `FN_DEF` at `scripts/build-matrix.py#L122` @ 08262da with its `@vTAG`
suffix, the checked-build resolver (path exists, range inside the file, quote
found after whitespace collapsing and comment-leader stripping — `norm_source`
at `#L157-L160`), and the whole HTML/CSS template. Byte-identical output is the
acceptance test (B3 gives today's hash), and until it passes, `var/html` cannot
be regenerated by the new tool without a diff no reviewer can read. Estimate a
few days of work plus one full re-verification run — and note that a POSIX-shell
port is not permitted by the rule's own wording, since it would not be
dispatching an existing binary.

**Smallest fix.** Ask The Tlatoani for the explicit exception the rule provides
for, and record it in `docs/matrix/README.md` beside the build command, naming
the two files it covers and the condition (no new Python, replacement in Rust
when the page generator is next touched substantially).

---

# D. What the forge hands an agent

## D1. The startup context every agent here reads hands out the pre-flip service URL shape

- Tag: tillandsias.org @ c00622b; runtime evidence at v56.9.2.1 and v56.9.5.1
- Area: `.forge-startup-context.md` (generated; source is the runtime's `images/default/lib-common.sh`)
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 3

**Claim on the site / in the spec.** `.forge-startup-context.md#L131-L136` in
this checkout tells the agent, for a dev server: "Hand the user
`http://tillandsias.org.<service>.localhost/` (no port)." That is
`<project>.<service>.localhost`.

**What the code does.** The runtime retired that shape in April.
`openspec/specs/subdomain-naming-flip/spec.md#L18` @ v56.9.2.1 and `#L19`
@ v56.9.5.1 — the requirement stands at **both** tags:

> All URLs referencing forge services MUST use the pattern
> `<service>.<project>.localhost` instead of `<project>.<service>.localhost`.

and the browser MCP enforces it: `crates/tillandsias-browser-mcp/src/allowlist.rs#L64`
@ v56.9.5.1 — `AllowlistDeny::HostShape => write!(f, "host must be
<service>.<project>.localhost")`. The generator carries the stale line at both
tags: `images/default/lib-common.sh#L4223` @ v56.9.2.1 and `#L4535` @ v56.9.5.1
both emit ``user `http://${project_name}.<service>.localhost/` (no port)``. The
publishing paragraph two lines below is correct (`www.<project>.localhost`), as
is this repository's own workstream note, `plan/local-https-serve.md`, which
uses `https://www.tillandsias.org.localhost`.

**Why it matters.** An agent that follows the context file hands its user a
hostname the router has no route for and the browser tool refuses by shape, and
then debugs a dev server that "looks dead" — the exact failure the same
paragraph warns about for the wrong reason. This is the fourth documented case
of the startup context misinforming an agent: level 3's page already flags the
Vault address (`docs/matrix/level-3-power.md#L50`, "The context file tells the
agent the vault is at `http://vault:8200`. The shipped listener is TLS-only"),
the on-demand attestation claim (`#L13`) and the Local Experts mode (`#L59`).
This one is flagged nowhere yet, and it is the only one of the four that hands
the agent a *wrong artifact to give the user* rather than a wrong belief about a
service.

**Smallest fix.** In the runtime, swap the two labels at
`images/default/lib-common.sh#L4535` to
``http://<service>.${project_name}.localhost/``. This file is generated and
gitignored here (`.gitignore#L6`), so nothing in this repository can fix it —
relay it to the runtime alongside the Vault-address and Sigstore-attestation
entries already in `2026-09-05-issues-tillandsias.md` — "The forge startup
context tells the agent Vault is at `http://vault:8200`; the listener is
TLS-only" and "The startup context says on-demand installs verify a Sigstore
attestation" — and add it to level 3's context-file RED at the next
re-verification.

---

# E. Figures

## E1. Ten of the eleven figures are placed, `loop` is drawn and never used, and the new capability sections carry none

- Tag: tillandsias.org @ c00622b
- Area: `scripts/figures.py`, `docs/matrix/level-3-power.md`, `docs/matrix/level-4-security.md`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, levels 1–5

**Claim on the site / in the spec.** `docs/matrix/README.md` lists eleven
figures — "`layers`, `loop`, `staircase`, `lln`, `lattice`, `crdt`, `gate`,
`ephemeral`, `fixpoint`, `galois`, `hasse` — defined as inline SVG in
`scripts/figures.py`".

**What the code does.** All eleven exist and are registered in the `FIGURES`
dict at `scripts/figures.py#L307-L311`. Ten are placed on a page: `ephemeral`
(levels 1, 3), `gate` (2, 3, 4), `staircase` (2, 5), `layers` (3), and
`lattice`, `hasse`, `fixpoint`, `lln`, `galois`, `crdt` (5) — fourteen
placements in all, of which level 5 has seven. `loop` — `scripts/figures.py#L41`,
"The closed loop from specs through evidence back to specs" — appears in no
level file and in no byte of `var/html/index.html`. The two sections written
today are figureless: level 3's eight-capability inventory (`#L3-L77`) has none,
and level 4's layer-by-layer case has one, `@fig:gate` at `#L27`, inherited from
before.

**Do the new sections want one?** Two, and they already exist. Level 3's
inventory is a list of eight things attached to one enclave: `@fig:layers` is
placed further down at `#L91` under "The anatomy", which is where the reader has
already stopped needing it — moving it above the inventory gives the eight
subsections something to hang on. And `loop` is the missing picture for level
3's gate section (`#L140-L152`, "Driving it, and where the gate sits") or for
level 4's assurance section (`#L90-L93`, "What the assurance claim actually
is"), both of which argue that specs, evidence and the gate close on each other
in exactly the shape that figure draws. No new figure needs drawing.

**Why it matters.** A figure defined and never placed is dead weight in a file
whose whole point is that the figures "carry one idea each"; and the longest,
newest, most list-shaped section on the site currently has no visual anchor at
all.

**Smallest fix.** Place `@fig:loop` in level 3's gate section, and move
`@fig:layers` above the capability inventory rather than below it — both are
one-line edits under the existing dialect.

---

# F. Audit records and file layout

## F1. `docs/matrix/*.audit.md` are superseded by this run's record and should move under `docs/audit/`

- Tag: tillandsias.org @ c00622b
- Area: `docs/matrix/level-{1,2,3,4}-*.audit.md`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, levels 1–4

**Claim on the site / in the spec.** Each file says so itself —
`docs/matrix/level-1-five.audit.md#L9`: "Valid for pin v56.9.2.1 only;
superseded by docs/audit/2026-09-05-v56.9.2.1.md once that record lands."
`docs/audit/README.md#L13-L15` agrees: "The per-level annotation files under
`docs/matrix/*.audit.md` are the predecessors of these records (written
2026-09-04 against v56.9.2.1); new runs write here." And `level-common`'s
"Audit records and their inputs" requirement makes it a rule: they "are
superseded by the next record under `docs/audit/` and are never a source of
requirement text."

**What the code does.** That record landed today
(`docs/audit/2026-09-05-v56.9.2.1.md`, 551 lines: per-level tables plus the
capability and security tables), so all four annotation files are now history —
and they still sit in `docs/matrix/`, the directory whose README opens with
"Edit the words here, never the HTML" and whose every other file is page
content. Each has to open with an eight-line comment header saying so
(`docs/matrix/level-1-five.audit.md#L2-L4`: "AGENT ANNOTATIONS, NOT PAGE
CONTENT. Build pipeline does NOT read this file"). There is no level-5
annotation file, so the set is also incomplete.

**Why it matters.** Two kinds of file in one directory, distinguished only by an
infix, is a trap for the next editing agent working from a glob — and the build
already protects itself by rendering only the slugs in `LEVELS`
(`scripts/build-matrix.py#L45-L78` @ 08262da), which means nothing but a human reader is
harmed, quietly.

**Smallest fix.** `git mv docs/matrix/level-<n>-<slug>.audit.md
docs/audit/2026-09-04-level-<n>-<slug>.audit.md`, then update the three places
that name the old path: `docs/audit/README.md#L13`,
`openspec/changes/add-level-page-specs/design.md#L9-L23`, and the level-common
requirement quoted above.

---

# G. Automation the update loop should grow

The five candidates in
[`skills/update-website/SKILL.md#L92-L110`](../../skills/update-website/SKILL.md),
re-ranked after running the loop by hand, plus one the run itself argued for.
The skill orders by value over effort and puts the weekly drift check first; I
put the pre-push gate first, because the drift check's cost is not its script —
it is finding a scheduler this repository does not have, while the gate's script
already exists and is exercised.

| Rank | Candidate | Skill's rank | Effort | Stops a lie reaching the reader? |
|---|---|---|---|---|
| G1 | Checked build as a pre-push gate | 3 | hook + installer, ~40 lines | **yes** |
| G2 | Drift check, extended to the daily channel | 1 | ~15 lines + a scheduler decision | no — it warns |
| G3 | Quote re-anchor helper | new | ~60 lines | no — it removes toil |
| G4 | Post-release trigger | 2 | a webhook or a poll, plus a home | no |
| G5 | Level-5 proposal generator | 5 | ~120 lines, needs G3 | no |
| G6 | Agent-driven re-verification | 4 | a model, per level, plus review | no |

## G1. Nothing stops a broken footnote from being published

- Tag: tillandsias.org @ c00622b
- Area: `skills/update-website/scripts/checked-build.sh`, `.git/hooks`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** The skill, step 7: "Checked build must
pass … It fails on any unresolved target or drifted quote of any level whose
checkout is present." `docs/matrix/README.md`: "Do a checked build before
publishing: a footnote that 404s is worse than no footnote."

**What the code does.** `checked-build.sh` does exactly what it promises —
`blocked:missing-checkouts`, `blocked:footnotes-do-not-resolve`,
`blocked:build-warnings`, non-zero exit — and **nothing runs it**. `.git/hooks/`
holds only the stock `*.sample` files, there is no `.github/` in this
repository, and `wrangler.jsonc` deploys committed assets with no build step, so
a push to `main` publishes whatever `var/html/index.html` contains. Both
qualities are a matter of the author remembering.

**What it would take.** A tracked `.githooks/pre-push` that runs
`skills/update-website/scripts/checked-build.sh` and refuses on non-zero, plus a
one-line `scripts/install-hooks.sh` (`git config core.hooksPath .githooks`) and
a line in the skill's step 9 telling a fresh forge to run it — the forge is
ephemeral, so hook installation is per-session, which is the only real design
question. Second question: what to do when the checkouts are absent
(`blocked:missing-checkouts`, exit 2) — fail closed and make the author run
`fetch-checkouts.sh`, or let a push through with a loud warning. Fail closed is
right: an unchecked level is not a checked build, as the script's own header
says.

**What it would catch.** The whole class the trial build measures: today, if the
five pins were moved to `v56.9.5.1` without re-verification, **121 of 329
footnotes** would resolve to a range that no longer contains their quote — 9 on
level 1, 2 on level 2, 77 on level 3, 27 on level 4, 6 on level 5 (measured, not
estimated: `TILLANDSIAS_PIN_OVERRIDE=v56.9.5.1` trial build, 2026-09-05). The
same check is what surfaced the two quote-matching gaps the build closed
mid-session today — a quote spanning comment lines would not match until the
stripper learned about `#`, `//` and then `//!` leaders (`a756c6d`, `898dc7d`).

**One rule the gate cannot check yet.** "Every `> RED:` is followed by a
`> PATH:`" (`docs/matrix/README.md`, and a requirement in `level-common`, which
binds every level) is
enforced by nobody: `scripts/build-matrix.py` renders the callouts and never
pairs them. All five levels satisfy it today — 2/2, 3/3, 15/18, 12/12 and 7/7
RED/PATH callouts, level 3's surplus being three REDs that carry two PATH lines
each. A lint would be ten lines, with one subtlety worth stating so the first
attempt does not fail on good prose: on level 4 the RED at `#L13` is followed by
a `> REFUTED:` at `#L14` before its PATH at `#L15`, so "followed by" must mean
"before the next RED or GREEN", not "on the next line".

**Smallest fix.** `.githooks/pre-push` calling the script that already exists.

## G2. The drift report goes silent exactly when every level is up to date

- Tag: tillandsias.org @ c00622b
- Area: `skills/update-website/scripts/drift-report.sh`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** The skill, step 4: "If every level already
pins the stable tag and nothing is broken it prints `ok:up-to-date`; the
daily-channel counts still tell you whether any PATH lines can be updated."

**What the code does.** `drift-report.sh#L64-L73` runs the trial build only when
`repin_needed=1`, which is set only when some level's pin differs from stable.
Today every level pins stable, so the report prints per-level daily-channel file
counts and `ok:up-to-date`, and the one number that matters for planning — how
much work the *next* promotion will be — is never computed. The same script
already knows how to compute it; it just points `TILLANDSIAS_PIN_OVERRIDE` at
stable rather than at the daily.

**What it would take.** Roughly fifteen lines: a second trial build with
`TILLANDSIAS_PIN_OVERRIDE=$daily` whenever `$daily != $stable`, reported
separately as a forecast and never as a failure, and a verdict that carries both
numbers (`ok:up-to-date:forecast:<n>`). Then the scheduling question, which is
the real cost: this repository has no CI and the forge is ephemeral, so a weekly
run needs a home — the runtime's own scheduler, a host session (`plan/host-notes.md`
is the channel), or a Cloudflare cron trigger, which would mean giving the site
worker a `main` and ending `wrangler.jsonc`'s current no-code shape. Pick the
host session first; it needs no new infrastructure.

**What it would catch.** The 121-footnote forecast above, a week before anyone
proposes moving a pin — which turns "we should look at the site" into a number,
which was the candidate's original promise.

**Smallest fix.** Run the trial build against the daily too, and report it as a
forecast.

## G3. Every broken footnote is re-anchored by hand, and the search is mechanical

- Tag: tillandsias.org @ c00622b
- Area: `skills/update-website/scripts/` (no such script)
- Class: defect
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** The skill, step 5: "Correct targets, quotes
and prose in `docs/matrix/<level>.md`", following `audit-site-claims` per level.

**What the code does.** The tooling reports *that* a quote left its range; it
never says where the quote went. Yet for almost all of it the answer is one
command. Measured over today's 121 breakages, by searching each drifted quote in
the whole of its own file at v56.9.5.1: **112 have simply moved** — the same
characters, elsewhere in the same file, needing only a new line range — and
**9 are genuinely gone**, needing a human to write new prose (2 on level 1, 1 on
level 3, 5 on level 4, 1 on level 5: `[^16]`, the withdrawn strong-law wording
of A2). A helper cannot do the nine; it can do the hundred and twelve.

**What it would take.** A `re-anchor.sh <level> <tag>` of about sixty lines that
parses the footnote definitions the way `FN_DEF` does, and for each broken
target prints one of three verdicts: `moved:<path>#L<a>-L<b>` (quote found
verbatim elsewhere in the same file, with the new range), `relocated:<newpath>`
(found in another file), or `gone` (not present anywhere at the tag — a human
writes new prose). Output is a paste-ready block per footnote. All shell over
`grep -F`, `sed` and `git`, no new Python — the measurement above was produced
by a throw-away version of exactly this, in about thirty lines, so the sixty is
for the paste-ready output and the `relocated` case rather than for the search.

**What it would catch.** Nothing by itself — it removes toil, and toil is what
makes a pin bump get postponed. It is also the precondition for G5: a delta
generator can only list "one delta per footnote whose target or quote drifted"
if something can compute the new target.

**Smallest fix.** Write it; it is the smallest script in this list with the
largest effect on how often the loop actually runs.

## G4. Nothing tells this repository that the runtime released

- Tag: tillandsias.org @ c00622b
- Area: `skills/update-website/scripts/latest-release.sh`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** The skill's candidate 2: "Same report,
fired when the runtime publishes a release (the release workflow could ping this
repo, or a cron polls tags)."

**What the code does.** `latest-release.sh` resolves both channels correctly and
cheaply — stable from `/releases/latest` with cache-busting headers, cross-checked
against the newest non-prerelease and the runtime's `stable` git tag; unstable
over `git ls-remote` with no API call at all (`#L6-L19`, `#L32-L39`). It is
polled by a human who remembers to run the loop. Dailies land daily; the pages
pin stable, which moves only on promotion, so the event worth waking up for is
rare and easy to miss.

**What it would take.** Either the runtime's release workflow pings this
repository (cross-repo, needs a credential this forge cannot hold — so a host
session or the enclave mirror would have to carry it), or a cron polls
`latest-release.sh` and opens the G2 report when the stable tag changes. The
second is strictly cheaper and shares G2's scheduler decision; the first is
better and belongs on the runtime's side of the fence, which makes it a request,
not a task.

**What it would catch.** The window between a promotion and someone noticing —
during which the site's PATH lines say "fixed in the daily channel, not yet
promoted" about things that *are* promoted, which is the one lie this design is
specifically built to avoid.

**Smallest fix.** A cron entry on a host session running `drift-report.sh` and
reporting to the operator when its last line is not `ok:up-to-date` —
`plan/host-notes.md` is the channel a host session already has.

## G5. The level-5 delta change is written by hand every time

- Tag: tillandsias.org @ c00622b
- Area: `openspec/changes/level-5-stable-pin-deltas/` (as the worked example)
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim on the site / in the spec.** The skill's candidate 5: "Step 6 for level
5 only: produce the OpenSpec change with the exact deltas and evidence, never
the edit." The requirement it serves is `.../specs/site/level-5/spec.md#L28-L31`:
one delta per requirement, flag or footnote touched, each with `path#Lstart-Lend`
evidence and a verbatim quote at the target tag.

**What the code does.** Today's change was assembled by hand: seven deltas, four
new footnotes, twenty-eight quotes, and a tasks list whose every line had to be
verified twice. The generated part of that is most of it — the drift set, the
new anchors (G3), the quote text at the target tag, and the skeleton of
`proposal.md`/`tasks.md`.

**What it would take.** About 120 lines on top of G3: take a target tag, diff
the cited-file set, run the trial build at the target tag and read level 5's
rows out of it, and emit `openspec/changes/level-5-<tag>/` with
`proposal.md` (one bullet per delta, with
evidence and the quote at the target tag), `tasks.md` (one unchecked box per
delta) and the minimal delta spec `openspec validate --changes` insists on. It
must never touch `docs/matrix/level-5-phd.md` — the spec forbids the edit, and
the generator's value is precisely that it stops short.

**What it would catch.** Deltas quietly omitted from the record. The spec's own
failure scenario — "the page's diff contains a hunk that no delta in the change
lists" — is detectable only if the change lists everything the diff should
contain, and a generator that starts from the drift set does that by
construction.

**Smallest fix.** Build it after G3, and use A2's table as its first test case.

## G6. Re-verification is the part that needs a model, and it is the part to keep reviewed

- Tag: tillandsias.org @ c00622b
- Area: `skills/audit-site-claims/SKILL.md`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05

**Claim on the site / in the spec.** The skill's candidate 4: "An agent per
level with the `audit-site-claims` procedure, then a skeptic per level, then a
human or a second agent reads the diff. Needs a model; not free; the part that
should stay reviewed."

**What the code does.** This run did it by hand, at scale, and the record says
what that cost: "Fifty-four audit agents ran in that phase. Twelve agents then
wrote the pages in the first writing phase, and seven more reviewed and fixed
them in the second" (`docs/audit/2026-09-05-v56.9.2.1.md`, "Method"). It also
says why the skeptic pass is not optional: several corrections came from it
rather than from the first pass, including the two sibling scripts that still
create the enclave network without the isolation flag, and the withdrawal of a
commit-count figure.

**What it would take.** A harness that fans out one agent per level over the
existing `audit-site-claims` procedure, a skeptic per level whose refutations
override, and a gate that refuses to publish until a human has read the diff.
The pieces that make it safe already exist and are cheap: the checked build is
the objective gate (G1), and every claim must carry a `path#L` and a verbatim
quote, which is machine-verifiable regardless of which model produced it.

**What it would catch.** The claims no script can check — a RED that is still
literally true but no longer honest, prose that outran its footnote, a PATH line
that promises something the ledger has closed. It should stay the last candidate
automated and the first to keep a human on.

**Smallest fix.** Not a fix — a sequencing decision: automate G1–G3 first, so
that when the agents do run, the objective failures are already impossible.

---

## Open questions this record does not answer

- **Where a scheduled run lives.** G2 and G4 both need one, and the three
  candidate homes (host session, runtime scheduler, Cloudflare cron) have
  different owners. `plan/host-notes.md` is the only channel to the host agent.
- **Whether the length norm is a norm at all** (B1). It is not written anywhere
  in this repository; the recommendation above assumes the operator wants the
  argument/reference split rather than a word budget.
- **Whether `openspec/specs/` should be populated by archiving the two open
  changes, or left empty until the container-framework change lands too** (A1).
  Three changes are open; the archive directory holds only `.gitkeep`.
- **The published site could not be checked.** `https://tillandsias.org/` is not
  reachable from this forge, so every claim here about what a reader sees rests
  on the committed `var/html/index.html` and its rebuild hash (B3).
