# Findings for the Tillandsias runtime — 2026-09-05

These came out of the 2026-09-05 tillandsias.org explanation-page audit, which
re-verified every claim on `docs/matrix/level-1..5.md` against two runtime
checkouts: `v56.9.2.1` (the stable release the pages pin) and `v56.9.5.1` (the
newest daily). Everything below belongs to `github.com/8007342/tillandsias`, not
to this site, and every entry was re-read at the tag it names by the author of
this file — the audit JSON was a lead, never a citation. This forge holds no
GitHub credential by design (see `skills/file-findings/SKILL.md`), so filing is
a relay: paste each `##` section into `gh issue create --repo 8007342/tillandsias
--title <the heading> --body-file <the section>`, or hand the whole file to a
host session that has `gh`. Sections are independent and can be filed in any
order; the ones under *Enclave network isolation*, *Egress proxy* and *Container
launch hardening* are the ones worth filing first.

Tag under audit: **v56.9.5.1** (commit `77958f552776874e3d43a75878b9caa80f4e6657`).
Where a claim is contrasted with the stable release, that is **v56.9.2.1**
(commit `49458e968aed4f65c73eba5f2ba0f3d5483abd65`).

---

# Enclave network isolation

## Two launchers still create the enclave network without `--internal` at v56.9.5.1

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `scripts/run-forge-project.sh`, `scripts/diagnose-proxy.sh`, `scripts/check-enclave-network-internal.sh`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the spec.** `openspec/specs/enclave-network/spec.md#L24` —
"**THEN** the system MUST create it with `podman network create
tillandsias-enclave --internal`".

**What the code does.** `scripts/run-forge-project.sh#L118` — `"$PODMAN_CTL"
network create --driver bridge --subnet "$ENCLAVE_SUBNET" "$ENCLAVE_NET"`.
`scripts/diagnose-proxy.sh#L92` — `podman network create --driver bridge
--subnet "10.0.42.0/24" "$ENCLAVE_NET"`. Neither passes `--internal`. Both are
guarded by `podman network exists`, so whichever launcher runs first on a host
decides permanently whether the enclave is isolated.

The guard added for exactly this defect does not see either one.
`scripts/check-enclave-network-internal.sh#L87-L89` states its own contract as
"Find every site that creates the enclave network … Read from source rather than
restating a list here, so a NEW launcher cannot be added without this check
seeing it" — but the implementation is a hardcoded three-file list:
`scripts/orchestrate-enclave.sh` (L93), then a `for rs in` loop over exactly
`crates/tillandsias-podman/src/client.rs` and
`crates/tillandsias-podman-cli/src/lib.rs` (L112-L119). Its own header names a
third Rust path, `crates/tillandsias-headless/src/main.rs`, which the loop does
not include either.

**Why it matters.** `--internal` is the isolation. Without it podman attaches a
gateway and every member of `tillandsias-enclave` gets NAT egress, so the squid
allowlist stops being the only way out and the whole egress story on the public
explanation pages stops holding. `scripts/orchestrate-enclave.sh#L100-L127`
already refuses to reuse a non-internal network; these two scripts create one.
And because the guard enumerates files rather than discovering create sites, its
"ok:enclave-network-internal:source" verdict is true of three files and silent
about the rest of the tree.

**Smallest fix.** Add `--internal` to both create calls, and replace the guard's
hardcoded file list with a repository-wide search for `podman network create`
invocations naming `$ENCLAVE_NET` / `tillandsias-enclave`, so a new launcher
fails the check instead of being invisible to it.

---

## `run_provider_login` attaches a container to the enclave without being a documented member, and the membership guard cannot see it

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-headless/src/main.rs`, `scripts/check-enclave-membership-documented.sh`, spec `enclave-network`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the spec.** `openspec/specs/enclave-network/spec.md#L45-L60` —
"The attach sites are these run-argument builders, named by SYMBOL so the list
survives every edit that does not rename one … A new enclave member MUST be
added to this list in the same commit that attaches it;
`scripts/check-enclave-membership-documented.sh` refuses the divergence in both
directions."

**What the code does.** `crates/tillandsias-headless/src/main.rs#L9728` and
`#L9764` — inside `fn run_provider_login` (defined at `#L9607`), two `podman
run` invocations pass `"--network", ENCLAVE_ONLY_NET`. `run_provider_login` is
not in the spec's twelve-symbol list.

The guard cannot report it. `scripts/check-enclave-membership-documented.sh#L71`
— `if (fname ~ /^(build|launch)_/) { print fname }`. Only enclosing functions
whose names begin `build_` or `launch_` are counted, so a production attach site
in any other function is filtered out before the comparison runs. The same name
filter is also silently doing the job the header at L59-L61 attributes to
something else: that header says "The `#[cfg(test)]` region is cut before
scanning", and no such cut exists anywhere in the script.

**Why it matters.** The spec's stated guarantee is that the membership list
cannot drift silently, and its own text explains that a hand-maintained prose
list had already gone stale by six members. The replacement mechanism reproduces
the failure one level down: this attach site has been undetectable since the
guard landed, and the spec's "Only the proxy MUST additionally be attached to
the egress network" is stated against a list that is missing a member. The
guard's own header even acknowledges a second dual-homed member ("the
dual-homed pair (proxy, and the login helper)") that the spec text denies.

**Smallest fix.** Drop the `^(build|launch)_` name filter (cutting the real
`#[cfg(test)]` region instead, as the header already claims), then add
`run_provider_login` to the spec's membership list or route it through a named
builder.

---

## The enclave-network spec's cleanup-on-exit and lifecycle-telemetry requirements have no implementation

- Tag: v56.9.5.1 (commit 77958f5)
- Area: spec `enclave-network`, `crates/tillandsias-headless/src/main.rs`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the spec.** `openspec/specs/enclave-network/spec.md#L31-L34` —
"**WHEN** the Tillandsias application exits **AND** no containers are attached
… **THEN** the system MUST remove the network with `podman network rm
tillandsias-enclave`". And `#L80-L86` — "**THEN** the system MUST log
`[enclave] Network created: tillandsias-enclave`" / "`[enclave] Container
attached: <name>`", both with `@trace spec:enclave-network`.

**What the code does.** `graceful_shutdown_async` at
`crates/tillandsias-headless/src/main.rs#L16652` stops `tillandsias-`-prefixed
containers and never touches a network. The only `network rm` in the crate is
`#L8845`, inside `run_reset_guest` — the explicit `--reset-guest` wipe, not an
exit path. `PodmanClient::remove_network`
(`crates/tillandsias-podman/src/client.rs#L975`) has no production caller: the
only references are `crates/tillandsias-podman-cli/src/lib.rs#L479` (the
scenario tool) and a `let _ =` liveness reference at `client.rs#L3374`. The two
mandated log strings — `Network created` and `Container attached` — do not
appear anywhere under `crates/`, `scripts/` or `images/`.

**Why it matters.** Two of the four scenarios under the spec's primary
requirement, and both scenarios of its telemetry requirement, describe behaviour
that does not exist. The network persists across every exit, which is also what
makes the `--internal` installed-base gap above permanent rather than
self-healing, and the `--log-enclave` accountability window the spec promises is
empty for enclave lifecycle events.

**Smallest fix.** Either implement the exit-time `podman network rm` (guarded on
zero attached containers) and the two log lines, or mark both requirements
`deferred` with the reason, so the spec stops asserting them.

---

# Egress proxy

## The permissive proxy port grants unfiltered egress to every enclave member with no source restriction

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `images/proxy/squid.conf`, spec `proxy-container`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 3

**Claim in the spec.** `openspec/specs/proxy-container/spec.md#L104` — the
dual-port table lists port 3129 as "Permissive | All domains allowed", and
`#L112-L114`: "**WHEN** a request is sent through port 3129 **THEN** all domains
on SSL ports (443, 8443) SHALL be permitted **AND** domain filtering SHALL NOT
apply."

**What the code does.** `images/proxy/squid.conf#L60` — `http_port 3129
ssl-bump \` with no bind address, so squid listens on `0.0.0.0:3129` on every
interface the container has. `#L133-L134` — `http_access allow CONNECT SSL_ports
build_port` / `http_access allow build_port`, with `build_port` defined at `#L93`
as `acl build_port localport 3129` and no source ACL anywhere in the file. The
container is dual-homed: `crates/tillandsias-headless/src/main.rs#L3425-L3426`
passes `--network ENCLAVE_EGRESS_NETS` (= `"tillandsias-enclave,tillandsias-egress"`,
`#L1651`), so the listener is reachable from both networks.

**Why it matters.** Every enclave container is handed
`http_proxy=http://proxy:3128` (`main.rs#L1711-L1717`), but nothing prevents any
of them from using `http://proxy:3129` instead and reaching the internet with
the allowlist skipped entirely. The port's own header comment (`squid.conf#L6-L45`)
is careful and honest about the port having no consumer today, and
`scripts/check-proxy-permissive-port-routing.sh` pins that honesty — but "no
consumer" is a statement about Tillandsias's own code, not about what an agent
inside a forge can dial. Filtering that a client can opt out of by changing a
port number is not a boundary, and the explanation pages describe the allowlist
as one.

**Smallest fix.** Bind the permissive listener to loopback
(`http_port 127.0.0.1:3129 …`) so it is unreachable from the enclave, or add a
source ACL restricting it, until a real consumer exists.

---

## The proxy CA is one persistent RSA-2048 30-day certificate; the spec promises a per-launch two-level EC P-256 chain on tmpfs

- Tag: v56.9.5.1 (commit 77958f5)
- Area: spec `proxy-container`, `crates/tillandsias-headless/src/main.rs`, `images/default/ca-path.txt`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 3

**Claim in the spec.** `openspec/specs/proxy-container/spec.md#L66` — "The
system SHALL generate a fresh two-level CA chain on every proxy launch. The
chain SHALL consist of a self-signed Root CA and an Intermediate CA signed by
the root, both using EC P-256 keys. All key material SHALL be stored on tmpfs
(`$XDG_RUNTIME_DIR/tillandsias/proxy-certs/`) and SHALL be destroyed when the
session ends (logout/reboot). No CA keys SHALL persist to disk." The four-file
table below it names `root.crt`, `intermediate.crt`, `intermediate.key`,
`ca-chain.crt`, each with lifetime "Session (tmpfs)", and a scenario requires
generation "in under 10ms (EC P-256 key generation)". The spec's Status is
`active` with no stale or superseded marker.

**What the code does.** `crates/tillandsias-headless/src/main.rs#L3170-L3189`
(`fn ensure_ca_bundle`) shells out to `openssl req -x509 -newkey rsa:2048 …
-days 30 -nodes -subj "/C=US/ST=Privacy/L=Local/O=Tillandsias/CN=Tillandsias CA"`
— one self-signed RSA-2048 certificate valid 30 days, not a two-level EC P-256
chain. It is not per-launch: `ca_bundle_needs_refresh` (`#L3055-L3068`) returns
false while both files are under 25 days old, so a launch reuses the existing
key. And it is deliberately not on tmpfs: the directory comes from
`tillandsias_core::ca_path::ca_dir()`, whose single-source manifest
`images/default/ca-path.txt` declares `${HOME}/.local/state/tillandsias` and
explains at length that a durable location was chosen by measurement because
"/tmp works everywhere and is the bug" — a reboot on a volatile path made the
proxy permanently unrestartable (order 975-rsgm).

**Why it matters.** The code is right and the spec is wrong, which is the worse
direction: the spec is the artifact a reader (or an auditing agent, or this
site) treats as the contract, and it currently promises ephemerality that the
implementation deliberately abandoned for a documented reason. "No CA keys SHALL
persist to disk" is a security claim, and the CA private key persists to
`$HOME/.local/state/tillandsias/ca/intermediate.key` for up to 25 days.

**Smallest fix.** Rewrite the "Ephemeral CA chain (per-launch generation)"
requirement to describe the durable single-certificate design and its 25-day
refresh, citing `images/default/ca-path.txt` for why the path is not tmpfs.

---

## Denied runtime traffic gets a TCP reset; the proxy spec says HTTP 403 twice

- Tag: v56.9.5.1 (commit 77958f5)
- Area: spec `proxy-container`, `images/proxy/squid.conf`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 3

**Claim in the spec.** `openspec/specs/proxy-container/spec.md#L53` — "**THEN**
the proxy SHALL deny the request with HTTP 403"; and again at `#L109` — "**AND**
all other domains SHALL be denied with HTTP 403". A third scenario (`#L186-L188`)
requires that "the proxy response SHALL include the blocked domain name for
debugging".

**What the code does.** `images/proxy/squid.conf#L137-L141` — `acl
strict_deny_acl localport 3128` followed by `deny_info TCP_RESET
strict_deny_acl`, with the inline rationale "Send a TCP reset instead of an HTTP
403 error for strictly-denied runtime traffic. This prevents sophisticated
tunneling/exfiltration over denied connections."

**Why it matters.** The behaviours are not interchangeable for a client: a 403
carries a body naming the blocked domain (which a third scenario in the same
spec requires), a TCP reset carries nothing. Anyone debugging a blocked domain
from inside a forge, or writing a test against the spec, is told to expect a
status code that never arrives. The deliberate choice recorded in the config is
the right one; the spec has simply not been updated to it.

**Smallest fix.** Change the two `HTTP 403` scenarios to `TCP_RESET` on port
3128, and either drop or re-scope the "response SHALL include the blocked
domain" scenario, which a reset cannot satisfy.

---

# Container launch hardening

## The hardening litmus header says the argv validator has zero production call sites; it has three

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the litmus header.**
`openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml#L66-L71` —
"WHAT IT STILL DOES NOT COVER … that every production launch site actually
APPLIES the envelope. The validator that would answer this — `validate_launch_argv`
in the same module — has zero production call sites, which is order 972-6vaj's
subject, not this file's."

**What the code does.** At this tag `validate_launch_argv`
(`crates/tillandsias-podman/src/policy.rs#L110`) has three non-test callers:
`crates/tillandsias-podman/src/container_spec.rs#L396` inside
`fn build_run_argv`, and `crates/tillandsias-headless/src/main.rs#L11711` and
`#L11877`. `container_spec.rs#L379-L384` documents the change explicitly ("THIS
WAS A `debug_assert!` AND THEREFORE NOTHING … the validator had zero production
call sites"), i.e. the header describes the state 972-6vaj fixed.

**Why it matters.** This is the file a reader consults to learn what the
hardening gate does and does not prove, and it is currently more pessimistic
than the truth in a way that hides the real remaining gap (see the next issue).
A stale disclaimer in a security fixture is read as current fact.

**Smallest fix.** Replace the paragraph with the current state: the validator
now guards `ContainerSpec::build_run_argv` and the two delegated-run entry
points, and name the launch paths that still bypass it.

---

## Five production container launches never reach `validate_launch_argv`, and one of them builds an argv the policy forbids

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-headless/src/main.rs`, `crates/tillandsias-podman/src/container_spec.rs`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the code.** `crates/tillandsias-headless/src/main.rs#L11681-L11688` —
"VERIFIED 2026-09-04: this function's only production caller is
`run_agent_container_attached`, which validates first; its four other callers
are inside `mod tests` … **Every production container launch therefore already
passes `validate_launch_argv`.**" A second doc comment at `#L14177` states
"Every option flows through the policy-validated `build_run_argv()` path".

**What the code does.** `ContainerSpec` has two serializers:
`build_run_argv()` validates (`container_spec.rs#L394-L397`), `build_run_args()`
does not (`#L274`). These production paths use the unvalidated one, or build
argv by hand and hand it straight to `PodmanClient::run_container_observed`
(`crates/tillandsias-podman/src/client.rs#L1022`), which performs no validation:

- the egress proxy — `main.rs#L3414` `fn build_proxy_run_args` returns a raw
  `Vec<String>`, launched at `#L3526`;
- the git mirror — `main.rs#L4284` `fn build_git_run_args`, launched at `#L9087`;
- the observatorium web container — `main.rs#L11246` `.build_run_args()`;
- the project browser — `main.rs#L11295` and `#L13047` `spec.build_run_args()`;
- the interactive forge — `build_forge_agent_run_args_with_vault` ends at
  `#L14736` with `spec.build_run_args()`, and `build_forge_agent_run_argv`
  (`#L14741`) merely prefixes `podman run` before `launch_forge_agent`
  (`#L15089`) spawns it in a host terminal emulator. This is the path the
  `#L14177` doc comment describes, and it never calls the validator.

And the gap is not theoretical. `fn run_provider_login`
(`main.rs#L9607`) launches a container at `#L9722-L9740` with `--cap-drop=ALL`,
`--security-opt=no-new-privileges` and `--userns=keep-id` — but **not**
`--security-opt=label=disable`, which `policy.rs#L17-L22`
(`MANDATORY_HARDENING_FLAGS`) declares mandatory. `validate_launch_argv` would
return `MissingMandatoryHardening(["--security-opt=label=disable"])` for that
argv. Nothing calls it there, so the launch proceeds.

**Why it matters.** The project's own framing (`container_spec.rs#L385-L392`) is
that an argv missing a hardening flag "is not a degraded launch to be reported,
it is a container that must not be created". At this tag that guarantee holds
for exactly the delegated-agent lanes, while the proxy, the mirror, the
observatorium, the browser and the interactive forge — the containers a user
actually runs — are outside it, and there is already one production argv the
policy would reject.

**Smallest fix.** Route every builder through `build_run_argv()` (or call
`validate_launch_argv` in `run_container_observed` / `run_container_attached_observed`
so no launcher can bypass it), fix `run_provider_login`'s missing flag, and
correct the two doc comments.

---

# Release integrity and install

## The macOS release lane signs a hardcoded three-asset list and runs no transitive integrity check

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `.github/workflows/release.yml`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim in the spec.** `openspec/specs/binary-signing/spec.md#L17-L18` — "**WHEN**
a release contains the Linux musl binary and installer helper scripts **THEN**
each signable artifact MUST have its own `.cosign.bundle` file".

**What the code does.** The Linux lane discovers what to sign and then proves
the property over whatever was staged: `.github/workflows/release.yml#L264-L268`
loops `for artifact in *` (skipping only `SHA256SUMS` and existing bundles), and
`#L293` runs `bash ../scripts/check-release-asset-integrity.sh .`, whose own
header (`scripts/check-release-asset-integrity.sh#L14-L20`) exists precisely
because "the Windows job's signing loop was an ALLOW-LIST".

The macOS lane at `#L507-L518` is that allow-list:

```
for artifact in tillandsias-tray-*-macos-arm64.tar.gz Tillandsias.dmg install-macos.sh; do
```

`SHA256SUMS-macos` — staged at `#L501` — is not in the list and gets no
`.cosign.bundle`. And `check-release-asset-integrity.sh` is invoked in only two
jobs (`#L293` Linux, `#L772` Windows); the macOS job does not run it.

**Why it matters.** The integrity guard was written after an asset shipped
unverifiable for exactly this reason, and the lane that reproduces the pattern
is the one it is not wired into. `scripts/install-macos.sh#L106-L128` downloads
`SHA256SUMS-macos` and trusts it as the sole integrity source for the tarball —
a manifest with no signature of its own. Any asset added to the macOS lane later
inherits the same silence.

**Smallest fix.** Replace the three-name glob with the Linux lane's `for
artifact in *` form and add `bash scripts/check-release-asset-integrity.sh
release-artifacts` to the macOS job.

---

## No default install path verifies a Cosign bundle, and the Linux installer continues when the checksum file is missing

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `scripts/install.sh`, `scripts/install-macos.sh`, `scripts/install-windows.ps1`, spec `update-system`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim in the spec.** `openspec/specs/binary-signing/spec.md#L27-L30` — "All
signable release artifacts MUST be signed with Cosign keyless mode and MUST be
verifiable locally using the bundle format." Verification itself is placed on
the user: `#L45-L52` requires only that the *instructions* and
`scripts/verify.sh` use `cosign verify-blob --bundle`.

**What the code does.** `cosign` appears in no installer. `scripts/verify.sh` is
the only consumer (`#L46`, `#L78`), and it is an opt-in helper the install path
never calls. The three install scripts stop at SHA-256:
`scripts/install.sh#L226-L239`, `scripts/install-macos.sh#L106-L128`,
`scripts/install-windows.ps1#L361-L390`.

`scripts/install.sh` additionally proceeds on every failure of that weaker
check — `#L232` "sha256sum not found; skipping checksum verification.", `#L235`
"SHA256SUMS did not contain $ASSET; skipping checksum verification.", `#L238`
"SHA256SUMS not available; skipping checksum verification." — and then installs
the downloaded bytes at `#L243`. (`install-macos.sh` and `install-windows.ps1`
do die on a missing manifest; only the Linux path degrades open.)

`openspec/specs/update-system/spec.md` — the spec governing how a running
install obtains a new artifact — contains one requirement, "Platform-appropriate
artifact selection", and the strings `cosign`, `verify`, `signature` and
`checksum` do not appear in it at all.

**Smallest fix.** Make `install.sh` fail closed when `SHA256SUMS` is missing or
does not name the asset, and add a signature-verification requirement to
`openspec/specs/update-system/spec.md` (verify the bundle when `cosign` is
present, refuse or warn loudly when it is not).

---

# Vault and secrets

## The Vault unseal share persists to a plain file that satisfies the "share in keychain" check, contradicting the tmpfs-only invariant, and `--reset-guest` leaves it behind

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-headless/src/vault_bootstrap.rs`, `crates/tillandsias-headless/src/main.rs`, spec `tillandsias-vault`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim in the spec.** `openspec/specs/tillandsias-vault/spec.md#L391-L393` —
"### Invariant: Unseal key is tmpfs-only … **Expression**:
`/run/secrets/vault-unseal IS_ON tmpfs AND NEVER persisted to disk`". `#L88-L91`
adds that "the host launcher captures the random Vault-generated share on first
boot, persists it in the host keychain, and deletes all local on-disk copies".

**What the code does.**
`crates/tillandsias-headless/src/vault_bootstrap.rs#L1295-L1322`
(`fn write_vm_credential_fallbacks`) writes the base64 Shamir share with
`fs::write(cache_dir.join(format!("fallback_{VAULT_SHAMIR_SHARE_V1}")), share_b64)`.
`cache_dir` is `crate::init_cache_dir()` (`main.rs#L2011-L2028`), which resolves
to `$XDG_CACHE_HOME/tillandsias` or `$HOME/.cache/tillandsias` — ordinary durable
disk. The write is unconditional whenever the host delivers a share into the
guest (`vault_bootstrap.rs#L108-L124`), and its doc comment says so plainly: the
file "is the ONLY evidence inside the guest that `operator init` ever
completed".

That file is also what answers the "is the share in the keychain?" question.
`has_shamir_share_in_keyring` (`#L1345-L1372`) tries the OS keychain, then falls
through to `fs::read_to_string(cache_dir.join(format!("fallback_{}",
VAULT_SHAMIR_SHARE_V1)))` and returns true if it base64-decodes to 32 bytes — so
the predicate that guards the partial-init wipe is satisfied by a file, not by a
keychain.

Nothing deletes it. There is no `remove_file` / `delete` of any `fallback_*`
path anywhere under `crates/`. And `--reset-guest`, documented at
`main.rs#L1430` as an "EPHEMERAL RESET: wipe the guest substrate", removes
containers, volumes, podman secrets and networks (`main.rs#L8803-L8848`) and
then exactly one host path — `reset_guest_wipe_paths` (`#L8746-L8748`) returns
`vec![cache_dir.join("vault-data")]`. The share file sits in the same directory
and survives. `--reset-guest` also never touches the OS keychain: the only
`delete_credential` call in the crate is `vault_bootstrap.rs#L1924`, inside
`fn sanitize_keychain`, and it deletes only the legacy `vault-unseal-v1` entry.

**Why it matters.** The unseal share is the key to the vault holding the user's
provider tokens and GitHub credential. The spec's headline invariant is that it
never reaches disk; in the VM guest it always does, in a directory that survives
the command whose entire purpose is discarding guest state.

**Smallest fix.** Add the fallback share (and root-token) files to
`reset_guest_wipe_paths`, delete the OS-keychain entry in the same reset, and
either restrict the fallback file to a tmpfs path or amend the
`unseal-key-tmpfs-only` invariant to state the guest exception explicitly.

---

## The forge startup context tells the agent Vault is at `http://vault:8200`; the listener is TLS-only

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `images/default/lib-common.sh`, `images/vault/vault.hcl`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 2

**Claim in the startup context.** `images/default/lib-common.sh#L4441` — the
text printed into every forge agent's opening context reads: "**Vault**: secrets
are available at `http://vault:8200`; token is injected automatically."

**What the code does.** `images/vault/vault.hcl#L16-L21` configures the only
listener with `tls_cert_file`, `tls_key_file` and `tls_client_ca_file` and no
`tls_disable`, and `#L23` sets `api_addr = "https://vault:8200"`. The Rust side
agrees: `crates/tillandsias-headless/src/vault_bootstrap.rs#L900` —
`const VAULT_EXEC_ADDR: &str = "https://127.0.0.1:8200"`, and its own test at
`#L4864` asserts `linux_vault_api_base_url(true) == "https://vault:8200"`.

**Why it matters.** This string is the first thing an autonomous agent reads
about how to reach Vault, and following it produces a TLS-handshake failure
against a plaintext request. It also mis-teaches the security posture: the
in-enclave hop is authenticated TLS, and the context says it is not.

**Smallest fix.** Change the line to `https://vault:8200`.

---

# Forge on-demand tooling

## The startup context says on-demand installs verify a Sigstore attestation; the shim disables attestation, and the Homebrew prefix is backed by no volume

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `images/default/lib-common.sh`, `images/default/brew-shim-exec.sh`, `images/default/Containerfile`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 2

**Claim in the startup context.** `images/default/lib-common.sh#L4514-L4516` —
"**On-demand tools** (`tmux`, `lazygit`, `gum`, `fd`, `rg`, …): typing the
command triggers a userspace Homebrew install through a shim, gated on an
allowlist. That install is NOT free — **it verifies a Sigstore attestation per
bottle** and is time-bounded". The same file repeats it in the shim-generation
comment at `#L3336`: "(homebrew-core formulae only, Sigstore attestation
verification REQUIRED)".

**What the code does.** `images/default/brew-shim-exec.sh#L89` — `export
HOMEBREW_NO_VERIFY_ATTESTATIONS=1`, with a long, correct explanation at
`#L62-L88` of why it had to be turned off (the attestation path calls `gh
attestation verify`, which needs a GitHub credential the forge deliberately does
not have) and what replaced it (Homebrew's own signed formula index, which the
comment is careful to call "authenticated integrity from a single publisher …
NOT provenance").

Separately, the prefix that install lands in is
`BREW_PREFIX="${TILLANDSIAS_BREW_PREFIX:-/home/linuxbrew/.linuxbrew}"`
(`brew-shim-exec.sh#L32`). `/home/linuxbrew` exists only as a directory created
in the image (`images/default/Containerfile#L27`); no builder mounts a volume
there. The per-project tool-cache volume mounts `/home/forge/.cache/tillandsias-project`
(`crates/tillandsias-headless/src/main.rs#L14414-L14416`), a different path.
Forge containers run `--rm` (`ContainerSpec::new` sets `remove: true`,
`crates/tillandsias-podman/src/container_spec.rs#L121`), so the Homebrew clone
and every installed bottle are discarded when the container exits and re-fetched
on the next launch.

**Why it matters.** The startup context is the security story an agent is given
about the tools it installs, and it asserts a provenance check that the shim
explicitly turns off — the one place where the code comment is more honest than
the user-facing text. The unbacked prefix is a second, quieter cost: an
"on-demand install" that is redone from scratch every launch, against an egress
allowlist, rather than cached.

**Smallest fix.** Rewrite both lib-common.sh strings to describe what actually
holds (signed formula index → bottle checksum; no attestation, no provenance),
and mount a named volume at `/home/linuxbrew` in the forge builders.

---

# Git mirror

## `litmus:git-mirror-no-anonymous-daemon-write` asserts the opposite of its own name

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `openspec/litmus-tests/litmus-git-mirror-no-anonymous-daemon-write.yaml`
- Class: doc-drift
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the name.** The fixture is registered as
`name: litmus:git-mirror-no-anonymous-daemon-write`
(`openspec/litmus-tests/litmus-git-mirror-no-anonymous-daemon-write.yaml#L2`),
`severity: critical`.

**What the file says.** `#L7-L17` — "Historical name retained, but the current
daemon **DOES** expose anonymous enclave receive-pack (order 450). Any reachable
peer can create or fast-forward refs and cause the privileged service relay to
carry those updates upstream … This litmus pins only honest interim containment
… It MUST NOT be cited as zero-trust closure."

**Why it matters.** The body is exemplary; the name is what appears in
`openspec/litmus-bindings.yaml`, in gate output, and in any summary a reader or
an auditing agent assembles from test names. A green `critical` test called
"no-anonymous-daemon-write" reads as proof that anonymous daemon writes are
impossible, which is the exact opposite of what the file establishes.

**Smallest fix.** Rename it to what it pins — e.g.
`litmus:git-mirror-anonymous-write-relay-containment` — and leave a one-line
alias note for the old name.

---

## The mirror relay wires the GitHub credential helper for any `https://` origin, and the helper answers unconditionally

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `images/git/relay-refs.sh`, `images/git/git-credential-tillandsias.sh`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 4

**What the code does.** `images/git/relay-refs.sh#L182-L221` — the credential
wiring is inside `case "$REMOTE_URL" in https://*)`, i.e. it triggers for any
HTTPS upstream, not for GitHub specifically. `REMOTE_URL` is the project's own
`remote.origin.url`, read from the host checkout and passed into the mirror
(`crates/tillandsias-headless/src/main.rs` `fn read_host_project_origin_url`, `#L3653-L3660`, and the `remote.origin.url` read at `#L3588`). The helper it installs
is `images/git/git-credential-tillandsias.sh`, which states at `#L34-L37`: "Drain
stdin (git sends protocol/host/path). **We do not branch on it**: this helper is
wired per-invocation by the relay for one specific remote, so answering
unconditionally is correct" — and then returns the Vault-held GitHub token
(`#L48-L57`) for whatever host git asked about.

**Why it matters.** The helper's assumption ("wired for one specific remote") is
enforced nowhere: the relay wires it on the basis of the URL *scheme* alone. A
project whose `origin` is any non-GitHub HTTPS remote — or a redirect chain
ending at one — gets the user's GitHub token offered to that host on the first
push through the mirror. The mirror is the privileged component in this design
precisely because it holds the credential the forge is denied; the condition
that decides when it hands that credential out should be the host, not the
scheme.

**Smallest fix.** Match on the origin host (`https://github.com/*`, plus any
explicitly configured enterprise host) rather than `https://*`, and have the
helper read `host=` from stdin and refuse anything it does not recognise.

---

# Inference

## The inference engine is fetched at first run from an unpinned `latest` release with no integrity check, the specs promise baked models the image does not carry, and the health check tests the runner binary

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `images/inference/entrypoint.sh`, `images/inference/Containerfile`, specs `inference-container` and `zen-default-with-ollama-analysis-pool`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 3

**What the code does.** Three separate gaps in one container.

*Unpinned, unverified engine.* `images/inference/entrypoint.sh#L293` —
`OLLAMA_URL="https://github.com/ollama/ollama/releases/latest/download/ollama-linux-${OLLAMA_ARCH}.tar.zst"`.
`latest` is a moving target, and the download at `#L309-L312` is followed by
`zstd -dc | tar -xf` and `install -m 0755 … "$OLLAMA_BIN"` (`#L345-L348`) with
no checksum, no signature and no pinned digest anywhere in the file. The fetch
goes through the enclave proxy, which bumps `release-assets.githubusercontent.com`
with a certificate the container is configured to trust
(`openspec/specs/proxy-container/spec.md#L36-L42`), so TLS is not standing in
for provenance here either.

*Promised baked models that are absent.*
`openspec/specs/zen-default-with-ollama-analysis-pool/spec.md#L47-L54` — T0
`qwen2.5:0.5b` and T1 `llama3.2:3b` are both marked "Baked", and "T0 and T1 are
baked into the inference image at build time so the first attach has a usable
analysis model with zero network overhead"; `#L59` repeats it as a scenario
outcome. `openspec/specs/inference-container/spec.md#L285` lists "T0 models baked
into image" as a gating point (while `#L110` of the same file says they are
pulled at startup — the two specs already disagree with each other).
`images/inference/Containerfile#L70` only runs `mkdir -p /opt/baked-models &&
chown`; no `COPY` ever puts a model there, so the seeding block at
`entrypoint.sh#L399-L406` has nothing to seed from. T1 is absent altogether:
`entrypoint.sh#L120` sets `DEFAULT_MODELS="${TILLANDSIAS_DEFAULT_MODELS:-qwen2.5:0.5b}"`,
and the comment at `#L114-L115` records that `llama3.2:3b` was replaced. So
`llama3.2:3b` is named by both specs and is neither baked nor pulled.

*A health check that cannot see the failure it was written for.*
`images/inference/Containerfile#L118-L121` — `curl -sf
http://127.0.0.1:11434/api/version && test -x
/home/ollama/.ollama/models/.tools/lib/ollama/llama-server`. The header above it
(`#L100-L117`) explains the live incident it exists for: the container sat at
`Up (healthy)` while every `/api/generate` returned HTTP 500. The repair
upgrades the probe from "the port is bound" to "the port is bound and a file is
executable" — it still never loads a model, so a present-but-broken engine or an
empty model cache still reads healthy.

**Why it matters.** The engine binary is the largest single untrusted input the
runtime installs, and it arrives from a mutable URL into a container that then
serves every forge on the enclave. The baked-model promise is what the specs
offer as the offline/first-attach guarantee, and it is not there. And the
health signal that the launcher's readiness gate believes is still a proxy for
serving, not serving.

**Smallest fix.** Pin the ollama release to a version and verify its published
checksum before extracting; then either bake T0/T1 (`COPY` into
`/opt/baked-models`) or correct both specs to say the models are pulled and drop
`llama3.2:3b`; and make the health check issue one tiny `/api/generate` (or
`/api/show`) against T0 rather than stat a file.

---

# Published local web service

## `--publish-local` serves the whole repository, `.git` included, on a route with no auth gate — and does it with none of the hardening flags the spec's builder carries

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-headless/src/main.rs`, `images/web/entrypoint.sh`, spec `enclave-service-catalog`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the spec.** `openspec/specs/enclave-service-catalog/spec.md#L61-L65`
names `build_catalog_service_run_args` as a source of truth for how a catalog
service is launched, and `openspec/specs/enclave-network/spec.md#L53` lists it
as the enclave attach site for this service.

**What the code does.** `build_catalog_service_run_args`
(`crates/tillandsias-headless/src/main.rs#L3368-L3394`) is hardened and
digest-pinned — `--cap-drop=ALL`, `--security-opt=no-new-privileges`,
`--security-opt=label=disable`, `--userns=keep-id`, `--pids-limit=32`, and an
image resolved to `entry.digest`. **It has no production caller**: the only
reference in the tree is the test at `#L18836`.

The live path is `fn publish_local_service` (`#L16812`), reached from
`--publish-local` (`#L1082-L1084`) and from the MCP `publish_local` tool
(`crates/tillandsias-headless/src/tray/mod.rs#L1012-L1017`). It builds its own
argv at `#L16841-L16853`:

```
"--detach", "--rm", "--name", <container>, "--hostname", …,
"--network", "tillandsias-enclave",
"-v", format!("{}:/var/www:ro,Z", worktree.display()),
image /* "tillandsias-web", a mutable tag */
```

No capability drop, no `no-new-privileges`, no `userns`, no pids limit, no
digest pin. `worktree` is `host_project_root().join(project_name)`
(`#L16836`) — the project's repository root, `.git` and all — and the image
serves it with `httpd -f -p 8080 -h /var/www` (`images/web/entrypoint.sh#L17`)
with no config file, so no path is excluded. The route is then registered with
`new_route.public = true` (`#L16883-L16885`), which
`generate_dynamic_caddyfile` renders as a bare `reverse_proxy` with no
`forward_auth` gate — the project's own test at `#L18872-L18886` asserts exactly
that.

**Why it matters.** Any forge agent (the MCP tool is in-forge reachable) can
publish `http://www.<project>.localhost/`, and from that moment
`.git/config`, `.git/objects/**` and any untracked secret in the working tree
are served without authentication to everything that can reach the router. The
hardened, digest-pinned builder that the two specs point at as the
implementation is dead code, so reviewing it tells you nothing about what runs.

**Smallest fix.** Have `publish_local_service` call
`build_catalog_service_run_args` (deleting its inline argv), and give the web
image an httpd config that refuses dot-directories — or mount a build output
directory rather than the repository root.

---

# Browser

## The browser allowlist cannot open any window for a project whose directory name contains a dot

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-browser-mcp/src/allowlist.rs`, `crates/tillandsias-headless/src/local_projects.rs`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 4

**What the code does.** `crates/tillandsias-browser-mcp/src/allowlist.rs#L233-L246`
— `validate()` splits the host on `.` and refuses anything that is not exactly
three labels:

```
let labels = split_host_labels(&host);
if labels.len() != 3 || labels[2] != "localhost" { return Err(AllowlistDeny::HostShape); }
…
if host_project_label != project_label { return Err(AllowlistDeny::ProjectMismatch { … }); }
```

The project label it compares against is the raw directory name.
`crates/tillandsias-browser-mcp/src/server.rs#L62-L63` reads it from
`TILLANDSIAS_PROJECT`, which the forge builders set to `project_name`
(`crates/tillandsias-headless/src/main.rs#L11236`, `#L14437`), and `project_name`
comes from `scan_project_root`'s `path.file_name()`
(`crates/tillandsias-headless/src/local_projects.rs#L76-L78`) with no
dot-substitution — only a leading-dot skip.

**Why it matters.** For a project directory such as `tillandsias.org`, the label
is `tillandsias.org`, so every candidate host is four labels
(`web.tillandsias.org.localhost`) and hits `HostShape`; and a three-label host
would fail `ProjectMismatch` because `labels[1]` is `tillandsias`. There is no
path through `validate()` that succeeds, so `browser.open` is unusable for the
whole class of projects named after a domain — a common naming convention, and
the one this very site's repository uses.

**Smallest fix.** Compare the trailing labels against the project label rather
than requiring `len() == 3`, or normalise dots to `-` when deriving the label
(matching `project_label_from_path` at `main.rs#L11189`, which already does
this for container hostnames) and use the same normalised label on both sides.

---

## `browser.open` cannot resolve a browser binary: the on-demand chromium installer has no consumer, and the chromium images are built but never run

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-browser-mcp/src/launcher.rs`, `scripts/install-chromium.sh`, `images/chromium/`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 4

**What the code does.** `crates/tillandsias-browser-mcp/src/launcher.rs#L67-L91`
(`fn resolve_browser_binary`) accepts an explicit override, then
`TILLANDSIAS_BROWSER_BIN`, then `TILLANDSIAS_CHROMIUM_BIN`, then looks only under
the cache root (`~/.cache/tillandsias/chromium/current/chrome` and four
siblings) and otherwise returns `LaunchError::BrowserUnavailable` — declared at
`#L21` as "bundled chromium not yet downloaded". There is no `PATH` fallback to a
system chrome/chromium.

The only thing that would populate that directory is
`scripts/install-chromium.sh`, and nothing invokes it. Outside the script itself,
a repository-wide search for `install-chromium.sh` returns no caller anywhere
under `crates/`, `scripts/` or `images/`; the only reference that runs is
`openspec/litmus-tests/litmus-host-chromium-on-demand-shape.yaml`, whose steps
(`#L33-L75`) are `grep` assertions over the script's own text. The shape test is
green while the installer has no caller. (The repository already knows:
`plan/index.yaml#L22893` carries a packet titled "scripts/install-chromium.sh has
ZERO consumers … wire it or tombstone it", so check that packet's state before
filing.)

Separately, `images/chromium/Containerfile.core` and `Containerfile.framework`
are wired into the build (`scripts/build-image.sh#L214-L215`,
`crates/tillandsias-core/src/image_builder.rs#L329-L330`), but no Rust code
launches either image — the only non-build references under `crates/` are build
plumbing and status maps.

**Why it matters.** On a fresh host the whole host-browser MCP surface fails at
its first call with an error that names a download step no code performs, and
the litmus that is supposed to cover "host chromium on demand" cannot detect
that because it only greps the installer's source. Meanwhile two multi-hundred-
megabyte container images are built on every image pass and never started.

**Smallest fix.** Call `scripts/install-chromium.sh` from
`resolve_browser_binary`'s miss path (or from the tray's first `browser.open`),
add a `PATH` fallback for a system chromium, and add one step to the litmus that
asserts a *caller* exists rather than only the script's text.

---

## The safe-browser launcher defaults to host networking; its spec promises enclave-only egress through the proxy

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `scripts/launch-chromium.sh`, spec `chromium-safe-variant`
- Class: spec-vs-code
- Found by: tillandsias.org audit 2026-09-05, level 4

**Claim in the spec.** `openspec/specs/chromium-safe-variant/spec.md#L18-L19` —
"Full network isolation inside the enclave, with allowlist enforcement via the
proxy only; **no host-gateway internet fallback**"; and `#L137-L138` — "**THEN**
it SHALL connect through the enclave network **AND** all web egress SHALL
traverse the proxy/allowlist path".

**What the code does.** `run-safe-browser.sh` execs
`scripts/run-safe-browser.sh`, which execs
`scripts/launch-chromium.sh safe-browser "$URL" 9222 open_safe_window`
(`scripts/run-safe-browser.sh#L42`). That script's podman argv is built at
`scripts/launch-chromium.sh#L84-L98`, and line 90 reads:

```
"--network=${TILLANDSIAS_BROWSER_NETWORK:-host}"
```

Neither wrapper sets `TILLANDSIAS_BROWSER_NETWORK` — the string does not appear
in either file — so the documented entry point for the "safe" variant launches
the browser in the host network namespace, with direct internet access and no
proxy in the path. The surrounding flags (`--cap-drop=ALL`,
`--security-opt=no-new-privileges`, `--read-only`, tmpfs mounts) are all
correctly applied; only the network default contradicts the spec.

**Why it matters.** The variant's name and its spec both say the containment is
network containment, and that is the one control the default turns off. A user
running `./run-safe-browser.sh --url …` gets a hardened-but-unisolated browser
while every other property the spec lists is genuinely enforced, which is the
hardest kind of gap to notice.

**Smallest fix.** Default to `tillandsias-enclave` (`:-tillandsias-enclave`) and
keep `host` reachable only by explicitly setting `TILLANDSIAS_BROWSER_NETWORK`.

---

# Secure control wire

## The Windows tray reads the secure-wire variable directly, the single-reader ratchet has two slots of slack, and the WSL guest unit never receives the flag

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `crates/tillandsias-windows-tray/src/hvsocket.rs`, `scripts/check-secure-wire-single-reader.sh`, `crates/tillandsias-vm-layer/src/wsl.rs`
- Class: defect
- Found by: tillandsias.org audit 2026-09-05, level 5

**Claim in the guard.** `scripts/check-secure-wire-single-reader.sh#L3-L5` —
"`TILLANDSIAS_SECURE_CONTROL_WIRE` has ONE reader, and this ratchets the number
of files that name it down, never up." `#L39` sets
`BASELINE="${TILLANDSIAS_SECURE_WIRE_READER_BASELINE:-3}"`, and `#L37-L38` says
"Lower this as each is converted; it must never rise. 0 means the flip may
land."

**What the code does.** At this tag exactly one file outside the owning module
still reads the variable — `crates/tillandsias-windows-tray/src/hvsocket.rs#L29`,
`if std::env::var("TILLANDSIAS_SECURE_CONTROL_WIRE").as_deref() == Ok("on")`,
i.e. the case-sensitive byte comparison the guard's own header (`#L15-L20`)
identifies as the behaviour that made `On` silently plaintext. So the count is 1
against a baseline of 3: two more direct readers could be added, with two more
private interpretations of the value, and the guard would still print `ok`.

The other half is that the flag never reaches the Windows-side server.
`crates/tillandsias-vm-layer/src/vz.rs#L859` injects
`Environment=TILLANDSIAS_SECURE_CONTROL_WIRE=__SECURE_CONTROL_WIRE__` into the
macOS guest's systemd unit; the WSL equivalent, `fn headless_unit`
(`crates/tillandsias-vm-layer/src/wsl.rs#L90-L110`), writes only
`Environment=HOME=/root` and `Environment=XDG_RUNTIME_DIR=/run/user/0`. The
guest headless therefore always runs with the variable unset, so even a tray
told `on` would hand a Noise handshake to a server that is not expecting one —
which is precisely the one-sided flip the guard's header records as having
already happened once (`#L23-L27`, flipped at e6a80609f, reverted at 08a7d3cc7).

Worth recording alongside: the PSK root is `release_root_secret()`
(`crates/tillandsias-secure-channel/src/lib.rs#L86-L101`), which on debug builds
is the literal `b"tillandsias-dev-root-not-a-secret"` (`#L68`) and on release
builds is the SHA-256 of the shipped binary. Both are values an attacker holding
a public artifact can compute, so the channel provides version binding, not
confidentiality against anyone who has the release. The source comments say this
plainly; the word "secret" in the function name does not.

**Smallest fix.** Lower `BASELINE` to 1 now (it can only be lowered honestly if
it tracks reality), convert `hvsocket.rs` to
`tillandsias_control_wire::secure_wire_mode`, and add the
`TILLANDSIAS_SECURE_CONTROL_WIRE` line to `wsl.rs`'s `headless_unit` before the
default is flipped.

---

# Documentation and release ledger

## README's release ledger has no row for v56.9.5.1

- Tag: v56.9.5.1 (commit 77958f5)
- Area: `README.md`
- Class: stale-plan-entry
- Found by: tillandsias.org audit 2026-09-05, level 1

**Claim in the README.** `README.md#L107` — "The release skill appends a row per
release; STABLE marks channel promotions." The ledger table header is at `#L112`.

**What the file contains.** The newest row is `v56.9.4.1` (`#L114`), then
`v56.9.2.1` (`#L115`), then `v56.8.31.3` (`#L116`). The string `56.9.5.1` does
not appear anywhere in `README.md`, while `VERSION` at this tag reads
`56.9.5.1`.

**Why it matters.** The ledger is explicitly addressed to agents ("Agents doing
smoke curl-installs or jumpstarting work read the recent rows first",
`README.md#L103-L104`), so an agent on the newest daily reads a ledger whose
newest entry is a different release and has no way to see what changed under it.
It is also the mechanism by which this site's explanation pages decide what a
release shipped.

**Smallest fix.** Append the `v56.9.5.1` row, or make the release skill's ledger
append a gated step rather than a convention.

---

# Already filed — do not re-file

**The stale `stable` git tag.** Reported to the fleet coordinator on 2026-09-05,
which replied that it is filed as a p3 packet, that the cause was promotion
tagging the promoting checkout's local main, and that moving the published tag
is an operator decision. None of that is verifiable from this checkout, whose
mirror carries no `stable` ref. Recorded here so a
reader of this file does not open a duplicate.
