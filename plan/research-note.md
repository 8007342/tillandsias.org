# Workstream: the research note on the Methodology page

**Status:** 🟡 **JUMPSTARTED 2026-11-13** — page and stubs built, first evidence
pass done, nothing published as a result yet.
**Target:** published by **2026-12-31**.
**Opened:** 2026-11-13, on the operator's direction of that day.
**Owner:** the operator writes the argument. Agents outline, gather evidence,
check numbers and edit. An agent does not write the final prose as if it were
the operator's; stubs, theses and edit suggestions are fine.
**Design:** [`openspec/changes/methodology-page-and-research-note/`](../openspec/changes/methodology-page-and-research-note/)
**Evidence:** [`research-note-evidence.md`](research-note-evidence.md)

---

## 1. What this is

A short research note, with numbers, on three ideas from the Tillandsias
methodology:

1. **Peer falsification.** Agents hand peers a test with enumerated outcomes
   instead of a claim; a self-report counts only as evidence.
2. **Fail-closed gates.** Guards refuse on doubt; a credential gate is never
   weakened for a test; an exit criterion must fail on the pre-fix code.
3. **Refusal strings treated as interfaces.** The `refused:<name>:<detail>`
   verdict plus `why:` and `remedy:` lines; changing a verdict token needs a
   sweep of its consumers.

It lives at `#research-note` on the site (menu → Methodology). It also serves
as the operator's writing sample for research programmes (MATS Residency,
Anthropic Fellows) and grant applications, so it has to stand on its own for a
reader who has never seen the project.

## 2. Rules for this work

- **The site is fleet-agnostic.** No host names, session details or private
  infrastructure on the page. This repository is public too, so the same holds
  for this file and the evidence file: sources are cited by path and id, hosts
  as `<host>`.
- **No number reaches the page before M3.** A count on the page must be
  reproducible by a reader from the public runtime repository at a named
  release, with the command recorded.
- **A mention is not an instance.** Most counts gathered so far are grep
  counts of mentions. Each must be read down to instances before it is used.
- **Say what counts against the idea.** Each idea's evidence list includes the
  costs and the failures (wrong refusals, missed consumers, weak controls).

## 3. Milestones and exit criteria

| # | Milestone | Who | Target | Exit criterion |
|---|---|---|---|---|
| M1 | **Outline** | agent drafts, operator accepts | 2026-11-24 | For each of the three ideas, this file holds: the claim in one sentence, what observation would count against it, the 2–4 incidents chosen as worked examples, and the figures the note will quote. The operator has marked the outline accepted in the session log. |
| M2 | **Draft** | operator | 2026-12-08 | A complete draft in the operator's own words exists in this repository (as `plan/research-note-draft.md` or on a branch). Every figure in it is a placeholder keyed to a row of the evidence file. No agent-written paragraph is in it. |
| M3 | **Numbers verified** | agent, then a second agent or the operator re-runs | 2026-12-15 | Every figure the draft uses has, in the evidence file: the command, the runtime release or commit it ran at, the output, and a second independent run that matched. Every "mention" count the draft relies on has been read down to instances. Every row is marked `public-safe: yes` or has been dropped. |
| M4 | **Operator voice pass** | operator | 2026-12-22 | The operator has read the whole note aloud-speed, start to finish, after M3, and recorded "voice pass done" in the session log. Agent edits after this point are limited to typos and broken links. |
| M5 | **Published** | agent builds, operator merges | 2026-12-31 | The note replaces the stubs at `#research-note`; `checked-build.sh` prints `ok:checked-build`; every figure on the page links to its source; the PR is merged by the operator and the page is live. The "in progress" label and this file's status are updated the same day. |

Slack: nine days between M4 and M5. If M2 slips past 2026-12-15, cut scope to
two ideas rather than publish unverified numbers.

## 4. Outline (M1, started)

Each idea below: the claim, what would count against it, candidate worked
examples (see the evidence file for sources and status).

### 4.1 Peer falsification

- **Claim.** A claim that travels with the test that would kill it converges
  faster and more reliably than a claim that travels with endorsements.
- **Against it.** Retractions that only happened because the operator
  intervened; claims that survived a peer's test and were still wrong; the
  method's cost being larger than the errors it removes.
- **Candidate examples.** E1.3 (four endorsed premises, each falsified by the
  first measurement), E1.5 (a self-report of "met" beside its own failing
  numbers), E1.6 (falsifiers committed before the event).
- **Open question for the operator.** Is the note about agents specifically,
  or about any group that reports to itself? The evidence is all agents.

### 4.2 Fail-closed gates

- **Claim.** "Refuse when you cannot decide" is one rule with three faces:
  could-not-run is not a pass, a credential gate is not loosened for a test,
  and a criterion must be seen to fail before the fix.
- **Against it.** Wrong refusals and what they cost; gates that were green and
  proved nothing; honest verdicts that a guard made more expensive than
  flattering ones (the methodology records this one itself).
- **Candidate examples.** E2.3 (a test-only credential seam refused; the
  fixture was changed instead), E2.4 (a criterion that passed on the unfixed
  code, found by a mutation control), E2.5 (four checks that printed zero and
  never ran).

### 4.3 Refusal strings as interfaces

- **Claim.** When the reader is an agent, a refusal is an interface: it needs
  a stated remedy, and renaming it is a breaking change.
- **Against it.** No measurement yet shows that a remedy line shortens
  recovery; the share of refusals that carry one is rising but well short of
  all; a careful rename still missed a consumer.
- **Candidate examples.** E3.2 (the share of refusal sites with why and
  remedy, release over release), E3.3 (a verdict rename with two consumers
  reconciled and a third missed), E3.4 (a shared exit code for "denied" and
  "could not run").

## 5. Open questions for the operator

1. Length and form: a 1,500–2,500 word note with one small table per idea, or
   something shorter?
2. May the note name order ids and link to ledger entries in the runtime
   repository? Those paths are public, and some file names contain host names.
3. Should the note say how many machines and agents were involved, without
   naming them? A reader will want the scale.
4. The comparison period (before the rules existed) is weak: the rules were
   adopted because of the incidents. Is "no control, and here is why" an
   acceptable answer for the note?

## 6. Session log (append only)

- **2026-11-13** — Jumpstart. Built the Methodology page with the three stubs;
  wrote the OpenSpec change; first evidence pass against the runtime
  repository at commit `6a7abb9c5` and at four pinned releases (see the
  evidence file). MCP note: the runtime's methodology expert routes a fixed
  table of questions and returned `unsupported` for all three ideas, so the
  evidence was gathered by reading and counting files directly; the spec
  expert returned retrieval-only citations for idea 3, which were used.
  Not done: no instance-level reading of the mention counts, no second run of
  any figure, no operator review. Next: M1 — the operator picks the worked
  examples and answers §5.
