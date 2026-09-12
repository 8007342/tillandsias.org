# Refresh level 5 against stable v56.9.12.2

Preserve the argument and manual additions while applying only the individually justified deltas below. Tests on a committed model are not a theorem about live validators; withdrawal of a mathematical citation is an improvement in accuracy.

## D1

Model and IDs landed; old introduction is stale.

Before:

Two of its load-bearing hypotheses are assumed rather
than discharged, and the instrumentation that would test them does not exist.

After:

Its model now has generative property tests and stable requirement identifiers.
Connecting those checks to live validation and justifying dependent iteration remain
separate obligations.

## D2

Distinguish fixture model from real validator proof.

Before:

which is exactly
the right shape of obligation, and exactly what is not run.

After:

which is the right shape of obligation. That program now has executable tests
over a committed rule set; it does not establish the same properties for every live validator[^41].

## D3

Replace missing dependency/model claim with implemented test boundary.

Before:

> RED: The fixed-point argument's load-bearing hypothesis is monotonicity of the refinement operator, and monotonicity is assumed, not proved. The repository's own discharge procedure is generative property testing over reachable obligation states; the workspace contains no property-testing dependency at all — no `proptest`, no `quickcheck`, in any crate manifest. What would be needed is modest and specific: an enumeration of the permitted transition relation, plus a proof or a generative test that every transition is order-preserving in each affected coordinate, with tombstones and scope changes excluded as declared non-monotone.
> PATH: The checks are specified as phase one of a staged validation program[^9]. That phase was unimplemented at this release; implementing the model and its generative property tests was filed as scheduled work on 2026-09-03. The prerequisite is the sharper half: there is nothing to property-test until the obligation model exists as code rather than as prose. The obligation model and its generative property tests landed on 2026-09-03 and reached the daily channel in v56.9.4.1, cut 2026-09-04, over a committed rule set rather than the live validators, and are not yet in the stable channel[^41].



After:

> RED: The refinement model has generative tests for monotonicity, inflationarity and idempotence, but they exercise a committed rule set rather than every live validator[^41]. They establish a model boundary, not semantic correctness of the running system.
> PATH: The staged validation program names the remaining obligation: enumerate permitted transitions and check every affected coordinate, treating tombstones and scope changes separately[^9].



## D4

Stable IDs are implemented; preserve semantic identity limitation.

Before:

> RED: The lattice's coordinates are mostly not instantiated. The obligation model is indexed by stable requirement identifiers, but no specification file in the tree carries a requirement identifier field — requirements are named by prose headings, against several thousand RFC-2119 keywords. The credit term that prices this, `requirement_has_stable_id`, occurs exactly once in the entire repository: in the weight table that defines it[^10]. Nothing reads it. A product order over coordinates that do not exist is a well-formed object over an empty index.
> PATH: Priced in the scoring rules but not gated on, and unscheduled at this release. A migration to stable random identifiers was filed on 2026-09-03, carrying the rule that a refinement preserving the original intent keeps its identifier while a change of meaning becomes a tombstone plus a new one — a boundary that is author judgement and cannot be enforced by a validator, so the documentation must say so rather than imply a guard covers it. Landed on 2026-09-03 and in the daily channel from v56.9.4.1, cut 2026-09-04: every requirement received a stable random identifier and a gate check now refuses a missing or duplicated one[^42]; nothing yet computes the credit term.



After:

> GREEN: Requirement identifiers now exist and a gate checks presence and uniqueness, including tombstoned specifications[^42]. Whether an edit preserves meaning and should keep its identifier remains author judgement; the guard cannot decide that. The evidence-credit table still lists stable identifiers as a scoring input[^10], which by itself does not establish that credit is computed.



## D5

Remove false no-instrumentation claim and incorrect ratio solution; bound local regime checking.

Before:

There is a further objection the repository has not addressed. If $d_v$ were the
CentiColon residual, it is integer-valued, and a non-increasing integer sequence
bounded below is eventually constant — stronger than Proposition 4, and it would
make $d_* = 0$ decidable in finitely many steps under any strict-progress premise.
But the residual is computed against a denominator that is policy and may change per
release[^15]. Then $d_{v+1} \le d_v$ compares two integers drawn from different
scales, and the inequality is not scale-invariant: a release can lower its residual
by enlarging its denominator.

> RED: The release-boundary inequality is stated over a quantity whose codomain is allowed to change between the two terms being compared. Nothing normalises residuals across a denominator change, so non-increase is a comparison between two differently-scaled integers. A ratio $d_v/N_v$ would be comparable and is not what is checked.
> PATH: A phase-two check requiring denominator changes to emit an explicit scope-change signal is specified[^9]; it is unimplemented, and no normalisation rule is recorded even in specification. In the daily channel the ranking function in code now labels a score whose denominator lost a tombstoned obligation as not comparable, and the script prints that label[^44]; still no normalisation rule is recorded.



After:

There is a further boundary. Under a fixed denominator, a non-increasing integer
residual is eventually constant; strict progress while positive would force zero.
Changing the obligation scope breaks that comparison. A ratio alone cannot repair
it: adding easy obligations can improve the percentage without closing an old gap.

> RED: The scorer marks a tombstone as a broken monotone regime, and the shell reports that regime[^44][^45]. This is useful local instrumentation, but does not establish a cross-release comparison for arbitrary changes of weights or obligation scope.
> PATH: The validation program requires denominator changes to be reported separately[^9]. A complete cross-release comparison must align the obligation set and weights; no general normalisation rule is established by the cited implementation.



## D6

SLLN withdrawal is stable now.

Before:

This is the intellectual core[^16]. Set it up properly.

After:

The methodology now withdraws its strong-law citation for dependent iterations[^16].
The mathematics below explains why that correction matters. Set it up properly.

## D7

Doctrine no longer invokes theorem.

Before:

the version the doctrine
actually needs is Kolmogorov's variance criterion

After:

a candidate generalisation is Kolmogorov's variance criterion

## D8

Old bias inference and green distinction overclaim; preserve rigorous conditional theorem.

Before:

Weak versus strong is convergence in probability versus almost-sure convergence, and
the implication runs one way: a.s. $\implies$ in probability, never the converse.
The repository states the split in its correct form and, more importantly, correctly
identifies the term that defeats iteration: not the variance, which averages away
under the criterion above, but the bias. If $|b_k| \le \beta$ then $|\bar b| \le \beta$
and the stream converges to within $\beta$ of truth; if skew is unbounded, or bounded
away from zero at the end of every prompt, $\bar X_N$ converges almost surely to the
*wrong number* and more iterations do not help. The file says exactly this — *"if a
prompt's skew is not bounded, infinite iterations do NOT converge hard"*[^16]. That
is a hypothesis of the theorem being named as one, which is more than most
engineering essays manage.



After:

Weak versus strong is convergence in probability versus almost-sure convergence;
almost-sure convergence implies convergence in probability, but the converse need
not hold. Under the criterion above and existence of the mean-bias limit, bounded
bias bounds the limiting error. Bounded bias alone does not imply convergence,
and unbounded skew does not by itself prove divergence. The methodology retains
small, fast iterations as engineering guidance while withdrawing the almost-sure
claim[^16].



## D9

Withdrawal acknowledges dependence.

Before:

Now the objection the methodology does not address, and it is the load-bearing one.

After:

The objection the methodology now acknowledges is the load-bearing one.

## D10

Avoid promising substitutes without hypotheses.

Before:

Two substitutes would serve, neither argued.

After:

Two possible substitutes remain unestablished.

## D11

Withdrawal closes former RED; remove inaccurate weak-LLN praise.

Before:

> RED: The methodology invokes the strong law of large numbers to license almost-sure convergence of the iteration stream, four lines above the passage describing the retrieval cache that makes consecutive iterations dependent by design. The theorem is applied outside its hypotheses, in the same block that documents why the hypotheses fail.
> PATH: Corrected on 2026-09-03, after the release this page cites — so the passage quoted above is the pre-fix text, and the citation is left pinned to it deliberately. The almost-sure claim was **withdrawn rather than weakened**, at both sites that carried it: the guiding principle a reader meets first, and the detailed block beneath it. What a rigorous claim would require is now written into the file — Birkhoff with stationarity and ergodicity argued, or a martingale law with the conditional-mean condition argued — and the empirical release-boundary record becomes the load-bearing statement, described as a track record rather than a theorem. Nothing about the iteration design changed, and nothing machine-reads the corrected block, so the blast radius is documentation only.

> GREEN: The weak/strong distinction is stated in the correct direction with the bias term, not the variance, identified as what defeats iteration — the version most treatments get backwards.



After:

> GREEN: The methodology explicitly withdraws the strong-law citation because the cache makes successive iterations dependent[^16]. It names ergodic and martingale hypotheses as work needed for a future theorem, and presents the iteration practice as an empirical track record rather than an almost-sure guarantee.



## D12

Credit actual model integration, preserve missing full arithmetic and snapshot caveat.

Before:

> RED: What computes the score is not the specified arithmetic. A sixteen-arm hardcoded weight table over CI check names in a shell script produces it[^27], and the committed dashboard's 890/990 is that pass-rate[^28]. None of the base weights, multipliers, cap rules or sixteen penalties in the methodology are computed anywhere in the tree.
> PATH: The framework specification delegates the arithmetic to a named crate and modules[^29]; that crate is a README and one `.rs.example` file, and is not a workspace member. Ruled on 2026-09-03: the two are to be the same object, the shell scorer is to call the model rather than reimplement it, completed work is to be backfilled retroactively, and the requirement is to be hard-enforced going forward rather than requested. The three parts of the ruling were executed the same day, and reached the daily channel in v56.9.4.1, cut 2026-09-04 — the shell scorer hands its weights to the model[^43], completed work was backfilled where the ledger pins the evidence (a small fraction of rows), and a gate refuses new obligations the score cannot see.



After:

> RED: The shell scorer now delegates arithmetic to the obligation model[^43], but still supplies weights over CI check names[^27]. A passing check earns its weight at the positive-test bar; it is not runtime observation or bundled evidence. This wiring does not implement the full methodology table of multipliers, evidence credits, caps and penalties[^15]. The committed dashboard remains a historical 890/990 snapshot[^28], not a measurement of this release.
> PATH: The framework specification still names a separate scoring implementation[^29]. The shipped path centralises the arithmetic; completing and evidencing the richer scoring contract remains distinct work.



## D13

Remove brittle counts and never-fired inference pending skeptic.

Before:

is itself 1,739 lines and the shell corpus it dispatches into exceeds 78,000.

After:

has grown beyond that documented red-flag threshold when considered with the validators it dispatches.

## D14

Absence of found check is not proof it never fired.

Before:

is uninstrumented and has never fired,

After:

has no enforcing check identified in this audit,

## D15

Bound negative search claim.

Before:

> PATH: The rule names two measurement procedures; neither is implemented as a check.

After:

> PATH: The rule names two measurement procedures[^30]; no enforcing implementation was found in the scripts searched.

## D16

Correct mathematical overreach without deleting version discussion.

Before:

> GREEN: The version scheme is argued correctly as a join-semilattice — SemVer has no natural total order under merge because patch counters reset and collide, destroying causality, whereas a temporal anchor joined componentwise by max does have least upper bounds[^37].

After:

> GREEN: Componentwise maximum gives version tuples a join-semilattice. The document uses that algebra to motivate mergeable version coordinates[^37]. Its claim that SemVer has no natural total order is too broad: version precedence and preservation of branch causality are different properties.

## D17

Verdict must reflect actual improvements and surviving limits.

Before:

Two things stop it being finished mathematics. The fixed-point argument runs on a
monotonicity hypothesis that is asserted rather than proved, over a coordinate set
that is largely uninstantiated. And the iteration doctrine, the most ambitious part,
invokes laws that require independence for a process the same document designs to be
self-referential. Neither is fatal; both are the sort of thing a referee returns for
revision rather than rejection. Use the mathematics. Discount the dashboard.



After:

Two boundaries remain. Generative tests cover the committed refinement model,
not the semantic correctness of all live validators. And dependent iteration
still lacks a convergence theorem, although the methodology now retracts the
unsupported strong-law claim. Stable identifiers and centralised score arithmetic
make the bookkeeping more concrete; they do not turn closure into probability
or a dashboard snapshot into release evidence.



## D18

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^10]: The evidence-credit table containing `requirement_has_stable_id` | methodology/proximity.yaml#L47-L57
    > requirement_has_stable_id: 0.10

After:

[^10]: The evidence-credit table containing `requirement_has_stable_id` | methodology/proximity.yaml#L88-L97
    > requirement_has_stable_id: 0.10

## D19

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^11]: Multi-version convergence: the moving target, the residual floor, and the refusal of the zero-floor claim | methodology/philosophy.yaml#L103-L121
    > Release-over-release non-increase of d_v guarantees convergence to some residual floor d_* >= 0; it does not by itself prove d_* = 0. A zero-floor claim would additionally require a validated progress premise that excludes positive residual fixed points

After:

[^11]: Multi-version convergence: the moving target, the residual floor, and the refusal of the zero-floor claim | methodology/philosophy.yaml#L134-L137
    > Release-over-release non-increase of d_v guarantees convergence to some residual floor d_* >= 0; it does not by itself prove d_* = 0. A zero-floor claim would additionally require a validated progress premise that excludes positive residual fixed points

## D20

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^15]: The cap rules, the sixteen penalties, and the rollup that makes the score non-additive in its parts | methodology/proximity.yaml#L60-L97
    > requirement_cc = weighted_obligation * earned_credit + penalties bounded to [0, weighted_obligation].

After:

[^15]: The cap rules, the sixteen penalties, and the rollup that makes the score non-additive in its parts | methodology/proximity.yaml#L100-L135
    > requirement_cc = weighted_obligation * earned_credit + penalties bounded to [0, weighted_obligation].

## D21

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^16]: Weak versus strong LLN, bounded per-prompt skew, and the unbounded-skew hazard | methodology/philosophy.yaml#L8-L31
    > then iterate — the STRONG LLN (almost-sure convergence) makes the stream of iterations converge hard. The hazard is uncontrolled skew sneaking in at the END of every individual prompt: if a prompt's skew is not bounded, infinite iterations do NOT converge hard.

After:

[^16]: The strong-law citation withdrawn for dependent iteration | methodology/philosophy.yaml#L29-L47
    > So the almost-sure claim is not available as stated and is withdrawn rather than weakened.

## D22

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^19]: Retrieval as a cache; commits as the Lamport clock versioning it — the mechanism that makes iterations dependent | methodology/philosophy.yaml#L32-L39
    > That cache is updated on COMMITS — a commit hitting the relevant bits retrains the RAG. Commits are therefore the LAMPORT CLOCK of the RAG models: they causally order and version the cached knowledge against the code

After:

[^19]: Retrieval as a cache; commits as the Lamport clock versioning it — the mechanism that makes iterations dependent | methodology/philosophy.yaml#L54-L57
    > That cache is updated on COMMITS — a commit hitting the relevant bits retrains the RAG. Commits are therefore the LAMPORT CLOCK of the RAG models: they causally order and version the cached knowledge against the code

## D23

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^27]: What actually computes the score: a sixteen-arm hardcoded weight table over CI check names | scripts/local-ci.sh#L384-L403
    > check_weight() { case "$1" in spec-cheatsheet-binding) echo 100 ;; spec-code-drift) echo 120 ;; spec-trace-coverage) echo 90 ;; version-monotonicity) echo 40 ;;

After:

[^27]: The shell still supplies weights over CI check names | scripts/local-ci.sh#L384-L403
    > check_weight() { case "$1" in spec-cheatsheet-binding) echo 100 ;; spec-code-drift) echo 120 ;; spec-trace-coverage) echo 90 ;; version-monotonicity) echo 40 ;;

## D24

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^29]: The framework specification delegating CentiColon arithmetic to a crate that is a README and one example file | methodology/litmus-framework.yaml#L88-L96
    > files: - crates/tillandsias-litmus/src/convergence/mod.rs - crates/tillandsias-litmus/src/convergence/centicolon.rs

After:

[^29]: The framework specification names its intended scoring implementation | methodology/litmus-framework.yaml#L88-L96
    > files: - crates/tillandsias-litmus/src/convergence/mod.rs - crates/tillandsias-litmus/src/convergence/centicolon.rs

## D25

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^34]: Commutativity and idempotence of the fold pinned as named tests | crates/tillandsias-plan/src/fragments.rs#L2648-L2668
    > fn the_fold_is_commutative_the_defining_crdt_property() { Order of arrival must not change the result.

After:

[^34]: Commutativity and idempotence of the fold pinned as named tests | crates/tillandsias-plan/src/fragments.rs#L2853-L2886
    > fn the_fold_is_commutative_the_defining_crdt_property() { Order of arrival must not change the result.

## D26

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^41]: Generative property tests for monotonicity, inflationarity and idempotence of the refinement operator, over a committed rule set | crates/tillandsias-plan/src/obligation_props.rs#L172-L219 @v56.9.5.1
    > MONOTONICITY over the real rule set — what Knaster-Tarski actually needs and what the methodology's idempotence check never examined. #[test] fn refine_is_monotone_on_the_real_rules((x, y) in comparable_pair()) {

After:

[^41]: Generative property tests for monotonicity, inflationarity and idempotence of the refinement operator, over a committed rule set | crates/tillandsias-plan/src/obligation_props.rs#L172-L219
    > fn refine_is_monotone_on_the_real_rules((x, y) in comparable_pair()) {

## D27

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^42]: The gate that refuses a missing or duplicated requirement identifier, and states what it cannot check | scripts/check-requirement-ids.sh#L5-L35 @v56.9.5.1
    > Every spec requirement carries a stable identifier, and no two carry the same one.

After:

[^42]: The gate that refuses a missing or duplicated requirement identifier, and states what it cannot check | scripts/check-requirement-ids.sh#L5-L6
    > Every spec requirement carries a stable identifier, and no two carry the same one.

## D28

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^43]: The shell scorer hands its weights to the model instead of summing them itself | scripts/local-ci.sh#L538-L563 @v56.9.5.1
    > What LEFT is the arithmetic: earned/denominator/residual are now computed by `tillandsias-plan score-checks`, which runs obligation::centicolon_function over a SpecState.

After:

[^43]: The shell scorer hands its weights to the model instead of summing them itself | scripts/local-ci.sh#L542-L544
    > What LEFT is the arithmetic: earned/denominator/residual are now computed by `tillandsias-plan score-checks`, which runs obligation::centicolon_function over a SpecState.

## D29

Reverify citation at new stable release; preserve unchanged ranges where valid.

Before:

[^44]: The ranking function in code names which side of the monotone band a score is on | crates/tillandsias-plan/src/obligation.rs#L620-L638 @v56.9.5.1
    > Outside the band, with the reason NAMED rather than implied. A consumer must not read a rise or fall across this boundary as progress or regress. Broken(&'static str),

After:

[^44]: The ranking function in code names which side of the monotone band a score is on | crates/tillandsias-plan/src/obligation.rs#L634-L637
    > Outside the band, with the reason NAMED rather than implied. A consumer must not read a rise or fall across this boundary as progress or regress. Broken(&'static str),

## D30

Cites printing separately from model enum.

Before:

(new citation)

After:

Footnote 45: shell regime reporting

## D31 — Shared mathematical illustrations

The staircase is conditional on comparable residuals; the LLN illustration cannot establish convergence from bounded bias; the CRDT picture demonstrates set union, while registers select winners. These corrections preserve all figures and the manual Slides page. Evidence: methodology/math-foundations.yaml#L91-L104; methodology/philosophy.yaml#L29-L47; crates/tillandsias-plan/src/fragments.rs#L28-L47 at v56.9.12.2.

```diff
diff --git a/scripts/figures.py b/scripts/figures.py
index f226900..5fb11e8 100644
--- a/scripts/figures.py
+++ b/scripts/figures.py
@@ -69,7 +69,7 @@ LOOP = _wrap(
 
 STAIRCASE = _wrap(
     "600 270", "Residual distance falling release over release toward a floor above zero",
-    "Distance-to-target falls at every release and is never allowed to rise — but it settles on a "
+    "Schematic: if comparable residuals never rise, they approach a "
     "floor, and nobody has proven that floor is zero.",
     """
     <line x1="58" y1="20" x2="58" y2="212" class="s-axis"/>
@@ -92,9 +92,9 @@ STAIRCASE = _wrap(
     """)
 
 LLN = _wrap(
-    "600 260", "One slow sample versus many fast samples converging",
-    "Left: one long run, one sample, one skew you cannot see. Right: many short runs whose "
-    "average lands — provided each run's bias is bounded.",
+    "600 260", "An illustration of averaging, not a measured convergence result",
+    "Schematic only: averaging can reduce variation under suitable hypotheses. "
+    "Dependent iterations and persistent bias need a separate argument; this diagram is not evidence.",
     """
     <text x="150" y="24" class="s-lbl" text-anchor="middle">one big slow iteration</text>
     <text x="450" y="24" class="s-lbl s-accent" text-anchor="middle">many small fast iterations</text>
@@ -117,9 +117,9 @@ LLN = _wrap(
       <circle cx="532" cy="93" r="2.6"/><circle cx="550" cy="98" r="2.6"/>
     </g>
     <path d="M352 108 C 420 104 480 98 566 96" class="s-mean" fill="none"/>
-    <text x="450" y="184" class="s-lbl s-accent" text-anchor="middle">the running average converges</text>
-    <text x="450" y="200" class="s-lbl" text-anchor="middle">&#8212; only if each sample's bias is bounded</text>
-    <text x="300" y="234" class="s-lbl" text-anchor="middle">Unbounded per-iteration skew: infinitely many iterations still miss.</text>
+    <text x="450" y="184" class="s-lbl s-accent" text-anchor="middle">an illustrative running average</text>
+    <text x="450" y="200" class="s-lbl" text-anchor="middle">no convergence theorem established here</text>
+    <text x="300" y="234" class="s-lbl" text-anchor="middle">Bounded bias alone does not make the average reach the truth.</text>
     """)
 
 LATTICE = _wrap(
@@ -154,8 +154,8 @@ LATTICE = _wrap(
 
 CRDT = _wrap(
     "600 250", "Two agents appending independently and folding to the same result",
-    "Two machines that never spoke, folded in either order, produce byte-identical state. "
-    "That is the whole trick.",
+    "With the same delivered facts and valid merge rules, replicas agree regardless of arrival order. "
+    "This illustration shows set union, not every field in the ledger.",
     """
     <text x="120" y="26" class="s-lbl">agent A &#8212; offline</text>
     <text x="400" y="26" class="s-lbl">agent B &#8212; offline</text>
@@ -175,7 +175,7 @@ CRDT = _wrap(
     </g>
     <rect x="176" y="172" width="248" height="40" rx="8" class="s-line s-gate"/>
     <text x="300" y="197" class="s-txt s-accent">fold &#8212; order does not matter</text>
-    <text x="300" y="236" class="s-lbl" text-anchor="middle">no lock, no coordinator, no merge conflict, no lost write</text>
+    <text x="300" y="236" class="s-lbl" text-anchor="middle">set union preserves facts; registers choose a winning value</text>
     """)
 
 GATE = _wrap(
```


## Final exact proposed page delta

The final hunk set below controls if an earlier delta excerpt differs: remove unmeasured shell line-count comparison and cite the actual tombstone branch rather than merely its enum.

```diff
--- docs/matrix/level-5-phd.md
+++ docs/matrix/level-5-phd.md
@@ -8,8 +8,9 @@
 depends on them.
 
 The short verdict: the theory is small, finite, and unusually candid about the
-theorems it declines to claim. Two of its load-bearing hypotheses are assumed rather
-than discharged, and the instrumentation that would test them does not exist.
+theorems it declines to claim. Its model now has generative property tests and stable requirement identifiers.
+Connecting those checks to live validation and justifying dependent iteration remain
+separate obligations.
 
 ## The lattice, and the one step worth checking
 
@@ -84,14 +85,13 @@
 sends $a \mapsto \top$, $b \mapsto b$ with $a < b$ is idempotent and not monotone.
 Nor does it imply inflationarity. The validation program that would discharge the
 missing two is written down — enumerate the allowed transitions and property-test
-that each is order-preserving for every affected obligation[^9] — which is exactly
-the right shape of obligation, and exactly what is not run.
-
-> RED: The fixed-point argument's load-bearing hypothesis is monotonicity of the refinement operator, and monotonicity is assumed, not proved. The repository's own discharge procedure is generative property testing over reachable obligation states; the workspace contains no property-testing dependency at all — no `proptest`, no `quickcheck`, in any crate manifest. What would be needed is modest and specific: an enumeration of the permitted transition relation, plus a proof or a generative test that every transition is order-preserving in each affected coordinate, with tombstones and scope changes excluded as declared non-monotone.
-> PATH: The checks are specified as phase one of a staged validation program[^9]. That phase was unimplemented at this release; implementing the model and its generative property tests was filed as scheduled work on 2026-09-03. The prerequisite is the sharper half: there is nothing to property-test until the obligation model exists as code rather than as prose. The obligation model and its generative property tests landed on 2026-09-03 and reached the daily channel in v56.9.4.1, cut 2026-09-04, over a committed rule set rather than the live validators, and are not yet in the stable channel[^41].
-
-> RED: The lattice's coordinates are mostly not instantiated. The obligation model is indexed by stable requirement identifiers, but no specification file in the tree carries a requirement identifier field — requirements are named by prose headings, against several thousand RFC-2119 keywords. The credit term that prices this, `requirement_has_stable_id`, occurs exactly once in the entire repository: in the weight table that defines it[^10]. Nothing reads it. A product order over coordinates that do not exist is a well-formed object over an empty index.
-> PATH: Priced in the scoring rules but not gated on, and unscheduled at this release. A migration to stable random identifiers was filed on 2026-09-03, carrying the rule that a refinement preserving the original intent keeps its identifier while a change of meaning becomes a tombstone plus a new one — a boundary that is author judgement and cannot be enforced by a validator, so the documentation must say so rather than imply a guard covers it. Landed on 2026-09-03 and in the daily channel from v56.9.4.1, cut 2026-09-04: every requirement received a stable random identifier and a gate check now refuses a missing or duplicated one[^42]; nothing yet computes the credit term.
+that each is order-preserving for every affected obligation[^9] — which is the right shape of obligation. That program now has executable tests
+over a committed rule set; it does not establish the same properties for every live validator[^41].
+
+> RED: The refinement model has generative tests for monotonicity, inflationarity and idempotence, but they exercise a committed rule set rather than every live validator[^41]. They establish a model boundary, not semantic correctness of the running system.
+> PATH: The staged validation program names the remaining obligation: enumerate permitted transitions and check every affected coordinate, treating tombstones and scope changes separately[^9].
+
+> GREEN: Requirement identifiers now exist and a gate checks presence and uniqueness, including tombstoned specifications[^42]. Whether an edit preserves meaning and should keep its identifier remains author judgement; the guard cannot decide that. The evidence-credit table still lists stable identifiers as a scoring input[^10], which by itself does not establish that credit is computed.
 
 > GREEN: The negative results — no contraction, no Galois connection, no probabilities — are first-class claims carrying their own discharge conditions, not caveats appended to positive ones. Each names the object a future claim would have to construct.
 
@@ -151,21 +151,18 @@
 *by the object currently on offer*, and the work of building a better one is open
 rather than blocked.
 
-There is a further objection the repository has not addressed. If $d_v$ were the
-CentiColon residual, it is integer-valued, and a non-increasing integer sequence
-bounded below is eventually constant — stronger than Proposition 4, and it would
-make $d_* = 0$ decidable in finitely many steps under any strict-progress premise.
-But the residual is computed against a denominator that is policy and may change per
-release[^15]. Then $d_{v+1} \le d_v$ compares two integers drawn from different
-scales, and the inequality is not scale-invariant: a release can lower its residual
-by enlarging its denominator.
-
-> RED: The release-boundary inequality is stated over a quantity whose codomain is allowed to change between the two terms being compared. Nothing normalises residuals across a denominator change, so non-increase is a comparison between two differently-scaled integers. A ratio $d_v/N_v$ would be comparable and is not what is checked.
-> PATH: A phase-two check requiring denominator changes to emit an explicit scope-change signal is specified[^9]; it is unimplemented, and no normalisation rule is recorded even in specification. In the daily channel the ranking function in code now labels a score whose denominator lost a tombstoned obligation as not comparable, and the script prints that label[^44]; still no normalisation rule is recorded.
+There is a further boundary. Under a fixed denominator, a non-increasing integer
+residual is eventually constant; strict progress while positive would force zero.
+Changing the obligation scope breaks that comparison. A ratio alone cannot repair
+it: adding easy obligations can improve the percentage without closing an old gap.
+
+> RED: The scorer marks a tombstone as a broken monotone regime, and the shell reports that regime[^44][^45]. This is useful local instrumentation, but does not establish a cross-release comparison for arbitrary changes of weights or obligation scope.
+> PATH: The validation program requires denominator changes to be reported separately[^9]. A complete cross-release comparison must align the obligation set and weights; no general normalisation rule is established by the cited implementation.
 
 ## Iteration: the law of large numbers at full strength
 
-This is the intellectual core[^16]. Set it up properly. Let $(X_k)_{k\ge1}$ be
+The methodology now withdraws its strong-law citation for dependent iterations[^16].
+The mathematics below explains why that correction matters. Set it up properly. Let $(X_k)_{k\ge1}$ be
 random elements on a probability space, $X_k$ the value of a real quality functional
 on iteration $k$, with $\mathbb{E}|X_k| < \infty$ and
 $\mathbb{E}[X_k] = \mu + b_k$, where $b_k$ is the per-iteration skew. Write
@@ -177,8 +174,7 @@
 
 $$X_k \text{ i.i.d.}, \;\; \mathbb{E}|X_1| < \infty \qquad\Longrightarrow\qquad \bar X_N \;\xrightarrow{\;\text{a.s.}\;}\; \mathbb{E}X_1$$
 
-The iterations here are not identically distributed, so the version the doctrine
-actually needs is Kolmogorov's variance criterion, which drops identical
+The iterations here are not identically distributed, so a candidate generalisation is Kolmogorov's variance criterion, which drops identical
 distribution and keeps independence[^18]:
 
 $$X_k \text{ independent}, \;\; \sum_{k\ge1} \frac{\mathrm{Var}(X_k)}{k^2} < \infty \qquad\Longrightarrow\qquad \bar X_N - \frac{1}{N}\sum_{k \le N} \mathbb{E}X_k \;\xrightarrow{\;\text{a.s.}\;}\; 0$$
@@ -188,21 +184,17 @@
 Same family as the three-series theorem; independence and the summable-variance
 condition are the whole price of admission.
 
-Weak versus strong is convergence in probability versus almost-sure convergence, and
-the implication runs one way: a.s. $\implies$ in probability, never the converse.
-The repository states the split in its correct form and, more importantly, correctly
-identifies the term that defeats iteration: not the variance, which averages away
-under the criterion above, but the bias. If $|b_k| \le \beta$ then $|\bar b| \le \beta$
-and the stream converges to within $\beta$ of truth; if skew is unbounded, or bounded
-away from zero at the end of every prompt, $\bar X_N$ converges almost surely to the
-*wrong number* and more iterations do not help. The file says exactly this — *"if a
-prompt's skew is not bounded, infinite iterations do NOT converge hard"*[^16]. That
-is a hypothesis of the theorem being named as one, which is more than most
-engineering essays manage.
+Weak versus strong is convergence in probability versus almost-sure convergence;
+almost-sure convergence implies convergence in probability, but the converse need
+not hold. Under the criterion above and existence of the mean-bias limit, bounded
+bias bounds the limiting error. Bounded bias alone does not imply convergence,
+and unbounded skew does not by itself prove divergence. The methodology retains
+small, fast iterations as engineering guidance while withdrawing the almost-sure
+claim[^16].
 
 @fig:lln
 
-Now the objection the methodology does not address, and it is the load-bearing one.
+The objection the methodology now acknowledges is the load-bearing one.
 Every form of Theorem 5 quoted above requires **independence**. Iterations of an
 agent that reads its own prior output are not independent: $X_{k+1}$ is a measurable
 function of $X_k$ and the accumulated context. The architecture makes the dependence
@@ -211,7 +203,7 @@
 code[^19]. That is a feedback loop by construction, and it invalidates every
 independence hypothesis in the section above.
 
-Two substitutes would serve, neither argued. Either the sequence is stationary and
+Two possible substitutes remain unestablished. Either the sequence is stationary and
 ergodic and one invokes Birkhoff's pointwise ergodic theorem[^20] — but stationarity
 is implausible for a process whose corpus grows monotonically, and ergodicity is
 exactly what fails if the chain can be absorbed. Or the increments form a martingale
@@ -236,10 +228,7 @@
 The repair is cheap in words and real in work — name the dependence structure, then
 cite the theorem that covers it.
 
-> RED: The methodology invokes the strong law of large numbers to license almost-sure convergence of the iteration stream, four lines above the passage describing the retrieval cache that makes consecutive iterations dependent by design. The theorem is applied outside its hypotheses, in the same block that documents why the hypotheses fail.
-> PATH: Corrected on 2026-09-03, after the release this page cites — so the passage quoted above is the pre-fix text, and the citation is left pinned to it deliberately. The almost-sure claim was **withdrawn rather than weakened**, at both sites that carried it: the guiding principle a reader meets first, and the detailed block beneath it. What a rigorous claim would require is now written into the file — Birkhoff with stationarity and ergodicity argued, or a martingale law with the conditional-mean condition argued — and the empirical release-boundary record becomes the load-bearing statement, described as a track record rather than a theorem. Nothing about the iteration design changed, and nothing machine-reads the corrected block, so the blast radius is documentation only.
-
-> GREEN: The weak/strong distinction is stated in the correct direction with the bias term, not the variance, identified as what defeats iteration — the version most treatments get backwards.
+> GREEN: The methodology explicitly withdraws the strong-law citation because the cache makes successive iterations dependent[^16]. It names ergodic and martingale hypotheses as work needed for a future theorem, and presents the iteration practice as an empirical track record rather than an almost-sure guarantee.
 
 ## What the repository renounces, and what that costs
 
@@ -289,11 +278,11 @@
 to today's scores is unlicensed. Building the layer that would license it is open
 work, and the repository files it as such.
 
-> RED: What computes the score is not the specified arithmetic. A sixteen-arm hardcoded weight table over CI check names in a shell script produces it[^27], and the committed dashboard's 890/990 is that pass-rate[^28]. None of the base weights, multipliers, cap rules or sixteen penalties in the methodology are computed anywhere in the tree.
-> PATH: The framework specification delegates the arithmetic to a named crate and modules[^29]; that crate is a README and one `.rs.example` file, and is not a workspace member. Ruled on 2026-09-03: the two are to be the same object, the shell scorer is to call the model rather than reimplement it, completed work is to be backfilled retroactively, and the requirement is to be hard-enforced going forward rather than requested. The three parts of the ruling were executed the same day, and reached the daily channel in v56.9.4.1, cut 2026-09-04 — the shell scorer hands its weights to the model[^43], completed work was backfilled where the ledger pins the evidence (a small fraction of rows), and a gate refuses new obligations the score cannot see.
-
-> RED: The methodology's own complexity constraint — methodology-to-codebase ratio below 0.15, with a red flag at 5000 lines of CI validators[^30] — is uninstrumented and has never fired, while the script that computes the score is itself 1,739 lines and the shell corpus it dispatches into exceeds 78,000.
-> PATH: The rule names two measurement procedures; neither is implemented as a check.
+> RED: The shell scorer now delegates arithmetic to the obligation model[^43], but still supplies weights over CI check names[^27]. A passing check earns its weight at the positive-test bar; it is not runtime observation or bundled evidence. This wiring does not implement the full methodology table of multipliers, evidence credits, caps and penalties[^15]. The committed dashboard remains a historical 890/990 snapshot[^28], not a measurement of this release.
+> PATH: The framework specification still names a separate scoring implementation[^29]. The shipped path centralises the arithmetic; completing and evidencing the richer scoring contract remains distinct work.
+
+> RED: The methodology's own complexity constraint — methodology-to-codebase ratio below 0.15, with a red flag at 5000 lines of CI validators[^30] — has no enforcing check identified in this audit, while the script that computes the score dispatches a large shell validator corpus.
+> PATH: The rule names two measurement procedures[^30]; no enforcing implementation was found in the scripts searched.
 
 ## CRDTs as algebra
 
@@ -333,7 +322,7 @@
 
 > GREEN: The repository retracts its own CRDT claim where it fails, and names the property that failed: a deduplication routine's header states plainly that it is a seen-set dedup, not a CRDT, because first-wins keeps whichever duplicate arrives first, so commutativity is false[^36]. Most projects keep the word.
 
-> GREEN: The version scheme is argued correctly as a join-semilattice — SemVer has no natural total order under merge because patch counters reset and collide, destroying causality, whereas a temporal anchor joined componentwise by max does have least upper bounds[^37].
+> GREEN: Componentwise maximum gives version tuples a join-semilattice. The document uses that algebra to motivate mergeable version coordinates[^37]. Its claim that SemVer has no natural total order is too broad: version precedence and preservation of branch causality are different properties.
 
 > GREEN: Semantic merges are typed honestly as "semantic cache with CRDT preconditions" rather than as CRDTs, with the anti-pattern named: calling a lossy cache a CRDT manufactures false convergence claims[^32]. The claim registry holds the lineage at strength "external analogy" until generative property tests exist[^38].
 
@@ -349,12 +338,12 @@
 rather than assumed[^40]. As a thesis position that is defensible, and I did not
 expect to write that sentence.
 
-Two things stop it being finished mathematics. The fixed-point argument runs on a
-monotonicity hypothesis that is asserted rather than proved, over a coordinate set
-that is largely uninstantiated. And the iteration doctrine, the most ambitious part,
-invokes laws that require independence for a process the same document designs to be
-self-referential. Neither is fatal; both are the sort of thing a referee returns for
-revision rather than rejection. Use the mathematics. Discount the dashboard.
+Two boundaries remain. Generative tests cover the committed refinement model,
+not the semantic correctness of all live validators. And dependent iteration
+still lacks a convergence theorem, although the methodology now retracts the
+unsupported strong-law claim. Stable identifiers and centralised score arithmetic
+make the bookkeeping more concrete; they do not turn closure into probability
+or a dashboard snapshot into release evidence.
 
 ## Footnotes
 
@@ -373,21 +362,21 @@
     > is a one-off scope expansion that The Tlatoāni MUST approve every time. Recurring automation (the meta-orchestration loop) MUST NOT self-escalate the bar.
 [^9]: The staged validation program: the monotonicity property tests and the denominator scope-change check | methodology/math-foundations.yaml#L175-L198
     > - allowed_evidence_transitions_are_monotone - tombstone_and_scope_change_transitions_are_explicitly_non_monotone
-[^10]: The evidence-credit table containing `requirement_has_stable_id` | methodology/proximity.yaml#L47-L57
+[^10]: The evidence-credit table containing `requirement_has_stable_id` | methodology/proximity.yaml#L88-L97
     > requirement_has_stable_id: 0.10
-[^11]: Multi-version convergence: the moving target, the residual floor, and the refusal of the zero-floor claim | methodology/philosophy.yaml#L103-L121
+[^11]: Multi-version convergence: the moving target, the residual floor, and the refusal of the zero-floor claim | methodology/philosophy.yaml#L134-L137
     > Release-over-release non-increase of d_v guarantees convergence to some residual floor d_* >= 0; it does not by itself prove d_* = 0. A zero-floor claim would additionally require a validated progress premise that excludes positive residual fixed points
 [^12]: Rudin, *Principles of Mathematical Analysis*, 3rd ed., Thm. 3.14 — monotone bounded sequences converge | https://archive.org/details/principlesofmath0000rudi
 [^13]: Banach, *Sur les opérations dans les ensembles abstraits*, Fund. Math. 3 (1922) | https://doi.org/10.4064/fm-3-1-133-181
 [^14]: Contraction explicitly not claimed, with the metric/operator/constant debt itemised | methodology/math-foundations.yaml#L108-L120
     > Without that metric proof, "monotonic convergence" means ordered non-regression plus finite residual descent, not metric contraction.
-[^15]: The cap rules, the sixteen penalties, and the rollup that makes the score non-additive in its parts | methodology/proximity.yaml#L60-L97
+[^15]: The cap rules, the sixteen penalties, and the rollup that makes the score non-additive in its parts | methodology/proximity.yaml#L100-L135
     > requirement_cc = weighted_obligation * earned_credit + penalties bounded to [0, weighted_obligation].
-[^16]: Weak versus strong LLN, bounded per-prompt skew, and the unbounded-skew hazard | methodology/philosophy.yaml#L8-L31
-    > then iterate — the STRONG LLN (almost-sure convergence) makes the stream of iterations converge hard. The hazard is uncontrolled skew sneaking in at the END of every individual prompt: if a prompt's skew is not bounded, infinite iterations do NOT converge hard.
+[^16]: The strong-law citation withdrawn for dependent iteration | methodology/philosophy.yaml#L29-L47
+    > So the almost-sure claim is not available as stated and is withdrawn rather than weakened.
 [^17]: Kolmogorov, *Grundbegriffe der Wahrscheinlichkeitsrechnung* (1933) — the strong law and its variance criterion | https://doi.org/10.1007/978-3-642-49888-6
 [^18]: Durrett, *Probability: Theory and Examples*, 5th ed. — SLLN, Kolmogorov's three-series theorem, and the ergodic and martingale substitutes | https://doi.org/10.1017/9781108591034
-[^19]: Retrieval as a cache; commits as the Lamport clock versioning it — the mechanism that makes iterations dependent | methodology/philosophy.yaml#L32-L39
+[^19]: Retrieval as a cache; commits as the Lamport clock versioning it — the mechanism that makes iterations dependent | methodology/philosophy.yaml#L54-L57
     > That cache is updated on COMMITS — a commit hitting the relevant bits retrains the RAG. Commits are therefore the LAMPORT CLOCK of the RAG models: they causally order and version the cached knowledge against the code
 [^20]: Birkhoff, *Proof of the ergodic theorem*, PNAS 17 (1931) | https://doi.org/10.1073/pnas.17.2.656
 [^21]: Cousot & Cousot, *Abstract Interpretation*, POPL 1977 | https://doi.org/10.1145/512950.512973
@@ -398,11 +387,11 @@
     > Evidence bundles and CentiColon scores should not be interpreted as probabilities. If probabilistic or belief-function confidence is later added, it must be a separate layer from obligation closure.
 [^25]: Shafer, *A Mathematical Theory of Evidence* (1976), cited as a possible separate confidence layer | https://press.princeton.edu/books/paperback/9780691100425/a-mathematical-theory-of-evidence
 [^26]: Walley, *Statistical Reasoning with Imprecise Probabilities* (1991) | https://doi.org/10.1007/978-1-4899-3472-7
-[^27]: What actually computes the score: a sixteen-arm hardcoded weight table over CI check names | scripts/local-ci.sh#L384-L403
+[^27]: The shell still supplies weights over CI check names | scripts/local-ci.sh#L384-L403
     > check_weight() { case "$1" in spec-cheatsheet-binding) echo 100 ;; spec-code-drift) echo 120 ;; spec-trace-coverage) echo 90 ;; version-monotonicity) echo 40 ;;
 [^28]: The committed dashboard's earned and total figures | docs/convergence/centicolon-dashboard.json#L75-L76
     > "total_cc": 990, "earned_cc": 890,
-[^29]: The framework specification delegating CentiColon arithmetic to a crate that is a README and one example file | methodology/litmus-framework.yaml#L88-L96
+[^29]: The framework specification names its intended scoring implementation | methodology/litmus-framework.yaml#L88-L96
     > files: - crates/tillandsias-litmus/src/convergence/mod.rs - crates/tillandsias-litmus/src/convergence/centicolon.rs
 [^30]: The uninstrumented complexity constraint and its 5000-line red flag | methodology/convergence.yaml#L329-L342
     > ratio_constraint: "methodology_complexity / codebase_complexity < 0.15" anti_pattern: > A validation system that requires more code to understand than the code being validated. Red flag: CI validators exceed 5000 lines or require specialized training to understand.
@@ -412,7 +401,7 @@
     > Calling a lossy semantic cache a CRDT without stable IDs, tombstones, deterministic merge, and property tests creates false convergence claims.
 [^33]: Determinism rules: fold order and idempotence | crates/tillandsias-plan/src/fragments.rs#L41-L49
     > Fragments fold in `(ts, filename)` order, never directory order — the filesystem does not promise an order, and two hosts folding differently would compute different states from identical inputs, which presents as corruption rather than as a sorting bug.
-[^34]: Commutativity and idempotence of the fold pinned as named tests | crates/tillandsias-plan/src/fragments.rs#L2648-L2668
+[^34]: Commutativity and idempotence of the fold pinned as named tests | crates/tillandsias-plan/src/fragments.rs#L2853-L2886
     > fn the_fold_is_commutative_the_defining_crdt_property() { Order of arrival must not change the result.
 [^35]: Rank-aware status join with a falsification escape hatch | crates/tillandsias-plan/src/fragments.rs#L307-L320
     > The closure ladder implemented<completed<verified<done is a monotone lattice: you climb UP freely and move DOWN only through a `falsified` event.
@@ -426,11 +415,14 @@
     > Major: meaning: "Contract version — breaking changes only"
 [^40]: Thesis defence position: finite ordered convergence under declared validators, with unknown-event intake as the escape hatch | methodology/math-foundations.yaml#L200-L206
     > The defensible claim is finite ordered convergence under declared validators: stable obligations form a finite lattice; evidence-improving transitions are checked for monotonicity; CentiColons are a bounded ranking function over that model; fixed points mean validator stability; and unknown-event intake is the escape hatch
-[^41]: Generative property tests for monotonicity, inflationarity and idempotence of the refinement operator, over a committed rule set | crates/tillandsias-plan/src/obligation_props.rs#L172-L219 @v56.9.5.1
-    > MONOTONICITY over the real rule set — what Knaster-Tarski actually needs and what the methodology's idempotence check never examined. #[test] fn refine_is_monotone_on_the_real_rules((x, y) in comparable_pair()) {
-[^42]: The gate that refuses a missing or duplicated requirement identifier, and states what it cannot check | scripts/check-requirement-ids.sh#L5-L35 @v56.9.5.1
+[^41]: Generative property tests for monotonicity, inflationarity and idempotence of the refinement operator, over a committed rule set | crates/tillandsias-plan/src/obligation_props.rs#L172-L219
+    > fn refine_is_monotone_on_the_real_rules((x, y) in comparable_pair()) {
+[^42]: The gate that refuses a missing or duplicated requirement identifier, and states what it cannot check | scripts/check-requirement-ids.sh#L5-L6
     > Every spec requirement carries a stable identifier, and no two carry the same one.
-[^43]: The shell scorer hands its weights to the model instead of summing them itself | scripts/local-ci.sh#L538-L563 @v56.9.5.1
+[^43]: The shell scorer hands its weights to the model instead of summing them itself | scripts/local-ci.sh#L542-L544
     > What LEFT is the arithmetic: earned/denominator/residual are now computed by `tillandsias-plan score-checks`, which runs obligation::centicolon_function over a SpecState.
-[^44]: The ranking function in code names which side of the monotone band a score is on | crates/tillandsias-plan/src/obligation.rs#L620-L638 @v56.9.5.1
-    > Outside the band, with the reason NAMED rather than implied. A consumer must not read a rise or fall across this boundary as progress or regress. Broken(&'static str),
+[^44]: The ranking function in code names which side of the monotone band a score is on | crates/tillandsias-plan/src/obligation.rs#L675-L708
+    > Regime::Broken("denominator scope changed: an obligation was tombstoned")
+
+[^45]: The shell prints non-comparability when the scorer reports a broken regime | scripts/local-ci.sh#L591-L599
+    > this score is NOT comparable with the previous run
```
