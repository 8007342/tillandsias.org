# Level 5 — For the MathWiz / Hacker

The lower levels gave you the object and its defects. What is left is the only part
that can be attacked with a pencil: the formal content, stated as claims with
hypotheses, sorted into (a) standard theorems being invoked, (b) what the repository
actually asserts, (c) what follows, and (d) what does not. The security findings of
level 4 are not repeated; they enter here only where a mathematical hypothesis
depends on them.

The short verdict: the theory is small, finite, and unusually candid about the
theorems it declines to claim. Two of its load-bearing hypotheses are assumed rather
than discharged, and the instrumentation that would test them does not exist.

## The lattice, and the one step worth checking

An **obligation** is a named, auditable requirement, invariant, litmus signal, trace
signal, provenance binding, or environment assumption carrying a stable
identifier[^1]. Its state ranges over a finite chain, seven long[^2]:

$$\mathcal{O} = \{\,\texttt{absent} < \texttt{declared} < \texttt{traced} < \texttt{pos\_tested} < \texttt{neg\_tested} < \texttt{runtime\_obs} < \texttt{evidence\_bundled}\,\}$$

$$S_{\text{spec}} = \prod_{i \in \mathrm{Obl}} \mathcal{O}_i, \qquad S_{\text{proj}} = \prod_{s} S_{\text{spec}}(s), \qquad x \le y \iff \forall i,\; x_i \le_{\mathcal{O}} y_i$$

Fix the convention, since authors differ: the **height** of a finite poset is the
maximum number of *strict order steps* in a chain — so a chain of $n$ elements has
height $n-1$, and the one-element poset has height $0$.

**Proposition 1.** *$S_{\text{proj}}$ is a finite complete lattice of height
$6|\mathrm{Obl}|$.* Each $\mathcal{O}_i$ is a finite chain, hence a complete lattice;
a finite product of complete lattices is complete with $\vee,\wedge$ computed
componentwise; a chain of seven elements has height six and heights add over
products[^3]. Nothing here is in dispute — it is the least interesting true thing
in the file, and the repository correctly declines to inflate it: *"this proves
monotonicity of the model, not truth of the modeled requirement or adequacy of the
chosen obligation set"*[^4].

Two hypotheses do quiet work. The order is componentwise **after aligning stable IDs
and tombstones**[^1], so a renamed coordinate yields a different lattice, not a lower
point in the same one; and $|\mathrm{Obl}|$ must be finite and known, which is what
makes the height bound a bound rather than an ordinal.

@fig:lattice
@fig:hasse

## The fixed point, in full

Let $\mathrm{refine}: S \to S$ be validation followed by semantic distillation at a
fixed bar $B$. The repository's stated claim is idempotence[^5]:

$$\mathrm{refine}(\mathrm{refine}(x)) = \mathrm{refine}(x)$$

**Theorem 2 (Knaster–Tarski).** *A monotone map on a complete lattice has a complete
lattice of fixed points, in particular a least one*[^6]. Applied here it gives
existence, non-constructively, and says nothing about how to reach it.

**Theorem 3 (finite monotone inflationary iteration).** *If $f: L \to L$ is monotone and
inflationary ($x \le f(x)$) on a finite lattice of height $h$, then for every $x$
the chain $x \le f(x) \le f^2(x) \le \cdots$ stabilises after at most $h$ strict
increases, and its limit is the least fixed point $\ge x$.* The bound is immediate:
each strict step rises at least one level in a poset of height $h$. Leastness is a
two-line argument worth doing, because it is the step people skip: if $y = f(y)$ and
$y \ge x$, then monotonicity gives $f^n(x) \le f^n(y) = y$ for every $n$, so the
limit is $\le y$.

Note where Kleene's theorem proper — least fixed point as $\bigsqcup_n f^n(\bot)$ for
a Scott-continuous $f$ on a CPO[^7] — would otherwise be invoked outside its
hypotheses. Continuity is not assumed, it is *free*: in a finite poset every directed
subset is finite and contains its own supremum, so every monotone map is
Scott-continuous. That is the first place a referee probes, and it survives.

@fig:fixpoint

So "done" is a computable predicate — $x$ is closed iff $\mathrm{refine}(x) = x$ —
and governance supplies the hypothesis that makes it non-vacuous: the bar $B_v$ is
**fixed within a release**, rising only by explicit operator decision, with the
automation forbidden from self-escalating it[^8]. A continuously rising bar makes
$\mathrm{refine}$ a moving operator and destroys stabilisation; discrete,
externally gated raises preserve it. That is the standing hypothesis of Theorem 3,
not decoration.

And now the gap. Theorem 3 needs **monotone and inflationary**; the repository
asserts **idempotent**. These are the three axioms of a closure operator, and the
repository states one of them. Idempotence does not imply monotonicity: a map that
sends $a \mapsto \top$, $b \mapsto b$ with $a < b$ is idempotent and not monotone.
Nor does it imply inflationarity. The validation program that would discharge the
missing two is written down — enumerate the allowed transitions and property-test
that each is order-preserving for every affected obligation[^9] — which is exactly
the right shape of obligation, and exactly what is not run.

> RED: The fixed-point argument's load-bearing hypothesis is monotonicity of the refinement operator, and monotonicity is assumed, not proved. The repository's own discharge procedure is generative property testing over reachable obligation states; the workspace contains no property-testing dependency at all — no `proptest`, no `quickcheck`, in any crate manifest. What would be needed is modest and specific: an enumeration of the permitted transition relation, plus a proof or a generative test that every transition is order-preserving in each affected coordinate, with tombstones and scope changes excluded as declared non-monotone.
> PATH: The checks are specified as phase one of a staged validation program[^9]. That phase was unimplemented at this release; implementing the model and its generative property tests was filed as scheduled work on 2026-09-03. The prerequisite is the sharper half: there is nothing to property-test until the obligation model exists as code rather than as prose. The obligation model and its generative property tests landed in the daily channel on 2026-09-03 (release v56.9.4.1), over a committed rule set rather than the live validators, and are not yet in the stable channel[^41].

> RED: The lattice's coordinates are mostly not instantiated. The obligation model is indexed by stable requirement identifiers, but no specification file in the tree carries a requirement identifier field — requirements are named by prose headings, against several thousand RFC-2119 keywords. The credit term that prices this, `requirement_has_stable_id`, occurs exactly once in the entire repository: in the weight table that defines it[^10]. Nothing reads it. A product order over coordinates that do not exist is a well-formed object over an empty index.
> PATH: Priced in the scoring rules but not gated on, and unscheduled at this release. A migration to stable random identifiers was filed on 2026-09-03, carrying the rule that a refinement preserving the original intent keeps its identifier while a change of meaning becomes a tombstone plus a new one — a boundary that is author judgement and cannot be enforced by a validator, so the documentation must say so rather than imply a guard covers it. In the daily channel, on 2026-09-03, every requirement received a stable random identifier and a gate check now refuses a missing or duplicated one[^42]; nothing yet computes the credit term.

> GREEN: The negative results — no contraction, no Galois connection, no probabilities — are first-class claims carrying their own discharge conditions, not caveats appended to positive ones. Each names the object a future claim would have to construct.

## The moving target, and what would force the floor to zero

Write $T_v$ for the specifications at version $v$, $I_v$ for the implementation,
$d_v = d(I_v, T_v) \ge 0$. Because the specifications evolve, $T$ moves and no final
target exists[^11]. The mechanically checkable release rule is non-increase.

**Proposition 4 (monotone convergence).** *A non-increasing real sequence bounded
below converges to its infimum*[^12]. Here:

$$d_{v+1} \le d_v \;\text{ for all } v, \quad d_v \ge 0 \qquad\Longrightarrow\qquad d_v \;\longrightarrow\; d_* \;=\; \inf_{v} d_v \;\ge\; 0$$

That is the whole result, and it is correct.

What does **not** follow is $d_* = 0$, and the repository says so in those words[^11].
The exact extra hypothesis is a uniform progress premise, in either of two forms:

$$\exists\,\varepsilon > 0 : \; d_v > 0 \implies d_{v+1} \le d_v - \varepsilon \qquad\text{or}\qquad \exists\,\theta < 1 : \; d_{v+1} \le \theta\, d_v$$

Either excludes positive residual fixed points and forces $d_* = 0$ — the additive
form in finitely many steps, the multiplicative one geometrically. The repository's
phrase — "a validated progress premise that excludes positive residual fixed
points"[^11] — is precisely this, asserted as a requirement on a future claim rather
than as a fact.

@fig:staircase

**The Banach alternative, itemised.** A contraction claim[^13] would owe a complete
metric space $(X,d)$, an operator $F: X \to X$, and a constant $0 \le c < 1$ with

$$d\big(F(x),F(y)\big) \le c\,d(x,y) \quad \forall x,y \in X \qquad\Longrightarrow\qquad \exists!\,x^* = F(x^*), \quad d\big(F^n(x),x^*\big) \le \frac{c^n}{1-c}\,d\big(x,F(x)\big)$$

Missing: (i) a metric, (ii) completeness, (iii) any bound on $c$. The repository
lists all three[^14]. The binding one is (i), and it is worse than "unproven".
$d$ as used is not a function on $X \times X$ at all — it is only ever evaluated at
the single pair $(I_v, T_v)$, giving a sequence of numbers indexed by release, not a
binary function on a set. Ask which axiom fails and the honest answers are:

$$\underbrace{d(x,y) = d(y,x)}_{\text{undefined}}, \quad \underbrace{d(x,z) \le d(x,y) + d(y,z)}_{\text{undefined}}, \quad \underbrace{d(x,y) = 0 \implies x = y}_{\text{false on the natural candidate}}$$

The first two are *undefined* rather than false, because $d(x,y)$ for two arbitrary
project states is never given a value; identity of indiscernibles fails outright,
since two materially different implementations can close the same obligation set and
score residual zero. Absent
(i), items (ii) and (iii) are not merely unproven — they are not well-posed. Until
a metric exists, "monotonic convergence" means ordered non-regression plus finite
residual descent, which is what the file claims and no more[^14].

Be careful about the scope of that verdict, because it is easy to overstate and I
will not. Everything above concerns the $d$ the repository actually documents. It is
**not** an argument that no suitable metric exists on project states, and nothing
here forecloses one: a genuine metric — with a completion, and a contraction constant
— may well be constructible, and if it were, the Banach route would reopen exactly as
written. The claim is the narrow one. The contraction argument cannot be discharged
*by the object currently on offer*, and the work of building a better one is open
rather than blocked.

There is a further objection the repository has not addressed. If $d_v$ were the
CentiColon residual, it is integer-valued, and a non-increasing integer sequence
bounded below is eventually constant — stronger than Proposition 4, and it would
make $d_* = 0$ decidable in finitely many steps under any strict-progress premise.
But the residual is computed against a denominator that is policy and may change per
release[^15]. Then $d_{v+1} \le d_v$ compares two integers drawn from different
scales, and the inequality is not scale-invariant: a release can lower its residual
by enlarging its denominator.

> RED: The release-boundary inequality is stated over a quantity whose codomain is allowed to change between the two terms being compared. Nothing normalises residuals across a denominator change, so non-increase is a comparison between two differently-scaled integers. A ratio $d_v/N_v$ would be comparable and is not what is checked.
> PATH: A phase-two check requiring denominator changes to emit an explicit scope-change signal is specified[^9]; it is unimplemented, and no normalisation rule is recorded even in specification. In the daily channel the ranking function in code now labels a score whose denominator lost a tombstoned obligation as not comparable, and the script prints that label[^44]; no normalisation rule is recorded.

## Iteration: the law of large numbers at full strength

This is the intellectual core[^16]. Set it up properly. Let $(X_k)_{k\ge1}$ be
random elements on a probability space, $X_k$ the value of a real quality functional
on iteration $k$, with $\mathbb{E}|X_k| < \infty$ and
$\mathbb{E}[X_k] = \mu + b_k$, where $b_k$ is the per-iteration skew. Write
$\bar{X}_N = N^{-1}\sum_{k \le N} X_k$ and $\bar b = \lim_N N^{-1}\sum_{k\le N} b_k$
when that limit exists.

**Theorem 5 (Kolmogorov's SLLN).** *Under independence, identical distribution, and
integrability*[^17]:

$$X_k \text{ i.i.d.}, \;\; \mathbb{E}|X_1| < \infty \qquad\Longrightarrow\qquad \bar X_N \;\xrightarrow{\;\text{a.s.}\;}\; \mathbb{E}X_1$$

The iterations here are not identically distributed, so the version the doctrine
actually needs is Kolmogorov's variance criterion, which drops identical
distribution and keeps independence[^18]:

$$X_k \text{ independent}, \;\; \sum_{k\ge1} \frac{\mathrm{Var}(X_k)}{k^2} < \infty \qquad\Longrightarrow\qquad \bar X_N - \frac{1}{N}\sum_{k \le N} \mathbb{E}X_k \;\xrightarrow{\;\text{a.s.}\;}\; 0$$

$$\text{hence} \qquad \bar X_N \;\xrightarrow{\;\text{a.s.}\;}\; \mu + \bar b, \qquad \bar b = \lim_{N} \frac{1}{N}\sum_{k \le N} b_k$$

Same family as the three-series theorem; independence and the summable-variance
condition are the whole price of admission.

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

@fig:lln

Now the objection the methodology does not address, and it is the load-bearing one.
Every form of Theorem 5 quoted above requires **independence**. Iterations of an
agent that reads its own prior output are not independent: $X_{k+1}$ is a measurable
function of $X_k$ and the accumulated context. The architecture makes the dependence
explicit and deliberate — retrieval is a cache of converged knowledge, updated on
commits, with commits acting as a Lamport clock ordering the corpus against the
code[^19]. That is a feedback loop by construction, and it invalidates every
independence hypothesis in the section above.

Two substitutes would serve, neither argued. Either the sequence is stationary and
ergodic and one invokes Birkhoff's pointwise ergodic theorem[^20] — but stationarity
is implausible for a process whose corpus grows monotonically, and ergodicity is
exactly what fails if the chain can be absorbed. Or the increments form a martingale
difference sequence with respect to the natural filtration $\mathcal{F}_k = \sigma(X_1,\dots,X_k)$,
giving an $L^2$ or Azuma-type law — but that requires

$$\mathbb{E}\big[X_{k+1} \mid \mathcal{F}_k\big] = \mu \quad \text{a.s. for all } k$$

which is precisely the assertion that yesterday's output does not bias today's, and
the cache design says it does. Under positive feedback an absorbing state is
available: the stream converges almost surely to whatever the loop locked onto, and
$\bar X_N$ converges beautifully to a number with no relation to $\mu$. Bounding
per-prompt skew does not repair this; it is a hypothesis about marginals, and the
failure is in the joint.

Be precise about what this objection kills. It does **not** show the iteration
scheme is wrong, and it does not show the stream fails to converge — small fast
iterations may well be the right engineering, and dependent sequences converge under
plenty of other hypotheses. What it kills is the *invocation of the strong law as
stated*: the theorem named is being applied to a sequence that does not satisfy its
independence hypothesis, so the almost-sure conclusion is unearned rather than false.
The repair is cheap in words and real in work — name the dependence structure, then
cite the theorem that covers it.

> RED: The methodology invokes the strong law of large numbers to license almost-sure convergence of the iteration stream, four lines above the passage describing the retrieval cache that makes consecutive iterations dependent by design. The theorem is applied outside its hypotheses, in the same block that documents why the hypotheses fail.
> PATH: Corrected on 2026-09-03, after the release this page cites — so the passage quoted above is the pre-fix text, and the citation is left pinned to it deliberately. The almost-sure claim was **withdrawn rather than weakened**, at both sites that carried it: the guiding principle a reader meets first, and the detailed block beneath it. What a rigorous claim would require is now written into the file — Birkhoff with stationarity and ergodicity argued, or a martingale law with the conditional-mean condition argued — and the empirical release-boundary record becomes the load-bearing statement, described as a track record rather than a theorem. Nothing about the iteration design changed, and nothing machine-reads the corrected block, so the blast radius is documentation only.

> GREEN: The weak/strong distinction is stated in the correct direction with the bias term, not the variance, identified as what defeats iteration — the version most treatments get backwards.

## What the repository renounces, and what that costs

**No Galois connection.** Specs and scores are described as abstractions that
deliberately forget detail — the Cousot framing[^21] — and the file concedes that no
adjunction is defined between program semantics and spec obligations[^22]. State the
missing object precisely. With $C$ the lattice of sets of concrete executions and
$A$ the obligation lattice, a Galois connection $\alpha \dashv \gamma$ requires
monotone $\alpha: C \to A$, $\gamma: A \to C$ with

$$\alpha(c) \sqsubseteq a \iff c \sqsubseteq \gamma(a) \qquad\text{equivalently}\qquad c \sqsubseteq \gamma(\alpha(c)) \;\text{ and }\; \alpha(\gamma(a)) \sqsubseteq a$$

@fig:galois

What is forfeited is the transport theorem, and only that — but that is everything.
Given the adjunction and a sound abstract operator ($\alpha \circ F \sqsubseteq F^\# \circ \alpha$),
one gets $\alpha(\mathrm{lfp}\,F) \sqsubseteq \mathrm{lfp}\,F^\#$: a fixed point
computed in the abstract over-approximates the concrete, so a property proved
upstairs holds of every concrete execution downstairs. Without it, closure in the
obligation lattice implies precisely nothing about the program. It is bookkeeping
over evidence, and is labelled as such.

**A ranking function, not a measure.** The CentiColon map $c: S_{\text{spec}} \to \mathbb{N}$
is bounded, with separately reported denominator and residual, and monotone *only*
for transitions preserving obligation IDs and introducing no penalties, ambiguity,
or denominator scope change[^1]. That is a Floyd-style ranking function[^23]: a
well-founded descent witness into a finite ordinal, of the kind that proves
termination.

It is not a measure. There is no $\sigma$-algebra on
$S_{\text{spec}}$; $c$ is not additive, because obligations overlap and sixteen
penalties plus six cap rules make the rollup non-linear in its parts[^15]; and the
normaliser is policy rather than a fixed total mass. A bounded ranking function into
a finite ordinal therefore induces no probability, and the repository says so
outright[^24]. What that forecloses is concrete: two scores may not be combined by
Bayes; there is no complement rule, so 89% closed is not an 11% chance of a defect;
and no calibration statement is available, because there is no event space on which
to calibrate. Shafer[^25] and Walley[^26] are cited as the layer a confidence model
would have to occupy separately — correctly, since a belief function would at least
supply the monotone-capacity structure that $c$ lacks.

That is a statement about $c$ as defined, and about nothing more. It does not show
that no transformation, extension or added structure could turn part of this model
into a measure or another probabilistic object — the citation of belief functions is
precisely an admission that such a layer is available to be built. What is claimed is
that $c$ does not *already* carry that structure, so probabilistic language applied
to today's scores is unlicensed. Building the layer that would license it is open
work, and the repository files it as such.

> RED: What computes the score is not the specified arithmetic. A sixteen-arm hardcoded weight table over CI check names in a shell script produces it[^27], and the committed dashboard's 890/990 is that pass-rate[^28]. None of the base weights, multipliers, cap rules or sixteen penalties in the methodology are computed anywhere in the tree.
> PATH: The framework specification delegates the arithmetic to a named crate and modules[^29]; that crate is a README and one `.rs.example` file, and is not a workspace member. Ruled on 2026-09-03: the two are to be the same object, the shell scorer is to call the model rather than reimplement it, completed work is to be backfilled retroactively, and the requirement is to be hard-enforced going forward rather than requested. The three parts of the ruling were executed the same day in the daily channel — the shell scorer hands its weights to the model[^43], completed work was backfilled where the ledger pins the evidence (a small fraction of rows), and a gate refuses new obligations the score cannot see.

> RED: The methodology's own complexity constraint — methodology-to-codebase ratio below 0.15, with a red flag at 5000 lines of CI validators[^30] — is uninstrumented and has never fired, while the script that computes the score is itself 1,739 lines and the shell corpus it dispatches into exceeds 78,000.
> PATH: The rule names two measurement procedures; neither is implemented as a check.

## CRDTs as algebra

The plan ledger is a genuine convergent replicated data type. State is
$\text{base} \oplus \mathrm{fold}(\text{fragments})$; the carriers are two
join-semilattices[^31]: grow-only sets of packets and of events keyed by
$(\text{packet id}, \text{event identity})$, with $x \sqcup y = x \cup y$; and
last-writer-wins registers per $(\text{packet id}, \text{field})$, the winner chosen
by the total order $(\text{timestamp}, \text{host})$.

$$\text{state} = \Big(\bigcup_i P_i,\; \bigcup_i E_i,\; \textstyle\bigsqcup_i R_i\Big), \qquad \bigsqcup \text{ componentwise}$$

The algebra: a commutative, associative, idempotent $\sqcup$ induces a partial order
$x \le y \iff x \sqcup y = y$ under which $x \sqcup y = \sup\{x,y\}$ — the join *is* the
least upper bound, which is why the three properties are a definition rather than a
checklist. Convergence follows because the fold is then a function of the *set* of
delivered updates, not their sequence: idempotence kills duplicates, commutativity
and associativity kill order.

@fig:crdt

State exactly what that buys, because it is strictly less than the folklore
suggests[^32]. It gives: replicas having delivered the same update set hold equal
state. It does **not** give delivery — liveness is someone else's problem; it does
not give correctness of the converged value; and it does not preserve concurrent
intent, which is where LWW does its damage. Applying LWW to a *list* silently
discards the loser's entries, which is why events are a set and not a register — a
distinction the file calls the whole correctness argument[^31]. Determinism is pinned
by folding in $(\text{timestamp}, \text{filename})$ order rather than directory
order[^33], and two of the three properties — commutativity and idempotence — are tested by name[^34].

The status field is not a plain register: it composes a monotone join over a closure
rank with LWW as tiebreak at equal rank, treats terminal-but-lateral values as
non-ladder moves, and permits descent only under an explicit falsification flag[^35]
— a lexicographic join with a deliberate non-monotone escape hatch, so that
monotonicity cannot force retention of a certainty later shown false.

> GREEN: The repository retracts its own CRDT claim where it fails, and names the property that failed: a deduplication routine's header states plainly that it is a seen-set dedup, not a CRDT, because first-wins keeps whichever duplicate arrives first, so commutativity is false[^36]. Most projects keep the word.

> GREEN: The version scheme is argued correctly as a join-semilattice — SemVer has no natural total order under merge because patch counters reset and collide, destroying causality, whereas a temporal anchor joined componentwise by max does have least upper bounds[^37].

> GREEN: Semantic merges are typed honestly as "semantic cache with CRDT preconditions" rather than as CRDTs, with the anti-pattern named: calling a lossy cache a CRDT manufactures false convergence claims[^32]. The claim registry holds the lineage at strength "external analogy" until generative property tests exist[^38].

> RED: That same versioning document defines its two leading components as a contract version and a feature phase[^39]. The live scheme is a temporal anchor throughout — years since epoch, month, day, build. The join algebra survives untouched, since componentwise max does not care what the coordinates mean; the documented semantics of two of four components are false.
> PATH: The drift was caught once at a release boundary and the shape test corrected; the doctrine file was not.

## Verdict

The formal core is a finite product lattice, a finite monotone-inflationary stabilisation under declared
validators at an operator-gated bar, a Floyd-style ranking function, and a correctly
stated moving-target result whose zero-floor corollary is declined for want of a
metric. Contraction, Galois connections and probabilistic readings are named *absent*
rather than assumed[^40]. As a thesis position that is defensible, and I did not
expect to write that sentence.

Two things stop it being finished mathematics. The fixed-point argument runs on a
monotonicity hypothesis that is asserted rather than proved, over a coordinate set
that is largely uninstantiated. And the iteration doctrine, the most ambitious part,
invokes laws that require independence for a process the same document designs to be
self-referential. Neither is fatal; both are the sort of thing a referee returns for
revision rather than rejection. Use the mathematics. Discount the dashboard.

## Footnotes

[^1]: Formal objects — obligation, the state chain, product lattices, and the ranking function's monotonicity conditions | methodology/math-foundations.yaml#L13-L43
    > A named, auditable requirement, invariant, litmus signal, trace signal, provenance binding, or environment assumption with a stable ID.
[^2]: Stated purpose — separating defensible mathematics from analogy | methodology/math-foundations.yaml#L4-L11
    > Separate the math the methodology can defend from analogies it must not overclaim.
[^3]: Davey & Priestley, *Introduction to Lattices and Order*, 2nd ed. — product orders, heights, completeness | https://doi.org/10.1017/CBO9780511809088
[^4]: The lattice-model claim and its stated limit | methodology/math-foundations.yaml#L46-L59
    > This proves monotonicity of the model, not truth of the modeled requirement or adequacy of the chosen obligation set.
[^5]: The fixed-point claim: idempotence of refine, and its limit | methodology/math-foundations.yaml#L61-L74
    > Define the refinement operator over a finite artifact snapshot and check idempotence: refine(refine(state)) == refine(state).
[^6]: Tarski, *A lattice-theoretical fixpoint theorem and its applications*, Pacific J. Math. 5 (1955) — the Knaster–Tarski theorem, generalising Knaster's 1928 powerset case | https://doi.org/10.2140/pjm.1955.5.285
[^7]: Kleene, *Introduction to Metamathematics* (1952), cited for the iterative least-fixed-point construction | https://archive.org/details/introductiontome00klee
[^8]: Bar-raise governance — the bar is fixed within a release, rises only by operator decision, and the automation must not self-escalate | methodology/convergence.yaml#L410-L432
    > is a one-off scope expansion that The Tlatoāni MUST approve every time. Recurring automation (the meta-orchestration loop) MUST NOT self-escalate the bar.
[^9]: The staged validation program: the monotonicity property tests and the denominator scope-change check | methodology/math-foundations.yaml#L175-L198
    > - allowed_evidence_transitions_are_monotone - tombstone_and_scope_change_transitions_are_explicitly_non_monotone
[^10]: The evidence-credit table containing `requirement_has_stable_id` | methodology/proximity.yaml#L47-L57
    > requirement_has_stable_id: 0.10
[^11]: Multi-version convergence: the moving target, the residual floor, and the refusal of the zero-floor claim | methodology/philosophy.yaml#L103-L121
    > Release-over-release non-increase of d_v guarantees convergence to some residual floor d_* >= 0; it does not by itself prove d_* = 0. A zero-floor claim would additionally require a validated progress premise that excludes positive residual fixed points
[^12]: Rudin, *Principles of Mathematical Analysis*, 3rd ed., Thm. 3.14 — monotone bounded sequences converge | https://archive.org/details/principlesofmath0000rudi
[^13]: Banach, *Sur les opérations dans les ensembles abstraits*, Fund. Math. 3 (1922) | https://doi.org/10.4064/fm-3-1-133-181
[^14]: Contraction explicitly not claimed, with the metric/operator/constant debt itemised | methodology/math-foundations.yaml#L108-L120
    > Without that metric proof, "monotonic convergence" means ordered non-regression plus finite residual descent, not metric contraction.
[^15]: The cap rules, the sixteen penalties, and the rollup that makes the score non-additive in its parts | methodology/proximity.yaml#L60-L97
    > requirement_cc = weighted_obligation * earned_credit + penalties bounded to [0, weighted_obligation].
[^16]: Weak versus strong LLN, bounded per-prompt skew, and the unbounded-skew hazard | methodology/philosophy.yaml#L8-L31
    > then iterate — the STRONG LLN (almost-sure convergence) makes the stream of iterations converge hard. The hazard is uncontrolled skew sneaking in at the END of every individual prompt: if a prompt's skew is not bounded, infinite iterations do NOT converge hard.
[^17]: Kolmogorov, *Grundbegriffe der Wahrscheinlichkeitsrechnung* (1933) — the strong law and its variance criterion | https://doi.org/10.1007/978-3-642-49888-6
[^18]: Durrett, *Probability: Theory and Examples*, 5th ed. — SLLN, Kolmogorov's three-series theorem, and the ergodic and martingale substitutes | https://doi.org/10.1017/9781108591034
[^19]: Retrieval as a cache; commits as the Lamport clock versioning it — the mechanism that makes iterations dependent | methodology/philosophy.yaml#L32-L39
    > That cache is updated on COMMITS — a commit hitting the relevant bits retrains the RAG. Commits are therefore the LAMPORT CLOCK of the RAG models: they causally order and version the cached knowledge against the code
[^20]: Birkhoff, *Proof of the ergodic theorem*, PNAS 17 (1931) | https://doi.org/10.1073/pnas.17.2.656
[^21]: Cousot & Cousot, *Abstract Interpretation*, POPL 1977 | https://doi.org/10.1145/512950.512973
[^22]: The concession: no Galois connection is defined — "an abstraction discipline, not a formal abstract interpreter" | methodology/math-foundations.yaml#L76-L89
    > Tillandsias does not yet define a full Galois connection between program semantics and spec obligations. Until then, this is an abstraction discipline, not a formal abstract interpreter.
[^23]: Floyd, *Assigning Meanings to Programs* (1967), cited for ranking-style progress reasoning | https://doi.org/10.1090/psapm/019/0235771
[^24]: Scores are not probabilities; finite coverage is not proof of absence | methodology/math-foundations.yaml#L122-L135
    > Evidence bundles and CentiColon scores should not be interpreted as probabilities. If probabilistic or belief-function confidence is later added, it must be a separate layer from obligation closure.
[^25]: Shafer, *A Mathematical Theory of Evidence* (1976), cited as a possible separate confidence layer | https://press.princeton.edu/books/paperback/9780691100425/a-mathematical-theory-of-evidence
[^26]: Walley, *Statistical Reasoning with Imprecise Probabilities* (1991) | https://doi.org/10.1007/978-1-4899-3472-7
[^27]: What actually computes the score: a sixteen-arm hardcoded weight table over CI check names | scripts/local-ci.sh#L384-L403
    > check_weight() { case "$1" in spec-cheatsheet-binding) echo 100 ;; spec-code-drift) echo 120 ;; spec-trace-coverage) echo 90 ;; version-monotonicity) echo 40 ;;
[^28]: The committed dashboard's earned and total figures | docs/convergence/centicolon-dashboard.json#L75-L76
    > "total_cc": 990, "earned_cc": 890,
[^29]: The framework specification delegating CentiColon arithmetic to a crate that is a README and one example file | methodology/litmus-framework.yaml#L88-L96
    > files: - crates/tillandsias-litmus/src/convergence/mod.rs - crates/tillandsias-litmus/src/convergence/centicolon.rs
[^30]: The uninstrumented complexity constraint and its 5000-line red flag | methodology/convergence.yaml#L329-L342
    > ratio_constraint: "methodology_complexity / codebase_complexity < 0.15" anti_pattern: > A validation system that requires more code to understand than the code being validated. Red flag: CI validators exceed 5000 lines or require specialized training to understand.
[^31]: The three CRDT primitives, and why each field uses the one it does | crates/tillandsias-plan/src/fragments.rs#L28-L39
    > Applying LWW to a LIST would silently discard the loser's entries, which is why events are a set and not a register.
[^32]: Semantic merge typed as a cache with CRDT preconditions, plus the anti-pattern | methodology/cheatsheets.yaml#L88-L114
    > Calling a lossy semantic cache a CRDT without stable IDs, tombstones, deterministic merge, and property tests creates false convergence claims.
[^33]: Determinism rules: fold order and idempotence | crates/tillandsias-plan/src/fragments.rs#L41-L49
    > Fragments fold in `(ts, filename)` order, never directory order — the filesystem does not promise an order, and two hosts folding differently would compute different states from identical inputs, which presents as corruption rather than as a sorting bug.
[^34]: Commutativity and idempotence of the fold pinned as named tests | crates/tillandsias-plan/src/fragments.rs#L2648-L2668
    > fn the_fold_is_commutative_the_defining_crdt_property() { Order of arrival must not change the result.
[^35]: Rank-aware status join with a falsification escape hatch | crates/tillandsias-plan/src/fragments.rs#L307-L320
    > The closure ladder implemented<completed<verified<done is a monotone lattice: you climb UP freely and move DOWN only through a `falsified` event.
[^36]: A retracted CRDT claim, with the failed property named | crates/tillandsias-plan/lua/collect.lua#L7-L11
    > This is a SEEN-SET DEDUP, not a CRDT — the earlier header's CRDT claim (commutativity in particular) was false: first-wins keeps whichever duplicate arrives first, so order matters.
[^37]: The join-semilattice argument for the version scheme, and the SemVer critique | methodology/versioning.yaml#L104-L124
    > SemVer (Major.Minor.Patch) allows arbitrary resets: Patch can go 1→2→1 if someone hotfixes a branch. There is no natural total order.
[^38]: CRDT preconditions filed at claim strength "external analogy" | methodology/provenance.yaml#L179-L192
    > claim_strength: external_analogy
[^39]: The documented component semantics the project retired | methodology/versioning.yaml#L9-L20
    > Major: meaning: "Contract version — breaking changes only"
[^40]: Thesis defence position: finite ordered convergence under declared validators, with unknown-event intake as the escape hatch | methodology/math-foundations.yaml#L200-L206
    > The defensible claim is finite ordered convergence under declared validators: stable obligations form a finite lattice; evidence-improving transitions are checked for monotonicity; CentiColons are a bounded ranking function over that model; fixed points mean validator stability; and unknown-event intake is the escape hatch
[^41]: Generative property tests for monotonicity, inflationarity and idempotence of the refinement operator, over a committed rule set | crates/tillandsias-plan/src/obligation_props.rs#L172-L219 @v56.9.5.1
    > MONOTONICITY over the real rule set — what Knaster-Tarski actually needs and what the methodology's idempotence check never examined. #[test] fn refine_is_monotone_on_the_real_rules((x, y) in comparable_pair()) {
[^42]: The gate that refuses a missing or duplicated requirement identifier, and states what it cannot check | scripts/check-requirement-ids.sh#L5-L35 @v56.9.5.1
    > Every spec requirement carries a stable identifier, and no two carry the same one.
[^43]: The shell scorer hands its weights to the model instead of summing them itself | scripts/local-ci.sh#L538-L563 @v56.9.5.1
    > What LEFT is the arithmetic: earned/denominator/residual are now computed by `tillandsias-plan score-checks`, which runs obligation::centicolon_function over a SpecState.
[^44]: The ranking function in code names which side of the monotone band a score is on | crates/tillandsias-plan/src/obligation.rs#L620-L638 @v56.9.5.1
    > Outside the band, with the reason NAMED rather than implied. A consumer must not read a rise or fall across this boundary as progress or regress. Broken(&'static str),
