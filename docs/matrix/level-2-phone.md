# Tillandsias, explained simply

## What it is for, in one paragraph

The reason a grown-up wants one is narrower than "the cloud, but at home". Software you did not write — increasingly, AI assistants that write and run code for you — has to work somewhere. The choice is between your actual machine and a sealed room containing only the project folder you deliberately opened.[^1] Tillandsias is that room, plus the plumbing to open it in a second and forget about it.

@fig:gate

## Is my stuff private, and who could see it?

Nobody, because there is nowhere for it to go. The people who make Tillandsias operate no servers your copy talks to: no account, no sign-up, no usage tracking, no crash reporting, no identifier attached to you or your machine.[^2] Your logs stay on your own disk where you can read them, and leave only if you send them somewhere yourself; any login you hand over goes into your operating system's own password store, not a file of the project's devising.[^3]

> GREEN: The privacy claim does not rest on anyone's intentions. There is no server of theirs to send anything to, so there is no decision to trust and none to reverse.[^2] It covers their side only — a service you sign into yourself still sees what you tell it.

## Does it cost money? Does it need the internet?

It costs nothing: free software under a licence that lets anyone read, run, modify and pass it on.[^4] You have already paid for the only hardware involved.

The internet is needed only for ordinary, visible reasons: fetching the program, fetching updates, reaching a service you chose. The work itself does not require it, and the AI assistants can run on your own machine — which is why the privacy claim survives them.

## What happens when I turn it off? Can it break my computer?

Turning it off is the expected motion, not an interruption. Anything you saved is a real file on your real disk, untouched by the rebuild. Even the internal passwords the pieces use to talk to each other are reissued at every start, so yesterday's messy shutdown cannot jam today's start.[^5]

> GREEN: Those internal passwords are replaced at every launch rather than left lying about, so one that leaked is stale by the next start — written down as a required behaviour with named cases, not left to habit.[^5]

As for damage: a misbehaving tool inside the sealed room sees only the folder you gave it.[^1] Wiping the installation and rebuilding is documented and supported, not a last resort.[^6] The cost you do pay is ordinary and reversible — it is a real virtual machine, so it holds real memory and disk while running and gives them back when it stops.

## Sharpening one thing you were told

@fig:staircase

You were told they check that nothing got worse. Precisely: each release must sit no further from its own written specifications than the last, and that distance is measured by a machine, not judged by a person.[^7]

Two honest limits follow, in the project's own words. Passing tests are *evidence, not proof* — they show no contradiction was found, not that none exists.[^8] And "never worse" means settling toward some floor, not that the floor is zero; the stronger mathematical result that would guarantee zero is explicitly not claimed.[^9]

## Where it falls short today

> RED: On Macs, the application has not yet passed Apple's inspection service, so a copy downloaded with a web browser is blocked on first launch; the recommended one-line install sidesteps that only by not going through a browser.[^10]
> PATH: The fix — an Apple Developer identity and notarization — is written up and costed, and the release machinery is pre-wired for it. Enrolment is still pending.[^11]

> RED: One Windows package in a past release went out without its signature, which makes it not merely warned-about but impossible to install, with no user-side workaround.[^12]
> PATH: The release process now refuses to publish that file unsigned, and the signing route has been chosen but not yet put in place.[^13]

> RED: A built-in "expert" feature gave confident answers with invented sources: it described a careful research procedure, did not run it, and marked its own output verified anyway.[^14]
> PATH: It has been switched off and is being rebuilt so that an answer either carries real citations it actually used or is refused. That replacement is in progress, not finished.[^15]

Two install problems and one feature promising more than it delivered. None touch the privacy story, and all three are here because the project's own checking found them.

## Footnotes

[^1]: What a workspace can reach, and why that isolation exists to protect you from the tools | PRIVACY.md#L30-L41
[^2]: "Tillandsias collects nothing" — no account, no telemetry, no analytics, no server | PRIVACY.md#L5-L17
[^3]: Credentials in the local secret store; logs kept on your own disk | PRIVACY.md#L42-L46
[^4]: GNU General Public License, version 3 | LICENSE#L1-L2
[^5]: Internal secrets are removed and reissued at every start, so an unclean shutdown leaves nothing stale | openspec/specs/ephemeral-secret-refresh/spec.md#L1-L20
[^6]: "Designed to be wiped and rebuilt freely" | PRIVACY.md#L47-L48
[^7]: The convergence objective: the measured distance between specification, code and reality must not grow | methodology/convergence.yaml#L1-L20
[^8]: Evidence boundaries — traceability and passing tests are evidence, not proof of correctness | methodology/philosophy.yaml#L228-L232
[^9]: The stronger contraction result is explicitly not claimed | methodology/math-foundations.yaml#L107-L120
[^10]: Install instructions warning that a browser download hits a Gatekeeper block on first launch | README.md#L27-L45
[^11]: Recorded options and costs for Apple signing and notarization | plan/issues/macos-gatekeeper-signing-options-2026-08-29.md
[^12]: The unsigned Windows package is uninstallable, with no user-side workaround | plan/issues/store-msix-submission-blockers-2026-08-31.md#L26-L40
[^13]: The chosen signing route for the Windows release channel | plan/issues/windows-signing-research-2026-08-16.md#L1-L25
[^14]: Audit of the shipped "local expert" facade: answers stamped valid with no retrieval and no citations | openspec/changes/expert-serve-grounded-pipeline/proposal.md#L1-L25
[^15]: The grounded replacement pipeline, still an in-progress change | openspec/changes/expert-serve-grounded-pipeline/tasks.md
