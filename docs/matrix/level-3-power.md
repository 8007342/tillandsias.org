# Tillandsias, for a power user

## What you get the moment a forge opens

`tillandsias --headless /path/to/project --claude` starts a container with your project in it and an agent at the prompt. Nothing below is configured by you or by the agent: the context file the agent reads first lists the plumbing under the heading "all transparent — zero configuration needed".[^16] Every claim here is checked against the stable release, v56.10.9.1.

### The forge container

A forge is a Fedora Minimal image in two layers: a heavy base carrying the toolchains — gcc, make, cmake, Rust with cargo and rust-analyzer, Go, Node, Java, Python, the debuggers — and a thin runtime layer with the entrypoints, cheatsheets and the agent's configuration.[^17][^18] The tag is a content hash of its sources, so an unchanged rebuild is a no-op.[^19] The coding agents are not baked in: every launch refreshes them into a per-project cache volume that outlives the container, rolling back to the last known-good version when upstream ships a broken one.[^20][^21] Cheatsheets, `/tmp` and the runtime directory sit on RAM-backed tmpfs with hard caps.[^22] The default clone-only lane now puts the source tree in RAM too — a tmpfs-backed volume the launcher creates for the lane, sized from the mirror’s pack; the opt-in host-mounted checkout keeps its host mount.[^30][^149] Allowlisted commands — tmux and lazygit among them — are shims that install userspace Homebrew on first use.[^23] On start the forge writes a context file into the checkout naming what is present, what is absent, and what needs no configuring.[^24]

> GREEN: Works out of the box. The tool cache is a named volume, never a host path, so first-run installs survive the container's removal without opening a host-home surface.[^21]

> RED: The storage spec names four RAM-backed roots and a host RAM gate with a matching container memory ceiling; the default lane now mounts all four roots, but the host RAM gate and the matching container memory ceiling remain library code nothing calls.[^25][^26] The Homebrew prefix is backed by no volume, so every on-demand tool is re-installed at every launch and its bootstrap needs live egress each time.[^27] And the context file tells the agent each such install verifies a signed attestation per bottle; the shim states that attestation is off, because fetching it would need a GitHub credential no forge may hold — what remains is integrity from one publisher.[^28][^29]
> PATH: The source tmpfs landed on 2026-09-04 and is now in stable.[^30][^144] The RAM gate and ceiling stay an open, ready item whose remaining slice is named: run the host RAM check before launch and emit equal memory limits.[^26] The recorded remedy for the prefix asks for a decision between persisting it and baking the tools into the image.[^27] For the context file's wording there is a recorded remedy too: fetch and pin the attestation bundles when the image is built, so a lane can verify one with no GitHub credential present at all.[^145]

### The HTTPS proxy and its cache

Every container is born with its proxy variables set and the proxy's certificate composed into the system trust bundle before any network client starts; no per-client CA variable is set, and a regression test refuses a launcher that tries.[^34][^35][^36][^37] The allowlist of developer hosts — registries, GitHub, cloud SDKs, model providers — is generous enough that npm, cargo, pip and flutter work unconfigured.[^38] It decrypts exactly one of them, GitHub's release-asset CDN, so a large asset is fetched once for the whole machine.[^39][^40] Everything else passes through encrypted, so the proxy never sees, and never caches, crates.io, npm, PyPI or api.github.com.[^41] What makes the second `cargo build` fast is not the proxy but a per-project cache volume for cargo, npm, pip and go that outlives the forge.[^42] A blocked host gets no 403: the connection is reset, and only the proxy log names the domain.[^43]

> GREEN: The trust wiring is pinned by a test: the forge launcher mounts the single runtime CA input read-only and sets none of the per-client CA variables.[^37]

> RED: The cache-hit claim for the one decrypted host has never been shown live. The fix for a rule order that made decryption unreachable shipped the config and static tests, and records that no real miss-then-hit trace was obtained.[^44]
> PATH: The next step is written down: on a Podman host, request one release-asset URL twice through the strict proxy and record a miss followed by a hit with equal checksums.[^44]

### Local inference

The launcher prepares a shared model server at `http://inference:11434`, started on launch if it is not already running and shared across projects.[^45][^46][^146] The first run pulls the engine and one small tool-capable chat model into a host directory that outlives the containers.[^47][^48][^9] Readiness is best-effort: a failed readiness wait warns and the forge launches anyway; errors while preparing the service can still fail launch.[^46] The context file tells the agent, in a closed vocabulary, what the host's accelerators are and whether the endpoint is ready — ready means at least one model is cached, never "starting up".[^49][^50] Larger tiers are opt-in behind an environment variable; the CPU floor is unconditional by spec.[^51][^52]

> GREEN: A failed model-readiness wait is non-fatal, so it does not hold up the agent session.[^46] The CPU floor is the required fallback, rather than evidence that every fresh host has successfully loaded a model.[^52]

> GREEN: The first-run engine download now pins an Ollama release and checks an architecture-specific SHA-256 before execution; a missing checksum tool or mismatched digest stops it.[^48][^53]

> RED: Two limits remain. GPUs reach the container only with a vendor stack — NVIDIA with a CDI spec, AMD when ROCm reports the card — and NPUs are named on every platform and used on none: no device argument for one exists in the launcher, and the spec itself says the engine cannot use them.[^54][^55][^56][^57] The container's health check tests that the runner binary exists, not that a model loads.[^58]
> PATH: NPUs have two open, ready items — device passthrough for the container, and a host-native sidecar for Metal and the NPUs a Linux guest cannot see.[^59][^60]
> PATH: For the health check: No path to green is recorded in the repo. The entrypoint runs the real load check once at startup.[^58]

### The git mirror and push relay

For an agent, a refinement is a controlled data path: it receives selected source,
rules, task context and tool results; it proposes a patch; local checks and review
decide whether that patch becomes a commit. Git retains reachable commits, while the
current tree is a snapshot that may replace or delete files. Calling the repository a
"set of vectors" is therefore a useful description of the model's selected context,
not Git's storage format and not a guarantee that every current file survives.[^61][^62][^66]

Several tasks can run this loop at once. Each needs its own declared target and
measurement; the shared repository is the coordination point, not evidence that
their measurements are already comparable. The relay makes an accepted push atomic,[^62][^63]
which preserves the record of what was accepted, not the truth of the patch.

**Why this is built rather than borrowed.** The mirror has to satisfy two
requirements at the same time. The credential for the upstream must stay on the
server side, so a workspace can publish its own work without ever holding a token
that could publish anything else — the git service reads that token when it pushes
and it never crosses into a workspace container.[^152] And the push must be
*synchronously durable*: the hook relays the proposed ref transaction upstream
before accepting it locally, so a client's success means the upstream has durably
accepted the same atomic ref set.[^153] The live relay performs that as a single
atomic push.[^154]

Tools in general offer one of those or the other. A managed push mirror holds the
credential for you and copies asynchronously, reporting success before the copy
lands — which is precisely the false success that strands an agent's work. A
caching or redirecting git proxy relays synchronously but forwards the client's
credentials, which is the isolation being bought in the first place. Needing both
at once is the unusual requirement, and it is what the pre-receive relay exists to
provide.

> NOTE: The pairing is the argument, not novelty. The pattern of relaying a push
> onward from a hook is documented elsewhere; what is specific here is refusing to
> report success before the upstream has it, while the credential stays outside the
> workspace.

> PLAUSIBLE: That no off-the-shelf component satisfies both requirements together.
> The comparison is recorded in the repository as a survey rather than as a
> benchmark, and a reader should treat it as the reason a decision was taken, not
> as a proof that no such tool exists.

Rolling the decision back is deliberately cheap: the relay is a bare repository
plus a pre-receive hook, so undoing it means pointing the daemon back at the bare
repository.

Git needs nothing from you inside a forge. A read-only global gitconfig redirects the project's GitHub URL to a bare mirror in its own named volume, so `git remote -v` still says github.com while clone, fetch and push hit the enclave.[^61][^6] A push is not acknowledged until the mirror's hook has relayed exactly those refs upstream with one atomic push.[^62][^63] The token authorising that relay is read from the vault inside the git service at push time and never enters the forge.[^64][^65] Deletions and branch rewinds land nowhere;[^66] a project with no upstream keeps its pushes in the mirror.[^67]

> GREEN: Works out of the box once GitHub Login has run on the host; without a stored token the relay refuses the push and says so.[^68]

> RED: The push path inside the enclave is anonymous: any peer that can reach the mirror may create branches or fast-forward them and have the privileged relay carry those updates upstream. Being on an internal-only network is placement, not client authentication.[^69] The authenticated SSH lane that would replace it is built but dark behind an environment variable that defaults to off.[^70] Offline, a push simply fails — nothing is queued.[^71]
> PATH: Flipping the SSH lane on by default is an open, ready item, pending the transport decision behind it.[^72] For the offline push: No path to green is recorded in the repo.

### The vault

Secrets live in a Vault container at `vault:8200`, reached over TLS with the enclave certificate already trusted.[^74][^75] A lane with a credentialed provider is handed a single-purpose token on tmpfs at `/run/secrets/vault-token` whose policy reaches only that provider's paths; the generic forge policy cannot read the GitHub token, which the git mirror, the tray and the login flow can.[^76][^77][^78][^79] Across a stop, Vault unseals itself from one Shamir share held in your host keychain, with no passphrase prompt.[^8]

> GREEN: The token is injected at container start with nothing for the agent to do,[^76] and a test pins that every credentialed lane mounts its scoped lease while a credential-free lane mounts none.[^147]

> RED: The context file tells the agent the vault is at `http://vault:8200`. The shipped listener is TLS-only, so that address answers an HTTP error; only the in-image helper carries the right default.[^80][^75][^81] The token defaults to a one-hour life and nothing in the lane renews it.[^82]
> PATH: No path to green is recorded in the repo.

### The experts and the project index

The agent finds four tool servers already registered, for Claude Code and OpenCode alike: git tools, a project index, the host-browser bridge, and a plan expert.[^83][^84] The index answers project type, status, commands and layout for any checkout, citing what it indexed; the plan expert returns cited answers or a typed refusal, never a guess, and answers only on a checkout carrying Tillandsias' own plan crate — elsewhere it reports itself degraded, by design.[^85][^86][^87] Both start in the background after the clone and never gate the session.[^88] The status now distinguishes the running expert’s capabilities from what a relaunch would build: waiting for a build, needing a relaunch, and losing capabilities on relaunch have different machine-readable verdicts.[^150] A ready index is separate from a usable answer engine. Deterministic project questions can work without local inference; synthesis still returns a typed refusal when the synthesis capability is absent, even if inference itself is ready.[^151] The "on-demand" spec describes tray-side spawning and health checks that do not exist; the harness launches each server itself.[^89]

> GREEN: Works out of the box on any project, with no registration step.[^85]

> RED: The context file tells the Claude lane about a conversational Local Experts mode, but only the OpenCode configuration carries an agent that reaches the grounded endpoint behind it.[^90][^91] And the pre-expert-binary trap is half closed: a forge seeded from a checkout without the expert sources now reports itself degraded instead of ready, but the fresh-forge criterion — an in-forge probe grading full marks with no manual step — is recorded open.[^92]
> PATH: No path to green is recorded in the repo for the Claude-lane mismatch. The trap's entry stays open on purpose until the release-branch decision it waits on is made.[^92]

### Sibling web containers

Ask the agent to publish the project and it does not start a server in the forge. It asks the host, over a socket that exists only for that lane, to launch a sibling web container beside it: read-only, capability-dropped, joined to the enclave network and given a router route.[^93][^94][^95] The sibling sees the running forge's own worktree, resolved from the lane's live container and its RAM-backed source volume rather than from a path on the host, and it is given a selected public document tree rather than the repository: `var/html`, `public` or `dist` if one exists, otherwise the root `index.html` and the plainly static files and asset directories beside it; a Wrangler configuration at the project root selects a second, Wrangler-based runtime instead.[^160] The URL comes back as `https://www.<project>.localhost:<port>`, on a loopback TLS port the router listens on, with a leaf certificate issued for that name.[^96] The project is attributed from the socket the request arrived on, never from the request.[^95] From inside the forge the proxy forwards `.localhost` requests to the router;[^97] this page has not traced the HTTPS preview port through that rule.

> GREEN: Two defects of the earlier publish path are closed in the code. The sibling no longer serves the repository root: the source says it never mounts `.git`, `.env` or the forge root into a sibling, so the `.git` exposure through the router that a consumer found on the earlier path has no mount left to reach.[^160][^98] The earlier requirement that the project live under `~/src` on the host no longer applies to publishing, which reads the running forge; the plan item filed against that hardcoded path is a separate matter.[^100] And the sibling is no longer orphaned when its forge dies: a watcher stops it and removes its route once the forge that published it is gone, and the next launch of the same lane clears a departed one; the stack-wide sweep still names no pattern that matches the sibling, so this cleanup is the preview's own.[^161][^99] Both are read in code, not demonstrated live.

> RED: The feature's own spec still calls itself a draft whose verification is design-only, with executable coverage and live evidence pending.[^162] The only end-to-end test of publishing is still on the list of tests that no suite has ever run.[^104] Only `www` is routed, not the apex.[^96] The static web image is built by initialisation rather than by a forge launch, which ensures only four images;[^101][^102] a host that never initialised now gets an explicit error telling it to initialise the managed runtime image, where the earlier path hit a phantom registry pull that was fixed only for the status-check path.[^164][^103] The Wrangler runtime needs a second image that the list of images initialisation builds does not contain, so it stops with the same error.[^101][^164]
> PATH: The plan records an open item to prove the preview live and then activate its specs.[^163]
> PATH: For the apex route and the Wrangler image: No path to green is recorded in the repo.

### Chromium

Two browser images are built at initialisation: a minimal headless core, and a framework layer on top of it with GUI Chromium, Node and Playwright.[^101][^105][^106] The runtime launches the framework image as a read-only, capability-dropped, incognito app window — but only for the OpenCode-web and observatory modes, and only on a machine with a display.[^107][^108] The browser tool the agent sees — open, screenshot, click, type, close; eval switched off — is a different thing: it drives a host Chrome from the user's cache directory that nothing shipped installs, so a fresh host answers "browser unavailable".[^109][^110][^111][^112]

> RED: The headless core is built and never run,[^105] and the on-demand Chrome download the browser tool depends on still has no caller.[^111] The browser script now defaults to the enclave network,[^115] and the tool's allowlist accepts dotted project names while checking the project label exactly.[^113] Neither change installs the missing host Chrome or demonstrates proxy-only egress for every browser path.[^114]
> PATH: The installer is an open, ready item — wire a real consumer or tombstone the script, its test and its spec.[^112]
> PATH: For the remaining browser egress paths: No path to green is recorded in the repo.

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

> GREEN: Isolation is structural — one `--internal` network, exactly one dual-homed container — not a firewall ruleset you maintain. The launcher the tray runs passes the flag,[^1][^31] and the membership guard runs in the build gate.[^32][^148]

> GREEN: A standing audit corrected the routing spec against the live runtime: it had pinned a privileged port a rootless host cannot always bind. The invariant it protects, loopback-only, was untouched.[^2]

> RED: One thing the spec asks for is missing; another is enforced more narrowly than it reads. The spec requires the network to be removed at application exit when empty, and nothing implements that — the only removal is the destructive reset.[^1][^33] And the membership guard, which does run, counts only builder and launcher functions by name, so an attach site written any other way is invisible to it.[^32]
> PATH: No path to green is recorded in the repo.

> GREEN: The stack-orchestration script now creates the network with `--internal` and refuses to reuse a network lacking isolation.[^3][^117] Its fix landed on 3 September 2026 and is now in stable.[^119] The tray launcher also passes the flag.[^31]

> GREEN: The per-project runner and proxy diagnostic now create the network with `--internal`.[^120][^121] The source gate discovers tracked shell launchers and checks each network-create command; its Rust check still reports a file-scoped limit.[^118]

## What the walls are made of

Agent tooling exists only inside the forge image, never on your host `$PATH`; a missing image makes the launcher refuse rather than fall back to a host binary.[^4][^122] Mounts are enumerated — your project, a read-only CA certificate, the tmpfs roots, a per-launch temp dir, the persistent tool-cache volumes and a Tillandsias-written read-only gitconfig — so `$HOME`, `~/.config` and your keychain are simply not addressable from inside, and a regression test asserts no user home is ever mounted.[^5]

@fig:ephemeral

The forge does not touch your working tree by default: it clones fresh from the enclave mirror, and pushes travel back through the mirror on their way upstream.[^123][^124] An opt-in escape hatch bind-mounts your real checkout read-write and prints a reduced-isolation warning.[^125] Hence the blunt operating rule: **a finding you did not push is a finding you destroyed.**[^7]

## What survives, exactly

Idempotence is what makes destroy-and-recreate a repair procedure rather than a loss. Every layer comes up clean from scratch, so the boundary worth memorising is not "will it break" but "what is on which side of the wipe":

- **Survives a stop:** the bare mirror in its per-project volume, with everything you pushed to it.[^6]
- **Survives a stop:** vault data, auto-unsealed from a single Shamir share held in your host keychain, with no passphrase prompt. The spec requires the share to reach the vault only through a tmpfs-mounted secret;[^8] the shipped guest also keeps a fallback copy of the share on its own disk when no keyring is reachable, and inside a VM guest that file is written on every initialisation.[^126][^127] The lifecycle spec amended on 2026-09-27 says survival of the store requires an unlocking keyring and allows no persisted fallback share, so that code path is ahead of the spec in the other direction: the fallback writer is still present at this release.[^158]
- **Survives even `podman system reset`,** on Linux: the model cache, because it is a host bind mount and not a named volume. The spec spells that distinction out, having once cost someone a wrong answer.[^9] The spec now moves that directory to `~/.tillandsias/downloads/models`, with a one-time migration from the old cache path; the launcher at this release still resolves the model directory under the cache root, so the move is specified and not yet in the code.[^9][^159]
- **Does not survive `--reset-guest`:** it removes every Tillandsias container, volume (the per-project git mirrors among them) and secret and the enclave and egress networks, then re-initialises. On Linux at this release it keeps the model cache and no longer deletes the Vault store, which is a host directory; whether your sign-ins then survive depends on the keyring still holding the unseal share. Push first.[^10][^128][^129] `--reset-state` goes further: it also destroys every Podman image, and still keeps the models and the keyring entries.[^156]

> GREEN: On Linux the reset boundary is documented per artifact and matches the code for what a reset removes and keeps.[^128][^129] The one divergence is the model directory's path, which the spec has moved and the launcher has not.[^9][^159]

> RED: The spec also promises that your host working copy is fast-forwarded after every successful push. No code implements it at this release: the file the spec names does not exist, and the tray-managed host checkout it fed was removed by ruling. After a forge push, your host checkout moves only when you pull.[^130][^143]
> PATH: No path to green is recorded in the repo.

> RED: On macOS the "cache survives" line is not yet proven. The VM at this release already boots with a second shared directory for the model cache, and the guest's first boot mounts it, so the durable path exists.[^131][^132] What remains open: guests provisioned before that change are not migrated, because the mount is written on first boot only, and survival across a VM rebuild has not been demonstrated end to end.[^11][^133] The shipped uninstaller now preserves the VM unless asked to wipe, and asks for a typed confirmation before it removes anything.[^134][^135][^157] A partially restored cache is worse than none — the inference service answers a version check and then fails every request.[^11]
> PATH: An open, ready item: prove survival end to end, which needs a re-provision nobody has authorised, and migrate the guests provisioned before the share. The next recorded step, dated 2026-09-04, is to re-measure on a warm cache: the one cold measurement taken so far came in far below the re-download cost the item was filed with, which now stands as unverified in magnitude.[^133][^136]

> RED: On Windows, wiping the guest used to leave the old unseal share in Credential Manager, and the tray pushed that dead key into the fresh guest, permanently breaking GitHub login. The wipe paths now clear the stale share; a host that already holds one still delivers it, and the guest cannot tell the host it was rejected.[^12][^137]
> PATH: The reconcile half is blocked: the delivery reply carries no accept-or-reject signal, so a delivered share that fails to authenticate cannot yet lose to the guest's own secret.[^138] Until then, remove the stale credential by hand. A second wipe path that still missed the clearing was found and fixed on 2026-09-02 and is included in stable.[^139]

> RED: A host's container engine used to carry a global configuration line routing *all* registry traffic through the enclave proxy unconditionally, so with the stack down `podman build` and `podman pull` died on a raw DNS error that names nothing. Initialising a host now removes that line and hands the proxy setting to each container instead; a host never re-initialised still carries it, and a build that needs the absent proxy still fails without naming it.[^140][^141][^142][^13]
> PATH: The global-config half is done: re-running initialisation converges the file.[^141] The rest is an open, ready item no one has picked up: a build must either not depend on a service that may be absent, or fail with a verdict that names the proxy.[^13]

## Driving it, and where the gate sits

@fig:gate

The verification the earlier levels described is, operationally, a **local** gate: specs declare intent, litmus tests turn each requirement into an executable signal, traces prove the signal ran, and the gate refuses a push that breaks the chain. Two things follow that change how you work.

First, read a green gate with care. Eleven litmus files sit on disk and have never been executed by any suite — grandfathered onto a shrink-only list so that switching the gate on did not flip them all red at once.[^14] The list may shrink; nothing may join it.

Second, the gate on your machine is the only gate there is.

> NOTE: Where a shortcoming below says *No path to green is recorded in the repo*, that is literal: the defect is described and no remedy exists in the plan. Those are collected into one tracking entry so an outside report has somewhere to land, rather than being rediscovered independently.[^155]

> RED: There is no push CI and no PR CI. Actions runs exactly one workflow, the release, because the signing keys exist only in the cloud. Nothing server-side validates a push; the local gate is the sole trunk protection — made load-bearing after an agent pushed unparseable code and every developer inherited the red build.[^15]
> PATH: Not restoration. This is a deliberate budget trade, carrying a standing obligation to run the local gate before every push and an explicit instruction not to add a workflow to catch what a local gate should have caught.[^15]

## Footnotes

[^1]: Enclave network requirements — `--internal` creation, reuse, cleanup on exit, proxy-only egress, and the symbol-anchored membership list the guard enforces | openspec/specs/enclave-network/spec.md#L19-L75
    > A new enclave member MUST be added to this list in the same commit that attaches it; `scripts/lua/check-enclave-membership-documented.lua` refuses the divergence in both directions.
[^2]: Loopback-only publish, the host-port fallback chain, and the 2026-09 freshness audit that corrected the drifted literals | openspec/specs/subdomain-routing-via-reverse-proxy/spec.md#L3-L43
    > What did NOT change, and what the requirement is actually protecting, is the loopback-only invariant: the publish is `127.0.0.1:{host_port}:8080` in every branch.
[^3]: The stack orchestration path now creates an internal network | scripts/orchestrate-enclave.sh#L90-L103
    > --internal
[^4]: Forge-as-only-runtime: the agent binaries must resolve inside a fresh forge, and the host must not need them | openspec/specs/forge-as-only-runtime/spec.md#L48-L68
    > `command -v claude codex opencode bash` MUST print four valid paths from inside a freshly built forge container.
[^5]: Regression test asserting no user home is mounted into a forge, and the mounts it deliberately allows | crates/tillandsias-headless/src/main.rs#L24432-L24432
    > must not mount a host .config dir into the forge; got source in: {arg}
[^6]: Bare mirror per project in a named volume; forge pushes persist there | openspec/specs/git-mirror-service/spec.md#L19-L39
    > The system SHALL create and maintain a bare mirror repository for each project at `/srv/git/<project>` inside the git service container, backed by the named Podman volume `tillandsias-mirror-<project>`.
[^7]: The ephemerality rule, stated for agents | AGENTS.md#L61-L61
    > **IN A FORGE, A FINDING YOU DID NOT PUSH IS A FINDING YOU DESTROYED.**
[^8]: Auto-unseal from the host native keychain, no passphrase prompt, share on tmpfs only | openspec/specs/tillandsias-vault/spec.md#L109-L128
    > The unseal secret SHALL be loaded into a podman secret and mounted at `/run/secrets/vault-unseal` on tmpfs only.
[^9]: Model cache is a host bind mount, NOT a named volume — and why that decides what `podman system reset` destroys; the spec now names `~/.tillandsias/downloads/models/` | openspec/specs/inference-container/spec.md#L30-L32
    > Models SHALL be stored in a HOST DIRECTORY (a bind mount, NOT a named Podman volume)
[^10]: What `--reset-guest` wipes and what it keeps | crates/tillandsias-headless/src/main.rs#L1706-L1706
    > keeps the model cache) and re-initialize.
[^11]: macOS model cache and engine payload inside the VM disk image; the destroyers, the outage a lost engine caused, and the ~2.47 GB figure as filed (status: ready) | plan/index.yaml#L27667-L27667
    > every VM-directory deletion forces a ~2.47 GB re-download — the macOS twin of 518
[^12]: Windows Credential Manager retains a stale unseal share across a guest wipe; the wipe half landed, the reconcile half still open (status: ready) | plan/index.yaml#L26930-L26930
    > every Windows reset path (--reset-guest, installer -Purge, the e2e smoke) wipes the guest vault but never clears vault-shamir-share-v1 from Credential Manager
[^13]: Global container config hardcodes the enclave proxy, so builds fail on DNS when the stack is down; the open deliverable is a verdict naming the proxy (status: ready) | plan/index.yaml#L37615-L37615
    > ~/.config/containers/containers.conf hardcodes http_proxy=http://proxy:3128 unconditionally, so when the enclave is down EVERY image build fails on DNS — and with it the release gate
[^14]: The ratchet list of litmus files that have never run, and why they are exempt | openspec/litmus-tests/unbound-grandfathered.txt#L1-L25
    > THE ONLY LEGITIMATE EDIT TO THIS FILE IS A DELETION
[^15]: The Actions budget ruling: one workflow, what was removed, and what was given up | methodology/ci.yaml#L286-L324
    > GitHub Actions runs EXACTLY ONE workflow: the release. Nothing else may consume cloud minutes — no push CI, no PR CI, no scheduled jobs, no cache warming, no webhooks. Every other gate runs locally.
[^16]: The startup context's infrastructure section: everything transparent, nothing to configure | images/default/lib-common.sh#L4978-L5007
    > You never need to configure git remotes, tokens, SSH keys, proxy settings, or CA certs.
[^17]: The heavy base layer: Fedora Minimal with the toolchains in one package set | images/default/Containerfile.base#L5-L35
    > rust cargo clippy rustfmt rust-analyzer cargo-deny
[^18]: The thin runtime layer on top of the base | images/default/Containerfile#L1-L6
    > Builds upon the heavy base image to inject configuration,
[^19]: Image identity is a content hash of the sources | openspec/specs/default-image/spec.md#L100-L104
    > The default forge image SHALL use a content-hash canonical tag derived from the image source set.
[^20]: Harnesses refresh at every launch into the persistent per-project tool cache, and a freshly installed binary that fails its contracts is replaced by the last good one | openspec/specs/default-image/spec.md#L196-L237
    > A freshly installed OpenCode that violates any of those contracts SHALL be rejected and replaced by that last-good binary.
[^21]: The tool cache is a podman named volume, not a host bind-mount, so it cannot become a credential-leak path | crates/tillandsias-headless/src/main.rs#L17589-L17589
    > A named volume — not a host bind-mount —
[^22]: The three RAM-backed roots the launcher mounts at this release | crates/tillandsias-headless/src/main.rs#L18125-L18125
    > .tmpfs("/tmp:size=256m,mode=1777")
[^23]: The on-demand tool allowlist in full: every listed command becomes a PATH shim that installs on first use | images/default/brew-tools-allowlist.txt#L1-L122
    > Commands listed here get a PATH shim in the forge: running the command
[^24]: Where the startup context file is written | images/default/lib-common.sh#L4679-L4679
    > local ctx_file="$project_dir/.forge-startup-context.md"
[^25]: The hot/cold spec: exactly four RAM-backed roots, the source tree among them | openspec/specs/forge-hot-cold-split/spec.md#L11-L24
    > Only these four path roots are HOT. "Maybe a hot path" is a HARD NO.
[^26]: The mount-topology packet: source tmpfs, host RAM gate and memory ceiling still to wire (status: ready) | plan/index.yaml#L8207-L8207
    > production launch runs check_host_ram, derives compute_memory_ceiling_mb, and emits equal --memory and --memory-swap limits
[^27]: The Homebrew prefix is ephemeral; every launch re-installs on-demand tools (status: ready) | plan/index.yaml#L12407-L12407
    > The brew prefix is ephemeral, so every forge launch re-installs and re-attests every tool — that is the rate-limit multiplier
[^28]: The startup context's claim of a Sigstore attestation per bottle | images/default/lib-common.sh#L5079-L5084
    > it verifies a Sigstore attestation per bottle
[^29]: What the shim verifies today: integrity from one publisher, attestation off | images/default/brew-shim-exec.sh#L12-L21
    > Sigstore verification is OFF because it requires a GitHub credential to FETCH
[^30]: The source tmpfs budget is calculated from the mirror pack size | crates/tillandsias-headless/src/main.rs#L17625-L17625
    > format!("/home/forge/src:size={budget}m,mode=0777")
[^31]: The launcher creates the enclave network with `--internal` on first launch, after ensuring the egress network | crates/tillandsias-headless/src/main.rs#L3218-L3221
    > command.args([ "network", "create", "--internal",
[^32]: The membership guard (now a Lua decider): every attach site's enclosing function must be in the spec and vice versa; it counts only builder and launcher functions | scripts/lua/check-enclave-membership-documented.lua#L60-L81
    > local BUILD_LAUNCH = [[^(build|launch)_]]
[^33]: The only network removal in the launcher: the destructive reset | crates/tillandsias-headless/src/main.rs#L10642-L10642
    > command.args(["network", "rm", "-f", &name]);
[^34]: Proxy variables injected into every enclave container from one source | crates/tillandsias-headless/src/main.rs#L2015-L2015
    > "http_proxy=http://proxy:3128".into(),
[^35]: The forge composes vendor roots plus the proxy CA into the system-default bundle before any network client starts | images/default/lib-common.sh#L12-L23
    > Compose the per-install CA into that target atomically, before any network
[^36]: No per-client CA variables; trust flows through the distribution's standard path | openspec/specs/transparent-https-caching/spec.md#L57-L62
    > launchers and entrypoints SHALL NOT select CA files with `GIT_SSL_CAINFO`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, or `NODE_EXTRA_CA_CERTS`.
[^37]: A regression test pins the CA mount and the absence of CA overrides | crates/tillandsias-headless/src/main.rs#L24542-L24542
    > typed forge launcher must mount the single runtime CA input
[^38]: Package-manager workflows must work with no configuration | openspec/specs/proxy-container/spec.md#L157-L157
    > common development workflows (npm install, cargo build, pip install, flutter pub get) work out of the box without configuration.
[^39]: Proxy purpose: allowlisted caching forward proxy, bump only the release-asset CDN, splice all other TLS | openspec/specs/proxy-container/spec.md#L8-L14
    > HTTPS interception is deliberately exceptional: the proxy bumps only the exact GitHub release-asset CDN hostname and splices all other TLS traffic end to end.
[^40]: The three ssl_bump rules: peek once, bump one exact host, splice everything else | images/proxy/squid.conf#L133-L139
    > ssl_bump peek ssl_bump_step1 ssl_bump bump github_release_assets ssl_bump splice all
[^41]: Spliced HTTPS is never cached by the proxy | openspec/specs/proxy-container/spec.md#L44-L49
    > the HTTPS response SHALL NOT be cached (tunneled traffic is opaque to squid)
[^42]: cargo, Go, npm and pip caches all redirected into the per-project cache | images/default/lib-common.sh#L2227-L2259
    > export CARGO_HOME="$PROJECT_CACHE/cargo"
[^43]: Blocked hosts get a TCP reset, not a 403 | images/proxy/squid.conf#L151-L156
    > deny_info TCP_RESET strict_deny_acl
[^44]: The live miss-then-hit trace for the bumped host was never recorded, and the next action that would record it (status: ready) | plan/index.yaml#L7533-L7576
    > no rebuilt-image parser result or real identical-key MISS-to-HIT trace is claimed
[^45]: The consumer contract: one endpoint at inference:11434, downloads through the proxy | openspec/specs/inference-container/spec.md#L13-L14
    > Forge containers SHALL access it via `OLLAMA_HOST=http://inference:11434`. The inference container SHALL use the proxy for model downloads.
[^46]: Inference readiness is best-effort, never a launch gate | crates/tillandsias-headless/src/main.rs#L17226-L17226
    > Local inference readiness (order 392) is BEST-EFFORT, not a launch
[^47]: The single default chat model pulled on first run | images/inference/entrypoint.sh#L120-L120
    > DEFAULT_MODELS="${TILLANDSIAS_DEFAULT_MODELS:-qwen2.5:0.5b}"
[^48]: The engine download pins a version and architecture-specific digests | images/inference/entrypoint.sh#L329-L335
    > OLLAMA_VERSION="v0.34.0"
[^49]: The closed-vocabulary accelerator line every forge receives | crates/tillandsias-headless/src/accel_probe.rs#L4402-L4402
    > accel_class=<workstation-gpu|mobile-npu|hybrid-gpu-npu|cpu-only>
[^50]: Ready means the endpoint answers and at least one model is cached; there is no "starting up" | images/default/lib-inference-state.sh#L14-L24
    > Reason vocabulary (CLOSED SET — there is deliberately no "starting up"):
[^51]: Larger tier models are opt-in, not default | images/inference/entrypoint.sh#L795-L798
    > tier pulls opt-in (set TILLANDSIAS_INFERENCE_TIER_PULLS=1) — skipping runtime tier pulls
[^52]: The CPU floor is unconditional by spec | openspec/specs/inference-container/spec.md#L154-L159
    > Tier-S SHALL be available on every host regardless of GPU, NPU, driver, or engine availability, and SHALL NOT be gated on any device probe.
[^53]: A missing verifier or wrong engine digest prevents execution | images/inference/entrypoint.sh#L371-L383
    > FATAL: sha256sum unavailable — cannot verify the engine payload, refusing to execute it
[^54]: NVIDIA delivery is gated on a CDI spec; without one the host degrades to CPU with a loud remedy | crates/tillandsias-headless/src/main.rs#L6059-L6059
    > a GPU host without CDI degrades to CPU with a LOUD remedy
[^55]: The AMD lane is selected only when ROCm reports a graphics agent | crates/tillandsias-headless/src/main.rs#L5171-L5171
    > let rocm = std::process::Command::new("rocminfo")
[^56]: The spec: NPU rows are never attempted on the shipped engine | openspec/specs/inference-container/spec.md#L186-L193
    > N rows SHALL NOT be attempted on the `ollama` engine kind. Ollama cannot use any NPU
[^57]: On Windows the NPU cannot be seen from inside the guest at all | scripts/windows-host-capability-probe.sh#L12-L14
    > The NPU is not merely undetected in the guest, it is STRUCTURALLY invisible:
[^58]: The health check tests that the runner binary exists; the real load check runs once at startup | images/inference/Containerfile#L112-L121
    > A real generate would be the strongest assertion but is far too expensive at a
[^59]: NPU passthrough for the container is an open packet (status: ready) | plan/index.yaml#L9263-L9263
    > Impl: NPU /dev/accel passthrough plumbing for the inference container (AMD XDNA2 first lane)
[^60]: The host-native sidecar for Metal and the NPUs is an open packet (status: ready) | plan/index.yaml#L9419-L9419
    > Impl: host-native inference sidecar registry (macOS Metal/MLX, AMD XDNA2 flm/Lemonade, Intel NPU OpenVINO) behind the enclave proxy
[^61]: Agents configure nothing and still see the original GitHub URL | openspec/specs/git-mirror-service/spec.md#L470-L476
    > `git push`, `git fetch`, and `git clone` SHALL work with zero agent-side configuration
[^62]: One atomic push of explicit refspecs | images/git/relay-refs.sh#L298-L298
    > git push --atomic "$PUSH_URL" "$@"
[^63]: The mirror acknowledges only after upstream durably accepts the ref transaction | images/git/pre-receive-hook.sh#L765-L765
    > Push rejected: configured upstream did not durably accept the ref transaction
[^64]: The GitHub token is read from Vault at push time inside the git service and never crosses into a forge | openspec/specs/git-mirror-service/spec.md#L14-L16
    > The git service reads the GitHub token from Vault at push time via Vault CLI; the token never crosses into a forge container.
[^65]: The credential helper fetches the token from Vault over git's credential protocol | images/git/git-credential-tillandsias.sh#L93
    > TOKEN="$(vault-cli read -field=token secret/github/token 2>/dev/null || true)"
[^66]: Every start re-applies receive hardening: no deletes, no rewinds, object checks | openspec/specs/git-mirror-service/spec.md#L98-L106
    > the git service SHALL set `receive.denyNonFastForwards=true`, `receive.denyDeletes=true`, and `receive.fsckObjects=true`.
[^67]: A project with no upstream keeps pushes durably in the local-only mirror | images/git/relay-refs.sh#L157-L157
    > No upstream configured; accepting as a durable local-only mirror update
[^68]: Without a stored token the relay refuses and names the remedy | images/git/relay-refs.sh#L193-L193
    > HTTPS upstream credential is unavailable; run GitHub Login before pushing
[^69]: The mirror daemon's push path is anonymous inside the enclave, and the repo says so in the same breath as the hardening that limits the damage | images/git/entrypoint.sh#L504-L504
    > The daemon remains anonymous inside the enclave: any reachable peer can still
[^70]: The authenticated SSH push lane is dark behind one flag until the default flip | crates/tillandsias-headless/src/main.rs#L13186-L13186
    > std::env::var("TILLANDSIAS_MIRROR_SSHD")
[^71]: Offline or credential-less, the forge's push returns non-zero and nothing is partially applied | openspec/specs/git-mirror-service/spec.md#L224-L230
    > the forge's `git push` SHALL return non-zero
[^72]: The SSH-lane default flip is an open packet (status: ready) | plan/index.yaml#L20538-L20538
    > T11+T12 — flip one lane behind a flag once the §4a matrix is green
[^74]: Vault is the default and only Linux secrets backend; GitHub token and short-lived per-container tokens | openspec/specs/tillandsias-vault/spec.md#L11-L14
    > Run a HashiCorp Vault container as the default and ONLY Linux secrets backend for Tillandsias.
[^75]: The shipped Vault listener is TLS-only | images/vault/vault.hcl#L16-L24
    > tls_cert_file   = "/run/secrets/tillandsias-vault-tls-cert"
[^76]: Every OAuth-credentialed agent lane mounts one scoped Vault token | crates/tillandsias-headless/src/main.rs#L18186-L18186
    > Every OAuth-credentialed agent lane mounts a scoped Vault token so its
[^77]: Forge containers get no broad Vault token, only a provider-scoped short-lived one | openspec/specs/tillandsias-vault/spec.md#L348-L353
    > Forge containers SHALL NOT receive a broad Vault token.
[^78]: The generic forge policy cannot read the GitHub token | images/vault/policies/forge.hcl#L1-L8
    > Explicitly NO github or token access — forge containers must remain
[^79]: The tray policy reads the whole secret tree | images/vault/policies/tray.hcl#L1-L6
    > path "secret/*" {
[^80]: The startup context advertises http for a TLS-only Vault | images/default/lib-common.sh#L5005-L5005
    > http://vault:8200
[^81]: The in-image helper defaults to https and the tmpfs token path | images/default/vault-cli.sh#L23-L24
    > VAULT_ADDR="${VAULT_ADDR:-https://vault:8200}"
[^82]: Client tokens default to a one-hour TTL | openspec/specs/tillandsias-vault/spec.md#L252-L256
    > Every client token, including tokens minted by Vault Agent, SHALL default to TTL 1h with a maximum TTL of 24h.
[^83]: Four MCP servers registered for Claude Code inside the forge image | images/default/config-overlay/claude/mcp.json#L2-L23
    > "command": "/home/forge/.config-overlay/mcp/forge-plan.sh"
[^84]: The same four servers registered for OpenCode | images/default/config-overlay/opencode/config.json#L66-L87
    > "command": ["/home/forge/.config-overlay/mcp/forge-plan.sh"],
[^85]: Spec: the generic project expert bootstraps for any project with no registration or configuration | openspec/specs/forge-environment-discoverability/spec.md#L171-L173
    > The forge MUST bootstrap a project expert surface for an ARBITRARY mounted project without manual registration, configuration, or repository-type knowledge from the caller.
[^86]: The plan expert's refusal rule: zero citations means unsupported | images/default/config-overlay/mcp/forge-plan.sh#L1355
    > An answer with zero citations is returned as confidence=unsupported — the expert refuses rather than guesses.
[^87]: The plan expert is degraded by design on a project without the plan crate | images/default/lib-common.sh#L4996-L4996
    > (this project has no plan expert — expected off-tillandsias)
[^88]: Discovery, expert build and the grounded endpoint all backgrounded and fail-soft after the clone | images/default/lib-common.sh#L1652-L1658
    > ensure_forge_experts >>/tmp/forge-lifecycle.log 2>&1 || true
[^89]: The on-demand spec obliges the tray to detect and spawn servers | openspec/specs/mcp-on-demand/spec.md#L32-L37
    > the tray MUST detect that the filesystem MCP server is not running
[^90]: The startup context every lane reads names Local Experts mode | images/default/lib-common.sh#L5015-L5015
    > Local Experts mode (the
[^91]: Only the OpenCode configuration carries an agent bound to the grounded endpoint | images/default/config-overlay/opencode/config.json#L18-L30
    > "model": "tillandsias-experts/all",
[^92]: The pre-expert-binary trap: criterion 2 closed, the fresh-forge criterion still open (status: ready) | plan/index.yaml#L6796-L6873
    > criterion 1 (release/branch decision) still OPEN — packet intentionally stays `ready` (partial reduction)
[^93]: The catalog is an allowlist: WEB only, refused host-side otherwise | openspec/specs/enclave-service-catalog/spec.md#L22-L26
    > Requests outside the catalog are refused host-side; the guest cannot mint categories.
[^94]: The web image: busybox httpd on 8080, document root /var/www | openspec/specs/web-image/spec.md#L24-L25
    > The image MUST serve static files from `/var/www` on port 8080 using busybox httpd with no additional packages or configuration.
[^95]: One socket per lane, bind-mounted into the forge; attribution comes from the listener that accepted the connection, never from the request | openspec/specs/mcp-tool-socket/spec.md#L31-L64
    > The project (and instance) a request acts on SHALL be derived from WHICH LISTENER accepted the connection. The tray SHALL NOT read the project from the request body, from the peer process's environment, or from any other peer-supplied source.
[^96]: The live publish path hands back an https URL for the www name on the router's TLS port | crates/tillandsias-headless/src/local_web_preview.rs#L730-L730
    > Ok(format!("https://www.{project}.localhost:{}", tls_port()?))
[^97]: From inside the forge, .localhost requests are forwarded by the proxy to the router | images/proxy/squid.conf#L183-L188
    > cache_peer_access tillandsias-router allow localhost_subdomain
[^98]: What a consumer found reachable when the earlier path served the repository root (status as filed: ready) | plan/index.yaml#L44421-L44421
    > /.git/config returned 200 through the router (full history + remote URLs reconstructible)
[^99]: The stack sweep's name patterns: a published sibling matches none of them | crates/tillandsias-headless/src/main.rs#L7698-L7698
    > name.starts_with("tillandsias-git-")
[^100]: Projects must live under ~/src on the host; discovery hardcodes it (status: ready) | plan/index.yaml#L42106-L42106
    > tray discover_projects hardcodes ~/src and run_opencode_mode starts no lane listener
[^101]: The declarative image set initialisation builds: both Chromium images and the web image among them | crates/tillandsias-headless/src/main.rs#L10190-L10192
    > "forge-base", "forge", "web",
[^102]: An ordinary forge launch ensures four images, not the web or browser ones | crates/tillandsias-headless/src/main.rs#L17144-L17144
    > let images = ["router", "git", "inference", "forge"];
[^103]: The phantom pull the status-check path was fixed for | crates/tillandsias-headless/src/main.rs#L11005-L11005
    > phantom registry pull (125) on any version handover.
[^104]: The end-to-end publish litmus has never been run by any suite | openspec/litmus-tests/unbound-grandfathered.txt#L21-L21
    > litmus:publish-local-e2e
[^105]: The headless core image and its entrypoint | images/chromium/Containerfile.core#L36-L37
    > ENTRYPOINT ["/usr/lib64/chromium-browser/headless_shell", "--headless=new"]
[^106]: The framework image extends the core with GUI Chromium, Node and Playwright | images/chromium/Containerfile.framework#L15-L35
    > RUN npm install -g --prefix=/usr \ playwright \
[^107]: The hardened, ephemeral browser container the runtime launches | crates/tillandsias-headless/src/main.rs#L15944-L15944
    > Hardened browser boundary: read-only rootfs, CAP_DROP=ALL, no-new-privileges,
[^108]: Browser launch requires a graphical session | crates/tillandsias-headless/src/main.rs#L15902-L15902
    > OpenCode Web browser launch requires a graphical session (DISPLAY or WAYLAND_DISPLAY)
[^109]: The browser tool spawns a host Chromium from the cache directory, not a container | crates/tillandsias-browser-mcp/src/launcher.rs#L78-L82
    > root.join("current/chrome"),
[^110]: A missing bundled Chromium returns BROWSER_UNAVAILABLE | crates/tillandsias-browser-mcp/src/server.rs#L431-L435
    > BROWSER_UNAVAILABLE: bundled chromium not yet downloaded
[^111]: The only Chromium installer has no consumer | scripts/install-chromium.sh#L10-L16
    > INTEGRATION STATUS (2026-08-16 freshness audit, 774-cfw8): NO consumer
[^112]: The wire-it-or-tombstone packet for the orphaned installer (status: ready) | plan/index.yaml#L22074-L22074
    > scripts/install-chromium.sh has ZERO consumers while its header claimed two integrations; a litmus pins a shape nothing ships — wire it or tombstone it
[^113]: The allowlist accepts dotted project labels and compares them exactly | crates/tillandsias-browser-mcp/src/allowlist.rs#L250-L257
    > let host_project_label = labels[1..labels.len() - 1].join(".");
[^114]: Safe variant: proxy-only egress is the spec | openspec/specs/chromium-safe-variant/spec.md#L16-L19
    > Full network isolation inside the enclave, with allowlist enforcement via the proxy only; no host-gateway internet fallback
[^115]: The browser script defaults to the enclave network | scripts/launch-chromium.sh#L93-L98
    > "--network=${TILLANDSIAS_BROWSER_NETWORK:-${TILLANDSIAS_ENCLAVE_NET:-tillandsias-enclave}}"
[^116]: The router's host-port candidates: an explicit --port first, then 80 and the fallbacks | crates/tillandsias-headless/src/main.rs#L6915-L6915
    > let mut candidates = vec![80, 8080, 18080, 28080, 38080, 48080, 58080];
[^117]: Stack orchestration script now passes `--internal` and refuses to reuse an unisolated network | scripts/orchestrate-enclave.sh#L82-L126
    > Network $ENCLAVE_NET EXISTS BUT IS NOT INTERNAL — it was created without --internal, so every member has NAT egress and the proxy is not the only way out (order 972-a8vh, spec:enclave-network).
[^118]: The gate discovers tracked shell launchers and names its Rust limit | scripts/check-enclave-network-internal.sh#L113-L135
    > The shell side IS invocation-scoped: continuations are folded first, and the flag must appear on the same logical line as the create verb.
[^119]: The fix recorded complete on 2026-09-03, with isolation measured from inside a member container | plan/archive/packets-2026-09.yaml#L7344-L7344
    > Both exit criteria met; fixed in de9560fb5.
[^120]: The per-project runner creates an internal network | scripts/run-forge-project.sh#L127-L130
    > "$PODMAN_CTL" network create --driver bridge --internal --subnet "$ENCLAVE_SUBNET" "$ENCLAVE_NET" >/dev/null
[^121]: The proxy diagnostic creates an internal network | scripts/diagnose-proxy.sh#L94-L97
    > podman network create --driver bridge --internal --subnet "10.0.42.0/24" "$ENCLAVE_NET"
[^122]: A missing forge image makes the launcher refuse, never fall back to a host binary | openspec/specs/forge-as-only-runtime/spec.md#L114-L115
    > The tray MUST refuse to launch an agent if the forge image is missing — it MUST NOT silently fall back to a host binary.
[^123]: Clone-only by default: the host checkout is the opt-in path | crates/tillandsias-headless/src/main.rs#L18039-L18039
    > Order 437: clone-only by default.
[^124]: Forge containers clone from the mirror and push through it | openspec/specs/git-mirror-service/spec.md#L54-L61
    > Forge containers SHALL clone from `git://git-service/<project>`
[^125]: The reduced-isolation warning the host-mount escape hatch prints | crates/tillandsias-headless/src/main.rs#L7435-L7435
    > WARNING: WORKSPACE ENCLAVE ISOLATION IS REDUCED
[^126]: Inside a VM guest the share is written to a fallback file on every initialisation | crates/tillandsias-headless/src/vault_bootstrap.rs#L2851-L2851
    > Inside the VM there is no OS keychain, so these files are the only durable
[^127]: Where no OS keyring is reachable the share falls back to a file in the cache directory | crates/tillandsias-headless/src/vault_bootstrap.rs#L4907-L4907
    > using fallback file (expected in VM guest and headless environments)
[^128]: What the reset wipes on the host side: nothing; the function that used to name the vault data directory returns an empty list | crates/tillandsias-headless/src/main.rs#L10397-L10399
    > fn reset_guest_wipe_paths(_cache_dir: &Path) -> Vec<PathBuf> {
[^129]: The pin test: the model cache must never be in the reset wipe set | crates/tillandsias-headless/src/main.rs#L33303-L33303
    > the inference model cache must never be in the reset wipe set
[^130]: The host working-copy fast-forward is specified, and specified against a file that does not exist | openspec/specs/git-mirror-service/spec.md#L344-L363
    > The tray SHALL trigger a fast-forward attempt on the host working copy at `<watch_path>/<project>` for every successful push to the enclave bare mirror
[^131]: The VM boots with a second shared directory for the model cache | crates/tillandsias-vm-layer/src/vz.rs#L2907-L2907
    > tag: "model-cache".to_string(),
[^132]: The guest's first boot persists the model-cache mount | crates/tillandsias-vm-layer/src/vz.rs#L1078-L1078
    > model-cache /root/.cache/tillandsias/models virtiofs nofail 0 0
[^133]: The enabling change landed and the packet stayed ready: migration and end-to-end survival unverified | plan/index.yaml#L27804-L27804
    > guest wiring verified by source scan, MIGRATION UNVERIFIED.
[^134]: The shipped uninstaller preserves the VM unless asked to wipe | scripts/uninstall.sh#L228-L228
    > Preserving the VM image in $DATA_DIR (use --wipe to remove it).
[^135]: The uninstaller defect the macOS packet waited on, closed | plan/archive/packets-2026-08.yaml#L23430-L23436
    > shipped uninstall.sh deletes the 11.83 GiB VM directory with no --wipe, no root and no prompt
[^136]: The cold measurement and its limit for a populated model cache | plan/index.yaml#L27838-L27838
    > Re-fetched from the network: the Fedora Cloud qcow2 only, 514 MB.
[^137]: The wipe half landed; a host already holding a stale share is unaffected | plan/index.yaml#L26924-L26924
    > a host that ALREADY holds a stale credential is unaffected
[^138]: The delivery reply carries no accept-or-reject signal (status: ready) | plan/index.yaml#L37937-L37937
    > DeliverCredentials reply says "I received it", never "I accepted it"
[^139]: A second wipe path found and fixed in the daily channel | plan/index.yaml#L27111-L27111
    > found Part A missing on the SECOND purge path (build-and-install-windows-local.ps1); unifying and gating it
[^140]: Initialisation removes the orphaned global proxy block | crates/tillandsias-headless/src/main.rs#L9222-L9222
    > Remove the orphaned `[engine] env` proxy block.
[^141]: What initialisation prints when it converges the file | crates/tillandsias-headless/src/main.rs#L9383-L9383
    > removed the orphaned [engine] env proxy block from {} (923-rmtw); containers receive proxy env per-container
[^142]: The global-config fix, archived as completed | plan/archive/packets-2026-08.yaml#L46813-L46818
    > containers-conf-env-line-is-orphaned-and-never-converges
[^143]: The operator directive that removed the tray-managed host checkout | plan/index.yaml#L16185-L16185
    > It is REMOVED ENTIRELY.
[^144]: The daily channel's record of the source tmpfs landing, dated | plan/index.yaml#L46599-L46599
    > TMPFS SLICE LANDED (997-e4v2, slice 1 of 3). compute_hot_budget() has a real caller for the first time since it was archived as complete on 2026-04-27.
[^145]: Fetch and pin the attestation bundles at image build time so no lane needs a GitHub identity (status: ready) | plan/index.yaml#L12320-L12320
    > a forge lane installs an allowlisted tool with attestation verified and NO GitHub credential present anywhere in the lane
[^146]: The shared inference container is created only when it is not already running, so sibling forges share one | crates/tillandsias-headless/src/main.rs#L17277-L17278
    > inference is recreate-if-not-running (a --replace would drop loaded models and interrupt a sibling's inference mid-flight).
[^147]: The test pinning the scoped lease for every credentialed lane, and its absence from the credential-free ones | crates/tillandsias-headless/src/main.rs#L29042-L29042
    > Credential-free lanes never mount a provider lease.
[^148]: The check gate invokes the membership guard and fails the build when it refuses | build.sh#L2922-L2922
    > if ! _run_lua_decider "scripts/lua/check-enclave-membership-documented.lua" 2>&1; then

[^149]: Only the clone-only lane mounts the RAM-backed source volume; the host-mount arm binds the checkout instead | crates/tillandsias-headless/src/main.rs#L18051-L18062
    > forge_ram_workspace_volume(project_name),

[^150]: The context distinguishes waiting, relaunching and relaunch regression | images/default/lib-common.sh#L4994-L5003
    > \`relaunch-regresses\` means the running binary has MORE than the checkout and a relaunch would REMOVE capability.

[^151]: Ready inference alone does not provide the project index with a synthesis tier | images/default/config-overlay/mcp/project-info.sh#L789-L789
    > no synthesis tier is wired into project_answer yet

[^152]: The upstream token is read by the git service at push time and never enters a workspace container | openspec/specs/git-mirror-service/spec.md#L15-L16
    > The git service reads the GitHub token from Vault at
    > push time via Vault CLI; the token never crosses into a forge container.
[^153]: The relay is synchronous: local acceptance follows upstream acceptance | images/git/pre-receive-hook.sh#L6-L8
    > Validates ledger YAML, then synchronously relays the proposed ref transaction
    > upstream before accepting it locally. A client success therefore means the
    > configured upstream has durably accepted the same atomic ref set.
[^154]: The live relay pushes the refs as one atomic transaction | images/git/relay-refs.sh#L298-L298
    > if OUTPUT="$(GIT_TERMINAL_PROMPT=0 git push --atomic "$PUSH_URL" "$@" 2>&1)"; then
[^155]: The entry tracking every shortcoming here for which no remedy is recorded | https://github.com/8007342/tillandsias/blob/linux-next/plan/index.d/20260915t215254z-1213-rbt9-website-found-fourteen-shortcomings-the-ledger-does-not-track-macuahuitl.yaml
[^156]: What a soft reset destroys and what it keeps | crates/tillandsias-headless/src/main.rs#L10557-L10567
    > <cache>/tillandsias/models and every other download in the cache
[^157]: The uninstaller asks for a typed confirmation before removing anything | scripts/uninstall.sh#L184-L184
    > Type \"delete\" to uninstall, or press Enter to cancel:
[^158]: The lifecycle spec's amendment: store survival requires an unlocking keyring, no persisted fallback share | openspec/specs/host-state-lifecycle/spec.md#L13-L18
    > survival of the Vault store REQUIRES an unlocking keyring — no persisted fallback share
[^159]: The launcher resolves the model directory under the cache root | crates/tillandsias-headless/src/main.rs#L5954-L5957
    > &tillandsias_core::cache_root::cache_root().join("models"),
[^160]: The preview never mounts .git, .env or the forge root; it selects a document tree or named assets | crates/tillandsias-headless/src/local_web_preview.rs#L544-L551
    > Static compatibility selects a public document tree, never mounts .git/.env/the forge root into a sibling.
[^161]: A departed lane's preview and route are removed | crates/tillandsias-headless/src/local_web_preview.rs#L1289-L1291
    > Called only after the launcher proves no forge remains for this lane.
[^162]: The preview spec's own status | openspec/specs/local-web-preview/spec.md#L7-L10
    > verification: S0 (design; executable coverage and live evidence pending)
[^163]: The plan item to prove the preview live and activate the scoped specs | plan/index.d/20261007-local-web-preview-design-yoga.yaml#L79-L79
    > title: Prove live tillandsias.org preview and activate scoped specs
[^164]: Publishing refuses when the managed runtime image is absent | crates/tillandsias-headless/src/local_web_preview.rs#L1038-L1041
    > initialize the managed runtime image before publication
