# Research note: evidence ledger

Tracking for [`research-note.md`](research-note.md). **Nothing here is on the
public page.** A row moves to the page only after milestone M3 (re-run,
read down to instances, marked public-safe).

**Source.** The public runtime repository, `github.com/8007342/tillandsias`,
read on 2026-11-13 at commit `6a7abb9c557cc160c6798d7859b3f4a14201cd72`
(integration branch), plus release checkouts `v56.10.9.1` (2026-10-09),
`v56.10.20.1` (2026-10-20) and `v56.11.7.1` (2026-11-07). Paths below are
relative to that repository. Line numbers are at `v56.11.7.1` unless a row
says otherwise.

**This file is public too** (this repository is). So: hosts are written
`<host>`, people are not named, and a source whose *file name* contains a host
name is cited by order id and a search command instead of its path. The
"Scrub" column says what the *source itself* contains, so whoever quotes it
knows what to remove.

**Status vocabulary.**
`counted` = a command was run once and its output is recorded here.
`located` = the incident was found in the repository and its key line read.
`pointer` = known from an agent's working notes only; **not yet found in the
repository**; do not use until located.
No row is `verified` yet: that needs a second independent run (M3).

**Mention versus instance.** Rows marked *mentions* count files that contain a
word. They bound the size of the corpus to read; they are not counts of
incidents and must not be quoted as such.

## 0. Scale of the record (context for all three ideas)

| # | Figure | Value | How | Status | Scrub |
|---|---|---|---|---|---|
| E0.1 | Commits in the runtime repository | 20,899, first 2026-03-21, last 2026-11-13 | `git log --oneline \| wc -l`; `git log --format=%ad --date=short` first and last | counted | none |
| E0.2 | Append-only plan fragments | 6,144 files in `plan/index.d/` | `ls plan/index.d \| wc -l` minus the README | counted | file names end in a host name |
| E0.3 | Event kinds in those fragments | note 3,398; filed 1,305; progress 1,066; completed 872; evidence 89; correction 20; falsified 9 | `grep -rhoE "^\s*-? *type: *[a-z_]+" plan/index.d \| sort \| uniq -c` | counted | none in the counts; every event has a `host:` field |
| E0.4 | Methodology corpus | 27 YAML files under `methodology/` plus `methodology.yaml`, 12,561 lines | `wc -l methodology/*.yaml methodology.yaml` | counted | incident text names hosts throughout |
| E0.5 | Specs and issue write-ups | 186 entries in `openspec/specs/`; 777 files in `plan/issues/` | `ls … \| wc -l` | counted | some issue file names contain a host name |

Caveat for E0.3: older fragments are compacted into `plan/index.yaml`, so
counts over `plan/index.d/` undercount the early months. M3 must decide
whether to count both.

## 1. Peer falsification

| # | Evidence | Value / incident | Source | Status | Scrub |
|---|---|---|---|---|---|
| E1.1 | Recorded falsification events (the only move down the closure ladder) | **9** events. By the claim taken back: 4 × "completed", 3 × "implemented", 2 × "in_progress" | `grep -rhA6 -E "^\s*type: *falsified" plan/index.d \| grep -oE "falsified '[a-z_]+' claim" \| sort \| uniq -c`; rule at `methodology/distributed-work.yaml#L428-L433` | counted; 3 of 9 read | each event names its host; packet ids are internal |
| E1.1a | Caveat on E1.1 | At least one "in_progress" falsification is scheduling bookkeeping (work not started, priority changed), not a disproved claim. The honest figure for "a done-claim disproved" is at most **7**, pending a read of all nine | the event summaries themselves | located | as E1.1 |
| E1.1b | Worked instance | A "completed" claim reopened by a review that found 3 of 4 exit criteria unmet | the 2026-09-26 falsified event (search `falsified 'completed' claim` in `plan/index.d`) | located | host in file name and event; names an internal credential-path finding |
| E1.2 | Correction events | **20** | E0.3 command | counted, none read | as E1.1 |
| E1.3 | One night, four premises endorsed by several agents and each falsified by the first one that measured | **4** premises; "the endorsement chain was longer than the evidence chain"; the coordinator amplified at least twice. Led to the measured / reported / inferred tagging rule | `methodology/distributed-work.yaml#L1496-L1508` (evidence), `#L1479-L1485` (rule), `#L1509-L1516` ("N endorsements are not N evidence": three agents, one measurement) | located | **names four hosts** and a date (2026-08-25); quote the rule lines only |
| E1.4 | Same evening, a cold/warm timing confusion fooled three agents; one retracted its own trend claim within the hour | **3** agents; one phase measured 40,151 ms cold and 814 ms warm on one tree, 2.5 minutes apart (49×) | `methodology/distributed-work.yaml#L1538-L1564` (range approximate; re-anchor) | located | **names three hosts**; timings are from one named machine |
| E1.5 | A self-report of "criterion met" beside its own failing numbers | The implementer reported the criterion met while its measurements read 76 s then 70 s against "under 20 s". Led to the rule that a delegate's report is not an input to acceptance, and to a closure-verifying script | `methodology/distributed-work.yaml#L1888-L1896`; order 1437-gbwi; `scripts/verify-closure.sh` | located | names a model tier (fine); order ids are internal |
| E1.6 | Falsifiers committed before the event | One evening "produced seven self-retractions and at least two claims that lived only in transcripts"; the response was a pre-registration with **6** falsifiers, committed before the release tag existed so the ordering is checkable in git | `plan/issues/exploration-linux-e2e-preregistered-falsifiers-<host>-2026-08-26.md` | located | **host name in the file name and body**; body lists local container and image state |
| E1.7 | Rule: state the falsifier before the numbers | A judgment rule, with the incident that earned it | `methodology/verification.yaml#L277-L285` | located | line 286 names an order id |
| E1.8 | Rule set earned by dated incidents | `methodology/verification.yaml` holds **20** rules, **19** with an `earned_by` incident | `grep -cE "^      - id:" …`; `grep -c earned_by …` (counts at the working commit, not the pin) | counted | most `earned_by` blocks name a host |
| E1.9 | Size of the corpus to read | *mentions*: "falsif" in 171 fragments and 74 of 777 issue files; "retract" in 84 fragments and 25 issue files; commit subjects or bodies matching "falsif" 382, "retract" 144, "self-report" 17 | `grep -rliE … \| wc -l`; `git log -i --grep=… \| wc -l` | counted (mentions) | n/a |
| E1.10 | Enumerated-outcome test handed to a peer instead of a counter-claim | A three-outcome search test, each outcome pointing at a different work item; it came back as the outcome the claimant had not considered | agent working notes, 2026-08-25/26 | **pointer** | names hosts; must be located in the ledger or dropped |

**Not yet gathered:** author-retracted versus peer-forced split; cost per
claim; any comparison period.

## 2. Fail-closed gates

| # | Evidence | Value / incident | Source | Status | Scrub |
|---|---|---|---|---|---|
| E2.1 | Number of guards | **198** check scripts (86 shell, 112 Lua); **211** entries in the gate's step directory; 9 git or tool hooks | `ls scripts/check-*.sh scripts/lua/check-*.lua \| wc -l`; `ls scripts/gate-steps.d \| wc -l`; `ls scripts/hooks` | counted | none |
| E2.2 | "Fail before the fix, pass after" is a written precondition of declaring work ready | The step and the matching "never" clause | `methodology/multi-host-development.yaml#L647-L655` and the `never:` block below it | located | none in those lines |
| E2.2a | How often the record mentions it | *mentions*: "pre-fix" in **1,255** of 6,144 fragments (20%); "mutation control" or "mutant" in 99; "no teeth" or "vacuous" in 84 | `grep -rliE 'pre-fix' plan/index.d \| wc -l` etc. | counted (mentions) | n/a |
| E2.3 | A test asked for a credential gate to be loosened | A security fix pinned the credential helper to one host. A release-tier fixture using a fake upstream then failed (pre-fix result recorded as FAILS, with the helper's refusal quoted). The work item as filed proposed a test-only seam the helper would honour when set | order 1161-42pc and the fix it follows, 1118-bscs (`grep -rl 1161-42pc plan/index.d`) | located (the request) | host in file names; **describes credential handling: have the operator read before quoting** |
| E2.3a | What was done instead | The seam was refused as a token-redirection path; the fixture was changed to ask with an allowed host, the helper was left unchanged, and the refusal became a tested arm with a negative control | agent working notes, 2026-09-13 | **pointer** | as E2.3; locate the closing event for 1161-42pc before use |
| E2.4 | An exit criterion that passed on the unfixed code | The filed criterion ("a stubbed failing push makes the script exit non-zero") passed against the pre-fix script. A mutation control showed it: **26/28** arms pre-fix, **28/28** post-fix, the criterion's own arm green in both. Replaced by an arm shaped like the real failure | `plan/index.yaml` near line 56216 at the working commit (search "THE MUTATION CONTROL CORRECTED THIS PACKET'S OWN TEST DESIGN"); order 1061-zd83 | located | names a host and a release tag state |
| E2.5 | A zero that was not evidence | Verifying six items, **4** checks printed 0 and had never executed (a shell rewrote the command); two present items would have been reported missing | `methodology/verification.yaml#L287-L308` | located | none in the rule; the date is in the incident |
| E2.6 | A null result from a probe that could not match | A scan returned 0 matches in 5 m 20 s; run against a known positive it also returned 0 | `methodology/verification.yaml#L309-L335` (range approximate) | located | **names a host** |
| E2.7 | A planted fault that changed nothing | A setup edit ran, exited 0 and did not apply; the check printed ok. "Third invalid control that host wrote in one day." A second case: a partial mutation built a different, weaker defect | `methodology/verification.yaml#L391-L436` (range approximate) | located | **names two hosts** |
| E2.8 | Counter-evidence the methodology records against its own guards | Two guards on one night made the honest verdict more expensive than the flattering one | `methodology/verification.yaml` rule `a_guard_must_not_penalise_the_honest_verdict` | located | none noticed; re-read |
| E2.9 | Further criterion and control failures | Four mutations in one session that did not apply and "passed"; four green arms asserting nothing; a mutant built from git history that could only be red on its author's machine | agent working notes (orders 1055-6yp8, 1084-nzqc, 1142-85zx; all three ids exist in the ledger) | **pointer** for the details | names hosts |
| E2.10 | Size of the corpus to read | *mentions*: "fail-closed" / "fail closed" in 6 spec files, 1 methodology file, 30 issue files, 50 fragments; 122 commits | `grep -rliE "fail[- ]closed" …`; `git log -i --grep` | counted (mentions) | n/a |

**Not yet gathered:** a count of refusals that stopped a real defect (needs a
definition and a read of the 259 fragments that quote a `refused:` verdict);
wrong refusals and their cost; the share of *fixes* (not fragments) that carry
pre-fix and post-fix evidence.

## 3. Refusal strings treated as interfaces

| # | Evidence | Value / incident | Source | Status | Scrub |
|---|---|---|---|---|---|
| E3.1 | The contract is a spec requirement | "Every refusal names why and what would clear it": verdict token on stdout, `why:` and `remedy:` lines on stderr; the remedy must name a concrete form | `openspec/specs/command-policies/spec.md#L97-L105` | located | none |
| E3.1a | The ruling behind it, and the guard that keeps new refusals from arriving bare | Quoted operator ruling of 2026-09-17; the guard checks only lines a change adds | `scripts/check-refusal-affordance-added.sh#L4-L12` | located | quotes the operator (public file; operator's call whether to quote) |
| E3.2 | **Share of refusal sites that carry a why and a remedy, release over release** | `v56.10.9.1`: 120 of 551 (21.8%). `v56.10.20.1`: 224 of 522 (42.9%). `v56.11.7.1`: 243 of 541 (44.9%). Working commit `6a7abb9c5`: 327 of 533 (61.4%) | `bash scripts/check-refusal-affordance-added.sh --audit \| tail -1` in a checkout of each release; output `audit:refusal-affordance:covered=<c> bare=<b> sites=<n>`. The script does not exist at `v56.9.27.2` or earlier | counted, one run each | none. **Strongest figure so far**; a reader can reproduce it |
| E3.2a | Caveats on E3.2 | The audit covers shell scripts and `build.sh` only, not Rust or Lua. "Covered" is a text heuristic (a helper call, or why + remedy words within a window), and a marker can exempt a machine-read verdict. It measures presence of a remedy, not whether the remedy is right | the script's own header, lines 14–37 | located | none |
| E3.3 | Verdict vocabulary in use | **316** distinct `refused:<name>` tokens in scripts and crates. Token occurrences by verdict word: ok 2,496; refused 1,508; blocked 856; violation 837; warn 106; drift 26; unmet 13; unscoreable 8; advised 6 | `grep -rhoE "refused:[a-z0-9_-]+" scripts crates --include=*.sh --include=*.lua --include=*.rs \| sort -u \| wc -l` and the same with the verdict-word alternation | counted | none. Includes tests and fixtures; M3 should split emitters from expectations |
| E3.4 | A verdict rename with a missed consumer | A credential guard's answer was renamed on purpose (the old token's remedy was a disruptive re-authentication). Two consumers were found and reconciled; a third, a test step pinning the old string, failed later and only at the release tier | order 1347-r9g8 (20 fragments mention it; the filing fragment records the old token and a "one emitter per verdict string" finding) | located (the rename and the old token); **pointer** for the missed third consumer | host in file names; **about credential state on named machines: operator reads before quoting** |
| E3.5 | The same failure for what a script reads | A one-line change to where a helper resolves a file broke six fixtures that build scratch trees; two release-tier tests went red | order 1337-3tk6 (10 fragments) | **pointer** for the counts | names a host |
| E3.6 | An exit code shared by "denied" and "could not run" | A hook's deny must carry its verdict in text, because the exit status alone is ambiguous | agent working notes | **pointer**; not found by a first search | unknown |
| E3.7 | Refusals in use by agents | *mentions*: 259 of 6,144 fragments quote a `refused:<name>` verdict; the work item that drove the conversion (1247-amcu) is cited in 33 fragments | `grep -rlE 'refused:[a-z]' plan/index.d \| wc -l` | counted (mentions) | n/a |

**Not yet gathered:** a list of every verdict rename with the size of its
sweep; any case where a bare refusal demonstrably sent an agent the wrong way;
any measurement of recovery time with and without a remedy line (none is
known to exist; the note should say so).

## 4. Before publishing: the scrub list

Everything below is in the public runtime repository already. The site's rule
is stricter than "already public": the page names no machine, session or
person.

- **Host names** appear in: `plan/index.d/` file names and every event's
  `host:` field; the incident text of `methodology/distributed-work.yaml`
  around lines 1486–1575; most `earned_by` blocks in
  `methodology/verification.yaml`; some `plan/issues/` file names. Quote rule
  lines, not incident lines, or paraphrase with "one machine" / "a peer".
- **People.** The 2026-09-17 ruling is attributed to "the operator" in the
  source. The site's Home already carries the author's name by their own
  choice; whether the note quotes the ruling is theirs to decide.
- **Credentials and security posture.** E2.3 and E3.4 describe how a
  credential helper and a keyring behave on specific machines. Nothing secret
  is in the rows above, but the operator should read both sources before
  either becomes a worked example.
- **Local machine state.** The pre-registration file in E1.6 lists container,
  image and installed-version state for one machine. Cite the idea, not the
  listing.
- **Internal identifiers.** Order ids (`1161-42pc` and the like) are used here
  to find things. `docs/matrix/README.md` keeps them out of page prose; on the
  page they belong in link targets only.
- **This repository.** `plan/README.md` already names a host in its reader
  table. That predates this work and is left for the operator to decide.

## 5. Reproducing a row

Counts over `plan/index.d/` and `git log` change with every commit. To re-run
a row, check out the commit named at the top (or record the new one), run the
command in the "How" or "Source" column unchanged, and write the output and
date under the row. Use `grep -F` or escape `$` in patterns; pipe nothing
through `head` when counting.
