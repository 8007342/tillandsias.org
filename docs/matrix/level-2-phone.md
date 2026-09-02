# Tillandsias, explained simply

## A rented kitchen that appears inside your own computer

Imagine renting a kitchen for an afternoon. You bring your ingredients, you cook, you leave, and nothing you did there follows you home. Tillandsias is that kitchen, except it appears *inside the computer you already own*, and it disappears when you are done.

Its job is to give software helpers — including AI assistants that write and run code — a sealed room. Rather than letting them loose on your machine, Tillandsias builds a small pretend computer inside your real one, puts the tools in it, and hands them only the project folder you deliberately opened.

When you are finished, that pretend computer is **thrown away rather than repaired**. Next time you get a brand-new one that is identical, like a photocopier that gives the same copy however often you press the button.

@fig:ephemeral

That "throw it away" habit is the safety design. Something always rebuilt from the same instructions cannot slowly rot into a state nobody understands. Even the internal passwords the parts use to talk to each other are reissued at every start, so a messy shutdown yesterday cannot poison today.[^1]

## The worries people actually have

**Is my stuff private?** Unusually so. The people who make Tillandsias run no servers your copy talks to. No account, no sign-up, no usage tracking, no crash reports.[^2] Your files stay put because there is nowhere else for them to go. Logins you provide are kept in your own machine's secure storage.[^3]

**Does it cost money?** No. It is free software under a licence that lets anyone read, use and share it.[^4] You already paid for the hardware.

**Do I need the internet?** Only for ordinary reasons — downloading the program, updates, or signing in to a service you chose. The workspaces are walled off, with one watched doorway for anything that must go out. It can run its AI helpers on your own machine, so nothing need leave it.

**What if I turn it off, or something goes wrong?** Nothing breaks. Temporary things are meant to vanish; what you saved is kept. The repair procedure is to throw the confused part away and let a fresh one appear — which is simply the machine behaving as designed. You can wipe the whole thing and rebuild it freely.[^5]

> GREEN: The privacy promise is structural, not a pinky-swear — there is no server to send anything to, so there is nothing to leak or sell.
> GREEN: Each workspace sees only the folder you opened, never your whole drive.
> GREEN: Free and open source, so the claims above can be checked by anyone, not just believed.
> GREEN: The design treats "start over" as normal, which is why a bad day rarely leaves lasting damage.

## How they keep themselves honest

The team holds to one rule: every step must leave the project *less uncertain* than before, and the reduction must be checkable by a machine — never just felt.[^6]

In practice it works like a strict recipe collection. Someone writes down in plain words what a part must do. Someone else writes a test that would visibly fail if reality stopped matching. Rules that cannot be tested are not allowed, because a promise nobody can check is only a hope. The written recipe is the truth; if the machinery disagrees, the machinery is wrong.

They are refreshingly blunt about the limits. Their own notes say passing tests are *evidence, not proof*.[^7] And because the recipes keep improving, the target keeps moving — "finished" is not a place you arrive at.

@fig:staircase

What they promise instead is that the gap never slides backwards: each release must be no further from the recipes than the last, and a machine checks that at every release. That means it settles toward some floor, not that the floor is zero. They explicitly refuse to claim the stronger mathematical result that would guarantee zero.[^8]

## Where it falls short today

> RED: On Macs, the app has not yet been through Apple's inspection service, so a copy downloaded with a web browser gets blocked on first launch; the recommended install avoids this only by not going through the browser.[^9]
> PATH: The full fix is written up and costed — an Apple Developer identity plus notarization — and the plumbing is pre-wired, but enrollment is still pending.[^10]

> RED: One Windows installer file in a past release was shipped without its signature and was simply impossible to install — no workaround for the user.[^11]
> PATH: The release process now refuses to publish that file unsigned, and the signing route is chosen but not yet in place.[^12]

> RED: A local AI "expert" feature confidently produced answers with invented sources — it announced a careful research pipeline that was never actually run.[^13]
> PATH: It was switched off and rewritten so that answers either come with real, used citations or are refused outright; that replacement is recorded as a change in progress.[^14]

> RED: On some Linux desktops, clicking the little tray icon could freeze the whole screen session.[^15]
> PATH: The faulty replies were audited and corrected, but a further freeze was found after the last release and fixed only on a development branch, so the issue is deliberately left open.[^15]

None of these break the privacy story. They are install-and-launch problems plus one over-promising feature — caught because somebody is checking, which is the whole point of the method.

## Footnotes

[^1]: Internal secrets are wiped and reissued on every start | openspec/specs/ephemeral-secret-refresh/spec.md#L1-L20
[^2]: "Tillandsias collects nothing" — no telemetry, no analytics, no server | PRIVACY.md#L5-L17
[^3]: Only folders you open; credentials in a local secret store | PRIVACY.md#L30-L44
[^4]: GNU General Public License, version 3 | LICENSE#L1-L2
[^5]: "Designed to be wiped and rebuilt freely" | PRIVACY.md#L45-L48
[^6]: The convergence objective: shrink the distance between spec, code, and reality | methodology/convergence.yaml#L1-L20
[^7]: Evidence boundaries — traceability and passing tests are evidence, not proof | methodology/philosophy.yaml#L228-L232
[^8]: The stronger contraction result is explicitly not claimed | methodology/math-foundations.yaml#L107-L120
[^9]: Install instructions warning that browser downloads hit a Gatekeeper block | README.md#L27-L45
[^10]: Recorded options and costs for Apple signing and notarization | plan/issues/macos-gatekeeper-signing-options-2026-08-29.md
[^11]: Unsigned Windows package is uninstallable, with no user-side workaround | plan/issues/store-msix-submission-blockers-2026-08-31.md#L26-L40
[^12]: Chosen signing route for the Windows release channel | plan/issues/windows-signing-research-2026-08-16.md#L1-L25
[^13]: Audit of the shipped "local expert" facade: stamped answers valid with no retrieval and no citations | openspec/changes/expert-serve-grounded-pipeline/proposal.md#L1-L25
[^14]: The grounded replacement pipeline, still an in-progress change | openspec/changes/expert-serve-grounded-pipeline/tasks.md
[^15]: Tray menu replies did not match the desktop specification, freezing the session | plan/loop_status.d/20260830t004603z-3b425083-linux.md
