# Separate a measurable residual from a convergence guarantee

Scoped follow-up to BigPickle's stable v56.9.27.2 audit (website b3f3091).
The operator requested a challenge to Level 5's missing metric, using the Lua
runtime and CentiColons. Keep the stable pin and all unrelated sections.
This proposal records website deltas, not authority to change runtime policy.
Leave it unarchived for operator review.

## Individually justified Level 5 deltas

1. Replace the equation of validator fixed point with completion. A fixed
   point can retain unmet obligations; methodology/math-foundations.yaml
   lines 200–206 explicitly says fixed points mean validator stability.
2. Add a concrete candidate residual for a fixed finite scope, positive
   integer weights and explicit closure predicates. Distinguish measurement,
   per-obligation non-regression and strict progress. Prove the conditional
   K*R0 cycle bound, without asserting that the runtime supplies its premise.
   This instantiates the existing residual-floor caveat (footnote 11), not a
   contraction theorem or a probability model.
3. Qualify the ranking-function paragraph: earned credit ascends; its
   residual is a termination witness only when progress forces descent.
   A bounded non-increasing integer sequence can plateau above zero.
4. Replace the Lua PATH overclaim and add stable-source footnotes. At
   v56.9.27.2, lua_predicate.rs lines 69–90 separates capabilities;
   centicolon-grade-static.lua lines 180–201 shares requirement candidates
   across scenarios; centicolon-grade-observed.lua lines 38–105 selects
   latest by test/digest, accepts incomplete subject provenance and computes
   a raw positive-test residual. centicolon-extract.lua lines 258–266 emits
   invariants separately. check-centicolon-ratchet.sh lines 4–29 and 77–115
   warns, compares a local untracked baseline, and exits zero. These are
   source-inspection findings, not claims of new runtime exploit tests.
5. Qualify the conclusion: CentiColons operationalize declared uncertainty,
   but trustworthy evidence, policy alignment and enforced comparison remain
   prerequisites; finite-time completion needs the extra progress premise.
6. Clarify the paragraph added in BigPickle's audit: evidence can support
   tested behavior without a Galois connection. Absence of that connection
   withholds the abstract-interpretation transfer theorem, not all empirical
   knowledge. A configured positive-test bar is not evidence_bundled.

## CentiColon page deltas

Preserve sections, example figures, weights and navigation. Correct modern
Stockfish's centipawn analogy using its official WDL documentation; remove a
guarantee of victory. Label the binary worked example as a simplified model,
distinct from methodology/proximity.yaml's partial credits/caps/penalties and
the Lua raw count. Require applicable evidence for closure; explain that an
aggregate improvement can conceal a regression. Label invariant/environment
integration as proposed and remove an unmeasured milliseconds guarantee.
Add links to stable source and the Level 5 explanation.

## Verification

Independent skeptical source review precedes page edits. Record corrections
as a scoped audit addendum and an append-only retraction in issues.d. Run
the checked build with all pinned/historical checkouts, ledger validation,
HTML identifier/link checks and a same-HEAD reproducibility check. No full
runtime test, new five-level audit or deployed-site claim is implied.
