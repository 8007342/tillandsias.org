# Tillandsias, explained like you are five

## A tiny cloud on your own table

When you open a website, you borrow a computer in a huge building far away — **the cloud**. Tillandsias builds a tiny cloud **inside your own computer**, so your things never go to a stranger's building.

It is a doll house. Your computer is the table. Tillandsias puts a clean pretend-computer on it, and inside that, little rooms, one program each.

It should never say rooms or boxes to you — only ever **app**. That is a written promise.[^1] The message you see while it wakes up really is guarded: a machine reads every one of those lines and fails if a wrong word sneaks in.[^6]

> GREEN: This part works great — on the waking-up message the promise is machine-checked, not just hoped for.

## Nobody goes outside except the doorman

The rooms have no doors outside. They share one private hallway, and exactly **one** room — the doorman — may step out to the internet. Everyone else asks it.[^2]

The honest bit: they once kept a *list* of who lived in the hallway, and six residents moved in without it being updated. So they binned the list and wrote a machine that reads the real building instead.[^2]

Robot helpers may only play **inside** the doll house. If one knocks something over, the furniture is pretend.

> GREEN: This part works great — one way out, kept honest by a machine.

## Broken things get thrown away, not glued

@fig:ephemeral

If a room breaks, nobody glues it. You sweep it into the bin and Tillandsias builds a new one, identical every time. Gluing is banned: each time they glued, something *underneath* broke next.[^3]

Your real work lives outside the doll house and never gets swept.

## How the grown-ups keep getting better at it

Before building anything, they write down what it should do — so clearly nobody could argue about whether it came true. Then someone builds a machine that presses the promise and shows a green light or a red one.

The part worth remembering:

**Every time they fix something, they check that nothing else got worse — and they write down what they checked.**

They are honest about a hard thing: getting less broken every time does **not** mean ending up perfect. It means creeping toward *some* resting place, which might not be zero. They wrote that down rather than pretend.[^4]

They work in many tiny fast tries rather than one long careful think — small tries find the answer sooner, so long as each is only allowed to be a *little* bit wrong.[^5] Anyone may have it, read it and change it, free.

## Things that are still broken

> RED: This part is still broken — the doorman's secret key for opening sealed letters sits in the computer's shared scratch drawer. It is no longer unlocked (anyone could read it once; now only you can), but it is still in the shared drawer, when it was meant to travel in a proper safe.[^7]
> PATH: Three fixes are written down, best one first: hand the key over in the safe the doorman already knows how to open. Nobody has done it.[^7]

> RED: This part is still broken — the little status badge in the corner of your screen says things like "Ready (podman starting…)" and "VM failed": exactly the machine words the promise forbids.[^9]
> PATH: A written plan would give the badges one shared word list. It waits on a person, not a robot, to pick the winning wording — changing what you see needs a human's yes.[^8]

## Footnotes

[^1]: The rule that the user must always hear "app", never the machine words | openspec/specs/app-lifecycle/spec.md#L12-L22
[^2]: One way out, and why the hand-written resident list was replaced by a checking machine | openspec/specs/enclave-network/spec.md#L10-L12
[^3]: Throw away and rebuild, never hand-patch — with the real story of gluing making it worse | methodology/philosophy.yaml#L63-L78
[^4]: The grown-ups writing down what they have *not* proven, including that "getting better every time" is not the same as "ends up perfect" | methodology/math-foundations.yaml#L108-L120
[^5]: Many small fast tries beat one big slow one — but only if each try's wrongness stays small | methodology/philosophy.yaml#L7-L25
[^6]: The banned-word list for the waking-up message, and the test that proves none of them can appear | crates/tillandsias-headless/src/bringup_progress.rs#L119-L175
[^7]: The write-up of the doorman's key problem, with the three recorded fixes (still open) | plan/issues/proxy-ca-private-key-world-readable-2026-08-15.md#L38-L46
[^8]: The open plan to give both badges one shared word list, and why a person must sign it off | plan/issues/tray-string-parity-and-i18n-layer-2026-08-09.md#L104-L130
[^9]: The badge text that breaks the rule | crates/tillandsias-macos-tray/src/action_host.rs#L255-L266
