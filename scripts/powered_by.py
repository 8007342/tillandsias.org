"""Powered By: the stack ledger as one very simple graph, plus a flat credits table.

The data is docs/powered-by/stack.v1.json, a copy of the runtime's generated
docs/credits/stack.v1.json (scripts/snapshot-stack.py). Nothing here types a
licence: every ring colour is read from the ledger's `license_family`, every
link from its `homepage`, every dashed stroke from its `optional` flag.

The graph is deliberately flat: Tillandsias at the top, one edge to each
cluster (a container image, the Rust workspace, the models, the studios, the
bundled docs, the external services), and inside each cluster one small ring
per dependency. Containment is the depends-on edge. Transitive Rust crates sit
in their own shelf, collapsed by default (a checkbox, no script needed). The
table under the graph carries every node for screen readers and search.
"""
import html
import json
import pathlib

LEDGER = pathlib.Path(__file__).resolve().parent.parent / "docs/powered-by/stack.v1.json"

FAMILIES = [
    # id, label, what it means for a user, css colour var
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
}


def _cluster_order(components):
    """Rust first, required images, optional images, then the rest."""
    def key(c):
        kind = c["kind"]
        rank = {"rust-crate": 0, "container-image": 1, "media-models": 2, "studios": 3, "documentation": 4, "services": 5}.get(kind, 6)
        return (rank, 1 if c.get("optional") else 0, c["id"])
    return sorted(components, key=key)


def _rings(nodes, x0, y0, width, r=6, gap=16):
    """Lay small rings in rows; returns (svg, height)."""
    per_row = max(1, int((width - 2 * r) // gap))
    out = []
    for i, n in enumerate(nodes):
        col, row = i % per_row, i // per_row
        cx, cy = x0 + r + col * gap, y0 + r + row * gap
        colour = FAMILY_COLOUR.get(n["license_family"], FAMILY_COLOUR["unknown"])
        dash = ' stroke-dasharray="3 2"' if n.get("optional") else ""
        label = "%s %s — %s%s — %s" % (n["name"], n.get("version") or "", n.get("license") or "unknown",
                                      " (optional)" if n.get("optional") else "", LINKS.get(n["link"], n["link"]))
        circle = ('<circle cx="%d" cy="%d" r="%d" fill="var(--bg-2)" stroke="%s" stroke-width="2.2"%s>'
                  '<title>%s</title></circle>' % (cx, cy, r, colour, dash, html.escape(label)))
        if n.get("homepage"):
            # the <title> inside the circle is the accessible name; no duplicate aria-label
            circle = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(n["homepage"], quote=True), circle)
        out.append(circle)
    rows = (len(nodes) + per_row - 1) // per_row
    return "".join(out), rows * gap + 2 * r


def render():
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
    snap = ledger.get("snapshot") or {}
    ref = snap.get("tag") or snap.get("branch") or (snap.get("commit") or "")[:12] or "unpinned"

    # Direct membership: a node belongs to the cluster of each component that has a direct
    # (non-transitive) edge to it. Rust crates fold into one cluster; the crates' transitive
    # pulls form a shelf of their own.
    direct = {}
    transitive_rust = {}
    for e in ledger["edges"]:
        if e["from"] in components and e["to"] in nodes:
            if e["kind"].startswith("transitive"):
                continue
            cid = "rust" if components[e["from"]]["kind"] == "rust-crate" else e["from"]
            direct.setdefault(cid, {})[e["to"]] = nodes[e["to"]]
    for n in ledger["nodes"]:
        if n["id"].startswith("cargo:") and n["id"] not in direct.get("rust", {}):
            transitive_rust[n["id"]] = n
    clusters = []
    rust_crates = [c for c in components.values() if c["kind"] == "rust-crate"]
    clusters.append({"id": "rust", "title": "Tillandsias binaries (%d Rust crates)" % len(rust_crates),
                     "optional": False, "nodes": sorted(direct.get("rust", {}).values(), key=lambda n: n["name"].lower()),
                     "note": "the tray, the launcher, the plan tools and the sidecars"})
    for c in _cluster_order([c for c in components.values() if c["kind"] != "rust-crate"]):
        members = sorted(direct.get(c["id"], {}).values(), key=lambda n: n["name"].lower())
        if not members:
            continue
        clusters.append({"id": c["id"], "title": c["title"], "optional": bool(c.get("optional")),
                         "nodes": members, "note": c.get("description", "")})

    # --- the SVG ---------------------------------------------------------------
    W, LEFT, PAD = 720, 150, 12
    y = 54
    parts = ['<rect x="%d" y="14" width="150" height="30" rx="8" fill="var(--panel)" stroke="var(--violet)" stroke-width="2.2"/>'
             '<text x="%d" y="34" text-anchor="middle" class="pb-root">Tillandsias · GPL-3.0</text>' % (W / 2 - 75, W / 2)]
    spine_x = 24
    parts.append('<path d="M%d 44 V%d" class="pb-spine"/>' % (W / 2, 50))
    edge_paths = []
    cluster_svgs = []
    for cl in clusters:
        rings, h = _rings(cl["nodes"], LEFT + PAD, y + 30, W - LEFT - 2 * PAD)
        box_h = h + 42
        dash = ' class="pb-edge pb-edge-optional"' if cl["optional"] else ' class="pb-edge"'
        edge_paths.append('<path d="M%d 50 V%d H%d"%s/>' % (spine_x, y + 20, LEFT, dash))
        cluster_svgs.append(
            '<g class="pb-cluster%s"><rect x="%d" y="%d" width="%d" height="%d" rx="10"%s/>'
            '<text x="%d" y="%d" class="pb-cluster-title">%s</text>'
            '<text x="%d" y="%d" class="pb-cluster-meta">%d · %s</text>%s</g>' % (
                " pb-cluster-optional" if cl["optional"] else "", LEFT, y, W - LEFT - 4, box_h,
                ' stroke-dasharray="6 4"' if cl["optional"] else "", LEFT + PAD, y + 18, html.escape(cl["title"]),
                LEFT + PAD, y + box_h - 10, len(cl["nodes"]), "optional" if cl["optional"] else "required", rings))
        y += box_h + 14
    parts.append('<path d="M%d 50 H%d" class="pb-spine"/>' % (spine_x, W / 2))
    parts.extend(edge_paths)
    parts.extend(cluster_svgs)
    main_h = y
    # transitive shelf
    trans = sorted(transitive_rust.values(), key=lambda n: n["name"].lower())
    trings, th = _rings(trans, LEFT + PAD, 30, W - LEFT - 2 * PAD)
    trans_svg = ('<svg viewBox="0 0 %d %d" class="pb-svg" role="img" aria-label="Transitive Rust crates">'
                 '<rect x="%d" y="0" width="%d" height="%d" rx="10" stroke-dasharray="2 4"/>'
                 '<text x="%d" y="18" class="pb-cluster-title">Pulled in transitively by the crates above (%d)</text>%s</svg>' % (
                     W, th + 42, LEFT, W - LEFT - 4, th + 40, LEFT + PAD, len(trans), trings))

    legend = "".join(
        '<li><span class="pb-swatch" style="border-color:%s"></span><b>%s</b> <span>%s</span></li>' % (
            colour, html.escape(label), html.escape(meaning)) for _, label, meaning, colour in FAMILIES)
    fam = ledger["summary"]["license_families"]
    counts = ", ".join("%s %d" % (k.replace("-", " "), v) for k, v in sorted(fam.items(), key=lambda kv: -kv[1]))

    # --- the table -------------------------------------------------------------
    rows = []
    for n in sorted(ledger["nodes"], key=lambda n: (n["license_family"], n["name"].lower())):
        name = html.escape(n["name"])
        if n.get("homepage"):
            name = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(n["homepage"], quote=True), name)
        pulled = ", ".join(sorted(components[c]["title"] if c in components else c for c in n.get("pulled_by", [])))
        rows.append('<tr data-family="%s"><td>%s</td><td>%s</td><td><code>%s</code></td><td><span class="pb-dot" style="border-color:%s"></span>%s</td>'
                    '<td>%s</td><td>%s</td><td>%s</td></tr>' % (
                        n["license_family"], name, html.escape(str(n.get("version") or "")), html.escape(str(n.get("license") or "unknown")),
                        FAMILY_COLOUR[n["license_family"]], html.escape(n["license_family"].replace("-", " ")),
                        html.escape(LINKS.get(n["link"], n["link"])), "optional" if n.get("optional") else "required", html.escape(pulled)))

    source_link = html.escape(snap.get("source") or "https://github.com/8007342/tillandsias/blob/linux-next/docs/credits/stack.v1.json", quote=True)
    return (
        '<section class="view" id="view-powered-by" role="tabpanel" aria-labelledby="nav-powered-by">'
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
        'Inside, one ring per dependency, coloured by licence family, dashed when that dependency is optional. Containment is the depends-on edge. '
        'Hover or focus a ring for its name; select it to open its homepage. %d nodes: %s.</p><ul>%s</ul></div>'
        '<div class="pb-svg-wrap"><svg viewBox="0 0 %d %d" class="pb-svg" role="img" aria-label="Tillandsias and the clusters of software it depends on">%s</svg></div>'
        '<details class="pb-trans"><summary>Show the %d Rust crates pulled in transitively</summary>%s</details>'
        '<h3 id="pb-table-h">Every credit, flat</h3>'
        '<p class="pb-table-note">The same %d entries as a table, for screen readers and search. Filter by name, licence or family.</p>'
        '<input type="search" id="pb-filter" class="pb-filter" placeholder="Filter credits…" aria-label="Filter the credits table" aria-controls="pb-table">'
        '<div class="pb-table-wrap"><table id="pb-table" class="pb-table" aria-labelledby="pb-table-h"><thead><tr>'
        '<th>Project</th><th>Version</th><th>Declared licence</th><th>Family</th><th>How we link it</th><th>Need</th><th>Pulled in by</th>'
        '</tr></thead><tbody>%s</tbody></table></div>'
        '<p class="pb-foot">Generated from the ledger by <code>scripts/powered_by.py</code>; the ledger by '
        '<a href="https://github.com/8007342/tillandsias/blob/linux-next/scripts/lua/build-stack-ledger.lua" target="_blank" rel="noopener">build-stack-ledger.lua</a>. '
        'No tracking on this page; the only requests are the links you choose to follow.</p>'
        '</div></section>' % (
            len(ledger["nodes"]), source_link, html.escape(ref), len(ledger["nodes"]), html.escape(counts), legend,
            W, main_h, "".join(parts), len(trans), trans_svg, len(ledger["nodes"]), "".join(rows)))


CSS = r"""
/* --- Powered By: one flat graph and a flat table --- */
.pb-wrap{max-width:980px;margin:0 auto;padding:0 16px 40px}
.pb-wrap h2{margin:0 0 8px;font-size:30px;letter-spacing:-.03em}
.pb-lede{color:var(--ink-dim);font-size:16px;line-height:1.55;max-width:70ch}
.pb-honesty{margin:22px 0;padding:16px 18px;border:1px solid var(--line);border-left:3px solid var(--leaf);border-radius:10px;background:var(--panel)}
.pb-honesty h3{margin:0 0 10px;font-size:17px}
.pb-honesty ul{margin:0;padding-left:18px}.pb-honesty li{margin:0 0 8px;color:var(--ink-dim);line-height:1.55;font-size:14px}
.pb-honesty li b,.pb-legend b{color:var(--ink)}
.pb-honesty a,.pb-foot a,.pb-table a{color:var(--leaf)}
.pb-legend p{color:var(--ink-dim);font-size:14px;line-height:1.55}
.pb-legend ul{list-style:none;margin:8px 0 16px;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:6px 18px}
.pb-legend li{display:flex;gap:10px;align-items:flex-start;color:var(--ink-faint);font-size:12.5px;line-height:1.45}
.pb-legend li b{display:block;font-size:13px}
.pb-swatch,.pb-dot{flex:none;display:inline-block;width:12px;height:12px;margin-top:3px;border:2.5px solid;border-radius:50%;background:var(--bg-2)}
.pb-dot{width:9px;height:9px;margin:0 6px -1px 0;border-width:2px}
.pb-svg{display:block;width:100%;height:auto;margin:10px 0;overflow:visible}
.pb-svg rect{fill:var(--panel);stroke:var(--line-2);stroke-width:1.2}
.pb-svg .pb-root{fill:var(--ink);font:600 13px var(--sans)}
.pb-svg .pb-cluster-title{fill:var(--ink);font:600 12px var(--sans)}
.pb-svg .pb-cluster-meta{fill:var(--ink-faint);font:10px var(--mono);letter-spacing:.06em;text-transform:uppercase}
.pb-svg .pb-cluster-optional .pb-cluster-title{fill:var(--ink-dim)}
.pb-svg .pb-spine,.pb-svg .pb-edge{fill:none;stroke:#527384;stroke-width:1.8}
.pb-svg .pb-edge-optional{stroke-dasharray:5 4;stroke:#3d5a6a}
.pb-svg a circle{cursor:pointer;transition:r .12s ease}
.pb-svg a:hover circle,.pb-svg a:focus circle{r:9;fill:var(--line-2)}
.pb-svg a:focus{outline:none}
.pb-trans{margin:6px 0 24px;color:var(--ink-dim)}.pb-trans summary{cursor:pointer;font-size:14px;padding:6px 0}
.pb-wrap h3#pb-table-h{margin:26px 0 4px;font-size:20px}
.pb-table-note{margin:0 0 10px;color:var(--ink-dim);font-size:13.5px}
.pb-filter{width:100%;max-width:420px;padding:9px 12px;border:1px solid var(--line-2);border-radius:8px;background:var(--bg-2);color:var(--ink);font:14px var(--sans)}
.pb-table-wrap{overflow-x:auto;margin-top:10px;border:1px solid var(--line);border-radius:10px}
.pb-table{width:100%;border-collapse:collapse;font-size:12.5px}
.pb-table th,.pb-table td{padding:6px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.pb-table th{position:sticky;top:0;background:var(--panel);color:var(--ink-dim);font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.08em}
.pb-table td{color:var(--ink-dim)}.pb-table td:first-child{color:var(--ink);white-space:nowrap}
.pb-table code{font:11.5px var(--mono);color:var(--ink)}
.pb-table tr[hidden]{display:none}
.pb-foot{margin-top:18px;color:var(--ink-faint);font-size:12px;line-height:1.5}
.pb-svg-wrap{overflow-x:auto;overscroll-behavior-x:contain}
@media(max-width:700px){.pb-wrap{padding-top:44px}.pb-wrap h2{font-size:24px}.pb-svg-wrap .pb-svg,.pb-trans .pb-svg{min-width:720px}.pb-trans{overflow-x:auto}.pb-lede{font-size:15px}.pb-table{font-size:12px}.pb-table td:last-child{max-width:160px}}
body.is-accessible .pb-table{font-size:15px}body.is-accessible .pb-legend li{font-size:14px}
"""

JS = r"""
(function(){
  var box=document.getElementById('pb-filter'), table=document.getElementById('pb-table');
  if(!box||!table) return;
  var rows=[].slice.call(table.tBodies[0].rows), t;
  box.addEventListener('input', function(){
    clearTimeout(t);
    t=setTimeout(function(){
      var q=box.value.trim().toLowerCase();
      rows.forEach(function(r){
        r.hidden = q!=='' && r.textContent.toLowerCase().indexOf(q)===-1;
      });
    }, 80);
  });
})();
"""
