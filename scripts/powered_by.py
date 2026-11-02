"""Powered By: the stack ledger as one very simple graph, plus a flat credits table.

The data is docs/powered-by/stack.v1.json, a copy of the runtime's generated
docs/credits/stack.v1.json (scripts/snapshot-stack.py). Nothing here types a
licence: every ring colour is read from the ledger's `license_family`, every
link from its `homepage`, every dashed stroke from its `optional` flag.

The page ships SMALL: index.html carries only the preface, the legend and an
empty graph and table. The ledger itself is written beside the page as
var/html/credits/stack.v1.json (compact) and fetched the first time the
Powered By view opens, with a loading line meanwhile and a plain link to the
file for a reader without script. Visitors who never open the view never
download the 1900-odd credits.

The graph is deliberately flat: Tillandsias at the top, one edge to each
cluster (a container image, the Rust workspace, the models, the studios, the
bundled docs, the external services), and inside each cluster one small ring
per dependency. Containment is the depends-on edge. Transitive Rust crates sit
in their own shelf, collapsed by default. Hovering a ring shows a toast,
selecting it opens an in-place chip with the chain that pulls it in.
"""
import html
import json
import pathlib
from collections import deque
from urllib.parse import urlparse

LEDGER = pathlib.Path(__file__).resolve().parent.parent / "docs/powered-by/stack.v1.json"
DATA_PATH = "credits/stack.v1.json"  # served beside index.html

FAMILIES = [
    # id, label, what it means for a user, css colour
    ("permissive", "Permissive", "MIT, Apache-2.0, BSD, ISC, Zlib and friends: use freely, keep the notice.", "var(--leaf)"),
    ("weak-copyleft", "Weak copyleft", "MPL-2.0, LGPL: changes to that library stay open; your program need not.", "var(--sky)"),
    ("strong-copyleft", "Strong copyleft", "GPL family, like Tillandsias itself: derived works stay under the same terms.", "var(--violet)"),
    ("model", "Model licence", "OpenRAIL family: open weights with use-based restrictions you accept before the download.", "var(--amber)"),
    ("restricted", "Restricted", "Non-commercial, revenue-capped or custom terms: only ever behind an explicit acknowledgement.", "var(--rose)"),
    ("service", "Service", "A network endpoint with its own terms; nothing of it ships in Tillandsias.", "#8fa3b8"),
    ("unknown", "Unknown", "No file in our tree declares it (distro packages carry theirs inside the image). Listed so you can look.", "#5b6672"),
]
FAMILY_COLOUR = {f[0]: f[3] for f in FAMILIES}
LINKS = {
    "static-link": "compiled into a Tillandsias binary",
    "dynamic-link": "loaded by a Tillandsias binary at run time",
    "separate-process": "runs beside Tillandsias as its own process or container, unmodified",
    "container-image": "installed into a container image Tillandsias builds and runs",
    "runtime-download": "downloaded on first use, after you accept its terms",
    "bundled-file": "a file copied into our tree with its upstream licence",
    "service": "an external service we contact",
    "build-stage-only": "a build tool used while making an image; not shipped",
    "unknown": "how it is joined is not declared by any file we read",
}
KIND = {"direct": "a direct dependency of", "direct-build": "a build dependency of", "direct-dev": "a development dependency of",
        "package": "a package installed into", "base-image": "the base image of", "runtime-image": "a runtime image used by",
        "bundled": "a file bundled with", "vendored": "vendored into", "service": "a service contacted by",
        "runtime-download": "downloaded on first use by", "download": "downloaded by", "source-build": "built from source into",
        "plugin": "a plugin of"}


def _cluster_order(components):
    """Rust first, required images, optional images, then the rest."""
    def key(c):
        rank = {"rust-crate": 0, "container-image": 1, "media-models": 2, "studios": 3, "documentation": 4, "services": 5}.get(c["kind"], 6)
        return (rank, 1 if c.get("optional") else 0, c["id"])
    return sorted(components, key=key)


def _load():
    ledger = json.loads(LEDGER.read_text())
    if ledger.get("schema") != "tillandsias-stack/v1":
        raise ValueError("Powered By ledger has an unknown schema: %s" % ledger.get("schema"))
    nodes = {n["id"]: n for n in ledger["nodes"]}
    components = {c["id"]: c for c in ledger["components"]}
    for e in ledger["edges"]:
        if e["from"] not in components and e["from"] not in nodes:
            raise ValueError("Powered By edge from an unknown node: " + e["from"])
    for n in ledger["nodes"]:
        if n["license_family"] not in FAMILY_COLOUR:
            raise ValueError("Powered By has an unknown licence family: " + n["license_family"])
        if n["link"] not in LINKS:
            raise ValueError("Powered By has an unknown link kind: " + n["link"])
    return ledger, nodes, components


def _detail(ledger, nodes, components):
    """Per-node data for the rings, the toast and the chip: the ledger's own fields, the
    shortest chain up to a Tillandsias component, and a reason derived only from the edge
    kind and the component (nothing invented; omitted when not derivable)."""
    parents = {}
    for e in ledger["edges"]:
        parents.setdefault(e["to"], []).append(e)

    def title(i):
        return components[i]["title"] if i in components else nodes[i]["name"] if i in nodes else i

    out = {}
    for nid, n in nodes.items():
        prev, seen, q, top = {}, {nid}, deque([nid]), None
        while q:
            cur = q.popleft()
            if cur in components:
                top = cur
                break
            for e in parents.get(cur, ()):
                if e["from"] not in seen:
                    seen.add(e["from"]); prev[e["from"]] = cur; q.append(e["from"])
        chain = []
        if top:
            cur = top
            while cur != nid:
                chain.append(title(cur)); cur = prev[cur]
        why = sorted({"%s %s" % (KIND[e["kind"]], components[e["from"]]["title"])
                      for e in parents.get(nid, ()) if e["from"] in components and e["kind"] in KIND})
        reason = ""
        if why:
            reason = "It is " + "; ".join(why[:3]) + (" and %d more" % (len(why) - 3) if len(why) > 3 else "") + "."
            if n.get("link_note") and "=" not in n["link_note"]:
                reason += " " + n["link_note"].rstrip(".") + "."
        home = n.get("homepage") or ""
        dom = (urlparse(home).hostname or "") if home.startswith("https://") else ""
        out[nid] = {"n": n["name"], "v": str(n.get("version") or ""), "l": n.get("license") or "unknown",
                    "f": n["license_family"], "k": n["link"], "o": bool(n.get("optional")),
                    "h": home, "d": dom, "w": reason, "c": ["Tillandsias"] + chain,
                    "p": sorted(title(c) for c in n.get("pulled_by", []))}
    return out


def data():
    """The compact payload fetched when the view opens."""
    ledger, nodes, components = _load()
    direct, transitive_rust = {}, []
    for e in ledger["edges"]:
        if e["from"] in components and e["to"] in nodes and not e["kind"].startswith("transitive"):
            cid = "rust" if components[e["from"]]["kind"] == "rust-crate" else e["from"]
            direct.setdefault(cid, {})[e["to"]] = True
    for n in ledger["nodes"]:
        if n["id"].startswith("cargo:") and n["id"] not in direct.get("rust", {}):
            transitive_rust.append(n["id"])
    rust_crates = [c for c in components.values() if c["kind"] == "rust-crate"]
    by_name = lambda ids: sorted(ids, key=lambda i: nodes[i]["name"].lower())
    clusters = [{"id": "rust", "t": "Tillandsias binaries (%d Rust crates)" % len(rust_crates), "o": False,
                 "n": by_name(direct.get("rust", {}))}]
    for c in _cluster_order([c for c in components.values() if c["kind"] != "rust-crate"]):
        members = direct.get(c["id"], {})
        if members:
            clusters.append({"id": c["id"], "t": c["title"], "o": bool(c.get("optional")), "n": by_name(members)})
    snap = ledger.get("snapshot") or {}
    return {
        "schema": "tillandsias-powered-by/v1",
        "ref": snap.get("tag") or snap.get("branch") or (snap.get("commit") or "")[:12] or "unpinned",
        "source": snap.get("source") or "https://github.com/8007342/tillandsias/blob/linux-next/docs/credits/stack.v1.json",
        "fam": {f[0]: [f[1], f[3]] for f in FAMILIES},
        "links": LINKS,
        "clusters": clusters,
        "transitive": by_name(transitive_rust),
        "nodes": _detail(ledger, nodes, components),
    }


def write_data(path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data(), separators=(",", ":"), ensure_ascii=False) + "\n"
    path.write_text(body)
    return len(body.encode())


def render():
    ledger, nodes, components = _load()
    snap = ledger.get("snapshot") or {}
    ref = snap.get("tag") or snap.get("branch") or (snap.get("commit") or "")[:12] or "unpinned"
    fam = ledger["summary"]["license_families"]
    counts = ", ".join("%s %d" % (k.replace("-", " "), v) for k, v in sorted(fam.items(), key=lambda kv: -kv[1]))
    legend = "".join(
        '<li><span class="pb-swatch" style="border-color:%s"></span><b>%s</b> <span>%s</span></li>' % (
            colour, html.escape(label), html.escape(meaning)) for _, label, meaning, colour in FAMILIES)
    source_link = html.escape(snap.get("source") or "https://github.com/8007342/tillandsias/blob/linux-next/docs/credits/stack.v1.json", quote=True)
    total = len(ledger["nodes"])
    return (
        '<section class="view" id="view-powered-by" role="tabpanel" aria-labelledby="nav-powered-by" data-credits="%s">'
        '<div class="pb-wrap"><h2>Powered By</h2>'
        '<p class="pb-lede">Tillandsias is GPL-3.0-or-later and it stands on %d other projects. This page is the honest list: '
        'what we wire in, how it is joined to the program, which licence its author declared, and a link to each one.</p>'
        '<div class="pb-honesty"><h3>Licensing is a mess, so here is what we did</h3>'
        '<ul>'
        '<li><b>Nothing here was typed by hand.</b> A generator in the runtime repository reads <code>cargo metadata</code>, every Containerfile, '
        'the npm lockfiles, the model licence register, the studio registry and the vendored LICENSE texts, and writes the ledger this page is drawn from. '
        'When no source declares a licence the node says <em>unknown</em> rather than a guess.</li>'
        '<li><b>Our own files are checked.</b> A guard in the build refuses any file of ours that declares a licence other than GPL-3.0-or-later, '
        'and any container image that leaves its licence label to its base image (we found our images shipping their base images’ MIT and Apache-2.0 labels as if they were ours; fixed 2026-11-01).</li>'
        '<li><b>Licences pass through to you.</b> Permissive and copyleft components come with the install under their own terms. '
        'Model weights are never shipped: they are downloaded on first use, after you read and accept that model’s licence. '
        'Anything restricted (non-commercial, revenue-capped, custom terms) is only ever offered behind an explicit acknowledgement, and today the ledger lists none.</li>'
        '<li><b>The ledger is the record.</b> <a href="%s" target="_blank" rel="noopener">stack.v1.json</a> (snapshot from <code>%s</code>) is machine-readable and regenerated at each stable release. '
        'If we got something wrong, the fix is a pull request against it, not against this page.</li>'
        '</ul></div>'
        '<div class="pb-legend"><p><b>Reading the graph.</b> Tillandsias at the top; one edge to each cluster, dashed when the whole cluster is optional. '
        'Inside, one ring per dependency, coloured by licence family, dashed when that dependency is optional; a faint dotted ring is a build tool that is not shipped. '
        'Containment is the depends-on edge. Hover a ring for its name; select it for its details and the chain that pulls it in. %d nodes: %s.</p><ul>%s</ul></div>'
        '<div id="pb-graph" class="pb-graph" aria-live="polite"><p class="pb-loading" id="pb-loading">Loading the %d credits (about %s)…</p>'
        '<noscript><p class="pb-loading">The graph needs script. The same data is <a href="%s">one JSON file</a>, and the ledger it comes from is on GitHub above.</p></noscript></div>'
        '<div id="pb-toast" class="pb-toast" role="tooltip" hidden></div>'
        '<div id="pb-chip" class="pb-chip" role="dialog" aria-modal="false" aria-labelledby="pb-chip-name" hidden></div>'
        '<h3 id="pb-table-h">Every credit, flat</h3>'
        '<details class="pb-credits"><summary>Show all %d credits as a table</summary>'
        '<p class="pb-table-note">For screen readers and search. Filter by name, licence or family; scroll sideways for every column.</p>'
        '<input type="search" id="pb-filter" class="pb-filter" placeholder="Filter credits…" aria-label="Filter the credits table" aria-controls="pb-table">'
        '<div class="pb-table-wrap"><table id="pb-table" class="pb-table" aria-labelledby="pb-table-h"><thead><tr>'
        '<th>Project</th><th>Version</th><th>Declared licence</th><th>Family</th><th>How we link it</th><th>Need</th><th>Pulled in by</th>'
        '</tr></thead><tbody></tbody></table></div></details>'
        '<p class="pb-foot">Generated from the ledger by <code>scripts/powered_by.py</code>; the ledger by '
        '<a href="https://github.com/8007342/tillandsias/blob/linux-next/scripts/lua/build-stack-ledger.lua" target="_blank" rel="noopener">build-stack-ledger.lua</a>. '
        'No tracking on this page; the only requests are this page’s own data file and the links you choose to follow.</p>'
        '</div></section>' % (
            DATA_PATH, total, source_link, html.escape(ref), total, html.escape(counts), legend,
            total, "%d&nbsp;KB" % (len(json.dumps(data(), separators=(",", ":"))) // 1024), DATA_PATH, total))


CSS = r"""
/* --- Powered By: one flat graph and a flat table, data fetched on open --- */
.pb-wrap{max-width:980px;margin:0 auto;padding:0 16px 40px}
.pb-wrap h2{margin:0 0 8px;font-size:30px;letter-spacing:-.03em}
.pb-lede{color:var(--ink-dim);font-size:16px;line-height:1.55;max-width:70ch}
.pb-honesty{margin:22px 0;padding:16px 18px;border:1px solid var(--line);border-left:3px solid var(--leaf);border-radius:10px;background:var(--panel)}
.pb-honesty h3{margin:0 0 10px;font-size:17px}
.pb-honesty ul{margin:0;padding-left:18px}.pb-honesty li{margin:0 0 8px;color:var(--ink-dim);line-height:1.55;font-size:14px}
.pb-honesty li b,.pb-legend b{color:var(--ink)}
.pb-honesty a,.pb-foot a,.pb-table a,.pb-loading a{color:var(--leaf)}
.pb-legend p{color:var(--ink-dim);font-size:14px;line-height:1.55}
.pb-legend ul{list-style:none;margin:8px 0 16px;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:6px 18px}
.pb-legend li{display:flex;gap:10px;align-items:flex-start;color:var(--ink-faint);font-size:12.5px;line-height:1.45}
.pb-legend li b{display:block;font-size:13px}
.pb-swatch,.pb-dot{flex:none;display:inline-block;width:12px;height:12px;margin-top:3px;border:2.5px solid;border-radius:50%;background:var(--bg-2)}
.pb-dot{width:9px;height:9px;margin:0 6px -1px 0;border-width:2px}
.pb-graph{min-height:120px}
.pb-loading{margin:18px 0;padding:14px 16px;border:1px dashed var(--line-2);border-radius:10px;color:var(--ink-dim);font-size:14px}
.pb-loading.is-error{border-color:var(--rose);color:var(--ink)}
.pb-svg{display:block;width:100%;height:auto;margin:10px 0;overflow:visible}
.pb-svg rect{fill:var(--panel);stroke:var(--line-2);stroke-width:1.2}
.pb-svg .pb-root{fill:var(--ink);font:600 13px var(--sans)}
.pb-svg .pb-cluster-title{fill:var(--ink);font:600 12px var(--sans)}
.pb-svg .pb-cluster-meta{fill:var(--ink-faint);font:10px var(--mono);letter-spacing:.06em;text-transform:uppercase}
.pb-svg .pb-cluster-optional .pb-cluster-title{fill:var(--ink-dim)}
.pb-svg .pb-spine,.pb-svg .pb-edge{fill:none;stroke:#527384;stroke-width:1.8}
.pb-svg .pb-edge-optional{stroke-dasharray:5 4;stroke:#3d5a6a}
.pb-svg .pb-node{cursor:pointer;transition:r .12s ease}
.pb-svg .pb-node:hover,.pb-svg .pb-node:focus,.pb-svg .pb-node.is-open{r:9;fill:var(--line-2)}
.pb-svg .pb-node:focus{outline:none}.pb-svg .pb-node:focus-visible{stroke-width:3.4}
.pb-toast{position:fixed;z-index:60;pointer-events:none;max-width:260px;padding:8px 11px;border:1px solid var(--line-2);border-radius:9px;
 background:var(--panel);color:var(--ink);box-shadow:0 8px 24px rgba(0,0,0,.35);font:12.5px/1.4 var(--sans)}
.pb-toast b{display:block;font-size:13.5px}.pb-toast .pb-meta{color:var(--ink-faint);font:11px var(--mono)}
.pb-badge{display:inline-block;margin:4px 0 2px;padding:1px 8px;border:1.5px solid;border-radius:999px;font:600 10.5px var(--mono);letter-spacing:.04em}
.pb-toast .pb-k{display:block;color:var(--ink-dim)}
.pb-chip{position:absolute;z-index:55;width:min(340px,calc(100vw - 32px));padding:14px 16px 12px;border:1px solid var(--line-2);border-left:4px solid;border-radius:12px;
 background:var(--panel);color:var(--ink);box-shadow:0 14px 40px rgba(0,0,0,.4);font:13px/1.5 var(--sans);animation:pb-pop .14s ease-out}
@keyframes pb-pop{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
.pb-chip-head{display:flex;gap:10px;align-items:center;padding-right:24px}
.pb-chip-head img,.pb-avatar{flex:none;width:32px;height:32px;border-radius:8px;background:var(--bg-2)}
.pb-avatar{display:grid;place-items:center;font:700 16px var(--sans);color:var(--bg);text-transform:uppercase}
.pb-chip h4{margin:0;font-size:15px;line-height:1.25;word-break:break-word}.pb-chip h4 span{color:var(--ink-faint);font:11.5px var(--mono);margin-left:4px}
.pb-chip p{margin:8px 0 0;color:var(--ink-dim)}.pb-chip a{color:var(--leaf)}
.pb-chip dl{margin:8px 0 0;display:grid;grid-template-columns:auto 1fr;gap:3px 10px;font-size:12.5px}
.pb-chip dt{color:var(--ink-faint);font:11px var(--mono);text-transform:uppercase;letter-spacing:.05em;padding-top:2px}.pb-chip dd{margin:0;color:var(--ink-dim);word-break:break-word}
.pb-chain{list-style:none;margin:6px 0 0;padding:0;font:11.5px var(--mono);color:var(--ink-dim)}
.pb-chain li{padding-left:14px;position:relative}.pb-chain li+li:before{content:"\21B3";position:absolute;left:0;color:var(--ink-faint)}
.pb-chain li:last-child{color:var(--ink)}
.pb-chip-x{position:absolute;top:8px;right:8px;width:28px;height:28px;border:0;border-radius:6px;background:transparent;color:var(--ink-dim);font:18px var(--sans);cursor:pointer}
.pb-chip-x:hover,.pb-chip-x:focus-visible{background:var(--bg-2);color:var(--ink)}
.pb-svg-wrap,.pb-trans{position:relative}
.pb-svg-wrap{overflow-x:auto;overscroll-behavior-x:contain}
.pb-credits>summary{cursor:pointer;font-size:14px;padding:6px 0;color:var(--ink-dim)}
.pb-trans{margin:6px 0 24px;color:var(--ink-dim)}.pb-trans summary{cursor:pointer;font-size:14px;padding:6px 0}
.pb-wrap h3#pb-table-h{margin:26px 0 4px;font-size:20px}
.pb-table-note{margin:0 0 10px;color:var(--ink-dim);font-size:13.5px}
.pb-filter{width:100%;max-width:420px;padding:9px 12px;border:1px solid var(--line-2);border-radius:8px;background:var(--bg-2);color:var(--ink);font:14px var(--sans)}
.pb-table-wrap{overflow:auto;max-height:60vh;overscroll-behavior:contain;margin-top:10px;border:1px solid var(--line);border-radius:10px}
.pb-table{width:100%;border-collapse:collapse;font-size:12.5px}
.pb-table th,.pb-table td{white-space:nowrap;padding:6px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.pb-table th{position:sticky;top:0;z-index:1;background:var(--panel);color:var(--ink-dim);font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.08em}
.pb-table td{color:var(--ink-dim)}.pb-table td:first-child{color:var(--ink)}
.pb-table code{font:11.5px var(--mono);color:var(--ink)}
.pb-table tr[hidden]{display:none}
.pb-foot{margin-top:18px;color:var(--ink-faint);font-size:12px;line-height:1.5}
@media(max-width:700px){.pb-wrap{padding-top:44px}.pb-wrap h2{font-size:24px}.pb-svg-wrap .pb-svg,.pb-trans .pb-svg{min-width:720px}.pb-trans{overflow-x:auto}.pb-lede{font-size:15px}.pb-table{font-size:12px}}
@media(prefers-reduced-motion:reduce){.pb-chip{animation:none}.pb-svg .pb-node{transition:none}}
body.is-accessible .pb-table{font-size:15px}body.is-accessible .pb-legend li{font-size:14px}
"""

JS = r"""
(function(){
  var view=document.getElementById('view-powered-by'), graph=document.getElementById('pb-graph');
  if(!view||!graph) return;
  var loaded=false, loading=false;
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}

  /* ---- fetch once, the first time the view is shown ---- */
  function maybeLoad(){
    if(loaded||loading||!view.classList.contains('is-active')) return;
    loading=true;
    var url=view.getAttribute('data-credits'), line=document.getElementById('pb-loading');
    fetch(url,{credentials:'omit'}).then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
      .then(function(D){ loaded=true; render(D); })
      .catch(function(err){
        loading=false;
        if(line){ line.className='pb-loading is-error'; line.innerHTML='The credits could not be loaded ('+esc(err.message)+'). The data is <a href="'+esc(url)+'">one JSON file</a>; reload to try again.'; }
      });
  }
  maybeLoad();
  new MutationObserver(maybeLoad).observe(view,{attributes:true,attributeFilter:['class']});

  /* ---- the graph, drawn from the payload ---- */
  var W=720, LEFT=150, PAD=12, R=6, GAP=16;
  function colour(D,id){ var f=D.fam[D.nodes[id].f]||D.fam.unknown; return f[1]; }
  function ring(D,id,cx,cy){
    var d=D.nodes[id], dash=d.o?' stroke-dasharray="3 2"':'';
    if(d.k==='build-stage-only') dash=' stroke-dasharray="1.5 2.5" opacity=".6"';
    var label=d.n+' '+d.v+', '+d.l+(d.o?' (optional)':'')+(d.k==='build-stage-only'?', not shipped':'');
    return '<circle class="pb-node" data-id="'+esc(id)+'" tabindex="0" role="button" aria-haspopup="dialog" aria-label="'+esc(label)+'"'+
      ' cx="'+cx+'" cy="'+cy+'" r="'+R+'" fill="var(--bg-2)" stroke="'+colour(D,id)+'" stroke-width="2.2"'+dash+'/>';
  }
  function rings(D,ids,x0,y0,width){
    var per=Math.max(1,Math.floor((width-2*R)/GAP)), out=[];
    for(var i=0;i<ids.length;i++){ out.push(ring(D,ids[i],x0+R+(i%per)*GAP,y0+R+Math.floor(i/per)*GAP)); }
    return {svg:out.join(''), h:Math.ceil(ids.length/per)*GAP+2*R};
  }
  function render(D){
    var y=54, parts=[], edges=[], boxes=[], spine=24;
    parts.push('<rect x="'+(W/2-75)+'" y="14" width="150" height="30" rx="8" fill="var(--panel)" stroke="var(--violet)" stroke-width="2.2"/>'+
      '<text x="'+(W/2)+'" y="34" text-anchor="middle" class="pb-root">Tillandsias · GPL-3.0</text><path d="M'+(W/2)+' 44 V50" class="pb-spine"/>');
    D.clusters.forEach(function(cl){
      var r=rings(D,cl.n,LEFT+PAD,y+30,W-LEFT-2*PAD), h=r.h+42;
      edges.push('<path d="M'+spine+' 50 V'+(y+20)+' H'+LEFT+'" class="pb-edge'+(cl.o?' pb-edge-optional':'')+'"/>');
      boxes.push('<g class="pb-cluster'+(cl.o?' pb-cluster-optional':'')+'"><rect x="'+LEFT+'" y="'+y+'" width="'+(W-LEFT-4)+'" height="'+h+'" rx="10"'+(cl.o?' stroke-dasharray="6 4"':'')+'/>'+
        '<text x="'+(LEFT+PAD)+'" y="'+(y+18)+'" class="pb-cluster-title">'+esc(cl.t)+'</text>'+
        '<text x="'+(LEFT+PAD)+'" y="'+(y+h-10)+'" class="pb-cluster-meta">'+cl.n.length+' · '+(cl.o?'optional':'required')+'</text>'+r.svg+'</g>');
      y+=h+14;
    });
    parts.push('<path d="M'+spine+' 50 H'+(W/2)+'" class="pb-spine"/>');
    var t=rings(D,D.transitive,LEFT+PAD,30,W-LEFT-2*PAD);
    graph.innerHTML='<div class="pb-svg-wrap"><svg viewBox="0 0 '+W+' '+y+'" class="pb-svg" role="img" aria-label="Tillandsias and the clusters of software it depends on">'+
        parts.join('')+edges.join('')+boxes.join('')+'</svg></div>'+
      '<details class="pb-trans"><summary>Show the '+D.transitive.length+' Rust crates pulled in transitively</summary>'+
        '<svg viewBox="0 0 '+W+' '+(t.h+42)+'" class="pb-svg" role="img" aria-label="Transitive Rust crates"><rect x="'+LEFT+'" y="0" width="'+(W-LEFT-4)+'" height="'+(t.h+40)+'" rx="10" stroke-dasharray="2 4"/>'+
        '<text x="'+(LEFT+PAD)+'" y="18" class="pb-cluster-title">Pulled in transitively by the crates above ('+D.transitive.length+')</text>'+t.svg+'</svg></details>';
    renderTable(D); wireToast(D);
  }

  /* ---- the flat table ---- */
  function renderTable(D){
    var tb=document.querySelector('#pb-table tbody'); if(!tb) return;
    var ids=Object.keys(D.nodes).sort(function(a,b){ var x=D.nodes[a], y=D.nodes[b]; return x.f===y.f ? x.n.toLowerCase().localeCompare(y.n.toLowerCase()) : x.f.localeCompare(y.f); });
    var rows=ids.map(function(id){ var d=D.nodes[id], f=D.fam[d.f]||D.fam.unknown;
      var name=d.h?'<a href="'+esc(d.h)+'" target="_blank" rel="noopener">'+esc(d.n)+'</a>':esc(d.n);
      var need=d.k==='build-stage-only'?'not shipped':(d.o?'optional':'required');
      return '<tr><td>'+name+'</td><td>'+esc(d.v)+'</td><td><code>'+esc(d.l)+'</code></td><td><span class="pb-dot" style="border-color:'+f[1]+'"></span>'+esc(d.f.replace(/-/g,' '))+'</td>'+
        '<td>'+esc(D.links[d.k]||d.k)+'</td><td>'+need+'</td><td>'+esc(d.p.join(', '))+'</td></tr>'; });
    tb.innerHTML=rows.join('');
    var box=document.getElementById('pb-filter'), trs=[].slice.call(tb.rows), tm;
    if(box) box.addEventListener('input',function(){ clearTimeout(tm); tm=setTimeout(function(){ var q=box.value.trim().toLowerCase();
      trs.forEach(function(r){ r.hidden = q!=='' && r.textContent.toLowerCase().indexOf(q)===-1; }); },80); });
  }

  /* ---- hover toast and click chip ---- */
  function wireToast(D){
    var toast=document.getElementById('pb-toast'), chip=document.getElementById('pb-chip'), N=D.nodes, F=D.fam, openNode=null;
    function fam(d){return F[d.f]||F.unknown;}
    function badge(d){var f=fam(d);return '<span class="pb-badge" style="border-color:'+f[1]+';color:'+f[1]+'">'+esc(f[0])+'</span>';}
    function kind(d){return (D.links[d.k]||d.k)+(d.o?' (optional)':'');}
    function showToast(c){
      var d=N[c.getAttribute('data-id')]; if(!d) return;
      toast.innerHTML='<b>'+esc(d.n)+'</b><span class="pb-meta">'+esc(d.v?'v'+d.v+' · ':'')+esc(d.l)+'</span><br>'+badge(d)+
        '<span class="pb-k">'+esc(kind(d))+'</span>'+(d.p.length?'<span class="pb-meta">'+esc(d.p.slice(0,4).join(', '))+'</span>':'');
      toast.hidden=false;
      var r=c.getBoundingClientRect(), tw=toast.offsetWidth, th=toast.offsetHeight, x=r.right+14, y=r.top-th-10;
      if(x+tw>innerWidth-8) x=r.left-tw-14;
      if(x<8) x=Math.max(8,Math.min(innerWidth-tw-8,r.left));
      if(y<8) y=r.bottom+12;
      toast.style.left=x+'px'; toast.style.top=y+'px';
    }
    function hideToast(){toast.hidden=true;}
    function avatar(d){var f=fam(d);return '<span class="pb-avatar" style="background:'+f[1]+'" aria-hidden="true">'+esc((d.n.replace(/^[^a-z0-9]+/i,'')[0]||'?'))+'</span>';}
    function closeChip(focusBack){
      if(!openNode) return; chip.hidden=true; openNode.classList.remove('is-open');
      var n=openNode; openNode=null; if(focusBack) n.focus();
    }
    function openChip(c){
      var d=N[c.getAttribute('data-id')]; if(!d) return;
      if(openNode===c){closeChip(true);return;}
      closeChip(false); hideToast(); openNode=c; c.classList.add('is-open');
      var f=fam(d), logo=d.d?'<img src="https://'+esc(d.d)+'/favicon.ico" alt="" width="32" height="32" loading="lazy" referrerpolicy="no-referrer">':'';
      chip.style.borderLeftColor=f[1];
      chip.innerHTML='<button type="button" class="pb-chip-x" aria-label="Close">×</button>'+
        '<div class="pb-chip-head">'+(logo||avatar(d))+'<h4 id="pb-chip-name">'+esc(d.n)+(d.v?'<span>'+esc(d.v)+'</span>':'')+'</h4></div>'+
        (d.w?'<p>'+esc(d.w)+'</p>':'')+
        '<dl><dt>Licence</dt><dd><code>'+esc(d.l)+'</code> '+badge(d)+'</dd>'+
        '<dt>Linked</dt><dd>'+esc(kind(d))+'</dd>'+
        (d.h?'<dt>Site</dt><dd><a href="'+esc(d.h)+'" target="_blank" rel="noopener">'+esc(d.h.replace(/^https?:\/\//,''))+'</a></dd>':'')+'</dl>'+
        (d.c.length>1?'<p><b>Why it is here</b></p><ol class="pb-chain">'+d.c.concat([d.n]).map(function(s){return '<li>'+esc(s)+'</li>';}).join('')+'</ol>':'');
      var img=chip.querySelector('.pb-chip-head img');
      if(img) img.onerror=function(){img.outerHTML=avatar(d);};
      var host=c.closest('.pb-svg-wrap,.pb-trans'); host.appendChild(chip); chip.hidden=false;
      var hr=host.getBoundingClientRect(), r=c.getBoundingClientRect(), cw=chip.offsetWidth;
      var x=r.right-hr.left+host.scrollLeft+12, y=r.top-hr.top+host.scrollTop-6, vis=hr.width+host.scrollLeft;
      if(x+cw>vis-4) x=Math.max(host.scrollLeft+4,r.left-hr.left+host.scrollLeft-cw-12);
      chip.style.left=x+'px'; chip.style.top=y+'px';
      chip.querySelector('.pb-chip-x').onclick=function(){closeChip(true);};
      chip.querySelector('.pb-chip-x').focus({preventScroll:true});
    }
    [].forEach.call(graph.querySelectorAll('.pb-svg'),function(s){
      s.addEventListener('mouseover',function(e){if(e.target.classList.contains('pb-node')) showToast(e.target);});
      s.addEventListener('mouseout',function(e){if(e.target.classList.contains('pb-node')) hideToast();});
      s.addEventListener('focusin',function(e){if(e.target.classList.contains('pb-node')) showToast(e.target);});
      s.addEventListener('focusout',hideToast);
      s.addEventListener('click',function(e){if(e.target.classList.contains('pb-node')){e.stopPropagation();openChip(e.target);}});
      s.addEventListener('keydown',function(e){if(e.target.classList.contains('pb-node')&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openChip(e.target);}});
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){hideToast();closeChip(true);}});
    document.addEventListener('click',function(e){if(openNode&&!chip.contains(e.target)) closeChip(false);});
    window.addEventListener('scroll',hideToast,{passive:true});
  }
})();
"""
