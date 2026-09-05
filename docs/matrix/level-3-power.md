# Tillandsias, for a power user

## What you get the moment a forge opens

`tillandsias --headless /path/to/project --claude` starts a container with your project in it and an agent at the prompt. Nothing below is configured by you or by the agent: the context file the agent reads first lists the plumbing under the heading "all transparent — zero configuration needed".[^16] Every claim here is at the stable release; where the daily channel has moved on, the path line says so.

### The forge container

A forge is a Fedora Minimal image in two layers: a heavy base carrying the toolchains — gcc, make, cmake, Rust with cargo and rust-analyzer, Go, Node, Java, Python, the debuggers — and a thin runtime layer with the entrypoints, cheatsheets and the agent's configuration.[^17][^18] The tag is a content hash of its sources, so an unchanged rebuild is a no-op.[^19] The coding agents are not baked in: every launch refreshes them into a per-project cache volume that outlives the container, rolling back to the last known-good version when upstream ships a broken one.[^20][^21] Cheatsheets, `/tmp` and the runtime directory sit on RAM-backed tmpfs with hard caps.[^22] Eighty-one allowlisted commands — tmux and lazygit among them — are shims that install userspace Homebrew on first use.[^23] On start the forge writes a context file into the checkout naming what is present, what is absent, and what needs no configuring.[^24]

> GREEN: Works out of the box. The tool cache is a named volume, never a host path, so first-run installs survive the container's removal without opening a host-home surface.[^21]

> RED: The storage spec names four RAM-backed roots and a host RAM gate with a matching container memory ceiling; at this release three roots are mounted, the source tree is not one of them, and the RAM gate and the ceiling exist as library code nothing calls.[^25][^26] The Homebrew prefix is backed by no volume, so every on-demand tool is re-installed at every launch and its bootstrap needs live egress each time.[^27] And the context file tells the agent each such install verifies a signed attestation per bottle; the shim states that attestation is off, because fetching it would need a GitHub credential no forge may hold — what remains is integrity from one publisher.[^28][^29]
> PATH: The source tmpfs landed in the daily channel, sized from the mirror's pack.[^30] The RAM gate and ceiling stay an open, ready item whose remaining slice is named: run the host RAM check before launch and emit equal memory limits.[^26] The recorded remedy for the prefix asks for a decision between persisting it and baking the tools into the image.[^27] The context file's wording has no fix recorded.

### The HTTPS proxy and its cache

Every container is born with its proxy variables set and the proxy's certificate composed into the system trust bundle before any network client starts; no per-client CA variable is set, and a regression test refuses a launcher that tries.[^34][^35][^36][^37] The allowlist of developer hosts — registries, GitHub, cloud SDKs, model providers — is generous enough that npm, cargo, pip and flutter work unconfigured.[^38] It decrypts exactly one of them, GitHub's release-asset CDN, so a large asset is fetched once for the whole machine.[^39][^40] Everything else passes through encrypted, so the proxy never sees, and never caches, crates.io, npm, PyPI or api.github.com.[^41] What makes the second `cargo build` fast is not the proxy but a per-project cache volume for cargo, npm, pip and go that outlives the forge.[^42] A blocked host gets no 403: the connection is reset, and only the proxy log names the domain.[^43]

> GREEN: The trust wiring is pinned by a test: the forge launcher mounts the single runtime CA input read-only and sets none of the per-client CA variables.[^37]

> RED: The cache-hit claim for the one decrypted host has never been shown live. The fix for a rule order that made decryption unreachable shipped the config and static tests, and records that no real miss-then-hit trace was obtained.[^44]
> PATH: The next step is written down: on a Podman host, request one release-asset URL twice through the strict proxy and record a miss followed by a hit with equal checksums.[^44]

### Local inference

Every forge finds a model server at `http://inference:11434`, started on launch if it is not already running and shared across projects.[^45][^46] The first run pulls the engine and one small tool-capable chat model into a host directory that outlives the containers.[^47][^48][^9] Readiness is best-effort: a failed wait warns and the forge launches anyway.[^46] The context file tells the agent, in a closed vocabulary, what the host's accelerators are and whether the endpoint is ready — ready means at least one model is cached, never "starting up".[^49][^50] Larger tiers are opt-in behind an environment variable; the CPU floor is unconditional by spec.[^51][^52]

> GREEN: Works out of the box on the CPU floor, and a missing or broken endpoint never blocks a session.[^46]

> RED: Three limits. The engine is downloaded at first run from an unpinned "latest" release with no checksum and no signature, then executed inside the enclave.[^48][^53] GPUs reach the container only with a vendor stack — NVIDIA with a CDI spec, AMD when ROCm reports the card — and NPUs are named on every platform and used on none: no device argument for one exists in the launcher, and the spec itself says the engine cannot use them.[^54][^55][^56][^57] And the container's health check tests that the runner binary exists, not that a model loads.[^58]
> PATH: Integrity is an open, ready item: verify the tarball against the checksum file upstream already publishes.[^53] NPUs are two open, ready items — device passthrough for the container, and a host-native sidecar for Metal and the NPUs a Linux guest cannot see.[^59][^60]
> PATH: For the health check: No path to green is recorded in the repo. The entrypoint runs the real load check once at startup.[^58]

### The git mirror and push relay

Git needs nothing from you inside a forge. A read-only global gitconfig redirects the project's GitHub URL to a bare mirror in its own named volume, so `git remote -v` still says github.com while clone, fetch and push hit the enclave.[^61][^6] A push is not acknowledged until the mirror's hook has relayed exactly those refs upstream with one atomic push.[^62][^63] The token authorising that relay is read from the vault inside the git service at push time and never enters the forge.[^64][^65] Deletions and branch rewinds land nowhere;[^66] a project with no upstream keeps its pushes in the mirror.[^67]

> GREEN: Works out of the box once GitHub Login has run on the host; without a stored token the relay refuses the push and says so.[^68]

> RED: Offline, a push simply fails — nothing is queued.[^71] The authenticated SSH lane is built but dark behind an environment variable that defaults to off.[^70]
> PATH: Flipping the SSH lane on by default is an open, ready item, pending the transport decision behind it.[^72]

### The vault

Secrets live in a Vault container at `vault:8200`, reached over TLS with the enclave certificate already trusted.[^74][^75] A lane with a credentialed provider is handed a single-purpose token on tmpfs at `/run/secrets/vault-token` whose policy reaches only that provider's paths; the generic forge policy cannot read the GitHub token, which the git mirror, the tray and the login flow can.[^76][^77][^78][^79] Across a stop, Vault unseals itself from one Shamir share held in your host keychain, with no passphrase prompt.[^8]

> GREEN: The token is injected at container start with nothing for the agent to do, and a test pins that a credentialed lane gets exactly one scoped secret.[^76]

> RED: The context file tells the agent the vault is at `http://vault:8200`. The shipped listener is TLS-only, so that address answers an HTTP error; only the in-image helper carries the right default.[^80][^75][^81] The token defaults to a one-hour life and nothing in the lane renews it.[^82]
> PATH: No path to green is recorded in the repo.

### The experts and the project index

The agent finds four tool servers already registered, for Claude Code and OpenCode alike: git tools, a project index, the host-browser bridge, and a plan expert.[^83][^84] The index answers project type, status, commands and layout for any checkout, citing what it indexed; the plan expert returns cited answers or a typed refusal, never a guess, and answers only on a checkout carrying Tillandsias' own plan crate — elsewhere it reports itself degraded, by design.[^85][^86][^87] Both start in the background after the clone and never gate the session.[^88] The "on-demand" spec describes tray-side spawning and health checks that do not exist; the harness launches each server itself.[^89]

> GREEN: Works out of the box on any project, with no registration step.[^85]

> RED: The context file tells the Claude lane about a conversational Local Experts mode, but only the OpenCode configuration carries an agent that reaches the grounded endpoint behind it.[^90][^91] And the pre-expert-binary trap is half closed: a forge seeded from a checkout without the expert sources now reports itself degraded instead of ready, but the fresh-forge criterion — an in-forge probe grading full marks with no manual step — is recorded open.[^92]
> PATH: No path to green is recorded in the repo for the Claude-lane mismatch. The trap's entry stays open on purpose until the release-branch decision it waits on is made.[^92]

### Sibling web containers

Ask the agent to publish the project and it does not start a server in the forge. It asks the host, over a socket that exists only for that lane, to launch a sibling: a busybox httpd with the project mounted read-only, joined to the enclave network and given a router route.[^93][^94][^95][^96] The URL comes back as `http://www.<project>.localhost:<port>`, fetchable from the forge through the proxy.[^96][^97] The project is attributed from the socket the request arrived on, never from the request.[^95]

> RED: Works with caveats, and they are real. The sibling serves the repository root, so a site kept in a subdirectory answers 404 at `/` and `.git` was reachable through the router.[^98] Only `www` is routed, not the apex.[^96] Nothing reaps the sibling when the forge that published it dies: its name matches none of the stack sweep's patterns.[^99] The project must live under `~/src` on the host,[^100] the web image is built by initialisation rather than by a forge launch, so a host that never initialised hits a phantom registry pull,[^101][^102][^103] and the only end-to-end test of publishing has never been run by any suite.[^104]
> PATH: The document-root convention and the `~/src` assumption are open, ready items.[^98][^100]
> PATH: For the orphaned sibling and the phantom pull: No path to green is recorded in the repo.

### Chromium

Two browser images are built at initialisation: a minimal headless core, and a framework layer on top of it with GUI Chromium, Node and Playwright.[^101][^105][^106] The runtime launches the framework image as a read-only, capability-dropped, incognito app window — but only for the OpenCode-web and observatory modes, and only on a machine with a display.[^107][^108] The browser tool the agent sees — open, screenshot, click, type, close; eval switched off — is a different thing: it drives a host Chrome from the user's cache directory that nothing shipped installs, so a fresh host answers "browser unavailable".[^109][^110][^111][^112]

> RED: Spec-only in three places: the headless core is built and never run;[^105] the safe variant's proxy-only egress is a requirement without a launch flag, the script defaulting to host networking;[^114][^115] and the on-demand Chrome download the browser tool depends on has no caller.[^111] Partial in one: the tool's allowlist demands exactly three host labels, so a project whose directory name contains a dot — this site's does — can never open a window.[^113]
> PATH: The installer is an open, ready item — wire a real consumer or tombstone the script, its test and its spec.[^112]
> PATH: For the allowlist and the safe variant: No path to green is recorded in the repo.

## The anatomy

The region is one Fedora guest — a VM, or a WSL2 distro on Windows — running a rootless Podman stack. Among the members:

- a **forge**, the container your coding agent runs in, one per project;
- a **git mirror**, a bare repo on the internal network;
- a **vault** holding your tokens;
- a **forward proxy**, the single outbound door;
- a **router**, a Caddy reverse proxy giving web services stable names;
- an **inference container**, the shared model server.

The roster is longer — a Nix cache, a catalog service, the observatory's web container, an SSH-lane sidecar — and most of those do not run in an ordinary session.[^1] Membership is not a hand-kept list: the spec names the attach sites by function symbol, and a guard compares the attach sites it finds in the source with that list, refusing the build if either side drifts. It reads code, not a live network.[^1][^32]

@fig:layers

One rule carries the isolation: the containers share a Podman network created with `--internal` — no gateway, no route out.[^1] Only the proxy is dual-homed onto an egress network, and the launcher creates both networks on the first launch and reuses them after.[^1][^31]

The router publishes to one loopback address — port 80 by default, with fallbacks, or the port you pass with `--port` — and maps `<service>.<project>.localhost` onto internal ports. Nothing binds `0.0.0.0`.[^2][^116]

Starting one is a curl on Linux, an installer script on macOS, a tray executable on Windows. Then `tillandsias --headless /path/to/project --claude`.

> GREEN: Isolation is structural — one `--internal` network, exactly one dual-homed container — not a firewall ruleset you maintain. The launcher the tray runs passes the flag, and the membership guard runs in the build gate.[^1][^31][^32]

> GREEN: A standing audit corrected the routing spec against the live runtime: it had pinned a privileged port a rootless host cannot always bind. The invariant it protects, loopback-only, was untouched.[^2]

> RED: Two things the spec asks for are absent. It requires the network to be removed at application exit when empty; nothing implements that — the only removal is the destructive reset.[^1][^33] And the guard counts only builder and launcher functions by name, so an attach site written any other way is invisible to it.[^32]
> PATH: No path to green is recorded in the repo.

> RED: The repo's own stack-orchestration script creates the enclave network with **no `--internal`**. A stack brought up that way is not isolated, and at this release nothing checks for the missing flag.[^3]
> PATH: Fixed in the daily channel on 2026-09-03: the script now passes the flag, refuses to reuse an existing network that is not internal, and a build-gate check reads the create sites.[^117][^118][^119] Two sibling scripts — a per-project runner and a proxy diagnostic — still create the network without the flag and pass that gate, which checks a fixed list of three files.[^120][^121][^118] The launcher the tray actually runs created the network with the flag at both releases.[^31]

## What the walls are made of

Agent tooling exists only inside the forge image, never on your host `$PATH`; a missing image makes the launcher refuse rather than fall back to a host binary.[^4][^122] Mounts are enumerated — your project, a read-only CA certificate, the tmpfs roots, a per-launch temp dir, the persistent tool-cache volumes and a Tillandsias-written read-only gitconfig — so `$HOME`, `~/.config` and your keychain are simply not addressable from inside, and a regression test asserts no user home is ever mounted.[^5]

@fig:ephemeral

The forge does not touch your working tree by default: it clones fresh from the enclave mirror, and pushes travel back through the mirror on their way upstream.[^123][^124] An opt-in escape hatch bind-mounts your real checkout read-write and prints a reduced-isolation warning.[^125] Hence the blunt operating rule: **a finding you did not push is a finding you destroyed.**[^7]

## What survives, exactly

Idempotence is what makes destroy-and-recreate a repair procedure rather than a loss. Every layer comes up clean from scratch, so the boundary worth memorising is not "will it break" but "what is on which side of the wipe":

- **Survives a stop:** the bare mirror in its per-project volume, with everything you pushed to it.[^6]
- **Survives a stop:** vault data, auto-unsealed from a single Shamir share held in your host keychain, with no passphrase prompt. The spec requires the share to reach the vault only through a tmpfs-mounted secret;[^8] the shipped guest also keeps a fallback copy of the share on its own disk when no keyring is reachable, and inside a VM guest that file is written on every initialisation.[^126][^127]
- **Survives even `podman system reset`,** on Linux: the model cache, because it is a host bind mount and not a named volume. The spec spells that distinction out, having once cost someone a wrong answer.[^9]
- **Does not survive `--reset-guest`:** it wipes the vault and every enclave container, volume, secret and network, then re-initialises, keeping the model cache. Push first.[^10][^128][^129]

> GREEN: On Linux that boundary is documented per artifact and matches the code.[^9][^129]

> RED: The spec also promises that your host working copy is fast-forwarded after every successful push. No code implements it at this release: the file the spec names does not exist, and the tray-managed host checkout it fed was removed by ruling. After a forge push, your host checkout moves only when you pull.[^130][^143]
> PATH: No path to green is recorded in the repo.

> RED: On macOS the "cache survives" line is not yet proven. The VM at this release already boots with a second shared directory for the model cache, and the guest's first boot mounts it, so the durable path exists.[^131][^132] What remains open: guests provisioned before that change are not migrated, because the mount is written on first boot only; survival across a VM rebuild has not been demonstrated end to end; and the re-download cost was put at about 2.5 GB when filed, with the one later measurement much smaller and the figure recorded as unverified.[^11][^133] The shipped uninstaller now preserves the VM unless asked to wipe.[^134][^135] A partially restored cache is worse than none — the inference service answers a version check and then fails every request.[^11]
> PATH: An open, ready item: prove survival end to end, which needs a re-provision nobody has authorised, and migrate the guests provisioned before the share. The next recorded step, from the daily channel on 2026-09-04, is to re-measure on a warm cache.[^133][^136]

> RED: On Windows, wiping the guest used to leave the old unseal share in Credential Manager, and the tray pushed that dead key into the fresh guest, permanently breaking GitHub login. The wipe paths now clear the stale share; a host that already holds one still delivers it, and the guest cannot tell the host it was rejected.[^12][^137]
> PATH: The reconcile half is blocked: the delivery reply carries no accept-or-reject signal, so a delivered share that fails to authenticate cannot yet lose to the guest's own secret.[^138] Until then, remove the stale credential by hand. A second wipe path that still missed the clearing was found and fixed in the daily channel on 2026-09-02.[^139]

> RED: A host's container engine used to carry a global configuration line routing *all* registry traffic through the enclave proxy unconditionally, so with the stack down `podman build` and `podman pull` died on a raw DNS error that names nothing. Initialising a host now removes that line and hands the proxy setting to each container instead; a host never re-initialised still carries it, and a build that needs the absent proxy still fails without naming it.[^140][^141][^142][^13]
> PATH: The global-config half is done: re-running initialisation converges the file.[^141] The rest is an open, ready item no one has picked up: a build must either not depend on a service that may be absent, or fail with a verdict that names the proxy.[^13]

## Driving it, and where the gate sits

@fig:gate

The verification the earlier levels described is, operationally, a **local** gate: specs declare intent, litmus tests turn each requirement into an executable signal, traces prove the signal ran, and the gate refuses a push that breaks the chain. Two things follow that change how you work.

First, read a green gate with care. Eleven litmus files sit on disk and have never been executed by any suite — grandfathered onto a shrink-only list so that switching the gate on did not flip them all red at once.[^14] The list may shrink; nothing may join it.

Second, the gate on your machine is the only gate there is.

> RED: There is no push CI and no PR CI. Actions runs exactly one workflow, the release, because the signing keys exist only in the cloud. Nothing server-side validates a push; the local gate is the sole trunk protection — made load-bearing after an agent pushed unparseable code and every developer inherited the red build.[^15]
> PATH: Not restoration. This is a deliberate budget trade, carrying a standing obligation to run the local gate before every push and an explicit instruction not to add a workflow to catch what a local gate should have caught.[^15]

## Footnotes

[^1]: Enclave network requirements — `--internal` creation, reuse, cleanup on exit, proxy-only egress, and the symbol-anchored membership list the guard enforces | openspec/specs/enclave-network/spec.md#L17-L69
    > A new enclave member MUST be added to this list in the same commit that attaches it; `scripts/check-enclave-membership-documented.sh` refuses the divergence in both directions.
[^2]: Loopback-only publish, the host-port fallback chain, and the 2026-09 freshness audit that corrected the drifted literals | openspec/specs/subdomain-routing-via-reverse-proxy/spec.md#L2-L42
    > What did NOT change, and what the requirement is actually protecting, is the loopback-only invariant: the publish is `127.0.0.1:{host_port}:8080` in every branch.
[^3]: Stack orchestration script creating the enclave network without `--internal` | scripts/orchestrate-enclave.sh#L76-L90
    > podman network create \ --driver bridge \ --subnet "$ENCLAVE_SUBNET" \ "$ENCLAVE_NET" || {
[^4]: Forge-as-only-runtime: the agent binaries must resolve inside a fresh forge, and the host must not need them | openspec/specs/forge-as-only-runtime/spec.md#L47-L67
    > `command -v claude codex opencode bash` MUST print four valid paths from inside a freshly built forge container.
[^5]: Regression test asserting no user home is mounted into a forge, and the mounts it deliberately allows | crates/tillandsias-headless/src/main.rs#L18844-L18894
    > must not mount a host .config dir into the forge; got source in: {arg}
[^6]: Bare mirror per project in a named volume; forge pushes persist there | openspec/specs/git-mirror-service/spec.md#L18-L38
    > The system SHALL create and maintain a bare mirror repository for each project at `/srv/git/<project>` inside the git service container, backed by the named Podman volume `tillandsias-mirror-<project>`.
[^7]: The ephemerality rule, stated for agents | AGENTS.md#L47
    > **IN A FORGE, A FINDING YOU DID NOT PUSH IS A FINDING YOU DESTROYED.**
[^8]: Auto-unseal from the host native keychain, no passphrase prompt, share on tmpfs only | openspec/specs/tillandsias-vault/spec.md#L76-L95
    > The unseal secret SHALL be loaded into a podman secret and mounted at `/run/secrets/vault-unseal` on tmpfs only.
[^9]: Model cache is a host bind mount, NOT a named volume — and why that decides what `podman system reset` destroys | openspec/specs/inference-container/spec.md#L27-L30
    > Models SHALL be stored in a HOST DIRECTORY (a bind mount, NOT a named Podman volume) at `~/.cache/tillandsias/models/`, mounted into the inference container at `/home/ollama/.ollama/models/`.
[^10]: What `--reset-guest` wipes and what it keeps | crates/tillandsias-headless/src/main.rs#L1377-L1381
    > keeps the model cache) and re-initialize.
[^11]: macOS model cache and engine payload inside the VM disk image; the destroyers, the outage a lost engine caused, and the ~2.47 GB figure as filed (status: ready) | plan/index.yaml#L28798-L28845
    > every VM-directory deletion forces a ~2.47 GB re-download — the macOS twin of 518
[^12]: Windows Credential Manager retains a stale unseal share across a guest wipe; the wipe half landed, the reconcile half still open (status: ready) | plan/index.yaml#L27914-L27960
    > every Windows reset path (--reset-guest, installer -Purge, the e2e smoke) wipes the guest vault but never clears vault-shamir-share-v1 from Credential Manager
[^13]: Global container config hardcodes the enclave proxy, so builds fail on DNS when the stack is down; the open deliverable is a verdict naming the proxy (status: ready) | plan/index.yaml#L38649-L38660
    > ~/.config/containers/containers.conf hardcodes http_proxy=http://proxy:3128 unconditionally, so when the enclave is down EVERY image build fails on DNS — and with it the release gate
[^14]: The ratchet list of litmus files that have never run, and why they are exempt | openspec/litmus-tests/unbound-grandfathered.txt#L1-L25
    > THE ONLY LEGITIMATE EDIT TO THIS FILE IS A DELETION
[^15]: The Actions budget ruling: one workflow, what was removed, and what was given up | methodology/ci.yaml#L286-L324
    > GitHub Actions runs EXACTLY ONE workflow: the release. Nothing else may consume cloud minutes — no push CI, no PR CI, no scheduled jobs, no cache warming, no webhooks. Every other gate runs locally.
[^16]: The startup context's infrastructure section: everything transparent, nothing to configure | images/default/lib-common.sh#L4102-L4131
    > You never need to configure git remotes, tokens, SSH keys, proxy settings, or CA certs.
[^17]: The heavy base layer: Fedora Minimal with the toolchains in one package set | images/default/Containerfile.base#L5-L35
    > rust cargo clippy rustfmt rust-analyzer cargo-deny
[^18]: The thin runtime layer on top of the base | images/default/Containerfile#L1-L6
    > Builds upon the heavy base image to inject configuration,
[^19]: Image identity is a content hash of the sources | openspec/specs/default-image/spec.md#L94-L98
    > The default forge image SHALL use a content-hash canonical tag derived from the image source set.
[^20]: Harnesses refresh at every launch into the persistent per-project tool cache; the first launch must fail loudly | openspec/specs/default-image/spec.md#L185-L193
    > Agent harnesses SHALL be refreshed at container launch into the persistent project tool cache.
[^21]: The tool cache is a podman named volume, not a host bind-mount, so it cannot become a credential-leak path | crates/tillandsias-headless/src/main.rs#L13482-L13493
    > A named volume — not a host bind-mount —
[^22]: The three RAM-backed roots the launcher mounts at this release | crates/tillandsias-headless/src/main.rs#L13682-L13684
    > .tmpfs("/tmp:size=256m,mode=1777")
[^23]: On-demand tools: allowlisted commands become PATH shims that install on first use | images/default/brew-tools-allowlist.txt#L14-L16
    > Commands listed here get a PATH shim in the forge: running the command
[^24]: Where the startup context file is written | images/default/lib-common.sh#L3828
    > local ctx_file="$project_dir/.forge-startup-context.md"
[^25]: The hot/cold spec: exactly four RAM-backed roots, the source tree among them | openspec/specs/forge-hot-cold-split/spec.md#L10-L23
    > Only these four path roots are HOT. "Maybe a hot path" is a HARD NO.
[^26]: The mount-topology packet: source tmpfs, host RAM gate and memory ceiling still to wire (status: ready) | plan/index.yaml#L7967-L7991
    > production launch runs check_host_ram, derives compute_memory_ceiling_mb, and emits equal --memory and --memory-swap limits
[^27]: The Homebrew prefix is ephemeral; every launch re-installs on-demand tools (status: ready) | plan/index.yaml#L12173-L12177
    > The brew prefix is ephemeral, so every forge launch re-installs and re-attests every tool — that is the rate-limit multiplier
[^28]: The startup context's claim of a Sigstore attestation per bottle | images/default/lib-common.sh#L4202-L4207
    > it verifies a Sigstore attestation per bottle
[^29]: What the shim verifies today: integrity from one publisher, attestation off | images/default/brew-shim-exec.sh#L12-L21
    > Sigstore verification is OFF because it requires a GitHub credential to FETCH
[^30]: The source tmpfs, sized from the mirror pack — the fourth hot root, landed in the daily channel | crates/tillandsias-headless/src/main.rs#L14195-L14222 @v56.9.5.1
    > Three of the four shipped; this one did not
[^31]: The launcher creates the enclave network with `--internal` on first launch, after ensuring the egress network | crates/tillandsias-headless/src/main.rs#L2809-L2840
    > command.args([ "network", "create", "--internal",
[^32]: The membership guard: every attach site's enclosing function must be in the spec and vice versa; it counts only builder and launcher functions | scripts/check-enclave-membership-documented.sh#L21-L75
    > if (fname ~ /^(build|launch)_/) { print fname }
[^33]: The only network removal in the launcher: the destructive reset | crates/tillandsias-headless/src/main.rs#L8360-L8370
    > command.args(["network", "rm", "-f", &name]);
[^34]: Proxy variables injected into every enclave container from one source | crates/tillandsias-headless/src/main.rs#L1646-L1667
    > "http_proxy=http://proxy:3128".into(),
[^35]: The forge composes vendor roots plus the proxy CA into the system-default bundle before any network client starts | images/default/lib-common.sh#L11-L22
    > Compose the per-install CA into that target atomically, before any network
[^36]: No per-client CA variables; trust flows through the distribution's standard path | openspec/specs/transparent-https-caching/spec.md#L54-L59
    > launchers and entrypoints SHALL NOT select CA files with `GIT_SSL_CAINFO`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, or `NODE_EXTRA_CA_CERTS`.
[^37]: A regression test pins the CA mount and the absence of CA overrides | crates/tillandsias-headless/src/main.rs#L18988-L18998
    > typed forge launcher must mount the single runtime CA input
[^38]: Package-manager workflows must work with no configuration | openspec/specs/proxy-container/spec.md#L151
    > common development workflows (npm install, cargo build, pip install, flutter pub get) work out of the box without configuration.
[^39]: Proxy purpose: allowlisted caching forward proxy, bump only the release-asset CDN, splice all other TLS | openspec/specs/proxy-container/spec.md#L8-L14
    > HTTPS interception is deliberately exceptional: the proxy bumps only the exact GitHub release-asset CDN hostname and splices all other TLS traffic end to end.
[^40]: The three ssl_bump rules: peek once, bump one exact host, splice everything else | images/proxy/squid.conf#L120-L124
    > ssl_bump peek ssl_bump_step1 ssl_bump bump github_release_assets ssl_bump splice all
[^41]: Spliced HTTPS is never cached by the proxy | openspec/specs/proxy-container/spec.md#L43-L48
    > the HTTPS response SHALL NOT be cached (tunneled traffic is opaque to squid)
[^42]: cargo, npm and pip caches redirected into the per-project cache | images/default/lib-common.sh#L1732
    > export CARGO_HOME="$PROJECT_CACHE/cargo"
[^43]: Blocked hosts get a TCP reset, not a 403 | images/proxy/squid.conf#L136-L141
    > deny_info TCP_RESET strict_deny_acl
[^44]: The live miss-then-hit trace for the bumped host was never recorded, and the next action that would record it (status: ready) | plan/index.yaml#L7183-L7226
    > no rebuilt-image parser result or real identical-key MISS-to-HIT trace is claimed
[^45]: The consumer contract: one endpoint at inference:11434, downloads through the proxy | openspec/specs/inference-container/spec.md#L12-L13
    > Forge containers SHALL access it via `OLLAMA_HOST=http://inference:11434`. The inference container SHALL use the proxy for model downloads.
[^46]: Inference readiness is best-effort, never a launch gate | crates/tillandsias-headless/src/main.rs#L13149-L13156
    > Local inference readiness (order 392) is BEST-EFFORT, not a launch
[^47]: The single default chat model pulled on first run | images/inference/entrypoint.sh#L120
    > DEFAULT_MODELS="${TILLANDSIAS_DEFAULT_MODELS:-qwen2.5:0.5b}"
[^48]: The engine self-installs from an unpinned latest release | images/inference/entrypoint.sh#L293
    > OLLAMA_URL="https://github.com/ollama/ollama/releases/latest/download/ollama-linux-${OLLAMA_ARCH}.tar.zst"
[^49]: The closed-vocabulary accelerator line every forge receives | crates/tillandsias-headless/src/accel_probe.rs#L1820-L1823
    > accel_class=<workstation-gpu|mobile-npu|hybrid-gpu-npu|cpu-only>
[^50]: Ready means the endpoint answers and at least one model is cached; there is no "starting up" | images/default/lib-inference-state.sh#L14-L24
    > Reason vocabulary (CLOSED SET — there is deliberately no "starting up"):
[^51]: Larger tier models are opt-in, not default | images/inference/entrypoint.sh#L654-L657
    > tier pulls opt-in (set TILLANDSIAS_INFERENCE_TIER_PULLS=1) — skipping runtime tier pulls
[^52]: The CPU floor is unconditional by spec | openspec/specs/inference-container/spec.md#L141-L146
    > Tier-S SHALL be available on every host regardless of GPU, NPU, driver, or engine availability, and SHALL NOT be gated on any device probe.
[^53]: The engine payload is fetched with no integrity check (status: ready) | plan/index.yaml#L10233-L10240
    > The inference engine payload is downloaded and executed with NO integrity verification
[^54]: NVIDIA delivery is gated on a CDI spec; without one the host degrades to CPU with a loud remedy | crates/tillandsias-headless/src/main.rs#L4655-L4672
    > a GPU host without CDI degrades to CPU with a LOUD remedy
[^55]: The AMD lane is selected only when ROCm reports a graphics agent | crates/tillandsias-headless/src/main.rs#L4190-L4196
    > let rocm = std::process::Command::new("rocminfo")
[^56]: The spec: NPU rows are never attempted on the shipped engine | openspec/specs/inference-container/spec.md#L172-L179
    > N rows SHALL NOT be attempted on the `ollama` engine kind. Ollama cannot use any NPU
[^57]: On Windows the NPU cannot be seen from inside the guest at all | scripts/windows-host-capability-probe.sh#L12-L14
    > The NPU is not merely undetected in the guest, it is STRUCTURALLY invisible:
[^58]: The health check tests that the runner binary exists; the real load check runs once at startup | images/inference/Containerfile#L112-L121
    > A real generate would be the strongest assertion but is far too expensive at a
[^59]: NPU passthrough for the container is an open packet (status: ready) | plan/index.yaml#L8973-L8980
    > Impl: NPU /dev/accel passthrough plumbing for the inference container (AMD XDNA2 first lane)
[^60]: The host-native sidecar for Metal and the NPUs is an open packet (status: ready) | plan/index.yaml#L9129-L9134
    > Impl: host-native inference sidecar registry (macOS Metal/MLX, AMD XDNA2 flm/Lemonade, Intel NPU OpenVINO) behind the enclave proxy
[^61]: Agents configure nothing and still see the original GitHub URL | openspec/specs/git-mirror-service/spec.md#L457-L463
    > `git push`, `git fetch`, and `git clone` SHALL work with zero agent-side configuration
[^62]: One atomic push of explicit refspecs | images/git/relay-refs.sh#L266
    > git push --atomic "$PUSH_URL" "$@"
[^63]: The mirror acknowledges only after upstream durably accepts the ref transaction | images/git/pre-receive-hook.sh#L487
    > Push rejected: configured upstream did not durably accept the ref transaction
[^64]: The GitHub token is read from Vault at push time inside the git service and never crosses into a forge | openspec/specs/git-mirror-service/spec.md#L14-L16
    > The git service reads the GitHub token from Vault at push time via Vault CLI; the token never crosses into a forge container.
[^65]: The credential helper fetches the token from Vault over git's credential protocol | images/git/git-credential-tillandsias.sh#L47
    > TOKEN="$(vault-cli read -field=token secret/github/token 2>/dev/null || true)"
[^66]: Every start re-applies receive hardening: no deletes, no rewinds, object checks | openspec/specs/git-mirror-service/spec.md#L95-L103
    > the git service SHALL set `receive.denyNonFastForwards=true`, `receive.denyDeletes=true`, and `receive.fsckObjects=true`.
[^67]: A project with no upstream keeps pushes durably in the local-only mirror | images/git/relay-refs.sh#L157
    > No upstream configured; accepting as a durable local-only mirror update
[^68]: Without a stored token the relay refuses and names the remedy | images/git/relay-refs.sh#L193
    > HTTPS upstream credential is unavailable; run GitHub Login before pushing
[^70]: The authenticated SSH push lane is dark behind one flag until the default flip | crates/tillandsias-headless/src/main.rs#L9708-L9714
    > std::env::var("TILLANDSIAS_MIRROR_SSHD")
[^71]: Offline or credential-less, the forge's push returns non-zero and nothing is partially applied | openspec/specs/git-mirror-service/spec.md#L220-L226
    > the forge's `git push` SHALL return non-zero
[^72]: The SSH-lane default flip is an open packet (status: ready) | plan/index.yaml#L20790-L20797
    > T11+T12 — flip one lane behind a flag once the §4a matrix is green
[^74]: Vault is the default and only Linux secrets backend; GitHub token and short-lived per-container tokens | openspec/specs/tillandsias-vault/spec.md#L11-L14
    > Run a HashiCorp Vault container as the default and ONLY Linux secrets backend for Tillandsias.
[^75]: The shipped Vault listener is TLS-only | images/vault/vault.hcl#L16-L24
    > tls_cert_file   = "/run/secrets/tillandsias-vault-tls-cert"
[^76]: Every OAuth-credentialed agent lane mounts one scoped Vault token | crates/tillandsias-headless/src/main.rs#L13719-L13727
    > Every OAuth-credentialed agent lane mounts a scoped Vault token so its
[^77]: Forge containers get no broad Vault token, only a provider-scoped short-lived one | openspec/specs/tillandsias-vault/spec.md#L311-L316
    > Forge containers SHALL NOT receive a broad Vault token.
[^78]: The generic forge policy cannot read the GitHub token | images/vault/policies/forge.hcl#L1-L8
    > Explicitly NO github or token access — forge containers must remain
[^79]: The tray policy reads the whole secret tree | images/vault/policies/tray.hcl#L1-L6
    > path "secret/*" {
[^80]: The startup context advertises http for a TLS-only Vault | images/default/lib-common.sh#L4129
    > http://vault:8200
[^81]: The in-image helper defaults to https and the tmpfs token path | images/default/vault-cli.sh#L23-L24
    > VAULT_ADDR="${VAULT_ADDR:-https://vault:8200}"
[^82]: Client tokens default to a one-hour TTL | openspec/specs/tillandsias-vault/spec.md#L216-L220
    > Every client token, including tokens minted by Vault Agent, SHALL default to TTL 1h with a maximum TTL of 24h.
[^83]: Four MCP servers registered for Claude Code inside the forge image | images/default/config-overlay/claude/mcp.json#L2-L23
    > "command": "/home/forge/.config-overlay/mcp/forge-plan.sh"
[^84]: The same four servers registered for OpenCode | images/default/config-overlay/opencode/config.json#L66-L87
    > "command": ["/home/forge/.config-overlay/mcp/forge-plan.sh"],
[^85]: Spec: the generic project expert bootstraps for any project with no registration or configuration | openspec/specs/forge-environment-discoverability/spec.md#L162-L164
    > The forge MUST bootstrap a project expert surface for an ARBITRARY mounted project without manual registration, configuration, or repository-type knowledge from the caller.
[^86]: The plan expert's refusal rule: zero citations means unsupported | images/default/config-overlay/mcp/forge-plan.sh#L1171
    > An answer with zero citations is returned as confidence=unsupported — the expert refuses rather than guesses.
[^87]: The plan expert is degraded by design on a project without the plan crate | images/default/lib-common.sh#L4120
    > (this project has no plan expert — expected off-tillandsias)
[^88]: Discovery, expert build and the grounded endpoint all backgrounded and fail-soft after the clone | images/default/lib-common.sh#L1287-L1293
    > ensure_forge_experts >>/tmp/forge-lifecycle.log 2>&1 || true
[^89]: The on-demand spec obliges the tray to detect and spawn servers | openspec/specs/mcp-on-demand/spec.md#L31-L36
    > the tray MUST detect that the filesystem MCP server is not running
[^90]: The startup context every lane reads names Local Experts mode | images/default/lib-common.sh#L4139
    > Local Experts mode (the
[^91]: Only the OpenCode configuration carries an agent bound to the grounded endpoint | images/default/config-overlay/opencode/config.json#L18-L30
    > "model": "tillandsias-experts/all",
[^92]: The pre-expert-binary trap: criterion 2 closed, the fresh-forge criterion still open (status: ready) | plan/index.yaml#L6446-L6523
    > criterion 1 (release/branch decision) still OPEN — packet intentionally stays `ready` (partial reduction)
[^93]: The catalog is an allowlist: WEB only, refused host-side otherwise | openspec/specs/enclave-service-catalog/spec.md#L21-L25
    > Requests outside the catalog are refused host-side; the guest cannot mint categories.
[^94]: The web image: busybox httpd on 8080, document root /var/www | openspec/specs/web-image/spec.md#L22-L23
    > The image MUST serve static files from `/var/www` on port 8080 using busybox httpd with no additional packages or configuration.
[^95]: One socket per lane, bind-mounted into the forge; attribution comes from the listener | openspec/specs/mcp-tool-socket/spec.md#L29-L35
    > The tray SHALL create one socket per lane at
[^96]: The live publish path: worktree mounted read-only, a www route made public, an http URL on the router's host port | crates/tillandsias-headless/src/main.rs#L15964-L16052
    > "http://www.{project_name}.localhost:{router_host_port}"
[^97]: From inside the forge, .localhost requests are forwarded by the proxy to the router | images/proxy/squid.conf#L170-L175
    > cache_peer_access tillandsias-router allow localhost_subdomain
[^98]: Serving the repository root: the document-root rung (status: ready), and what a consumer found reachable | plan/index.yaml#L46860-L46907
    > /.git/config returned 200 through the router (full history + remote URLs reconstructible)
[^99]: The stack sweep's name patterns: a published sibling matches none of them | crates/tillandsias-headless/src/main.rs#L6000-L6013
    > name.starts_with("tillandsias-git-")
[^100]: Projects must live under ~/src on the host; discovery hardcodes it (status: ready) | plan/index.yaml#L43551-L43564
    > tray discover_projects hardcodes ~/src and run_opencode_mode starts no lane listener
[^101]: The declarative image set initialisation builds: both Chromium images and the web image among them | crates/tillandsias-headless/src/main.rs#L7410-L7421
    > "forge-base", "forge", "web",
[^102]: An ordinary forge launch ensures four images, not the web or browser ones | crates/tillandsias-headless/src/main.rs#L13076-L13083
    > let images = ["router", "git", "inference", "forge"];
[^103]: The phantom pull the status-check path was fixed for | crates/tillandsias-headless/src/main.rs#L8480-L8492
    > phantom registry pull (125) on any version handover.
[^104]: The end-to-end publish litmus has never been run by any suite | openspec/litmus-tests/unbound-grandfathered.txt#L21
    > litmus:publish-local-e2e
[^105]: The headless core image and its entrypoint | images/chromium/Containerfile.core#L36-L37
    > ENTRYPOINT ["/usr/lib64/chromium-browser/headless_shell", "--headless=new"]
[^106]: The framework image extends the core with GUI Chromium, Node and Playwright | images/chromium/Containerfile.framework#L15-L35
    > RUN npm install -g --prefix=/usr \ playwright \
[^107]: The hardened, ephemeral browser container the runtime launches | crates/tillandsias-headless/src/main.rs#L12096-L12101
    > Hardened browser boundary: read-only rootfs, CAP_DROP=ALL, no-new-privileges,
[^108]: Browser launch requires a graphical session | crates/tillandsias-headless/src/main.rs#L12053-L12057
    > OpenCode Web browser launch requires a graphical session (DISPLAY or WAYLAND_DISPLAY)
[^109]: The browser tool spawns a host Chromium from the cache directory, not a container | crates/tillandsias-browser-mcp/src/launcher.rs#L78-L82
    > root.join("current/chrome"),
[^110]: A missing bundled Chromium returns BROWSER_UNAVAILABLE | crates/tillandsias-browser-mcp/src/server.rs#L431-L435
    > BROWSER_UNAVAILABLE: bundled chromium not yet downloaded
[^111]: The only Chromium installer has no consumer | scripts/install-chromium.sh#L10-L16
    > INTEGRATION STATUS (2026-08-16 freshness audit, 774-cfw8): NO consumer
[^112]: The wire-it-or-tombstone packet for the orphaned installer (status: ready) | plan/index.yaml#L22450-L22457
    > scripts/install-chromium.sh has ZERO consumers while its header claimed two integrations; a litmus pins a shape nothing ships — wire it or tombstone it
[^113]: The three-label allowlist a dotted project name cannot satisfy | crates/tillandsias-browser-mcp/src/allowlist.rs#L234-L237
    > if labels.len() != 3 || labels[2] != "localhost" {
[^114]: Safe variant: proxy-only egress is the spec | openspec/specs/chromium-safe-variant/spec.md#L16-L19
    > Full network isolation inside the enclave, with allowlist enforcement via the proxy only; no host-gateway internet fallback
[^115]: Safe variant: the script launcher defaults to host networking | scripts/launch-chromium.sh#L90
    > "--network=${TILLANDSIAS_BROWSER_NETWORK:-host}"
[^116]: The router's host-port candidates: an explicit --port first, then 80 and the fallbacks | crates/tillandsias-headless/src/main.rs#L5469-L5477
    > let mut candidates = vec![80, 8080, 18080, 28080, 38080, 48080, 58080];
[^117]: Stack orchestration script now passes `--internal` and refuses to reuse an unisolated network | scripts/orchestrate-enclave.sh#L82-L126 @v56.9.5.1
    > Network $ENCLAVE_NET EXISTS BUT IS NOT INTERNAL — it was created without --internal, so every member has NAT egress and the proxy is not the only way out (order 972-a8vh, spec:enclave-network).
[^118]: The new gate check, and the fixed list of files it reads | scripts/check-enclave-network-internal.sh#L1-L115 @v56.9.5.1
    > sh_launcher="$ROOT/scripts/orchestrate-enclave.sh"
[^119]: The fix recorded complete on 2026-09-03, with isolation measured from inside a member container | plan/index.yaml#L51875-L51920 @v56.9.5.1
    > Both exit criteria met; fixed in de9560fb5.
[^120]: A per-project runner still creates the network without the flag | scripts/run-forge-project.sh#L116-L119 @v56.9.5.1
    > "$PODMAN_CTL" network create --driver bridge --subnet "$ENCLAVE_SUBNET" "$ENCLAVE_NET" >/dev/null
[^121]: The proxy diagnostic still creates the network without the flag | scripts/diagnose-proxy.sh#L89-L93 @v56.9.5.1
    > podman network create --driver bridge --subnet "10.0.42.0/24" "$ENCLAVE_NET"
[^122]: A missing forge image makes the launcher refuse, never fall back to a host binary | openspec/specs/forge-as-only-runtime/spec.md#L105-L106
    > The tray MUST refuse to launch an agent if the forge image is missing — it MUST NOT silently fall back to a host binary.
[^123]: Clone-only by default: the host checkout is the opt-in path | crates/tillandsias-headless/src/main.rs#L13614-L13617
    > Order 437: clone-only by default.
[^124]: Forge containers clone from the mirror and push through it | openspec/specs/git-mirror-service/spec.md#L52-L59
    > Forge containers SHALL clone from `git://git-service/<project>`
[^125]: The reduced-isolation warning the host-mount escape hatch prints | crates/tillandsias-headless/src/main.rs#L5762-L5770
    > WARNING: WORKSPACE ENCLAVE ISOLATION IS REDUCED
[^126]: Inside a VM guest the share is written to a fallback file on every initialisation | crates/tillandsias-headless/src/vault_bootstrap.rs#L1269-L1316
    > Inside the VM there is no OS keychain, so these files are the only durable
[^127]: Where no OS keyring is reachable the share falls back to a file in the cache directory | crates/tillandsias-headless/src/vault_bootstrap.rs#L2903-L2919
    > using fallback file (expected in VM guest and headless environments)
[^128]: What the reset wipes on the host side: only the vault data directory | crates/tillandsias-headless/src/main.rs#L8268-L8270
    > vec![cache_dir.join("vault-data")]
[^129]: The pin test: the model cache must never be in the reset wipe set | crates/tillandsias-headless/src/main.rs#L25121-L25129
    > the inference model cache must never be in the reset wipe set
[^130]: The host working-copy fast-forward is specified, and specified against a file that does not exist | openspec/specs/git-mirror-service/spec.md#L335-L354
    > The tray SHALL trigger a fast-forward attempt on the host working copy at `<watch_path>/<project>` for every successful push to the enclave bare mirror
[^131]: The VM boots with a second shared directory for the model cache | crates/tillandsias-vm-layer/src/vz.rs#L1810-L1828
    > tag: "model-cache".to_string(),
[^132]: The guest's first boot persists the model-cache mount | crates/tillandsias-vm-layer/src/vz.rs#L709-L715
    > model-cache /root/.cache/tillandsias/models virtiofs nofail 0 0
[^133]: The enabling change landed and the packet stayed ready: migration and end-to-end survival unverified | plan/index.yaml#L28881-L28941
    > guest wiring verified by source scan, MIGRATION UNVERIFIED.
[^134]: The shipped uninstaller preserves the VM unless asked to wipe | scripts/uninstall.sh#L121-L126
    > Preserving the VM image in $DATA_DIR (use --wipe to remove it).
[^135]: The uninstaller defect the macOS packet waited on, closed | plan/archive/packets-2026-08.yaml#L23430-L23436
    > shipped uninstall.sh deletes the 11.83 GiB VM directory with no --wipe, no root and no prompt
[^136]: The later cold measurement, and the figure recorded as unverified | plan/index.yaml#L29724-L29728 @v56.9.5.1
    > macneo measured the cold case at 514 MB transferred and 64 s / 357 s wall clock on a never-populated image, so the ~2.47 GB title figure is unverified in magnitude.
[^137]: The wipe half landed; a host already holding a stale share is unaffected | plan/index.yaml#L27914-L27916
    > a host that ALREADY holds a stale credential is unaffected
[^138]: The delivery reply carries no accept-or-reject signal (status: ready) | plan/index.yaml#L38968-L38975
    > DeliverCredentials reply says "I received it", never "I accepted it"
[^139]: A second wipe path found and fixed in the daily channel | plan/index.yaml#L28882-L28891 @v56.9.5.1
    > found Part A missing on the SECOND purge path (build-and-install-windows-local.ps1); unifying and gating it
[^140]: Initialisation removes the orphaned global proxy block | crates/tillandsias-headless/src/main.rs#L7270-L7273
    > Remove the orphaned `[engine] env` proxy block.
[^141]: What initialisation prints when it converges the file | crates/tillandsias-headless/src/main.rs#L7378-L7389
    > removed the orphaned [engine] env proxy block from {} (923-rmtw); containers receive proxy env per-container
[^142]: The global-config fix, archived as completed | plan/archive/packets-2026-08.yaml#L46813-L46818
    > containers-conf-env-line-is-orphaned-and-never-converges
[^143]: The operator directive that removed the tray-managed host checkout | plan/index.yaml#L16322
    > It is REMOVED ENTIRELY.
