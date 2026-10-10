## ADDED Requirements

### Requirement: Every block is written for the level's reader
Every sentence, flag and footnote label on a level MUST answer a question that
the end user the level names would ask. The project, its editors and its
auditors are not the reader. A page MUST NOT carry:

- meta rules: how the site or the product is written (vocabulary rules, the
  meaning of requirement keywords, which flags a level may use), how the
  project runs its process (cadences, standing obligations, budget rulings), or
  how the site verified a claim (what an audit covered, how open items are
  collected for tracking);
- anecdote: the history of a fix (who found it, when an internal change
  landed, what was reverted first) where the present behaviour can be stated
  instead;
- internal identifiers in prose or in footnote labels: order or packet ids,
  pull request numbers, fragment names, ledger rows, or plan status words
  ("ready", "packet", "row", "ruling") left untranslated.

Meta rules live in `docs/matrix/README.md`, `openspec/`, `AGENTS.md` or
`skills/`. A disclosed limitation is not anecdote. It stays on the page, in the
reader's words, until the code at the pin no longer has it. What the project
tests about itself is reader material only where it changes what the reader
can trust about the software they install.

#### Scenario: A rule about wording reaches a page
- **WHEN** a draft tells the reader which words the product's screens may use,
  or which words this site uses
- **THEN** the sentence is moved to the editor guide or the spec. The page
  keeps only a defect that rule exposes, and only if the reader is affected by
  that defect.

#### Scenario: A limitation is hard to say simply
- **WHEN** a limitation's only existing wording is technical or internal
- **THEN** it is rewritten in the level's words and kept. Dropping it to avoid
  the rewrite is a silent omission, and silent omission is forbidden.

### Requirement: Evidence is offered, not imposed
Each claim's footnote MUST stay one click from the sentence: the number in the
text opens the cited lines at the pinned release, and hovering it shows the
quote. The level's full source list MUST be present in the page and MAY be
collapsed under a plain question such as "How we know". The visible flag labels
MUST be words the reader understands without the editor vocabulary: *checked*,
*known limitation*, *what happens next*, *shown*, *not yet shown*, *does not
hold*.

#### Scenario: A reader wants to check a sentence
- **WHEN** a reader clicks a footnote number
- **THEN** the source opens at the cited lines of the pinned release, whether or
  not the source list is expanded

## MODIFIED Requirements

### Requirement: RED lifecycle at a pin bump
Every RED MUST be true of the code at the level's pinned tag and MUST be
followed by a PATH. When a level's pin moves, a RED the new pin's code has
fixed becomes a GREEN that states the present behaviour, or is dropped when the
level's reader no longer needs it. The story of the fix belongs in the dated
audit record, not on the page. A RED fixed only in a build newer than the pin
stays RED, and its PATH says when the fix landed, citing it with that build's
`@vTAG` footnote. A partial fix says what remains. When the repository records
no remedy, the PATH says `No fix is planned yet.`, written only after looking.

#### Scenario: The pin outruns a RED
- **WHEN** a level's pin moves to a tag whose code fixes a RED
- **THEN** the RED is rewritten as a GREEN in the present tense, footnoted at the
  new pin, or removed, and the audit record notes the fix

#### Scenario: A daily fixes a RED
- **WHEN** a fix exists only in a build newer than the level's pin
- **THEN** the RED stays, and its PATH names the build the fix landed in with an
  `@vTAG` footnote
