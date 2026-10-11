# Tillandsias, explained simply

## What it is for, in one paragraph

The reason a grown-up wants one is narrower than "the cloud, but at home". Software you did not write — increasingly, AI assistants that write and run code for you — has to work somewhere. The choice is between your actual machine and a sealed room containing only the project folder you deliberately opened.[^1] Tillandsias is that room, plus the plumbing to prepare it and start your tools.

@fig:gate

## Is my stuff private, and who could see it?

The people who make Tillandsias operate no servers your copy talks to: no account, no sign-up, no usage tracking, no crash reporting, no identifier attached to you or your machine.[^2] Your logs stay on your own disk where you can read them, and leave only if you send them somewhere yourself. Any login you hand over goes into a secret store on your own machine — the program's own vault, whose key sits in your operating system's keychain, or on some computers in a local file — never on anyone else's server.[^3][^16]

This does not depend on trusting anyone's intentions: there is no server of theirs to send anything to.[^2] It covers their side only. A service you sign into yourself still sees what you tell it.[^18]

## Does it cost money? Does it need the internet?

It costs nothing: free software under a licence that lets anyone read, run, modify and pass it on.[^4] You have already paid for the only hardware involved.

The internet is needed only for ordinary, visible reasons: fetching the program, fetching updates, reaching a service you chose.[^17] Local work can continue without sending it to an AI provider: language models can run on your own machine.[^18] That does not make every action offline-ready. Fetching a missing tool or model needs a connection, and publishing your work to GitHub fails when GitHub cannot be reached.[^31]

## What happens when I turn it off? Can it break my computer?

Turning it off is the expected motion, not an interruption. Anything you saved is a real file on your real disk, untouched by the rebuild. Even the internal passwords the pieces use to talk to each other are replaced at every start, so yesterday's messy shutdown cannot jam today's start.[^5]

Installing a new release is a bigger change than turning it off: the Linux, Mac and Windows installers all reset the program's own working state and set it up again.[^36][^37][^38] On Linux this reset is gentle: it rebuilds the program's parts but deletes none of your stored data, so your downloads survive, and so do your sign-ins as long as your keychain can still unlock them.[^39] Windows runs the same gentle reset without telling you first.[^38][^40] The Linux and Mac installers tell you before they reset; to skip the part that deletes things, set `TILLANDSIAS_DESTRUCTIVE_RESET_OK=0` before installing.[^37]

> RED: On a Mac the reset is not gentle yet. It still deletes your saved vault keys and the secret store, although the project's own rules say every platform's reset must keep them.[^41][^42]
> PATH: A fix is being written. It is not in any release yet.

Publishing your work follows the same idea. Inside the sealed room you push to a copy that lives on your own machine, not to the internet. That copy passes your work on and waits: it reports success only once the copy outside has really accepted the same changes, so a success you can see is one that survives the room being thrown away.[^32] It is also the only part that holds your GitHub login — it uses it when it publishes, and never hands it to the room where your tools run.[^33]

As for damage: a misbehaving tool inside the sealed room sees only the folder you gave it.[^1] Wiping the installation and rebuilding is documented and supported, not a last resort.[^6] The cost you do pay is ordinary and reversible. It is a real virtual machine, so it holds real memory while running and gives it back when it stops. The system image it downloaded stays on your disk so the next start is quick; uninstalling clears it, though on a Mac you have to ask for that explicitly, and the uninstaller makes you type a confirmation first.[^20][^30][^43]

## Will an update break what already works?

@fig:staircase

Each change to Tillandsias has to pass its tests, and a machine refuses a change that makes a test fail that was not already known to fail.[^23]

Two honest limits come with that. Passing tests are *evidence, not proof*: they show no problem was found, not that none exists.[^8] And "never worse" means settling toward some floor, not that the floor is zero problems.[^9]

## Where it falls short today

> RED: On a Mac, the app has not yet passed Apple's inspection, so a copy downloaded with a web browser is blocked the first time you open it. The recommended one-line install avoids that only because it does not go through a browser.[^10]
> PATH: The fix needs a paid Apple developer membership, which is still pending.[^10][^11] The build is already able to do the inspection step once it has those credentials.[^24]

> RED: The Windows downloads are not signed yet.[^27] One kind of Windows installer package cannot be installed at all without a signature, so it is left out of a release until signing is in place.[^12][^26]
> PATH: The signing service has been chosen but is not set up yet.[^13]

> RED: The Linux program shows a version number but not the exact source it was built from, so two builds with the same number cannot be told apart.[^34][^35]
> PATH: It is recorded as an open problem in this release.[^35]

None of these touch the privacy answer above.

## Footnotes

[^1]: What a workspace can reach, and why that isolation exists to protect you from the tools | PRIVACY.md#L32-L40
    > Each workspace sees the project you opened, not your whole filesystem. That isolation exists to protect you from the tools, not to hide anything from you.
[^2]: "Tillandsias collects nothing" — no account, no telemetry, no analytics, no server | PRIVACY.md#L5-L17
    > **Tillandsias collects nothing.** There is no account to create, no telemetry, no analytics, and no server operated by us that your installation talks to.
[^3]: Credentials in a local secret store on your machine; logs kept on your own disk | PRIVACY.md#L41-L44
    > **Credentials you provide** (for example, a GitHub login you initiate) are stored in a local secret store on your machine.
[^4]: GNU General Public License, version 3 | LICENSE#L1-L2
    > GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
[^5]: Internal passwords are removed and reissued at every start, so an unclean shutdown leaves nothing stale | openspec/specs/ephemeral-secret-refresh/spec.md#L10-L25
    > The system SHALL check for existing podman secrets before creation. If a secret exists from a prior unclean shutdown, it SHALL be removed and recreated with fresh content.
[^6]: "Designed to be wiped and rebuilt freely" | PRIVACY.md#L46-L47
    > You can remove all of it at any time by resetting or uninstalling; the application is designed to be wiped and rebuilt freely.
[^8]: Passing tests are evidence, not proof that the program is correct | methodology/philosophy.yaml#L249-L252
    > Traceability, version matching, litmus success, and CRDT metadata convergence are evidence. They are not proof of semantic correctness by themselves.
[^9]: The project does not claim it will reach zero problems | methodology/math-foundations.yaml#L107-L120
    > The methodology does not currently claim Banach-style contraction. It can report decreasing residuals, but it has not proven a contraction constant over a complete metric space of project states.
[^10]: The install instructions: a Mac download through a browser is blocked on first launch | README.md#L27-L45
    > Tillandsias is signed but not yet notarized (Apple Developer enrollment is pending), and macOS tags anything a *browser* downloads with `com.apple.quarantine` — so the .dmg route hits a Gatekeeper block on first launch, while `curl` does not tag at all and the app opens normally.
[^11]: Apple signing and inspection options, and which steps need a paid membership | plan/issues/macos-gatekeeper-signing-options-2026-08-29.md#L39-L48
    > | Developer ID Application certificate | **Yes** — no free-tier equivalent.
[^12]: An unsigned Windows installer package of this kind cannot be installed | plan/issues/store-msix-submission-blockers-2026-08-31.md#L26-L40
    > **Consequence for the pending signing decision.** The unsigned MSIX (`0x800B0100`, packet 722-w7a2) blocks the **GitHub-release** channel only. It does not block the Store channel at all.
[^13]: The signing service chosen for the Windows downloads | plan/issues/windows-signing-research-2026-08-16.md#L1-L25
    > **SignPath Foundation is the signing path for the GitHub-release channel.** Packet 722-w7a2 is reshaped, not closed: its deliverable changes from "an Azure Trusted Signing account" to the SignPath Foundation chain, with Azure **Artifact Signing** as the recorded fallback.
[^16]: Where no keychain is available, the vault's key falls back to a local file | crates/tillandsias-headless/src/vault_bootstrap.rs#L2943-L2943
    > Fallback: file (populated by keychain_set_blocking when keyring unavailable,
[^17]: Software sources — package repositories and release downloads, reached at your direction | PRIVACY.md#L51-L56
    > **Software sources** — package repositories and release downloads (for example GitHub, Linux distribution mirrors, and language package registries) to fetch the software it runs.
[^18]: AI providers only if you configure one; language models can run entirely on your own machine | PRIVACY.md#L60-L63
    > **AI providers, only if you configure one.** Tillandsias can run language models entirely on your own machine. If you instead configure a remote provider, the content you send is transmitted to that provider under their terms.
[^20]: The downloaded system image is cached on the host between runs | openspec/specs/vm-provisioning-lifecycle/spec.md#L48-L51
    > cached at `~/.local/share/tillandsias/rootfs-fedora-44-<sha256>.tar.xz` (on macOS: `~/Library/Application Support/tillandsias/rootfs-…`; on Windows: `%LOCALAPPDATA%\tillandsias\rootfs-…`).
[^23]: The test verdict: a failure not already on the known-failing list is refused as new | build.sh#L2451-L2451
    > THE VERDICT IS A RATCHET, NOT CARGO'S EXIT CODE.
[^24]: The Mac build inspects and seals the app when given Apple's credentials | scripts/build-macos-tray.sh#L267-L290
    > say "notarize: submitting (this waits for Apple's verdict)"
[^26]: That installer package is left out of a release when it is unsigned | .github/workflows/release.yml#L751-L751
    > ::warning::withholding unsigned MSIX from release assets: $($_.Name) (uninstallable without a signature; set TILLANDSIAS_SIGNING_ACCOUNT to publish it)
[^27]: The other Windows downloads are published unsigned | .github/workflows/release.yml#L740-L740
    > ::warning::TILLANDSIAS_SIGNING_ACCOUNT is unset — publishing UNSIGNED Windows artifacts (plan packet 722-w7a2)
[^30]: Uninstalling removes the cached image, except on macOS where it is preserved unless you ask for a full wipe | scripts/uninstall.sh#L228-L228
    > Preserving the VM image in $DATA_DIR (use --wipe to remove it).
[^31]: A publish that cannot reach GitHub fails instead of half-succeeding | openspec/specs/git-mirror-service/spec.md#L225-L230
    > the forge's `git push` SHALL return non-zero
[^32]: Success means the faraway copy really accepted the same changes | images/git/pre-receive-hook.sh#L6-L8
    > Validates ledger YAML, then synchronously relays the proposed ref transaction
    > upstream before accepting it locally. A client success therefore means the
    > configured upstream has durably accepted the same atomic ref set.
[^33]: The GitHub login is read by the publishing service and never enters a workspace | openspec/specs/git-mirror-service/spec.md#L15-L16
    > The git service reads the GitHub token from Vault at
    > push time via Vault CLI; the token never crosses into a forge container.
[^34]: The version shown is the one written into the program when it was built | crates/tillandsias-headless/src/main.rs#L161-L161
    > pub(crate) const VERSION: &str = include_str!("../../../VERSION");
[^35]: The open problem: the Linux program records no build commit | plan/index.d/20260914t185710z-1188-mm9y-installed-launcher-has-no-provenance-lenovinha.yaml#L27-L43
    > the Linux launcher has no build.rs reading it.
[^36]: The Linux installer runs the reset | scripts/install.sh#L340-L340
    > "$INSTALL_PATH" --reset-state --debug
[^37]: The Mac installer runs the reset, and the setting that skips its deleting part | scripts/install-macos.sh#L290-L290
    > TILLANDSIAS_DESTRUCTIVE_RESET_OK=0 skips the destruction
[^38]: The Windows installer runs the reset without asking | scripts/install-windows.ps1#L968-L968
    > --reset-state < NUL
[^39]: The Linux reset rebuilds the program's parts and deletes no stored data | crates/tillandsias-headless/src/main.rs#L10474-L10490
    > A SOFT reset destroys DERIVED state only and deletes NO store under any
[^40]: The Windows installer's rule: the gentle reset, with no prompt | scripts/install-windows.ps1#L951-L952
    > So SOFT reset is the default only and forever.
[^41]: The Mac reset deletes the saved vault keys and the vault data | crates/tillandsias-macos-tray/src/reset_state.rs#L286-L292
    > remove_path(&cache_root.join("vault-data"))?;
[^42]: The project's rule: every platform's reset must keep your data | openspec/specs/host-state-lifecycle/spec.md#L180-L182
    > `--reset-state` on every platform SHALL be a SOFT reset: it destroys every item of derived state and SHALL NOT remove, move or rewrite any item of operator data.
[^43]: The uninstaller asks for a typed confirmation and refuses without a terminal | scripts/uninstall.sh#L184-L185
    > Type \"delete\" to uninstall, or press Enter to cancel:
