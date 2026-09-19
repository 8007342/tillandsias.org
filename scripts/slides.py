"""Presentation summaries; draws_on keeps editorial provenance out of the deck.

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
            ("fig", "local-region"),
            ("p", "Tools, services and AI assistants share one local region. "
                  "Rebuild a workspace when needed; commit and push to keep your work."),
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
                 "Egress, credential and supply-chain gaps remain."),
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
            ("p", "Apps share a private network. On Mac and Windows, their "
                  "containers run inside a Linux virtual machine; on Linux, "
                  "they share the host kernel."),
            ("p", "Each layer has its own job and lifecycle. Rebuild a workspace "
                  "while keeping shared services and pushed work."),
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
            ("p", "This is the intended boundary. Egress and credential gaps remain; "
                  "its protection depends on the checks actually enforcing it."),
        ],
        "draws_on": ("level-3-power", "level-4-security"),
    },
    {
        "label": "The git mirror",
        "eyebrow": "tillandsias \u00b7 the decision",
        "title": "Push once. Keep a copy beyond your computer.",
        "blocks": [
            ("fig", "push-journey"),
            ("p", "The mirror holds the upstream credential; your workspace never sees it. "
                  "With an upstream configured, success means that upstream accepted the same refs."),
            ("p", "No upstream? The push stays in the local mirror."),
        ],
        "draws_on": ("level-3-power", "level-4-security"),
    },
    {
        "label": "The orchestrated workspace",
        "eyebrow": "tillandsias · the whole workspace",
        "title": "One project. An orchestrated enclave.",
        "layout": "diagram",
        "blocks": [
            ("fig", "project-orchestration"),
        ],
        "draws_on": ("level-2-phone", "level-3-power", "level-4-security"),
    },
    {
        "label": "The methodology",
        "eyebrow": "tillandsias · from what it is to how it improves",
        "title": "Turn every change into a checked refinement.",
        "layout": "method",
        "blocks": [
            ("fig", "methodology-bridge"),
            ("p", "The same loop works for code, specs, artifacts and documentation: "
                  "state a constraint, make a small change, check it, and keep the evidence."),
            ("p", "A prompt stops when it is close enough for this scope. More checked "
                  "events increase refinement effort; they can reduce a non-zero skew "
                  "in the remaining uncertainty, but this is an analogy to a weak law "
                  "of large numbers, not a theorem about dependent prompts."),
        ],
        "draws_on": ("level-5-phd",),
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
            ("p", "Each run reads what earlier runs learned. Think of more events as a "
                  "larger sample that may reduce a non-zero skew in the residual, while "
                  "remembering that the prompts are dependent."),
            ("p", "The weak-law picture is a useful intuition, not a convergence proof. "
                  "The practical loop remains: make a small change, check it, seek a "
                  "counterexample, and keep the correction in the record."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "Refinement",
        "eyebrow": "tillandsias · the working model",
        "title": "Small steps bring each part closer.",
        "blocks": [
            ("fig", "small-steps"),
            ("p", "Accessibility, copy and dashboards each have a target. A small change, "
                  "a check, then a recorded result: repeat that loop within each workstream."),
            ("p", "Keep the checked gains and investigate setbacks. Each path can get "
                  "closer at its own pace without being finished."),
        ],
        "draws_on": ("level-1-five", "level-2-phone", "level-3-power",
                     "level-4-security", "level-5-phd"),
    },
    {
        "label": "Aggregation",
        "eyebrow": "tillandsias · the working model",
        "title": "Progress in the parts adds up across the project.",
        "blocks": [
            ("fig", "shared-progress"),
            ("p", "With a fixed set of requirements and fixed weights, fewer gaps in "
                  "each part means fewer gaps overall. Earlier gains remain while "
                  "another workstream takes its next step."),
            ("p", "If every local gap settles toward a limit, their fixed weighted "
                  "total does too. That limit may still be above zero. Changed scope "
                  "needs a new baseline; a better total never erases a local failure."),
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
    {
        "label": "CRDTs and the method",
        "eyebrow": "tillandsias · keep what you learn",
        "title": "Many contributors. One accumulating evidence record.",
        "blocks": [
            ("fig", "evidence-record"),
            ("p", "Conflict-free replicated data types (CRDTs) let contributors add "
                  "distinct evidence events independently. Once everyone has the same "
                  "events, merging them produces the same record, even after retries."),
            ("p", "That supports the method: preserve what was learned, then check the "
                  "next step. A failed check adds a correction or falsification; "
                  "agreement on the record does not make its claims true."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "CRDTs, Git and versions",
        "eyebrow": "tillandsias · collaborate and remember",
        "title": "Git carries the history. CRDT rules combine the record.",
        "blocks": [
            ("fig", "git-record"),
            ("p", "Commit distinct ledger fragments on each branch. Exchange and merge "
                  "them through Git, then fold the delivered events into a shared view. "
                  "Code and competing scalar edits still need their own merge rules and review."),
            ("p", "Commits and tags let you revisit a recorded state. Mergeable version "
                  "coordinates use a different rule: (2, 1) and (1, 3) join to (2, 3), "
                  "taking each coordinate’s maximum. This illustrative join does not "
                  "select a Git commit or prove release compatibility."),
        ],
        "draws_on": ("level-3-power", "level-5-phd"),
    },
    {
        "label": "The refinement vectors",
        "eyebrow": "tillandsias · one project, many coordinates",
        "title": "Every artifact contributes a vector of evidence.",
        "blocks": [
            ("fig", "artifact-vectors"),
            ("p", "Files, specs, build artifacts and documentation evolve together. "
                  "Here, a “vector” means their named requirements and evidence states."),
            ("p", "Give evidence events stable IDs and merge them as a set. "
                  "That record can follow CRDT rules across every artifact type. "
                  "Git versions the files; ordinary file edits still need semantic review."),
        ],
        "draws_on": ("level-3-power", "level-5-phd"),
    },
    {
        "label": "Tree of refinement",
        "eyebrow": "tillandsias · many histories, one bounded record",
        "title": "Many trees overlap toward a shared, bounded record.",
        "layout": "finale",
        "lede": "Many branches of effort. One increasingly evidenced project.",
        "blocks": [
            ("fig", "refinement-field"),
            ("p", "Fix N requirements, each with seven evidence ranks. Inflationary "
                  "steps keep or raise every rank; a monotone rule preserves their ordering. "
                  "A fixed rule with both properties stabilizes within 6N strict increases "
                  "\u2014 a bound on evidence states, not on commits, effort or elapsed time."),
            ("p", "Each small Git history brings a different kind of evidence. Checked "
                  "joins connect them into a shared refinement history within a fixed scope "
                  "and finite evidence ranks; new scope or falsification opens an explicit "
                  "new comparison. Tillandsias approximates this ideal through repeated "
                  "effort: preserve checked gains, expose counterexamples, and reduce the "
                  "remaining gaps. Monotonic convergence is conditional; its limit need not "
                  "be perfection."),
        ],
        "draws_on": ("level-5-phd",),
    },
]
