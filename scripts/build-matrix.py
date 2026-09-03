#!/usr/bin/env python3
"""Assemble var/html/index.html from docs/matrix/level-*.md.

The sources are written in a small markdown dialect (see docs/matrix/README.md):
headings, bullets, GREEN/RED/PATH/NOTE callouts, $math$, @fig:NAME figures, and
[^n] footnotes whose targets are repo-relative paths resolved against a pinned
release tag so a reader lands on the exact line.
"""
import html
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import figures  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "matrix"
OUT = ROOT / "var" / "html" / "index.html"

REPO = "https://github.com/8007342/tillandsias"
# Links are pinned to the release the copy was written against, not to main:
# a reader clicking a line number must land on the line we actually quoted.
REF = "v56.9.2.1"
# Set TILLANDSIAS_CLONE to a checkout at REF to validate every footnote target.
CLONE = pathlib.Path(
    __import__("os").environ.get("TILLANDSIAS_CLONE", "")) if True else None

LEVELS = [
    ("level-1-five",     "Like I'm 5",
     "The simplest way of putting it that is still true.", ""),
    ("level-2-phone",    "I barely understand my phone",
     "Straight answers to what you are actually wondering: privacy, cost, and what breaks.",
     "Picks up where \u201clike I\u2019m 5\u201d left off."),
    ("level-3-power",    "I'm a power user",
     "The anatomy: what runs where, what survives a teardown, and where the sharp edges are.",
     "Assumes the two levels before it."),
    ("level-4-security", "I'm a Cyber Security expert",
     "The architecture interrogated rather than described \u2014 boundaries, egress, provenance, "
     "and what the tests do not actually test.",
     "Assumes the three levels before it."),
    ("level-5-phd",      "I'm a PhD / MathWiz / Hacker",
     "And you would like me to be condescending about it. Very well.",
     "Assumes everything before it. Mathematics from here down."),
]


# Rolling stable installers. These deliberately point at GitHub's
# /releases/latest/ rather than anything hosted here: this site is static HTML
# and redeploys on commit, while the release channel moves on its own.
DL = "https://github.com/8007342/tillandsias/releases/latest/download"
INSTALL = [
    ("Linux",   "curl -fsSL %s/install.sh | bash" % DL),
    ("macOS",   "curl -fsSL %s/install-macos.sh | bash" % DL),
    ("Windows", "irm %s/install-windows.ps1 | iex" % DL),
]

FLAGS = {
    "GREEN": ("flag-green", "\U0001F7E2", "works"),
    "RED":   ("flag-red",   "\U0001F534", "shortcoming"),
    "PATH":  ("flag-path",  "→",     "path to green"),
    "NOTE":  ("flag-note",  "•",     "note"),
}

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
EM = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
FN_REF = re.compile(r"\[\^(\d+)\]")
MATH_INLINE = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
FN_DEF = re.compile(r"^\[\^(\d+)\]:\s*(.+?)\s*\|\s*(\S+)\s*$")

broken_links = []


def footnote_url(target, level):
    """Repo-relative path (with optional #L anchors) or external URL -> href."""
    if target.startswith(("http://", "https://")):
        return target, True
    path, _, anchor = target.partition("#")
    if CLONE and CLONE.name:
        if not (CLONE / path).exists():
            broken_links.append((level, target, "path does not exist at %s" % REF))
        elif anchor:
            m = re.match(r"^L(\d+)(?:-L(\d+))?$", anchor)
            if not m:
                broken_links.append((level, target, "malformed line anchor"))
            else:
                lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
                try:
                    n = len((CLONE / path).read_text(errors="replace").splitlines())
                    if lo < 1 or hi > n or lo > hi:
                        broken_links.append(
                            (level, target, "line range outside file (%d lines)" % n))
                except OSError as exc:
                    broken_links.append((level, target, str(exc)))
    url = "%s/blob/%s/%s" % (REPO, REF, path)
    return url + ("#" + anchor if anchor else ""), False


def inline(text, level, fns, notes=None):
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
        fns.add(n)
        # The tooltip carries the footnote's own label and target, so a reader
        # can judge a citation without losing their place in the sentence.
        tip = ""
        if notes and n in notes:
            label, target = notes[n]
            tip = ' data-tip="%s"' % html.escape("%s  \u00b7  %s" % (label, target), quote=True)
        return ('<sup class="fnref" id="r%s-%s"><a href="#f%s-%s"%s>%s</a></sup>'
                % (level, n, level, n, tip, n))

    out = FN_REF.sub(ref, out)
    return re.sub(r"\x00(\d+)\x00", lambda m: shield[int(m.group(1))], out)


def render(lines, level, fns, notes=None):
    out, para, items, ordered = [], [], [], [False]
    math_buf, in_math = [], [False]
    callout = []  # [css class, icon, label, [paragraphs]] while one is open

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para), level, fns, notes))
            para.clear()

    def flush_items():
        if items:
            tag = "ol" if ordered[0] else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(
                "<li>%s</li>" % inline(i, level, fns, notes) for i in items), tag))
            items.clear()
            ordered[0] = False

    def flush_callout():
        if callout:
            cls, icon, label, paras = callout[0]
            body = "".join("<p>%s</p>" % inline(x, level, fns, notes) for x in paras if x.strip())
            out.append(
                '<div class="callout %s"><span class="callout-icon" aria-hidden="true">%s</span>'
                '<span class="sr">%s: </span><div>%s</div></div>' % (cls, icon, label, body))
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
                print("  ! unknown figure @fig:%s in %s" % (name, level))
        elif line.startswith("### "):
            flush()
            out.append("<h4>%s</h4>" % inline(line[4:], level, fns, notes))
        elif line.startswith("## "):
            flush()
            out.append("<h3>%s</h3>" % inline(line[3:], level, fns, notes))
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
    """Split a source file into body lines and footnote definitions."""
    body, notes, in_notes = [], {}, False
    for line in path.read_text().splitlines():
        if re.match(r"^##\s+Footnotes\s*$", line, re.I):
            in_notes = True
            continue
        if in_notes:
            m = FN_DEF.match(line.strip())
            if m:
                notes[m.group(1)] = (m.group(2), m.group(3))
            elif line.strip():
                print("  ! unparsed footnote line in %s: %s" % (level, line[:70]))
        else:
            body.append(line)
    return body, notes


def build():
    panels, tabs = [], []
    for idx, (slug, title, blurb, cont) in enumerate(LEVELS):
        path = SRC / ("%s.md" % slug)
        fns = set()
        if path.exists():
            body, notes = parse(path, slug)
            content = render(body, slug, fns, notes)
        else:
            content, notes = "<p>Not written yet.</p>", {}

        missing = sorted(fns - set(notes), key=int)
        if missing:
            print("  ! %s references undefined footnotes: %s" % (slug, ", ".join(missing)))
        unused = sorted(set(notes) - fns, key=int)
        if unused:
            print("  ! %s defines unreferenced footnotes: %s" % (slug, ", ".join(unused)))

        fn_html = ""
        if notes:
            rows = []
            for n in sorted(notes, key=int):
                label, target = notes[n]
                url, external = footnote_url(target, slug)
                shown = target if not external else re.sub(r"^https?://", "", target)
                rows.append(
                    '<li id="f%s-%s"><a class="fn-back" href="#r%s-%s" aria-label="back to text">%s</a>'
                    '<span class="fn-body">%s <a class="fn-link" href="%s" target="_blank" '
                    'rel="noopener">%s<span class="ext" aria-hidden="true">&#8599;</span></a></span></li>'
                    % (slug, n, slug, n, n, html.escape(label), url, html.escape(shown)))
            fn_html = ('<section class="footnotes"><h3>Footnotes</h3>'
                       '<p class="fn-note">Every link points at release <code>%s</code> of the '
                       'source repository, so line numbers match the text above.</p>'
                       '<ol class="fn-list">%s</ol></section>' % (REF, "".join(rows)))

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
    doc = (TEMPLATE.replace("__INSTALL__", install)
           .replace("__DEFS__", figures.DEFS)
           .replace("__TABS__", "\n".join(tabs))
           .replace("__PANELS__", "\n".join(panels))
           .replace("__REF__", REF))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)

    if broken_links:
        print("\n  %d BROKEN footnote target(s):" % len(broken_links))
        for lvl, tgt, why in broken_links:
            print("    %-18s %-52s %s" % (lvl, tgt, why))
    elif CLONE and CLONE.name:
        print("  all footnote targets resolve at %s" % REF)
    print("wrote %s (%d bytes)" % (OUT, len(doc)))
    return 1 if broken_links else 0


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
header.hero{padding:76px 0 40px;border-bottom:1px solid var(--line)}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.22em;text-transform:uppercase;
  color:var(--leaf);margin:0 0 20px}
h1{margin:0;font-size:clamp(32px,5vw,56px);line-height:1.07;letter-spacing:-.026em;font-weight:650}
h1 .dim{color:var(--ink-faint);font-weight:400}
.lede{max-width:64ch;margin:22px 0 0;font-size:19px;color:var(--ink-dim)}
.lede strong{color:var(--ink);font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:18px;margin:28px 0 0;padding:16px 18px;
  border:1px solid var(--line);border-radius:11px;background:var(--bg-2);
  font-size:13.5px;color:var(--ink-dim)}
.legend b{color:var(--ink);font-weight:600}
.install{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;align-items:center;
  padding:14px 0 2px}
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
.tabs{display:flex;gap:6px;overflow-x:auto;padding:20px 0 0;margin:0 0 -1px;
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
.prose h3{margin:44px 0 14px;font-size:23px;letter-spacing:-.02em;font-weight:640;
  padding-top:18px;border-top:1px solid var(--line)}
.prose h3:first-child{border-top:none;margin-top:16px;padding-top:0}
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
.callout{display:flex;gap:12px;align-items:flex-start;margin:0 0 12px;padding:14px 16px;
  border:1px solid var(--line-2);border-radius:10px;background:var(--bg-2);max-width:74ch}
.callout div{color:#cdd8e4}
.callout-icon{flex:0 0 auto;font-size:14px;line-height:1.5;filter:saturate(1.1)}
.flag-green{border-left:3px solid var(--leaf)}
.flag-red{border-left:3px solid var(--rose)}
.flag-path{border-left:3px solid var(--amber);margin-top:-6px;margin-left:26px;
  background:transparent;border-top:none;border-right:none;border-bottom:none;
  border-radius:0;padding:4px 0 10px 14px;font-size:14.5px}
.flag-path .callout-icon{color:var(--amber);font-weight:700}
.flag-path div{color:var(--ink-dim)}
.flag-note{border-left:3px solid var(--line-2)}
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
.fnref a{color:var(--leaf);text-decoration:none;padding:0 1px}
.fnref a:hover{text-decoration:underline}
.fnref a{position:relative}
#tip{position:fixed;z-index:60;max-width:min(30rem,calc(100vw - 24px));padding:9px 12px;
  border:1px solid var(--line-2);border-radius:8px;background:#141b24;color:var(--ink-dim);
  font:400 13px/1.5 var(--sans);box-shadow:0 10px 30px rgba(0,0,0,.5);pointer-events:none;
  opacity:0;transform:translateY(3px);transition:opacity .12s,transform .12s}
#tip.on{opacity:1;transform:none}
#tip b{color:var(--ink);font-weight:600}
#tip span{display:block;margin-top:4px;font:500 11.5px var(--mono);color:var(--ink-faint);
  word-break:break-all}
.footnotes{margin:56px 0 0;padding:26px 0 0;border-top:1px solid var(--line)}
.footnotes h3{margin:0 0 6px;font:600 12px/1 var(--mono);letter-spacing:.2em;
  text-transform:uppercase;color:var(--ink-dim)}
.fn-note{margin:0 0 18px;font-size:13.5px;color:var(--ink-faint)}
.fn-list{list-style:none;margin:0;padding:0;counter-reset:none}
.fn-list li{display:flex;gap:12px;margin:0 0 9px;font-size:14px;line-height:1.55}
.fn-back{flex:0 0 22px;text-align:right;font:600 11px var(--mono);color:var(--leaf-dim);
  text-decoration:none;padding-top:3px}
.fn-back:hover{color:var(--leaf)}
.fn-body{color:var(--ink-dim)}
.fn-link{display:inline;color:var(--ink-faint);font:500 12.5px var(--mono);
  text-decoration:none;border-bottom:1px dotted var(--line-2);word-break:break-all}
.fn-link:hover{color:var(--leaf);border-bottom-color:var(--leaf-dim)}
.ext{padding-left:3px;opacity:.7}
footer{border-top:1px solid var(--line);padding:34px 0 60px;color:var(--ink-faint);font-size:14px}
footer a{color:var(--ink-dim)}
footer a:hover{color:var(--leaf)}
@media (max-width:760px){
  header.hero{padding:48px 0 28px}
  .tab-t{display:none}
  .tab{padding:12px}
  .install{grid-template-columns:1fr;gap:3px;padding:10px 0 2px}
  .ins-row{display:block}
  .ins-os{display:block;margin:7px 0 3px}
  .callout{padding:12px 13px}
  .flag-path{margin-left:12px}
}
</style>
</head>
<body>
__DEFS__

<header class="hero">
  <div class="wrap">
    <p class="eyebrow">tillandsias.org</p>
    <h1>An idempotent, ephemeral cloud region,<br><span class="dim">folded through your hypervisor.</span></h1>
    <p class="lede">Local hardware. Free software. Nothing rented, nothing metered, nothing left
      behind. Below is <strong>what it is and how it works</strong>, told five times over — pick
      the version that fits the person reading.</p>
    <div class="legend">
      <span>&#x1F7E2; <b>Green flag</b> — verified and working.</span>
      <span>&#x1F534; <b>Red flag</b> — incomplete, pending, or overclaimed.</span>
      <span>&#8594; <b>Path to green</b> — what the plan records as the fix, or that it records none.</span>
    </div>
  </div>
</header>

<div class="sticky">
  <div class="wrap">
    <div class="install" aria-label="Install">
__INSTALL__
    </div>
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

<footer>
  <div class="wrap">
    <p>Source: <a href="https://github.com/8007342/tillandsias/">github.com/8007342/tillandsias</a>.
    Every footnote on this page links into release <code>__REF__</code>, so the line numbers
    stay true even as the project moves on.</p>
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
// Footnote tooltips: shown on hover and on keyboard focus, positioned inside
// the viewport so a citation near the right edge is not clipped.
(function(){
  var tip = document.createElement('div');
  tip.id = 'tip'; tip.setAttribute('role', 'tooltip');
  document.body.appendChild(tip);
  var hideTimer;
  function show(a){
    var raw = a.getAttribute('data-tip'); if (!raw) return;
    clearTimeout(hideTimer);
    var parts = raw.split('  \u00b7  ');
    tip.innerHTML = '';
    var b = document.createElement('b'); b.textContent = parts[0]; tip.appendChild(b);
    if (parts[1]) { var s = document.createElement('span'); s.textContent = parts[1]; tip.appendChild(s); }
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
    var a = e.target.closest('.fnref a[data-tip]'); if (a) show(a);
  });
  document.addEventListener('mouseout', function(e){
    if (e.target.closest('.fnref a[data-tip]')) hide();
  });
  document.addEventListener('focusin', function(e){
    var a = e.target.closest('.fnref a[data-tip]'); if (a) show(a);
  });
  document.addEventListener('focusout', hide);
  window.addEventListener('scroll', function(){ tip.classList.remove('on'); }, {passive:true});
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
    if (e.key >= '1' && e.key <= '5' && !/^(INPUT|TEXTAREA)$/.test(e.target.tagName)) {
      var t = tabs[+e.key - 1]; if (t) show(t.dataset.target);
    }
  });
  // A footnote link from another level must switch to that level before jumping.
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
