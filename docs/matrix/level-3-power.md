# Level 3 — Power User

## A private region you can throw away

Tillandsias gives you a **region** — a small self-contained cloud on your own machine, built so you can destroy it at any moment without losing anything you care about. It is one Fedora guest (a VM, or a WSL2 distro on Windows) running a rootless Podman stack:

- a **forge** — the container your coding agent runs in, one per project;
- a **git mirror** — a bare repo on the internal network, the only route your work takes out;
- a **vault** — a secrets store for your tokens;
- a **forward proxy** — the single outbound door;
- a **router** — a Caddy reverse proxy giving web services stable names.

@fig:layers

Everything hangs on one network rule: the containers share a Podman network created with `--internal` — no NAT, no route to the internet.[^1] Only the proxy is dual-homed onto an egress network, and adding a member without recording it in the same commit is refused by a guard.[^1]

Starting one is a curl on Linux, an installer script on macOS, a tray executable on Windows. Then: `tillandsias --headless /path/to/project --claude`.

> GREEN: Isolation is structural — one `--internal` network, exactly one dual-homed container — not a firewall ruleset you maintain, and the membership guard fails in both directions.

## What "ephemeral" actually buys you

The agent tools exist **only inside the forge image**, never on your host `$PATH`; if the image is missing the launcher refuses rather than fall back to a host binary.[^2] Mounts are enumerated — your project, a read-only CA certificate, a tmpfs, a per-launch temp dir — so `$HOME`, `~/.config` and your keychain are unreachable from inside.[^3]

By default the forge never touches your working tree: it clones fresh from the enclave mirror, and pushes travel back through it on their way upstream.[^4] An opt-in escape hatch bind-mounts your real checkout read-write, printing a reduced-isolation warning when used.[^5] Hence the blunt rule: **a finding you did not push is a finding you destroyed.**[^6]

@fig:ephemeral

**Idempotent** is the companion property: every layer comes up clean from scratch, so the declared response to a broken container, guest or stack is destroy-and-recreate, never hand-patch:

- **Survives a stop:** the bare mirror in its per-project volume, and your host working copy, fast-forwarded from the mirror non-destructively (skipping a dirty tree, detached HEAD or non-fast-forward).
- **Survives a stop:** vault data, auto-unsealed from a single Shamir share in your host keychain — no passphrase prompt, and the share only ever lands on tmpfs.[^7]
- **Survives even `podman system reset`** (on Linux): the model cache, being a bind-mounted host directory rather than a named volume — a distinction the spec spells out, having once cost someone a wrong answer.[^8]
- **Does not survive `--reset-guest`:** it wipes the vault and every enclave container, volume and secret, then re-initializes, keeping the model cache. Push first.[^9]

Web services never publish to the world: the router binds one loopback address (`80`, falling back to `8080`, then `--port`) and maps `<service>.<project>.localhost` onto internal ports.[^10] Nothing listens on `0.0.0.0`.

> GREEN: On Linux the teardown/keep boundary is documented per artifact and matches the code.

> GREEN: A standing audit corrected the routing spec against the live runtime — it had pinned a privileged port a rootless host cannot always bind — leaving the invariant it protects, loopback-only, untouched.[^10]

> RED: The repo's own stack-orchestration script creates the enclave network with **no `--internal`** — a stack brought up that way is not isolated, and nothing checks for the missing flag.[^11]
> PATH: No path to green is recorded in the repo.

> RED: On macOS the "cache survives" promise is false. The VM exposes one shared directory, so the model cache and engine payload sit inside the VM disk image — four code paths delete it, the shipped uninstaller included, costing a ~2.5 GB re-download; a partially restored cache yields an inference service that answers a version check but fails every request.[^12]
> PATH: An open, ready item; the smallest named fix is a second shared directory, gated behind a related uninstaller fix.

> RED: On Windows, wiping the guest leaves the old unseal share in Credential Manager and the tray pushes that dead key into the fresh guest, permanently breaking GitHub login.[^13]
> PATH: Half landed — wipe paths now clear the host credential. The reconcile half (a delivered share that fails to authenticate must lose to the guest's own secret) is blocked: the delivery reply carries no accept/reject signal. A stale credential must be removed by hand.

> RED: Once a host is initialised, the container engine's global config routes *all* registry traffic through the enclave proxy unconditionally, so with the stack down `podman build` and `podman pull` die on a raw DNS error naming nothing.[^14]
> PATH: An open, ready item: a build must either not depend on a service that may be absent, or fail with a verdict naming the proxy.

## How it is held together

The method has a name: **monotonic reduction of uncertainty under verifiable constraints**. Read it as a loop: specs declare intent, litmus tests turn each requirement into an executable signal, code implements, traces prove it ran, a gate refuses anything that breaks the chain.

Progress is a **bounded ranking function**, not a probability: each spec gets a denominator from weighted obligations, and an obligation earns credit only when its evidence is queryable and the cited artifact exists at that revision.[^15] The loop attacks the *worst* residual, not the easiest passing test.

@fig:staircase

The honest version of the convergence claim, stated by the project itself: the residual must not increase release over release, and **the target moves**, because the specs keep growing.[^16] With $d_v$ the distance between implementation and specs at release $v$:

$$d_{v+1} \le d_v \implies d_v \to d_* \ge 0$$

Non-increase gives you a floor; it does **not** prove the floor is zero. Within a release the bar is frozen, which is what makes "done" decidable there; across releases it steps up at operator-gated boundaries. Banach-style contraction is explicitly *not* claimed — no metric, operator and constant have been proven — and the methodology says so, citing the theorem it declines to invoke.[^17]

The loop favours many small iterations over one long one for the same reason: one prompt is a single finite sample landing near the answer with a bias. Fighting that bias inside the prompt is a weak-law problem; keeping each iteration small with **bounded** skew and letting the stream run buys almost-sure convergence. With unbounded per-iteration skew, infinite iterations still do not converge.[^18]

> GREEN: The math is scoped honestly — scores are labelled obligation closure, not confidence, and the one theorem that would make the story sound stronger is listed as not claimed.

Read a green gate with care: eleven litmus files sit on disk and have never been executed by any suite — grandfathered onto a shrink-only list so that switching the gate on did not flip them all red at once.[^19]

> RED: There is no push CI and no PR CI. Actions runs exactly one workflow, the release, because the signing keys exist only in the cloud. Nothing server-side validates a push; the local gate is the sole trunk protection, made load-bearing after an agent pushed unparseable code and every developer inherited the red build.[^20]
> PATH: Not restoration — a deliberate trade for budget, with a standing obligation to run the local gate before every push, and an instruction not to add a workflow to catch what a local gate should.

## Footnotes

[^1]: Enclave network requirements — `--internal` creation, reuse, proxy-only egress, and the documented-membership guard | openspec/specs/enclave-network/spec.md#L17-L69
[^2]: Forge-as-only-runtime: the four agent binaries must resolve inside a fresh forge, and the host must not need them | openspec/specs/forge-as-only-runtime/spec.md#L49-L67
[^3]: Regression test asserting no user home is mounted into a forge | crates/tillandsias-headless/src/main.rs#L18844
[^4]: Bare mirror per project in a named volume; forge pushes persist there | openspec/specs/git-mirror-service/spec.md#L18-L38
[^5]: Clone-only is the default; the host-mount is an opt-in escape hatch with a loud reduced-isolation warning | crates/tillandsias-headless/src/main.rs#L5740-L5775
[^6]: The ephemerality rule, stated for agents | AGENTS.md#L47
[^7]: Auto-unseal from the host native keychain, no passphrase prompt, share on tmpfs only | openspec/specs/tillandsias-vault/spec.md#L76-L95
[^8]: Model cache is a host bind mount, NOT a named volume — and why that decides what `podman system reset` destroys | openspec/specs/inference-container/spec.md#L28-L30
[^9]: What `--reset-guest` wipes and what it keeps | crates/tillandsias-headless/src/main.rs#L1377-L1381
[^10]: Loopback-only publish, the 80→8080→`--port` fallback chain, and the 2026-09 freshness audit that corrected the drifted literals | openspec/specs/subdomain-routing-via-reverse-proxy/spec.md#L2-L42
[^11]: Stack orchestration script creating the enclave network without `--internal` | scripts/orchestrate-enclave.sh#L76-L90
[^12]: macOS model cache and engine payload live inside the VM disk image; the four code paths that delete it (status: ready) | plan/index.yaml#L28798-L28845
[^13]: Windows Credential Manager retains a stale unseal share across a guest wipe; Part A landed, the reconcile half still open (status: ready) | plan/index.yaml#L27914-L27960
[^14]: Global container config hardcodes the enclave proxy, so builds fail on DNS when the stack is down (status: ready) | plan/index.yaml#L38649-L38660
[^15]: CentiColon weights and denominators — a bounded ranking function, not a probability | methodology/proximity.yaml#L13-L33
[^16]: The per-release inequality, the floor, and why a stepping bar is not a moving goalpost | methodology/convergence.yaml#L462-L472
[^17]: Contraction-not-claimed, with the metric, operator and constant a future claim would have to supply | methodology/math-foundations.yaml#L106-L120
[^18]: Weak vs strong law of large numbers as an iteration-velocity argument | methodology/philosophy.yaml#L8-L27
[^19]: The ratchet list of litmus files that have never run, and why they are exempt | openspec/litmus-tests/unbound-grandfathered.txt
[^20]: The Actions budget ruling: one workflow, what was removed, and what was given up | methodology/ci.yaml#L286-L324
