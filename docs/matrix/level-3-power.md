# Level 3 — Power User

## The anatomy

The region is one Fedora guest — a VM, or a WSL2 distro on Windows — running a rootless Podman stack. Five members:

- a **forge**, the container your coding agent runs in, one per project;
- a **git mirror**, a bare repo on the internal network;
- a **vault** holding your tokens;
- a **forward proxy**, the single outbound door;
- a **router**, a Caddy reverse proxy giving web services stable names.

@fig:layers

One rule carries the isolation: the containers share a Podman network created with `--internal` — no NAT, no route out.[^1] Only the proxy is dual-homed onto an egress network. Membership is not a maintained list; a guard reads the live network and refuses a member added without a matching record in the same commit, in both directions.[^1]

The router publishes to one loopback address (`80`, falling back to `8080`, then `--port`) and maps `<service>.<project>.localhost` onto internal ports. Nothing binds `0.0.0.0`.[^2]

Starting one is a curl on Linux, an installer script on macOS, a tray executable on Windows. Then `tillandsias --headless /path/to/project --claude`.

> GREEN: Isolation is structural — one `--internal` network, exactly one dual-homed container — not a firewall ruleset you maintain.

> GREEN: A standing audit corrected the routing spec against the live runtime: it had pinned a privileged port a rootless host cannot always bind. The invariant it protects, loopback-only, was untouched.[^2]

> RED: The repo's own stack-orchestration script creates the enclave network with **no `--internal`**. A stack brought up that way is not isolated, and nothing checks for the missing flag.[^3]
> PATH: No path to green is recorded in the repo.

## What the walls are made of

Agent tooling exists only inside the forge image, never on your host `$PATH`; a missing image makes the launcher refuse rather than fall back to a host binary.[^4] Mounts are enumerated — your project, a read-only CA certificate, a tmpfs, a per-launch temp dir — so `$HOME`, `~/.config` and your keychain are simply not addressable from inside, and a regression test asserts no user home is ever mounted.[^5]

@fig:ephemeral

The forge does not touch your working tree by default: it clones fresh from the enclave mirror, and pushes travel back through the mirror on their way upstream.[^6] An opt-in escape hatch bind-mounts your real checkout read-write and prints a reduced-isolation warning. Hence the blunt operating rule: **a finding you did not push is a finding you destroyed.**[^7]

## What survives, exactly

Idempotence is what makes destroy-and-recreate a repair procedure rather than a loss. Every layer comes up clean from scratch, so the boundary worth memorising is not "will it break" but "what is on which side of the wipe":

- **Survives a stop:** the bare mirror in its per-project volume, plus your host working copy, fast-forwarded from the mirror non-destructively — skipped on a dirty tree, a detached HEAD, or a non-fast-forward.[^6]
- **Survives a stop:** vault data, auto-unsealed from a single Shamir share held in your host keychain. No passphrase prompt, and the share only ever lands on tmpfs.[^8]
- **Survives even `podman system reset`,** on Linux: the model cache, because it is a host bind mount and not a named volume. The spec spells that distinction out, having once cost someone a wrong answer.[^9]
- **Does not survive `--reset-guest`:** it wipes the vault and every enclave container, volume and secret, then re-initialises, keeping the model cache. Push first.[^10]

> GREEN: On Linux that boundary is documented per artifact and matches the code.

> RED: On macOS the "cache survives" line above is false. The VM exposes one shared directory, so the model cache and engine payload sit inside the VM disk image; four code paths delete it, the shipped uninstaller included, costing a ~2.5 GB re-download. A partially restored cache is worse than none — the inference service answers a version check and then fails every request.[^11]
> PATH: An open, ready item; the smallest named fix is a second shared directory, gated behind a related uninstaller fix.

> RED: On Windows, wiping the guest leaves the old unseal share in Credential Manager, and the tray pushes that dead key into the fresh guest, permanently breaking GitHub login.[^12]
> PATH: Half landed — wipe paths now clear the host credential. The reconcile half, in which a delivered share that fails to authenticate must lose to the guest's own secret, is blocked: the delivery reply carries no accept/reject signal. Until then, remove the stale credential by hand.

> RED: Once a host is initialised, the container engine's global config routes *all* registry traffic through the enclave proxy unconditionally. With the stack down, `podman build` and `podman pull` die on a raw DNS error that names nothing.[^13]
> PATH: An open, ready item: a build must either not depend on a service that may be absent, or fail with a verdict that names the proxy.

## Driving it, and where the gate sits

@fig:gate

The verification the earlier levels described is, operationally, a **local** gate: specs declare intent, litmus tests turn each requirement into an executable signal, traces prove the signal ran, and the gate refuses a commit that breaks the chain. Two things follow that change how you work.

First, read a green gate with care. Eleven litmus files sit on disk and have never been executed by any suite — grandfathered onto a shrink-only list so that switching the gate on did not flip them all red at once.[^14] The list may shrink; nothing may join it.

Second, the gate on your machine is the only gate there is.

> RED: There is no push CI and no PR CI. Actions runs exactly one workflow, the release, because the signing keys exist only in the cloud. Nothing server-side validates a push; the local gate is the sole trunk protection — made load-bearing after an agent pushed unparseable code and every developer inherited the red build.[^15]
> PATH: Not restoration. This is a deliberate budget trade, carrying a standing obligation to run the local gate before every push and an explicit instruction not to add a workflow to catch what a local gate should have caught.

## Footnotes

[^1]: Enclave network requirements — `--internal` creation, reuse, proxy-only egress, and the documented-membership guard | openspec/specs/enclave-network/spec.md#L17-L69
[^2]: Loopback-only publish, the 80→8080→`--port` fallback chain, and the 2026-09 freshness audit that corrected the drifted literals | openspec/specs/subdomain-routing-via-reverse-proxy/spec.md#L2-L42
[^3]: Stack orchestration script creating the enclave network without `--internal` | scripts/orchestrate-enclave.sh#L76-L90
[^4]: Forge-as-only-runtime: the agent binaries must resolve inside a fresh forge, and the host must not need them | openspec/specs/forge-as-only-runtime/spec.md#L49-L67
[^5]: Regression test asserting no user home is mounted into a forge | crates/tillandsias-headless/src/main.rs#L18844
[^6]: Bare mirror per project in a named volume; forge pushes persist there | openspec/specs/git-mirror-service/spec.md#L18-L38
[^7]: The ephemerality rule, stated for agents | AGENTS.md#L47
[^8]: Auto-unseal from the host native keychain, no passphrase prompt, share on tmpfs only | openspec/specs/tillandsias-vault/spec.md#L76-L95
[^9]: Model cache is a host bind mount, NOT a named volume — and why that decides what `podman system reset` destroys | openspec/specs/inference-container/spec.md#L28-L30
[^10]: What `--reset-guest` wipes and what it keeps | crates/tillandsias-headless/src/main.rs#L1377-L1381
[^11]: macOS model cache and engine payload live inside the VM disk image; the four code paths that delete it (status: ready) | plan/index.yaml#L28798-L28845
[^12]: Windows Credential Manager retains a stale unseal share across a guest wipe; the wipe half landed, the reconcile half still open (status: ready) | plan/index.yaml#L27914-L27960
[^13]: Global container config hardcodes the enclave proxy, so builds fail on DNS when the stack is down (status: ready) | plan/index.yaml#L38649-L38660
[^14]: The ratchet list of litmus files that have never run, and why they are exempt | openspec/litmus-tests/unbound-grandfathered.txt
[^15]: The Actions budget ruling: one workflow, what was removed, and what was given up | methodology/ci.yaml#L286-L324
