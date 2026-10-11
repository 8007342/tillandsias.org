# Reader-first claims

## Why

The explanation pages were written while the site's own rules were being
worked out, and the rules leaked onto the pages. A five-year-old's page told
its reader about a vocabulary rule the product's screens obey and about a
machine that enforces it. The power-user page ended on the project's CI budget
and "a standing obligation to run the local gate". Footnote labels said
"packet", "(status: ready)", "ruling" and "row". Flags were labelled "path to
green" and "plausible". A pull request number sat in the level 2 prose.

None of that is for the page's reader. The reader of a level is the end user
that level names. The project and its editors are not the reader. Writing
rules, process rules and descriptions of how we verify are meta: they belong in
this repository's specs and editor guides. The history of how a fix happened
and the internal identifiers of the work are anecdote. What stays on the page
is what that reader needs: what the software does, what it does not do yet,
and where to check.

The site's value does not change. Every claim is still checked against the
pinned release. Every known limitation is still disclosed, in plain words. The
evidence is still one click away.

## What Changes

- **A new shared requirement: each block is written for the level's reader.**
  Meta rules, anecdote and internal identifiers are kept off the pages. Their
  home is `docs/matrix/README.md`, `openspec/`, `AGENTS.md` or `skills/`. A
  disclosed limitation is not anecdote and stays.
- **The evidence is offered, not imposed.** The source list at the foot of each
  level is collapsed under "How we know — N sources". The small numbers in the
  text still open the exact cited lines, and hovering one still shows the
  quote. Flag labels are the reader's words: *checked*, *known limitation*,
  *what happens next*, *shown*, *not yet shown*, *does not hold*. The source
  keywords (`GREEN`, `RED`, `PATH`, …) stay as editor vocabulary.
- **The no-remedy sentence is plain.** `No path to green is recorded in the
  repo.` becomes `No fix is planned yet.` It is still written only after
  looking, and it can still be scoped to one item.
- **A fixed shortcoming states the present.** When the pin outruns a RED, the
  RED becomes a GREEN or is dropped. The story of the fix stays in the audit
  record. The past-tense "this used to be broken" note is no longer an optional
  page element.
- **Level 1** no longer has to state the product's "app" vocabulary rule or how
  a machine checks it. That is a rule about the product's own wording, not
  something a five-year-old needs. The "how it gets better" section shrinks to
  two plain facts: a machine checks that a fix breaks nothing that worked, and
  less broken is not the same as perfect.
- **Level 2's** "sharpening" section becomes the question its reader actually
  asks: *will an update break what already works?* It gives the same two honest
  limits.
- **Level 3's** workflow section becomes "How Tillandsias itself is tested".
  What stays is what changes the reader's trust in the binary: the local gate,
  the litmus files that never run, and the absence of server-side checks.
  Budget rulings and standing obligations go.
- **Level 5** gets three deltas (below) and the new flag labels. Level 5 moves
  only through OpenSpec, so the deltas are listed one by one.
- **Home and "What is it?"** The positioning line, the hero and the lede are
  rewritten in plain words. The hero said "folded through your hypervisor",
  which is false on Linux, where no VM is provisioned. The lede said "nothing
  left behind", which is false while the downloaded system image and model
  cache are kept on disk.

### Level 5 deltas

Each delta below is checked against `v56.10.9.1`. No flag changes state, and no
argument changes.

- **D1.** In "What the repository renounces", delete the sentence "This is the
  distinction the CentiColon page's simplified example must preserve." It is an
  instruction to the editors of another page, which is meta. It makes no claim
  about the formal content.
- **D2.** In the complexity-constraint RED, "has no enforcing check identified
  in this audit" becomes "has no enforcing check that we found". The absence
  claim keeps its scope, without the audit vocabulary. The PATH, which says the
  scripts were searched, is unchanged.
- **D3.** In the versioning RED, the PATH "The drift was caught once at a
  release boundary and the shape test corrected; the doctrine file was not."
  becomes "The release-shape test was corrected; the versioning document still
  gives the old meanings." The anecdote goes, and the present state stays. The
  RED it answers, footnoted at the pin, already says the document's semantics
  are false.

### Flags this change raises for the operator

- Level 2's Mac reset PATH used to say that a fix "is in review" as a numbered
  pull request. Nothing at the pin footnotes it. The page now says only "A fix
  is being written. It is not in any release yet." Whether a fix is in review
  needs checking at the next audit.

## Capabilities

### Modified Capabilities

- `site/level-common`: adds reader-first writing and evidence presentation, and
  changes the RED lifecycle so that a fixed RED states the present.
- `site/level-1`: removes the app-vocabulary requirement and narrows the
  required sections and the optional elements.
- `site/level-2`: changes the "sharpening" section, the optional elements and
  the closing-section rule.
- `site/level-3`: changes the required workflow section, the gate requirement,
  the no-remedy sentence and the optional elements.
- `site/level-5`: adds the delta record for this change.

These modify requirements first proposed in `add-level-page-specs`, which has
not been archived yet. Archive that change first, or fold these deltas into it.

## Impact

- `docs/matrix/level-{1..5}-*.md`: prose, flags and footnote labels. Footnotes
  nothing references any more are removed. No footnote target or quote that
  stays was moved, except one quote at level 4 that was narrowed to the part of
  the cited line its label names.
- `scripts/build-matrix.py`: flag labels, the collapsed "How we know" source
  list, and the home, hero, lede and footer prose.
- `docs/matrix/README.md`: the dialect table's reader-facing labels, the new
  no-remedy sentence, and the "reader is the end user" rule.

## Operator decision (2026-10-10)

Approved: "Yes the website is just what the reader needs, not the whole
ledger. It's the top view of the latest state of our Tillandsias stable
release." Archival still waits on `add-level-page-specs` being archived first
(or these deltas folded into it).
