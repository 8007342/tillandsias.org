#!/usr/bin/env python3
"""Assemble var/html/index.html from docs/matrix/level-*.md.

Each source file has two H2 sections: `## WHAT IT IS` and `## HOW IT WAS BUILT`.
Content is minimal markdown: paragraphs, bullets, `code`, **bold**, _em_.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "matrix"
OUT = ROOT / "var" / "html" / "index.html"

LEVELS = [
    ("level-1-five",     "Like I'm 5",        "the simplest, stupidest way of explaining it correctly"),
    ("level-2-phone",    "I barely understand my phone", "no jargon, everyday analogies, the questions you actually have"),
    ("level-3-power",    "I'm a power user",  "you've run Docker and self-hosted things; here are the real parts"),
    ("level-4-security", "I'm a Cyber Security expert", "trust boundaries, blast radius, provenance — answered before you ask"),
    ("level-5-phd",      "I'm a PhD / MathWiz / Hacker", "and I'd like you to be condescending about it"),
]

INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"), r"<em>\1</em>"),
]


def inline(text):
    """Escape, then apply inline markup — code spans are shielded from bold/em."""
    out = html.escape(text.strip())
    spans = []

    def stash(m):
        spans.append("<code>%s</code>" % m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    out = INLINE[0][0].sub(stash, out)
    for pat, rep in INLINE[1:]:
        out = pat.sub(rep, out)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], out)


def render(block_lines):
    """Turn a run of markdown lines into HTML."""
    out, buf, bullets = [], [], []
    ordered = [False]

    def flush_para():
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
            buf.clear()

    def flush_list():
        if bullets:
            items = "".join("<li>%s</li>" % inline(b) for b in bullets)
            out.append("<%(t)s>%(i)s</%(t)s>" % {"t": "ol" if ordered[0] else "ul", "i": items})
            bullets.clear()
            ordered[0] = False

    for line in block_lines:
        stripped = line.strip()
        if not stripped:
            flush_para(); flush_list()
        elif stripped.startswith("### "):
            flush_para(); flush_list()
            out.append("<h3>%s</h3>" % inline(stripped[4:]))
        elif re.match(r"^[-*+]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            is_ord = bool(re.match(r"^\d+[.)]\s+", stripped))
            if bullets and is_ord != ordered[0]:
                flush_list()
            flush_para()
            ordered[0] = is_ord
            bullets.append(re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", stripped))
        elif bullets:
            bullets[-1] += " " + stripped
        else:
            buf.append(stripped)
    flush_para(); flush_list()
    return "\n".join(out)


def split_sections(text):
    sections, key, lines = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            if key:
                sections[key] = lines
            key, lines = m.group(1).strip().upper(), []
        elif key:
            lines.append(line)
    if key:
        sections[key] = lines
    return sections


def main():
    panels, tabs = [], []
    for idx, (slug, title, blurb) in enumerate(LEVELS):
        path = SRC / f"{slug}.md"
        secs = split_sections(path.read_text()) if path.exists() else {}
        what = render(secs.get("WHAT IT IS", ["_Not written yet._"]))
        how = render(secs.get("HOW IT WAS BUILT", ["_Not written yet._"]))
        active = " is-active" if idx == 0 else ""
        tabs.append(
            f'<button class="tab{active}" role="tab" aria-selected="{"true" if not idx else "false"}" '
            f'aria-controls="panel-{slug}" id="tab-{slug}" data-target="{slug}">'
            f'<span class="tab-n">{idx + 1}</span><span class="tab-t">{html.escape(title)}</span></button>'
        )
        panels.append(f"""<section class="panel{active}" id="panel-{slug}" role="tabpanel" aria-labelledby="tab-{slug}">
  <p class="blurb">{html.escape(blurb)}</p>
  <div class="grid">
    <article class="cell what">
      <h2><span class="marker">01</span> What it is</h2>
      {what}
    </article>
    <article class="cell how">
      <h2><span class="marker">02</span> How it was built</h2>
      {how}
    </article>
  </div>
</section>""")

    doc = TEMPLATE.replace("__TABS__", "\n".join(tabs)).replace("__PANELS__", "\n".join(panels))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"wrote {OUT} ({len(doc)} bytes)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tillandsias — an ephemeral cloud region, folded through your hypervisor</title>
<meta name="description" content="What Tillandsias is, and how it was built — explained at five levels, from five-year-old to condescended-to PhD.">
<style>
:root{
  --bg:#07090c; --bg-2:#0c1015; --panel:#0f141b; --line:#1c2531;
  --ink:#dfe7ef; --ink-dim:#8d9bab; --ink-faint:#5d6a79;
  --leaf:#5fd6a4; --leaf-dim:#2e7f61; --violet:#a48bf0; --amber:#e6b45e;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Inter,Roboto,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:400 16px/1.65 var(--sans); -webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(60rem 40rem at 15% -10%, rgba(95,214,164,.07), transparent 60%),
    radial-gradient(50rem 36rem at 92% 4%, rgba(164,139,240,.06), transparent 62%);
  background-attachment:fixed;
}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
header.hero{padding:72px 0 40px;border-bottom:1px solid var(--line)}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.22em;text-transform:uppercase;color:var(--leaf);margin:0 0 20px}
h1{margin:0;font-size:clamp(34px,5.2vw,60px);line-height:1.06;letter-spacing:-.025em;font-weight:650}
h1 .dim{color:var(--ink-faint);font-weight:400}
.lede{max-width:62ch;margin:22px 0 0;font-size:19px;color:var(--ink-dim)}
.lede strong{color:var(--ink);font-weight:600}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin:26px 0 0;padding:0;list-style:none}
.pills li{font:500 12px/1 var(--mono);letter-spacing:.06em;color:var(--ink-dim);
  border:1px solid var(--line);border-radius:999px;padding:8px 13px;background:var(--bg-2)}
.tabs{display:flex;gap:6px;overflow-x:auto;padding:22px 0 0;margin:0 0 -1px;scrollbar-width:thin}
.tab{appearance:none;cursor:pointer;flex:0 0 auto;display:flex;align-items:center;gap:9px;
  background:transparent;border:1px solid transparent;border-bottom:none;color:var(--ink-faint);
  font:500 13.5px/1 var(--sans);padding:12px 15px;border-radius:9px 9px 0 0;transition:.15s}
.tab:hover{color:var(--ink);background:rgba(255,255,255,.03)}
.tab.is-active{color:var(--ink);background:var(--panel);border-color:var(--line)}
.tab-n{font:600 11px/1 var(--mono);color:var(--leaf-dim);border:1px solid var(--line);
  border-radius:5px;padding:4px 6px}
.tab.is-active .tab-n{color:var(--bg);background:var(--leaf);border-color:var(--leaf)}
.sticky{position:sticky;top:0;z-index:10;background:rgba(7,9,12,.86);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}
main{padding:0 0 96px}
.panel{display:none;animation:fade .28s ease both}
.panel.is-active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.blurb{margin:34px 0 26px;font:400 15px/1.6 var(--sans);color:var(--ink-faint);
  border-left:2px solid var(--leaf-dim);padding-left:14px;max-width:70ch}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start}
.cell{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:30px 32px;
  position:relative;overflow:hidden}
.cell::before{content:"";position:absolute;inset:0 0 auto 0;height:2px}
.cell.what::before{background:linear-gradient(90deg,var(--leaf),transparent)}
.cell.how::before{background:linear-gradient(90deg,var(--violet),transparent)}
.cell h2{margin:0 0 20px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;
  font-family:var(--mono);font-weight:600;color:var(--ink-dim);display:flex;align-items:center;gap:10px}
.cell.what h2{color:var(--leaf)}
.cell.how h2{color:var(--violet)}
.marker{font-size:11px;opacity:.5}
.cell h3{margin:26px 0 10px;font-size:15px;font-weight:650;letter-spacing:-.01em;color:var(--ink)}
.cell p{margin:0 0 15px;color:#c6d1dd}
.cell ul{margin:0 0 16px;padding-left:0;list-style:none}
.cell ol{margin:0 0 18px;padding-left:0;list-style:none;counter-reset:n}
.cell ol>li{counter-increment:n;padding-left:34px}
.cell ol>li::before{content:counter(n,decimal-leading-zero);left:0;top:0;width:auto;height:auto;
  background:none;border-radius:0;font:600 11px/1.7 var(--mono);color:var(--leaf-dim);letter-spacing:.06em}
.cell.how ol>li::before{color:#7a68b8}
.cell li{position:relative;padding-left:18px;margin:0 0 9px;color:#c6d1dd}
.cell li::before{content:"";position:absolute;left:3px;top:.68em;width:5px;height:5px;
  border-radius:50%;background:var(--leaf-dim)}
.cell.how li::before{background:#5a4a8e}
code{font:500 .875em/1.4 var(--mono);background:#161d26;border:1px solid #212b38;
  border-radius:5px;padding:.12em .38em;color:var(--amber);word-break:break-word}
strong{color:#eef3f8;font-weight:640}
footer{border-top:1px solid var(--line);padding:34px 0 60px;color:var(--ink-faint);font-size:14px}
footer a{color:var(--ink-dim)}
footer a:hover{color:var(--leaf)}
@media (max-width:900px){
  .grid{grid-template-columns:1fr}
  .cell{padding:24px 22px}
  header.hero{padding:48px 0 28px}
  .tab-t{display:none}
  .tab{padding:12px}
}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <p class="eyebrow">tillandsias.org</p>
    <h1>An idempotent, ephemeral cloud region,<br><span class="dim">folded through your hypervisor.</span></h1>
    <p class="lede">Local hardware. Free software. Nothing rented, nothing metered, nothing left
      behind. Below: <strong>what it is</strong> and <strong>how it was built</strong>, told five times
      over — pick the version that fits the person reading.</p>
    <ul class="pills">
      <li>local hardware</li><li>free software</li><li>ephemeral by default</li>
      <li>idempotent</li><li>CRDT at every layer</li>
      <li>monotonic reduction of uncertainty</li>
    </ul>
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

<footer>
  <div class="wrap">
    <p>Source: <a href="https://github.com/8007342/tillandsias/">github.com/8007342/tillandsias</a>
    — content drawn from the Tillandsias Spec and the Tillandsias Methodology.</p>
  </div>
</footer>

<script>
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
  var h = location.hash.slice(1);
  if (h && document.getElementById('panel-' + h)) show(h);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
