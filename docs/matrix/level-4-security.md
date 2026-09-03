# Tillandsias, for an IT / security reader

## Where the boundary actually is

The anatomy does not answer the security question: *when an agent does something you did not intend, how far does it get?*

First, a correction. The region was described as one Fedora guest — a VM, or WSL2 on Windows. True on two platforms, false on the third: **Linux provisions no VM**, and the orchestrator drives rootless containers directly on your host.[^1] The enclave is a hypervisor boundary on macOS and Windows, a namespace boundary on Linux — where an escape lands as your own uid, with your `$HOME`.[^2]

> GREEN: The threat model is written down in the project's own voice, including the parts that make it look bad — the architecture notes state plainly that the allowlist is generous by design and that an attacker can encode data in DNS queries or headers to an allowed domain.[^3]

Inside, every launch is meant to carry four flags — userns mapped to your uid, all capabilities dropped, no-new-privileges, and label-disable, which is to say **SELinux labelling off on every container** — audited by a policy module that rejects privileged mode, a non-identity userns, or a blanket capability add.[^4] Read that envelope as *defaults on a struct*, not an invariant.

> RED: The requirement that the hardening flags are immutable has no production enforcement. Each flag is emitted only if its boolean field is true, and the one place that checks the assembled command line is a debug assertion — compiled out of every release build.[^6] In a shipped binary, a caller that turns a flag off or adds back a capability is not stopped, or even logged. The test covering it is worse than absent: five of its eight steps echo their own success token on the failure branch, printing `CAP_DROP_ALL_SET` whether the inspection found the flag or not — structurally incapable of going red. And the container it inspects is one the test itself launched with the flags typed on the command line, so even the steps that can fail are testing Podman, not Tillandsias.[^7]
> PATH: Partial, and it does not reach this file. A scanner for litmus steps that pass while failing exists, but it is explicitly advisory with nothing gating on it, skips over half the corpus as not provably read-only, and keys on a non-zero exit — which `|| echo` suppresses, leaving it blind to this exact variant.[^8] A separately approved bar-raise on litmus quality is diff-scoped and, in the project's own words, structurally incapable of flagging the existing corpus.

> NOTE: The defect is contained, not systemic. Sweeping all 415 litmus files for the same-token-on-both-branches pattern returns five occurrences, and all five are in this one file — so the remedy is one file plus a scanner rule, not a corpus-wide audit.

> RED: SELinux confinement is disabled with no compensating control, so on a Fedora or RHEL host you are *less* confined than a default container would be.
> PATH: MCS labelling is recorded as a planned later phase — intent, with no implementation and no litmus behind it.[^5] For the missing hypervisor on Linux nothing is recorded at all: a design choice, mitigated by defence in depth rather than a stronger boundary.

## Egress: intercepted versus passed through

The single door is enforced by **network placement plus proxy environment variables**, and nothing else — no iptables, no nftables, no packet filter anywhere. An agent can unset `HTTP_PROXY`; what stops it is that the namespace has nowhere to send the packet. Then the question everyone asks on hearing "trusted CA in the container":

@fig:gate

> GREEN: This is **not** a blanket MITM. The proxy peeks at the handshake and then splices — passes through undecrypted — everything but one exact hostname, GitHub's release-asset CDN, bumped so large binaries can be cached. Registries, GitHub's APIs and every auth endpoint stay end-to-end encrypted.[^9]

> GREEN: Where it does terminate TLS it still verifies upstream against the system trust store, and the config carries a standing written order never to disable peer or domain verification — that would hide a real origin MITM behind a proxy-issued certificate.[^10]

The cost of that restraint: with one host decrypted the proxy does **no payload inspection** — hostnames, not content — and its default-deny allowlist admits anyone-can-publish namespaces, so an allowlist hit is no evidence of a benign destination.[^3] Egress control here is a routing property, not a content one.

> RED: Extending the world-readable proxy CA key flagged earlier: the code fix is not the whole fix. It lives in the tray binary, and every host runs a pre-fix release, so two machines were found still carrying a world-readable CA key days after the issue was marked closed — a fleet-versus-repo gap, not a code gap.
> PATH: An idempotent host-side repair script exists — it clamps the directory before the key to avoid a traversal window and heals material the old binary created. That is the remediation until a release ships with the code fix.[^11]

> RED: The published proxy spec describes something the code does not do: a fresh two-level EC P-256 chain generated per launch, held only on tmpfs, no CA key ever touching disk.[^12] The shipped code generates one self-signed RSA-2048 certificate with a 30-day life into a temp directory, reused across restarts.[^13]
> PATH: No path to green is recorded in the repo — the spec has not been marked stale, and no change proposal reconciles it with the implementation.

## Secrets, and the channel that guards them

The GitHub token never enters the agent container: the mirror holds short-lived role credentials, relays pushes on the agent's behalf, and passes the credential on stdin rather than argv, closing a process-listing leak.

> GREEN: Credential separation is structural, not procedural — exfiltrating a token requires compromising the mirror *and* the proxy, because the mirror has no external route of its own.[^3]

> RED: The write path the agent pushes to is an anonymous `git daemon` receive-pack listener. The spec is blunt: network placement SHALL NOT be described as client authentication — any process on the enclave network can write to any mirror.
> PATH: The spec labels it *interim* and constrains what may be built on it, but records no dated authenticated replacement.[^14]

The host↔guest control channel can run a Noise handshake keyed by HKDF from the running binary's own SHA-256, domain-separated per hop and release.[^15] Elegant version binding — but read what it authenticates, and whether it is on.

> RED: Two things weaken this below what the mechanism suggests. First, the handshake is **opt-in** — gated on an environment variable that defaults to off, which nothing in the shipped packaging sets — so the default posture is a plaintext control listener bound to accept any caller, unauthenticated. Second, even switched on it proves the peer runs *the same released binary*, not that the peer is the legitimate orchestrator: any local process holding a copy of the shipped binary derives the same key.[^16]
> PATH: Both are recorded and staged. The default-off flag is rung M1 of an active maturity ladder that advances through per-platform evidence gates to secure-by-default and finally to deleting the plaintext path; the project sits on that first rung.[^17] The key hardening — mixing in a per-boot host secret so a leaked release secret alone no longer lets a matching binary attach — is written, approved, deferred, unimplemented.[^18]

## Supply chain and provenance

> GREEN: Release artifacts are signed with Sigstore cosign keyless — no long-lived key, identity asserted by the CI OIDC token, inclusion recorded in a public transparency log — and every advertised asset is checked for transitive coverage.[^19]

> RED: The signature proves less than it looks like. Verification matches an identity regexp pinning only the repository *name* — not the owning organization, the workflow, or the ref — so a fork of the same name signing through the same CI provider satisfies it.[^19] Beyond that there is no SBOM, no build-provenance attestation, no SLSA or in-toto predicate, no container-image signing; base images are pinned by mutable tag rather than digest, so the image you build tomorrow is not the one you built today.[^20]
> PATH: Recorded only as research — a study of another distribution channel shows such provenance verifies with no verifier identity at all, and recommends shipping bundles plus a pinned root. Nothing has been adopted here.[^21]

## Where ephemerality stops being a control

Ephemerality resets *compute*, not *identity*. Of what survives teardown, the security-relevant item is the Vault unseal share, which lives in the **host OS keychain** — outside every boundary the enclave draws.[^22] Destroying the region does not destroy the ability to open what it held.

> RED: On Linux the documented full-reset command is not credential-cold. A "pristine" re-initialization recovered an unseal share dated months earlier from the host keychain and preserved the existing data volume — so the vault re-initialization path the smoke test claims to exercise has never actually run there. Two hosts held shares of different ages, ruling out a shared fixture.
> PATH: Filed as an open defect, framed honestly in the release notes: the gap predates the release that found it, which is simply the first whose validation looked.[^23]

## Blast radius, autonomy, auditability

An agent's reach: its forge, every mirror on the enclave network, any allowlisted hostname with nothing inspecting the payload. Not your keychain, `$HOME`, or real checkout — unless you took the host-mount escape hatch.

> GREEN: The one MCP surface that lets a contained agent drive a *host* browser ships with arbitrary JavaScript evaluation **disabled** — the tool is advertised but returns an explicit refusal, so it is visible without being live.[^24]

The audit trail is committed and unusually candid. It is also agent-self-reported and unsigned, with no commit signing evidenced: a tree once passed green while red, and the repo calls its own fix unforgeable by accident, not by intent. With nothing validating a push server-side either, the record's provenance rests on the honesty of the process that wrote it.

## What the assurance claim actually is

The convergence argument you already have is not a security argument, and the project does not offer it as one. What carries the weight is a pair of invariants — verification claims must be falsifiable, and evidence is not proof[^25] — plus the methodology's refusal to read its completion score as a probability.[^26] So: a passing suite is a bounded signal over the defects someone thought to write a litmus test for, and, as the hardening case shows, only over those whose tests can fail. Finite litmus coverage is not proof of absence of defects; the repo says so before you do.

## Footnotes

[^1]: Podman the only host dependency on Linux; macOS/Windows provision a VM | README.md#L52-L53
[^2]: Escape lands as the invoking user's UID on the host | openspec/specs/podman-idiomatic-patterns/spec.md#L201-L203
[^3]: Enclave architecture — attack scenarios and stated limits | docs/cheatsheets/enclave-architecture.md#L217-L225
[^4]: The mandatory hardening envelope and the argv policy checker | crates/tillandsias-podman/src/policy.rs#L14-L22
[^5]: SELinux MCS labelling recorded as a planned future phase | openspec/specs/default-image/spec.md#L743
[^6]: The only production call of the policy checker is a `debug_assert!`, compiled out of release builds; the flags themselves are conditional struct fields | crates/tillandsias-podman/src/container_spec.rs#L376-L383
[^7]: Litmus steps ending `|| echo '<SUCCESS_TOKEN>'` — the same token on both branches | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L30-L53
[^8]: The false-pass scanner: advisory, no caller gates on it, skips over half the corpus, keyed on a non-zero exit | scripts/scan-litmus-false-pass.sh#L1-L41
[^9]: Peek at step 1, bump one exact hostname, splice everything else | images/proxy/squid.conf#L109-L124
[^10]: Upstream verification retained; standing order against disabling it | images/proxy/squid.conf#L75-L81
[^11]: Host-side CA re-clamp, with the reasoning for why a code fix was only half the job | scripts/clamp-ca-material.sh#L1-L28
[^12]: Spec: per-launch EC P-256 root-and-intermediate chain on tmpfs | openspec/specs/proxy-container/spec.md#L63-L74
[^13]: What the code actually generates: one self-signed RSA-2048 30-day CA in a temp directory | scripts/orchestrate-enclave.sh#L95-L120
[^14]: Anonymous receive-pack listener; network placement is not authentication | openspec/specs/git-mirror-service/spec.md#L53-L68
[^15]: Noise PSK derived from the binary's own hash | crates/tillandsias-secure-channel/src/lib.rs#L64-L101
[^16]: The secure control wire is gated on an env var whose absent and empty values both resolve to Off. Six files under `crates/` read, document or log this variable; none of them, and nothing in packaging or the installers, sets it | crates/tillandsias-headless/src/vsock_server.rs#L83-L106
[^17]: The maturity ladder from default-OFF to secure-by-default to removing the plaintext path — status active | plan/issues/secure-channel-maturity-ladder-2026-07-04.md#L1-L12
[^18]: Per-boot key hardening — approved, deferred, unimplemented | plan/issues/encrypted-channel-perboot-key-hardening-2026-07-01.md#L1-L22
[^19]: Keyless signing, and the verification identity regexp that pins the repo name only | .github/workflows/release.yml#L325-L326
[^20]: Base images pinned by mutable tag | images/git/Containerfile#L19-L21
[^21]: Sigstore/in-toto provenance studied for another channel, not adopted here | plan/issues/homebrew-harness-distribution-research-2026-07-11.md#L28-L29
[^22]: Vault unseal share stored in the host OS keychain | openspec/specs/tillandsias-vault/spec.md#L85-L91
[^23]: Release notes: the non-credential-cold Linux reset | README.md#L115
[^24]: Arbitrary JavaScript evaluation disabled in v1 | openspec/specs/host-browser-mcp/spec.md#L387-L404
[^25]: Falsifiability and evidence-is-not-proof invariants | methodology/philosophy.yaml#L48-L50
[^26]: Bounded ranking function, explicitly not a probability | methodology/math-foundations.yaml#L91-L125
