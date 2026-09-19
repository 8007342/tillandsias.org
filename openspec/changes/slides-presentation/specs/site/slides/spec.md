## Purpose

**Slides** is the presentation page for a live talk about Tillandsias. It is a
fourth page behind the site's hamburger menu, not an explanation level: it
carries no footnote lists and no flag legend. Its job is to stand in front of a
room and tell the project's story in a handful of slides — the containerized
workflow, Linux security, the portable cloud region, and the methodology that
keeps a distributed region's state conflict-free through replicated data types —
each slide decodable at a glance, and the whole deck moving forward one slide at
a time.

The deck is a presentation, so it must not turn into an argument. The levels are
the argument. A slide names the level it draws on, and everything else on a
slide is either the site's own established one-liners or a labelled placeholder.

## ADDED Requirements

### Requirement: The deck is a page behind the menu
The site MUST present the deck as its own page, **Slides**, reached by a fourth
entry in the collapsing menu after **Live progress**, and the entry MUST be
marked current while the page is shown. The page MUST NOT restate a level's
content wholesale, MUST NOT duplicate the install commands, the flag legend or a
level's prose, and MUST NOT promote the five level tabs into the menu. It MUST
carry a heading a search engine and a screen reader can find, and the frame
around the deck MUST say what it is: a presentation about Tillandsias.

#### Scenario: A reader opens the menu
- **WHEN** a reader opens the menu
- **THEN** Slides is listed after Live progress, and it is marked as current
  when the deck is on screen

#### Scenario: A claim is wanted on a slide
- **WHEN** an editor wants a slide to state something the site has not yet
  established on a level page
- **THEN** it is first added to the level that owns it, with its footnote, and
  the slide then names that level

### Requirement: One slide at a time, and a way to move
The deck MUST show exactly one slide at a time and MUST provide a mechanism to
move from slide **N** to slide **N+1** and back to **N−1**: visible prev/next
controls, arrow and home/end keys (ArrowRight/ArrowLeft or Space for next, Home
for the first slide, End for the last), and — because the site rejects nothing
that runs without a script — the markup MUST contain a way to reach the deck's
first slide without scripting. The reader MUST always see where they are: a
counter (e.g. "2 / 3", where the denominator is the deck's actual slide count as rendered, not a fixed number in this spec) and a progress rail that fills as the reader advances.

#### Scenario: A talk moves forward
- **WHEN** the reader presses the next control or the right arrow or space
- **THEN** slide N is hidden and slide N+1 is shown, the counter reads N+1, and
  the menu is not involved

#### Scenario: A talk moves back
- **WHEN** the reader presses the previous control or the left arrow
- **THEN** the deck shows slide N−1

#### Scenario: The deck is asked to move past either end
- **WHEN** the reader is on the first or last slide and presses the control
  beyond it
- **THEN** nothing happens: the deck does not wrap, does not jump, and does not
  leave the page

#### Scenario: The first slide is wanted without scripting
- **WHEN** a browser runs no script and follows the page's link into Slides
- **THEN** the first slide of the deck is visible

### Requirement: A slide is addressable
The page MUST be reachable at a bare fragment (`#slides`), and each slide at its
own fragment (`#slides-2`). Following such a link MUST open the slides page with
that slide shown and the counter reading its number. The deck MUST re-render
from the URL when the fragment changes, so the browser's back button undoes a
slide change. An empty input (no slide number) MUST mean the first slide.

#### Scenario: A talk starts at slide two
- **WHEN** a reader follows a link to `#slides-2`
- **THEN** the slides page opens with the second slide shown and the counter
  reading its number over the deck's actual count, e.g. 2 / 3

#### Scenario: The back button is pressed
- **WHEN** a reader advances from slide two to slide three and then presses back
- **THEN** the deck returns to slide two

#### Scenario: A broken slide number
- **WHEN** a link names a slide beyond the last (or below the first)
- **THEN** the number is clamped to the nearest real slide and the URL is
  corrected, never left pointing at nothing

### Requirement: The deck ships inside the page
All slides MUST ship in the page markup, chosen and laid out by the build
from a source beside the generator, and MUST NOT be fetched, drawn or animated
from a third party. The site loads no external images; the deck inherits that
rule — no external image, no external script, no CDN content in the deck. The
deck source MUST be the only place an editor changes the deck; the rendered
markup is a build product. A rebuild from unchanged sources MUST reproduce the
same slide markup in the same order.

#### Scenario: The deck is reworded
- **WHEN** an editor wants to change a slide
- **THEN** they edit the deck source and rebuild; the rendered page is not the
  thing that was edited

#### Scenario: The page is built twice
- **WHEN** the same sources are built twice
- **THEN** the two pages carry identical slide markup, in the same order

### Requirement: Editorial provenance stays outside the presentation
Slides MUST NOT display links back to the five explanation levels or a
"drawing on" footer. The source MAY retain `draws_on` metadata for editorial
review. Software claims MUST remain no stronger than their supporting evidence;
illustrations and proposed modeling patterns MUST be distinguishable from
measured behavior.

#### Scenario: A slide restates a level claim
- **WHEN** a slide says something about what Tillandsias does
- **THEN** its source records the supporting level, its words are no stronger,
  and no reference footer is rendered

#### Scenario: A slide borrows nothing
- **WHEN** a slide states only presentation furniture — the deck's own labels,
  the counter, "this is still to come"
- **THEN** no drawing-on line is required

### Requirement: A placeholder is labelled as one
Until a slide's content is written, the slide MUST hold its place honestly: the
empty region MUST carry a visible label saying content is still to come, drawn
in the site's own theme, and MUST NOT present a stand-in as finished content or
a sketch as a claim. The placeholder MUST NOT make the claim the content will
eventually make — the label is room being held, and a reader must be able to
tell it is an empty room. A slide may hold several labelled placeholders in the
same frame.

#### Scenario: A slide's content arrives
- **WHEN** the content is written and checked against the level it draws on
- **THEN** the placeholder label is removed with the content it was holding
  room for

#### Scenario: A stand-in claim is offered
- **WHEN** an editor wants to fill the space with a phrase the site has not
  established
- **THEN** it is refused: the slide keeps the labelled placeholder rather than a
  claim without a home level

### Requirement: The three slides tell the planned story
The deck MUST open with **the thesis** slide: what Tillandsias is, in the site's
own established words. It MUST then carry **the pillars** slide naming the three
pillars of the story — the containerized workflow, Linux security, and the
portable cloud region — and MUST close with **the mechanism** slide naming the
methodology and conflict-free replicated data types. That ordering is the
deck's contract: adding a slide between or ahead of these three is a change to
this spec. A change MAY add a CRDT-methodology tail after the mechanism slide — never between or ahead of the three — and each tail slide still names the level it draws on, no stronger. Each of the three slides MUST show its title and MUST hold space for
its content with labelled placeholders where the content is not yet written.

#### Scenario: A fourth slide is proposed
- **WHEN** someone wants to insert a slide between the thesis and the pillars
- **THEN** it is a change to this requirement, and it moves the counter with it

#### Scenario: The story changes
- **WHEN** a pillar of the story is renamed, added or dropped at a later change
- **THEN** the pillars slide is edited to match, and its drawing-on lines are
  re-checked
### Requirement: The deck fits the viewport
The deck MUST render without causing a scrollbar on the page itself: while the
deck is the active view, the page MUST NOT acquire a scrollbar from the deck's
frame, so the deck displays cleanly in a fullscreen presentation. The deck
frame MUST use the available viewport width and height. Slides MUST reflow their
figures and text for the screen shape, then scale the complete content if needed.
Neither the page, slide body nor an embedded figure may introduce a vertical or
horizontal scroll pane. The deck MUST NOT hide overflow as a substitute for
fitting every line and figure inside the frame. Navigation MUST remain visible.

#### Scenario: A talk is projected fullscreen
- **WHEN** the deck is the active view and the browser is fullscreen
- **THEN** the page shows no scrollbar from the deck, the deck frame fills the
  available height, and the current slide's every line is reachable

#### Scenario: A slide has more text than the frame holds
- **WHEN** a slide's content is taller than the deck frame
- **THEN** the complete slide reflows and scales to fit, without clipping or
  either axis of scrolling

#### Scenario: The viewport changes during a talk
- **WHEN** the browser is resized or the device rotates
- **THEN** the current slide is fitted again without changing its content,
  fragment or position in the deck

### Requirement: A slide may embed the site's own figure
A slide MAY embed one of the site's own figures by name. An embedded figure MUST
come from the site's own figure registry, drawn by the site's own code, so the
deck never imports a foreign image, a third-party script or a CDN. Figures MAY
be designed specifically for slides. Their captions MUST distinguish illustrative
models from measurements and retain the assumptions behind convergence claims.

#### Scenario: A slide wants the staircase
- **WHEN** an editor wants a slide to show the methodology's staircases or
  convergence
- **THEN** the slide embeds a registry figure with its assumptions intact,
  retaining editorial provenance in the source

#### Scenario: A slide wants a foreign diagram
- **WHEN** an editor wants to drop in a diagram the site did not draw
- **THEN** it is refused: the deck embeds only the site's own figures, and
  nothing from a third party

### Requirement: The CRDT slides tell the story the methodology establishes
The deck MUST explain the role of small checked iterations and a convergent
evidence record. It MUST distinguish Git's file histories from CRDT event-set
and field merge rules: arbitrary source files, specs and prose do not acquire
conflict-free semantic merges merely by being versioned in Git.

The closing sequence MUST cover artifact evidence vectors, iterative history,
finite evidence bounds, and a combined tree-of-refinement illustration. The
tree MUST be identified as a methodology metaphor for histories that are DAGs.
Finite stabilization MUST be conditional on fixed finite requirements and a
fixed monotone, inflationary refinement rule. The bound is on strict increases
in modeled evidence, not on history size, execution time or real-world truth.
The methodology's approximation of this ideal MUST remain an aim, not an
unconditional convergence or zero-residual guarantee.

#### Scenario: The great graph is wanted on a slide
- **WHEN** an editor wants the deck to show the many-small-prompts graph
- **THEN** it is the level's own staircase/LLN figure, drawn on that level, and
  the slide's words are exactly as strong as that level's footnote carries

#### Scenario: A CRDT fact the methodology has not established is wanted
- **WHEN** an editor wants a slide to claim something about the replicated data
  type that no level footnotes (liveness, a zero floor, a proof of monotonicity)
- **THEN** it is refused: the slide keeps, at most, the wording its drawing-on
  level already makes, and anything stronger is a labelled placeholder
