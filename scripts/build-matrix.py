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
import progress  # noqa: E402
import big_graph  # noqa: E402
import metrics  # noqa: E402

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
     "v56.10.9.1",
     ("ionantha",
      "A real tillandsia needs no soil and no pot — it drinks from the air, and borrows nothing.")),
    ("level-2-phone",    "I barely understand my phone",
     "Straight answers to what you are actually wondering: privacy, cost, and what breaks.",
     "Picks up where “like I’m 5” left off.",
     "v56.10.9.1",
     ("bulbosa",
      "A tillandsia is an epiphyte, not a parasite: it rests on its tree and takes nothing from it.")),
    ("level-3-power",    "I'm a power user",
     "The anatomy: what runs where, what survives a teardown, and where the sharp edges are.",
     "Assumes the two levels before it.",
     "v56.10.9.1",
     ("xerographica",
      "Its roots only grip; the leaves do the drinking — a plant that runs rootless.")),
    ("level-4-security", "I'm a Cyber Security expert",
     "The architecture interrogated rather than described — boundaries, egress, provenance, "
     "and what the tests do not actually test.",
     "Assumes the three levels before it.",
     "v56.10.9.1",
     ("usneoides",
      "Silvery leaf scales open to take water in, then trap air to keep it: every exchange "
      "across one surface.")),
    ("level-5-phd",      "I'm a MathWiz / Hacker",
     "And you would like me to be condescending about it. Very well.",
     "Assumes everything before it. Mathematics from here down.",
     "v56.10.9.1",
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
# (slug, label, command). The slug keys the row to the OS switcher on the
# I want it! page (see QUICKSTART_OS), so both share one vocabulary.
INSTALL = [
    ("linux",   "Linux",   "curl -fSsL %s/install.sh | bash" % SITE),
    ("macos",   "macOS",   "curl -fSsL %s/install-macos.sh | bash" % SITE),
    ("windows", "Windows", "irm %s/install.ps1 | iex" % SITE),
]

# kind -> (css class, glyph, visible label). GREEN/RED say what the *thing*
# does; PROVEN/PLAUSIBLE/REFUTED say how good *our argument* for it is. The
# source keywords are editor vocabulary; the visible labels are the reader's,
# so they say what the box means in plain words rather than naming a status.
FLAGS = {
    "GREEN":     ("flag-green",     "●", "checked"),
    "RED":       ("flag-red",       "●", "known limitation"),
    "PATH":      ("flag-path",      "→", "what happens next"),
    "NOTE":      ("flag-note",      "•", "note"),
    "PROVEN":    ("flag-proven",    "✓", "shown"),
    "PLAUSIBLE": ("flag-plausible", "∼", "not yet shown"),
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


# Runtime links in site prose are written `rcite("path#Lx-Ly", "label")` inside
# the page's HTML strings. They resolve against the site-wide pin, are checked
# like footnotes, and are re-anchored by content when the pin moves
# (scripts/anchors.py). An `@vTAG` suffix holds one at the release it was
# verified at, when its text could not be found again at the new pin.
RCITE = re.compile(r'rcite\("([^"]+)", "([^"]+)"\)')


def rcite(target, label, where):
    target, _, own = target.partition("@")
    ref = own or SITE_REF
    check_target(where, ref, target, "")
    url, _ = footnote_url(target, ref)
    return '<a href="%s">%s</a>' % (html.escape(url, quote=True), label)


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


def home_view():
    """The landing portrait: a photo of the Tlatoāni, and one fact drawn in the browser."""
    pool = "".join('<li>%s</li>' % html.escape(f) for f in facts.FACTS)
    art = ('<div class="homeart" role="img" aria-label="Tlatoāni at the monitor, stars above">'
           '<img class="homeart-img" src="assets/fedora-up.png" alt="">'
           '<span class="homeart-vignette" aria-hidden="true"></span></div>')
    return ('<section class="view is-active" id="view-home" role="tabpanel" aria-labelledby="nav-home">'
            '<div class="homecard">'
            '%s'
            '<h1 class="wordmark">Tillandsias</h1>'
            '<p class="byline">by Tlatoāni '
            '<a class="linkedin-badge" href="https://www.linkedin.com/in/luisdanielrangeltovar/" '
            'target="_blank" rel="noopener noreferrer" aria-label="Tlatoāni on LinkedIn (opens in a new tab)">'
            '<span class="linkedin-mark" aria-hidden="true">in</span></a></p>'
            '<p class="fact" id="fact">%s</p>'
            '<ul class="factpool" id="factpool" hidden>%s</ul>'
            '<p class="homelead">A small private cloud on your own computer. Its workspaces are '
            'thrown away and rebuilt; the work you push out of them is kept.</p>'
            '<p class="homego"><button class="gobtn" data-go="view-what">What is it?</button></p>'
            '</div></section>'
            % (art, html.escape(facts.FACTS[0]), pool))


# Screenshots for the "I want it!" page. Drop a file named <slug>.png (or .webp,
# .jpg) into var/html/assets/screenshots/ and rebuild: it appears in this order,
# captioned with its label. Missing ones are skipped, so the section is absent
# until the first screenshot lands.
SCREENSHOTS = [
    ("windows", "Windows"),
    ("macos",   "macOS"),
    ("gnome",   "Linux &#183; GNOME"),
    ("kde",     "Linux &#183; KDE Plasma"),
    ("cosmic",  "Linux &#183; COSMIC"),
]
SHOTS = ROOT / "var" / "html" / "assets" / "screenshots"
SHOT_EXTS = ("png", "webp", "jpg")

# The quickstart storyboard: four steps, one picture each, per system. Pictures
# are read from QUICKSTART_DIR as <os>-<step>.<ext>; an absent one renders a
# labelled placeholder (allowed live: it says what it is and claims nothing).
# Each step's last element cites where the sentence rests in the stable pin; it
# is never rendered, it is there for the update-website re-verification. A
# sentence may carry one link as [label](https://url); see qs_text().
QUICKSTART_OS = [("linux", "Linux"), ("macos", "macOS"), ("windows", "Windows")]
QUICKSTART = [
    # step, headline, sentence, {os: scene label}, source (not rendered)
    ("install", "Paste",
     "Run the line above. When it finishes, a Tillandsias icon sits in your tray.",
     {"linux":   "Linux top bar with the Tillandsias icon",
      "macos":   "macOS menu bar with the Tillandsias icon",
      "windows": "Windows notification area with the Tillandsias icon"},
     "v56.10.9.1 README.md:154-156"),
    ("scan", "Scan",
     "Choose GitHub login from that icon, point your phone at the QR code in the "
     "terminal and confirm the code at github.com/login/device.",
     {"linux":   "Phone over the QR code in a Linux terminal",
      "macos":   "Phone over the QR code in a macOS terminal",
      "windows": "Phone over the QR code in a Windows terminal"},
     "v56.10.9.1 tray-ux/spec.md:92; headless main.rs:11657 (QR of "
     "https://github.com/login/device?user_code=..., printed in the terminal); "
     "gh-auth-script/spec.md:152; windows-tray main.rs:1135; macos-tray diagnose.rs:2054-2056"),
    ("authorize", "Authorize",
     "Install the [Tillandsias GitHub App](https://github.com/apps/tillandsias) and "
     "choose which repositories it can use.",
     {"linux":   "GitHub's install page for the Tillandsias app, choosing repositories",
      "macos":   "GitHub's install page for the Tillandsias app, choosing repositories",
      "windows": "GitHub's install page for the Tillandsias app, choosing repositories"},
     "owner decision 2026-10-07 (design.md): the device flow logs in but does not "
     "install the App or pick repositories; v56.10.9.1 headless main.rs:11247 "
     "(GitHub App, App ID 5081125) names the App the flow belongs to; the install "
     "page itself is GitHub's, not in the release"),
    ("prompt", "Prompt",
     "Pick a project from the same icon and start typing.",
     {"linux":   "Prompt in a project opened from the Linux tray",
      "macos":   "Prompt in a project opened from the macOS menu bar",
      "windows": "Prompt in a project opened from the Windows tray"},
     "v56.10.9.1 simplified-tray-ux/spec.md:108; README.md:175"),
]
QUICKSTART_DIR = SHOTS / "quickstart"
# A browser cannot tell a Linux desktop apart, so a desktop-specific shot
# stands in for the generic Linux one; `any-<step>` serves every system.
QUICKSTART_FALLBACK = {"linux": ("gnome", "kde", "cosmic")}
QUICKSTART_ANY = "any"


def qs_text(text):
    """Escape a storyboard sentence, rendering its one optional [label](url) link."""
    m = re.fullmatch(r"(.*?)\[([^\]]+)\]\((https://[^)\s]+)\)(.*)", text, re.S)
    if not m:
        return html.escape(text)
    pre, label, url, post = m.groups()
    return '%s<a href="%s" target="_blank" rel="noopener">%s</a>%s' % (
        html.escape(pre), html.escape(url, quote=True), html.escape(label), html.escape(post))


def quickstart_shot(os_, step):
    """Resolve the storyboard picture for (os, step) to (src, alt), or None.

    Order: <os>-<step>, then the Linux desktop stand-ins (Linux only), then
    any-<step>; each tried as png, webp, jpg. None means "render the placeholder".
    """
    scene = next(s[3][os_] for s in QUICKSTART if s[0] == step)
    for prefix in (os_,) + QUICKSTART_FALLBACK.get(os_, ()) + (QUICKSTART_ANY,):
        for ext in SHOT_EXTS:
            if (QUICKSTART_DIR / ("%s-%s.%s" % (prefix, step, ext))).exists():
                return ("assets/screenshots/quickstart/%s-%s.%s" % (prefix, step, ext), scene)
    return None


INSTALL_NOTE = """\
Each line fetches a short script from this site, which
resolves the <strong>latest stable release</strong> on GitHub and runs that
release&#8217;s own installer. Stable moves only when a daily build is
promoted, so it normally trails the newest code. The scripts here are not
rebuilt when the app releases; they look the release up every time they
run. Current installers reset local application state and reprovision by
default; set <code>TILLANDSIAS_DESTRUCTIVE_RESET_OK=0</code> before running
one to skip the destructive reset. On Linux and Windows that reset keeps your
local vault and sign-ins; on macOS the stable release&#8217;s reset still
clears them, and a fix is pending."""


def quickstart_steps():
    """The four-step storyboard: per step one headline, one sentence, and one
    figure per system (hidden/shown by the OS radios' CSS), image or placeholder."""
    steps = []
    for n, (step, head, text, scenes, _source) in enumerate(QUICKSTART, 1):
        figs = []
        for os_, _label in QUICKSTART_OS:
            shot = quickstart_shot(os_, step)
            if shot:
                body = ('<img src="%s" alt="%s" loading="lazy">'
                        % (html.escape(shot[0], quote=True), html.escape(shot[1], quote=True)))
            else:
                body = ('<div class="qs-ph" role="img" aria-label="Screenshot to come: %s">'
                        '<span class="qs-ph-k">screenshot to come</span>'
                        '<span class="qs-ph-t">%s</span></div>'
                        % (html.escape(scenes[os_], quote=True), html.escape(scenes[os_])))
            figs.append('<figure class="qs-shot" data-os="%s">%s</figure>' % (os_, body))
        steps.append('<li class="qs-step"><h3 class="qs-h"><span class="qs-n" aria-hidden="true">%d</span>%s</h3>'
                     '<p class="qs-t">%s</p>%s</li>'
                     % (n, html.escape(head), qs_text(text), "".join(figs)))
    return '<ol class="qs-steps">%s</ol>' % "".join(steps)


def install_view(install):
    """The "I want it!" page: OS switcher, install commands, the four-step
    storyboard, then screenshots by platform."""
    # The radios are direct children of .qs so `:checked ~` reaches both the
    # install rows and the storyboard figures; no script is needed to switch.
    radios = "".join('<input class="sr" type="radio" name="qs-os" id="qs-%s" value="%s"%s>'
                     % (slug, slug, " checked" if slug == QUICKSTART_OS[0][0] else "")
                     for slug, _label in QUICKSTART_OS)
    switch = ('<div class="qs-os" role="group" aria-label="Your system">%s</div>'
              % "".join('<label for="qs-%s">%s</label>' % (slug, html.escape(label))
                        for slug, label in QUICKSTART_OS))
    shots = []
    for slug, label in SCREENSHOTS:
        for ext in SHOT_EXTS:
            if (SHOTS / ("%s.%s" % (slug, ext))).exists():
                shots.append('<figure class="shot"><img src="assets/screenshots/%s.%s" alt="Tillandsias '
                             'running on %s" loading="lazy"><figcaption>%s</figcaption></figure>'
                             % (slug, ext, label.replace("&#183;", "-"), label))
                break
    gallery = ('<h3 class="shots-h">On your desktop</h3><div class="shots">%s</div>' % "".join(shots)
               if shots else "")
    return ('<section class="view" id="view-install" role="tabpanel" aria-labelledby="nav-install">'
            '<div class="wrap"><h2 class="view-h">I want it!</h2>'
            '<p class="view-lede">One line in a terminal, one photo, one GitHub app, one prompt.</p>'
            '<div class="qs" id="quickstart">%s%s'
            '<div class="install-strip"><div class="install" aria-label="Install">%s'
            '<p class="ins-note">%s</p></div></div>%s</div>%s</div></section>'
            % (radios, switch, install, INSTALL_NOTE, quickstart_steps(), gallery))


def centicolons_view():
    """The CentiColons page: Stockfish analogy, worked model and shipped limits.

    The analogy is only the door. What follows states the unit, the three
    numbers in the worked model, the conditions that make comparisons
    comparable, three worked moves against a five-obligation example spec, the
    spec-to-element arrow the validators run, and the four things the score
    does not say. The example weights are the methodology's declared base
    weights; the example spec is invented for the page and is labelled as one.
    """
    body = """
<p>Chess engines like Stockfish combine bounded search with an evaluation of promising positions.
They do not solve the whole game from move one. The familiar <b>centipawn</b> label is now a calibrated
scale: Stockfish&rsquo;s <a href="https://github.com/official-stockfish/WDL_model">official WDL model</a>
relates evaluation and remaining material to self-play outcomes under its test conditions. It is not
a literal pawn count, a monotonically improving score, or a guarantee of victory.</p>

<p>Software engineering borrows the useful idea of an explicit evaluation, not chess&rsquo;s outcome model.
Tests provide evidence about declared behavior; a score can make remaining obligations visible.
Measuring that remainder is one task. Ensuring accepted changes do not regress is another.
Guaranteeing that the remainder eventually reaches zero additionally requires progress.</p>

<p><b>CentiColons (cc)</b> are evidence-based accounting for declared obligations. The intended contract
binds each credited assertion to the obligation, implementation inputs and required platform it actually
tested. A green test file alone is not enough. Under a fixed scope and scoring policy, the
<b>residual (R)</b> records what has not reached its evidence bar. Zero means those declared bars are met,
not that every possible defect is absent.</p>

<p><b>At stable @@SITE_REF@@:</b> Lua extracts scenario/requirement obligations and grades recorded
positive-test results. The rcite("scripts/lua/centicolon-grade-observed.lua#L38-L105", "grader")
still has assertion, implementation-provenance and platform-attribution gaps; its residual is a raw count,
not the full weighted policy below. The
rcite("scripts/lua/check-centicolon-ratchet.lua#L4-L138", "regression check is advisory"),
not enforced. Lua makes the metric executable; it does not by itself complete the methodology&rsquo;s guarantee.</p>

<h3>What a CentiColon counts</h3>

<p>The following is a <b>simplified binary weighted model</b>, not a claim that the entire policy is shipped.
Its base weights come from the
rcite("methodology/proximity.yaml#L27-L135", "methodology"),
which also declares modifiers, partial evidence credits, caps and penalties omitted from this example.
Every auditable
thing the project commits to&mdash;a <code>must</code> requirement, a systemic invariant, a positive or
negative litmus signal, a runtime trace, a provenance binding, an environment assumption&mdash;enters the
model as a named obligation with a stable identifier and a weight. The weights are declared policy
rather than measurement: a <code>must</code> requirement is worth 100, a systemic invariant 120, a passing
positive litmus 80, a passing negative litmus 100, a runtime trace 60, a <code>should</code> requirement 40.
Add up every weight in the fixed scope and you have the <b>budget</b>. New scope or changed policy
starts a different comparison; ordinary evidence improvement does not change that budget.</p>

<p>In this binary model, an obligation whose applicable evidence has reached its bar
contributes its weight to the earned column; one that has not contributes nothing. Three numbers come out,
and they are always reported together:</p>

<ul>
<li><b>earned</b> &mdash; the weights that reached their bar;</li>
<li><b>budget</b> &mdash; every weight the spec declared;</li>
<li><b>residual</b> &mdash; budget &minus; earned, the distance still to travel.</li>
</ul>

<p>This example has one property worth saying out loud: <b>closing an obligation moves the score by exactly that
obligation&rsquo;s weight, and the residual by exactly the same amount.</b> Nothing is averaged, smoothed
or estimated. Close the 80-point positive litmus and the score moves 80 and the residual moves 80, and a
reader can check it by hand. But a rising total can hide a lost obligation behind another gain.
Non-regression therefore compares <b>each retained obligation</b>, with the same policy and applicable
evidence, not just the total. That accounting rule is not a property of Stockfish&rsquo;s evaluations.</p>

<h3>A worked example, with declared weights</h3>

<p>Take a five-obligation example spec, invented for this page: a Submit button, an invariant about how
its payload is serialised, a positive litmus, a negative litmus, and a runtime trace. All declared,
none yet tested, the budget is 460 and the earned is 0. Now play the position.</p>

@@POS@@

<p>A quiet move. One positive litmus goes green and nothing else happens: no material changes hands,
no feature ships. In chess terms it is Nb1&ndash;c3 &mdash; the piece simply got to a better square, and
the number improved because the position improved. The score goes 0 &rarr; 80 of 460, the residual goes
460 &rarr; 380, and the budget does not move, because closing a claim is not deleting one.</p>

@@TACT@@

<p>A combination. One change ships the button end to end: the requirement is positively tested, its
negative case passes, and a runtime trace records the click. That is the knight fork &mdash; three things
fall at once, and the number says so by the size of the jump. 80 &rarr; 340 of 460, residual
380 &rarr; 120, +260 in a single move. Notice what the two moves share: the size of the jump is exactly
the declared weight of what closed. An engine&rsquo;s number moves because the position changed; this one
moves because evidence arrived, and by an amount somebody wrote down in advance rather than one an
evaluation function invented on the spot.</p>

<h3>From a sentence in a spec to a button on the screen</h3>

<p>Which raises the only question that matters: what does it <i>mean</i> for &ldquo;the Submit button
stays disabled until the form is valid&rdquo; to be closed? It means there is an arrow from that sentence
to something that can actually be executed, and that applicable execution evidence was recorded.
The assertion must discriminate the intended behavior; recording an unrelated pass cannot close it.
The arrow is the
validator, and it is the same shape every time: take the obligation the spec names, take the element the
spec is about, and run the check that decides whether the clause holds.</p>

@@BTN@@

<p>Each row is a clause, an executable witness, and a price. The three rows are three different kinds of
evidence for three different clauses &mdash; a <code>must</code> requirement at 100, a negative litmus at
100, a runtime trace at 60 &mdash; landing in one ledger, which is why the tactical move above is worth
+260 and not an average of three opinions.</p>

<p>The proposed <b>submetrics</b> also cover work outside feature behavior. Systems engineering does
not live in user-facing specifications alone. A large share of the real work is <b>systemic invariants</b>
&mdash; deterministic JSON sorting, sandboxed execution, no fragile shell pipes &mdash; and <b>transient
platform preconditions</b>, the Darwin <code>bash</code> quirks, the Windows CRLF line endings, the
container tmpfs bounds. If the metric only measured feature specs, all of that would read as zero progress
or be omitted from the evidence contract. Internal invariants can live in specifications too.
The proposed common model treats a scenario, invariant and platform precondition as a named obligation
with applicable evidence and a bar, without counting the same obligation twice.
The <code>./plan</code> ledger links a transient fix to the durable obligation and test that prevent recurrence;
closing a packet is not itself correctness credit. Stable Lua extraction lists invariants separately,
but the grading path does not yet consume them. Cacheable predicates restrict observation capabilities;
observing predicates acquire external evidence. Neither label proves an assertion adequate or its cost negligible.</p>

<h3>What would make the reduction monotonic?</h3>

<p>Fix the obligation set, weights and evidence policy; bind results to the exact assertions, inputs and
required platforms; keep a durable accepted baseline; and preserve every retained obligation&rsquo;s credit.
Under those conditions the residual cannot increase across accepted implementation changes.
A new counterexample must still invalidate bad credit: honest measurement can rise when we learn that
an earlier claim was wrong. Retractions are disclosed breaks in that monotone comparison, not exceptions
silently counted as non-regression. New scope and corrected knowledge must remain visible.</p>

<p>Even perfect non-regression permits a plateau. To guarantee eventual zero, require a further progress
premise: while a fixed nonnegative integer residual is positive, it decreases by at least one within
every next <i>K</i> cycles. Then completion takes at most <i>K &times; R<sub>0</sub></i> cycles.
That is a conditional bound, not a guarantee delivered by the current runtime.
<a href="#level-5-phd">Level 5</a> states the assumptions and the remaining evidence gap.</p>

<h3>What the number does not say</h3>

<p>A number this clean is exactly the number people will over-read, so here are the four things it
does not carry:</p>

<ul>
<li><b>It is a ranking, not a probability.</b> 340/460 is not a 74% chance the software is correct,
and two scores cannot be combined by Bayes. It orders states; it does not measure belief.</li>
<li><b>It answers the question it was asked.</b> Of what you declared, how much is closed. A requirement
nobody wrote down is invisible to it, not free.</li>
<li><b>Effort is not in it.</b> A hard obligation and an easy one are worth what their weights say they
are worth. The score records closure, never the cost of getting there.</li>
<li><b>A percentage can be improved by throwing obligations away.</b> The weighted Rust scorer reports
a broken comparison regime when an obligation is tombstoned; removing an obligation changes the budget
and may remove earned credit. This comparison warning prevents reading deletion as progress.
The separate Lua advisory reports retirements without refusing the run.</li>
</ul>

<p>The worked arithmetic is deliberately simpler than the full declared policy, and the shipped
measurements are narrower still. <a href="#level-5-phd">Level 5</a> separates those three layers.
CentiColons help operationalize the promise: they make declared evidence debt inspectable.
They do not yet complete an enforced non-regression guarantee, and a measurement alone cannot supply
the strict-progress premise of a termination proof.</p>
"""
    for key, name in (("@@POS@@", "cc-positional"), ("@@TACT@@", "cc-tactical"),
                      ("@@BTN@@", "cc-spec-button")):
        body = body.replace(key, figures.FIGURES[name])
    body = body.replace("@@SITE_REF@@", SITE_REF)
    body = RCITE.sub(lambda m: rcite(m.group(1), m.group(2), "centicolons"), body)
    body += metrics.centicolon_status(SITE_REF)
    art = ('<div class="pageart" role="img" aria-label="A chess game: Tlatoāni facing Mācron across the board">'
           '<img class="pageart-img" src="assets/chess-tlatoni-vs-macron.png" alt="">'
           '<span class="pageart-vignette" aria-hidden="true"></span></div>')
    return ('<section class="view" id="view-centicolons" role="tabpanel" aria-labelledby="nav-centicolons">'
            '<div class="wrap">'
            '<h2 class="view-h">...wait, WHAT?!</h2>'
            '<p class="view-lede">How measuring chess pawns inspired how we measure software convergence.</p>'
            + art +
            '<div class="prose" style="margin:28px 0 56px;">'
            + body +
            '</div>'
            '</div></section>')


def crdt_view():
    """The CRDT page: from a shared notebook to append-and-distil.

    The reader's journey is the operator's: "CRDT ...what?!" → non-conflict →
    semantic distillation → Lamport clocks (the next page). Every statement
    about the project describes what the ledger code and methodology actually
    do at the site's checked release; the page claims what git gives for free
    and what the project's discipline adds, and never that git is a CRDT.
    """
    body = """
<h3>Three friends and one notebook</h3>

<p>Imagine three friends keeping one notebook about a shared garden. There is only one notebook, so
they pass it around, and whoever has it writes. Then two of them go travelling, each takes a
photocopy, and for a month all three write in their own copy. When they meet again they hold three
notebooks that disagree.</p>

<p>Now the trouble starts. One crossed out &ldquo;water the ferns on Tuesdays&rdquo; and wrote
&ldquo;Thursdays&rdquo;. Another crossed out the same line and wrote &ldquo;Mondays&rdquo;. Which copy
is right? Nobody can say from the notebooks alone. Someone has to sit down, compare the three, and
decide. That sitting-down is a <b>merge conflict</b>, and it is the thing every team of people, and
every team of programs, eventually dreads.</p>

<h3>The rule that makes the dread go away</h3>

<p>Here is a different way to keep the notebook. <b>Nobody ever crosses anything out.</b> Each friend
only adds dated, signed lines: &ldquo;10 June, Ana: I watered the ferns.&rdquo; &ldquo;12 June, Ben:
the ferns look dry; I think Thursdays is wrong.&rdquo; When the three copies come back together you
simply put every line from every copy into one list and sort them. No line fights another line,
because no line was ever <i>replaced</i>. Three copies, one pile, zero arguments.</p>

<p>That is the whole idea behind a <b>conflict-free replicated data type</b>, or CRDT. Replicated:
many copies. Conflict-free: the copies can be combined by a rule that never needs a referee. The
rule has to have three everyday properties, and the notebook already has them:</p>

<ul>
<li><b>Order does not matter.</b> Add Ana&rsquo;s lines then Ben&rsquo;s, or Ben&rsquo;s then Ana&rsquo;s: same pile.</li>
<li><b>Grouping does not matter.</b> Combine two copies first and the third later, or all three at once: same pile.</li>
<li><b>Repeating does not matter.</b> Add the same copy twice by mistake: still the same pile.</li>
</ul>

<p>A pile you can only add to, with those three properties, is the simplest CRDT there is, and
mathematicians call it a <b>grow-only set</b>. Everything on this page is a variation of it.</p>

<h3>What git gives you for free</h3>

<p>A git repository is a very good notebook. Every change becomes a <b>commit</b>, every commit is
named by a fingerprint of its own contents, and every commit records which commit it came after. Any
number of people can take a copy, work alone for a month, and bring their commits back; git keeps all
of them, and it remembers exactly which commit knew about which. Branches, worktrees, forks and
pull requests are just different ways of carrying commits from one copy to another.</p>

<p>But git, on its own, is <b>not</b> a CRDT, and this page would be lying if it said so. Two people
who edit the same line of the same file still produce a conflict that a human has to settle. Git
replicates perfectly and remembers perfectly; what it cannot do is decide. The notebook rule has to
come from how you use it.</p>

<h3>The happy pile</h3>

<p>Tillandsias runs many AI agents on many computers: Linux, macOS and Windows hosts, some of them
disposable containers that exist for an hour. They all need to read and write one shared plan: what
is being worked on, what was found, what was proved, what was retracted. If that plan were one big
file that everyone edited, every hour would end in the three-notebooks problem. For a while it was,
and it did.</p>

<p>So the project applies the notebook rule to its own plan. Shared state is written as
<b>append-only evidence</b>: a host that wants to record something writes a <i>new file</i>, in a
folder of fragments, with a name only that host could have produced: the time in UTC, a random
suffix, and the host&rsquo;s own name. Once written, a fragment is never edited. If it turns out to
be wrong, the correction is another fragment. Git then has nothing to argue about, because no two
hosts ever touch the same file.</p>

@@PILE@@

<p>Seen this way, the whole GitHub apparatus stops being a source of friction and becomes a set of
conveyor belts. A work branch is a host&rsquo;s private stack of fragments. A pull request is that
stack arriving at the shared pile. A landing queue takes the stacks one at a time, checks each
against the pile as it stands at that moment, and adds it or sends it back; the tree that gets
checked is the tree that lands, never a slightly different one. Hooks refuse the few things that
would break the rule, such as editing the compacted base in place. None of these parts needs to know
about the others, because the only thing any of them ever does is <b>dump information into a shared
pile of evidence</b>.</p>

<h3>Semantic distillation</h3>

<p>A pile of thousands of fragments is not something you want to read. What you read is a
<b>view</b>, computed from the pile by a fixed recipe the project calls the fold: start from the last
compacted base, then apply every fragment, in an order the file names fix, so two hosts holding the
same files always compute the same view. Applying a fragment twice changes nothing. That recipe
is the distillation, and it is where the real CRDT thinking lives, because different kinds of
information need different rules:</p>

<ul>
<li><b>Work items and events are a grow-only set.</b> Two hosts adding different items both win;
adding the same item twice yields one item. A fact, once recorded, is never lost by a merge.</li>
<li><b>Single-valued fields are a register.</b> A status can hold only one value, so the fold picks
a winner deterministically, by timestamp and host name, never by whichever copy happened to arrive
first. The project is careful to say what this costs: a register keeps one value and drops the
other, which is exactly why facts are kept as a set and never as a register.</li>
<li><b>Progress climbs a ladder.</b> A status may move up (implemented, completed, verified, done)
freely, and may move down only when an explicit falsification event says so. A later, lower claim
cannot quietly undo a verified one; a disproof can.</li>
</ul>

<p>Every so often a host that can afford the full checks folds the fragments into a new base and
deletes exactly the files it folded, by name, never by pattern, so a fragment written by someone else
during compaction survives untouched.</p>

<h3>Rectified provenance</h3>

<p>The pile has one more property the notebook had: every line is signed and dated. Each fragment
records which host and which agent wrote it, when, and about which work item. Because nothing is
ever edited, the pile also keeps every mistake next to its correction: an agent that cited the wrong
evidence writes a fragment saying so, and a reader can see both the claim and the retraction,
in that order, forever.</p>

<p>That combination, an append-only pile plus provenance on every entry plus a deterministic way to
distil it, is what the project means when it says generated software should stand on
<b>evidence</b>. Code written by many agents in many places is only trustworthy if you can later
ask &ldquo;who claimed this, from what, and did anyone disprove it?&rdquo; and get an answer that
does not depend on which copy of the notebook you happen to be holding.</p>

<h3>What the pile does not promise</h3>

<p>Honesty about the limits is part of the method, so here are the three things a CRDT cannot do:</p>

<ul>
<li><b>It does not deliver.</b> Copies that hold the same fragments agree; nothing makes a fragment
arrive. Pushing, fetching and the landing queue are separate machinery.</li>
<li><b>It does not make a claim true.</b> Three hosts agreeing on a pile of evidence agree about what
was <i>recorded</i>. Whether a recorded test actually proves anything is a question for the
<a href="#centicolons">CentiColon</a> accounting, not for the merge rule.</li>
<li><b>It does not merge code.</b> Source files are still edited in place and still conflict; they go
through review and the full build. The pile is for the plan and its evidence, not for the program.</li>
</ul>

<p>The project also retracts its own CRDT claims when they fail: one deduplication routine once
described itself as a CRDT, and its header now says plainly that it is not, because first-wins
depends on arrival order. A pile that keeps its retractions is a pile worth trusting.</p>

<h3>One question left: who went first?</h3>

<p>Sorting the pile &ldquo;by date&rdquo; hides a problem. Three computers have three clocks, and none
of them agrees with the others to the millisecond. Whether one fragment came before another is not
something a wristwatch can settle. The answer is that computers do not need wristwatches at all;
they need to know what <i>caused</i> what, and git has been writing that down all along.
<button type="button" class="gobtn" data-go="view-lamport">Computers don&rsquo;t understand time &#8594;</button></p>
"""
    body = body.replace("@@PILE@@", figures.FIGURES["append-fold"])
    return ('<section class="view" id="view-crdt" role="tabpanel" aria-labelledby="nav-crdt">'
            '<div class="wrap">'
            '<h2 class="view-h">CRDT ...what?</h2>'
            '<p class="view-lede">Why many agents on many machines can all write to one shared plan '
            'and never have to argue about it.</p>'
            '<div class="prose" style="margin:28px 0 56px;">'
            + body +
            '</div>'
            '</div></section>')


def lamport_view():
    """The Lamport clocks page: "Computers don't understand time".

    Discrete time, why synchronising clocks is finicky, why logical time is
    the better abstraction, Lamport's rule, and the honest relationship to a
    git commit graph: the graph is the causal order itself; a Lamport clock is
    the smallest counter consistent with it, and git computes one of its own
    (generation numbers) for its commit-graph file. What Tillandsias ships is
    stated as it is: UTC-first fragment names and a (timestamp, host) register,
    with the causal order carried by git, and Lamport-style counters described
    in the methodology for iteration ordering.
    """
    body = """
<h3>Everyone&rsquo;s watch is a little wrong</h3>

<p>Ask three friends what time it is and you get three answers, a minute or two apart. Usually that
is fine. It stops being fine the moment you ask a question like &ldquo;did Ana write her note before
Ben read the notebook?&rdquo; and the two watches disagree by more than the gap between the two
events. Then &ldquo;before&rdquo; has no answer. Computers live in that situation all day long.</p>

<h3>Why a computer counts instead of flows</h3>

<p>A river flows; a metronome ticks. Inside a computer, time is a metronome: a tiny crystal
vibrates, a counter goes up by one on each vibration, and <i>that count is the only clock the machine
has</i>. Between two ticks nothing happens at all. The computer cannot say &ldquo;a bit after
tick 400&rdquo;; it can only say &ldquo;tick 400&rdquo; or &ldquo;tick 401&rdquo;. Time in a computer
is <b>discrete</b>: a staircase, not a ramp.</p>

<p>This is not a defect. A count is something a machine can compare exactly, copy exactly and
write down exactly. &ldquo;Four hundred&rdquo; is the same on every machine; &ldquo;a moment
ago&rdquo; is not.</p>

<h3>Why making clocks agree is so hard</h3>

<p>Fine, you say, just set every computer&rsquo;s counter from one trustworthy clock. Here is why that
is finicky in practice:</p>

<ul>
<li><b>The crystals drift.</b> Two quartz crystals never vibrate at exactly the same rate; left alone,
two machines drift apart by seconds a month. Warm one of them and it drifts faster.</li>
<li><b>Asking takes time.</b> To learn the time from a server you send a question and wait for the
answer. The answer is already stale by the time it arrives, and you cannot know by how much, because
the trip out and the trip back need not take the same time.</li>
<li><b>The sleep problem.</b> Laptops sleep, virtual machines pause, containers are frozen and
thawed. When they wake, their counter is wrong by exactly the time they were asleep, and they do not
know it yet. Tillandsias runs most of its work in exactly such machines.</li>
<li><b>Time itself is edited.</b> Leap seconds, time-zone rules, daylight saving and a human typing
the wrong date all change the number without anything having happened.</li>
</ul>

<p>Protocols such as NTP work hard at this and get two machines on one network to within a few
milliseconds. A few milliseconds is an eternity for a computer: thousands of events fit inside
it. So two timestamps from two machines can never prove which event came first.</p>

<h3>Letters crossing in the mail</h3>

<p>Step back and ask what we actually wanted to know. Not the time of day. We wanted to know whether
Ana&rsquo;s note <i>could have influenced</i> Ben&rsquo;s. If Ben read the notebook before Ana wrote in
it, his note cannot depend on hers, no matter what either watch says. If Ana posted a letter and Ben
replied to it, the reply came after the letter, even if Ben&rsquo;s clock says otherwise. And if two
letters crossed in the mail, neither came &ldquo;first&rdquo; in any sense that matters: they are
simply <b>concurrent</b>.</p>

<p>This relation, &ldquo;could have caused&rdquo;, is called <b>happens-before</b>, and it is the only
order a distributed system truly needs. Notice that it is a <i>partial</i> order: some pairs of events
are ordered, and some are not, and that is the honest answer.</p>

<h3>The trick: carry a counter in every letter</h3>

<p>In 1978 Leslie Lamport showed that you can capture happens-before with nothing but counting.
Each machine keeps one integer. The rule has three lines:</p>

<ol>
<li>Before you do anything worth recording, add one to your counter.</li>
<li>When you send a message, write your counter on it.</li>
<li>When you receive a message, set your counter to one more than the larger of your own and the
number on the message.</li>
</ol>

@@LAMPORT@@

<p>No machine ever asks what time it is. Yet if one event could have caused another, the first
always carries the smaller number, because the message that carried the influence also carried the
count. The number is not a time; it is a <b>logical clock</b>, and it is exactly as discrete as the
computer wanted it to be in the first place.</p>

<p>One honest caveat. A smaller number does not prove causation: two concurrent letters may carry
3 and 5 without either having influenced the other. Lamport&rsquo;s counter is consistent with
happens-before, not equal to it. Keeping one counter per machine (a <i>vector clock</i>) closes that
gap, at a cost in size. For most of what a project needs, the single counter is the right tool: it is
small, it never disagrees with causality, and a tie can be broken by the machine&rsquo;s name.</p>

<h3>Your git history already is this</h3>

<p>Now look at a git repository with the above in mind. Each commit is named by a fingerprint of
its contents, and that fingerprint covers the names of its parents. So a commit literally cannot
exist before its parents, and anyone holding a commit can follow the parent names all the way back.
The arrows in the graph are happens-before, written down.</p>

@@DAG@@

<p>This is better than a Lamport clock, not worse: the graph <i>is</i> the causal order, and a
Lamport clock is just the smallest counter that respects it. You can read one off the graph by
giving each commit one more than the largest number among its parents. Git in fact computes that
very number, which it calls a generation number, to speed up its own history searches. Git also
records the author&rsquo;s wall-clock date on every commit, but nothing about branching or merging
depends on it; two commits with crossed dates merge exactly as well as any others.</p>

<p>So the punchline is a cheap one, and that is the point: <b>back your project up in a git
repository and you get happens-before for free</b>. Every clone is a replica; every commit is an
event with its causes attached; every merge is a letter arriving. The clocks on the machines can be
wrong by hours, and the history still says, correctly, what came after what.</p>

<h3>How Tillandsias uses it</h3>

<p>The project keeps its shared plan as an append-only pile of fragments inside that git history,
so every fragment inherits the causal order of the commit that carried it. Within the pile, two
smaller choices are worth naming plainly:</p>

<ul>
<li><b>Fragment names begin with the UTC time</b>, so a plain alphabetical sort of the folder is
also a chronological one and every host folds the pile in the same order. That is a wall-clock
stamp, and the project knows it: nothing is <i>lost</i> if two hosts&rsquo; clocks disagree, because
facts are kept as a set, where order does not matter at all.</li>
<li><b>Where one value must win</b>, the fold breaks ties by timestamp and then by host name, so
every host picks the same winner from the same files. That is the familiar &ldquo;later watch
wins&rdquo; rule, chosen for a field where only one value can survive anyway, and never applied to
the facts.</li>
</ul>

<p>The methodology also describes Lamport-style counters for ordering an agent&rsquo;s iterations
across merges: tick locally, take the maximum on fetch, break ties by agent name. Where it matters
most, though, the project does not reach for a clock at all. The landing queue checks a candidate
against the shared branch at a particular commit, and just before pushing it reads the branch again:
if the commit has changed, the green result described a tree nobody is shipping, and the candidate
goes back in the queue. That is a happens-before check, done with git&rsquo;s own graph, and it is
the one that keeps the shipped tree equal to the tested tree.</p>

<p>Which is where this page and the last one meet. A pile you only add to needs no referee;
a history that names its causes needs no synchronised clock. Together they are most of what a
crowd of agents on a crowd of machines needs in order to agree.
<button type="button" class="gobtn" data-go="view-crdt">&#8592; CRDT ...what?</button></p>
"""
    body = (body.replace("@@LAMPORT@@", figures.FIGURES["lamport-exchange"])
                .replace("@@DAG@@", figures.FIGURES["commit-dag"]))
    return ('<section class="view" id="view-lamport" role="tabpanel" aria-labelledby="nav-lamport">'
            '<div class="wrap">'
            '<h2 class="view-h">Computers don&rsquo;t understand time</h2>'
            '<p class="view-lede">Why machines count instead of telling the time, and why a git '
            'history is already the clock you wanted.</p>'
            '<div class="prose" style="margin:28px 0 56px;">'
            + body +
            '</div>'
            '</div></section>')


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
        if s.get("layout") == "diagram":
            copy += '<p><button type="button" class="gobtn" data-go="view-big-graph">Explore Big Graph →</button></p>'
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


REVIEWED = metrics.reviewed_at()


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
            # The sources are evidence the reader can use, not a wall the
            # reader has to scroll past: collapsed under one plain question,
            # still in the page, and each number in the text still opens its
            # source directly.
            # A pin moved by the release refresh re-anchors citations, not
            # judgement: say which release a person last read the claims at.
            seen = REVIEWED.get(slug)
            review = ("" if not seen or seen == ref else
                      ' The sources were re-anchored to <code>%s</code> automatically; a person '
                      'last reviewed the claims themselves against <code>%s</code>.' % (ref, seen))
            fn_html = ('<details class="footnotes"><summary>How we know &#8212; %d sources</summary>'
                       '<p class="fn-note">Each small number in the text opens the exact lines '
                       'of the Tillandsias source that back that sentence, as they stand in '
                       'release <code>%s</code>, the one the install commands give you. Hover '
                       'a number to read the quoted lines without leaving the page. A source '
                       'marked with its own release points at a newer one.%s</p>'
                       '<ol class="fn-list">%s</ol></details>' % (len(notes), ref, review, "".join(rows)))
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

    install = "".join('<div class="ins-row" data-os="%s"><span class="ins-os">%s</span>'
                      '<span class="ins-box"><input readonly value="%s" '
                      'aria-label="%s install command" spellcheck="false">'
                      '<button class="ins-copy" type="button" title="Copy">Copy</button>'
                      '</span></div>'
                      % (slug, os_, html.escape(cmd, quote=True), os_) for slug, os_, cmd in INSTALL)
    # The tab icon is the same glyph the header carries, inlined as a data URI:
    # nothing to fetch, and the CSP has no image host to allow.
    favicon = "data:image/svg+xml," + urllib.parse.quote(
        figures.PLANTS["ionantha"].replace('stroke="currentColor"', 'stroke="#5fd6a4"'), safe="")
    doc = (TEMPLATE.replace("__INSTALL_VIEW__", install_view(install))
           .replace("__LEAF__", figures.PLANTS["ionantha"])
           .replace("__FAVICON__", favicon)
           .replace("__DEFS__", figures.DEFS)
           .replace("__HOME__", home_view())
           .replace("__PROGRESS__", progress.render(SITE_REF))
           .replace("__CENTICOLONS__", centicolons_view())
           .replace("__CRDT__", crdt_view())
           .replace("__LAMPORT__", lamport_view())
           .replace("__BIG_GRAPH__", big_graph.render(SITE_REF))
           .replace("__BIG_GRAPH_CSS__", big_graph.CSS + metrics.CSS)
           .replace("__BIG_GRAPH_JS__", big_graph.JS)
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
.install-strip{padding:18px 0 4px}
.shots-h{margin:48px 0 16px;font-size:18px;font-weight:600}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin:0 0 56px}
.shot{margin:0;border:1px solid var(--line);border-radius:11px;overflow:hidden;background:var(--bg-2)}
.shot img{display:block;width:100%;height:auto}
.shot figcaption{padding:9px 12px;font:600 11px/1.3 var(--mono);letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-faint)}
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
/* Quickstart: the OS radios sit first inside .qs, so `:checked ~` picks the
   emphasised install row and the visible storyboard figure without script. */
.qs-os{display:inline-flex;flex-wrap:wrap;gap:4px;margin:4px 0 8px;padding:3px;
  border:1px solid var(--line);border-radius:7px;background:var(--bg-2)}
.qs-os label{cursor:pointer;padding:7px 12px;border-radius:5px;border:1px solid transparent;
  font:600 11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-faint);transition:.15s}
.qs-os label:hover{color:var(--ink)}
#qs-linux:checked ~ .qs-os label[for=qs-linux],
#qs-macos:checked ~ .qs-os label[for=qs-macos],
#qs-windows:checked ~ .qs-os label[for=qs-windows]{color:var(--ink);border-color:var(--leaf-dim)}
#qs-linux:focus-visible ~ .qs-os label[for=qs-linux],
#qs-macos:focus-visible ~ .qs-os label[for=qs-macos],
#qs-windows:focus-visible ~ .qs-os label[for=qs-windows]{outline:2px solid var(--leaf);outline-offset:2px}
#qs-linux:checked ~ .install-strip .ins-row[data-os=linux] .ins-box,
#qs-macos:checked ~ .install-strip .ins-row[data-os=macos] .ins-box,
#qs-windows:checked ~ .install-strip .ins-row[data-os=windows] .ins-box{border-color:var(--leaf-dim)}
#qs-linux:checked ~ .install-strip .ins-row[data-os=linux] .ins-os,
#qs-macos:checked ~ .install-strip .ins-row[data-os=macos] .ins-os,
#qs-windows:checked ~ .install-strip .ins-row[data-os=windows] .ins-os{color:var(--leaf)}
.qs-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:28px 0 8px;
  padding:0;list-style:none}
.qs-step{min-width:0}
.qs-h{margin:0;font-size:15px;font-weight:600;line-height:1.3}
.qs-n{display:inline-block;margin-right:8px;font:600 12px/1 var(--mono);color:var(--leaf)}
.qs-t{margin:6px 0 0;max-width:36ch;font-size:14px;line-height:1.5;color:var(--ink-dim)}
.qs-t a{color:inherit}
.qs-shot{margin:10px 0 0;display:none}
#qs-linux:checked ~ .qs-steps .qs-shot[data-os=linux],
#qs-macos:checked ~ .qs-steps .qs-shot[data-os=macos],
#qs-windows:checked ~ .qs-steps .qs-shot[data-os=windows]{display:block}
.qs-shot img{display:block;width:100%;height:auto;border:1px solid var(--line);
  border-radius:9px;background:var(--bg-2)}
.qs-ph{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
  aspect-ratio:16/10;padding:14px 16px;border:1px dashed var(--line-2);border-radius:9px;
  background:rgba(255,255,255,.015);color:var(--ink-faint);font-size:13px;line-height:1.5;
  text-align:center}
.qs-ph-k{font:600 10.5px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-faint)}
.qs-ph-t{margin-top:4px}
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
/* Only the level rail is sticky; the hero scrolls away above it. */
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
/* CentiColon figures: a board fragment, its readouts, and the spec-to-element
   arrow. The board shades a1 dark and derives the rest, so the fragment cannot
   disagree with a full board; pieces are discs with letters rather than
   silhouettes, which stays legible at the small sizes the deck renders at. */
.s-l{fill:var(--ink);font:500 13px var(--sans);text-anchor:start}
.s-l.s-xs{font-size:11.5px}
.s-l.s-c{text-anchor:middle}
.s-big{fill:var(--ink);font:600 21px var(--mono);text-anchor:start}
.s-code{fill:var(--amber);font:500 9.5px var(--mono);text-anchor:middle}
.s-num{fill:var(--leaf);font:600 11.5px var(--mono);text-anchor:start}
.cb-d{fill:#101720;stroke:var(--line-2);stroke-width:.7}
.cb-l{fill:rgba(255,255,255,.055);stroke:var(--line-2);stroke-width:.7}
.cb-c{fill:var(--ink-faint);font:500 9.5px var(--mono);text-anchor:middle}
.pw{fill:#eef3f9;stroke:#0a0e14;stroke-width:1}
.pb{fill:#212a35;stroke:#8fa2b6;stroke-width:1.1}
.pl{fill:#0a0e14;font:700 12.5px var(--mono);text-anchor:middle}
.pli{fill:#dfe8f2;font:700 12.5px var(--mono);text-anchor:middle}
.cc-box{fill:#131a23;stroke:var(--line-2);stroke-width:1.2}
.cc-move{stroke:var(--leaf);stroke-width:2.2;fill:none;color:var(--leaf)}
.cc-atk{stroke:var(--amber);stroke-width:1.5;stroke-dasharray:4 4;fill:none;
  color:var(--amber)}
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
.footnotes summary{margin:0 0 6px;font:600 12px/1.6 var(--mono);letter-spacing:.2em;
  text-transform:uppercase;color:var(--ink-dim);cursor:pointer;width:max-content;max-width:100%}
.footnotes summary:hover{color:var(--leaf)}
.footnotes[open] summary{margin-bottom:12px}
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
.acc{display:flex;align-items:center;gap:10px;width:100%;text-align:left;cursor:pointer;
  background:transparent;border:1px solid transparent;border-radius:8px;color:var(--ink-dim);
  font:500 14.5px/1 var(--sans);padding:11px 10px;transition:.15s}
.acc:hover{color:var(--ink);background:rgba(255,255,255,.04)}
.acc[aria-checked="true"]{color:var(--ink);background:var(--panel);border-color:var(--line)}
.acc .acc-label{margin-right:auto}
.acc-track{position:relative;flex:0 0 auto;width:40px;height:23px;border:1px solid var(--line-2);
  border-radius:12px;background:var(--bg-2);transition:.18s}
.acc-track::after{content:"";position:absolute;top:2px;left:2px;width:17px;height:17px;
  border-radius:50%;background:var(--ink-faint);transition:.18s}
.acc[aria-checked="true"] .acc-track{background:var(--leaf-dim);border-color:var(--leaf)}
.acc[aria-checked="true"] .acc-track::after{left:19px;background:var(--leaf)}
.acc:focus-visible{outline:2px solid var(--leaf);outline-offset:2px}
.scrim{position:fixed;inset:0;z-index:38;background:rgba(4,6,9,.55)}
/* --- home --- */
.homecard{max-width:760px;margin:0 auto;padding:96px 24px 80px;text-align:center}
.homeart,.pageart{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;
  border:1px solid var(--line);border-radius:14px;
  background:linear-gradient(180deg,#0c1119,#080b10);color:var(--leaf-dim)}
.homeart{height:clamp(240px,42vh,460px);margin:0 0 34px}
.pageart{height:clamp(210px,30vh,340px);margin:0 0 26px}
.homeart-img,.pageart-img{width:100%;height:100%;object-fit:cover;display:block}
.homeart-vignette,.pageart-vignette{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(130% 130% at 50% 45%, transparent 50%, rgba(7,9,12,.55) 76%, rgba(7,9,12,.94) 100%),
    linear-gradient(180deg, rgba(7,9,12,.6), transparent 20% 80%, rgba(7,9,12,.8))}
.homeart-note{position:absolute;bottom:12px;right:14px;font:500 10.5px/1 var(--mono);
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint)}
.wordmark{margin:0;font-size:clamp(46px,10vw,96px);line-height:1;letter-spacing:-.04em;font-weight:660}
.byline{margin:12px 0 0;font:400 17px/1 var(--sans);color:var(--ink-dim)}
.linkedin-badge{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;
  margin-left:9px;border-radius:6px;background:#0a66c2;color:#fff;text-decoration:none;vertical-align:middle}
.linkedin-badge:hover{background:#004182;color:#fff}
.linkedin-badge:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.linkedin-mark{font:bold 14px/1 var(--sans)}
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
/* --- accountability ledger --- */
.ledger{max-width:1180px}
.ledger-stats{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}
.ledger-stats span{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--panel);font-size:12px;color:var(--ink-dim)}
.ledger-stats b{color:var(--leaf);font:600 15px var(--mono)}
.ledger-note{max-width:95ch;padding:12px 16px;border-left:3px solid var(--amber);background:var(--bg-2);color:var(--ink-dim);font-size:13px}
.ledger-note a,.ledger-detail a{color:var(--leaf)}
.ledger-search-label{display:block;margin:22px 0 7px;font:600 12px var(--mono);color:var(--ink-dim)}
.ledger-search{width:min(100%,650px);padding:12px 14px;border:1px solid var(--line-2);border-radius:8px;background:var(--panel);color:var(--ink);font:14px var(--sans)}
.ledger-search:focus{outline:2px solid var(--leaf-dim)}
.ledger-results{min-height:1.3em;margin:6px 0 25px;color:var(--ink-faint);font:11px var(--mono)}
.ledger-group{margin:32px 0 48px}.ledger-group h3{display:flex;align-items:center;gap:9px;margin:0;font-size:19px}
.ledger-group h3 span{padding:2px 8px;border-radius:20px;background:var(--line-2);color:var(--ink-dim);font:600 11px var(--mono)}
.ledger-group>p{margin:4px 0 14px;color:var(--ink-faint);font-size:13px}
.ledger-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:10px;align-items:start}
.ledger-card{min-width:0;border:1px solid var(--line);border-left:3px solid var(--line-2);border-radius:9px;background:var(--panel)}
.ledger-card.finding.sev-high{border-left-color:var(--rose)}.ledger-card.finding.sev-medium{border-left-color:var(--amber)}
.ledger-card.spec.current,.ledger-card.change.complete{border-left-color:var(--leaf-dim)}
.ledger-card.spec.retired,.ledger-card.spec.draft,.ledger-card.change.partial{border-left-style:dashed;opacity:.82}
.ledger-card summary{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px 8px;padding:13px 13px 12px;cursor:pointer;list-style:none}
.ledger-card summary::-webkit-details-marker{display:none}
.ledger-card summary:after{content:'+';order:3;margin-left:auto;color:var(--leaf);font:600 17px var(--mono)}
.ledger-card[open] summary:after{content:'−'}
.ledger-code{color:var(--leaf-dim);font:600 10px var(--mono);text-transform:uppercase}
.ledger-title{flex:1 1 75%;font-size:13px;line-height:1.4;color:var(--ink)}
.ledger-badge{border:1px solid var(--line-2);border-radius:4px;padding:1px 5px;color:var(--ink-faint);font:600 10px var(--mono)}
.ledger-meta{flex:1 1 100%;color:var(--ink-faint);font:11px var(--mono)}
.ledger-detail{padding:0 14px 13px;border-top:1px solid var(--line);overflow-wrap:anywhere}
.ledger-detail p,.ledger-detail li{font-size:12.5px;line-height:1.55;color:var(--ink-dim)}
.ledger-detail ul,.ledger-detail ol{padding-left:20px}.ledger-detail .muted{color:var(--ink-faint)}
.ledger-field h5{margin:15px 0 4px;color:var(--leaf);font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.11em}
.ledger-field p{margin:0 0 7px}
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
@media (max-width:900px){.cols{grid-template-columns:1fr}.qs-steps{grid-template-columns:repeat(2,1fr)}}
@media (max-width:760px){
  header.hero{padding:48px 0 24px}
  .tab{padding:12px}
  .install{grid-template-columns:1fr;gap:3px}
  .install-strip{padding:12px 0 2px}
  .ins-row{display:block}
  .ins-os{display:block;margin:7px 0 3px}
  .qs-steps{grid-template-columns:1fr}
  .qs-os{display:flex}
  .flag-path{margin-left:8px}
  .s-pillars{grid-template-columns:1fr}
}
@media (max-aspect-ratio:1/1){
  .has-art .s-body{grid-template-columns:1fr;gap:18px}
  .s-title{font-size:clamp(24px,5vw,46px)}
  .s-copy>p{font-size:clamp(16px,2.4vw,23px)}
  .s-body .fig{max-width:100%}
  /* Collapse the level tabs to one title: only the active level names
     itself, the rest stay clickable as number badges, and the fixed burger
     tucks into the left of the sticky rail instead of covering tab one. */
  .sticky .wrap{padding-left:64px}
  .burger{top:9px}
  .tabs{gap:5px}
  .tab{padding:11px 7px;font-size:12.5px}
  .tab .tab-t{display:none}
  .tab.is-active .tab-t{display:inline}
  .tab-n{padding:3px 4px;min-width:20px;text-align:center}
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
/* OpenDyslexic arrives via Fontsource on jsDelivr. The faces are declared
   unconditionally, but the default page never names the family, so the font
   files are only fetched once the accessibility switch turns the mode on. */
@font-face{font-family:'OpenDyslexic';font-style:normal;font-weight:400;font-display:swap;
  src:url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-400-normal.woff2) format('woff2'),
      url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-400-normal.woff) format('woff')}
@font-face{font-family:'OpenDyslexic';font-style:italic;font-weight:400;font-display:swap;
  src:url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-400-italic.woff2) format('woff2'),
      url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-400-italic.woff) format('woff')}
@font-face{font-family:'OpenDyslexic';font-style:normal;font-weight:700;font-display:swap;
  src:url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-700-normal.woff2) format('woff2'),
      url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-700-normal.woff) format('woff')}
@font-face{font-family:'OpenDyslexic';font-style:italic;font-weight:700;font-display:swap;
  src:url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-700-italic.woff2) format('woff2'),
      url(https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@5.3.0/files/opendyslexic-latin-700-italic.woff) format('woff')}
/* --- accessibility mode: high contrast, dyslexia-friendly type, no motion --- */
html:has(body.is-accessible){scroll-behavior:auto}
body.is-accessible{
  --bg:#050607; --bg-2:#0d0f11; --panel:#121518; --line:#3f464e; --line-2:#5a636d;
  --ink:#ffffff; --ink-dim:#f3f6fa; --ink-faint:#d2d9e1;
  --leaf:#7dffbc; --leaf-dim:#3ee08b; --sky:#9cc5ff; --sky-dim:#6fa0ee;
  --violet:#cdbcff; --amber:#ffd27a; --rose:#ff9fb0;
  --rg-0:#6dffb0; --rg-1:#55f4ba; --rg-2:#4ce8c8; --rg-3:#57d6dd; --rg-4:#69b8ec;
  --rg-5:#82a5ef; --rg-6:#a395ee; --rg-7:#bb8cf2;
  --sans:"OpenDyslexic",ui-sans-serif,-apple-system,"Segoe UI",Inter,Roboto,sans-serif;
  --mono:"OpenDyslexic",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  background:#000;background-image:none;color:#fff;font-size:18px;line-height:1.78}
body.is-accessible .prose p,body.is-accessible .lede,body.is-accessible .view-lede,
body.is-accessible .homelead,body.is-accessible .fact,body.is-accessible .ins-note,
body.is-accessible .drawer-f,body.is-accessible .card-t,body.is-accessible .card-m,
body.is-accessible .card-d,body.is-accessible .ledger-detail,body.is-accessible .blurb,
body.is-accessible footer,body.is-accessible .fn-note,body.is-accessible .qs-t,
body.is-accessible .s-lede,body.is-accessible .s-copy>p
{color:#fff}
body.is-accessible .prose,body.is-accessible .lede,body.is-accessible .view-lede,
body.is-accessible .homelead,body.is-accessible .fact,body.is-accessible .ins-note,
body.is-accessible .drawer-f,body.is-accessible .card-t,body.is-accessible .card-m,
body.is-accessible .ledger-detail,body.is-accessible .s-lede,body.is-accessible .s-copy>p,
body.is-accessible .qs-t
{letter-spacing:.018em;word-spacing:.05em;line-height:1.72}
body.is-accessible .qs-t{font-size:16px;max-width:44ch}
body.is-accessible .qs-ph{color:#d7dde4;border-color:#5a636d}
body.is-accessible .nav,body.is-accessible .acc{font-size:16px;line-height:1.2}
body.is-accessible .blurb,body.is-accessible .card-t{font-size:15px}
body.is-accessible a{text-decoration:underline;text-underline-offset:3px}
body.is-accessible :focus-visible{outline:3px solid var(--amber);outline-offset:2px}
body.is-accessible *,body.is-accessible *::before,body.is-accessible *::after{
  animation:none!important;transition:none!important}
body.is-accessible .eyebrow .updated{opacity:1}
body.is-accessible .ext{opacity:1}
body.is-accessible .homeart svg{opacity:1}
body.is-accessible .graph-lane-toggle[aria-pressed="false"]{opacity:.75}
body.is-accessible .s-prev:disabled,body.is-accessible .s-next:disabled{opacity:.65}
body.is-accessible code{background:#11151a;border-color:#5a636d;color:#ffd27a}
body.is-accessible .ins-box{background:#050607}
body.is-accessible .ins-box input:focus{color:#ffe9b0}
body.is-accessible .sticky{background:#000;backdrop-filter:none}
body.is-accessible .burger{background:#0d0f11}
body.is-accessible .homeart,body.is-accessible .pageart,body.is-accessible .fig{background:#050607}
body.is-accessible .deck-frame{background:#000}
body.is-accessible #tip{background:#0b0d10}
body.is-accessible #tip q{color:#fff}
body.is-accessible .graph-head{background:#050607}
body.is-accessible .graph-viewport{
  background:radial-gradient(circle at 1px 1px,#4d5b68 1px,transparent 0) 0 0/24px 24px,#000}
body.is-accessible .graph-node{background:#0c0e10;box-shadow:none}
body.is-accessible #graph-lines path{stroke:#8fa8bd}
body.is-accessible .graph-inspector{background:#0b0d10fa}
__BIG_GRAPH_CSS__
</style>
</head>
<body>
__DEFS__

<button class="burger" id="burger" aria-label="Open the menu" aria-expanded="false"
        aria-controls="drawer"><span></span><span></span><span></span></button>
<nav class="drawer" id="drawer" aria-label="Site">
  <p class="drawer-h">tillandsias.org</p>
  <button class="nav is-on" id="nav-home" data-go="view-home"><span class="nav-i">&#127968;</span>Home</button>
  <button class="nav" id="nav-what" data-go="view-what"><span class="nav-i">&#63;</span>What is it?</button>
  <button class="nav" id="nav-install" data-go="view-install"><span class="nav-i">&#8595;</span>I want it!</button>
  <button class="nav" id="nav-progress" data-go="view-progress"><span class="nav-i">&#9673;</span>Live progress</button>
  <button class="nav" id="nav-centicolons" data-go="view-centicolons"><span class="nav-i">&#9823;</span>CentiColons</button>
  <button class="nav" id="nav-crdt" data-go="view-crdt"><span class="nav-i">&#8853;</span>CRDT ...what?</button>
  <button class="nav" id="nav-lamport" data-go="view-lamport"><span class="nav-i">&#9201;</span>Lamport Clocks</button>
  <button class="nav" id="nav-slides" data-go="view-slides"><span class="nav-i">&#9654;</span>Slides</button>
  <button class="nav" id="nav-big-graph" data-go="view-big-graph"><span class="nav-i">&#9638;</span>Big Graph</button>
  <p class="drawer-f">Checked against release <code>__SITE_REF__</code>.</p>
  <button type="button" class="acc" id="acc-toggle" role="switch" aria-checked="false">
    <span class="acc-label">Accessible</span>
    <span class="acc-track" aria-hidden="true"></span>
  </button>
</nav>
<div class="scrim" id="scrim" hidden></div>

__HOME__

<section class="view" id="view-what" role="tabpanel" aria-labelledby="nav-what">
<header class="hero">
  <div class="wrap">
    <p class="eyebrow"><span class="leaf-ico" aria-hidden="true">__LEAF__</span>tillandsias.org <span class="ver" title="The release of the source repository this page was last checked against">&middot; __SITE_REF__</span> <span class="updated">&middot; website last updated __BUILD_STAMP__</span></p>
    <h1>A small cloud on your own computer,<br><span class="dim">built to be thrown away and rebuilt.</span></h1>
    <p class="lede">Your own hardware. Free software. No account and no subscription. Below is
      <strong>what it is and how it works</strong>, told five times over — pick the version that
      fits the person reading.</p>
  </div>
</header>

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

__INSTALL_VIEW__

__PROGRESS__

__CENTICOLONS__

__CRDT__

__LAMPORT__

__BIG_GRAPH__

__SLIDES__

<footer>
  <div class="wrap">
    <p>Source: <a href="https://github.com/8007342/tillandsias/">github.com/8007342/tillandsias</a>.
    The small numbers on each page open the lines of source that back each sentence, as they
    stand in the release named under &#8220;How we know&#8221; at the foot of that page, so
    they keep pointing at the right lines as the project moves on. Last checked against
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
// Quickstart: tick the visitor's system so the install row and the storyboard
// pictures match it. Client hints first, the UA string otherwise; an unknown
// platform leaves the markup default (Linux). Nothing is stored.
(function(){
  var p = ((navigator.userAgentData && navigator.userAgentData.platform) || navigator.userAgent || '').toLowerCase();
  var os = /mac|iphone|ipad|ipod/.test(p) ? 'macos'
         : /win/.test(p) ? 'windows'
         : /linux|android|x11|cros/.test(p) ? 'linux' : null;
  var r = os && document.getElementById('qs-' + os);
  if (r) r.checked = true;
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
// The menu, the five views, and one fact chosen per visit.
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

  // The accessibility switch: one class on <body> gates every override, the
  // choice is remembered per browser, and it starts off — today's styles.
  var acc = document.getElementById('acc-toggle'),
      KEY = 'tillandsias.org.accessibility';
  function applyAcc(on){
    document.body.classList.toggle('is-accessible', on);
    acc.setAttribute('aria-checked', on ? 'true' : 'false');
  }
  if (acc) {
    acc.addEventListener('click', function(){
      var on = !document.body.classList.contains('is-accessible');
      applyAcc(on);
      try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) {}
    });
    var saved;
    try { saved = localStorage.getItem(KEY); } catch (e) {}
    applyAcc(saved === '1');
  }

  var views = [].slice.call(document.querySelectorAll('.view')),
      navs  = [].slice.call(document.querySelectorAll('.nav'));
  function go(id, push){
    if (!document.getElementById(id)) return;
    document.body.classList.toggle('is-presenting', id === 'view-slides');
    document.body.classList.toggle('is-graphing', id === 'view-big-graph');
    views.forEach(function(v){ v.classList.toggle('is-active', v.id === id); });
    navs.forEach(function(n){ n.classList.toggle('is-on', n.dataset.go === id); });
    setMenu(false);
    if (push) history.replaceState(null, '', id === 'view-home' ? location.pathname + location.search : '#' + id.slice(5));
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

  // A deep link opens its view: #home, #what, #install, #progress, #centicolons, #crdt, #lamport, #slides, #big-graph, or a level.
  function fromHash(){
    var h = location.hash.slice(1);
    if (!h) return go('view-home', false);
    if (h === 'home' || h === 'what' || h === 'install' || h === 'progress' || h === 'slides' || h === 'centicolons' || h === 'crdt' || h === 'lamport' || h === 'big-graph') return go('view-' + h, false);
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
  // A plain cross-view link (#level-5-phd, from the CentiColons page) must
  // select the tab too: switching views alone would land the reader on level 1.
  window.addEventListener('hashchange', function(){
    var h = location.hash;
    if (/^#[rf]level-[a-z0-9-]+-\\d+$/.test(h)) return show(h.replace(/^#[rf]/, '').replace(/-\\d+$/, ''));
    if (/^#level-[a-z0-9-]+$/.test(h)) show(h.slice(1));
  });
  var h = location.hash.slice(1);
  if (h && document.getElementById('panel-' + h)) show(h);
})();
// Search only filters the rendered entries; the complete snapshot remains in the HTML.
(function(){
  var input=document.getElementById('ledger-search'),out=document.getElementById('ledger-results');
  if(!input)return;
  var cards=[].slice.call(document.querySelectorAll('[data-ledger-item]'));
  function filter(){var q=input.value.trim().toLowerCase(),shown=0;
    cards.forEach(function(card){var yes=!q||card.dataset.search.toLowerCase().indexOf(q)!==-1;
      card.hidden=!yes;if(yes)shown++;});
    document.querySelectorAll('[data-ledger-group]').forEach(function(group){
      group.hidden=!!q&&!group.querySelector('[data-ledger-item]:not([hidden])');});
    out.textContent=q?shown+' matching entries':'All '+cards.length+' entries shown';
  }
  input.addEventListener('input',filter);filter();
})();
__BIG_GRAPH_JS__
</script>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(build())
