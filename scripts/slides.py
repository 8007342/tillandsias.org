"""Presentation summaries; each slide links to the levels carrying its evidence.

Keep the five-part story and its deep links. Add claims to an owning level with
citations before summarising them here. Diagrams illustrate an argument, not
measurements; their hypotheses must survive the shorter presentation wording.
"""

SLIDES = [
    {
        "label": "Thesis",
        "eyebrow": "tillandsias · in one line",
        "title": "A small cloud region on your own computer.",
        "lede": "Disposable workspaces. Durable work. Boundaries you can inspect.",
        "blocks": [
            ("p", "Tillandsias brings the tools, network services and AI assistants "
                  "into a local region. Recreating a broken workspace is part of "
                  "the design; keeping your work means committing and pushing it."),
            ("p", "The software is free. Your hardware, electricity and any paid "
                  "AI service you choose still have costs."),
        ],
        "draws_on": ("level-1-five", "level-2-phone"),
    },
    {
        "label": "Pillars",
        "eyebrow": "tillandsias · the story",
        "title": "Three pillars: the workflow, its boundaries, and the host.",
        "blocks": [
            ("pillars", [
                ("Containerized workflow",
                 "A forge holds the agent and its tools. Shared services provide "
                 "the proxy, git mirror, secrets and local inference."),
                ("Linux security",
                 "Rootless containers and launch checks restrict the workspace. "
                 "Read the security level for the remaining egress, credential "
                 "and supply-chain gaps."),
                ("Portable cloud region",
                 "macOS and Windows add a Linux virtual machine. Linux runs "
                 "rootless containers on the host, sharing its kernel."),
            ]),
        ],
        "draws_on": ("level-3-power", "level-4-security", "level-2-phone"),
    },
    {
        "label": "Boxes in boxes",
        "eyebrow": "tillandsias \u00b7 the shape",
        "title": "Containerization is not one layer.",
        "blocks": [
            ("fig", "nesting"),
            ("p", "An app runs in a container. The containers run beside each "
                  "other on one private network. On Mac and Windows that whole "
                  "arrangement runs inside a Linux machine made for you, which "
                  "itself runs on your hardware \u2014 one box more than Linux "
                  "needs, doing the same job at a different level."),
            ("p", "Every layer in between is boxed too, not just the outermost "
                  "one and not just the app. That is what makes a workspace "
                  "disposable: you can throw away any box and rebuild it "
                  "without touching the ones around it."),
        ],
        "draws_on": ("level-2-phone", "level-3-power", "level-4-security"),
    },
    {
        "label": "The enclave",
        "eyebrow": "tillandsias \u00b7 the boundary",
        "title": "One private network, and one guarded door.",
        "blocks": [
            ("fig", "layers"),
            ("p", "The services an agent needs \u2014 the proxy, the git mirror, "
                  "secrets, local inference \u2014 sit on a network with no route "
                  "to the internet. Traffic that leaves goes through a single "
                  "checked exit; everything else is refused rather than "
                  "silently allowed."),
            ("p", "Read the security level before trusting that sentence: it "
                  "records what the boundary does not yet cover, and a refused "
                  "path is only as good as the check that refuses it."),
        ],
        "draws_on": ("level-3-power", "level-4-security"),
    },
    {
        "label": "The git mirror",
        "eyebrow": "tillandsias \u00b7 the decision",
        "title": "Your push is not finished until the copy outside has it.",
        "blocks": [
            ("p", "Inside the enclave your work pushes to a local mirror, not "
                  "to the internet. The mirror holds the upstream credential; "
                  "the workspace never sees it. So an agent can publish work "
                  "without ever holding a token that could publish anything "
                  "else."),
            ("p", "The mirror relays the push onward and waits. Your push "
                  "succeeds only once the upstream has durably accepted the "
                  "same set of refs \u2014 so a success you can see is a "
                  "success that survived the machine being thrown away."),
            ("p", "That pairing is why this is built rather than borrowed. "
                  "Managed mirrors hold the credential for you and copy "
                  "asynchronously, reporting success before the copy lands. "
                  "Caching proxies relay synchronously and forward your "
                  "credentials, which is the isolation we are buying. Needing "
                  "both at once is the unusual requirement."),
        ],
        "draws_on": ("level-3-power", "level-4-security"),
    },
    {
        "label": "Mechanism",
        "eyebrow": "tillandsias · the how",
        "title": "Keep the target fixed while checking the next step.",
        "blocks": [
            ("fig", "staircase"),
            ("p", "At a fixed scope, checked evidence can advance along an "
                  "ordered ladder. A release may change the target: compare "
                  "scores only after accounting for that change."),
            ("p", "A non-increasing residual bounded below has a limit. That "
                  "alone does not show that the limit is zero, or that the "
                  "implementation satisfies every real-world requirement."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "Uncertainty",
        "eyebrow": "tillandsias · the method",
        "title": "Short iterations, explicit evidence, room to be wrong.",
        "blocks": [
            ("fig", "lln"),
            ("p", "Each run reads what earlier runs learned. Those dependent "
                  "iterations do not inherit an independent-sample convergence "
                  "theorem, and bounded bias alone cannot make an average true."),
            ("p", "The methodology withdrew its strong-law claim. The practical "
                  "loop remains: make a small change, check it, seek a "
                  "counterexample, and keep the correction in the record."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "Refinement",
        "eyebrow": "tillandsias · the working model",
        "title": "Many local changes, one shared record.",
        "blocks": [
            ("fig", "refinement-mesh"),
            ("p", "Treat the repository and prompt as selected context for a "
                  "refinement, not as literal vector sets stored by Git. The "
                  "model proposes a delta; tests, review and a commit decide "
                  "whether it joins the record."),
            ("p", "Accessibility, product copy and dashboards can each have a local "
                  "target. Their residuals are meaningful only against their "
                  "own fixed specifications. The shared line is useful "
                  "engineering telemetry after scope is aligned, not a proof "
                  "that any sequence converges to truth."),
        ],
        "draws_on": ("level-1-five", "level-2-phone", "level-3-power",
                     "level-4-security", "level-5-phd"),
    },
    {
        "label": "Aggregation",
        "eyebrow": "tillandsias · the working model",
        "title": "Local truths can compose into one accountable picture.",
        "blocks": [
            ("fig", "aggregate-traces"),
            ("p", "Each coloured trace is a product job with its own target "
                  "and start time: accessibility and language, marketing, "
                  "dashboards, or customer support. The dots can wobble while "
                  "they move nearer their own dotted line; one trace must not "
                  "borrow certainty from another."),
            ("p", "The lower line aggregates only comparable work: the same "
                  "identities, scope and weights. It is a compact record of "
                  "what the project measured across workstreams, not a claim "
                  "that all targets share one probability law."),
        ],
        "draws_on": ("level-2-phone", "level-3-power", "level-4-security",
                     "level-5-phd"),
    },
    {
        "label": "CRDTs, everywhere",
        "eyebrow": "tillandsias · the how",
        "title": "Merge the same facts with the same rules.",
        "blocks": [
            ("fig", "crdt"),
            ("p", "Set union preserves distinct facts. A last-writer-wins "
                  "register chooses one scalar value; it does not preserve "
                  "every competing edit. The choice of merge rule matters."),
            ("p", "Convergence needs the same delivered updates and a merge "
                  "operation with the stated algebraic properties. It does "
                  "not guarantee delivery, eliminate all git conflicts, or "
                  "prove that a recorded claim is true."),
        ],
        "draws_on": ("level-5-phd",),
    },
]
