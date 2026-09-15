# Tillandsias, for an IT / security reader

## Where the boundary actually is

The anatomy does not answer the security question: *when an agent does something you did not intend, how far does it get?*

First, a correction. The region was described as one Fedora guest — a VM, or WSL2 on Windows. True on two platforms, false on the third: **Linux provisions no VM**, and the orchestrator drives rootless containers directly on your host.[^1] The promise is that this costs nothing but Podman; the price is that the enclave is a hypervisor boundary on macOS and Windows and a namespace boundary on Linux — where an escape lands as your own uid, with your `$HOME`.[^2]

> GREEN: The threat model is written down in the project's own voice, including the parts that make it look bad — the architecture notes state plainly that the allowlist is generous by design and that an attacker can encode data in DNS queries or headers to an allowed domain.[^3]

Inside, every launch is meant to carry four flags — userns mapped to your uid, all capabilities dropped, no-new-privileges, and label-disable, which is to say **SELinux labelling off on every container** — audited by a policy module that rejects privileged mode, a non-identity userns, or a blanket capability add.[^4][^98] Why this envelope: keep-id makes an escape land as you rather than root, and a checker that never runs Podman is one small place to ask whether a launch still carries it. The compromise is the fourth flag, bought so bind mounts work on an SELinux-enforcing host.[^92][^94] Read the envelope as *defaults on a struct*, not an invariant — and not quite every container: the vault adds one capability back, omits `--rm`, and never passes the checker at all.[^53]

> GREEN: Production hardening checks now survive release compilation: the checked serializer returns an error for a stripped envelope, and both attached and delegated forge launch paths refuse it.[^6][^55][^56][^57] The general capability-add escape hatch has also been removed from the typed container builder.[^27] Previously the check was only a debug assertion and the security litmus printed success on both branches; those defects are repaired in this stable release.[^7]

The litmus now derives its launch flags from the product's declared envelope.[^58] Its repaired user-namespace probe checks ownership of a host-owned mounted file, because inspecting the namespace label or comparing the process uid alone could give a misleading answer.[^100] That is evidence about the declared envelope and Podman on the tested host, not proof that every production launch uses it.

> RED: Enforcement is still incomplete across launch paths: proxy, mirror, observatorium and a host-browser launch assemble or serialize arguments without the policy check, and the Podman client accepts raw arguments.[^64][^90][^95][^96][^97] The typed builder retains private boolean fields, although its public constructor turns all four on and exposes no setters to turn them off.[^63] A separate test defect remains: the capability probe treats empty output as success without checking whether the inspection ran, so a failed `podman exec` can still print `CAPABILITIES_DROPPED`.[^101]
> PATH: The checked serializer and forge callers provide the existing enforcement mechanism; extending that mechanism to every launch remains unimplemented.[^55][^65] The build now rejects identical success/failure tokens across the litmus corpus,[^60][^61] but that narrow scanner does not catch the empty-output failure above.[^62] The older advisory scanner and diff-scoped quality rule also remain bounded instruments, not a clean bill of health for the existing corpus.[^8][^54]
> REFUTED: "The litmus proves every launch is hardened." It launches a probe from declared flags, leaving production call-site coverage to other checks; even its cleanup step reports success unconditionally.[^58][^59]

> RED: SELinux confinement is disabled on every forge, so on a Fedora or RHEL host the agent's container is *less* confined than a default one. The project does confine elsewhere — the vault carries a loadable policy module,[^50] the Windows guest embeds policies for the control daemon and the vault[^51] — but on a rootless Linux host the vault too runs unconfined.[^52]
> PATH: MCS labelling of the forge is recorded as a planned later phase — intent, with no implementation and no litmus behind it.[^5] For the missing hypervisor on Linux no design tradeoff is recorded, only the blast radius of an escape — your uid, your `$HOME`[^2] — mitigated by defence in depth rather than a stronger boundary.
> PLAUSIBLE: Defence in depth is argued layer by layer below; nothing demonstrates that the layers compose to bound an escape.

## Egress: intercepted versus passed through

The intended egress boundary is **network placement plus proxy environment variables**. The proxy configuration supplies hostname rules; it does not establish that the host or container networking stack uses no packet filters. An agent can unset `HTTP_PROXY`; what stops it is that the namespace has nowhere to send the packet. Then the question everyone asks on hearing "trusted CA in the container":

@fig:gate

> GREEN: This is **not** a blanket MITM. The proxy peeks at the handshake and then splices — passes through undecrypted — everything but one exact hostname, GitHub's release-asset CDN, bumped so large binaries can be cached. Registries, GitHub's APIs and every auth endpoint stay end-to-end encrypted.[^9]
> PROVEN: The policy is three lines of a config file you can read, and the bump is scoped to one client-requested server name.[^9]

> GREEN: Where it does terminate TLS it still verifies upstream against the system trust store, and the config carries a standing written order never to disable peer or domain verification — that would hide a real origin MITM behind a proxy-issued certificate.[^10]

The cost of that restraint: with one host decrypted the proxy does **no payload inspection** — hostnames, not content — and its default-deny allowlist admits anyone-can-publish namespaces, so an allowlist hit is no evidence of a benign destination.[^3][^30] What it buys is a denial that looks like a network fault: a refused runtime request gets a TCP reset, not a page to negotiate with — the config's behaviour; the spec still promises a 403.[^37][^38]

> RED: The proxy's second, permissive port is a reachable allowlist bypass. Squid listens on it on every interface,[^31] the rules allow every destination on it with no source restriction,[^32] and the spec says outright that domain filtering does not apply there.[^33] The config calls it a port that serves nobody, because no launcher points a proxy variable at it[^34] — but an agent can point its own, and network placement does not stop that: the proxy sits on the same network.
> PATH: No path to green is recorded for the bypass itself, only an operator decision — route image builds through the port, or delete it — open in the config[^35] and still open in the network audit.[^36]

> GREEN: The stable release now puts the CA bundle under per-user persistent state instead of `/tmp`, so reboot cleanup no longer removes its declared location.[^28][^43][^91] On Unix, new key material is clamped to owner-only before publication, and the existing-key path attempts the same repair; the non-Unix helper is a documented no-op.[^39][^40][^41] This addresses the code side of a defect whose earlier fix had not reached material already created on hosts.[^11]

> RED: Moving the directory does not make its permissions private by construction. The launcher still uses ordinary recursive directory creation, and the repair script remains part of preflight.[^102][^44] Historical installation reports establish that two hosts received the earlier key fix, not that every current host's material has been inspected.[^42]
> PATH: The recorded remedy is still to create the directory privately and retire or give a retirement condition to the repair script.[^45] The persistent-path change has landed; the stronger directory-permission guarantee has not. The script clamps the directory before the key to remove traversal by other users first.[^11]

> RED: The published proxy spec describes something the code does not do: a fresh two-level EC P-256 chain generated per launch, held only on tmpfs, no CA key ever touching disk.[^12] The shipped launcher generates one self-signed RSA-2048 certificate with a 30-day life, stored in persistent per-user state and reused until refresh is needed.[^13][^28][^102]
> PATH: No path to green is recorded in the repo — the spec has not been marked stale, and no change proposal reconciles it with the implementation.

## Secrets, and the channel that guards them

The GitHub token never enters the agent container: the mirror holds short-lived role credentials, relays pushes on the agent's behalf, and passes the credential on stdin rather than argv, closing a process-listing leak. One clause on the relay: it wires the GitHub helper for any HTTPS origin and the helper answers unconditionally,[^48][^49] so the origin decides where the token goes.

> GREEN: The mirror holds the upstream credential and mediates pushes; the agent-facing write path is separate from that credential-bearing relay.[^14][^48][^49]
> REFUTED: "Exfiltrating a token requires compromising both the mirror and the proxy." The architecture says this,[^3] but the proxy already forwards permitted destinations and exposes a permissive port. A compromised mirror could use those routes without compromising the proxy process.[^30][^31][^32] Network placement restricts routes; it does not prove that an allowed request cannot carry a secret.

> RED: The write path the agent pushes to is an anonymous `git daemon` receive-pack listener. The spec is blunt: network placement SHALL NOT be described as client authentication — any process on the enclave network can write to any mirror.[^14]
> PATH: The spec labels it *interim* and constrains what may be built on it, but records no dated authenticated replacement.[^14] That replacement is built and dark: an SSH-CA push lane exists in the mirror image and the launcher, behind an environment variable that defaults off and that nothing in shipped packaging sets.[^46][^47]

**Why the relay is bespoke, in security terms.** The design needs the upstream
credential to stay server-side *and* the push to be synchronously durable, and those
two requirements pull against the available tools. A managed push mirror holds the
credential and copies asynchronously, so it reports success before the copy lands; a
caching or redirecting git proxy relays synchronously but forwards the client's
credentials, dissolving the separation this section is about. The hook takes the
third option: it relays the proposed ref transaction upstream before accepting it
locally, so a client's success means the upstream durably accepted the same atomic
ref set.[^107]

That is a security property and not only a convenience. A false success is
indistinguishable, to the agent that received it, from work that is safely
published — so an asynchronous mirror would put unpublished work behind a
green light, on exactly the disposable machine the design expects to be thrown
away.

> NOTE: This says what the relay refuses to report, not that the credential
> boundary is complete. The RED above about the anonymous receive-pack listener is
> the live gap on the agent-facing side of the same path, and it is not closed by
> anything in this paragraph.

The host↔guest control channel now uses a Noise handshake by default. Its key is derived through HKDF from the guest binary's SHA-256, separated by build version, wire version and hop.[^15][^103] This binds compatibility to known release material; it is not remote attestation that the peer runs unmodified code.

> GREEN: An absent secure-wire setting now selects encryption, blank or invalid values are refused, and the Windows tray uses the same parser as the other callers.[^16][^66][^67][^69] The earlier listener-only flip was reverted before the shared decision landed; a source scanner now allows zero independent readers.[^68] The macOS host writes the resulting value into the guest unit.[^93] Windows and the VM image need no explicit environment line to obtain the new default from the listener.[^70][^71]

A release exposed a second boundary: the tray and guest are different executables, so hashing each process's own binary produced different keys even at the same version. The host now derives its key from the guest digest embedded at build time, while the guest hashes itself.[^103][^104] The Windows caller refuses a missing embedded digest and includes tests for matching and mismatched guest digests.[^105][^106] A one-process round-trip test could never have detected the original two-binary mismatch; that limitation is now recorded beside the implementation.[^104]

> RED: Encryption is on by default, but caller identity remains weaker than operator authentication: anyone with the published guest bytes and version inputs can derive the same key. The guest's debug path instead uses a public constant.[^15][^29][^103] Explicit `off` still enables plaintext.[^16] Neither possession of the digest nor a completed handshake proves the caller is the legitimate orchestrator.
> PATH: The maturity ladder still records deletion of the insecure path as a later stage.[^17] Mixing in a per-boot host secret is approved and deferred; the present derivation does not include it.[^18][^103]

## Supply chain and provenance

> GREEN: Release artifacts are signed with Sigstore cosign keyless — no long-lived key, identity asserted by the CI OIDC token, inclusion recorded in a public transparency log — and the Linux and Windows asset sets are checked for transitive coverage as a property over whatever is staged, not over a remembered list.[^19][^72][^74]

> RED: The signature proves less than it looks like. Verification matches an identity regexp pinning only the repository *name* — not the owning organization, the workflow, or the ref — so a fork of the same name signing through the same CI provider satisfies it, in the published command and in the shipped verifier alike.[^19][^78] Beyond that there is no SBOM, no build-provenance attestation, no SLSA or in-toto predicate, no container-image signing; base images are pinned by mutable tag rather than digest, so the image you build tomorrow is not the one you built today.[^20]
> PATH: Recorded only as research — a study of another distribution channel shows such provenance verifies with no verifier identity at all, and recommends shipping bundles plus a pinned root.[^21][^80] Nothing has been adopted here.

> RED: The macOS lane is the exception: it signs an allow-list of three named assets and runs no integrity check, so its checksum manifest ships without a bundle[^73] — the allow-list shape the Windows lane's own comment blames for an installer once shipping bare.[^74]
> PATH: No path to green is recorded in the repo.

> RED: Nothing a user runs by default checks a signature; only the hand-run verifier does. The install scripts fetch the checksum manifest over the same channel as the binary and on Linux continue without it;[^75][^76][^77] no install path verifies a cosign bundle, and the updater's spec asks for no verification.[^79]
> PATH: No path to green is recorded in the repo.

## Where ephemerality stops being a control

Ephemerality resets *compute*, not *identity*. Of what survives teardown, the security-relevant item is the Vault unseal share, which lives in the **host OS keychain** — outside every boundary the enclave draws.[^22] The reason is fair — no passphrase prompt, never wipe a vault the host can still open — but destroying the region does not destroy the ability to open what it held.

> RED: On Linux the documented full-reset command is not credential-cold. A "pristine" re-initialization recovered an unseal share dated months earlier from the host keychain and preserved the existing data volume — so the vault re-initialization path the smoke test claims to exercise has never actually run there. Two hosts held shares of different ages, ruling out a shared fixture.[^23] The one-command reset fares no better: it wipes containers, secrets and the vault's storage but never touches the keychain entry.[^81][^82]
> PATH: Filed as an open defect, framed honestly in the release notes: the gap predates the release that found it, which is simply the first whose validation looked.[^23] A third host reproduced it on 2026-08-31;[^89] the packet's deliverable is that the reset becomes credential-cold or the runbook stops claiming it is, and no fix has landed.[^88]

> RED: The keychain is not the only copy. Where no OS keyring is available the launcher writes the share to a plaintext file in its cache directory,[^83] inside a VM guest it writes that file unconditionally,[^84] nothing ever deletes it, and the "share present in keychain" check that preserves the old volume is satisfied by the file alone[^85][^86] — while the spec says every persistent on-disk copy is deleted immediately.[^87]
> PATH: No path to green is recorded in the repo.

## Blast radius, autonomy, auditability

An agent's reach: its forge, every mirror on the enclave network, any allowlisted hostname with nothing inspecting the payload. Not your keychain, `$HOME`, or real checkout — unless you took the host-mount escape hatch.

> GREEN: The one MCP surface that lets a contained agent drive a *host* browser ships with arbitrary JavaScript evaluation **disabled** — the tool is advertised but returns an explicit refusal, so it is visible without being live.[^24]

The audit trail is committed and unusually candid. It is also agent-self-reported and unsigned, with no commit signing evidenced: a tree once passed green while red, and the repo calls its own fix unforgeable by accident, not by intent.[^99] With nothing in this repo evidencing server-side validation of a push, the record's provenance rests on the honesty of the process that wrote it.

## What the assurance claim actually is

The convergence argument you already have is not a security argument, and the project does not offer it as one. What carries the weight is a pair of invariants — verification claims must be falsifiable, and evidence is not proof[^25] — plus the methodology's refusal to read its completion score as a probability.[^26] So: a passing suite is a bounded signal over the defects someone thought to write a litmus test for, and, as the hardening case shows, only over those whose tests distinguish the relevant failure from success. Finite litmus coverage is not proof of absence of defects; the repo says so before you do.

Security is one local target among several. An agent may add a check, a boundary or
an audit record to the shared repository, but that does not make the next change
independent, nor does it turn a passing security test into a statement about every
other target. The useful engineering loop is narrower: make the claimed boundary
explicit, try to break it, retain the evidence and record the counterexample when it
fails.[^25][^26]

> NOTE: Several shortcomings on this page carry the line *No path to green is recorded in the repo.* That sentence is written after looking, and it means what it says: the defect is described here and no remedy is written down anywhere in the project's plan. Those cases are now collected and tracked as a single entry, so a reader who wants to argue with one — or report it — has something to attach it to.[^108]

## Footnotes

[^1]: Podman the only host dependency on Linux; macOS/Windows provision a VM | README.md#L52-L53
    > Podman is the only host dependency on Linux (auto-detected). macOS and Windows provision a lightweight Fedora-based utility VM; no host Podman required.
[^2]: Escape lands as the invoking user's UID on the host, with `$HOME` only | openspec/specs/podman-idiomatic-patterns/spec.md#L209-L210
    > - **THEN** the escaped process runs as the invoking user's UID on the host, not as root - **AND** it has access only to `$HOME` and user-owned resources
[^3]: Enclave architecture — attack scenarios and stated limits | docs/cheatsheets/enclave-architecture.md#L217-L225
    > The proxy allowlist is generous by design — a determined attacker could encode data in DNS queries or HTTP headers to an allowed domain.
[^4]: The mandatory hardening envelope and the argv policy checker | crates/tillandsias-podman/src/policy.rs#L14-L22
    > pub const MANDATORY_HARDENING_FLAGS: [&str; 4] = [ "--userns=keep-id", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--security-opt=label=disable", ];
[^5]: SELinux MCS labelling recorded as a planned future phase | openspec/specs/default-image/spec.md#L768-L769
    > future release will apply SELinux MCS labels to the forge domain, adding mandatory access control at the boundary layer.
[^6]: Checked serialization refuses an invalid launch in every build profile | crates/tillandsias-podman/src/container_spec.rs#L377-L397
    > crate::policy::validate_launch_argv(&argv)?; Ok(argv)
[^7]: Historical false-pass defect and its corpus-wide guard | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L7-L13
    > Both branches printed what the harness was looking for, so the greps decided nothing
[^8]: The false-pass scanner: advisory, no caller gates on it, skips over half the corpus, keyed on a non-zero exit | scripts/scan-litmus-false-pass.sh#L1-L41
    > Advisory — no caller gates on it.
[^9]: Peek at step 1, bump one exact hostname, splice everything else | images/proxy/squid.conf#L109-L124
    > ssl_bump peek ssl_bump_step1 ssl_bump bump github_release_assets ssl_bump splice all
[^10]: Upstream verification retained; standing order against disabling it | images/proxy/squid.conf#L75-L82
    > verification MUST remain enabled. Never add DONT_VERIFY_PEER or DONT_VERIFY_DOMAIN: doing so would hide an origin MITM behind a proxy-issued certificate that enclave clients trust.
[^11]: Host-side CA re-clamp, with the reasoning for why a code fix was only half the job, and the two hosts found world-readable | scripts/clamp-ca-material.sh#L1-L28
    > Two hosts were found with a world-readable CA private key days after the packet closed
[^12]: Spec: per-launch EC P-256 root-and-intermediate chain on tmpfs | openspec/specs/proxy-container/spec.md#L63-L74
    > The system SHALL generate a fresh two-level CA chain on every proxy launch. The chain SHALL consist of a self-signed Root CA and an Intermediate CA signed by the root, both using EC P-256 keys. All key material SHALL be stored on tmpfs
[^13]: Launcher generates self-signed RSA-2048 CA with a 30-day life | crates/tillandsias-headless/src/main.rs#L3187-L3205
    > "req", "-x509", "-newkey", "rsa:2048",
[^14]: Anonymous receive-pack listener; network placement is not authentication; owners named, no date | openspec/specs/git-mirror-service/spec.md#L52-L72
    > Network placement SHALL NOT be described as client authentication: any enclave peer can still create or fast-forward refs and cause the privileged relay to carry them upstream.
[^15]: Noise PSK derived from the binary's own hash | crates/tillandsias-secure-channel/src/lib.rs#L112-L114
    > let exe = std::env::current_exe().expect("current_exe for self-hash"); let bytes = std::fs::read(&exe).expect("read self binary for hash"); Sha256::digest(&bytes).to_vec()
[^16]: Absent means encrypted; plaintext requires explicit off | crates/tillandsias-control-wire/src/secure_wire_mode.rs#L85-L131
    > Err(std::env::VarError::NotPresent) => Ok(SecureWireMode::On),
[^17]: The maturity ladder from default-OFF to secure-by-default to removing the plaintext path — status active | plan/issues/secure-channel-maturity-ladder-2026-07-04.md#L1-L12
    > implement the e2e encrypted socket channel in ALL places, enable it at runtime with a flag, then advance through STABLE VERIFIABLE MATURITY GATES to secure-by-default and finally to removal of the insecure path.
[^18]: Per-boot key hardening — approved, deferred, unimplemented | plan/issues/encrypted-channel-perboot-key-hardening-2026-07-01.md#L1-L22
    > This packet is the operator-approved **later hardening**: mix in a **per-boot secret** the host controls, so a leaked release secret alone no longer lets an attacker with a matching-release binary attach across a different VM boot.
[^19]: Keyless signing recorded in the Rekor transparency log, and the verification identity regexp that pins the repo name only | .github/workflows/release.yml#L320-L326
    > --certificate-identity-regexp "https://github.com/.*/tillandsias/"
[^20]: Base images pinned by mutable tag | images/git/Containerfile#L19-L21
    > FROM docker.io/hashicorp/vault:1.18 AS vault-agent FROM docker.io/library/alpine:3.20
[^21]: The ledger's finding that such provenance verifies with no verifier identity, and its recommendation of bundles plus a pinned root — status ready, not adopted | plan/index.yaml#L12575-L12575
    > verifying a Sigstore/SLSA attestation requires NO identity from the verifier. Reproduced with no token, no gh config, and inside a network namespace with no interface at all: exit 0, real certificate chain, correct signer; one flipped byte gives exit 1.
[^22]: Vault unseal share stored in the host OS keychain | openspec/specs/tillandsias-vault/spec.md#L82-L91
    > The unseal key (the single Shamir share generated by Vault during initialization) SHALL be stored directly in the host OS's native secure keychain (Secret Service/KWallet on Linux, Credential Manager on Windows, Keychain on macOS) under the versioned name `vault-shamir-share-v1`.
[^23]: Release notes: the non-credential-cold Linux reset | README.md#L120-L120
    > Linux found its `podman system reset` is **not credential-cold** — Vault recovered a Shamir share dated 2026-06-15 and logged `preserving existing data volume`
[^24]: Host-browser tool dispatcher refuses arbitrary JavaScript evaluation | crates/tillandsias-browser-mcp/src/server.rs#L367-L379
    > "browser.eval" => Self::tool_error( id, "EVAL_DISABLED: browser.eval is disabled in v1; see follow-up change", ),
[^25]: Falsifiability and evidence-is-not-proof invariants | methodology/philosophy.yaml#L69-L71
    > - verification_claims_must_be_falsifiable: true - convergence_requires_stability: true - evidence_is_not_proof: true
[^26]: Bounded ranking function, explicitly not a probability | methodology/math-foundations.yaml#L91-L125
    > CentiColons are a finite bounded ranking function.
[^27]: General capability-add field and builder method removed | crates/tillandsias-podman/src/container_spec.rs#L85-L100
    > there is deliberately no `cap_add`. The field existed as an unvalidated pass-through
[^28]: Shared CA path accessor composes the ca leaf under the state root | crates/tillandsias-core/src/ca_path.rs#L37-L51
    > format!("{}/ca", ca_template())
[^29]: Debug builds derive the channel key from a fixed, public seed | crates/tillandsias-secure-channel/src/lib.rs#L63-L68
    > Fixed, non-secret dev seed used in debug builds. It lets a locally-built host + guest of the *same* tree interoperate without a release build. It is intentionally NOT a secret
[^30]: The allowlist table: package registries and cloud namespaces anyone can publish to | docs/cheatsheets/enclave-architecture.md#L144-L156
    > | Package registries | `registry.npmjs.org`, `crates.io`, `pypi.org`, `rubygems.org` | Package installation |
[^31]: The permissive port listens with no bind address, on every interface | images/proxy/squid.conf#L60-L64
    > http_port 3129 ssl-bump
[^32]: Permissive port: allow everything, no source restriction | images/proxy/squid.conf#L132-L134
    > http_access allow CONNECT SSL_ports build_port http_access allow build_port
[^33]: Spec: on the permissive port domain filtering does not apply | openspec/specs/proxy-container/spec.md#L114-L114
    > - **AND** domain filtering SHALL NOT apply
[^34]: The permissive port described as serving nobody | images/proxy/squid.conf#L9-L14
    > So this port listens, bumps, and serves nobody.
[^35]: The port is kept pending an operator decision, not deleted | images/proxy/squid.conf#L39-L44
    > That is an operator decision, not a cleanup. Until it is taken, this comment is the honest state.
[^36]: Network audit: the permissive-port decision still open | plan/issues/network-architecture-audit-2026-07-09.md#L531-L533
    > **STILL OPEN as a decision**, with the false claim removed and the agreement now enforced
[^37]: Denied runtime traffic gets a TCP reset rather than a 403 | images/proxy/squid.conf#L136-L141
    > Send a TCP reset instead of an HTTP 403 error for strictly-denied runtime traffic.
[^38]: The spec still promises an HTTP 403 for denied domains | openspec/specs/proxy-container/spec.md#L109-L109
    > - **AND** all other domains SHALL be denied with HTTP 403
[^39]: The owner-only clamp on the CA key, in the stable release's source | crates/tillandsias-headless/src/main.rs#L3077-L3079
    > fn enforce_ca_key_mode(key: &Path) -> std::io::Result<()> { use std::os::unix::fs::PermissionsExt; std::fs::set_permissions(key, std::fs::Permissions::from_mode(0o600))
[^40]: On non-unix targets the clamp is a documented no-op | crates/tillandsias-headless/src/main.rs#L3097-L3099
    > This is deliberately NOT a security regression on Windows: the key is not protected by mode bits there in the first place, and the enclave's Windows path receives it as a podman secret rather than through this file.
[^41]: Pre-fix keys are healed down to owner-only on every pass | crates/tillandsias-headless/src/main.rs#L3278-L3280
    > Heal DOWN to 0600 every call so keys generated before this fix (deliberately world-readable 0644) are repaired without requiring a CA rotation.
[^42]: Historical report that two hosts installed the earlier key fix | plan/index.yaml#L62096-L62099
    > esme and pirria just installed v56.9.2.1
[^43]: State root is persistent and explicitly shared between consumers | images/default/ca-path.txt#L1-L83
    > ${HOME}/.local/state/tillandsias
[^44]: The clamp script runs on every cycle preflight, best-effort | scripts/cycle-preflight.sh#L394-L394
    > bash "$ROOT/scripts/clamp-ca-material.sh" --fix >/dev/null 2>&1 || true
[^45]: Filed packet: make the CA directory private by construction and retire the clamp | plan/index.yaml#L28430-L28430
    > scripts/clamp-ca-material.sh gains a retirement condition or is deleted
[^46]: The authenticated push lane is gated on an environment variable that defaults to off | crates/tillandsias-headless/src/main.rs#L10473-L10475
    > std::env::var("TILLANDSIAS_MIRROR_SSHD") .map(|v| v == "1") .unwrap_or(false)
[^47]: The mirror's sshd starts only behind that flag | images/git/entrypoint.sh#L440-L444
    > Behind TILLANDSIAS_MIRROR_SSHD=1 until the T11 staged migration flips the default.
[^48]: The relay wires the GitHub credential helper for any HTTPS origin | images/git/relay-refs.sh#L154-L183
    > case "$REMOTE_URL" in https://*)
[^49]: The helper answers unconditionally, without reading which host git asked about | images/git/git-credential-tillandsias.sh#L34-L37
    > We do not branch on it: this helper is wired per-invocation by the relay for one specific remote, so answering unconditionally is correct
[^50]: The vault container carries an embedded SELinux policy module | crates/tillandsias-headless/src/vault_bootstrap.rs#L2160-L2170
    > const VAULT_SELINUX_CIL: &str = include_str!("../../../images/selinux/vault_container.cil");
[^51]: The Windows guest embeds policies for the control daemon and the vault | crates/tillandsias-windows-tray/src/wsl_lifecycle.rs#L284-L284
    > const SELINUX_VAULT_TE: &str = include_str!("../../../images/selinux/tillandsias_vault.te");
[^52]: On a rootless Linux host the vault too runs unconfined | crates/tillandsias-headless/src/vault_bootstrap.rs#L2199-L2217
    > `label=disable` runs the vault container unconfined on the host
[^53]: The vault launch adds a capability back and omits `--rm` | crates/tillandsias-headless/src/vault_bootstrap.rs#L2407-L2416
    > "--cap-drop".into(), "ALL".into(), "--cap-add".into(), "IPC_LOCK".into(),
[^54]: The approved bar-raise on litmus quality is diff-scoped by construction | plan/index.yaml#L14790-L14790
    > the check is DIFF-SCOPED BY CONSTRUCTION (examines added steps in the outgoing change only) and is structurally incapable of flagging the existing corpus
[^55]: Serialising a launch now refuses an argv that violates the envelope, in every build profile | crates/tillandsias-podman/src/container_spec.rs#L393-L397
    > crate::policy::validate_launch_argv(&argv)?; Ok(argv)
[^56]: The attached forge launch refuses on a hardening violation | crates/tillandsias-headless/src/main.rs#L12137-L12137
    > "refusing to launch {container_name}: hardening envelope violation: {err}"
[^57]: The delegated launch path refuses too | crates/tillandsias-headless/src/main.rs#L11965-L11965
    > [security] refusing to launch delegated {container_name}: {err}
[^58]: The rewritten litmus derives its launch flags from the product's declared envelope | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L23-L25
    > So the launch argv is now DERIVED from the product's own declared envelope, `MANDATORY_HARDENING_FLAGS` in crates/tillandsias-podman/src/policy.rs
[^59]: The ninth step, cleanup, still prints its token unconditionally | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L131-L134
    > expected_behavior: "CLEANED"
[^60]: A second scanner refuses litmus steps that print the same token on both branches | scripts/check-litmus-steps-can-fail.sh#L5-L6
    > Refuse a litmus step whose success and failure branches print the SAME token, because such a step passes whether the system works or not.
[^61]: The build gate fails on it | build.sh#L3858-L3858
    > a litmus step prints the same token on success and failure
[^62]: The second scanner refuses only the identical-token shape, by design | scripts/check-litmus-steps-can-fail.sh#L26-L30
    > Only identical tokens are refused, because only then is the branch a decoration.
[^63]: Private flags initialized on; serialization remains conditional | crates/tillandsias-podman/src/container_spec.rs#L85-L130
    > userns_keep_id: true, cap_drop_all: true, no_new_privileges: true, label_disable: true,
[^64]: A host-browser container still launches through the unchecked serialiser | crates/tillandsias-headless/src/main.rs#L13318-L13318
    > let args = spec.build_run_args();
[^65]: The repo's own admission that enforcement depends on call order | crates/tillandsias-headless/src/main.rs#L11946-L11948
    > An invariant that depends on call order is one refactor from being false, and this one decides whether a container runs unhardened.
[^66]: The one shared reader of the flag: a blank value is refused | crates/tillandsias-control-wire/src/secure_wire_mode.rs#L85-L126
    > is set but empty. Blank does NOT mean
[^67]: Windows tray uses shared mode reader and refuses bad values | crates/tillandsias-windows-tray/src/hvsocket.rs#L74-L87
    > let mode = match tillandsias_control_wire::secure_wire_mode::secure_wire_mode() { Ok(mode) => mode, Err(err) => return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, err)), };
[^68]: Default flip history and zero-reader ratchet | scripts/check-secure-wire-single-reader.sh#L22-L40
    > BASELINE REACHED 0 AND THE FLIP LANDED (commit B).
[^69]: Test pins the encrypted default through the shared parser | crates/tillandsias-control-wire/src/secure_wire_mode.rs#L159-L165
    > parse_secure_wire_mode(Err(VarError::NotPresent)).unwrap(), SecureWireMode::On,
[^70]: The Windows guest's service unit carries no secure-wire line | crates/tillandsias-windows-tray/src/wsl_lifecycle.rs#L1852-L1853
    > Environment=TILLANDSIAS_VAULT_API_BASE_URL=https://vault:8200 {low_power_env}ExecStart=/usr/local/bin/tillandsias-headless --listen-vsock 42420
[^71]: The VM image's default service unit carries no environment at all | images/vm/bootstrap/20-tillandsias.sh#L92-L104
    > ExecStart=/usr/local/bin/tillandsias-headless --listen-vsock 42420
[^72]: The Linux lane asserts transitive coverage as a property over what is staged | .github/workflows/release.yml#L289-L293
    > This asserts the PROPERTY over whatever is actually staged, so an asset added later cannot slip through unverifiable just because nobody added a line for it.
[^73]: The macOS lane signs an allow-list of three assets, and its checksum manifest is not among them | .github/workflows/release.yml#L500-L517
    > for artifact in tillandsias-tray-*-macos-arm64.tar.gz Tillandsias.dmg install-macos.sh; do
[^74]: The Windows lane's coverage check, why it follows the transitive path, and the allow-list it blames for an installer shipping bare | .github/workflows/release.yml#L742-L772
    > The check follows the TRANSITIVE path rather than counting unsigned files
[^75]: The Linux installer fetches the manifest over the same channel and continues without it | scripts/install.sh#L226-L239
    > say "SHA256SUMS not available; skipping checksum verification."
[^76]: The Windows installer compares a hash from the fetched manifest only | scripts/install-windows.ps1#L370-L399
    > Say "Verifying SHA-256..."
[^77]: The macOS installer likewise | scripts/install-macos.sh#L106-L128
    > curl -fsSL "$SHA_URL" -o "$TMP/SHA256SUMS-macos"
[^78]: The shipped verifier uses the same repository-name-only regexp | scripts/verify.sh#L24-L25
    > CERTIFICATE_IDENTITY_REGEXP="https://github.com/.*/tillandsias/"
[^79]: The in-app updater's spec: artifact selection, no verification requirement | openspec/specs/update-system/spec.md#L1-L53
    > The updater SHALL select the correct artifact for the current platform and handle platform-specific execution constraints.
[^80]: Sigstore/in-toto provenance studied for another channel | plan/issues/homebrew-harness-distribution-research-2026-07-11.md#L27-L31
    > every bottle built by Homebrew CI carries a **Sigstore/in-toto build-provenance attestation** (SLSA Build L2)
[^81]: The one-command reset deletes only the vault's storage directory on the host side | crates/tillandsias-headless/src/main.rs#L8760-L8761
    > Host-side directories the reset deletes under the init cache dir. ONLY `vault-data` (the vault storage backend)
[^82]: Its credential-discard step removes podman secrets; no keychain call in the function | crates/tillandsias-headless/src/main.rs#L8844-L8845
    > Secrets (vault unseal share + TLS material, CA, github token) — the credential-discard half of the ephemeral doctrine.
[^83]: Where no keyring is available the share is written to a fallback file in the cache directory | crates/tillandsias-headless/src/vault_bootstrap.rs#L2903-L2925
    > using fallback file (expected in VM guest and headless environments)
[^84]: Inside a VM guest both fallback writes are always attempted | crates/tillandsias-headless/src/vault_bootstrap.rs#L1290-L1316
    > BOTH writes are always ATTEMPTED — a token failure must never skip the share, because the share is the half that arms the wipe.
[^85]: The "share present in keychain" check falls through to the file | crates/tillandsias-headless/src/vault_bootstrap.rs#L1345-L1372
    > Fallback: file (populated by keychain_set_blocking when keyring unavailable, e.g. in a VM guest or headless environment without D-Bus)
[^86]: The preserve guard and the log line the smoke runs observed | crates/tillandsias-headless/src/vault_bootstrap.rs#L2284-L2304
    > [tillandsias-vault] preserving existing data volume (Shamir share present in keychain)
[^87]: Spec: every persistent on-disk copy of the share is deleted immediately | openspec/specs/tillandsias-vault/spec.md#L101-L101
    > delete all persistent on-disk copies immediately
[^88]: The open packet: make the Linux reset credential-cold, or stop claiming it is | plan/index.yaml#L42956-L42956
    > the Linux reset is credential-cold, or the runbook stops claiming it is
[^89]: The third-host reproduction, recorded 2026-08-31 | plan/index.yaml#L43064-L43064
    > Reproduced on a THIRD host during the v0.4.260830.5 curl-install smoke
[^90]: The Podman client runs whatever argv it is handed, with no policy call | crates/tillandsias-podman/src/client.rs#L1008-L1011
    > let mut full_args = vec!["run".to_string()]; full_args.extend_from_slice(args); match self.execute(OperationKind::Container, &full_args).await {
[^91]: Why the CA directory moved: /tmp is volatile by design and swept on reboot | images/default/ca-path.txt#L36-L38
    > /tmp works everywhere and is the bug — volatile by design, cleared on reboot and swept by systemd-tmpfiles
[^92]: Why label=disable: no `:z`/`:Z` relabelling, so bind mounts work under SELinux hosts | openspec/specs/podman-orchestration/spec.md#L110-L110
    > no `:z` or `:Z` suffix is needed because `--security-opt=label=disable` disables SELinux confinement for the container process
[^93]: The macOS host writes the secure-wire flag into the guest's service unit | crates/tillandsias-vm-layer/src/vz.rs#L1067-L1067
    > Environment=TILLANDSIAS_SECURE_CONTROL_WIRE=__SECURE_CONTROL_WIRE__
[^94]: Why the flag is applied — SELinux relabelling would otherwise break the bind mount | docs/audits/browser-isolation-audit-2026-04-30.md#L58
    > | `--security-opt=label=disable` | ✅ | Required for Silverblue bind mounts |
[^95]: The observatorium web launch serialises without the policy call | crates/tillandsias-headless/src/main.rs#L11492-L11492
    > .build_run_args()
[^96]: The proxy launch is assembled as a raw argv the checker never sees | crates/tillandsias-headless/src/main.rs#L3431-L3431
    > fn build_proxy_run_args(certs_dir: &Path, image: &str) -> Vec<String> {
[^97]: The mirror launch is assembled the same way | crates/tillandsias-headless/src/main.rs#L4301-L4301
    > fn build_git_run_args(
[^98]: What the checker refuses beside a missing flag | crates/tillandsias-podman/src/policy.rs#L189-L193
    > if arg == "--privileged" || arg.starts_with("--privileged=") || flag_value(arg, next, "--userns").is_some_and(|value| value != "keep-id") || flag_value(arg, next, "--cap-add").is_some_and(|value| value == "ALL")
[^99]: The release notes' own account of a red tree landing under a green stamp, and the scope claimed for the fix | README.md#L122-L122
    > A green gate now issues a one-shot pass token naming the tree it validated, consumed on use; the incident replays verbatim as a test arm, and peeling the onion found three more bare writes (release-gates 20/20). Claimed scope: unforgeable by accident, not by intent.

[^100]: Ownership probe distinguishes keep-id from misleading inspect labels | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L41-L64
    > The bind-mounted file discriminates — 1000 with keep-id, 0 without

[^101]: Capability probe ignores command exit status before declaring success | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L111-L114
    > expected_behavior: "CAPABILITIES_DROPPED"

[^102]: CA directory creation uses ordinary create_dir_all, followed by refresh decision | crates/tillandsias-headless/src/main.rs#L3131-L3138
    > std::fs::create_dir_all(&certs_dir) .map_err(|e| format!("Failed to create CA directory: {e}"))?;

[^103]: Host derives the control key from the build-time guest digest | crates/tillandsias-secure-channel/src/lib.rs#L157-L182
    > derive_psk(guest_binary_sha256, build_version, wire_version, hop)

[^104]: Why single-process tests could not reveal the host/guest digest mismatch | crates/tillandsias-secure-channel/src/lib.rs#L205-L228
    > The only integration proof is two DISTINCT binaries: a release-built tray and the release guest reaching Ready on a real cold provision.

[^105]: Windows refuses an absent embedded guest digest | crates/tillandsias-windows-tray/src/hvsocket.rs#L25-L43
    > EMBEDDED_GUEST_SHA256.as_ref().ok_or_else(|| {

[^106]: Windows handshake negative control rejects a different guest digest | crates/tillandsias-windows-tray/src/hvsocket.rs#L525-L610
    > a_guest_digest_mismatch_is_refused_not_carried

[^107]: Local acceptance follows upstream acceptance, so a reported success is a durable one | images/git/pre-receive-hook.sh#L6-L8
    > Validates ledger YAML, then synchronously relays the proposed ref transaction
    > upstream before accepting it locally. A client success therefore means the
    > configured upstream has durably accepted the same atomic ref set.
[^108]: The entry tracking every shortcoming here for which no remedy is recorded | https://github.com/8007342/tillandsias/blob/linux-next/plan/index.d/20260915t215254z-1213-rbt9-website-found-fourteen-shortcomings-the-ledger-does-not-track-macuahuitl.yaml
