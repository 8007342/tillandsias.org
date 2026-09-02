# Tillandsias, explained simply

## WHAT IT IS

Think about what happens when you rent a kitchen for an afternoon. You bring your own ingredients, you cook, you clean up, and you leave. The kitchen is not yours, you did not have to build it, and nothing you did in it follows you home. Tillandsias is that kitchen, except it appears inside the computer you already own, on demand, and it disappears when you are done.

Big companies rent out computing space "in the cloud" — someone else's machines, in someone else's building, holding your work. Tillandsias gives you the same kind of clean, ready-made workspace, but it builds it on your own laptop or desktop instead. It quietly sets up a small, sealed-off pretend computer inside your real one, puts the tools in it, and hands it to you ready to use. When you close it, that pretend computer is thrown away, not repaired or reused. Next time, you get a brand-new one that is exactly the same. Sameness every time is the whole point — like a photocopier that gives you an identical copy no matter how many times you press the button.

Is your stuff private? Yes, and unusually so. The people who make Tillandsias run no servers that your copy talks to. There is no account, no sign-up, no usage tracking, no crash reports. Your files stay on your machine because there is nowhere else for them to go. The workspace only ever sees the one folder you deliberately opened — it does not go looking through your drive or read your documents. Any password or login you give it is kept in your own computer's built-in secure storage.

Does it cost money? No. It is free software, released under a licence that lets anyone read, use and share it. You are not renting anything, and there is no monthly bill, because the hardware is the one you already paid for.

Do you need the internet? Only for the ordinary reasons: downloading the program, fetching updates and software ingredients, or signing in to a service you chose. The workspaces themselves are walled off from the internet by default — one single carefully watched doorway handles anything that must go out. It can even run its artificial-intelligence helpers entirely on your own machine, so nothing has to leave it at all, unless you personally decide to use an outside provider.

And if you turn it off? Nothing breaks. Everything temporary is meant to vanish; the things you saved deliberately are kept. If some part of it ever gets confused, the fix is to throw that part away and let a fresh one appear — which is exactly how it was designed to behave.

## HOW IT WAS BUILT

The people who built Tillandsias hold themselves to one rule, and everything else follows from it: every step must make the project a little less uncertain than it was before, and that reduction has to be provable, not merely felt. They call it "monotonic reduction of uncertainty under verifiable constraints", which is a mouthful for something quite homely — never let the fog get thicker, and never take your own word for it that it got thinner.

In practice this works like a very disciplined recipe collection. First someone writes down, in plain and unambiguous words, what a piece of the system must do — the recipe. Then someone writes a test that would visibly fail if the real thing stopped matching the recipe — the taste check. Rules that cannot be tested are not allowed, because a promise nobody can check is just a hope. The written recipe, not the machinery, is treated as the truth; if the machinery disagrees, the machinery is wrong.

They are honest about how far this proves anything. Their own notes say plainly that evidence is not proof, and that passing tests can never guarantee perfection — only that a named list of obligations has been met. The recipes themselves keep improving, so the target keeps moving; what they claim is that the gap keeps shrinking release after release, not that it ever reaches zero.

The work is done by many small workers rather than one large one — many quick, cheap attempts that converge on a good answer faster than a single long, careful one would. It is closer to a kitchen of line cooks than a single chef.

Because those workers run on different machines, in different sessions, and sometimes just stop mid-task, the shared to-do list is built on a trick borrowed from distributed systems. Nobody erases or overwrites anyone else's entry. Everyone only ever adds a note to the end of the list, each task carries a name derived from the task itself so two people describing the same job produce the same name, and the true state of things is worked out by reading all the notes together. That way two people writing at once produce two notes rather than a collision, and no coordinator or supervisor is needed. This same merge-don't-clobber idea shows up at every layer of the system.

Finally, everything is dated and traceable. Version numbers are built from the calendar so they always move forward, each released copy points back to the exact recipes and evidence behind it, and every rule in the method has to name where it came from and what would prove it wrong. A rule without that paperwork is treated as an assumption, not a fact.
