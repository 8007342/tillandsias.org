# Tillandsias, explained like you are five

## A tiny cloud on your own table

When you open a website, you borrow a computer in a huge building far away — **the cloud**. Tillandsias builds a tiny cloud **inside your own computer**, so your things never go to a stranger's building.

It is a doll house. Your computer is the table. Tillandsias puts a clean pretend-computer on it, and inside that, little rooms, one program each.

Everything you run there has one plain word: **app** — a small set of words, chosen on purpose, written down as a promise.[^1] A machine reads every line of the waking-up message and fails if a wrong word sneaks in.[^6]

> GREEN: On the waking-up message the promise is machine-checked, not just hoped for.

## Nobody goes outside except the doorman

The rooms have no doors outside. They share one private hallway, and exactly **one** room — the doorman — may step out to the internet. Everyone else asks it.[^2]

The honest bit: they once kept a *list* of who lived there, and six residents moved in unnoticed. So they binned it for a machine that reads the real building.[^10]

Robot helpers may only play **inside** the doll house.[^11] If one breaks something, it was pretend.

> GREEN: This part works great — one way out, kept honest by a machine.

## Broken things get thrown away, not glued

@fig:ephemeral

If a room breaks, nobody glues it. It goes in the bin and Tillandsias builds a fresh one from the same recipe. Gluing is banned: every glue job broke something *underneath* next.[^3]

Your real work lives outside the doll house and never gets swept.[^12]

## How the grown-ups keep getting better at it

First they write down what a thing should do, so clearly nobody could argue whether it came true. Then a machine presses the promise: green light or red.

**Every time they fix something, they check that nothing else got worse[^4] — and they write down what they checked.**

They are honest: less broken every time does **not** mean ending up perfect — only creeping toward *some* resting place, maybe not zero. They wrote that down.[^4]

They work in many tiny fast tries, not one long careful think — small tries find the answer sooner, so long as each is only a *little* wrong.[^5]

> PLAUSIBLE: It sounds right and works for them. But the sum first written to prove it[^5] needs every try to stand alone, and theirs do not — each reads what the last one learned. They took that proof back:[^13] the idea stays, the proof is owed.

Anyone may have it, read it and change it, free.[^14]

## Things that are still broken, and one that got fixed

> NOTE: This one got fixed. The doorman's key for sealed letters once sat unlocked in a shared scratch drawer, for anyone to read.[^7] Since August[^16] it travels in a proper safe, locked so only you can read it.[^15]

> RED: In this release the key lives in the shared drawer,[^17] locked a blink *after* it goes in,[^18] and a "check the lock" chore still runs on every grown-up's computer.[^19]
> PATH: The daily builds moved the drawer out of the shared space on 4 September 2026.[^20][^22] Locking it first, then retiring the chore, is the written next job.[^18]

> RED: The little status badge in the corner still says "Ready (podman starting…)", "Provisioning…" and "VM failed":[^9] machine words a second written promise forbids.[^21]
> PATH: A written plan gives the badges one shared word list. It waits on a person, not a robot, to pick the wording: changing what you see needs a human's yes.[^8]

## Footnotes

[^1]: The rule that the user always hears "app", never the machine words | openspec/specs/app-lifecycle/spec.md#L12-L22
    > All container operations SHALL be presented to the user as "app" actions. The words "container", "pod", "image", or "runtime" MUST NOT appear in any user-facing text.
[^2]: One way out: only the doorman may step outside | openspec/specs/enclave-network/spec.md#L10-L12
    > Only the proxy is dual-homed for external access; all other members communicate exclusively through the enclave.
[^3]: Throw away and rebuild, never hand-patch — with the real story of gluing making it worse | methodology/philosophy.yaml#L63-L78
    > Therefore the DEFAULT response to a borked host/VM/guest/podman/stack layer is to DESTROY and RECREATE it, never to hand-patch it forward.
[^4]: The grown-ups writing down what they have *not* proven: "getting better every time" means nothing gets worse and the leftovers shrink, not "ends up perfect" | methodology/math-foundations.yaml#L108-L120
    > Without that metric proof, "monotonic convergence" means ordered non-regression plus finite residual descent, not metric contraction.
[^5]: Many small fast tries beat one big slow one — but only if each try's wrongness stays small; this is the block that still claims the strong law at this release | methodology/philosophy.yaml#L7-L25
    > Instead make each prompt SMALL and FAST with a CONTROLLED, BOUNDED skew, then iterate — the STRONG LLN (almost-sure convergence) makes the stream of iterations converge hard.
[^6]: The word list for the waking-up message, and the test that checks every line it can emit | crates/tillandsias-headless/src/bringup_progress.rs#L119-L175
    > fn no_internals_vocabulary_in_any_emitted_line() { for total in 1..=12 { let mut p = BringUpProgress::with_enabled(total, true); for _ in 0..total { let line = p.next_line().to_ascii_lowercase(); for banned in BANNED { assert!( !line.contains(banned),
[^7]: The original write-up of the doorman's key problem (15 August 2026), with the three fixes it proposed | plan/issues/proxy-ca-private-key-world-readable-2026-08-15.md#L38-L46
    > 1. Preferred: deliver the key as a podman secret (the entrypoint's secret branch already handles ownership correctly and becomes REACHABLE), or
[^8]: The open plan to give both badges one shared word list, and why a person must sign it off | plan/issues/tray-string-parity-and-i18n-layer-2026-08-09.md#L104-L130
    > Reconciling existing drift **changes a user-visible string on whichever platform loses**. `spec:tray-ux` "UX curation governance" forbids that without recorded operator approval for the exact surface change.
[^9]: The badge text that breaks the rule | crates/tillandsias-macos-tray/src/action_host.rs#L256-L267
    > VmPhase::Ready => "\u{1F7E1} Ready (podman starting\u{2026})".to_string(),
[^10]: Why the hand-written resident list was replaced by a checking machine | openspec/specs/enclave-network/spec.md#L12
    > A hand-maintained prose list went stale by SIX members between 2026-07 and 2026-08-30 (order 245 P8) — it still said "forge, git, inference, and proxy" after vault, the router, the nix cache, the catalog service, the observatorium web and the ssh-lane sidecar had all joined.
[^11]: The rule that robot helpers run only inside the doll house | openspec/specs/forge-as-only-runtime/spec.md#L280-L282
    > the agent process MUST appear only inside the forge container
[^12]: Sweeping a room never touches your real work | openspec/specs/app-lifecycle/spec.md#L75-L77
    > the container is removed, project-specific cache data is deleted, but the project source directory in `~/src` is never touched
[^13]: The grown-ups taking the proof back: the rule they used needs each try to be independent, and theirs are not | methodology/philosophy.yaml#L29-L37 @v56.9.5.1
    > CITATION WITHDRAWN (order 976-bd3n, external review 2026-09-03). This block previously claimed the STRONG LLN — almost-sure convergence — for the stream of iterations. INDEPENDENCE IS A HYPOTHESIS OF THAT THEOREM, NOT A STYLISTIC ASSUMPTION, and this system deliberately violates it
[^14]: The licence: anyone may have it, read it and change it | LICENSE#L1-L2
    > GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
[^15]: The fix: the key is locked to its owner, and reaches the doorman as a secret rather than through the file | crates/tillandsias-headless/src/main.rs#L3009-L3020
    > Clamp the CA private key to owner-only access (0600) — 755-qcxh.
[^16]: The ledger closing the key fix on 16 August 2026 | plan/archive/packets-2026-08.yaml#L15094-L15133
    > order: 755-qcxh status: completed
[^17]: At this release the key's folder is still under the shared scratch drawer | crates/tillandsias-headless/src/main.rs#L1628
    > const CA_DIR: &str = "/tmp/tillandsias-ca";
[^18]: The written next job: make the folder private before any key is written, and retire the chore | plan/index.yaml#L26815-L26821
    > deliverable: CA material is created in a directory that is private by construction (XDG_RUNTIME_DIR, or DirBuilder::mode(0o700) before any key is written), and scripts/clamp-ca-material.sh gains a retirement condition or is deleted
[^19]: The "check the lock" chore that runs on every grown-up's computer at the start of each work cycle | scripts/cycle-preflight.sh#L250-L260
    > A checkout-side step reaches every host on its next cycle without waiting for a release
[^20]: The drawer's new home in the daily builds: a folder of your own, not the shared scratch space | images/default/ca-path.txt#L73-L83 @v56.9.5.1
    > ${HOME}/.local/state/tillandsias
[^21]: The second written promise: the badges' machine words are on the list of words the screen must never show | openspec/specs/tray-ux/spec.md#L31-L32
    > Internals vocabulary (VM, WSL, enclave, mirror, vault, container, podman, provisioning) MUST NOT appear in end-user-facing UX text.
[^22]: The ledger closing the move on 4 September 2026 | plan/index.yaml#L57386-L57387 @v56.9.5.1
    > - type: completed ts: "2026-09-04T09:17:37Z"
