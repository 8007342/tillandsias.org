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
            ("p", "Security, runtime and documentation can each have a local "
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
            ("p", "Each coloured trace has its own target and its own start "
                  "time. A checked target may settle sharply; an uncertain "
                  "one may only show a noisy downward tendency. Neither kind "
                  "of trace should borrow certainty from the other."),
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
