# Tillandsias, explained like you are five

## A tiny cloud on your own table

When you open a website, you borrow a computer in a huge building far away — **the cloud**. Tillandsias builds a tiny cloud **inside your own computer**, so you can work without sending your things to its makers. A service you choose to use can still receive what you send it.[^24]

It is a doll house. Your computer is the table. Tillandsias puts a clean pretend-computer on it, and inside that, little rooms, one program each.

Anyone may have it, read it and change it, for free.[^14]

## Nobody goes outside except the doorman

The rooms have no doors outside. They share one private hallway, and exactly **one** room — the doorman — may step out to the internet. Everyone else asks it.[^2]

Robot helpers may only play **inside** the doll house.[^11] If one makes a mess in its room, the room can be thrown away — but anything it sends out of the doll house is real, so look at what it sends.[^26]

## Broken things get thrown away, not glued

@fig:ephemeral

If a room breaks, nobody glues it. It goes in the bin and Tillandsias builds a fresh one from the same recipe. That is on purpose: gluing one layer tends to break the layer underneath next.[^3]

Your own project folder lives outside the doll house, and sweeping a room never touches it.[^12]

Getting work out of the doll house has its own rule. The doll house has a post box, and it does not say *done* until the shelf far away really has your parcel. If it cannot reach the shelf, it says so, instead of saying *done* and quietly keeping the parcel in a drawer.[^26]

## Getting better, honestly

Every time the makers fix something, a machine checks that nothing that used to work got broken.[^23]

Less broken every time does **not** mean perfect one day. It only means creeping toward *some* resting place, which may not be zero. They say so themselves.[^4]

## Things that are still broken

> RED: The doorman has a secret key. The key itself is locked so only you can read it,[^15] and it lives in a folder inside your own home folder.[^17][^20] But that folder is made the ordinary way, without first being made private.[^25]
> PATH: Making the folder private before the key goes in is the written next job. It is not done yet.[^18]

## Footnotes

[^2]: Only the doorman may step outside | openspec/specs/enclave-network/spec.md#L10-L12
    > Only the proxy is dual-homed for external access; all other members communicate exclusively through the enclave.
[^3]: Throw away and rebuild, never patch by hand, and why | methodology/philosophy.yaml#L84-L99
    > Therefore the DEFAULT response to a borked host/VM/guest/podman/stack layer is to DESTROY and RECREATE it, never to hand-patch it forward.
[^4]: Getting better every time means nothing gets worse and what is left shrinks, not that it ends up perfect | methodology/math-foundations.yaml#L108-L120
    > Without that metric proof, "monotonic convergence" means ordered non-regression plus finite residual descent, not metric contraction.
[^11]: Robot helpers run only inside the doll house | openspec/specs/forge-as-only-runtime/spec.md#L18-L19
    > Every coding agent, maintenance shell, and runtime utility executes inside the project's forge container; there is no host-side execution surface.
[^12]: Sweeping a room never touches your project folder | openspec/specs/app-lifecycle/spec.md#L79-L81
    > the container is removed, project-specific cache data is deleted, but the project source directory in `~/src` is never touched
[^14]: The licence: anyone may have it, read it and change it | LICENSE#L1-L16
    > the GNU General Public License is intended to guarantee your freedom to share and change all versions of a program
[^15]: The key is locked so only its owner can read it | crates/tillandsias-headless/src/main.rs#L3400-L3400
    > Clamp the CA private key to owner-only access (0600) — 755-qcxh.
[^17]: The key's folder sits inside the program's own folder | crates/tillandsias-core/src/ca_path.rs#L36-L50
    > format!("{}/ca", ca_template())
[^18]: The written next job: make the folder private before any key is written | plan/index.yaml#L26013-L26013
    > deliverable: CA material is created in a directory that is private by construction (XDG_RUNTIME_DIR, or DirBuilder::mode(0o700) before any key is written), and scripts/clamp-ca-material.sh gains a retirement condition or is deleted
[^20]: The program's own folder is inside your home folder | images/default/ca-path.txt#L83-L83
    > ${HOME}/.local/state/tillandsias
[^23]: After every fix, a test that used to pass may not start failing | build.sh#L2454-L2456
    > a failure not named in scripts/test-known-red.txt is a new regression, and a listed test that PASSED is a stale entry that must be deleted
[^24]: A service you choose receives what you send it | PRIVACY.md#L60-L63
    > If you instead configure a remote provider, the content you send is transmitted to that provider under their terms.
[^25]: The key's folder is made the ordinary way, with no private setting | crates/tillandsias-headless/src/main.rs#L3468-L3468
    > std::fs::create_dir_all(&certs_dir)
[^26]: The post box says done only once the faraway copy really has the work | images/git/pre-receive-hook.sh#L6-L8
    > Validates ledger YAML, then synchronously relays the proposed ref transaction
    > upstream before accepting it locally. A client success therefore means the
    > configured upstream has durably accepted the same atomic ref set.
