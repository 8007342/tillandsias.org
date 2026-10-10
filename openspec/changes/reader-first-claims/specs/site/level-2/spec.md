## MODIFIED Requirements

### Requirement: Required sections
The page MUST carry, in this order: its own title; a framing section that says
in one paragraph what the software is for, naming the choice it removes
(software the reader did not write, AI assistants among them, has to run
somewhere, and it runs against a folder the reader deliberately opened rather
than against the whole machine); a privacy section answering who could see the
reader's things; a section answering what it costs and whether it needs the
internet; a section answering what happens when it is turned off and whether it
can damage the machine, which MUST also name the ordinary, reversible cost the
reader does pay; a section answering whether an update can break what already
works, which MUST say what the project's test verdict refuses and MUST carry the
two honest limits required above; and a closing section collecting what falls
short today, which MUST be the last section before the footnotes. The rendered
footnote list MUST be present.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists, carries the purpose named for it, and
  the shortcomings section is last before the footnotes

#### Scenario: Nothing falls short at a pin
- **WHEN** no shortcoming holds against the code at the level's pin
- **THEN** the closing section stays and says so in one sentence, rather than
  being deleted

#### Scenario: A question is answered without its cost
- **WHEN** the page tells the reader that turning the software off is safe
- **THEN** the same section says what running it does cost: memory held while
  it runs and given back when it stops, and the disk the cached system image
  takes up

### Requirement: Optional sections and elements
The page MAY carry: at most one figure per section, each carrying that
section's single idea; GREEN callouts where a claim is worth separating from the
prose; a sentence noting that the reader has already paid for the only hardware
involved; and one closing sentence summarising the shortcomings and saying
which parts of the page they do and do not touch. None of these is required,
and dropping one MUST NOT be treated as a regression. Each one, when present,
MUST obey every wording and sourcing rule in this spec.

#### Scenario: The closing summary is present
- **WHEN** the closing section ends with a summarising sentence
- **THEN** it refers to the same shortcomings the flags above it state, and any
  claim it makes about what they do not touch is one the page has already
  sourced

### Requirement: The closing section is current at the pin
The closing section states what falls short today, judged against the code at
the level's pin. A defect that the pinned code has already replaced MUST NOT be
written as a present defect. Its replacement is stated in the present tense
where the reader needs it, and any remaining open item is named; otherwise the
defect is dropped and its history stays in the audit record.

#### Scenario: A defect was replaced before the pin
- **WHEN** a shortcoming the page carries has been replaced in the pinned build
- **THEN** the page states what the software does now, or drops the item, and
  states any part still open as its own RED
