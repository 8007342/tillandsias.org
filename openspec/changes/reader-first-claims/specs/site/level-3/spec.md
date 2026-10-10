## MODIFIED Requirements

### Requirement: Gate and CI statements
The section on how Tillandsias itself is tested MUST stay accurate at the pin
and sourced to `methodology/ci.yaml`,
`openspec/litmus-tests/unbound-grandfathered.txt` and the workflow files. It
states that checks run in a local gate, how many litmus files have never been
run by any suite, and that no server checks a change before release. Any count
it gives is the count at the pin. It MUST NOT carry the project's process
obligations or the history of how the arrangement came about.

#### Scenario: Gate claims stay sourced
- **WHEN** the gate section is edited
- **THEN** the never-run count and the workflow inventory still match the pinned
  tree, and are footnoted with quotes that pass the checked build

### Requirement: Required sections
The page MUST carry, in this order: its own title; an opening section stating
what a launch hands the reader with no configuration, which MUST carry the one
launch command, the zero-configuration statement attributed to the context file
the agent reads first, and the channel contract required below; one subsection
per subsystem that a launch brings up unconfigured, each saying what the reader
gets and what falls short at the pin; an anatomy section naming what runs where,
the single-egress rule, how the enclave's membership is recorded, and how a
reader starts one; a mounts-and-boundary section saying what is addressable from
inside a forge and what is not, that agent tooling exists only inside the image,
whether the working tree is touched by default, and the push-or-lose rule; a
survivorship section stating what crosses a stop, a `podman system reset` and a
`--reset-guest`; and a section on how Tillandsias itself is tested, as the gate
requirement states it. The rendered footnote list MUST be present and MUST be
last.

#### Scenario: Every required section is present
- **WHEN** an editor reviews the page
- **THEN** each required section exists in the stated order, carries the purpose
  named for it, and the footnote list is last

#### Scenario: A subsystem has nothing wrong with it at the pin
- **WHEN** no shortcoming holds for a subsystem against the code at the pin
- **THEN** its subsection stays and says what it gives, rather than being
  deleted for having no RED

### Requirement: Optional sections and elements
The page MAY carry: figures, at most one per section, each carrying that
section's single idea; a GREEN in a subsystem subsection where the
zero-configuration result is worth separating from the prose; and a sentence
naming the per-platform way a reader starts the software. None of these is
required, and dropping one MUST NOT be treated as a regression. Each one, when
present, MUST obey every wording and sourcing rule in this spec.

#### Scenario: An optional element is dropped
- **WHEN** an optional element is removed because its source no longer supports
  it
- **THEN** no requirement of this spec is violated by its absence

### Requirement: Every item of a RED is answered by a PATH
A RED that states several shortcomings MUST be answered item by item. Each item
either gets its remedy or is named in a scoped no-remedy clause. No item may be
silently dropped because another item in the same RED has a recorded remedy.
Where the repository records no remedy for an item, the PATH MUST say `No fix
is planned yet.`, optionally scoped to the item it answers ("For the apex
route, no fix is planned yet."). The sentence MUST NOT be written without
looking: where the repository records a remedy, however partial, the PATH says
what is recorded, in the reader's words and without plan status vocabulary.

#### Scenario: A RED carries three shortcomings
- **WHEN** a RED names three shortcomings and only one has a recorded remedy
- **THEN** the PATH gives that remedy and names the other two in a scoped
  no-remedy clause

#### Scenario: A remedy exists after all
- **WHEN** the repository records a work item that would close the gap
- **THEN** the PATH describes it and footnotes it, instead of claiming that
  nothing is planned
