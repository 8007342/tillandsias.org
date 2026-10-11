## REMOVED Requirements

### Requirement: App-vocabulary promise
**Reason**: The rule that the product's screens say "app" is a rule about how
the product is written. It is meta, and a five-year-old reader has no use for
it or for the machine that enforces it.
**Migration**: The page's own vocabulary rule stays under "Register, metaphor
and vocabulary". A screen that breaks the product's rule is a defect for the
product's tracker. It goes on a page only where the reader of that page is
affected.

## MODIFIED Requirements

### Requirement: Required sections
The page MUST carry, in this order: its own title; a framing section that says
what the thing is with the metaphor the rest of the page reuses; a section on
the single way out and who may use it; a section on disposability (broken
pieces are replaced rather than repaired), which MUST also say what of the
reader's own is never swept away; a short section on getting better, which MUST
say that a machine checks a fix does not break what used to work, and MUST give
the honest limit that getting less broken is not the same as ending up perfect;
and a closing section that collects what is still broken, which MUST be the
last section before the footnotes. The rendered footnote list MUST be present.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists, carries the purpose named for it, and
  the shortcomings section is last before the footnotes

#### Scenario: Nothing is broken at a pin
- **WHEN** no shortcoming holds against the code at the level's pin
- **THEN** the closing section stays and says so in one sentence, rather than
  being deleted

### Requirement: Optional sections and elements
The page MAY carry one figure in the disposability section, a one-sentence
statement of the licence freedoms, and a sentence placing automated helpers
inside the enclosure, bounded by what they can still send out. None of these is
required, and dropping one MUST NOT be treated as a regression. Each one, when
present, MUST obey every wording and sourcing rule in this spec.

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence
