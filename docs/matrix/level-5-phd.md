# Level 5 — For the PhD / MathWiz / Hacker

You asked to be addressed at your level, so I will skip the tour: below is this
system's formal content and an audit of which claims are discharged. The punchline
first — the *theory* is unusually well-behaved, finite, modest and candid about the
theorems it has not earned; the *instrumentation* meant to make it binding is a
thirteen-row shell table. Judge the thinking on the former, and do not confuse the
latter with a measure.

## The object of study

Tillandsias is a tray application that folds a disposable, four-tier-contained
Linux enclave through your hypervisor so that coding agents execute in exactly one
place and touch nothing above it. That is the product, and it is not why you are
reading at this level. The interesting artefact is the accompanying methodology: an attempt to state
software convergence as an order-theoretic problem rather than a vibe. The thesis
is one line — *monotonic reduction of uncertainty under verifiable constraints*[^1]
— and, unusually, it has a file whose entire purpose is to separate what that
sentence can defend from the analogies it must not overclaim[^2].

## The formal skeleton

Begin with the atom. An **obligation** is a named, auditable requirement,
invariant, litmus signal, trace signal, provenance binding, or environment
assumption carrying a stable identifier[^3]. Its state ranges over a finite
**total order** — a chain, seven long, from no evidence to bundled evidence:

$$\mathcal{O} = \{\,\texttt{absent} < \texttt{declared} < \texttt{traced} < \texttt{pos\_tested} < \texttt{neg\_tested} < \texttt{runtime\_obs} < \texttt{evidence\_bundled}\,\}$$

A **spec state** is the product of its obligations' states; a **project state**
the product over active specs, ordered componentwise after aligning stable IDs and
tombstones[^3]:

$$S_{\text{spec}} = \prod_{i \in \mathrm{Obl}} \mathcal{O}_i, \qquad S_{\text{proj}} = \prod_{s \in \mathrm{Specs}} S_{\text{spec}}(s), \qquad x \le y \iff \forall i,\; x_i \le_{\mathcal{O}} y_i$$

Each $\mathcal{O}_i$ is a finite chain, hence a complete lattice; finite products of
complete lattices are complete lattices with $\vee$ and $\wedge$ componentwise. So
$S_{\text{proj}}$ is a finite complete lattice of height $6\cdot|\mathrm{Obl}|$, and
the apparatus lands squarely inside Tarski[^4] and standard finite-order
machinery[^5]. What it buys, and does not, the repository states itself — *"this
proves monotonicity of the model, not truth of the modeled requirement or adequacy
of the chosen obligation set"*[^6]. Rarer in the wild than it should be.

@fig:lattice

## Why "done" is decidable at all

Let $\mathrm{refine}: S \to S$ be the composite of validation and semantic
distillation at a *fixed* bar. The closure claim is idempotence[^7]:

$$\mathrm{refine}(\mathrm{refine}(x)) = \mathrm{refine}(x)$$

That is the whole decidability argument, and it is a good one. $\mathrm{refine}$
is inflationary and monotone on a finite lattice, so by Kleene iteration[^8] the
ascending chain $x \le \mathrm{refine}(x) \le \mathrm{refine}^2(x) \le \cdots$
stabilises in at most $6\cdot|\mathrm{Obl}|$ steps; the stabilised point is the
least fixed point above $x$. "Done" is then not a mood but a computable predicate:
$x$ is closed iff $\mathrm{refine}(x) = x$.

The governance layer makes this non-vacuous. The bar $B_v$ — the declared depth at
which a signal counts as a finding — is **fixed within a release** and rises only
by explicit operator decision; the automation is forbidden from self-escalating
it[^9]. That is precisely the hypothesis the fixed-point argument needs: a
continuously rising bar makes $\mathrm{refine}$ a moving operator and destroys
stabilisation, while discrete, externally gated raises preserve it.

The honest caveat is stated too: a fixed point means *stable under known
validators*, not complete relative to unknown future requirements[^7]. Kleene
gives you least, not right.

## The moving target, and the theorem that is not proved

Now the part most would fudge, and this repository does not.

Write $T_v$ for the target — the specs at version $v$ — $I_v$ for the
implementation, and $d_v = d(I_v, T_v) \ge 0$ for residual distance. Because the
specs themselves evolve, $T$ moves, and no final target state exists[^10]. The
mechanically checkable release-boundary rule is therefore non-increase:

$$d_{v+1} \le d_v \quad \text{for all } v \implies \exists\, d_* \ge 0 : \lim_{v\to\infty} d_v = d_*$$

by monotone convergence of a bounded-below decreasing sequence. And the sentence
that earns the file its credibility: this **does not prove $d_* = 0$**. A zero-floor
claim additionally requires a validated progress premise excluding positive
residual fixed points — or a proven contraction, explicitly not claimed[^10].

@fig:staircase

The debt is itemised. A future Banach-style claim[^11] would owe a complete metric space $(X,d)$ of project states, an operator
$F: X \to X$, and a constant $0 \le c < 1$ with

$$d(F(x), F(y)) \le c\,d(x,y) \quad \forall x,y \in X$$

whence a unique fixed point $x^*$ with $d(F^n(x), x^*) \le \frac{c^n}{1-c}d(x,F(x))$
— geometric convergence to zero residual[^12]. Note exactly what is missing:
not the operator (that is $\mathrm{refine}$), but (i) a metric at all — the
project state is an order, and no metric compatible with it has been defined;
(ii) completeness of that space; and (iii) any empirical or structural bound $c$.
Absent (i), the other two are not even well-posed. Until then, "monotonic
convergence" means ordered non-regression plus finite residual descent, and the
file says so in those words[^12]. That is the difference between a methodology and
a pitch deck.

> GREEN: The load-bearing negative results — no contraction, no Galois connection, no probabilities — are written down as first-class claims with their discharge conditions, not buried as caveats.

## The law of large numbers, correctly split

The operating doctrine for agent iteration is a genuine weak/strong LLN
distinction, and it is the intellectual core of the whole design[^13].

Model one prompt as a single sample $X_k$ of a quality functional with
$\mathbb{E}[X_k] = \mu + b_k$, where $b_k$ is the per-iteration **skew** (bias).
For the empirical mean $\bar{X}_N = \frac{1}{N}\sum_{k\le N} X_k$:

$$\text{Weak LLN:}\quad \bar{X}_N - \frac{1}{N}\sum b_k \;\xrightarrow{\;\mathbb{P}\;}\; \mu \qquad\text{(convergence in probability, biased at finite } N)$$

$$\text{Strong LLN:}\quad \bar{X}_N \;\xrightarrow{\;\text{a.s.}\;}\; \mu + \bar{b}, \qquad \bar{b} = \lim_N \tfrac{1}{N}\textstyle\sum_{k\le N} b_k$$

The doctrine follows immediately. Fighting to maximise a single prompt's accuracy
is fighting its own finite-$N$ skew: you are trying to make one sample be the mean.
Instead make each iteration **small and fast with bounded skew**, then iterate, and
let the stream supply almost-sure convergence[^13].

The load-bearing hypothesis is the bound, and here is where the folklore gets
misread. If $|b_k| \le \beta$ with $\beta \to 0$ under the discipline, then
$|\bar b| \le \beta$ and the iteration stream converges hard to within $\beta$ of
truth. If instead skew is unbounded — or bounded away from zero at the *end* of
every prompt — then $\bar b \not\to 0$ and $\bar{X}_N$ converges almost surely to
the *wrong number*. Infinitely many iterations do not save you. The repository
states exactly this hazard: *"if a prompt's skew is not bounded, infinite
iterations do NOT converge hard"*[^13]. Bounding per-sample bias is therefore a
hypothesis of the theorem, not a performance optimisation — which is why the
architecture prefers many small composable retrieval experts over one large slow
model, and why answers are pinned to a source commit acting as a Lamport clock
over the cached corpus[^14].

@fig:lln

> GREEN: The weak/strong split is stated in its correct form — the bias term, not the variance, is identified as what defeats iteration. This is the version most engineering essays get backwards.

## Order-theoretic honesty: what the scores are not

Three renunciations, each with teeth.

**Abstract interpretation is claimed only as a discipline.** Specs and scores are
described as abstractions that deliberately forget irrelevant detail — the Cousot
framing[^15] — but the file concedes that **no Galois connection $(\alpha,\gamma)$
is defined** between program semantics and spec obligations[^16]. What that
forecloses is precise: with no $\alpha\circ\gamma \sqsubseteq \mathrm{id}$ /
$\mathrm{id} \sqsubseteq \gamma\circ\alpha$ adjunction there is no soundness theorem
transporting an abstract fixed point back to a guarantee about concrete
executions. Closure in the obligation lattice implies nothing about the program.
It is bookkeeping over evidence, and is labelled as such.

**Scores are a ranking function, not a measure.** The CentiColon map
$c: S_{\text{spec}} \to \mathbb{N}$ is bounded, with a separately reported
denominator and residual, and monotone *only* for transitions that preserve
obligation IDs and introduce no penalties, ambiguity, or denominator scope
change[^3]. That is a Floyd-style ranking function[^17] — a well-founded descent
witness, exactly as in termination arguments — not an additive set function.
Consequently it is not a measure: it is not countably additive, obligations
overlap, and the denominator is policy. And it is explicitly **not a
probability**[^18]: reports must label residuals as obligation closure and keep
any belief values in separately named fields, with Shafer[^19] and Walley[^20]
cited as the layer a future confidence model would have to occupy separately. What
this forecloses: you may not combine two scores by Bayes, and 89% closed is not an
89% chance of correctness — finite coverage is not proof of absence[^18].

> RED: The ranking function's own validation program calls for property-testing score monotonicity over generated obligation states. No property-testing harness exists anywhere in the workspace — no `proptest`, no `quickcheck` — so the monotonicity checks are enumerated but never run.
> PATH: The checks are written down as a staged validation program[^27]; the phase that would discharge them is specified and unimplemented.

> RED: The obligation model's atom is a stable requirement ID. Fifteen of one hundred seventy-seven spec files carry an ID field, against thousands of RFC-2119 keywords. The lattice is therefore defined over a coordinate set that mostly does not exist.
> PATH: `requirement_has_stable_id` is already an evidence-credit term in the scoring rules[^28], so the gap is priced — but nothing gates on it, and no migration is scheduled.

> RED: What actually computes the score is a hardcoded weight table over thirteen CI checks in a shell script[^29]; the committed dashboard's 890/990 is that pass-rate[^30]. None of the specified base weights, multipliers, cap rules, or sixteen penalties are computed anywhere outside the methodology YAML.
> PATH: The framework specification names the crate and modules that would own the arithmetic; that crate contains a README and one `.rs.example` and is not a workspace member[^36].

> RED: The methodology's own complexity constraint — methodology over codebase below 0.15, with a red flag at 5000 lines of CI validators — is not instrumented, so it has never fired despite the validator corpus exceeding its own red-flag threshold several times over[^31].
> PATH: The rule states its two measurement procedures; neither is implemented as a check.

## CRDT semantics, as algebra

The plan ledger is a real convergent replicated data type, and the repository
distinguishes it from the places where the word would be decoration.

The state is $\text{base} \oplus \mathrm{fold}(\text{fragments})$: one compacted
base document plus append-only, immutable per-host fragments. Two join-semilattices
carry it[^21]:

- **Grow-only sets.** Packets keyed by identifier, and events keyed by
  $(\text{packet id}, \text{event identity})$. Join is union:
  $x \sqcup y = x \cup y$, which is commutative, associative and idempotent —
  the three properties that make replica state a join-semilattice and make the
  merge order-independent. Deletion is by **tombstone**, because a G-Set has no
  remove and a naive delete is resurrected by any replica that missed it.
- **Last-writer-wins registers**, one per $(\text{packet id}, \text{field})$ key,
  with the winner chosen deterministically by $(\text{timestamp}, \text{host})$ —
  a total order on writes, hence a join.

$$\text{state} = \Big(\bigcup_i P_i,\; \bigcup_i E_i,\; \textstyle\bigsqcup_i R_i\Big), \qquad \bigsqcup \text{ componentwise}$$

Applying LWW to a *list* would silently discard the loser's entries — which is why
events are a set and not a register, a distinction the file calls "the whole
correctness argument"[^21]. Determinism is pinned by folding in
$(\text{timestamp}, \text{filename})$ order rather than directory order, since two
hosts folding differently present as corruption, not as a sorting bug[^22]. The
three properties are tested by name[^23].

@fig:crdt

The subtlety worth your attention: the status field is *not* a plain LWW register.
It composes a monotone join over a closure rank with LWW as tiebreak at equal rank,
treats terminal-but-lateral values as non-ladder moves, and permits descent only
under an explicit falsification flag[^24] — a lexicographic join with a deliberate
non-monotone escape hatch, so monotonicity cannot force retention of a certainty
later shown false.

The best evidence that the honesty is structural sits in a Lua file whose header
*retracts* a prior CRDT claim and names the property that failed: *"This is a SEEN-SET DEDUP, not a CRDT — the earlier header's CRDT
claim (commutativity in particular) was false: first-wins keeps whichever
duplicate arrives first, so order matters"*[^25]. Most repositories would have
kept the word.

> GREEN: Spec and cheatsheet merges are explicitly typed as "semantic merge with CRDT preconditions", with the anti-pattern spelled out: calling a lossy semantic cache a CRDT creates false convergence claims[^32].

> GREEN: The version scheme is argued correctly as a join-semilattice — SemVer has no natural total order under merge because patch counters reset and collide, so causality is lost, whereas a calendar anchor joined componentwise by max does have least upper bounds[^33].

> RED: That same versioning document defines its two leading components as a contract version and a feature phase. The live format is years-since-epoch, month, day, build — the algebra survives, the documented semantics of two components are false[^34].
> PATH: The drift was caught once at a release boundary and the shape test was corrected; the doctrine file was not.

> RED: The claim registry files the CRDT lineage at claim strength "external analogy"[^35] and holds the weaker label until commutativity/associativity/idempotence property tests exist for the semantic-merge cases. For the ledger the tests exist but are example-based, not generative; for cheatsheets and specs they do not exist at all.
> PATH: The precondition list is written and the missing item is named explicitly in it — an open obligation, correctly labelled rather than quietly closed.

## Verdict

The formal core is a finite product lattice, a Kleene fixed point under declared
validators at an operator-gated bar, a Floyd-style ranking function, and a
correctly stated moving-target result whose zero-floor corollary is declined for
want of a metric. Contraction, Galois connections and probabilistic reading are
named *absent* rather than assumed. A defensible thesis position[^26], and I did
not expect to write that sentence.

The gap is instrumentation, not epistemology. A lattice whose coordinates are
mostly undeclared, scored by a shell case-statement, is not measuring the object
the theory describes. The theory knows this: its escape hatch is an unknown-event
intake meant to stop the model confusing current completeness with truth[^26]. Use
the maths. Discount the dashboard.

## Footnotes

[^1]: Core principle, one line | methodology/philosophy.yaml#L5-L6
[^2]: Stated purpose — separating defensible maths from analogy | methodology/math-foundations.yaml#L4-L11
[^3]: Formal objects: obligation, obligation state chain, product lattices, ranking function | methodology/math-foundations.yaml#L13-L43
[^4]: Tarski, *A lattice-theoretical fixpoint theorem and its applications*, Pacific J. Math. 5 (1955) | https://doi.org/10.2140/pjm.1955.5.285
[^5]: Davey & Priestley, *Introduction to Lattices and Order*, 2nd ed. | https://doi.org/10.1017/CBO9780511809088
[^6]: The lattice-model claim and its stated limit | methodology/math-foundations.yaml#L46-L59
[^7]: The fixed-point claim: idempotence of refine, and its limit | methodology/math-foundations.yaml#L61-L74
[^8]: Kleene, *Introduction to Metamathematics* (1952), cited for iterative least-fixed-point construction | https://archive.org/details/introductiontome00klee
[^9]: Bar-raise governance: the bar is fixed, rises only by operator decision, automation must not self-escalate | methodology/convergence.yaml#L410-L432
[^10]: Multi-version convergence: moving target, residual floor, refusal of the zero-floor claim | methodology/philosophy.yaml#L103-L121
[^11]: Banach, *Sur les opérations dans les ensembles abstraits*, Fund. Math. 3 (1922) | https://doi.org/10.4064/fm-3-1-133-181
[^12]: Contraction explicitly not claimed, with the metric/operator/constant debt itemised | methodology/math-foundations.yaml#L108-L120
[^13]: Weak versus strong LLN, bounded per-prompt skew, and the unbounded-skew hazard | methodology/philosophy.yaml#L8-L31
[^14]: Retrieval as cache; commits as the Lamport clock versioning it | methodology/philosophy.yaml#L32-L39
[^15]: Cousot & Cousot, *Abstract Interpretation*, POPL 1977 | https://doi.org/10.1145/512950.512973
[^16]: The concession: no Galois connection is defined — "an abstraction discipline, not a formal abstract interpreter" | methodology/math-foundations.yaml#L76-L89
[^17]: Floyd, *Assigning Meanings to Programs* (1967), cited for ranking-style progress reasoning | https://doi.org/10.1090/psapm/019/0235771
[^18]: Scores are not probabilities; finite coverage is not proof of absence | methodology/math-foundations.yaml#L122-L135
[^19]: Shafer, *A Mathematical Theory of Evidence* (1976), cited as a possible separate confidence layer | https://press.princeton.edu/books/paperback/9780691100425/a-mathematical-theory-of-evidence
[^20]: Walley, *Statistical Reasoning with Imprecise Probabilities* (1991) | https://doi.org/10.1007/978-1-4899-3472-7
[^21]: The three CRDT primitives and why each field uses the one it does | crates/tillandsias-plan/src/fragments.rs#L28-L39
[^22]: Determinism rules: fold order and idempotence | crates/tillandsias-plan/src/fragments.rs#L41-L49
[^23]: Commutativity and idempotence of the fold pinned as named tests (order-independence at L4099) | crates/tillandsias-plan/src/fragments.rs#L2648-L2668
[^24]: Rank-aware status join with a falsification escape hatch | crates/tillandsias-plan/src/fragments.rs#L307-L320
[^25]: A retracted CRDT claim, with the failed property named | crates/tillandsias-plan/lua/collect.lua#L7-L11
[^26]: Thesis defence position: finite ordered convergence under declared validators, with unknown-event intake as the escape hatch | methodology/math-foundations.yaml#L200-L206
[^27]: Validation program — the property tests that would discharge monotonicity | methodology/math-foundations.yaml#L175-L198
[^28]: Evidence-credit terms, including `requirement_has_stable_id` | methodology/proximity.yaml#L47-L57
[^29]: What actually computes the score: a hardcoded weight table over CI checks | scripts/local-ci.sh#L384-L400
[^30]: The committed dashboard's earned/total figures | docs/convergence/centicolon-dashboard.json#L75-L76
[^31]: The uninstrumented complexity constraint and its 5000-line red flag | methodology/convergence.yaml#L329-L342
[^32]: Cheatsheet merge typed as a semantic cache with CRDT preconditions, plus the anti-pattern | methodology/cheatsheets.yaml#L88-L114
[^33]: The join-semilattice argument for the version scheme, and the SemVer critique | methodology/versioning.yaml#L104-L124
[^34]: The documented Major/Minor semantics the project retired | methodology/versioning.yaml#L9-L20
[^35]: CRDT preconditions filed at claim strength "external analogy" | methodology/provenance.yaml#L179-L192
[^36]: The framework spec delegating CentiColon arithmetic to a crate that is a README and one example file | methodology/litmus-framework.yaml#L88-L96
