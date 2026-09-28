# Scoped CentiColon and Level 5 correction

Follow-up to BigPickle's [stable audit](2026-09-28-v56.9.27.2.md), website
b3f3091cb6d21b47349e2b407c46981d9d34b515. Stable pin remains v56.9.27.2,
runtime commit 52e3bc32ec063c7a7090d0c8dca35bb8ade3c844. This is a targeted
claim review, not another complete five-level semantic audit.

## Result

CentiColons operationalize declared evidence debt; they do not yet establish
enforced monotonic reduction. A complete subject/assertion/platform evidence
contract, aligned units, per-obligation comparison and a durable accepted
baseline are missing prerequisites. A non-increasing residual may plateau.
For fixed finite scope and positive integer weights, a decline of at least
one within each next K cycles while positive suffices for the K*R0 bound.
The premise is not proved by adding a score, Lua, or an advisory alarm.

The prose now distinguishes the binary weighted example, the full policy
and the shipped raw positive-test residual. It also distinguishes validator
stability from completion, and empirical test evidence from a sound abstract
interpretation of all executions. Modern Stockfish's calibration is linked
to its official WDL documentation; the analogy carries no victory guarantee.

## Evidence and skeptical review

The main reviewer read each cited stable span; an independent read-only
reviewer tried to refute the proposed changes, then reviewed the written diff.
The second pass corrected three remaining overclaims: explained retractions
break non-regression too; the bounded-progress condition is sufficient, not
necessary; and the Rust comparison warning differs from the Lua advisory.

| Claim | Stable evidence inspected | Status |
| --- | --- | --- |
| Fixed point means stability | methodology/math-foundations.yaml#L61-L74, #L200-L206 | confirmed; completion claim withdrawn |
| Runtime capability separation | crates/tillandsias-plan/src/lua_predicate.rs#L69-L96 | implemented; no adequacy or latency theorem |
| Scenario-level attribution | scripts/lua/centicolon-grade-static.lua#L154-L201 | partial: candidates shared by requirement |
| Subject and platform applicability | scripts/lua/centicolon-grade-observed.lua#L38-L105 | partial: latest test/digest; conditional spec check |
| Invariant grading | scripts/lua/centicolon-extract.lua#L258-L266 plus static loop | extracted separately, not consumed by grader |
| Accepted non-regression baseline | scripts/check-centicolon-ratchet.sh#L4-L29, #L77-L115 | absent: local advisory snapshot advances after loss |
| Weighted full policy | methodology/proximity.yaml#L27-L45, #L66-L135 | declared; not equivalent to binary example/raw count |
| Positive-test credit vs bundled evidence | crates/tillandsias-plan/src/obligation.rs#L640-L646 | explicitly distinct |

The source review also confirmed producer limitations:
scripts/run-litmus-test.sh#L2161-L2174 serializes advisory as pass, and
#L2313-L2339 hashes test/spec files at suite emission, not implementation
dependencies. These are source observations, not new exploit executions.
The runtime research branch records the implications for the evidence contract.

## Scope and checks

- Level 5: 45 existing footnotes retained, six new stable-source citations
  manually read; all 51 mechanically checked. No pin or unrelated level edit.
- One new RED/PATH pair names the evidence/enforcement gap; one existing
  scoring PATH is corrected. Fixed-point, ranking and conclusion prose are
  narrowed. No new theorem is attributed to the shipped program.
- CentiColon examples and three figures retained; arithmetic independently
  checked: budget 460, earned 0 -> 80 -> 340, residual 460 -> 380 -> 120.
- Home, Slides, install commands, navigation and figure assets unchanged.
  Progress gains a reasoned retraction, not a runtime-resolution claim.
- Checked build passes against every pinned/historical checkout; all level
  citations resolve. Findings ledger: 62 findings, 11 fragments.
- Generated HTML: 941 unique identifiers, no duplicates; 375 fragment links
  resolve either to identifiers or declared tab routes; 16 slides retained.
- Repeated checked builds at the same HEAD are byte-identical (SHA-256
  recorded in the terminal verification); no live browser/deployment claim.

The unarchived OpenSpec change is
`openspec/changes/level-5-centicolon-guarantee/`. Finding 1b27ef15 records
the published overclaim and its retraction. This corrects website copy; it
does not complete runtime implementation or adopt the proposed scoring policy.
