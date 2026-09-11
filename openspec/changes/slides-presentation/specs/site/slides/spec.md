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
The three slides MUST ship in the page markup, chosen and laid out by the build
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

### Requirement: Every slide names the level it draws on
A slide that states anything substantive about the software MUST carry a visible
**drawing on** line naming the level page whose established claim is being
restated, linked to that level (e.g. "drawing on the power-user level"). The
wording on the slide MUST be no stronger than that level's own wording. This is
the deck's counterpart to a footnote — a short pointer, not a machinery-heavy
citation — and it MUST NOT carry a footnoted claim that the named level does not
make.

#### Scenario: A slide restates a level claim
- **WHEN** a slide says something about what Tillandsias does
- **THEN** the level named on its drawing-on line carries the same statement
  with a footnote, and the slide's words are no stronger

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
frame MUST size itself to the available viewport; a slide whose content would
exceed that room MUST still be reached in full — the frame scrolls its own slide
body rather than letting tall content escape the frame and push the page. A
reader on a slide MUST always be able to read every line that slide carries; the
deck MUST NOT clip a line to fit the room, and MUST NOT trade a page scrollbar
for a silently truncated slide.

#### Scenario: A talk is projected fullscreen
- **WHEN** the deck is the active view and the browser is fullscreen
- **THEN** the page shows no scrollbar from the deck, the deck frame fills the
  available height, and the current slide's every line is reachable

#### Scenario: A slide has more text than the frame holds
- **WHEN** a slide's content is taller than the deck frame
- **THEN** the slide's own body scrolls inside the frame, and the page itself
  does not scroll

### Requirement: A slide may embed the site's own figure
A slide MAY embed one of the site's own figures by name. An embedded figure MUST
come from the site's own figure registry — the same SVG the level pages already
ship, drawn by the site's own code — so the deck never imports a foreign image,
a third-party script or a CDN. The figure MUST restate only what its owning
level establishes, exactly as the level page's figureline states it: the slide
embeds the registry figure with its own caption, and MUST NOT redraw, reword or
strengthen it. The slide still carries its drawing-on line naming the level that
owns that figure.

#### Scenario: A slide wants the staircase
- **WHEN** an editor wants a slide to show the methodology's staircases or
  convergence
- **THEN** the slide embeds the registry figure `staircase` or `lln` — the page
  ships that figure on the level that owns it — and the slide's drawing-on line
  names that level

#### Scenario: A slide wants a foreign diagram
- **WHEN** an editor wants to drop in a diagram the site did not draw
- **THEN** it is refused: the deck embeds only the site's own figures, and
  nothing from a third party

### Requirement: The CRDT slides tell the story the methodology establishes
The deck's CRDT slides MUST restate the methodology exactly as the level that
owns it establishes the story: that the project's fastest path to truth is many
small fast prompts whose individual struggles are visibleable, not one big
prompt whose distance to the point cannot be seen from outside; and how keeping
the plan ledger convergent through replicated data types helps the region reduce
uncertainty monotonically — each slide drawing on the methodology level and
saying nothing that level's claim does not carry, with the same floor and the
same asserted-versus-proved honesty the level footnotes.

#### Scenario: The great graph is wanted on a slide
- **WHEN** an editor wants the deck to show the many-small-prompts graph
- **THEN** it is the level's own staircase/LLN figure, drawn on that level, and
  the slide's words are exactly as strong as that level's footnote carries

#### Scenario: A CRDT fact the methodology has not established is wanted
- **WHEN** an editor wants a slide to claim something about the replicated data
  type that no level footnotes (liveness, a zero floor, a proof of monotonicity)
- **THEN** it is refused: the slide keeps, at most, the wording its drawing-on
  level already makes, and anything stronger is a labelled placeholder
