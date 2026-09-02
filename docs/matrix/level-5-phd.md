# Level 5 — For the PhD / MathWiz / Hacker

You asked for it at your level. Fine. Read slowly; the interesting parts are the
places where the repository is *more* honest than you were expecting, and the
places where it is not.

## WHAT IT IS

Tillandsias is a tray binary that folds a disposable cloud region through your
hypervisor. Strip the marketing and the architecture is a four-tier containment
funnel — host tray → guest VM → podman enclave → forge container — with exactly
one declared execution surface and an argv-level policy checker standing in
front of it.

**The funnel.** The host runs one Tillandsias-owned process: a GTK/SNI tray on
Linux (`crates/tillandsias-headless`, whose `main.rs` is a 25k-line
orchestrator), a Win32 `NotifyIcon` tray, or an AppKit `NSStatusItem` — the
latter two sharing `crates/tillandsias-host-shell`, so their platform-specific
code is menu plumbing and nothing else. On macOS and Windows that process first
materialises a Fedora guest (Virtualization.framework VM, or a WSL2 distro)
through `crates/tillandsias-vm-layer`, whose `VmRuntime` trait is deliberately
the twin of the `ContainerRuntime` surface in `crates/tillandsias-podman`. The
guest is not a bespoke rootfs: `images/vm/manifest.toml` pins
`registry.fedoraproject.org/fedora:44` **by digest, per architecture**, names
Fedora's own artifact URLs and an `expected_rootfs_sha`, and exposes its
`recipe_sha` as `vm.recipe@<sha>` in the `Hello.capabilities` handshake so a
stale recipe is detectable rather than merely wrong. Inside the guest, rootless
Podman brings up a stack on an `--internal` network `tillandsias-enclave`
assembled from `images/{git,proxy,web,vault,router,inference,chromium,builder,
default}`. Agents run in the deepest container — the *forge* — and nowhere else.

That last clause is not aspiration.
`openspec/specs/forge-as-only-runtime/spec.md` forbids `Command::new("opencode")`
and its siblings anywhere in `crates/tillandsias-headless/src/` or
`crates/tillandsias-podman/src/`, requires the tray to *refuse* rather than fall
back when the forge image is missing, and declares the mount categories
**exhaustive**: exactly four legal sources — the canonical project workspace at
`/home/forge/src/<project>`, the ephemeral CA-cert dir from
`ensure_enclave_for_project` mounted read-only, `--tmpfs`, and a per-launch
`mktemp -d`. `$HOME`, `~/.config`, `~/.cache` are unreachable by construction,
pinned by the regression test the spec names in its own prose,
`launch_forge_agent_does_not_mount_user_home`. An exhaustive-categories
requirement is a *closed* predicate over one argv vector. That is the right
shape: falsifiable by inspecting a `Vec<String>`, not by arguing about least
privilege.

**The hardening envelope is a pure function.**
`crates/tillandsias-podman/src/policy.rs` declares
`MANDATORY_HARDENING_FLAGS: [&str; 4] = ["--userns=keep-id", "--cap-drop=ALL",
"--security-opt=no-new-privileges", "--security-opt=label=disable"]` and returns
typed `LaunchArgvError::{MissingRunSubcommand, MissingImage,
MissingMandatoryHardening, WeakensMandatoryHardening}`. Note the fourth variant:
it catches argv that *re-weakens* a flag already present
(`no-new-privileges=false`), which is the failure a naïve `contains()` check
misses. The module "deliberately does not execute Podman" — it is an auditable
checker, so the property is decidable before any OS process exists. `--rm` is
excluded on purpose; container ephemerality is a per-profile choice, the four
flags are not. And the consequence is real: `images/router/` strips
`cap_net_bind_service` from `/usr/bin/caddy`, because the kernel refuses to exec
a file-capability binary under `--cap-drop=ALL` +
`--security-opt=no-new-privileges`. The envelope binds hard enough to break
things, which is how you know it is on.

**Ephemerality is a stated invariant, not an emergent property.**
`methodology/philosophy.yaml` lists `runtime_substrate_is_ephemeral_recreate_
never_repair` among `global_invariants`, with a recreate ladder (podman/stack →
guest → host tray → release) and an `error_message_policy` that pushes the word
"recreate" into user-facing text. Repair is not a degraded mode here; it is a
category error. Idempotence follows: if the substrate is always recreated from a
same-revision image, re-running the launch is the identity on observable state.
Where idempotence is *claimed* it is tested — `ensure_containers_conf_dns_
servers` carries an explicit idempotency test; `populate_hot_paths()` must be
idempotent by spec; `cache-isolation` states outright that cache deletion is
never data loss because "the next launch MUST rebuild missing cache artifacts."
Forge staleness is keyed on `.last-build-forge.sha256` over **source hash only**,
so a `VERSION` bump refreshes human aliases and rebuilds nothing;
`containerfile-staleness` forbids comparing file mtimes and requires the runtime
image source digest. The four HOT tmpfs roots (`/opt/cheatsheets` 8MB,
`/home/forge/src` computed, `/tmp` 256MB/01777, `/run/user/1000` 64MB/0700) are
capped by `--tmpfs=<path>:size=<N>m,mode=<oct>` — kernel ENOSPC, not advisory —
and the spec says of a fifth: *"'Maybe a hot path' is a HARD NO."*

**The transport boundary is cryptographic, and version-bound by derivation
rather than comparison.** `crates/tillandsias-secure-channel` secures both hops
of the transparent exec chain (host tray ⇄ guest headless over vsock, guest ⇄
container) with
`PSK = HKDF-SHA256(ikm=release_root_secret, salt="tillandsias-control-channel",
info="v=<build_version>;wire=<wire_version>;hop=<hop_id>")`. Mismatched
releases do not *reject* each other; they cannot derive the same key, which is
strictly stronger than a version check an attacker can lie about — and it is why
`methodology/convergence.yaml` can list `"dual plaintext+secure acceptance in
the same boot"` as a **forbidden shortcut**. `crates/tillandsias-control-wire`
carries `[4-byte BE length][postcard ControlEnvelope]` with a `#[non_exhaustive]`
message enum whose variants are tombstoned, never reordered.
`crates/tillandsias-headless/src/exec_allowlist.rs` is a pure function (kept out
of `pty_handler` precisely because that module sits behind a feature combination
nobody lints): the verbatim-argv arm requires `argv[0]` to start with
`/usr/local/bin/`, `/usr/bin/` or `/bin/`, contain no `/..`, and have a basename
that is not any of `bash|sh|dash|zsh|ksh|fish|env` — after which arguments reach
`execve` untouched, so `a$(id)b` arrives as one data element. It is advertised
as capability `ExecArgvVector` in `HelloAck.server_caps` because hosts must
feature-detect, never version-compare. Secrets live in an in-enclave Vault
(`https://vault:8200`, AppRole tokens on 1h TTLs, no host port map in VM
launches) and the GitHub token never crosses into a forge at all — pushes go
through a `git push --atomic` pre-receive relay in `images/git/`.

**And the receipts, including the unflattering ones.** Push CI was removed
2026-08-03; the whole gate is `./build.sh --ci-full` on your own metal. What
stops an unstamped push is `scripts/gate-stamp.sh`, the best-engineered thing
here: a hook that runs the gate gets `--no-verify`'d on its second use, so the
gate instead *stamps* a digest over `HEAD` plus the full working-tree diff
**including untracked files**, and the hook verifies currency for the cost of
one hash. Since order 765-dt8h the stamp carries a `scope`, because `--check`,
`--ci` and `--ci-full` validate materially different things and previously wrote
byte-identical stamps; the class vocabulary is closed and **total**, with
unrecognised paths mapping to `other`, which only `scope full` covers. v1 stamps
are refused loudly rather than having a scope inferred — a correct refinement of
a partial function into a total one. Against that, the README's own release
table records `755-qcxh`: *"the enclave's TLS-interception CA private key is
0644 in /tmp — any local uid can mint certificates the enclave trusts; squid
only reads it because everyone can."* The Vault leaf key goes through a podman
secret. The MITM CA key did not. Both facts are in the repository, which is more
than most projects manage; only one of them is in the marketing.

## HOW IT WAS BUILT

The thesis is one sentence, and it is the title of a file:
**monotonic reduction of uncertainty under verifiable constraints**. The
eponymous root YAML is now a tombstone pointing at the nine-component split
under `methodology/`; the live statement is `methodology/philosophy.yaml`'s
`core_principle`.

### The formalisation, and its refreshingly narrow claims

`methodology/math-foundations.yaml` is where you should aim your scepticism, and
where you will be partly disarmed. The model:

- An **obligation** is a named auditable requirement with a stable ID, its state
  ranging over the finite chain `absent < declared < traced < positively_tested
  < negatively_tested < runtime_observed < evidence_bundled`.
- `spec_state` is the **product lattice** of those states; `project_state` the
  product over active specs, ordered componentwise after aligning stable IDs and
  tombstones.
- `centicolon_function: spec_state → ℕ` is bounded and "monotone **only** for
  evidence transitions that preserve obligation IDs and do not introduce
  penalties, ambiguity, or denominator scope changes."

Five claims carry backing refs and — the part that matters — explicit
`limits`. `math.order.lattice-model@v1` (Tarski 1955; Davey & Priestley) proves
monotonicity *of the model, not truth of the modelled requirement*.
`math.fixpoint.convergence-target@v1` (Kleene) defines closure as
`refine(refine(state)) == refine(state)` — idempotence under *known* validators,
not completeness against unknown requirements.
`math.abstract-interpretation.evidence-abstraction@v1` (Cousot & Cousot)
concedes that **no Galois connection is defined**: "an abstraction discipline,
not a formal abstract interpreter." `math.metric.contraction-not-claimed@v1`
cites Banach 1922 *in order to disclaim it*, specifying the debt a future claim
would owe — a metric `d`, an operator `F`, a constant `0 ≤ c < 1` with
`d(F(x),F(y)) ≤ c·d(x,y)`. And `math.evidence.uncertainty-not-probability@v1`
(Shafer, Walley) forbids reading CentiColons as probabilities.

So no, you cannot dismiss this as lattice cosplay: a finite product order, a
bounded ranking function in the Floyd/Lyapunov sense, a fixed point under
declared validators, with contraction and Galois connections named *absent*.
`philosophy.yaml:multi_version_convergence` closes it: with `d_v = d(I_v, T_v)`
and `T` a moving target, release-over-release non-increase of `d_v` gives a
floor `d_* ≥ 0` and explicitly *not* `d_* = 0` — that needs a progress premise
excluding positive residual fixed points. `bar_raise_governance` supplies
decidability: the bar is fixed *within* a release and steps only at operator-cut
boundaries, so every intra-release convergence point is well defined. Discrete
operator-gated steps, not a continuously rising goalpost. The reasoning holds.

### Which CRDT discipline appears where — precisely

The word "CRDT" appears in three distinct places with three different degrees of
earning it, and the repo distinguishes them itself.

1. **The plan ledger — a real, tested CRDT.**
   `crates/tillandsias-plan/src/fragments.rs` (4799 lines) implements
   `base ⊕ fold(fragments)` over `plan/index.yaml` plus immutable
   `plan/index.d/<utc>-<suffix>-<host>.yaml`. Per-field discipline:
   `packets:` is a **G-Set** keyed by `packet_id` (union: commutative,
   associative, idempotent); `events:` is a **G-Set** keyed by
   `(packet_id, event identity)`; `fields:` (alias `status:`, order 642-fedr) is
   an **LWW-Register** keyed on `{packet_id}\u{1}{field}`, resolved by
   `(ts, host)`. Deletion is by **tombstone** — a G-Set has no remove, and a
   naïve delete is re-added by any replica that missed it. Determinism comes
   from folding in `(ts, filename)` order with UTC-first names, never directory
   order ("the filesystem promises none"). Convergence is pinned by
   `the_fold_is_commutative_the_defining_crdt_property`,
   `the_fold_is_idempotent_so_a_half_finished_compaction_is_safe` and
   `the_fold_is_order_independent`, among 78 tests in that file. Compaction
   deletes exactly the fragments it folded **by name, never a glob** — the
   GC-versus-writer race, named as such. And the wrinkle you would have found:
   `status_entry_wins` is not a plain LWW-Register. It composes a monotone rank
   join over `closure_rank: implemented(0) < completed(1) < verified(2) <
   done(3)` with LWW as tiebreak at equal rank, treats `obsoleted`/`failed` as
   lateral, and permits descent only on an explicit `incoming_falsified` flag —
   a lexicographic join with a deliberate non-monotone escape hatch, which is
   the spec system's bounded-uncertainty exception expressed in code.
2. **Version metadata — a genuine join-semilattice.** `versioning.yaml` argues
   correctly that SemVer has no natural total order (patch resets;
   `LUB(1.0.1,1.0.1)` loses causality) and a bare counter collides across nodes;
   a calendar anchor plus a build counter joins componentwise by max.
   `scripts/verify-version-monotonic.sh` enforces `VERSION ≥ latest tag`.
3. **Specs and cheatsheets — deliberately *not* claimed.**
   `spec-system.yaml:crdt_properties` is typed
   `semantic_merge_with_crdt_preconditions`; `cheatsheets.yaml:crdt_model` lists
   preconditions including
   `property_tests_for_commutativity_associativity_idempotence`, with the
   anti-pattern spelled out — calling a lossy semantic cache a CRDT "creates
   false convergence claims". `provenance.yaml:methodology.crdt.preconditions@v1`
   files it as `claim_strength: external_analogy` and keeps the weaker label
   "CRDT-like" until those property tests exist. **They do not exist**: no
   `proptest` or `quickcheck` anywhere in the workspace, and the fragment tests
   are example-based. Honest, and still an open obligation.

The best evidence that the honesty is load-bearing rather than decorative sits
in a Lua file. `crates/tillandsias-plan/lua/collect.lua` opens: *"This is a
SEEN-SET DEDUP, not a CRDT — the earlier header's CRDT claim (commutativity in
particular) was false: first-wins keeps whichever duplicate arrives first, so
order matters."* A retracted convergence claim, with the property that failed
named. Most repositories would have kept the word.

### The LUA layers

`crates/tillandsias-plan/src/lua_runtime.rs` embeds mlua and hot-reloads four
scripts (302 lines: `tier.lua`, `decompose.lua`, `collect.lua`, and `init.lua`
loaded last so it may reference the others). The division of labour after order
920-pxg6 is strict: **Lua owns tier classification, variant trimming and
collection dedup — deterministic data-in/data-out; Rust owns everything with
consequences** — dispatch, endpoints, retrieval, envelope construction, and
citation validation (`answer::verify` in `pipeline::run_grounded`). The dead
`validate.lua` was deleted, not demoted. The module doc is titled "SECURITY
SURFACE, exactly as implemented — a PARTIAL stdlib restriction, **not a
sandbox**": it enumerates what `new()` nils (`os.execute/exit/getenv`, the `io`
open/popen/close family, `debug`, `loadfile`, `dofile`, `require`), states that
`os.remove` and `os.rename` **remain reachable**, tells the reader to treat
`lua/` as trusted code, and adds *"Do not re-promise a stronger sandbox here
without implementing one — that phantom claim is what the 920-pxg6 audit
removed."*
`LatencyTier` (Immediate 500ms → NonUsable >15s) ties this to
`philosophy.yaml:convergence_via_velocity`: bound each prompt's skew (weak LLN)
and let iteration supply strong-LLN convergence — an analogy, but the correctly
stated one, with the hazard named (unbounded terminal skew defeats infinite
iteration). Its corpus-side counterpart,
`not-enough-information.yaml` + `declined-alternatives.yaml`, exists because
cosine top-k always returns k: refusal had to be written in as retrievable text.
One entry was then *corrected* for declaring systemd unused when
`packaging/systemd/user/tillandsias.service` exists — the harness had measured
that the record converted questions, never that it was true.

### Specs, litmus, and the centicolon wiring

Specs live at `openspec/specs/<capability>/spec.md` with RFC-2119 modality,
`ambiguity.score` with `allowed: 0`, and mandatory tri-binding to `@trace`,
litmus and cheatsheets. Verification is two orthogonal ladders: **S0–S3** for
the spec (draft → syntactically valid → litmus-bound → runtime-validated) and
**L0–L3** for an annotation's evidence (spec → +cheatsheet → +API docs →
+passing litmus), under `declared_level_is_claim` /
`ci_validates_against_observed_level`. Ambiguity is operational: run
behaviourally distinct candidates against the same litmus; if contract-relevant
outcomes differ while all pass, the spec is ambiguous and activation blocked.

Litmus tests are 411 YAML files (34,606 lines) with `spec:`, `phase:`, a
`size:` tier carrying wall-clock budgets, and a `critical_path:` of shell steps.
Read `litmus-added-fragment-parse-gate-shape.yaml` before dismissing the genre:
**negative controls in hermetic throwaway git repos** — a bare
`ts: 2026-08-12T15:31:54Z` must be *refused* and the quoted form *accepted*,
without which the negative control is satisfied by a gate that refuses
everything. It exists because a script claimed `# Pinned by litmus:…` for weeks
against a test nobody had written — now gated by
`scripts/check-litmus-pin-claims.sh`.
`scripts/litmus-stdlib.sh` supplies `mf_stage`/`mf_holds*` because
`producer | grep -q` yields one status for two stages and SIGPIPEs its producer;
`set -o pipefail` was *measured* to move 4 of 249 tests to FAIL, **all four
false positives**, so the fix is a consumer reading a complete buffer, not the
flag. Also measured: `mf_holds` shipped as ERE while 321 of 460 sites used BRE
`grep -q`, where `fail:…:state={state}` does not mismatch but *errors*. One
variant per grep flag.

### Where the claims outrun the evidence

Now the part you came for.

- **`crates/tillandsias-litmus` does not exist as code.** It has a `README.md`
  and `src/mock/podman.rs.example` — no `lib.rs`, no `Cargo.toml`, **not a
  workspace member**. Yet `methodology/litmus-framework.yaml` specifies four
  layers with named files (`src/signal/registry.rs`, `src/test/graph.rs`,
  `src/convergence/centicolon.rs`) and `litmus-centicolon-wiring.yaml` tells
  agents the arithmetic "is managed by the tillandsias-litmus CLI" and that they
  "MUST NOT attempt to calculate CentiColon budgets and residuals manually."
  The authority delegated to is a `.rs.example`.
- **The CentiColon obligation model is unimplemented.** `proximity.yaml`
  specifies weights (`must_requirement: 100`, `invariant: 120`,
  `negative_litmus_signal: 100`), multipliers, six `cap_rules` and sixteen
  penalties (`ghost_trace: -50` … `metric_gaming_suspected: -120`). Not one of
  those identifiers appears outside `methodology/` and the `.example`. What
  computes the score is `scripts/local-ci.sh`'s `check_weight()` — a hardcoded
  table over **13 CI checks** whose pre-build subset sums to exactly the
  `total_cc: 990` in the committed dashboard. "89.9% closed" is `890/990` over
  thirteen shell checks: a CI pass-rate in a lattice's clothes. No caps, no
  penalties, no per-spec rollup, no scope-change event.
- **The atomic unit of that model is missing from 92% of specs.** Earning
  requires `requirement_has_stable_id`. Of 177 spec files, **15** carry a
  `**ID**:` field, against 2141 occurrences of `MUST`.
- **`versioning.yaml` documents a scheme the project retired.** It defines
  `v<Major>.<Minor>.<YYMMDD>.<Build>` with `Major` = contract version, `Minor` =
  feature phase. The live format, per the 2026-08-31 operator ruling pinned in
  `litmus-versioning-shape.yaml`, is `<years_since_epoch>.<month>.<day>.<build>`
  — hence `56.9.2.1`. The join-semilattice argument survives; the documented
  *semantics* of two components are false. The repo caught this once — the
  release ledger records "the versioning-shape litmus still pinned the retired
  scheme (the drift-protection had drifted)" — and fixed the litmus, not the
  doctrine.
- **Controlled vocabularies leak because nothing validates them.**
  `spec-system.yaml` closes spec status to `{draft, active, deprecated,
  obsolete}`; `forge-as-only-runtime/spec.md` says `Status: current`.
  `proximity.yaml:397` reads `remove_or perturb_runtime_trace_emission…` — a
  space where an underscore belongs. The constraint is
  `all_spec_elements_must_be_machine_parsable`; no machine reads either
  alphabet.
- **The complexity constraint is breached by its own metric.**
  `convergence.yaml:methodology_complexity_constraint` requires
  `methodology_complexity / codebase_complexity < 0.15` and red-flags "CI
  validators exceed 5000 lines". Methodology YAML is ~9,991 lines against
  ~192,634 of Rust — 0.052, comfortably inside — but that denominator omits
  34,606 lines of litmus YAML and ~16,225 lines of `scripts/check-*.sh`
  validators, which alone exceed the stated red flag by more than 3×. The
  constraint is real; it is not instrumented, so it has never fired.

What survives is the interesting result. `scripts/trace-coverage.sh` reports
`specs=202 traced=184 ghost=18 annotations=4963 files=1585` live, and the ghost
gate is a **ratchet** against `openspec/ghost-trace-baseline.txt` failing in
*both* directions — new ghosts fail, a stale baseline fails too. Its header
explains why it deleted 171 generated `TRACES.md` files: they *looked* like they
discharged the required `trace_coverage_summary` field and did not — a
spec→file:line index is not a coverage summary — so a declared obligation sat
open its whole life behind ~4000 lines of per-cycle churn.

That is the real methodology, and it is better than its own scoring system: an
event-intake directory (`methodology/event/`, 33 records) for observations the
model did not predict, a bounded-uncertainty exception so monotonicity cannot
force retention of false certainty, and a demonstrated willingness to delete the
artefact that was pretending to be evidence. The formal apparatus is sound and
modest; the instrumentation meant to make it *binding* is a thirteen-row weight
table and a stale dashboard. Judge the thinking on the former, the claim on the
latter.
