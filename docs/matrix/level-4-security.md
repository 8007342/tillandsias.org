# Tillandsias, for an IT / security reader

## The claim, and what it actually buys you

Tillandsias runs coding agents — LLMs with a shell — against your source inside a bounded, disposable enclave on your own machine. Nothing phones home: no project-operated server, no analytics SDK in the tree.[^1] The security question is therefore the old one: *when an agent does something you did not intend, how far does it get?*

> GREEN: The threat model is written down in the project's own voice, including the parts that make it look bad — the architecture notes state plainly that the allowlist is generous by design and that an attacker can encode data in DNS queries or headers to an allowed domain.[^2]

## The isolation model, layer by layer

@fig:layers

The layering differs by OS, and that is the first thing a reviewer gets wrong.

- **Windows** provisions a WSL2 Fedora guest; **macOS** a Virtualization.framework guest — both a real hypervisor boundary.
- **Linux does not.** Podman is the only host dependency; the orchestrator drives rootless containers directly on the host.[^3] There is no VM.

Inside, every launch is meant to carry four flags — userns mapping to your own uid, all capabilities dropped, no-new-privileges, label-disable — with a policy module that audits the argv and rejects privileged mode, a non-identity userns, or a blanket capability add.[^4] Read the fourth honestly: **SELinux labelling is off on every container**.[^5] And read the envelope as *defaults on a struct*, not an invariant.

> RED: The requirement that the hardening flags are immutable has no production enforcement. Each flag is emitted only if its boolean field is true, and the one place that checks the assembled command line is a debug assertion — compiled out of every release build.[^6] In a shipped binary, a caller that turns a flag off or adds back a capability is not stopped, or even logged. The test covering it is worse than absent: five of its eight steps echo their own success token on the failure branch, printing `CAP_DROP_ALL_SET` whether the inspection found the flag or not — structurally incapable of going red. And the container it inspects is one the test itself launched with the flags typed on the command line, so even the steps that can fail are testing Podman, not Tillandsias.[^7]
> PATH: Partial, and it does not reach this file. A scanner for litmus steps that pass while failing exists, but it is explicitly advisory with nothing gating on it, skips over half the corpus as not provably read-only, and keys on a non-zero exit — which `|| echo` suppresses, leaving it blind to this exact variant.[^8] A separately approved bar-raise on litmus quality is diff-scoped and, in the project's own words, structurally incapable of flagging the existing corpus.

> RED: On Linux the enclave is a namespace boundary, not a virtualization boundary — an escape lands as your own uid, with your `$HOME`, on the host[^9] — and SELinux confinement is disabled, so on a Fedora or RHEL host you are *less* confined than a default container would be.
> PATH: Partial. SELinux MCS labelling is recorded as a planned later phase, written as intent with no implementation and no litmus behind it.[^5] For the missing hypervisor nothing is recorded: Linux-native operation without a VM is a design choice, mitigated by defence in depth rather than a stronger boundary.

## Egress: what is blocked, and what is actually decrypted

The enclave network is `--internal`: containers on it have no default route, and name resolution is container-local.[^10] Only the proxy is dual-homed, running a Squid that is default-deny against an explicit allowlist. There is no packet filter anywhere — no iptables, no nftables. Enforcement is **network placement plus proxy environment variables**; an agent can trivially unset `HTTP_PROXY`, and what stops it is that the namespace has nowhere to send the packet.

@fig:gate

Then the question every reader asks on hearing "trusted CA in the container":

> GREEN: This is **not** a blanket MITM. The proxy peeks at the handshake and then splices — passes through undecrypted — everything but one exact hostname, GitHub's release-asset CDN, bumped so large binaries can be cached. Registries, GitHub's APIs and every auth endpoint stay end-to-end encrypted.[^11]

> GREEN: Where it does terminate TLS it still verifies upstream against the system trust store, and the config carries a standing written order never to disable peer or domain verification — that would hide a real origin MITM behind a proxy-issued certificate.[^12]

The flip side: because only one host is decrypted, the proxy does **no payload inspection** — it sees hostnames, not content — and the allowlist admits anyone-can-publish namespaces, so an allowlist hit is not evidence of a benign destination.[^2]

> RED: The proxy's certificate-authority private key was created world-readable in a shared temp directory, so any local account could mint certificates the whole enclave trusts. The code was fixed — but the fix lives in the tray binary and every host runs a pre-fix release, so two machines were found still carrying a world-readable CA key days after the issue was marked closed.
> PATH: An idempotent host-side repair script exists — it clamps the directory before the key to avoid a traversal window and heals material the old binary created. That is the remediation until a release ships with the code fix.[^13]

> RED: The published proxy spec describes something the code does not do: a fresh two-level EC P-256 chain generated per launch, held only on tmpfs, no CA key ever touching disk.[^14] The shipped code generates one self-signed RSA-2048 certificate with a 30-day life into a temp directory, reused across restarts.[^15]
> PATH: No path to green is recorded in the repo — the spec has not been marked stale, and no change proposal reconciles it with the implementation.

## Secrets, and the channel that guards them

Credentials live in an enclave-only Vault container with no host port. Agent containers get **no broad Vault token** and, by default, no bind mount of your project — the workspace is a `git clone` from a per-project enclave mirror. The GitHub token never enters the agent container: the mirror holds short-lived role credentials, relays pushes on its behalf, and passes the credential on stdin rather than argv, closing a process-listing leak.

> GREEN: Credential separation is structural, not procedural — exfiltrating a token requires compromising the mirror *and* the proxy, because the mirror has no external route of its own.[^2]

> RED: The write path the agent pushes to is an anonymous `git daemon` receive-pack listener. The spec is blunt: network placement SHALL NOT be described as client authentication — any process on the enclave network can write to any mirror.
> PATH: The spec labels it *interim* and constrains what may be built on it, but records no dated authenticated replacement.[^16]

The host↔guest control channel can run a Noise handshake whose pre-shared key is derived by HKDF from the running binary's own SHA-256, domain-separated per hop and per release.[^17] Elegant version binding — but read what it authenticates, and whether it is on.

> RED: Two things weaken this below what the mechanism suggests. First, the handshake is **opt-in** — gated on an environment variable that defaults to off, which nothing in the shipped packaging sets — so the default posture is a plaintext control listener bound to accept any caller, unauthenticated. Second, even switched on it proves the peer runs *the same released binary*, not that the peer is the legitimate orchestrator: any local process holding a copy of the shipped binary derives the same key.[^18]
> PATH: Both are recorded and staged. The default-off flag is rung M1 of an active maturity ladder that advances through per-platform evidence gates to secure-by-default and finally to deleting the plaintext path; the project sits on that first rung.[^19] The key hardening — mixing in a per-boot host secret so a leaked release secret alone no longer lets a matching binary attach — is written, approved, deferred, unimplemented.[^20]

## Supply chain

> GREEN: Release artifacts are signed with Sigstore cosign keyless — no long-lived key, identity asserted by the CI OIDC token, inclusion recorded in a public transparency log — and every advertised asset is checked for transitive coverage.[^21]

> RED: The signature proves less than it looks like. Verification matches an identity regexp pinning only the repository *name* — not the owning organization, the workflow, or the ref — so a fork of the same name signing through the same CI provider satisfies it.[^21] Beyond that there is no SBOM, no build-provenance attestation, no SLSA or in-toto predicate, no container-image signing; base images are pinned by mutable tag rather than digest, so the image you build tomorrow is not the one you built today.[^22]
> PATH: Recorded only as research — a study of another distribution channel shows such provenance verifies with no verifier identity at all, and recommends shipping bundles plus a pinned root. Nothing has been adopted here.[^23]

## Ephemerality as a control — and its limit

@fig:ephemeral

Agent containers are `--rm`; scratch space, runtime dirs and the reference corpus are tmpfs; browser profiles die with the window. What persists is the interesting part: the per-project git mirror (the only durable copy of committed work), the tool cache, the Vault data volume, and — critically — the Vault unseal share, in the **host OS keychain**.[^24] Ephemerality resets *compute*, not *identity*.

> RED: On Linux the documented full-reset command is not credential-cold. A "pristine" re-initialization recovered an unseal share dated months earlier from the host keychain and preserved the existing data volume — so the vault re-initialization path the smoke test claims to exercise has never actually run there. Two hosts held shares of different ages, ruling out a shared fixture.
> PATH: Filed as an open defect, framed honestly in the release notes: the gap predates the release that found it, which is simply the first whose validation looked.[^25]

> GREEN: The mirror-image Windows failure — a stale keychain share bricking login after a wipe — was fixed across all three wipe paths, and the ticket was deliberately **left open** rather than closed on a technicality, because the fix only helps hosts that wipe *after* upgrading.[^25]

## Agent autonomy and auditability

Agents execute only inside containers; no host-side agent binary is permitted, and the host does orchestration, terminal spawning, and Podman management.

> GREEN: The one MCP surface that lets a contained agent drive a *host* browser ships with arbitrary JavaScript evaluation **disabled** — the tool is advertised but returns an explicit refusal, so it is visible without being live.[^26]

The audit trail — issue files, attestations, a plan index — is committed and unusually candid. It is also agent-self-reported and unsigned, with no commit signing evidenced: a tree once passed as green while red, and the repo calls its own fix unforgeable by accident, not by intent.

## What the assurance claim actually is

The method holds two invariants worth taking seriously: verification claims must be falsifiable, and evidence is not proof.[^27] The score driving "is this done" is a **bounded ranking function** over a finite lattice of obligation states — the shape of a termination argument, not a confidence estimate; the methodology states outright that these numbers are **not probabilities**.[^28]

Convergence is asymptotic across releases, not terminal within one. With $T_v$ the specifications at version $v$, $I_v$ the implementation, $d_v = d(I_v, T_v) \ge 0$:

$$d_{v+1} \le d_v \implies d_v \to d_* \ge 0$$

Because the specifications themselves move, non-increase gives convergence to a floor — it **does not prove $d_* = 0$**. Within one release the bar is fixed and refinement is idempotent, $\mathrm{refine}(\mathrm{refine}(x)) = \mathrm{refine}(x)$, which is what makes "done" decidable. Banach-style contraction — a metric, operator $F$, constant $0 \le c < 1$ with $d(F(x), F(y)) \le c\,d(x,y)$ — is **explicitly not claimed**.[^28]

The translation: a passing suite is a bounded ranking signal over the defects someone thought to write a litmus test for — and, as the hardening case shows, only those whose tests can actually fail. Finite litmus coverage is not proof of absence of defects; the repo says so before you do.

## Footnotes

[^1]: No project-operated backend, no telemetry | PRIVACY.md
[^2]: Enclave architecture — attack scenarios and stated limits | docs/cheatsheets/enclave-architecture.md#L217-L225
[^3]: Podman the only host dependency on Linux; macOS/Windows provision a VM | README.md#L52-L53
[^4]: The mandatory hardening envelope and the argv policy checker | crates/tillandsias-podman/src/policy.rs#L14-L22
[^5]: SELinux MCS labelling recorded as a planned future phase | openspec/specs/default-image/spec.md#L743
[^6]: The only production call of the policy checker is a `debug_assert!`, compiled out of release builds; the flags themselves are conditional struct fields | crates/tillandsias-podman/src/container_spec.rs#L376-L383
[^7]: Litmus steps ending `|| echo '<SUCCESS_TOKEN>'` — the same token on both branches | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L30-L53
[^8]: The false-pass scanner: advisory, no caller gates on it, skips over half the corpus, keyed on a non-zero exit | scripts/scan-litmus-false-pass.sh#L1-L41
[^9]: Escape lands as the invoking user's UID on the host | openspec/specs/podman-idiomatic-patterns/spec.md#L201-L203
[^10]: Internal enclave network, no external route | openspec/specs/enclave-network/spec.md#L17-L23
[^11]: Peek at step 1, bump one exact hostname, splice everything else | images/proxy/squid.conf#L109-L124
[^12]: Upstream verification retained; standing order against disabling it | images/proxy/squid.conf#L75-L81
[^13]: Host-side CA re-clamp, with the reasoning for why a code fix was only half the job | scripts/clamp-ca-material.sh#L1-L28
[^14]: Spec: per-launch EC P-256 root-and-intermediate chain on tmpfs | openspec/specs/proxy-container/spec.md#L63-L74
[^15]: What the code actually generates: one self-signed RSA-2048 30-day CA in a temp directory | scripts/orchestrate-enclave.sh#L95-L120
[^16]: Anonymous receive-pack listener; network placement is not authentication | openspec/specs/git-mirror-service/spec.md#L53-L68
[^17]: Noise PSK derived from the binary's own hash | crates/tillandsias-secure-channel/src/lib.rs#L64-L101
[^18]: The secure control wire is gated on an env var whose absent and empty values both resolve to Off | crates/tillandsias-headless/src/vsock_server.rs#L83-L106
[^19]: The maturity ladder from default-OFF to secure-by-default to removing the plaintext path — status active | plan/issues/secure-channel-maturity-ladder-2026-07-04.md#L1-L12
[^20]: Per-boot key hardening — approved, deferred, unimplemented | plan/issues/encrypted-channel-perboot-key-hardening-2026-07-01.md#L1-L22
[^21]: Keyless signing, and the verification identity regexp that pins the repo name only | .github/workflows/release.yml#L325-L326
[^22]: Base images pinned by mutable tag | images/git/Containerfile#L19-L21
[^23]: Sigstore/in-toto provenance studied for another channel, not adopted here | plan/issues/homebrew-harness-distribution-research-2026-07-11.md#L28-L29
[^24]: Vault unseal share stored in the host OS keychain | openspec/specs/tillandsias-vault/spec.md#L85-L91
[^25]: Release notes: the non-credential-cold Linux reset, and the deliberately-open Windows ticket | README.md#L115
[^26]: Arbitrary JavaScript evaluation disabled in v1 | openspec/specs/host-browser-mcp/spec.md#L387-L404
[^27]: Falsifiability and evidence-is-not-proof invariants | methodology/philosophy.yaml#L48-L50
[^28]: Bounded ranking function, explicitly not a probability; Banach contraction not claimed | methodology/math-foundations.yaml#L91-L125
