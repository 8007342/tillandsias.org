# Tillandsias, for an IT / security reader

## Where the boundary actually is

The anatomy does not answer the security question: *when an agent does something you did not intend, how far does it get?*

First, a correction. The region was described as one Fedora guest — a VM, or WSL2 on Windows. True on two platforms, false on the third: **Linux provisions no VM**, and the orchestrator drives rootless containers directly on your host.[^1] The promise is that this costs nothing but Podman; the price is that the enclave is a hypervisor boundary on macOS and Windows and a namespace boundary on Linux — where an escape lands as your own uid, with your `$HOME`.[^2]

> GREEN: The threat model is written down in the project's own voice, including the parts that make it look bad — the architecture notes state plainly that the allowlist is generous by design and that an attacker can encode data in DNS queries or headers to an allowed domain.[^3]

Inside, every launch is meant to carry four flags — userns mapped to your uid, all capabilities dropped, no-new-privileges, and label-disable, which is to say **SELinux labelling off on every container** — audited by a policy module that rejects privileged mode, a non-identity userns, or a blanket capability add.[^4] Why this envelope: keep-id makes an escape land as you rather than root, and a checker that never runs Podman is one small place to ask whether a launch still carries it. The compromise is the fourth flag, bought so bind mounts work on every host.[^92] Read the envelope as *defaults on a struct*, not an invariant — and not quite every container: the vault adds one capability back, omits `--rm`, and never passes the checker at all.[^53]

> RED: The requirement that the hardening flags are immutable has no production enforcement. Each flag is emitted only if its boolean field is true, a capability pass-through sits beside them,[^27] and the one place that checks the assembled command line is a debug assertion — compiled out of every release build.[^6] In a shipped binary, a caller that turns a flag off or adds back a capability is not stopped, or even logged. The test covering it is worse than absent: five of its eight steps echo their own success token on the failure branch, printing `CAP_DROP_ALL_SET` whether the inspection found the flag or not — structurally incapable of going red. And the container it inspects is one the test itself launched with the flags typed on the command line, so even the steps that can fail are testing Podman, not Tillandsias.[^7]
> REFUTED: "The litmus proves the flags are on." At this release the test cannot fail, so a pass says nothing about the flags.
> PATH: At the stable release the remedy is partial and does not reach this file: an advisory false-pass scanner that skips over half the corpus and keys on a non-zero exit, which `|| echo` suppresses,[^8] and a diff-scoped bar-raise on litmus quality that is, in the project's own words, structurally incapable of flagging the existing corpus.[^54] The fix landed in the daily channel on 2026-09-03 and 2026-09-04: serialising a launch now returns an error the caller cannot log past,[^55] both agent launch paths refuse a stripped argv,[^56][^57] the litmus derives its flags from the declared envelope and eight of its nine steps can now fail,[^58][^59] and a second scanner refuses same-token steps corpus-wide, failing the build gate.[^60][^61] Still left: the flags are booleans on a struct,[^63] the scanner sees only identical tokens,[^62] and the proxy, mirror, observatorium and at least one host-browser launch never pass through the check.[^64][^65][^90]

> NOTE: The defect is contained, not systemic. Sweeping the litmus corpus for the same-token-on-both-branches pattern returns five occurrences, all in this one file — so the remedy is one file plus a scanner rule, not a corpus-wide audit.

> RED: SELinux confinement is disabled on every forge with no compensating control there, so on a Fedora or RHEL host the agent's container is *less* confined than a default one. The project does confine elsewhere — the vault carries a loadable policy module,[^50] the Windows guest embeds policies for the control daemon and the vault[^51] — but on a rootless Linux host the vault too runs unconfined.[^52]
> PATH: MCS labelling of the forge is recorded as a planned later phase — intent, with no implementation and no litmus behind it.[^5] For the missing hypervisor on Linux no design tradeoff is recorded, only the blast radius of an escape — your uid, your `$HOME`[^2] — mitigated by defence in depth rather than a stronger boundary.
> PLAUSIBLE: Defence in depth is argued layer by layer below; nothing demonstrates that the layers compose to bound an escape.

## Egress: intercepted versus passed through

The single door is enforced by **network placement plus proxy environment variables**, and nothing else — no iptables, no nftables, no packet filter anywhere. An agent can unset `HTTP_PROXY`; what stops it is that the namespace has nowhere to send the packet. Then the question everyone asks on hearing "trusted CA in the container":

@fig:gate

> GREEN: This is **not** a blanket MITM. The proxy peeks at the handshake and then splices — passes through undecrypted — everything but one exact hostname, GitHub's release-asset CDN, bumped so large binaries can be cached. Registries, GitHub's APIs and every auth endpoint stay end-to-end encrypted.[^9]
> PROVEN: The policy is three lines of a config file you can read, and the bump is scoped to one client-requested server name.[^9]

> GREEN: Where it does terminate TLS it still verifies upstream against the system trust store, and the config carries a standing written order never to disable peer or domain verification — that would hide a real origin MITM behind a proxy-issued certificate.[^10]

The cost of that restraint: with one host decrypted the proxy does **no payload inspection** — hostnames, not content — and its default-deny allowlist admits anyone-can-publish namespaces, so an allowlist hit is no evidence of a benign destination.[^3][^30] What it buys is a denial that looks like a network fault: a refused runtime request gets a TCP reset, not a page to negotiate with — the config's behaviour; the spec still promises a 403.[^37][^38]

> RED: The proxy's second, permissive port is a reachable allowlist bypass. Squid listens on it on every interface,[^31] the rules allow every destination on it with no source restriction,[^32] and the spec says outright that domain filtering does not apply there.[^33] The config calls it a port that serves nobody, because no launcher points a proxy variable at it[^34] — but an agent can point its own, and network placement does not stop that: the proxy sits on the same network.
> PATH: No path to green is recorded for the bypass itself, only an operator decision — route image builds through the port, or delete it — open in the config[^35] and still open in the network audit.[^36]

> RED: Extending the world-readable proxy CA key flagged earlier: the code fix was not the whole fix. It lived in the tray binary, every host ran a pre-fix release for weeks, and two machines were found still carrying a world-readable key days after the issue was marked closed — a fleet-versus-repo gap, not a code gap.[^11] The stable release this page pins carries the fix and the fleet has installed it:[^42] the key is created owner-only and healed back down on every pass,[^39][^41] on Linux and macOS — the clamp is a documented no-op on Windows.[^40] The directory it lives in is still world-traversable `/tmp` at this release.[^28]
> PATH: The host-side repair script still runs on every preflight, clamping the directory before the key and healing material an old binary created;[^44] a filed packet asks for the directory to be private by construction and the script retired.[^45] The daily channel moved the directory out of `/tmp` into per-user state on 2026-09-04, after a reboot swept the old one.[^43][^91]

> RED: The published proxy spec describes something the code does not do: a fresh two-level EC P-256 chain generated per launch, held only on tmpfs, no CA key ever touching disk.[^12] The shipped code generates one self-signed RSA-2048 certificate with a 30-day life into a temp directory, reused across restarts.[^13]
> PATH: No path to green is recorded in the repo — the spec has not been marked stale, and no change proposal reconciles it with the implementation.

## Secrets, and the channel that guards them

The GitHub token never enters the agent container: the mirror holds short-lived role credentials, relays pushes on the agent's behalf, and passes the credential on stdin rather than argv, closing a process-listing leak. One clause on the relay: it wires the GitHub helper for any HTTPS origin and the helper answers unconditionally,[^48][^49] so the origin decides where the token goes.

> GREEN: Credential separation is structural, not procedural — exfiltrating a token requires compromising the mirror *and* the proxy, because the mirror has no external route of its own.[^3]

> RED: The write path the agent pushes to is an anonymous `git daemon` receive-pack listener. The spec is blunt: network placement SHALL NOT be described as client authentication — any process on the enclave network can write to any mirror.[^14]
> PATH: The spec labels it *interim* and constrains what may be built on it, but records no dated authenticated replacement.[^14] That replacement is built and dark: an SSH-CA push lane exists in the mirror image and the launcher, behind an environment variable that defaults off and that nothing in shipped packaging sets.[^46][^47]

The host↔guest control channel can run a Noise handshake keyed by HKDF from the running binary's own SHA-256, domain-separated per hop and release.[^15] Elegant version binding — a reported version can be faked, a key derived from the build cannot — but read what it authenticates, and whether it is on.

> RED: Two things weaken this below what the mechanism suggests. First, the handshake is **opt-in** — gated on an environment variable that defaults to off, which nothing in the shipped packaging sets — so the default posture is a plaintext control listener bound to accept any caller, unauthenticated.[^16] Only the macOS host writes the flag into the guest's service unit;[^93] the Windows guest's unit and the VM image's default unit carry no such line, so the guest listener is plaintext there whatever the host sets.[^70][^71] Second, even switched on it proves the peer runs *the same released binary*, not that the peer is the legitimate orchestrator: any local process holding a copy of the shipped binary derives the same key — and a debug build derives it from a public constant.[^29]
> PATH: Both are recorded and staged. The default-off flag is rung M1 of an active maturity ladder that advances through per-platform evidence gates to secure-by-default and finally to deleting the plaintext path; the project sits on that first rung.[^17] In the daily channel five of the flag's six divergent readers were collapsed into one shared reader that refuses a blank value,[^66] the sixth — the Windows tray — still parses it itself,[^67] a listener-only flip was reverted,[^68] and the ledger is silent on the flip since 2026-09-03.[^69] The key hardening — mixing in a per-boot host secret so a leaked release secret alone no longer lets a matching binary attach — is written, approved, deferred, unimplemented.[^18]

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

The audit trail is committed and unusually candid. It is also agent-self-reported and unsigned, with no commit signing evidenced: a tree once passed green while red, and the repo calls its own fix unforgeable by accident, not by intent. With nothing in this repo evidencing server-side validation of a push, the record's provenance rests on the honesty of the process that wrote it.

## What the assurance claim actually is

The convergence argument you already have is not a security argument, and the project does not offer it as one. What carries the weight is a pair of invariants — verification claims must be falsifiable, and evidence is not proof[^25] — plus the methodology's refusal to read its completion score as a probability.[^26] So: a passing suite is a bounded signal over the defects someone thought to write a litmus test for, and, as the hardening case shows, only over those whose tests can fail. Finite litmus coverage is not proof of absence of defects; the repo says so before you do.

## Footnotes

[^1]: Podman the only host dependency on Linux; macOS/Windows provision a VM | README.md#L52-L53
    > Podman is the only host dependency on Linux (auto-detected). macOS and Windows provision a lightweight Fedora-based utility VM; no host Podman required.
[^2]: Escape lands as the invoking user's UID on the host, with `$HOME` only | openspec/specs/podman-idiomatic-patterns/spec.md#L201-L204
    > - **THEN** the escaped process runs as the invoking user's UID on the host, not as root - **AND** it has access only to `$HOME` and user-owned resources
[^3]: Enclave architecture — attack scenarios and stated limits | docs/cheatsheets/enclave-architecture.md#L217-L225
    > The proxy allowlist is generous by design — a determined attacker could encode data in DNS queries or HTTP headers to an allowed domain.
[^4]: The mandatory hardening envelope and the argv policy checker | crates/tillandsias-podman/src/policy.rs#L14-L22
    > pub const MANDATORY_HARDENING_FLAGS: [&str; 4] = [ "--userns=keep-id", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--security-opt=label=disable", ];
[^5]: SELinux MCS labelling recorded as a planned future phase | openspec/specs/default-image/spec.md#L743-L744
    > future release will apply SELinux MCS labels to the forge domain, adding mandatory access control at the boundary layer.
[^6]: The only production call of the policy checker is a `debug_assert!`, compiled out of release builds | crates/tillandsias-podman/src/container_spec.rs#L376-L383
    > debug_assert!( crate::policy::validate_launch_argv(&argv).is_ok(),
[^7]: Litmus steps ending `|| echo '<SUCCESS_TOKEN>'` — the same token on both branches | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L30-L53
    > && echo 'CAP_DROP_ALL_SET' || echo 'CAP_DROP_ALL_SET'
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
[^13]: What the shell orchestrator actually generates: one self-signed RSA-2048 30-day CA under /tmp | scripts/orchestrate-enclave.sh#L95-L120
    > "$OPENSSL" req -x509 -newkey rsa:2048 -keyout "$CERTS_DIR/intermediate.key" \ -out "$CERTS_DIR/intermediate.crt" -days 30 -nodes
[^14]: Anonymous receive-pack listener; network placement is not authentication; owners named, no date | openspec/specs/git-mirror-service/spec.md#L52-L72
    > Network placement SHALL NOT be described as client authentication: any enclave peer can still create or fast-forward refs and cause the privileged relay to carry them upstream.
[^15]: Noise PSK derived from the binary's own hash | crates/tillandsias-secure-channel/src/lib.rs#L64-L101
    > let exe = std::env::current_exe().expect("current_exe for self-hash"); let bytes = std::fs::read(&exe).expect("read self binary for hash"); Sha256::digest(&bytes).to_vec()
[^16]: The secure control wire is gated on an env var whose absent and empty values both resolve to Off. Six files under `crates/` read, document or log this variable; none of them, and nothing in packaging or the installers, sets it | crates/tillandsias-headless/src/vsock_server.rs#L83-L106
    > Ok(v) if v.eq_ignore_ascii_case("off") || v.is_empty() => Ok(SecureControlWireMode::Off),
[^17]: The maturity ladder from default-OFF to secure-by-default to removing the plaintext path — status active | plan/issues/secure-channel-maturity-ladder-2026-07-04.md#L1-L12
    > implement the e2e encrypted socket channel in ALL places, enable it at runtime with a flag, then advance through STABLE VERIFIABLE MATURITY GATES to secure-by-default and finally to removal of the insecure path.
[^18]: Per-boot key hardening — approved, deferred, unimplemented | plan/issues/encrypted-channel-perboot-key-hardening-2026-07-01.md#L1-L22
    > This packet is the operator-approved **later hardening**: mix in a **per-boot secret** the host controls, so a leaked release secret alone no longer lets an attacker with a matching-release binary attach across a different VM boot.
[^19]: Keyless signing, and the verification identity regexp that pins the repo name only | .github/workflows/release.yml#L325-L326
    > --certificate-identity-regexp "https://github.com/.*/tillandsias/"
[^20]: Base images pinned by mutable tag | images/git/Containerfile#L19-L21
    > FROM docker.io/hashicorp/vault:1.18 AS vault-agent FROM docker.io/library/alpine:3.20
[^21]: The ledger's finding that such provenance verifies with no verifier identity, and its recommendation of bundles plus a pinned root — status ready, not adopted | plan/index.yaml#L12068-L12087
    > verifying a Sigstore/SLSA attestation requires NO identity from the verifier. Reproduced with no token, no gh config, and inside a network namespace with no interface at all: exit 0, real certificate chain, correct signer; one flipped byte gives exit 1.
[^22]: Vault unseal share stored in the host OS keychain | openspec/specs/tillandsias-vault/spec.md#L82-L91
    > The unseal key (the single Shamir share generated by Vault during initialization) SHALL be stored directly in the host OS's native secure keychain (Secret Service/KWallet on Linux, Credential Manager on Windows, Keychain on macOS) under the versioned name `vault-shamir-share-v1`.
[^23]: Release notes: the non-credential-cold Linux reset | README.md#L115
    > Linux found its `podman system reset` is **not credential-cold** — Vault recovered a Shamir share dated 2026-06-15 and logged `preserving existing data volume`
[^24]: Arbitrary JavaScript evaluation disabled in v1 | openspec/specs/host-browser-mcp/spec.md#L387-L404
    > In the v1 release, `browser.eval` SHALL appear in `tools/list` but every `tools/call` invocation SHALL return
[^25]: Falsifiability and evidence-is-not-proof invariants | methodology/philosophy.yaml#L48-L50
    > - verification_claims_must_be_falsifiable: true - convergence_requires_stability: true - evidence_is_not_proof: true
[^26]: Bounded ranking function, explicitly not a probability | methodology/math-foundations.yaml#L91-L125
    > CentiColons are a finite bounded ranking function.
[^27]: Each flag is emitted only when its boolean is set, and a capability pass-through field is serialised beside them | crates/tillandsias-podman/src/container_spec.rs#L293-L308
    > for cap in &self.cap_add { args.push("--cap-add".to_string()); args.push(cap.clone()); }
[^28]: The tray binary's CA directory at this release is a constant under /tmp | crates/tillandsias-headless/src/main.rs#L1628
    > const CA_DIR: &str = "/tmp/tillandsias-ca";
[^29]: Debug builds derive the channel key from a fixed, public seed | crates/tillandsias-secure-channel/src/lib.rs#L63-L68
    > Fixed, non-secret dev seed used in debug builds. It lets a locally-built host + guest of the *same* tree interoperate without a release build. It is intentionally NOT a secret
[^30]: The allowlist table: package registries and cloud namespaces anyone can publish to | docs/cheatsheets/enclave-architecture.md#L144-L156
    > | Package registries | `registry.npmjs.org`, `crates.io`, `pypi.org`, `rubygems.org` | Package installation |
[^31]: The permissive port listens with no bind address, on every interface | images/proxy/squid.conf#L60-L64
    > http_port 3129 ssl-bump
[^32]: Permissive port: allow everything, no source restriction | images/proxy/squid.conf#L132-L134
    > http_access allow CONNECT SSL_ports build_port http_access allow build_port
[^33]: Spec: on the permissive port domain filtering does not apply | openspec/specs/proxy-container/spec.md#L108-L111
    > - **AND** domain filtering SHALL NOT apply
[^34]: The permissive port described as serving nobody | images/proxy/squid.conf#L9-L14
    > So this port listens, bumps, and serves nobody.
[^35]: The port is kept pending an operator decision, not deleted | images/proxy/squid.conf#L39-L44
    > That is an operator decision, not a cleanup. Until it is taken, this comment is the honest state.
[^36]: Network audit: the permissive-port decision still open | plan/issues/network-architecture-audit-2026-07-09.md#L531-L533
    > **STILL OPEN as a decision**, with the false claim removed and the agreement now enforced
[^37]: Denied runtime traffic gets a TCP reset rather than a 403 | images/proxy/squid.conf#L136-L141
    > Send a TCP reset instead of an HTTP 403 error for strictly-denied runtime traffic.
[^38]: The spec still promises an HTTP 403 for denied domains | openspec/specs/proxy-container/spec.md#L103-L106
    > - **AND** all other domains SHALL be denied with HTTP 403
[^39]: The owner-only clamp on the CA key, in the stable release's source | crates/tillandsias-headless/src/main.rs#L3016-L3020
    > fn enforce_ca_key_mode(key: &Path) -> std::io::Result<()> { use std::os::unix::fs::PermissionsExt; std::fs::set_permissions(key, std::fs::Permissions::from_mode(0o600))
[^40]: On non-unix targets the clamp is a documented no-op | crates/tillandsias-headless/src/main.rs#L3037-L3043
    > This is deliberately NOT a security regression on Windows: the key is not protected by mode bits there in the first place, and the enclave's Windows path receives it as a podman secret rather than through this file.
[^41]: Pre-fix keys are healed down to owner-only on every pass | crates/tillandsias-headless/src/main.rs#L3197-L3204
    > Heal DOWN to 0600 every call so keys generated before this fix (deliberately world-readable 0644) are repaired without requiring a CA rotation.
[^42]: Hosts have installed the stable release that carries the fix | plan/index.yaml#L59706-L59707 @v56.9.5.1
    > esme and pirria just installed v56.9.2.1
[^43]: The daily-channel move of the CA bundle off /tmp, completed 2026-09-04 | plan/index.yaml#L57026-L57033 @v56.9.5.1
    > move the CA bundle off /tmp so a reboot stops making the proxy unrestartable
[^44]: The clamp script runs on every cycle preflight, best-effort | scripts/cycle-preflight.sh#L258-L259
    > bash "$ROOT/scripts/clamp-ca-material.sh" --fix >/dev/null 2>&1 || true
[^45]: Filed packet: make the CA directory private by construction and retire the clamp | plan/index.yaml#L26814-L26822
    > scripts/clamp-ca-material.sh gains a retirement condition or is deleted
[^46]: The authenticated push lane is gated on an environment variable that defaults to off | crates/tillandsias-headless/src/main.rs#L9708-L9714
    > std::env::var("TILLANDSIAS_MIRROR_SSHD") .map(|v| v == "1") .unwrap_or(false)
[^47]: The mirror's sshd starts only behind that flag | images/git/entrypoint.sh#L440-L444
    > Behind TILLANDSIAS_MIRROR_SSHD=1 until the T11 staged migration flips the default.
[^48]: The relay wires the GitHub credential helper for any HTTPS origin | images/git/relay-refs.sh#L154-L183
    > case "$REMOTE_URL" in https://*)
[^49]: The helper answers unconditionally, without reading which host git asked about | images/git/git-credential-tillandsias.sh#L34-L37
    > We do not branch on it: this helper is wired per-invocation by the relay for one specific remote, so answering unconditionally is correct
[^50]: The vault container carries an embedded SELinux policy module | crates/tillandsias-headless/src/vault_bootstrap.rs#L2160-L2170
    > const VAULT_SELINUX_CIL: &str = include_str!("../../../images/selinux/vault_container.cil");
[^51]: The Windows guest embeds policies for the control daemon and the vault | crates/tillandsias-windows-tray/src/wsl_lifecycle.rs#L180-L184
    > const SELINUX_VAULT_TE: &str = include_str!("../../../images/selinux/tillandsias_vault.te");
[^52]: On a rootless Linux host the vault too runs unconfined | crates/tillandsias-headless/src/vault_bootstrap.rs#L2199-L2217
    > `label=disable` runs the vault container unconfined on the host
[^53]: The vault launch adds a capability back and omits `--rm` | crates/tillandsias-headless/src/vault_bootstrap.rs#L2407-L2416
    > "--cap-drop".into(), "ALL".into(), "--cap-add".into(), "IPC_LOCK".into(),
[^54]: The approved bar-raise on litmus quality is diff-scoped by construction | plan/index.yaml#L14252-L14302
    > the check is DIFF-SCOPED BY CONSTRUCTION (examines added steps in the outgoing change only) and is structurally incapable of flagging the existing corpus
[^55]: Serialising a launch now refuses an argv that violates the envelope, in every build profile | crates/tillandsias-podman/src/container_spec.rs#L393-L397 @v56.9.5.1
    > crate::policy::validate_launch_argv(&argv)?; Ok(argv)
[^56]: The attached forge launch refuses on a hardening violation | crates/tillandsias-headless/src/main.rs#L11877-L11886 @v56.9.5.1
    > "refusing to launch {container_name}: hardening envelope violation: {err}"
[^57]: The delegated launch path refuses too | crates/tillandsias-headless/src/main.rs#L11711-L11713 @v56.9.5.1
    > [security] refusing to launch delegated {container_name}: {err}
[^58]: The rewritten litmus derives its launch flags from the product's declared envelope | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L23-L25 @v56.9.5.1
    > So the launch argv is now DERIVED from the product's own declared envelope, `MANDATORY_HARDENING_FLAGS` in crates/tillandsias-podman/src/policy.rs
[^59]: The ninth step, cleanup, still prints its token unconditionally | openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L131-L134 @v56.9.5.1
    > expected_behavior: "CLEANED"
[^60]: A second scanner refuses litmus steps that print the same token on both branches | scripts/check-litmus-steps-can-fail.sh#L5-L6 @v56.9.5.1
    > Refuse a litmus step whose success and failure branches print the SAME token, because such a step passes whether the system works or not.
[^61]: The build gate fails on it | build.sh#L3235-L3239 @v56.9.5.1
    > a litmus step prints the same token on success and failure
[^62]: The second scanner refuses only the identical-token shape, by design | scripts/check-litmus-steps-can-fail.sh#L26-L30 @v56.9.5.1
    > Only identical tokens are refused, because only then is the branch a decoration.
[^63]: The flags remain conditional booleans on the struct | crates/tillandsias-podman/src/container_spec.rs#L297-L307 @v56.9.5.1
    > if self.cap_drop_all { args.push("--cap-drop=ALL".to_string()); }
[^64]: A host-browser container still launches through the unchecked serialiser | crates/tillandsias-headless/src/main.rs#L13047 @v56.9.5.1
    > let args = spec.build_run_args();
[^65]: The repo's own admission that enforcement depends on call order | crates/tillandsias-headless/src/main.rs#L11694-L11696 @v56.9.5.1
    > An invariant that depends on call order is one refactor from being false, and this one decides whether a container runs unhardened.
[^66]: The one shared reader of the flag: a blank value is refused | crates/tillandsias-control-wire/src/secure_wire_mode.rs#L85-L126 @v56.9.5.1
    > is set but empty. Blank does NOT mean
[^67]: The Windows tray reads the flag itself and falls back to plaintext for any value but exactly on | crates/tillandsias-windows-tray/src/hvsocket.rs#L29-L41
    > if std::env::var("TILLANDSIAS_SECURE_CONTROL_WIRE").as_deref() == Ok("on") {
[^68]: The listener-only flip that broke every client, and the ratchet that holds the default until the last reader converts | scripts/check-secure-wire-single-reader.sh#L22-L39 @v56.9.5.1
    > the listener alone was flipped (e6a80609f) and every client, still defaulting to plaintext, was refused by the server it had just been told to trust. Reverted at 08a7d3cc7.
[^69]: The default-off packet, ready, with no event after 2026-09-03 | plan/index.yaml#L51828-L51872 @v56.9.5.1
    > ts: "2026-09-03T03:46:20Z"
[^70]: The Windows guest's service unit carries no secure-wire line | crates/tillandsias-windows-tray/src/wsl_lifecycle.rs#L1745-L1752
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
[^81]: The one-command reset deletes only the vault's storage directory on the host side | crates/tillandsias-headless/src/main.rs#L8264-L8270
    > Host-side directories the reset deletes under the init cache dir. ONLY `vault-data` (the vault storage backend)
[^82]: Its credential-discard step removes podman secrets; no keychain call in the function | crates/tillandsias-headless/src/main.rs#L8309-L8352
    > Secrets (vault unseal share + TLS material, CA, github token) — the credential-discard half of the ephemeral doctrine.
[^83]: Where no keyring is available the share is written to a fallback file in the cache directory | crates/tillandsias-headless/src/vault_bootstrap.rs#L2903-L2925
    > using fallback file (expected in VM guest and headless environments)
[^84]: Inside a VM guest both fallback writes are always attempted | crates/tillandsias-headless/src/vault_bootstrap.rs#L1290-L1316
    > BOTH writes are always ATTEMPTED — a token failure must never skip the share, because the share is the half that arms the wipe.
[^85]: The "share present in keychain" check falls through to the file | crates/tillandsias-headless/src/vault_bootstrap.rs#L1345-L1372
    > Fallback: file (populated by keychain_set_blocking when keyring unavailable, e.g. in a VM guest or headless environment without D-Bus)
[^86]: The preserve guard and the log line the smoke runs observed | crates/tillandsias-headless/src/vault_bootstrap.rs#L2284-L2304
    > [tillandsias-vault] preserving existing data volume (Shamir share present in keychain)
[^87]: Spec: every persistent on-disk copy of the share is deleted immediately | openspec/specs/tillandsias-vault/spec.md#L97-L100
    > delete all persistent on-disk copies immediately
[^88]: The open packet: make the Linux reset credential-cold, or stop claiming it is | plan/index.yaml#L39735-L39745
    > the Linux reset is credential-cold, or the runbook stops claiming it is
[^89]: The third-host reproduction, recorded 2026-08-31 | plan/index.yaml#L39848-L39853
    > Reproduced on a THIRD host during the v0.4.260830.5 curl-install smoke
[^90]: The Podman client runs whatever argv it is handed, with no policy call | crates/tillandsias-podman/src/client.rs#L1008-L1011 @v56.9.5.1
    > let mut full_args = vec!["run".to_string()]; full_args.extend_from_slice(args); match self.execute(OperationKind::Container, &full_args).await {
[^91]: Why the CA directory moved: /tmp is volatile by design and swept on reboot | images/default/ca-path.txt#L36-L38 @v56.9.5.1
    > /tmp works everywhere and is the bug — volatile by design, cleared on reboot and swept by systemd-tmpfiles
[^92]: Why label=disable: no `:z`/`:Z` relabelling, so bind mounts work under SELinux hosts | openspec/specs/podman-orchestration/spec.md#L103-L106
    > no `:z` or `:Z` suffix is needed because `--security-opt=label=disable` disables SELinux confinement for the container process
[^93]: The macOS host writes the secure-wire flag into the guest's service unit | crates/tillandsias-vm-layer/src/vz.rs#L837-L838
    > Environment=TILLANDSIAS_SECURE_CONTROL_WIRE=__SECURE_CONTROL_WIRE__
