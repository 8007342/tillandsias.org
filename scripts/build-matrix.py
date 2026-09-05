#!/usr/bin/env python3
"""Assemble var/html/index.html from docs/matrix/level-*.md.

The sources are written in a small markdown dialect (see docs/matrix/README.md):
headings, bullets, GREEN/RED/PATH/NOTE and PROVEN/PLAUSIBLE/REFUTED callouts,
$math$, @fig:NAME figures, and [^n] footnotes whose targets are repo-relative
paths resolved against the release tag each level is pinned to, so a reader
lands on the exact line, with an optional verbatim quote shown in the tooltip.
"""
import html
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import facts  # noqa: E402
import figures  # noqa: E402
import issues  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "matrix"
# TILLANDSIAS_OUT redirects the output, so a trial build (see PIN_OVERRIDE) does
# not overwrite the published page.
OUT = pathlib.Path(os.environ.get("TILLANDSIAS_OUT") or ROOT / "var" / "html" / "index.html")

REPO = "https://github.com/8007342/tillandsias"

# TILLANDSIAS_PIN_OVERRIDE=vX.Y.Z.B builds every level as if it were pinned to
# that tag. With a checkout present, the broken-target list it prints is the
# exact work list for moving the levels to that release. It never edits LEVELS.
PIN_OVERRIDE = os.environ.get("TILLANDSIAS_PIN_OVERRIDE", "").strip() or None

# Each level pins the release its copy was verified against, not main: a reader
# clicking a line number must land on the line we actually quoted. Levels move
# independently so that a page whose owner accepts only tiny deltas (level 5)
# is not dragged forward by a re-verification of the others. The newest pin is
# shown in the page header as the release the site was last checked against.
# Each row: slug, tab title, blurb, continuation note, pinned release, and the
# plant aside — a glyph from figures.PLANTS and one true sentence about the
# genus the project is named after. The aside is page furniture, like the tab
# title and the blurb: it lives here rather than in the level's source so the
# explanation files carry only their argument, and so level 5, which moves
# only in individually tracked deltas, is not touched to add decoration.
LEVELS = [
    ("level-1-five",     "Like I'm 5",
     "The simplest way of putting it that is still true.", "",
     "v56.9.2.1",
     ("ionantha",
      "A real tillandsia needs no soil and no pot — it drinks from the air, and borrows nothing.")),
    ("level-2-phone",    "I barely understand my phone",
     "Straight answers to what you are actually wondering: privacy, cost, and what breaks.",
     "Picks up where “like I’m 5” left off.",
     "v56.9.2.1",
     ("bulbosa",
      "A tillandsia is an epiphyte, not a parasite: it rests on its tree and takes nothing from it.")),
    ("level-3-power",    "I'm a power user",
     "The anatomy: what runs where, what survives a teardown, and where the sharp edges are.",
     "Assumes the two levels before it.",
     "v56.9.2.1",
     ("xerographica",
      "Its roots only grip; the leaves do the drinking — a plant that runs rootless.")),
    ("level-4-security", "I'm a Cyber Security expert",
     "The architecture interrogated rather than described — boundaries, egress, provenance, "
     "and what the tests do not actually test.",
     "Assumes the three levels before it.",
     "v56.9.2.1",
     ("usneoides",
      "Silvery leaf scales open to take water in, then trap air to keep it: every exchange "
      "across one surface.")),
    ("level-5-phd",      "I'm a MathWiz / Hacker",
     "And you would like me to be condescending about it. Very well.",
     "Assumes everything before it. Mathematics from here down.",
     "v56.9.2.1",
     ("caput-medusae",
      "A monocot bromeliad flowers once and dies, leaving offsets behind — the pup is never "
      "the parent.")),
]


def version_key(ref):
    return tuple(int(x) for x in re.findall(r"\d+", ref))


if PIN_OVERRIDE:
    LEVELS = [lvl[:4] + (PIN_OVERRIDE,) + lvl[5:] for lvl in LEVELS]
    print("  trial build: every level pinned to %s (LEVELS untouched)" % PIN_OVERRIDE)

SITE_REF = max((lvl[4] for lvl in LEVELS), key=version_key)


# Rolling stable installers. These deliberately point at GitHub's
# /releases/latest/ rather than anything hosted here: this site is static HTML
# and redeploys on commit, while the release channel moves on its own.
DL = "https://github.com/8007342/tillandsias/releases/latest/download"
INSTALL = [
    ("Linux",   "curl -fsSL %s/install.sh | bash" % DL),
    ("macOS",   "curl -fsSL %s/install-macos.sh | bash" % DL),
    ("Windows", "irm %s/install-windows.ps1 | iex" % DL),
]

# kind -> (css class, glyph, visible label). GREEN/RED say what the *thing*
# does; PROVEN/PLAUSIBLE/REFUTED say how good *our argument* for it is.
FLAGS = {
    "GREEN":     ("flag-green",     "●", "verified"),
    "RED":       ("flag-red",       "●", "shortcoming"),
    "PATH":      ("flag-path",      "→", "path to green"),
    "NOTE":      ("flag-note",      "•", "note"),
    "PROVEN":    ("flag-proven",    "✓", "shown"),
    "PLAUSIBLE": ("flag-plausible", "∼", "plausible"),
    "REFUTED":   ("flag-refuted",   "✗", "does not hold"),
}

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
EM = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
FN_REF = re.compile(r"\[\^(\d+)\]")
MATH_INLINE = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
# `[^n]: Label | target` with an optional ` @vX.Y.Z.B` after the target: that
# footnote resolves against the named release instead of the level's pin, for
# a PATH line that acknowledges a fix which exists only in a newer channel.
FN_DEF = re.compile(r"^\[\^(\d+)\]:\s*(.+?)\s*\|\s*(\S+?)(?:\s+@(v[\d.]+))?\s*$")

broken_links = []
# (level, ref) pairs a footnote cited but no checkout could answer for. Silence
# here once let a build report "all checked footnote targets resolve" while
# every daily-channel footnote went unopened, so an unchecked target is now a
# first-class result rather than an early return.
unchecked = set()


# --- checked builds -----------------------------------------------------------
#
# TILLANDSIAS_CLONE_DIR=/dir   checkouts named by tag: /dir/v56.9.5.1, ...
# TILLANDSIAS_CLONE=/path      one checkout; its tag is read from git, and it
#                              is used only for levels pinned to that tag.
# With neither the page still builds; with either, every footnote target of a
# level whose checkout is present is checked — path exists, line range inside
# the file, quote found verbatim inside the cited range — and the build prints
# anything that does not resolve and exits non-zero.

def _clone_tag(path):
    try:
        out = subprocess.run(["git", "-C", str(path), "describe", "--tags", "--exact-match"],
                             capture_output=True, text=True, check=False)
        return out.stdout.strip() or None
    except OSError:
        return None


def _clones():
    found, unknown = {}, None
    d = os.environ.get("TILLANDSIAS_CLONE_DIR", "")
    if d:
        for p in pathlib.Path(d).iterdir() if pathlib.Path(d).is_dir() else []:
            if p.is_dir() and p.name.startswith("v"):
                found[p.name] = p
    one = os.environ.get("TILLANDSIAS_CLONE", "")
    if one:
        p = pathlib.Path(one)
        tag = _clone_tag(p)
        if tag:
            found.setdefault(tag, p)
        else:
            unknown = p
            print("  ! TILLANDSIAS_CLONE has no exact tag; checking every level against it")
    return found, unknown


CLONES, CLONE_UNTAGGED = _clones()


def clone_for(ref):
    return CLONES.get(ref) or CLONE_UNTAGGED


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def norm_source(lines):
    """Cited lines with comment leaders stripped, so a quote that spans two
    lines of a shell, YAML or Rust comment still matches verbatim."""
    return norm("\n".join(re.sub(r"^\s*(?:#|//[!/]?|--|\*)(?:\s+|$)", "", x) for x in lines))


def check_target(level, ref, target, quote):
    """Record anything that does not resolve at the release it names."""
    clone = clone_for(ref)
    if clone is None:
        unchecked.add((level, ref))
        return
    path, _, anchor = target.partition("#")
    file = clone / path
    if not file.exists():
        broken_links.append((level, target, "path does not exist at %s" % ref))
        return
    try:
        lines = file.read_text(errors="replace").splitlines()
    except OSError as exc:
        broken_links.append((level, target, str(exc)))
        return
    lo, hi = 1, len(lines)
    if anchor:
        m = re.match(r"^L(\d+)(?:-L(\d+))?$", anchor)
        if not m:
            broken_links.append((level, target, "malformed line anchor"))
            return
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        if lo < 1 or hi > len(lines) or lo > hi:
            broken_links.append(
                (level, target, "line range outside file (%d lines)" % len(lines)))
            return
    if quote:
        cited = lines[lo - 1:hi]
        q = norm(quote)
        if q not in norm("\n".join(cited)) and q not in norm_source(cited):
            broken_links.append((level, target, "quote not found in the cited range"))


def footnote_url(target, ref):
    """Repo-relative path (with optional #L anchors) or external URL -> href."""
    if target.startswith(("http://", "https://")):
        return target, True
    path, _, anchor = target.partition("#")
    url = "%s/blob/%s/%s" % (REPO, ref, path)
    return url + ("#" + anchor if anchor else ""), False


# --- rendering ------------------------------------------------------------------

class Ctx:
    """Per-level rendering state: slug, pinned ref, footnote table, resolved urls."""

    def __init__(self, level, ref, notes):
        self.level, self.ref, self.notes = level, ref, notes
        self.fns = set()
        self.urls = {n: footnote_url(t, own or ref) for n, (_, t, _, own) in notes.items()}

    def ref_for(self, n):
        return self.notes[n][3] or self.ref


def inline(text, ctx):
    """Escape, then apply inline markup. Code and math are shielded from emphasis."""
    out = html.escape(text.strip())
    shield = []

    def stash(markup):
        shield.append(markup)
        return "\x00%d\x00" % (len(shield) - 1)

    out = INLINE_CODE.sub(lambda m: stash("<code>%s</code>" % m.group(1)), out)
    # KaTeX reads textContent, so entities land as real characters. \( \) are
    # the inline delimiters configured on the page.
    out = MATH_INLINE.sub(lambda m: stash('<span class="math">\\(%s\\)</span>' % m.group(1)), out)
    out = BOLD.sub(r"<strong>\1</strong>", out)
    out = EM.sub(r"<em>\1</em>", out)

    def ref(m):
        n = m.group(1)
        ctx.fns.add(n)
        # The number opens the source in a new tab; the tooltip carries the
        # footnote's label, its verbatim quote when one is recorded, and the
        # target, so a reader can judge a citation without leaving the sentence.
        if n in ctx.notes:
            label, target, quote, own = ctx.notes[n]
            url, external = ctx.urls[n]
            shown = target if not external else re.sub(r"^https?://", "", target)
            if own and not external:
                shown += " @" + own
            attrs = (' href="%s" target="_blank" rel="noopener" data-label="%s" data-target="%s"'
                     % (html.escape(url, quote=True), html.escape(label, quote=True),
                        html.escape(shown, quote=True)))
            if quote:
                attrs += ' data-quote="%s"' % html.escape(quote, quote=True)
            attrs += ' aria-label="Footnote %s: %s (opens the source in a new tab)"' % (
                n, html.escape(label, quote=True))
        else:
            attrs = ' href="#f%s-%s"' % (ctx.level, n)
        return '<sup class="fnref" id="r%s-%s"><a%s>%s</a></sup>' % (ctx.level, n, attrs, n)

    out = FN_REF.sub(ref, out)
    return re.sub(r"\x00(\d+)\x00", lambda m: shield[int(m.group(1))], out)


def render(lines, ctx):
    out, para, items, ordered = [], [], [], [False]
    math_buf, in_math = [], [False]
    callout = []  # [css class, icon, label, [paragraphs]] while one is open

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para), ctx))
            para.clear()

    def flush_items():
        if items:
            tag = "ol" if ordered[0] else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(
                "<li>%s</li>" % inline(i, ctx) for i in items), tag))
            items.clear()
            ordered[0] = False

    def flush_callout():
        if callout:
            cls, icon, label, paras = callout[0]
            paras = [x for x in paras if x.strip()]
            body = "".join(
                "<p>%s%s</p>" % ('<span class="callout-k">%s</span> ' % label if i == 0 else "",
                                 inline(x, ctx))
                for i, x in enumerate(paras))
            out.append(
                '<div class="callout %s"><span class="callout-icon" aria-hidden="true">%s</span>'
                '<div>%s</div></div>' % (cls, icon, body))
            callout.clear()

    def flush():
        flush_para()
        flush_items()
        flush_callout()

    for raw in lines:
        line = raw.strip()

        if in_math[0]:
            if line.endswith("$$"):
                math_buf.append(line[:-2])
                in_math[0] = False
                body = html.escape(" ".join(x for x in math_buf if x).strip())
                out.append('<div class="math-block">\\[%s\\]</div>' % body)
                math_buf.clear()
            else:
                math_buf.append(line)
            continue

        if line.startswith("$$"):
            flush()
            rest = line[2:]
            if rest.endswith("$$") and rest[:-2].strip():
                body = html.escape(rest[:-2].strip())
                out.append('<div class="math-block">\\[%s\\]</div>' % body)
            else:
                in_math[0] = True
                if rest.strip():
                    math_buf.append(rest)
            continue

        if not line:
            if callout:
                flush_para()
                flush_items()
            else:
                flush()
        elif line.startswith("@fig:"):
            flush()
            name = line[5:].strip()
            if name in figures.FIGURES:
                out.append(figures.FIGURES[name])
            else:
                print("  ! unknown figure @fig:%s in %s" % (name, ctx.level))
        elif line.startswith("### "):
            flush()
            out.append("<h4>%s</h4>" % inline(line[4:], ctx))
        elif line.startswith("## "):
            flush()
            out.append("<h3>%s</h3>" % inline(line[3:], ctx))
        elif line.startswith("# "):
            # The level's own title, under the tab that already names the audience.
            flush()
            out.append('<h2 class="panel-h">%s</h2>' % inline(line[2:], ctx))
        elif line.startswith(">"):
            rest = line.lstrip(">").strip()
            kind, _, body = rest.partition(":")
            if kind.strip().upper() in FLAGS:
                # A new flag closes whichever callout was open before it.
                flush()
                cls, icon, label = FLAGS[kind.strip().upper()]
                callout.append([cls, icon, label, [body.strip()]])
            elif callout:
                # A bare ">" separates paragraphs inside the open callout;
                # anything else continues it.
                if rest:
                    callout[0][3].append(rest)
                elif callout[0][3][-1]:
                    callout[0][3].append("")
            elif rest:
                para.append(rest)
        elif re.match(r"^[-*+]\s+", line) or re.match(r"^\d+[.)]\s+", line):
            is_ord = bool(re.match(r"^\d+[.)]\s+", line))
            if items and is_ord != ordered[0]:
                flush_items()
            flush_para()
            ordered[0] = is_ord
            items.append(re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line))
        elif items:
            items[-1] += " " + line
        else:
            para.append(line)

    flush()
    return "\n".join(out)


def parse(path, level):
    """Split a source file into body lines and footnote definitions.

    A footnote is `[^n]: Label | target`, optionally followed by one or more
    lines starting with `>` that carry a verbatim quote from the target.
    """
    body, notes, in_notes, last = [], {}, False, None
    for line in path.read_text().splitlines():
        if re.match(r"^##\s+Footnotes\s*$", line, re.I):
            in_notes = True
            continue
        if in_notes:
            s = line.strip()
            m = FN_DEF.match(s)
            if m:
                last = m.group(1)
                notes[last] = [m.group(2), m.group(3), "", m.group(4)]
            elif s.startswith(">") and last:
                notes[last][2] = (notes[last][2] + " " + s.lstrip(">").strip()).strip()
            elif s:
                print("  ! unparsed footnote line in %s: %s" % (level, line[:70]))
        else:
            body.append(line)
    return body, {n: tuple(v) for n, v in notes.items()}


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
COLUMN_TITLE = {
    "red": ("Found, not yet tracked",
            "Newly found, undocumented or untracked, and still carrying real uncertainty."),
    "yellow": ("Tracked, with a plan",
               "Documented and being worked or actively followed, uncertainty low enough to act on."),
    "green": ("Done, and holding",
              "Complete, and the thing it was about now meets its own written criteria."),
}


def home_view():
    """The landing placeholder: a wordmark, and one fact drawn in the browser."""
    pool = "".join('<li>%s</li>' % html.escape(f) for f in facts.FACTS)
    return ('<section class="view" id="view-home" role="tabpanel" aria-labelledby="nav-home">'
            '<div class="homecard">'
            '<div class="homeart" role="img" aria-label="Placeholder for an image of the Tlatoāni">'
            '%s<span class="homeart-note">image to come</span></div>'
            '<h1 class="wordmark">Tillandsias</h1>'
            '<p class="byline">by Tlatoāni</p>'
            '<p class="fact" id="fact">%s</p>'
            '<ul class="factpool" id="factpool" hidden>%s</ul>'
            '<p class="homelead">Local hardware. Free software. Nothing rented, nothing metered, '
            'nothing left behind.</p>'
            '<p class="homego"><button class="gobtn" data-go="view-what">What is it?</button>'
            '<button class="gobtn" data-go="view-progress">Live progress</button></p>'
            '</div></section>'
            % (figures.PLANTS["xerographica"], html.escape(facts.FACTS[0]), pool))


def progress_view():
    """Three columns, straight off the ledger's own ladder. Every finding is in
    exactly one of them, because the ladder puts it there."""
    try:
        state = issues.fold()
    except Exception as exc:                       # a malformed fragment must not
        print("  ! issues ledger did not fold: %s" % exc)   # take the whole page down
        state = {}

    cols = {"red": [], "yellow": [], "green": []}
    for f in state.values():
        cols.get(f.get("column", "red"), cols["red"]).append(f)
    for rows in cols.values():
        rows.sort(key=lambda f: (SEVERITY_ORDER.get(f.get("severity"), 3), f["id"]))

    total = len(state) or 1
    done = len(cols["green"])
    tracked = len(cols["yellow"])

    def card(f):
        ev = f.get("events", [])
        first = ev[0].get("ts", "")[:10] if ev else ""
        last = ev[-1].get("ts", "")[:10] if ev else ""
        dep = "".join('<span class="dep">%s</span>' % html.escape(d)
                      for d in f.get("depends_on", []))
        # A runtime finding this project cannot file itself says so, so the gap
        # between "recorded here" and "in front of the people who can fix it"
        # is visible rather than quietly forgotten.
        if f.get("upstream"):
            up = ('<a class="up" href="%s" target="_blank" rel="noopener">filed &#8599;</a>'
                  % html.escape(f["upstream"], quote=True))
        elif f.get("repo") == "tillandsias":
            up = '<span class="up unfiled">not filed upstream</span>'
        else:
            up = ""
        when = ((" &middot; found %s" % first) if first else " &middot; no dated event") + \
               ((" &middot; moved %s" % last) if last and last != first else "")
        return ('<li class="card sev-%s"><div class="card-h"><code>%s</code>'
                '<span class="repo">%s</span><span class="sev">%s</span></div>'
                '<p class="card-t">%s</p><p class="card-m">%s%s</p>%s%s</li>'
                % (html.escape(f.get("severity", "low")), html.escape(f["id"]),
                   html.escape(f.get("repo", "")), html.escape(f.get("severity", "")),
                   html.escape(f.get("title", "(untitled)")),
                   html.escape(f.get("area", "")), when,
                   ('<p class="card-d">needs %s</p>' % dep) if dep else "",
                   ('<p class="card-u">%s</p>' % up) if up else ""))

    def column(key):
        title, blurb = COLUMN_TITLE[key]
        rows = cols[key]
        return ('<section class="col col-%s"><h3>%s <span class="n">%d</span></h3>'
                '<p class="col-b">%s</p><ul class="cards">%s</ul></section>'
                % (key, title, len(rows), blurb,
                   "".join(card(f) for f in rows) or '<li class="card empty">nothing here yet</li>'))

    bar = ('<div class="bar" role="img" aria-label="%d of %d findings resolved, %d tracked">'
           '<span class="bar-g" style="width:%.1f%%"></span>'
           '<span class="bar-y" style="width:%.1f%%"></span></div>'
           % (done, len(state), tracked, 100.0 * done / total, 100.0 * tracked / total))

    return ('<section class="view" id="view-progress" role="tabpanel" aria-labelledby="nav-progress">'
            '<div class="wrap">'
            '<h2 class="view-h">Live progress</h2>'
            '<p class="view-lede">Every defect this project has found, in one of three columns and '
            'nowhere else. A finding climbs from left to right and comes back only when someone '
            'writes down why. The columns are not maintained by hand: they are the ledger\'s own '
            'ladder, folded at build time from <code>issues.d/</code>.</p>'
            '%s'
            '<p class="tally"><b>%d</b> findings &middot; <b>%d</b> done &middot; <b>%d</b> tracked '
            '&middot; <b>%d</b> waiting &middot; <b>%d</b> filed upstream</p>'
            '<div class="cols">%s%s%s</div>'
            '%s'
            '</div></section>'
            % (bar, len(state), done, tracked, len(cols["red"]),
               sum(1 for f in state.values() if f.get("upstream")),
               column("red"), column("yellow"), column("green"),
               centicolon_note()))


def centicolon_note():
    """What we intend to plot here, and why there is no data yet. The site does
    not get to show a convergence curve it cannot compute."""
    return ('<section class="cc"><h3>Convergence, once there is something to plot</h3>'
            '<p>The plan is to grade this project the way the runtime grades itself, with its '
            'CentiColon score, and to show it per component on a logarithmic time axis so the '
            'newest work occupies the most width — the shape the staircase figure on the '
            'power-user level already draws for the argument.</p>'
            '<p>Two things are missing, and the page will not pretend otherwise. The score the '
            'runtime publishes today is a pass rate over a hardcoded weight table of continuous '
            'integration checks, not the arithmetic its own specification defines: none of the '
            'base weights, multipliers, cap rules or penalties in the methodology is computed '
            'anywhere in that tree. And nothing yet scores <em>this</em> project at all. Until '
            'both change, the bar above counts findings, which is a real measurement of a small '
            'thing rather than a fabricated measurement of a large one.</p>'
            '<p class="cc-open">Tracked as findings in the ledger, not as a promise here.</p>'
            '</section>')


def build():
    panels, tabs = [], []
    for idx, (slug, title, blurb, cont, ref, plant) in enumerate(LEVELS):
        path = SRC / ("%s.md" % slug)
        if path.exists():
            body, notes = parse(path, slug)
        else:
            body, notes = ["Not written yet."], {}
        ctx = Ctx(slug, ref, notes)
        content = render(body, ctx)

        # The plant aside sits under the level's own title, above its first
        # section: an aside, in the page's quietest voice, never a claim about
        # the software and so never footnoted.
        glyph, fact = plant
        note = ('<p class="plantnote"><span class="plant-ico" aria-hidden="true">%s</span>'
                '<span>%s</span></p>' % (figures.PLANTS[glyph], html.escape(fact)))
        head = re.search(r"</h2>", content)
        content = (content[:head.end()] + "\n" + note + content[head.end():]
                   if head else note + "\n" + content)

        missing = sorted(ctx.fns - set(notes), key=int)
        if missing:
            print("  ! %s references undefined footnotes: %s" % (slug, ", ".join(missing)))
        unused = sorted(set(notes) - ctx.fns, key=int)
        if unused:
            print("  ! %s defines unreferenced footnotes: %s" % (slug, ", ".join(unused)))

        fn_html = ""
        if notes:
            rows = []
            for n in sorted(notes, key=int):
                label, target, quote, own = notes[n]
                url, external = ctx.urls[n]
                if not external:
                    check_target(slug, own or ref, target, quote)
                shown = target if not external else re.sub(r"^https?://", "", target)
                tag = ('<span class="fn-tag" title="This footnote points at a newer release than '
                       'the rest of the level">@%s</span>' % own) if own and not external else ""
                q = '<q class="fn-quote">%s</q>' % html.escape(quote) if quote else ""
                rows.append(
                    '<li id="f%s-%s"><a class="fn-back" href="#r%s-%s" aria-label="back to text">%s</a>'
                    '<span class="fn-body">%s <a class="fn-link" href="%s" target="_blank" '
                    'rel="noopener">%s<span class="ext" aria-hidden="true">&#8599;</span></a>%s%s</span></li>'
                    % (slug, n, slug, n, n, html.escape(label), url, html.escape(shown), tag, q))
            quoted = sum(1 for v in notes.values() if v[2])
            fn_html = ('<section class="footnotes"><h3>Footnotes</h3>'
                       '<p class="fn-note">Every link points at release <code>%s</code> of the '
                       'source repository, so line numbers match the text above; a link marked '
                       'with its own release tag points at that newer release instead. A footnote '
                       'number in the text opens its source in a new tab; hover it for the '
                       'quoted lines.</p>'
                       '<ol class="fn-list">%s</ol></section>' % (ref, "".join(rows)))
            cited = {ref} | {v[3] for v in notes.values() if v[3]}
            missing = sorted(r for r in cited if clone_for(r) is None)
            state = ("unchecked at " + ", ".join(sorted(cited)) if len(missing) == len(cited)
                     else "checked at " + ", ".join(sorted(cited - set(missing)))
                     + (", UNCHECKED at " + ", ".join(missing) if missing else ""))
            print("  %-18s %2d footnotes, %2d quoted, %s"
                  % (slug, len(notes), quoted, state))

        active = " is-active" if idx == 0 else ""
        tabs.append(
            '<button class="tab%s" role="tab" aria-selected="%s" aria-controls="panel-%s" '
            'id="tab-%s" data-target="%s"><span class="tab-n">%d</span>'
            '<span class="tab-t">%s</span></button>'
            % (active, "true" if not idx else "false", slug, slug, slug, idx + 1,
               html.escape(title)))
        panels.append(
            '<section class="panel%s" id="panel-%s" role="tabpanel" aria-labelledby="tab-%s">'
            '<p class="blurb">%s%s</p><div class="prose">%s</div>%s</section>'
            % (active, slug, slug, html.escape(blurb),
               ('<span class="cont">%s</span>' % html.escape(cont)) if cont else "",
               content, fn_html))

    install = "".join('<div class="ins-row"><span class="ins-os">%s</span>'
                      '<span class="ins-box"><input readonly value="%s" '
                      'aria-label="%s install command" spellcheck="false">'
                      '<button class="ins-copy" type="button" title="Copy">Copy</button>'
                      '</span></div>'
                      % (os_, html.escape(cmd, quote=True), os_) for os_, cmd in INSTALL)
    # The tab icon is the same glyph the header carries, inlined as a data URI:
    # nothing to fetch, and the CSP has no image host to allow.
    favicon = "data:image/svg+xml," + urllib.parse.quote(
        figures.PLANTS["ionantha"].replace('stroke="currentColor"', 'stroke="#5fd6a4"'), safe="")
    doc = (TEMPLATE.replace("__INSTALL__", install)
           .replace("__LEAF__", figures.PLANTS["ionantha"])
           .replace("__FAVICON__", favicon)
           .replace("__DEFS__", figures.DEFS)
           .replace("__HOME__", home_view())
           .replace("__PROGRESS__", progress_view())
           .replace("__TABS__", "\n".join(tabs))
           .replace("__PANELS__", "\n".join(panels))
           .replace("__SITE_REF__", SITE_REF))
    if broken_links:
        print("\n  %d BROKEN footnote target(s):" % len(broken_links))
        for lvl, tgt, why in broken_links:
            print("    %-18s %-52s %s" % (lvl, tgt, why))
    if unchecked:
        print("\n  %d level/release pair(s) UNCHECKED — no checkout for the "
              "release the footnote names:" % len(unchecked))
        for lvl, ref in sorted(unchecked):
            print("    %-18s %s" % (lvl, ref))
    elif not broken_links and (CLONES or CLONE_UNTAGGED):
        print("  every footnote target resolves, at every release cited")

    # A page that failed its own check is not written: an earlier version of
    # this script overwrote the deploy artifact and then reported the failure.
    if broken_links:
        print("not written: %s" % OUT)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print("wrote %s (%d bytes)" % (OUT, len(doc.encode("utf-8"))))
    return 0


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="__FAVICON__">
<title>Tillandsias — an ephemeral cloud region, folded through your hypervisor</title>
<meta name="description" content="What Tillandsias is and how it works, explained at five levels — with its strengths and its unfinished edges both marked, and every claim linked to source.">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css"
      integrity="sha512-fHwaWebuwA7NSF5Qg/af4UeDx9XqUpYpOGgubo3yWu+b2IQR4UeQwbb42Ti7gVAjNtVoI/I9TEoYeu9omwcC6g=="
      crossorigin="anonymous" referrerpolicy="no-referrer">
<style>
:root{
  --bg:#07090c; --bg-2:#0c1015; --panel:#0f141b; --line:#1c2531; --line-2:#243044;
  --ink:#dfe7ef; --ink-dim:#93a1b1; --ink-faint:#616e7d;
  --leaf:#5fd6a4; --leaf-dim:#2e7f61; --violet:#a48bf0; --amber:#e6b45e; --rose:#f0798a;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Inter,Roboto,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.68 var(--sans);
  -webkit-font-smoothing:antialiased;
  background-image:radial-gradient(60rem 40rem at 12% -12%, rgba(95,214,164,.07), transparent 60%),
    radial-gradient(52rem 36rem at 94% 2%, rgba(164,139,240,.06), transparent 62%);
  background-attachment:fixed}
.wrap{max-width:980px;margin:0 auto;padding:0 24px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
header.hero{padding:76px 0 34px;border-bottom:1px solid var(--line)}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.22em;text-transform:uppercase;
  color:var(--leaf);margin:0 0 20px}
.eyebrow .ver{color:var(--ink-faint);letter-spacing:.12em;text-transform:none;font-weight:500}
h1{margin:0;font-size:clamp(32px,5vw,56px);line-height:1.07;letter-spacing:-.026em;font-weight:650}
h1 .dim{color:var(--ink-faint);font-weight:400}
.lede{max-width:64ch;margin:22px 0 0;font-size:19px;color:var(--ink-dim)}
.lede strong{color:var(--ink);font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin:26px 0 0;padding:12px 16px;
  border:1px solid var(--line);border-radius:11px;background:var(--bg-2);
  font-size:12.5px;line-height:1.5;color:var(--ink-faint)}
.legend b{color:var(--ink-dim);font-weight:600}
.legend .lg{display:inline-block;width:1.1em;font:600 11px/1 var(--mono);font-style:normal;text-align:center}
.lg-green,.lg-proven{color:var(--leaf)} .lg-red,.lg-refuted{color:var(--rose)}
.lg-path,.lg-plausible{color:var(--amber)}
.install-strip{padding:18px 0 4px}
.install{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;align-items:center}
.ins-row{display:contents}
.ins-os{font:600 11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-faint);white-space:nowrap}
.ins-box{display:flex;align-items:stretch;min-width:0;border:1px solid var(--line);
  border-radius:7px;background:#0b1016;overflow:hidden}
.ins-box:focus-within{border-color:var(--leaf-dim)}
.ins-box input{flex:1 1 auto;min-width:0;border:0;background:transparent;color:var(--amber);
  font:500 12.5px/1 var(--mono);padding:8px 10px;text-overflow:ellipsis}
.ins-box input:focus{outline:none;color:#f2d9a4}
.ins-copy{flex:0 0 auto;border:0;border-left:1px solid var(--line);background:transparent;
  color:var(--ink-faint);font:600 10.5px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;
  padding:0 12px;cursor:pointer;transition:.15s}
.ins-copy:hover{background:rgba(255,255,255,.04);color:var(--ink)}
.ins-copy.done{color:var(--leaf)}
.tabs{display:flex;gap:6px;overflow-x:auto;padding:10px 0 0;margin:0 0 -1px;
  /* The rail still scrolls on narrow screens; only the bar itself is hidden. */
  scrollbar-width:none;-ms-overflow-style:none}
.tabs::-webkit-scrollbar{display:none}
.tab{appearance:none;cursor:pointer;flex:0 0 auto;display:flex;align-items:center;gap:9px;
  background:transparent;border:1px solid transparent;border-bottom:none;color:var(--ink-faint);
  font:500 13.5px/1 var(--sans);padding:12px 15px;border-radius:9px 9px 0 0;transition:.15s}
.tab:hover{color:var(--ink);background:rgba(255,255,255,.03)}
.tab.is-active{color:var(--ink);background:var(--panel);border-color:var(--line)}
.tab-n{font:600 11px/1 var(--mono);color:var(--leaf-dim);border:1px solid var(--line);
  border-radius:5px;padding:4px 6px}
.tab.is-active .tab-n{color:var(--bg);background:var(--leaf);border-color:var(--leaf)}
/* Only the level rail is sticky; the install commands scroll away with the header. */
.sticky{position:sticky;top:0;z-index:10;background:rgba(7,9,12,.88);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
main{padding:0 0 96px}
.panel{display:none;animation:fade .28s ease both}
.panel.is-active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.blurb{margin:34px 0 8px;font:400 15px/1.6 var(--sans);color:var(--ink-faint);
  border-left:2px solid var(--leaf-dim);padding-left:14px;max-width:70ch}
.blurb .cont{display:block;margin-top:6px;font:500 12px var(--mono);color:var(--leaf-dim);
  letter-spacing:.03em}
.prose{padding-top:14px}
.prose h2.panel-h{margin:14px 0 18px;font-size:clamp(24px,3.2vw,32px);line-height:1.15;
  letter-spacing:-.024em;font-weight:650;max-width:30ch}
.prose h3{margin:44px 0 14px;font-size:23px;letter-spacing:-.02em;font-weight:640;
  padding-top:18px;border-top:1px solid var(--line)}
.prose h3:first-child,.prose h2.panel-h+h3,.prose .plantnote+h3{border-top:none;margin-top:16px;padding-top:0}
/* The plant aside: one true sentence about the genus the project is named
   after. Quiet on purpose — it sits beside the argument, never inside it. */
.plantnote{display:flex;gap:9px;align-items:flex-start;max-width:64ch;
  margin:-2px 0 30px;font:italic 400 13.5px/1.6 var(--sans);color:var(--ink-faint)}
.plant-ico{flex:0 0 auto;color:var(--leaf-dim);padding-top:2px}
.plant-ico svg{display:block;width:15px;height:15px}
.eyebrow .leaf-ico{color:var(--leaf);vertical-align:-2px;margin-right:7px}
.eyebrow .leaf-ico svg{display:inline-block;width:13px;height:13px}
.prose h4{margin:30px 0 10px;font-size:16.5px;font-weight:640;color:var(--ink)}
.prose p{margin:0 0 16px;color:#c9d4e0;max-width:74ch}
.prose ul,.prose ol{margin:0 0 20px;padding-left:0;list-style:none;max-width:74ch}
.prose li{position:relative;padding-left:20px;margin:0 0 10px;color:#c9d4e0}
.prose ul>li::before{content:"";position:absolute;left:4px;top:.72em;width:5px;height:5px;
  border-radius:50%;background:var(--leaf-dim)}
.prose ol{counter-reset:n}
.prose ol>li{counter-increment:n;padding-left:34px}
.prose ol>li::before{content:counter(n,decimal-leading-zero);position:absolute;left:0;top:0;
  font:600 11px/1.75 var(--mono);color:var(--leaf-dim);letter-spacing:.06em}
code{font:500 .875em/1.4 var(--mono);background:#161d26;border:1px solid #212b38;border-radius:5px;
  padding:.12em .38em;color:var(--amber);word-break:break-word}
strong{color:#eef3f8;font-weight:640}
em{color:#dbe4ee}
/* Callouts are deliberately quiet: a hairline, a glyph, a small label. The
   prose is the content; the flags annotate it. */
.callout{display:flex;gap:10px;align-items:flex-start;margin:0 0 10px;padding:4px 0 4px 12px;
  border-left:2px solid var(--line-2);max-width:74ch;font-size:14.5px;line-height:1.58}
.callout div{color:var(--ink-dim)}
.callout p{margin:0 0 8px;color:inherit}
.callout p:last-child{margin-bottom:0}
.callout-icon{flex:0 0 auto;width:1.1em;text-align:center;font:600 11px/1.9 var(--mono);color:var(--ink-faint)}
.callout-k{font:600 10px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-faint);margin-right:4px;white-space:nowrap}
.flag-green{border-left-color:var(--leaf-dim)} .flag-green .callout-icon,.flag-green .callout-k{color:var(--leaf)}
.flag-red{border-left-color:var(--rose)} .flag-red .callout-icon,.flag-red .callout-k{color:var(--rose)}
.flag-path{border-left-color:transparent;margin:-8px 0 12px 14px;padding-left:12px;font-size:13.5px}
.flag-path .callout-icon,.flag-path .callout-k{color:var(--amber)}
.flag-note{border-left-color:var(--line-2)}
.flag-proven{border-left-color:var(--leaf-dim)} .flag-proven .callout-icon,.flag-proven .callout-k{color:var(--leaf)}
.flag-plausible{border-left-color:var(--amber)} .flag-plausible .callout-icon,.flag-plausible .callout-k{color:var(--amber)}
.flag-refuted{border-left-color:var(--rose)} .flag-refuted .callout-icon,.flag-refuted .callout-k{color:var(--rose)}
.fig{margin:26px 0 28px;padding:18px 18px 12px;border:1px solid var(--line);border-radius:12px;
  background:linear-gradient(180deg,#0d1219,#0a0e14);color:var(--ink-dim)}
.fig svg{display:block;width:100%;height:auto;overflow:visible}
.fig figcaption{margin-top:12px;font-size:13.5px;line-height:1.55;color:var(--ink-faint);
  border-top:1px solid var(--line);padding-top:10px;max-width:70ch}
.s-line{fill:none;stroke:var(--line-2);stroke-width:1.2}
.s-fill1{fill:rgba(255,255,255,.016)}
.s-fill2{fill:rgba(95,214,164,.045);stroke:var(--leaf-dim)}
.s-box rect{fill:#131a23;stroke:var(--line-2);stroke-width:1.2}
.s-gate{fill:rgba(230,180,94,.08);stroke:var(--amber)}
.s-txt{fill:var(--ink);font:500 13px var(--sans);text-anchor:middle}
.s-txt.s-sm,.s-sm text{font-size:11.5px}
.s-lbl{fill:var(--ink-faint);font:500 11.5px var(--mono);letter-spacing:.02em}
.s-accent{fill:var(--leaf)}
.s-amber{fill:var(--amber)}
.s-red{fill:var(--rose)}
.s-axis{stroke:var(--line-2);stroke-width:1.2}
.s-arrow{stroke:var(--ink-faint);stroke-width:1.3;color:var(--ink-faint)}
.s-step{stroke:var(--leaf);stroke-width:2;stroke-linejoin:round}
.s-dot circle{fill:var(--leaf)}
.s-dot2 circle{fill:var(--leaf-dim)}
.s-floor{stroke:var(--amber);stroke-width:1.4;stroke-dasharray:5 5}
.s-target{stroke:var(--amber);stroke-width:1.2;stroke-dasharray:4 4}
.s-miss{fill:none;stroke:var(--rose);stroke-width:2}
.s-miss-g circle{fill:none;stroke:var(--rose);stroke-width:1.8}
.s-skew{stroke:var(--rose);stroke-width:1.4;stroke-dasharray:3 3}
.s-mean{stroke:var(--leaf);stroke-width:2}
.s-forbid{stroke:var(--rose);stroke-width:1.4;stroke-dasharray:4 4}
.s-boundary{stroke:var(--leaf);stroke-width:2;stroke-dasharray:6 4}
.math-block{margin:22px 0;padding:16px 18px;border:1px solid var(--line);border-radius:10px;
  background:var(--bg-2);overflow-x:auto}
.math,.math-block{color:#e6eef7}
.katex{font-size:1.04em}
.fnref{font:600 10.5px var(--mono);vertical-align:super;line-height:0}
.fnref a{color:var(--leaf);text-decoration:none;padding:0 1px;position:relative;cursor:pointer}
.fnref a:hover{text-decoration:underline}
#tip{position:fixed;z-index:60;max-width:min(32rem,calc(100vw - 24px));padding:9px 12px;
  border:1px solid var(--line-2);border-radius:8px;background:#141b24;color:var(--ink-dim);
  font:400 13px/1.5 var(--sans);box-shadow:0 10px 30px rgba(0,0,0,.5);pointer-events:none;
  opacity:0;transform:translateY(3px);transition:opacity .12s,transform .12s}
#tip.on{opacity:1;transform:none}
#tip b{color:var(--ink);font-weight:600}
#tip q{display:block;margin:6px 0 0;padding:2px 0 2px 10px;border-left:2px solid var(--leaf-dim);
  color:#cdd8e4;font-style:normal;quotes:none}
#tip q::before,#tip q::after{content:none}
#tip span{display:block;margin-top:6px;font:500 11.5px var(--mono);color:var(--ink-faint);
  word-break:break-all}
.footnotes{margin:56px 0 0;padding:26px 0 0;border-top:1px solid var(--line)}
.footnotes h3{margin:0 0 6px;font:600 12px/1 var(--mono);letter-spacing:.2em;
  text-transform:uppercase;color:var(--ink-dim)}
.fn-note{margin:0 0 18px;font-size:13.5px;color:var(--ink-faint);max-width:74ch}
.fn-list{list-style:none;margin:0;padding:0;counter-reset:none}
.fn-list li{display:flex;gap:12px;margin:0 0 9px;font-size:14px;line-height:1.55}
.fn-back{flex:0 0 22px;text-align:right;font:600 11px var(--mono);color:var(--leaf-dim);
  text-decoration:none;padding-top:3px}
.fn-back:hover{color:var(--leaf)}
.fn-body{color:var(--ink-dim)}
.fn-link{display:inline;color:var(--ink-faint);font:500 12.5px var(--mono);
  text-decoration:none;border-bottom:1px dotted var(--line-2);word-break:break-all}
.fn-link:hover{color:var(--leaf);border-bottom-color:var(--leaf-dim)}
.fn-tag{margin-left:6px;font:600 10px/1 var(--mono);letter-spacing:.06em;color:var(--amber);
  border:1px solid rgba(230,180,94,.35);border-radius:4px;padding:2px 5px;vertical-align:1px}
.fn-quote{display:block;margin:4px 0 2px;padding-left:10px;border-left:2px solid var(--line-2);
  font-size:13px;color:var(--ink-faint);font-style:normal;quotes:none}
.fn-quote::before,.fn-quote::after{content:none}
.ext{padding-left:3px;opacity:.7}
footer{border-top:1px solid var(--line);padding:34px 0 60px;color:var(--ink-faint);font-size:14px}
footer a{color:var(--ink-dim)}
footer a:hover{color:var(--leaf)}
/* --- the menu, and the three views it switches between --- */
.view{display:none}
.view.is-active{display:block}
.burger{position:fixed;top:14px;left:14px;z-index:40;width:38px;height:34px;display:flex;
  flex-direction:column;justify-content:center;gap:4px;padding:0 8px;cursor:pointer;
  background:rgba(12,16,21,.82);backdrop-filter:blur(8px);border:1px solid var(--line);
  border-radius:9px}
.burger span{display:block;height:1.5px;background:var(--ink-dim);border-radius:2px;transition:.18s}
.burger:hover span{background:var(--leaf)}
.burger[aria-expanded="true"] span:nth-child(1){transform:translateY(5.5px) rotate(45deg)}
.burger[aria-expanded="true"] span:nth-child(2){opacity:0}
.burger[aria-expanded="true"] span:nth-child(3){transform:translateY(-5.5px) rotate(-45deg)}
.drawer{position:fixed;top:0;left:0;bottom:0;z-index:39;width:250px;padding:66px 14px 20px;
  background:var(--bg-2);border-right:1px solid var(--line);
  transform:translateX(-100%);transition:transform .2s ease;display:flex;flex-direction:column;gap:2px}
.drawer.is-open{transform:none}
.drawer-h{margin:0 8px 14px;font:600 11px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;
  color:var(--leaf)}
.drawer-f{margin:auto 8px 0;font-size:12px;color:var(--ink-faint)}
.nav{display:flex;align-items:center;gap:10px;width:100%;text-align:left;cursor:pointer;
  background:transparent;border:1px solid transparent;border-radius:8px;color:var(--ink-dim);
  font:500 14.5px/1 var(--sans);padding:11px 10px;transition:.15s}
.nav:hover{color:var(--ink);background:rgba(255,255,255,.04)}
.nav.is-on{color:var(--ink);background:var(--panel);border-color:var(--line)}
.nav-i{width:1.2em;text-align:center;color:var(--leaf-dim);font-size:13px}
.nav.is-on .nav-i{color:var(--leaf)}
.scrim{position:fixed;inset:0;z-index:38;background:rgba(4,6,9,.55)}
/* --- home --- */
.homecard{max-width:760px;margin:0 auto;padding:96px 24px 80px;text-align:center}
.homeart{position:relative;display:flex;align-items:center;justify-content:center;
  height:clamp(180px,30vh,300px);margin:0 0 34px;border:1px solid var(--line);border-radius:14px;
  background:linear-gradient(180deg,#0c1119,#080b10);color:var(--leaf-dim)}
.homeart svg{width:74px;height:74px;opacity:.5}
.homeart-note{position:absolute;bottom:12px;right:14px;font:500 10.5px/1 var(--mono);
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint)}
.wordmark{margin:0;font-size:clamp(46px,10vw,96px);line-height:1;letter-spacing:-.04em;font-weight:660}
.byline{margin:12px 0 0;font:400 17px/1 var(--sans);color:var(--ink-dim)}
.fact{max-width:52ch;margin:34px auto 0;font:italic 400 15.5px/1.65 var(--sans);color:var(--ink-faint)}
.factpool{display:none}
.homelead{max-width:52ch;margin:26px auto 0;font-size:15px;color:var(--ink-dim)}
.homego{margin:32px 0 0;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.gobtn{cursor:pointer;background:transparent;border:1px solid var(--line-2);border-radius:9px;
  color:var(--ink-dim);font:500 14px/1 var(--sans);padding:11px 18px;transition:.15s}
.gobtn:hover{color:var(--ink);border-color:var(--leaf-dim);background:rgba(95,214,164,.05)}
/* --- live progress --- */
.view-h{margin:76px 0 10px;font-size:clamp(28px,4vw,40px);letter-spacing:-.026em;font-weight:650}
.view-lede{max-width:74ch;margin:0 0 22px;color:var(--ink-dim);font-size:15.5px}
.bar{display:flex;height:7px;border-radius:4px;overflow:hidden;background:#141b24;margin:0 0 10px}
.bar-g{background:var(--leaf)} .bar-y{background:var(--amber)}
.tally{margin:0 0 30px;font-size:13.5px;color:var(--ink-faint)}
.tally b{color:var(--ink-dim);font-weight:640}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;align-items:start}
.col{border:1px solid var(--line);border-radius:12px;background:var(--bg-2);padding:16px 14px}
.col h3{margin:0 0 4px;font-size:14.5px;font-weight:640;display:flex;align-items:center;gap:8px}
.col h3 .n{font:600 11px/1 var(--mono);color:var(--bg);border-radius:20px;padding:4px 8px}
.col-red h3{color:var(--rose)} .col-red h3 .n{background:var(--rose)}
.col-yellow h3{color:var(--amber)} .col-yellow h3 .n{background:var(--amber)}
.col-green h3{color:var(--leaf)} .col-green h3 .n{background:var(--leaf)}
.col-b{margin:0 0 14px;font-size:12.5px;line-height:1.5;color:var(--ink-faint)}
.cards{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
.card{border:1px solid var(--line);border-left:2px solid var(--line-2);border-radius:9px;
  background:var(--panel);padding:10px 11px}
.card.sev-high{border-left-color:var(--rose)}
.card.sev-medium{border-left-color:var(--amber)}
.card.sev-low{border-left-color:var(--line-2)}
.card.empty{color:var(--ink-faint);font-size:13px;border-left-color:transparent;text-align:center}
.card-h{display:flex;align-items:center;gap:8px;margin:0 0 5px;font:500 10.5px/1 var(--mono)}
.card-h code{background:none;border:0;padding:0;color:var(--leaf-dim)}
.card-h .repo{color:var(--ink-faint)}
.card-h .sev{margin-left:auto;color:var(--ink-faint);text-transform:uppercase;letter-spacing:.1em}
.card-t{margin:0 0 5px;font-size:13.5px;line-height:1.45;color:#c9d4e0}
.card-m{margin:0;font:400 11.5px/1.45 var(--mono);color:var(--ink-faint);word-break:break-word}
.card-d{margin:6px 0 0;font-size:11.5px;color:var(--ink-faint)}
.dep{display:inline-block;font:500 10.5px var(--mono);color:var(--amber);
  border:1px solid rgba(230,180,94,.3);border-radius:4px;padding:1px 5px;margin-right:4px}
.card-u{margin:6px 0 0}
.up{font:500 11px var(--mono);color:var(--leaf);text-decoration:none}
.up.unfiled{color:var(--ink-faint)}
.cc{margin:40px 0 0;padding:20px 20px 8px;border:1px solid var(--line);border-radius:12px;
  background:var(--bg-2)}
.cc h3{margin:0 0 10px;font-size:16px;font-weight:640}
.cc p{margin:0 0 14px;max-width:78ch;font-size:14px;line-height:1.6;color:var(--ink-dim)}
.cc-open{font:500 12px var(--mono);color:var(--ink-faint)}
@media (max-width:900px){.cols{grid-template-columns:1fr}}
@media (max-width:760px){
  header.hero{padding:48px 0 24px}
  .tab-t{display:none}
  .tab{padding:12px}
  .install{grid-template-columns:1fr;gap:3px}
  .install-strip{padding:12px 0 2px}
  .ins-row{display:block}
  .ins-os{display:block;margin:7px 0 3px}
  .flag-path{margin-left:8px}
}
</style>
</head>
<body>
__DEFS__

<button class="burger" id="burger" aria-label="Open the menu" aria-expanded="false"
        aria-controls="drawer"><span></span><span></span><span></span></button>
<nav class="drawer" id="drawer" aria-label="Site">
  <p class="drawer-h">tillandsias.org</p>
  <button class="nav" id="nav-home" data-go="view-home"><span class="nav-i">&#127968;</span>Home</button>
  <button class="nav is-on" id="nav-what" data-go="view-what"><span class="nav-i">&#63;</span>What is it?</button>
  <button class="nav" id="nav-progress" data-go="view-progress"><span class="nav-i">&#9673;</span>Live progress</button>
  <p class="drawer-f">Checked against release <code>__SITE_REF__</code>.</p>
</nav>
<div class="scrim" id="scrim" hidden></div>

__HOME__

<section class="view is-active" id="view-what" role="tabpanel" aria-labelledby="nav-what">
<header class="hero">
  <div class="wrap">
    <p class="eyebrow"><span class="leaf-ico" aria-hidden="true">__LEAF__</span>tillandsias.org <span class="ver" title="The release of the source repository this page was last checked against">&middot; __SITE_REF__</span></p>
    <h1>An idempotent, ephemeral cloud region,<br><span class="dim">folded through your hypervisor.</span></h1>
    <p class="lede">Local hardware. Free software. Nothing rented, nothing metered, nothing left
      behind. Below is <strong>what it is and how it works</strong>, told five times over — pick
      the version that fits the person reading.</p>
    <div class="legend">
      <span><i class="lg lg-green">&#x25CF;</i> <b>Verified</b> — checked against the source, and working.</span>
      <span><i class="lg lg-red">&#x25CF;</i> <b>Shortcoming</b> — incomplete, pending, or overclaimed.</span>
      <span><i class="lg lg-path">&#8594;</i> <b>Path</b> — what the plan records as the fix, or that it records none.</span>
      <span><i class="lg lg-proven">&#x2713;</i> <b>Shown</b> — an argument we can point at the code or a test for.</span>
      <span><i class="lg lg-plausible">&#x223C;</i> <b>Plausible</b> — sounds right; not yet demonstrated.</span>
      <span><i class="lg lg-refuted">&#x2717;</i> <b>Does not hold</b> — an argument we tried, and it failed.</span>
    </div>
  </div>
</header>

<div class="install-strip">
  <div class="wrap">
    <div class="install" aria-label="Install">
__INSTALL__
    </div>
  </div>
</div>

<div class="sticky">
  <div class="wrap">
    <div class="tabs" role="tablist" aria-label="Explanation level">
__TABS__
    </div>
  </div>
</div>

<main>
  <div class="wrap">
__PANELS__
  </div>
</main>
</section>

__PROGRESS__

<footer>
  <div class="wrap">
    <p>Source: <a href="https://github.com/8007342/tillandsias/">github.com/8007342/tillandsias</a>.
    Each level's footnotes link into the release named at the foot of that level, so the
    line numbers stay true even as the project moves on. Last checked against
    <code>__SITE_REF__</code>.</p>
  </div>
</footer>

<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"
  integrity="sha512-LQNxIMR5rXv7o+b1l8+N1EZMfhG7iFZ9HhnbJkTp4zjNr5Wvst75AqUeFDxeRUa7l5vEDyUiAip//r+EFLLCyA=="
  crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"
  integrity="sha512-iWiuBS5nt6r60fCz26Nd0Zqe0nbk1ZTIQbl3Kv7kYsX+yKMUFHzjaH2+AnM6vp2Xs+gNmaBAVWJjSmuPw76Efg=="
  crossorigin="anonymous" referrerpolicy="no-referrer"
  onload="renderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false});"></script>
<script>
// Copy-to-clipboard for the install commands, with a selection fallback for
// browsers that refuse the async clipboard outside a secure context.
(function(){
  document.querySelectorAll('.ins-box').forEach(function(box){
    var input = box.querySelector('input'), btn = box.querySelector('.ins-copy');
    input.addEventListener('focus', function(){ input.select(); });
    input.addEventListener('click', function(){ input.select(); });
    btn.addEventListener('click', function(){
      input.select();
      var done = function(){
        btn.textContent = 'Copied';
        btn.classList.add('done');
        setTimeout(function(){ btn.textContent = 'Copy'; btn.classList.remove('done'); }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(input.value).then(done, function(){
          try { document.execCommand('copy'); done(); } catch (e) {}
        });
      } else {
        try { document.execCommand('copy'); done(); } catch (e) {}
      }
    });
  });
})();
// Footnote tooltips: label, the quoted lines when recorded, and the target.
// Shown on hover and on keyboard focus, positioned inside the viewport so a
// citation near the right edge is not clipped. The click itself opens the
// source in a new tab; the list at the foot of the level stays for completeness.
(function(){
  var tip = document.createElement('div');
  tip.id = 'tip'; tip.setAttribute('role', 'tooltip');
  document.body.appendChild(tip);
  var hideTimer;
  function show(a){
    var label = a.getAttribute('data-label'); if (!label) return;
    clearTimeout(hideTimer);
    tip.innerHTML = '';
    var b = document.createElement('b'); b.textContent = label; tip.appendChild(b);
    var quote = a.getAttribute('data-quote');
    if (quote) { var q = document.createElement('q'); q.textContent = quote; tip.appendChild(q); }
    var target = a.getAttribute('data-target');
    if (target) { var s = document.createElement('span'); s.textContent = target + ' \\u2197'; tip.appendChild(s); }
    tip.classList.add('on');
    var r = a.getBoundingClientRect(), t = tip.getBoundingClientRect();
    var left = Math.min(Math.max(8, r.left + r.width / 2 - t.width / 2), window.innerWidth - t.width - 8);
    var top = r.top - t.height - 8;
    if (top < 8) top = r.bottom + 8;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  }
  function hide(){ hideTimer = setTimeout(function(){ tip.classList.remove('on'); }, 80); }
  document.addEventListener('mouseover', function(e){
    var a = e.target.closest('.fnref a[data-label]'); if (a) show(a);
  });
  document.addEventListener('mouseout', function(e){
    if (e.target.closest('.fnref a[data-label]')) hide();
  });
  document.addEventListener('focusin', function(e){
    var a = e.target.closest('.fnref a[data-label]'); if (a) show(a);
  });
  document.addEventListener('focusout', hide);
  window.addEventListener('scroll', function(){ tip.classList.remove('on'); }, {passive:true});
})();
// The menu, the three views, and one fact chosen per visit.
(function(){
  var burger = document.getElementById('burger'),
      drawer = document.getElementById('drawer'),
      scrim  = document.getElementById('scrim');
  function setMenu(open){
    drawer.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    scrim.hidden = !open;
  }
  burger.addEventListener('click', function(){
    setMenu(!drawer.classList.contains('is-open'));
  });
  scrim.addEventListener('click', function(){ setMenu(false); });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') setMenu(false);
  });

  var views = [].slice.call(document.querySelectorAll('.view')),
      navs  = [].slice.call(document.querySelectorAll('.nav'));
  function go(id, push){
    if (!document.getElementById(id)) return;
    views.forEach(function(v){ v.classList.toggle('is-active', v.id === id); });
    navs.forEach(function(n){ n.classList.toggle('is-on', n.dataset.go === id); });
    setMenu(false);
    if (push) history.replaceState(null, '', id === 'view-what' ? location.pathname : '#' + id.slice(5));
    window.scrollTo(0, 0);
  }
  [].slice.call(document.querySelectorAll('[data-go]')).forEach(function(b){
    b.addEventListener('click', function(){ go(b.dataset.go, true); });
  });

  // One fact per visit, drawn in the browser so the page is a little different
  // each time. The pool ships in the markup, so this works with no request.
  var pool = document.getElementById('factpool'), out = document.getElementById('fact');
  if (pool && out) {
    var lines = pool.querySelectorAll('li');
    if (lines.length) out.textContent = lines[Math.floor(Math.random() * lines.length)].textContent;
  }

  // A deep link opens its view: #home, #progress, or a level such as #level-3-power.
  function fromHash(){
    var h = location.hash.slice(1);
    if (!h) return;
    if (h === 'home' || h === 'progress') return go('view-' + h, false);
    if (document.getElementById('panel-' + h)) go('view-what', false);
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
(function(){
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  function show(slug){
    tabs.forEach(function(t){
      var on = t.dataset.target === slug;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    document.querySelectorAll('.panel').forEach(function(p){
      p.classList.toggle('is-active', p.id === 'panel-' + slug);
    });
    history.replaceState(null, '', '#' + slug);
  }
  tabs.forEach(function(t){ t.addEventListener('click', function(){ show(t.dataset.target); }); });
  document.addEventListener('keydown', function(e){
    var onWhat = document.getElementById('view-what').classList.contains('is-active');
    if (onWhat && e.key >= '1' && e.key <= '5' && !/^(INPUT|TEXTAREA)$/.test(e.target.tagName)) {
      var t = tabs[+e.key - 1]; if (t) show(t.dataset.target);
    }
  });
  // A back-link from the footnote list must switch to that level before jumping.
  window.addEventListener('hashchange', function(){
    var m = /^#(?:[rf])(level-[a-z0-9-]+)-\\d+$/.exec(location.hash);
    if (m) show(m[1]);
  });
  var h = location.hash.slice(1);
  if (h && document.getElementById('panel-' + h)) show(h);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(build())
