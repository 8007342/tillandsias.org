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
import slides  # noqa: E402

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
     "v56.9.21.1",
     ("ionantha",
      "A real tillandsia needs no soil and no pot — it drinks from the air, and borrows nothing.")),
    ("level-2-phone",    "I barely understand my phone",
     "Straight answers to what you are actually wondering: privacy, cost, and what breaks.",
     "Picks up where “like I’m 5” left off.",
     "v56.9.21.1",
     ("bulbosa",
      "A tillandsia is an epiphyte, not a parasite: it rests on its tree and takes nothing from it.")),
    ("level-3-power",    "I'm a power user",
     "The anatomy: what runs where, what survives a teardown, and where the sharp edges are.",
     "Assumes the two levels before it.",
     "v56.9.21.1",
     ("xerographica",
      "Its roots only grip; the leaves do the drinking — a plant that runs rootless.")),
    ("level-4-security", "I'm a Cyber Security expert",
     "The architecture interrogated rather than described — boundaries, egress, provenance, "
     "and what the tests do not actually test.",
     "Assumes the three levels before it.",
     "v56.9.21.1",
     ("usneoides",
      "Silvery leaf scales open to take water in, then trap air to keep it: every exchange "
      "across one surface.")),
    ("level-5-phd",      "I'm a MathWiz / Hacker",
     "And you would like me to be condescending about it. Very well.",
     "Assumes everything before it. Mathematics from here down.",
     "v56.9.21.1",
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

def build_stamp():
    """The stable app version this generated page describes.

    Tillandsias release tags have a fourth build coordinate. The website uses
    the app's three-part display version, while the full tag remains visible in
    the release reference beside it. The tracked pre-commit rebuild keeps this
    generated value synchronized whenever a pin changes.
    """
    return SITE_REF.removeprefix("v").rsplit(".", 1)[0]


BUILD_STAMP = build_stamp()


# Rolling stable installers. The short URLs are served from this site's own
# var/html as STATIC SHIMS: each one resolves the current installer from
# GitHub's /releases/latest/ at run time and executes that. The shims never
# need rebuilding when the app releases, so the property the long URLs had —
# this site redeploys on commit while the release channel moves on its own —
# is preserved rather than traded away for a shorter line.
#
# The shims also fix two things a bare `curl … | bash` cannot: they refuse a
# download that is not a script (a 404 or captive-portal page piped into a
# shell), and they run the installer from a file so it keeps a usable stdin.
DL = "https://github.com/8007342/tillandsias/releases/latest/download"
SITE = "https://tillandsias.org"
INSTALL = [
    ("Linux",   "curl -fSsL %s/install.sh | bash" % SITE),
    ("macOS",   "curl -fSsL %s/install-macos.sh | bash" % SITE),
    ("Windows", "irm %s/install.ps1 | iex" % SITE),
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
        self.ref_counts = {}
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
        ctx.ref_counts[n] = ctx.ref_counts.get(n, 0) + 1
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
        suffix = '' if ctx.ref_counts[n] == 1 else '-%d' % ctx.ref_counts[n]
        return '<sup class="fnref" id="r%s-%s%s"><a%s>%s</a></sup>' % (ctx.level, n, suffix, attrs, n)

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
            '<p class="homelead">A small cloud region on your own computer. Disposable workspaces, '
            'with work preserved through your git remote.</p>'
            '<p class="homego"><button class="gobtn" data-go="view-what">What is it?</button>'
            '<button class="gobtn" data-go="view-progress">Live progress</button>'
            '<button class="gobtn" data-go="view-slides">Slides</button></p>'
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
            '<p class="view-lede">Findings recorded by this website, as of this build. These columns '
            'show our audit record, not live telemetry or an inventory of every app defect. '
            'A finding advances when evidence supports it; a correction records why an earlier '
            'claim was wrong. Earlier events remain in the history.</p>'
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
    """Distinguish the website's measured counts from the runtime's scorer."""
    return ('<section class="cc"><h3>What this progress measures</h3>'
            '<p>The bar counts findings recorded here. A resolved finding means its stated '
            'remedy was checked; it does not mean the entire application is complete or that '
            'every installed copy has been repaired. Adding a newly discovered defect can '
            'lower the completed percentage while improving what we know.</p>'
            '<p>The runtime now delegates scoring to an obligation model, but coverage of '
            'the methodology’s full scoring rules remains partial. '
            '<a href="#level-5-phd">The methodology level explains the implemented model '
            'and its limits, with release-pinned evidence.</a> This website has no CentiColon '
            'scorer or comparable score history of its own, so no convergence curve is shown.</p>'
            '<p>We preserve findings, append evidence and record retractions. Monotonic '
            'improvement means a more accurate, reviewable record; it does not require the '
            'number of green flags to rise at every update.</p>'
            '</section>')


def slides_view():
    """The deck behind the menu, one visible at a time.

    Editorial provenance stays in slides.py; presentation slides stand alone.
    Figures and copy reflow together, then scale to fit the available frame."""

    def blk(kind, payload):
        if kind == "p":
            return ('<p>%s</p>' % html.escape(payload))
        if kind == "ph":
            return ('<div class="s-ph"><span class="s-ph-k">content to come</span>'
                    '<span class="s-ph-t">%s</span></div>' % html.escape(payload))
        if kind == "fig":
            if payload not in figures.FIGURES:
                return '<div class="s-ph"><span class="s-ph-k">content to come</span>' \
                       '<span class="s-ph-t">no figure named %s in the site registry</span></div>' \
                       % html.escape(payload)
            return figures.FIGURES[payload]
        if kind == "pillars":
            cards = "".join(
                '<div class="s-pillar"><h3>%s</h3><p>%s</p></div>'
                % (html.escape(name), html.escape(note)) for name, note in payload)
            return '<div class="s-pillars">%s</div>' % cards
        return ""

    slides_html = []
    for i, s in enumerate(slides.SLIDES, 1):
        artwork = "".join(blk(*b) for b in s["blocks"] if b[0] == "fig")
        copy = "".join(blk(*b) for b in s["blocks"] if b[0] != "fig")
        body = artwork + '<div class="s-copy">%s</div>' % copy
        layout = ' has-art' if artwork else ''
        if s.get("layout") == "finale":
            layout += ' slide-finale'
        if s.get("layout") == "diagram":
            layout += ' slide-diagram'
        if s.get("layout") == "method":
            layout += ' slide-method'
        lede = ('<p class="s-lede">%s</p>' % html.escape(s["lede"])) if s.get("lede") else ""
        slides_html.append(
            '<section class="slide%s%s" data-slide="%d" aria-hidden="%s">'
            '<div class="slide-content">'
            '<p class="s-eyebrow">%s</p>'
            '<h3 class="s-title">%s</h3>'
            '%s'
            '<div class="s-body">%s</div>'
            '</div></section>'
            % (" is-on" if i == 1 else "", layout, i, "false" if i == 1 else "true",
               html.escape(s["eyebrow"]), html.escape(s["title"]),
               lede, body))

    return ('<section class="view" id="view-slides" role="tabpanel" aria-labelledby="nav-slides">'
            '<div class="wrap deck">'
            '<h2 class="deck-h">Tillandsias <span> / Slides</span></h2>'
            '<div class="deck-frame">%s</div>'
            '<div class="deck-nav" role="group" aria-label="Slides">'
            '<button class="s-prev" id="slide-prev" type="button" disabled>&#8592; Prev</button>'
            '<span class="s-count"><b id="s-count-n">1</b> / %d</span>'
            '<button class="s-next" id="slide-next" type="button">Next &#8594;</button>'
            '</div>'
            '<div class="s-rail" role="progressbar" aria-label="Position in the deck" '
            'aria-valuemin="1" aria-valuemax="%d" aria-valuenow="1"><span class="s-rail-fill" '
            'id="s-rail-fill"></span></div>'
            '</div></section>'
            % ("".join(slides_html), len(slides.SLIDES), len(slides.SLIDES)))


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
           .replace("__SLIDES__", slides_view())
           .replace("__TABS__", "\n".join(tabs))
           .replace("__PANELS__", "\n".join(panels))
           .replace("__SITE_REF__", SITE_REF)
           .replace("__BUILD_STAMP__", BUILD_STAMP))
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
  --leaf:#5fd6a4; --leaf-dim:#2e7f61; --sky:#69a9ff; --sky-dim:#274d7d; --violet:#a48bf0; --amber:#e6b45e; --rose:#f0798a;
  /* A cool ramp, leaf-to-violet, one stop per refinement tree in the finale. */
  --rg-0:#5fd6a4; --rg-1:#47d2a8; --rg-2:#3bcbb8; --rg-3:#41bccb; --rg-4:#54a4d9; --rg-5:#6b8ce4; --rg-6:#8b7bea; --rg-7:#a678ea;
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
.eyebrow .updated{color:var(--ink-faint);opacity:.75;font-size:10px;letter-spacing:.08em;text-transform:none;font-weight:400;margin-left:8px}
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
.ins-note{grid-column:1/-1;margin:8px 0 0;max-width:72ch;font-size:13px;
  line-height:1.55;color:var(--ink-faint)}
.ins-note a{color:inherit}
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
/* --- the slides deck --- */
body.is-presenting{overflow:hidden}
body.is-presenting main{padding:0}
body.is-presenting footer{display:none}
.is-presenting .deck{height:100dvh;width:100%;max-width:none;display:flex;flex-direction:column;
  padding:14px clamp(12px,2.5vw,48px) 12px;gap:0}
.is-presenting .deck-h{flex-shrink:0;margin:0 0 14px;padding-left:46px;
  font:600 14px/34px var(--sans);letter-spacing:.02em}
.deck-h span{font-weight:400;color:var(--ink-faint)}
.is-presenting .deck-frame{flex:1;min-height:0;overflow:clip;position:relative}
.is-presenting .deck-nav{flex-shrink:0;margin:10px 0 8px}
.is-presenting .s-rail{flex-shrink:0;margin:0}
.deck-h{margin:76px 0 8px;font-size:clamp(28px,4vw,40px);letter-spacing:-.026em;font-weight:650}
.deck-frame{border:1px solid var(--line);border-radius:14px;overflow:hidden;
  background:linear-gradient(180deg,#0c1119,#080b10)}
.slide{display:none;position:absolute;inset:0;overflow:clip}
.slide.is-on{display:block}
.slide-content{position:absolute;left:50%;top:50%;width:100%;padding:clamp(18px,3vw,48px);
  transform:translate(-50%,-50%) scale(var(--fit,1));transform-origin:center}
.s-eyebrow{margin:0 0 16px;font:600 clamp(10px,1vw,13px)/1.4 var(--mono);letter-spacing:.16em;
  text-transform:uppercase;color:var(--leaf)}
.s-title{margin:0 0 12px;font-size:clamp(24px,3.4vw,56px);line-height:1.12;
  letter-spacing:-.025em;font-weight:650;max-width:40ch;text-wrap:balance}
.s-lede{margin:0;color:var(--ink-dim);font-size:clamp(15px,1.6vw,23px);line-height:1.5}
.s-body{margin-top:clamp(14px,2vw,30px)}
.has-art .s-body{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);
  align-items:center;gap:clamp(20px,3.5vw,56px)}
.slide-finale .s-body{grid-template-columns:minmax(0,1.7fr) minmax(0,1fr)}
.slide-diagram .slide-content{padding:12px 20px}
.slide-diagram .s-title{font-size:clamp(22px,2vw,32px);max-width:none}
.slide-diagram .s-eyebrow{display:none}
.slide-diagram .s-body{display:block;margin-top:12px}
.slide-diagram .s-copy:empty{display:none}
.slide-diagram .s-body .fig{padding:8px 12px;border:0;background:none}
.slide-diagram .s-body .fig figcaption{font-size:11px;line-height:1.4}
.slide-method .s-title{max-width:none}
.slide-method .s-body{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr);align-items:center;gap:clamp(18px,3vw,48px)}
.s-body .fig{margin:0;padding:clamp(10px,1.5vw,22px);min-width:0}
.s-body .fig svg{width:100%;height:auto;max-height:none}
.s-body .fig figcaption{max-width:none;margin-top:10px;padding-top:10px;
  font-size:clamp(10px,1vw,14px);line-height:1.5}
.s-copy{min-width:0}
.s-copy>p{margin:0 0 1em;color:#c9d4e0;font-size:clamp(16px,1.65vw,25px);line-height:1.55}
.s-copy>p:last-child{margin-bottom:0}
.s-ph{display:flex;flex-direction:column;gap:4px;max-width:74ch;margin:0 0 12px;
  padding:14px 16px;border:1px dashed var(--line-2);border-radius:9px;
  background:rgba(255,255,255,.015);color:var(--ink-faint);font-size:14px;line-height:1.55}
.s-ph-k{font:600 10.5px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-faint)}
.s-ph-t{margin-top:4px}
.s-pillars{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:8px 0 4px}
.s-pillar{border:1px solid var(--line);border-radius:10px;background:var(--bg-2);
  padding:14px 14px 12px;display:flex;flex-direction:column;gap:8px}
.s-pillar h3{margin:0;font-size:clamp(17px,1.8vw,28px);line-height:1.3;font-weight:640;color:var(--ink)}
.s-pillar p{margin:0;font-size:clamp(15px,1.45vw,23px);line-height:1.55;color:var(--ink-dim)}
.s-pillar .s-ph{margin:0;flex:1}
.deck-nav{display:flex;align-items:center;justify-content:space-between;gap:14px;
  margin:16px 0 10px}
.s-prev,.s-next{cursor:pointer;background:transparent;border:1px solid var(--line-2);
  border-radius:9px;color:var(--ink-dim);font:500 13.5px/1 var(--sans);
  padding:10px 16px;transition:.15s}
.s-prev:hover:not(:disabled),.s-next:hover:not(:disabled){color:var(--ink);
  border-color:var(--leaf-dim);background:rgba(95,214,164,.05)}
.s-prev:disabled,.s-next:disabled{opacity:.4;cursor:default}
.s-count{font:500 13px var(--mono);color:var(--ink-faint);letter-spacing:.05em}
.s-count b{color:var(--ink)}
.s-rail{height:5px;margin:0 0 40px;border-radius:3px;overflow:hidden;background:
  linear-gradient(to right,var(--leaf-dim) 0 var(--how-start,35.3%),var(--sky-dim) var(--how-start,35.3%) 100%)}
.s-rail-fill{display:block;height:100%;width:5.88%;background:var(--leaf);
  border-radius:2px;transition:width .25s ease}
.s-rail.is-how .s-rail-fill{background:var(--sky)}
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
  .s-pillars{grid-template-columns:1fr}
}
@media (max-aspect-ratio:1/1){
  .has-art .s-body{grid-template-columns:1fr;gap:18px}
  .s-title{font-size:clamp(24px,5vw,46px)}
  .s-copy>p{font-size:clamp(16px,2.4vw,23px)}
  .s-body .fig{max-width:100%}
}
@media (max-height:480px) and (min-aspect-ratio:1/1){
  .is-presenting .deck{padding-top:6px;padding-bottom:6px}
  .is-presenting .deck-h{margin-bottom:6px;line-height:30px}
  .slide-content{padding:16px 24px}
  .s-eyebrow{margin-bottom:8px}
  .s-title{font-size:24px}
  .s-body{margin-top:12px}
  .s-copy>p{font-size:15px;line-height:1.45}
  .s-pillars{grid-template-columns:repeat(3,1fr)}
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
  <button class="nav" id="nav-slides" data-go="view-slides"><span class="nav-i">&#9654;</span>Slides</button>
  <p class="drawer-f">Checked against release <code>__SITE_REF__</code>.</p>
</nav>
<div class="scrim" id="scrim" hidden></div>

__HOME__

<section class="view is-active" id="view-what" role="tabpanel" aria-labelledby="nav-what">
<header class="hero">
  <div class="wrap">
    <p class="eyebrow"><span class="leaf-ico" aria-hidden="true">__LEAF__</span>tillandsias.org <span class="ver" title="The release of the source repository this page was last checked against">&middot; __SITE_REF__</span> <span class="updated">&middot; website last updated __BUILD_STAMP__</span></p>
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
      <p class="ins-note">Each line fetches a short script from this site, which
      resolves the <strong>latest stable release</strong> on GitHub and runs that
      release&#8217;s own installer. Stable moves only when a daily build is
      promoted, so it normally trails the newest code. The scripts here are not
      rebuilt when the app releases; they look the release up every time they
      run. Current installers reset local application state and reprovision by
      default; set <code>TILLANDSIAS_DESTRUCTIVE_RESET_OK=0</code> before running
      one to skip the destructive reset.</p>
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

__SLIDES__

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
    document.body.classList.toggle('is-presenting', id === 'view-slides');
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

  // A deep link opens its view: #home, #progress, #slides, or a level such as #level-3-power.
  function fromHash(){
    var h = location.hash.slice(1);
    if (!h) return;
    if (h === 'home' || h === 'progress' || h === 'slides') return go('view-' + h, false);
    if (document.getElementById('panel-' + h)) go('view-what', false);
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
// The deck: one slide at a time. Moving a slide is a real history step, so the
// back button undoes it; a deep link (#slides-2) opens the view on that slide,
// and a number past either end is clamped and the URL corrected.
(function(){
  var view = document.getElementById('view-slides');
  if (!view) return;
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var count = slides.length;
  var num = document.getElementById('s-count-n'),
      fill = document.getElementById('s-rail-fill'),
      rail = document.querySelector('.s-rail'),
      prev = document.getElementById('slide-prev'),
      next = document.getElementById('slide-next');
  var current = 1;
  var frame = view.querySelector('.deck-frame');
  function fitSlide(){
    if (!view.classList.contains('is-active') || !frame.clientHeight) return;
    var content = slides[current - 1].querySelector('.slide-content');
    if (slides[current - 1].classList.contains('slide-diagram')) {
      // Give a diagram-only slide the remaining height directly. SVG's own
      // viewBox scales its labels and geometry together, without a nested
      // CSS scale (which can mispaint inherited SVG text in Chromium).
      content.style.setProperty('--fit', 1);
      var svg = content.querySelector('svg');
      svg.style.height = '0px';
      svg.style.height = Math.max(0, frame.clientHeight - content.offsetHeight - 4) + 'px';
      return;
    }
    // Reflow at the viewport width first. Scale only if the complete content
    // still exceeds the frame; never truncate copy or introduce a scroll pane.
    var scale = Math.min(1, (frame.clientHeight - 4) / content.offsetHeight,
                         (frame.clientWidth - 4) / content.scrollWidth);
    content.style.setProperty('--fit', scale);
  }
  new ResizeObserver(fitSlide).observe(frame);
  window.addEventListener('resize', fitSlide);
  if (document.fonts) document.fonts.ready.then(fitSlide);
  function set(n, push){
    current = Math.min(Math.max(1, n), count);
    slides.forEach(function(s){
      var on = +s.dataset.slide === current;
      s.classList.toggle('is-on', on);
      s.setAttribute('aria-hidden', on ? 'false' : 'true');
    });
    fitSlide();
    if (num) num.textContent = current;
    if (fill) fill.style.width = (100 * current / count) + '%';
    if (rail) rail.style.setProperty('--how-start', (100 * 6 / count) + '%');
    if (rail) rail.classList.toggle('is-how', current >= 7);
    if (rail) rail.setAttribute('aria-valuenow', current);
    if (prev) prev.disabled = current === 1;
    if (next) next.disabled = current === count;
    var url = current === 1 ? '#slides' : '#slides-' + current;
    history[push ? 'pushState' : 'replaceState'](null, '', url);
  }
  if (prev) prev.addEventListener('click', function(){ set(current - 1, true); });
  if (next) next.addEventListener('click', function(){ set(current + 1, true); });
  document.addEventListener('keydown', function(e){
    if (!view.classList.contains('is-active')) return;
    if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
    if (document.getElementById('drawer').classList.contains('is-open')) return;
    if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); set(current + 1, true); }
    else if (e.key === 'ArrowLeft') { set(current - 1, true); }
    else if (e.key === 'Home') { set(1, true); }
    else if (e.key === 'End') { set(count, true); }
  });
function fromDeckHash(){
    var h = location.hash.slice(1);
    var m = /^slides-(\\d+)$/.exec(h);
    if (m) {
      go('view-slides', false);
      set(parseInt(m[1], 10), false);
      return;
    }
    if (h === 'slides') {
      go('view-slides', false);
      set(1, false);
    }
  }
  window.addEventListener('hashchange', fromDeckHash);
  fromDeckHash();
})();
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
