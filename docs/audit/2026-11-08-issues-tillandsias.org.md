# Site issues from the v56.11.7.1 refresh

The refresh to stable `v56.11.7.1` (commit `8351a0f3ff4552b6ec0daadc3984e2a2d341f91c`)
re-anchored every citation but ten. Levels 1 and 5 moved to `v56.11.7.1`.
Levels 2, 3 and 4 stay at `v56.10.20.1` until all ten are settled, because a
level moves only when all of its citations do.

Seven of the ten need a person: the evidence behind each claim changed, and
the claim itself may now be false (the last two sections). The other three
are plain moves. The claim still holds, and the new target and quote are ready
(the next section). They can't be applied yet, because the build checks a
level's footnotes at that level's pin.

## Ready re-cites, to apply when Levels 3 and 4 move

The claim was checked at `v56.11.7.1` and holds. Replace the target and quote.

- level-3-power `crates/tillandsias-headless/src/main.rs#L26127-L26127` (`[^37]`,
  "A regression test pins the CA mount and the absence of CA overrides"). The
  test was renamed. New: `crates/tillandsias-headless/src/main.rs#L34304-L34320`,
  quote `opencode forge args must mount the single runtime CA input; got {args:?}`.
  The same block still forbids `GIT_SSL_CAINFO=`, `SSL_CERT_FILE=`,
  `REQUESTS_CA_BUNDLE=` and `NODE_EXTRA_CA_CERTS=`.
- level-4-security `crates/tillandsias-podman/src/policy.rs#L189-L193` (`[^98]`,
  "What the checker refuses beside a missing flag"). The userns test is now a
  helper that also accepts `keep-id:` with options, which is still an identity
  mapping. New: `crates/tillandsias-podman/src/policy.rs#L306-L309`, quote
  `if arg == "--privileged" || arg.starts_with("--privileged=") || flag_value(arg, next, "--userns").is_some_and(|value| !is_keep_id(value)) || flag_value(arg, next, "--cap-add").is_some_and(|value| value == "ALL")`.
- level-4-security `README.md#L52-L53` (`[^1]`, "Linux provisions no VM"). The
  README was rewritten. New: `README.md#L54-L57`, quote
  ``rootless Podman directly on Linux; on macOS a Fedora VM under Apple's Virtualization.framework, reached over vsock (`vm-provisioning-lifecycle`, `vsock-transport`); on Windows a Fedora WSL2 distro (`wsl-runtime`).``
  Suggested label: "On Linux, rootless Podman runs directly on the host; macOS
  gets a Fedora VM, Windows a Fedora WSL2 distro".

## The vault no longer keeps a fallback copy of its unlock share on disk

- Tag: v56.11.7.1 (commit 8351a0f3ff4552b6ec0daadc3984e2a2d341f91c)
- Area: vault bootstrap (`crates/tillandsias-headless/src/vault_bootstrap.rs`)
- Class: doc-drift (site claim against shipped code)
- Found by: tillandsias.org refresh 2026-11-08, levels 2, 3 and 4

Targets, as the refresh printed them:

- level-2-phone `crates/tillandsias-headless/src/vault_bootstrap.rs#L4070-L4072` (`[^16]`)
- level-3-power `crates/tillandsias-headless/src/vault_bootstrap.rs#L3145-L3145` (`[^126]`)
- level-3-power `crates/tillandsias-headless/src/vault_bootstrap.rs#L5351-L5351` (`[^127]`)
- level-4-security `crates/tillandsias-headless/src/vault_bootstrap.rs#L5351` (`[^83]`)
- level-4-security `crates/tillandsias-headless/src/vault_bootstrap.rs#L3167-L3168` (`[^84]`)
- level-4-security `crates/tillandsias-headless/src/vault_bootstrap.rs#L3329-L3330` (`[^85]`)

**Claim on the site.** Level 4 RED: "where no OS keyring is available the
launcher still writes the share to a plaintext file in its cache directory, and
inside a VM guest it writes that file on initialization … the ordinary key
lookup can still use a persistent file". Level 3 says the same in "Survives a
stop". Level 2 says the vault's key sits "on some computers in a local file".

**What the code does.** None of the quoted lines exist at `v56.11.7.1`. The
fallback reader (`read_credential_fallback`), the "both writes are always
attempted" path and the file branch of the keyring check are gone. The list
of old file names now carries the comment "Nothing writes or reads them now;
these names exist only so the purge can delete what an older build left
behind" (`vault_bootstrap.rs#L100-L103`). The purge itself,
`vault_bootstrap.rs#L125-L129`: "Zero-fill and unlink every
CREDENTIAL_FALLBACKS file in `dirs`, without reading it. Idempotent, so it runs
at every start", called at `vault_bootstrap.rs#L4672`. The change landed as
`53dc5be4f` ("a guest keeps no Vault token or unseal share on disk; it waits
for the host instead"). The non-vault stub of `has_shamir_share_in_keyring`
now simply returns `false` (`#L3566`).

**Why it matters.** Three levels tell readers a weakness exists that the
stable release appears to have fixed. A security RED that is no longer true
misleads the reader as much as a missing one.

**Smallest fix.** Re-read the vault claims on Levels 2, 3 and 4 against
`v56.11.7.1` (audit-site-claims), then either retire the Level 4 RED or narrow
it to what is still true. For example, the purge runs at startup, so a guest
that never restarts after upgrading may still have an old file. Re-cite each
footnote to the purge.

## The Mac notarization claim lost its source

- Tag: v56.11.7.1 (commit 8351a0f3ff4552b6ec0daadc3984e2a2d341f91c)
- Area: runtime README, install section
- Class: doc-drift
- Found by: tillandsias.org refresh 2026-11-08, level 2

Target, as the refresh printed it: level-2-phone `README.md#L27-L45` (`[^10]`).

**Claim on the site.** Level 2 RED: "On a Mac, the app has not yet passed
Apple's inspection, so a copy downloaded with a web browser is blocked the
first time you open it."

**What the code does.** The runtime README was rewritten (`d178ed8be`). It
still offers the `.dmg` and the one-line installer, but it no longer says
whether the app is notarized. The new README has nothing to cite for this RED,
for or against.

**Why it matters.** The RED may still be true, but the site can no longer
point to evidence for it at the pinned release.

**Smallest fix.** Find current evidence of the notarization status (release
workflow, signing spec or a smoke report at `v56.11.7.1`). Then re-cite the
RED to it, or retire the RED if the app is now notarized.
