"""The deck for the Slides page: three slides, then a CRDT-methodology tail.

The Slides page is the site's presentation page for a live talk about
Tillandsias. It is not a level page and carries no footnote lists, so the deck
holds itself to the non-level honesty rule: a slide states only what a level
page already establishes, or holds a labelled placeholder for content that is
still to come. Each slide's `draws_on` line names the level (by its slug) whose
claims the slide restates; `build-matrix.py` turns that into a linked "drawing
on" line so a reader can follow a claim to its footnote.

Rules for anything added here:
- Never state more than the named level states. If a slide says it, the level
  on its `draws_on` line carries it with a footnote.
- The two methodology slides embed the methodology levels' own staircase and
  law-of-large-numbers figure (the registry keeps both), and restate no more
  than those figures caption. Placeholders make no claims. A `ph` block renders
  as a labelled "content to come" chip, not as prose.
- The deck ships inside the page: nothing here is fetched, drawn or animated
  from a third party.

Block kinds the renderer knows:
  ("p", text)                 a paragraph of established or furniture prose
  ("fig", name)               embed the site's own figure by registry name; the
                              page draws that figure on a methodology level, and
                              this slide restates only its caption
  ("ph", text)                a labelled placeholder holding room for content
  ("pillars", [(name, note), ...])
                              three named cards; each card's note is the
                              "content to come" text for that card
"""

SLIDES = [
    {
        "label": "Thesis",
        "eyebrow": "tillandsias · in one line",
        "title": "An idempotent, ephemeral cloud region, folded through your "
                 "hypervisor.",
        "lede": "Local hardware. Free software. Nothing rented, nothing "
                "metered, nothing left behind.",
        "blocks": [
            ("ph", "The unpacking: what the region is, what idempotent and "
                   "ephemeral mean here, and where this talk goes next."),
        ],
        "draws_on": (),
    },
    {
        "label": "Pillars",
        "eyebrow": "tillandsias · the story",
        "title": "Three pillars, one region: a containerized workflow, Linux "
                 "security, and a portable cloud region.",
        "blocks": [
            ("pillars", [
                ("Containerized workflow",
                 "The anatomy: what runs where in the region, told at the "
                 "power-user level."),
                ("Linux security",
                 "Boundaries, egress and provenance — and what the tests do "
                 "not actually test, told at the security level."),
                ("Portable cloud region",
                 "A VM on macOS and Windows, rootless containers straight on a "
                 "Linux host, told at the phone level."),
            ]),
        ],
        "draws_on": ("level-3-power", "level-4-security", "level-2-phone"),
    },
    {
        "label": "Mechanism",
        "eyebrow": "tillandsias · the how",
        "title": "A region that stays convergent: the plan ledger as a "
                 "replicated data type, and the staircase it guarantees.",
        "lede": "",
        "blocks": [
            ("fig", "staircase"),
            ("p", "The methodology's own figure on the mechanism level: "
                  "evidence that only climbs, one run whose skew you cannot "
                  "see — and many short runs whose average lands, provided "
                  "each run's bias is bounded."),
            ("ph", "The algebra: where the join exists the ledger converges — "
                   "and where the site says itself it does not."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "Uncertainty",
        "eyebrow": "tillandsias · the method",
        "title": "Reducing uncertainty one slide-aware run at a time: the law "
                 "of large numbers, made visible.",
        "lede": "",
        "blocks": [
            ("fig", "lln"),
            ("p", "A single big prompt has a distance to the truth its own bar "
                  "cannot show; many small fast prompts land closer — provided "
                  "every prompt's bias stays bounded."),
            ("ph", "CRDT: how the region keeps those runs convergent, told at "
                   "the methodology level."),
        ],
        "draws_on": ("level-5-phd",),
    },
    {
        "label": "CRDTs, everywhere",
        "eyebrow": "tillandsias · the how",
        "title": "The ledger as a conflict-free replicated data type: state "
                 "that converges under any order of arrival.",
        "blocks": [
            ("fig", "crdt"),
            ("p", "The methodology's own figure: replicated fragments fold in "
                  "either order and land on the same state — no lock, no "
                  "coordinator, no merge conflict, no lost write."),
            ("ph", "Where the claim is put none too strongly: the algebraic "
                   "conditions under which the ledger converges, and the "
                   "footnotes that still hold."),
        ],
        "draws_on": ("level-5-phd",),
    },
]
