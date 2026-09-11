"""The deck for the Slides page: three slides, each a small dict.

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
- Placeholders make no claims. A `ph` block renders as a labelled "content to
  come" chip, not as prose.
- The deck ships inside the page: nothing here is fetched, drawn or animated
  from a third party.

Block kinds the renderer knows:
  ("p", text)                 a paragraph of established or furniture prose
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
        "title": "A region that stays convergent: built by the methodology, on "
                 "conflict-free replicated data types.",
        "blocks": [
            ("ph", "The methodology: the project grades its own work, spec-first "
                   "and delta-disciplined, and the ledger records every verdict "
                   "with the evidence."),
            ("ph", "CRDTs: the plan ledger as a convergent replicated data type — "
                   "where the claim holds, and where the project says itself it "
                   "does not. Told at the MathWiz level."),
        ],
        "draws_on": ("level-5-phd",),
    },
]