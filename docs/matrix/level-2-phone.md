# Tillandsias, explained simply

## What it is for, in one paragraph

The reason a grown-up wants one is narrower than "the cloud, but at home". Software you did not write — increasingly, AI assistants that write and run code for you — has to work somewhere. The choice is between your actual machine and a sealed room containing only the project folder you deliberately opened.[^1] Tillandsias is that room, plus the plumbing to prepare it and start your tools.

@fig:gate

## Is my stuff private, and who could see it?

The people who make Tillandsias operate no servers your copy talks to: no account, no sign-up, no usage tracking, no crash reporting, no identifier attached to you or your machine.[^2] Your logs stay on your own disk where you can read them, and leave only if you send them somewhere yourself. Any login you hand over goes into a secret store on your own machine — the project's own vault, whose key sits in your operating system's keychain, or on some hosts in a local file — never on anyone else's server.[^3][^16]

> GREEN: The privacy claim does not rest on anyone's intentions. There is no server of theirs to send anything to, so there is no decision to trust and none to reverse.[^2] It covers their side only — a service you sign into yourself still sees what you tell it.

## Does it cost money? Does it need the internet?

It costs nothing: free software under a licence that lets anyone read, run, modify and pass it on.[^4] You have already paid for the only hardware involved.

The internet is needed only for ordinary, visible reasons: fetching the program, fetching updates, reaching a service you chose.[^17] Local work can continue without sending it to an AI provider: language models can run on your own machine.[^18] That does not make every action offline-ready. Fetching a missing tool or model needs a connection, and a push configured for GitHub fails when its upstream cannot be reached.[^31]

## What happens when I turn it off? Can it break my computer?

Turning it off is the expected motion, not an interruption. Anything you saved is a real file on your real disk, untouched by the rebuild. Even the internal secrets the pieces use to talk to each other are re-registered at every start, so yesterday's messy shutdown cannot jam today's start.[^5]

> GREEN: That is written down as a required behaviour with named cases — the unclean shutdown among them — not left to the habits of whoever wrote the code.[^5]

Publishing your work has a rule that fits the same idea. Inside the sealed room you push to a mirror that lives on your own machine, not to the internet. The mirror passes the push onward and waits: it reports success only once the copy outside has durably accepted the same set of changes, so a success you can see is one that survives the room being thrown away.[^32] The mirror is also the only part that holds the credential for the outside service — it reads it when it pushes, and it never hands it to the room where your tools run.[^33]

As for damage: a misbehaving tool inside the sealed room sees only the folder you gave it.[^1] Wiping the installation and rebuilding is documented and supported, not a last resort.[^6] The cost you do pay is ordinary and reversible — it is a real virtual machine, so it holds real memory while running and gives it back when it stops. The system image it downloaded stays cached on your disk so the next start is quick; uninstalling clears it, though on a Mac you have to ask for that explicitly.[^20][^30]

## Sharpening one thing you were told

@fig:staircase

You were told they check that nothing got worse. Precisely: the project's stated objective is that the measured gap between what it specifies and what it builds must not grow,[^7][^21] and its build gate refuses a change that points at a specification that does not exist, or that adds a new failing test — a machine's verdict, not a person's.[^22][^23]

Two honest limits follow, in the project's own words. Passing tests are *evidence, not proof* — they show no contradiction was found, not that none exists.[^8] And "never worse" means settling toward some floor, not that the floor is zero; the stronger mathematical result that would guarantee zero is explicitly not claimed.[^9]

## Lots of small maps, one destination

An AI does not swallow a repository as one magic answer. It is given selected
source, rules and a request; it suggests a small change; then people and tests
decide whether to keep that change. Think of the selected material as a map, not
as every file turned literally into a vector. The next job starts from the newly
saved repository, so it can use what the earlier job learned.

Different jobs have different nearby destinations: a security repair, a clearer
screen, or a working installer. They all share the larger destination of matching
what the project promised. We can measure particular gaps and refuse a known
regression,[^7][^21] but a row of successful changes is not proof that the whole
journey reaches perfection.[^8][^9]

## Where it falls short today

> RED: On Macs, the application has not yet passed Apple's inspection service, so a copy downloaded with a web browser is blocked on first launch; the recommended one-line install sidesteps that only by not going through a browser.[^10]
> PATH: The fix — an Apple Developer identity and notarization — is written up and costed.[^11] The build script is already wired: hand it the signing identity and notary credentials and it notarizes.[^24] The release workflow has not yet been given them, and enrolment is still pending.[^25][^10]

> RED: One Windows package in a past release went out without its signature, which makes it not merely warned-about but impossible to install, with no user-side workaround.[^12]
> PATH: That one package is now withheld from a release whenever it is unsigned;[^26] the other Windows downloads still publish unsigned, with the only warning in the build log,[^27] and the signing route has been chosen but not yet put in place.[^13]

> NOTE: A built-in "expert" feature once gave confident answers with no sources at all: it described a careful research procedure, did not run it, returned an empty citation list, and stamped its own output verified anyway.[^14]
> GREEN: It was switched off and replaced: the shipped configuration now points the assistant at a grounded service that either cites the sources it actually used or plainly refuses.[^28] The replacement was checked live on 2026-09-02 and is now in the stable release.[^29] One limit remains below.

> RED: After installing, you cannot tell from the program what was installed. It prints a version number that was baked in when it was compiled, and nothing on it records which snapshot of the code it was built from.[^34] So "this is the stable release, which trails the newest code on purpose" and "this download was stale" look exactly the same from the outside, and neither the person who installed it nor the people who built it can tell which happened.[^35]
> PATH: The project has written the shortcoming down and is tracking it, including what a fix would have to record; it has not yet reached a released build, so the tracking entry is linked here on the development branch rather than in the release this page describes.[^35]

> RED: Portability evidence for the replacement’s small scripting layer is still missing from the Mac and Windows build lanes.[^15]
> PATH: Run that layer on those hosts and record the evidence; the task explicitly remains open until then.[^15]

Two install problems and one feature that once promised more than it delivered and has since been replaced. None touch the privacy story, and all three are here because the project's own checking found them.

## Footnotes

[^1]: What a workspace can reach, and why that isolation exists to protect you from the tools | PRIVACY.md#L32-L40
    > Each workspace sees the project you opened, not your whole filesystem. That isolation exists to protect you from the tools, not to hide anything from you.
[^2]: "Tillandsias collects nothing" — no account, no telemetry, no analytics, no server | PRIVACY.md#L5-L17
    > **Tillandsias collects nothing.** There is no account to create, no telemetry, no analytics, and no server operated by us that your installation talks to.
[^3]: Credentials in a local secret store on your machine; logs kept on your own disk | PRIVACY.md#L41-L44
    > **Credentials you provide** (for example, a GitHub login you initiate) are stored in a local secret store on your machine.
[^4]: GNU General Public License, version 3 | LICENSE#L1-L2
    > GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
[^5]: Internal secrets are removed and reissued at every start, so an unclean shutdown leaves nothing stale | openspec/specs/ephemeral-secret-refresh/spec.md#L10-L25
    > The system SHALL check for existing podman secrets before creation. If a secret exists from a prior unclean shutdown, it SHALL be removed and recreated with fresh content.
[^6]: "Designed to be wiped and rebuilt freely" | PRIVACY.md#L46-L47
    > You can remove all of it at any time by resetting or uninstalling; the application is designed to be wiped and rebuilt freely.
[^7]: The convergence objective: minimise the measured distance between specification, code and reality | methodology/convergence.yaml#L2-L8
    > objective: | Minimize: Δ(spec ↔ code) + Δ(code ↔ cheatsheet) + Δ(cheatsheet ↔ reality) + Δ(litmus_binding ↔ spec)
[^8]: Evidence boundaries — traceability and passing tests are evidence, not proof of correctness | methodology/philosophy.yaml#L249-L252
    > Traceability, version matching, litmus success, and CRDT metadata convergence are evidence. They are not proof of semantic correctness by themselves.
[^9]: The stronger contraction result is explicitly not claimed | methodology/math-foundations.yaml#L107-L120
    > The methodology does not currently claim Banach-style contraction. It can report decreasing residuals, but it has not proven a contraction constant over a complete metric space of project states.
[^10]: Install instructions warning that a browser download hits a Gatekeeper block on first launch | README.md#L27-L45
    > Tillandsias is signed but not yet notarized (Apple Developer enrollment is pending), and macOS tags anything a *browser* downloads with `com.apple.quarantine` — so the .dmg route hits a Gatekeeper block on first launch, while `curl` does not tag at all and the app opens normally.
[^11]: Recorded options and costs for Apple signing and notarization: which steps need paid membership | plan/issues/macos-gatekeeper-signing-options-2026-08-29.md#L39-L48
    > | Developer ID Application certificate | **Yes** — no free-tier equivalent.
[^12]: The unsigned Windows package is uninstallable, with no user-side workaround | plan/issues/store-msix-submission-blockers-2026-08-31.md#L26-L40
    > **Consequence for the pending signing decision.** The unsigned MSIX (`0x800B0100`, packet 722-w7a2) blocks the **GitHub-release** channel only. It does not block the Store channel at all.
[^13]: The chosen signing route for the Windows release channel | plan/issues/windows-signing-research-2026-08-16.md#L1-L25
    > **SignPath Foundation is the signing path for the GitHub-release channel.** Packet 722-w7a2 is reshaped, not closed: its deliverable changes from "an Azure Trusted Signing account" to the SignPath Foundation chain, with Azure **Artifact Signing** as the recorded fallback.
[^14]: Audit of the shipped "local expert" facade: answers stamped valid with no retrieval and no citations | openspec/changes/expert-serve-grounded-pipeline/proposal.md#L1-L24
    > The `pipeline` CLI arm did no retrieval and no validation, yet stamped every response `validated: true` with `confidence: 0.5` and `citations: []`
[^15]: The one item still open on the replacement: portability evidence from the Mac and Windows build lanes | openspec/changes/expert-serve-grounded-pipeline/tasks.md#L52-L54
    > 4.5 mlua portability evidence from the darwin/msys lanes (902-5bf9's blocking criterion) — OPEN: needs those hosts; the Lua surface kept here is deliberately thin enough to replace if evidence fails.
[^16]: Where no OS keyring is available, the key that unlocks the local vault falls back to a local file | crates/tillandsias-headless/src/vault_bootstrap.rs#L1363-L1364
    > Fallback: file (populated by keychain_set_blocking when keyring unavailable,
[^17]: Software sources — package repositories and release downloads, reached at your direction | PRIVACY.md#L51-L56
    > **Software sources** — package repositories and release downloads (for example GitHub, Linux distribution mirrors, and language package registries) to fetch the software it runs.
[^18]: AI providers only if you configure one; language models can run entirely on your own machine | PRIVACY.md#L60-L63
    > **AI providers, only if you configure one.** Tillandsias can run language models entirely on your own machine. If you instead configure a remote provider, the content you send is transmitted to that provider under their terms.
[^20]: The downloaded system image is cached on the host between runs | openspec/specs/vm-provisioning-lifecycle/spec.md#L42-L49
    > cached at `~/.local/share/tillandsias/rootfs-fedora-44-<sha256>.tar.xz` (on macOS: `~/Library/Application Support/tillandsias/rootfs-…`; on Windows: `%LOCALAPPDATA%\tillandsias\rootfs-…`).
[^21]: The rule that convergence is monotonic: once achieved, divergence must be detectable | methodology/convergence.yaml#L56-L58
    > - Convergence is monotonic under normal operation: once achieved, divergence must be detectable
[^22]: The build's trace ratchet: a new reference to a specification that does not exist fails the build | build.sh#L965-L973
    > The ratchet fails in BOTH directions: a new ghost, or a baseline entry
[^23]: The build's test verdict is a ratchet: a failure not on the known list is a new regression | build.sh#L1521-L1526
    > THE VERDICT IS A RATCHET, NOT CARGO'S EXIT CODE.
[^24]: The build script notarizes and staples when given a signing identity and the notary credentials | scripts/build-macos-tray.sh#L255-L278
    > say "notarize: submitting (this waits for Apple's verdict)"
[^25]: The release workflow runs the macOS build script with no credentials handed to it | .github/workflows/release.yml#L468-L469
    > run: scripts/build-macos-tray.sh
[^26]: The unsigned Windows installer package is withheld from a release rather than shipped uninstallable | .github/workflows/release.yml#L647-L658
    > ::warning::withholding unsigned MSIX from release assets: $($_.Name) (uninstallable without a signature; set TILLANDSIAS_SIGNING_ACCOUNT to publish it)
[^27]: The other Windows downloads still publish unsigned, with a warning in the build log | .github/workflows/release.yml#L641-L646
    > ::warning::TILLANDSIAS_SIGNING_ACCOUNT is unset — publishing UNSIGNED Windows artifacts (plan packet 722-w7a2)
[^28]: The shipped assistant configuration points at the grounded expert service: citations kept only if used, typed refusals otherwise | images/default/config-overlay/opencode/config.json#L18-L30
    > "description": "Grounded local experts: retrieval from the published spec index, citations kept only if used, typed unsupported: refusals — served by tillandsias-plan expert-serve beside the MCP servers (order 920-pxg6).",
[^29]: The live end-to-end check of the replacement, recorded 2026-09-02 in the daily channel | openspec/changes/expert-serve-grounded-pipeline/tasks.md#L86-L98
    > 5.10 Live OpenCode session verification against a running expert-serve — DONE on macuahuitl-tillandsias-forge 2026-09-02
[^30]: Uninstalling removes the cached image, except on macOS where it is preserved unless you ask for a full wipe | scripts/uninstall.sh#L124-L128
    > Preserving the VM image in $DATA_DIR (use --wipe to remove it).

[^31]: A failed upstream push is refused without partially updating refs | openspec/specs/git-mirror-service/spec.md#L225-L230
    > the forge's `git push` SHALL return non-zero

[^32]: A client's success means the upstream durably accepted the same refs | images/git/pre-receive-hook.sh#L6-L8
    > Validates ledger YAML, then synchronously relays the proposed ref transaction
    > upstream before accepting it locally. A client success therefore means the
    > configured upstream has durably accepted the same atomic ref set.
[^33]: The upstream token is read by the git service and never enters a workspace container | openspec/specs/git-mirror-service/spec.md#L15-L16
    > The git service reads the GitHub token from Vault at
    > push time via Vault CLI; the token never crosses into a forge container.

[^34]: The version shown is the version file as it stood when the program was compiled | crates/tillandsias-headless/src/main.rs#L121-L121
    > pub(crate) const VERSION: &str = include_str!("../../../VERSION");
[^35]: The tracking entry for this shortcoming, on the development branch | https://github.com/8007342/tillandsias/blob/linux-next/plan/index.d/20260914t185710z-1188-mm9y-installed-launcher-has-no-provenance-lenovinha.yaml
