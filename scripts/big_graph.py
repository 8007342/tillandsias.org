"""A source-linked goal-state system map with left-to-right journeys."""
import html
import json
import pathlib

BASE = "https://github.com/8007342/tillandsias/blob/{tag}/openspec/specs/{slug}/spec.md"

# id, lane, column, row, title, current state, concise role, expanded explanation, specs
NODES = [
    ("person", "host", 0, 0, "Operator", "implemented", "Chooses project, model and permissions.", "The person starts or tears down a local region, grants host access, reviews changes and owns the external account. A website checkout does not give the agent host authority by itself.", "app-lifecycle"),
    ("host", "host", 1, 0, "Host orchestrator", "partial", "Creates and supervises the region.", "The tray and headless controller provision networks, containers, routes and lifecycle. They bridge host privileges to the runtime; this is a trust boundary, not a container inside the enclave.", "podman-orchestration"),
    ("keychain", "host", 1, 2, "Host keychain", "partial", "Protects the Vault unseal material.", "The host credential store is intended to own the unseal key. Guest and cache copies and reset verification remain relevant limits; keychain isolation is not equivalent to an uncompromised host.", "tillandsias-vault"),
    ("browser", "host", 6, 1, "Personal browser", "implemented", "Operator-facing application.", "The personal browser is outside the enclave. Opening a local preview crosses a route from host to project web service; arbitrary host browsing is not the agent's browser capability.", "host-browser-mcp"),
    ("kernel", "host", 1, 1, "Kernel / VM boundary", "partial", "Linux host or Linux guest.", "On Linux, rootless containers share the host kernel. macOS and Windows use a Linux VM (Windows via WSL2). The VM is a boundary with host integrations, not a guarantee against host compromise.", "podman-orchestration"),
    ("github", "external", 7, 0, "GitHub remote", "implemented", "Durable upstream refs and release source.", "The mirror pushes accepted refs outward. Remote acceptance, not a local commit, establishes that this example's work survived the disposable forge. GitHub and its credentials remain external dependencies.", "git-mirror-service"),
    ("checkout", "forge", 2, 0, "tillandsias.org checkout", "implemented", "Project files mounted in the forge.", "Example path: this website source checkout enters a project forge. The agent edits scripts, OpenSpec changes and generated HTML, runs the checked build, then commits and pushes. The source tree and the generated site have different roles.", "forge-as-only-runtime"),
    ("agent", "forge", 3, 0, "Agent + tool process", "implemented", "Reads, edits, runs commands and tests.", "The coding agent lives in the forge container with scoped project and tool access. It can observe its checkout and invoke project commands. Its prompt and tool outputs are untrusted data with respect to host authority.", "forge-as-only-runtime"),
    ("forgefs", "forge", 3, 1, "Forge writable layer", "implemented", "Disposable tool and process state.", "The rootless forge has an image, writable container layer, project mount and cache mounts. Recreating it discards container-local state; only explicitly durable mounts and pushed git refs should be treated as surviving.", "default-image"),
    ("projectfs", "forge", 4, 1, "Project / worktree mount", "partial", "Source tree and generated page.", "The website checkout is the working tree, including docs, scripts, OpenSpec files and var/html output. Mount policy is a filesystem boundary; a writable mount permits file changes and does not authenticate those changes.", "forge-as-only-runtime"),
    ("cache", "forge", 6, 2, "Cache volumes", "partial", "Models and build caches across rebuilds.", "Caches can outlive a forge or VM. Survival is useful for model downloads but complicates reset, credential cleanup and provenance. Mac cache migration and end-to-end rebuild evidence are incomplete.", "forge-cache-architecture"),
    ("commit", "forge", 4, 0, "Commit + local push", "implemented", "Transparent history from the checkout.", "The agent commits the reviewed website diff and pushes to the local git mirror. A checked build can gate the generated output. A commit is a record of edits, not proof of security or upstream delivery.", "git-mirror-service"),
    ("network", "enclave", 3, 2, "Private enclave network", "partial", "Rootless siblings share internal DNS.", "The desired network has no direct route to the internet. Shell creation paths use Podman's internal network flag, while the Rust path's gate is file-scoped. Membership is reachability, not identity or mutual authentication.", "podman-orchestration"),
    ("proxy", "enclave", 6, 0, "Egress proxy", "partial", "One policy-controlled exit.", "HTTP egress should flow through allowlist and policy checks. A permissive listener is loopback-bound, but namespace and alternate-path gaps remain. The proxy is a chokepoint only if every launch and route actually uses it.", "proxy-container"),
    ("mirror", "enclave", 5, 0, "Git mirror", "partial", "Local git receiver and upstream relay.", "The forge pushes to a local sibling; the mirror holds the upstream credential and relays refs to GitHub. Agent-facing push is anonymous within the enclave, so network membership remains a material trust assumption.", "git-mirror-service"),
    ("vault", "enclave", 4, 2, "Vault service", "partial", "Scoped secrets for sibling services.", "Vault should release only the credential needed by a service after unseal. Host keychain, guest copies and reset paths define the true secret boundary. A compromised sibling can still exercise whatever token it receives.", "tillandsias-vault"),
    ("inference", "enclave", 5, 2, "Local inference", "partial", "Model service near the forge.", "A pinned, digest-checked engine may run locally; readiness remains best effort. The desired router chooses usable host CPU/GPU/NPU lanes from measured capabilities, rather than inferring safety or performance from device presence.", "inference-engine-slots"),
    ("web", "enclave", 5, 1, "Project web sibling", "partial", "Serves generated website preview.", "The website's var/html output is served by a sibling httpd and routed to the host browser. Document root, dotfile handling and lifecycle rules remain incomplete; the web service should never imply that the checkout itself is safely public.", "web-image"),
    ("rootless", "boundary", 2, 1, "Rootless container boundary", "partial", "User namespace, mounts, caps and labels.", "Containers separate processes and files under a non-root identity. Every launch path must apply checked settings; several raw paths do not yet share the validator. Linux forge SELinux/MCS confinement is a desired future boundary.", "podman-orchestration"),
    ("certs", "boundary", 3, 3, "Local CA + certificates", "partial", "TLS trust for proxy and local routes.", "A persistent local CA key, trust distribution and service certificates define where TLS terminates. Current parent-directory creation is not private by construction. Trusting a CA expands authority; it does not authenticate every enclave peer.", "certificate-authority"),
    ("wire", "boundary", 2, 2, "Encrypted control wire", "partial", "Protects host-to-runtime control traffic.", "The secure setting defaults on, but an explicit plaintext override and release-key limits remain. Channel encryption does not establish container isolation or the integrity of downloaded artifacts.", "host-guest-transport"),
    ("supply", "boundary", 5, 3, "Artifact provenance", "partial", "Verify images, installers and releases.", "Desired state: signed release artifacts and ordinary-install signature verification across platforms. Current signing is uneven; ordinary install can proceed without a checksum and does not verify a cosign bundle.", "binary-signing"),
    ("policy", "boundary", 4, 3, "Policy / allowlists", "partial", "Gate tools, routes and egress.", "Filesystem, browser and network allowlists should be checked at their actual invocation sites. A rule in a spec or shell test is not enforcement if a separate launch path bypasses it.", "proxy-container"),
    ("audit", "boundary", 6, 3, "Audit and evidence", "partial", "Tie claims to requirements and checks.", "Stable requirement IDs and model property checks exist in part. The website's source-linked levels and findings record are an audit layer, not live telemetry or proof of all runtime validators.", "spec-traceability"),
    ("install", "lifecycle", 0, 4, "Install / update", "partial", "Fetch, verify and provision.", "A stable installer sets up the application and can reset local state by default. Goal state verifies artifact provenance before execution, then records the exact release that produced the runtime and website claims.", "app-lifecycle"),
    ("create", "lifecycle", 1, 4, "Create project region", "partial", "Provision VM, network and services.", "The orchestrator starts the Linux runtime where needed, creates internal networking and shared siblings, then launches the project forge. Startup order and failure rollback matter: half-created siblings must not silently weaken the boundary.", "podman-orchestration"),
    ("edit", "lifecycle", 2, 4, "Edit → test → build", "implemented", "Run project checks in the forge.", "For tillandsias.org the agent changes source and OpenSpec records, rebuilds var/html/index.html, validates findings and checks release-pinned citations. Those checks establish source consistency, not live deployment behavior.", "forge-as-only-runtime"),
    ("publish", "lifecycle", 3, 4, "Push → publish", "partial", "Mirror upstream, serve preview, deploy.", "The local mirror relays git refs to GitHub; the site deploy path consumes the pushed repository. The preview sibling is separate from the public site. A successful local push without upstream is only local durability.", "git-mirror-service"),
    ("teardown", "lifecycle", 4, 4, "Stop / teardown", "partial", "Remove disposable state safely.", "The forge may be replaced without erasing pushed refs or intentionally persistent caches. Reset must also clear credentials and routes; app reset refuses incomplete host cleanup, while a Linux clean-room path still treats failed probes as best effort.", "app-lifecycle"),
    ("rebuild", "lifecycle", 5, 4, "Rebuild / recover", "partial", "Rehydrate from remote and durable layers.", "A new forge checks out upstream refs, mounts approved caches and recreates siblings. Recovery is not complete if a model cache or secret survives in an undocumented place, or if an unpushed commit was mistaken for durable work.", "forge-cache-architecture"),
    ("spec", "method", 0, 5, "OpenSpec requirements", "implemented", "Describe intended behavior.", "Canonical runtime specs and site delta specs describe the goal state. 'Active' is a document status; checklist completion and runtime verification are separate axes. The Progress ledger links the complete pinned inventory.", "spec-traceability"),
    ("plan", "method", 1, 5, "Plan / obligations", "partial", "Turn requirements into checkable work.", "The plan and obligation model track relationships between requirements, implementation and checks. The currently checked model is narrower than all live validators; a single score cannot honestly stand for the whole application.", "spec-traceability"),
    ("tests", "method", 2, 5, "Checks + source evidence", "partial", "Build, tests and citations.", "Static source checks, property tests and platform tests cover different claims. The website checked build validates quoted targets, while platform and public deployment behavior require separate tests. Failed evidence must remain visible.", "spec-traceability"),
    ("ledger", "method", 3, 5, "Website accountability ledger", "implemented", "Found, tracked and resolved findings.", "The append-only issue fragments fold into three columns with history and evidence. The spec inventory and archived change checklists add context, but none of these counts is a full completion score.", "spec-traceability"),
    ("score", "method", 4, 5, "Cross-release score", "goal", "Comparable convergence measure.", "A complete, comparable application-wide score is a goal, not a published result. The local obligation score covers a bounded model and a broken regime cannot be compared across releases without reconciling its denominator.", "spec-traceability"),
    ("review", "method", 5, 5, "Security review loop", "goal", "Challenge every boundary and revise.", "Review traces each threat to a concrete enforcement point and test. A finding can move backward when evidence falsifies a prior result; preserving that history is more honest than claiming monotonic green counts.", "spec-traceability"),
]

EDGES = [
    ("person", "host", "starts", "control"), ("host", "checkout", "attaches project", "control"),
    ("host", "kernel", "provisions", "control"),
    ("host", "keychain", "unseals", "secret"), ("host", "network", "creates", "control"),
    ("host", "browser", "opens preview", "web"), ("web", "browser", "preview response", "web"),
    ("checkout", "agent", "read/write", "file"), ("agent", "forgefs", "tools", "file"),
    ("agent", "projectfs", "edits", "file"), ("forgefs", "cache", "mounts", "file"),
    ("projectfs", "web", "generated output", "web"), ("agent", "commit", "commit", "git"),
    ("commit", "mirror", "push", "git"),
    ("vault", "mirror", "scoped token", "secret"), ("keychain", "vault", "unseal chain", "secret"),
    ("mirror", "proxy", "HTTPS", "network"), ("proxy", "github", "allowlisted", "network"),
    ("agent", "inference", "model request", "network"), ("agent", "proxy", "egress", "network"),
    ("network", "rootless", "isolation", "boundary"), ("proxy", "policy", "allowlist", "boundary"),
    ("certs", "proxy", "TLS trust", "boundary"), ("host", "wire", "control", "boundary"),
    ("install", "create", "boot", "lifecycle"), ("create", "edit", "attach", "lifecycle"),
    ("edit", "publish", "verified diff", "lifecycle"), ("publish", "teardown", "finish", "lifecycle"),
    ("teardown", "rebuild", "recover", "lifecycle"), ("rebuild", "checkout", "clone", "lifecycle"),
    ("spec", "plan", "refine", "method"), ("plan", "tests", "prove", "method"),
    ("tests", "ledger", "record", "method"), ("ledger", "score", "aggregate", "method"),
    ("score", "review", "challenge", "method"), ("review", "spec", "revise", "method"),
]

LANES = [("host", "Host and external account"), ("forge", "Project forge and filesystem"),
         ("enclave", "Shared enclave services"), ("boundary", "Security boundaries"),
         ("lifecycle", "Lifecycle events"), ("method", "Requirements and evidence")]

BANDS = [
    ("Build and publish", "Operator → forge → git mirror → guarded exit → GitHub"),
    ("Preview and files", "Runtime boundary → mounted output → web sibling → browser"),
    ("Internal services", "Host keys → control wire → enclave → secrets, inference and cache"),
    ("Security review", "Certificates, policy, provenance and evidence support the flows above"),
    ("Lifecycle", "Install → create → edit → publish → teardown → rebuild"),
    ("Accountability", "Requirements → obligations → checks → ledger → score → review"),
]


def render(tag):
    catalog = json.loads((pathlib.Path(__file__).resolve().parent.parent /
                          "docs/progress/runtime-specs.json").read_text())
    if catalog["tag"] != tag:
        raise ValueError("Big Graph spec sources do not match the website pin")
    valid_specs = {s["id"] for s in catalog["specs"]}
    ids = [n[0] for n in NODES]
    if len(ids) != len(set(ids)):
        raise ValueError("Big Graph has duplicate component IDs")
    if len({(n[2], n[3]) for n in NODES}) != len(NODES):
        raise ValueError("Big Graph has overlapping component positions")
    if max(n[3] for n in NODES) + 1 != len(BANDS):
        raise ValueError("Big Graph rows do not match their labels")
    for n in NODES:
        if n[5] not in ("implemented", "partial", "goal"):
            raise ValueError("Big Graph has an unknown current-state label: " + n[0])
        for slug in n[-1].split():
            if slug not in valid_specs:
                raise ValueError("Big Graph source is absent at %s: %s" % (tag, slug))
    for source, target, _, _ in EDGES:
        if source not in ids or target not in ids:
            raise ValueError("Big Graph edge has a missing component")
    positions = {n[0]: (n[2], n[3]) for n in NODES}
    pairs = {(e[0], e[1]) for e in EDGES}
    for flow in (("person", "host", "checkout", "agent", "commit", "mirror", "proxy", "github"),
                 ("projectfs", "web", "browser"),
                 ("install", "create", "edit", "publish", "teardown", "rebuild"),
                 ("spec", "plan", "tests", "ledger", "score", "review")):
        for source, target in zip(flow, flow[1:]):
            if (source, target) not in pairs or positions[source][0] >= positions[target][0] or positions[source][1] != positions[target][1]:
                raise ValueError("Big Graph primary journey must flow left to right: %s → %s" % (source, target))
    cards = []
    data = []
    for id_, lane, col, row, title, status, short, long, specs in NODES:
        refs = [BASE.format(tag=tag, slug=s) for s in specs.split()]
        data.append(dict(id=id_, lane=lane, x=col, y=row, title=title, status=status,
                         short=short, detail=long, specs=refs))
        cards.append('<button type="button" class="graph-node status-%s" id="graph-%s" '
                     'data-node="%s" data-lane="%s" aria-label="%s: %s. Open details">'
                     '<span class="graph-node-top"><small>%s</small><small>%s</small></span>'
                     '<strong>%s</strong><span class="graph-short">%s</span></button>' %
                     tuple(html.escape(str(v), quote=True) for v in
                           (status, id_, id_, lane, title, status, lane, status, title, short)))
    chips = ''.join('<button type="button" class="graph-lane-toggle" data-toggle-lane="%s" '
                    'aria-pressed="true">%s</button>' % (id_, title) for id_, title in LANES)
    bands = ''.join('<div class="graph-band" data-band="%d"><span>%02d · %s</span>'
                    '<small>%s</small></div>' %
                    (i, i + 1, html.escape(title), html.escape(note))
                    for i, (title, note) in enumerate(BANDS))
    return ('<section class="view" id="view-big-graph" role="tabpanel" aria-labelledby="nav-big-graph">'
            '<div class="graph-head"><div class="graph-title"><h2>Big Graph</h2>'
            '<p>The desired architecture of a tillandsias.org checkout inside a forge. '
            'Follow the main flows left to right; scroll to explore and select a component for its sources.</p></div>'
            '<p class="graph-honesty"><b>Reading key:</b> solid green = implemented at the pinned '
            'release; amber dashed = partial; gray dotted = goal only. These are editorial '
            'assessments from the <a href="https://github.com/8007342/tillandsias.org/blob/main/docs/audit/2026-09-22-v56.9.21.1.md" '
            'target="_blank" rel="noopener">stable audit</a>, not runtime telemetry. '
            'Edges show intended interactions; they do not prove enforcement.</p>'
            '<div class="graph-lanes" role="group" aria-label="Show or hide system layers">%s</div>'
            '</div><div class="graph-shell"><div class="graph-viewport" id="graph-viewport" '
            'aria-label="Scrollable architecture graph"><div class="graph-canvas" id="graph-canvas">'
            '%s<svg id="graph-lines" aria-hidden="true"></svg>%s</div></div>'
            '<aside class="graph-inspector" id="graph-inspector" aria-live="polite" hidden>'
            '<button type="button" class="graph-inspector-close" id="graph-inspector-close" '
            'aria-label="Close component details">×</button><div id="graph-inspector-body"></div></aside></div>'
            '<script type="application/json" id="graph-data">%s</script></section>' %
            (chips, bands, ''.join(cards), json.dumps({"nodes": data, "edges": EDGES}).replace("<", "\\u003c")))


CSS = r"""
/* --- Big Graph: a full-viewport, scrollable system map --- */
body.is-graphing{overflow:hidden}
body.is-graphing footer{display:none}
#view-big-graph.is-active{position:fixed;inset:0;z-index:2;display:flex;flex-direction:column;background:var(--bg);overflow:hidden}
.graph-head{flex:none;padding:12px 20px 10px 66px;border-bottom:1px solid var(--line);background:#0a0f15}
.graph-title{display:flex;align-items:baseline;gap:20px}
.graph-title h2{flex:none;margin:0;font-size:27px;line-height:1.2;letter-spacing:-.03em}
.graph-title p{margin:0;max-width:80ch;color:var(--ink-dim);font-size:12.5px;line-height:1.4}
.graph-honesty{margin:5px 0 0;color:var(--ink-faint);font-size:11.5px;line-height:1.4}
.graph-honesty a,.graph-inspector a{color:var(--leaf)}
.graph-lanes{display:flex;align-items:center;gap:6px;margin-top:8px;overflow-x:auto;white-space:nowrap;scrollbar-width:thin}
.graph-lane-toggle{flex:none;border:1px solid var(--line-2);background:var(--panel);color:var(--ink-dim);border-radius:6px;cursor:pointer;padding:5px 9px;font:500 11px var(--sans)}
.graph-lane-toggle:hover{border-color:var(--leaf);color:var(--ink)}
.graph-lane-toggle[aria-pressed="false"]{opacity:.43;text-decoration:line-through}
.graph-shell{position:relative;flex:1;min-height:0;min-width:0}
.graph-viewport{width:100%;height:100%;overflow:auto;overscroll-behavior:contain;background:radial-gradient(circle at 1px 1px,#202b38 1px,transparent 0) 0 0/24px 24px,#0a0e13}
.graph-canvas{position:relative;min-width:100%;min-height:100%}
.graph-band{position:absolute;left:0;right:0;height:210px;padding:8px 12px;border-top:1px solid #263442;background:linear-gradient(180deg,#14212b44,transparent 65%);pointer-events:none;z-index:0}
.graph-band span{display:block;color:#8fb8cb;font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.12em}
.graph-band small{display:block;margin-top:3px;max-width:150px;color:var(--ink-faint);font:10px/1.4 var(--sans)}
#graph-lines{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:1}
#graph-lines path{fill:none;stroke:#527384;stroke-width:2;opacity:.7;marker-end:url(#graph-arrow)}
#graph-lines path.edge-secret{stroke:#a48bf0}#graph-lines path.edge-git{stroke:#5fd6a4}
#graph-lines path.edge-boundary{stroke:#e6b45e;stroke-dasharray:5 5}
#graph-lines path.edge-goal{stroke:#777;stroke-dasharray:4 7}
.graph-node{position:absolute;width:260px;min-height:126px;padding:12px 14px;text-align:left;color:var(--ink);background:#111b24;border:1px solid var(--leaf-dim);border-left:4px solid var(--leaf);border-radius:10px;box-shadow:0 8px 26px #0008;cursor:pointer;font:400 12px/1.4 var(--sans);z-index:2}
.graph-node:hover,.graph-node:focus-visible,.graph-node.is-selected{outline:2px solid var(--sky);outline-offset:2px;z-index:3}
.graph-node.status-partial{border-color:#866a3d;border-left-color:var(--amber);border-style:dashed;background:#1b1a17}
.graph-node.status-goal{border-color:#4c535b;border-left-color:#87909b;border-style:dotted;background:#16191d;color:#b0bac4}
.graph-node-top{display:flex;justify-content:space-between;gap:8px;text-transform:uppercase;letter-spacing:.11em;color:var(--ink-faint);font:600 10px var(--mono)}
.graph-node strong{display:block;font-size:15px;line-height:1.25;margin:8px 0 5px}
.graph-short{display:block;color:var(--ink-dim)}
.graph-node[hidden]{display:none}
.graph-inspector{position:absolute;z-index:5;top:12px;right:16px;width:min(390px,calc(100vw - 32px));max-height:calc(100% - 24px);overflow:auto;padding:20px;border:1px solid var(--line-2);border-radius:11px;background:#0d151edc;backdrop-filter:blur(16px);box-shadow:0 16px 44px #000b}
.graph-inspector[hidden]{display:none}
.graph-inspector-close{float:right;cursor:pointer;border:1px solid var(--line-2);background:var(--panel);border-radius:6px;color:var(--ink);font:20px/1 var(--sans);width:30px;height:30px}
.graph-inspector h3{margin:0 0 10px;font-size:18px}.graph-inspector h4{margin:20px 0 5px;color:var(--leaf);font-size:12px;text-transform:uppercase;letter-spacing:.1em}
.graph-inspector p,.graph-inspector li{color:var(--ink-dim);font-size:13px;line-height:1.6}
.graph-inspector .graph-state{font:600 11px var(--mono);text-transform:uppercase;color:var(--amber)}
.graph-inspector ul{padding-left:18px}
@media(max-width:700px){.graph-head{padding-right:10px}.graph-title{display:block}.graph-title h2{font-size:22px}.graph-title p{font-size:11px}.graph-honesty{font-size:10.5px}.graph-band small{display:none}.graph-inspector{top:auto;bottom:8px;right:8px;max-height:min(55vh,480px)}}
"""

JS = r"""
(function(){
  var dataEl=document.getElementById('graph-data'); if(!dataEl) return;
  var data=JSON.parse(dataEl.textContent), nodes=data.nodes, edges=data.edges;
  var byId={}; nodes.forEach(function(n){byId[n.id]=n});
  var canvas=document.getElementById('graph-canvas');
  var svg=document.getElementById('graph-lines'), inspector=document.getElementById('graph-inspector');
  var inspectorBody=document.getElementById('graph-inspector-body');
  var visible={}; nodes.forEach(function(n){visible[n.lane]=true});
  var CARD_W=260,CARD_H=126,X_GAP=322,Y_GAP=220,LEFT=180,TOP=65;
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function place(){
    var width=LEFT+7*X_GAP+CARD_W+70, height=TOP+5*Y_GAP+CARD_H+80;
    canvas.style.width=width+'px';canvas.style.height=height+'px';svg.setAttribute('viewBox','0 0 '+width+' '+height);
    document.querySelectorAll('[data-band]').forEach(function(band){band.style.top=(TOP-35+Number(band.dataset.band)*Y_GAP)+'px'});
    nodes.forEach(function(n){
      var el=document.getElementById('graph-'+n.id);el.hidden=!visible[n.lane];
      el.style.left=(LEFT+n.x*X_GAP)+'px';el.style.top=(TOP+n.y*Y_GAP)+'px';
    });
    var out='<defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#6e8b98"/></marker></defs>';
    edges.forEach(function(e){
      var a=byId[e[0]],b=byId[e[1]];if(!visible[a.lane]||!visible[b.lane])return;
      var ax=LEFT+a.x*X_GAP,ay=TOP+a.y*Y_GAP,bx=LEFT+b.x*X_GAP,by=TOP+b.y*Y_GAP;
      var d;
      if(b.x>a.x){
        var x1=ax+CARD_W,y1=ay+CARD_H/2,x2=bx,y2=by+CARD_H/2;
        d='M'+x1+','+y1+' C'+(x1+40)+','+y1+' '+(x2-40)+','+y2+' '+x2+','+y2;
      }else if(b.x===a.x){
        var down=b.y>a.y,x1=ax+CARD_W/2,y1=ay+(down?CARD_H:0),x2=bx+CARD_W/2,y2=by+(down?0:CARD_H);
        d='M'+x1+','+y1+' C'+x1+','+((y1+y2)/2)+' '+x2+','+((y1+y2)/2)+' '+x2+','+y2;
      }else{
        var x1=ax+CARD_W/2,y1=ay,x2=bx+CARD_W/2,y2=by,turn=Math.min(y1,y2)-38;
        d='M'+x1+','+y1+' C'+x1+','+turn+' '+x2+','+turn+' '+x2+','+y2;
      }
      var goal=a.status==='goal'||b.status==='goal';
      var main=a.y===b.y&&b.x===a.x+1&&(a.y===0||a.y===1||a.y===4||a.y===5);
      out+='<path class="edge-'+esc(goal?'goal':e[3])+(main?' edge-main':'')+'" d="'+d+'"><title>'+esc(a.title+' → '+b.title+': '+e[2])+'</title></path>';
    });svg.innerHTML=out;
  }
  function inspect(id){
    var n=byId[id];inspector.hidden=false;
    document.querySelectorAll('.graph-node').forEach(function(el){el.classList.toggle('is-selected',el.dataset.node===id)});
    var links=n.specs.map(function(url){var name=url.split('/').slice(-2,-1)[0];return '<li><a target="_blank" rel="noopener" href="'+esc(url)+'">'+esc(name)+'</a></li>'}).join('');
    var contacts=edges.filter(function(e){return e[0]===id||e[1]===id}).map(function(e){
      var other=byId[e[0]===id?e[1]:e[0]];return '<li>'+esc(e[0]===id?'To ':'From ')+esc(other.title)+' · '+esc(e[2])+'</li>'}).join('');
    inspectorBody.innerHTML='<p class="graph-state">'+esc(n.status)+' now · '+esc(n.lane)+' layer</p><h3>'+esc(n.title)+'</h3><p>'+esc(n.detail)+'</p><h4>Interactions</h4><ul>'+contacts+'</ul><h4>Goal-state specifications</h4><ul>'+links+'</ul><p><a href="#progress">See the accountability ledger</a></p>';
  }
  document.querySelectorAll('.graph-node').forEach(function(el){el.addEventListener('click',function(){inspect(el.dataset.node)})});
  document.getElementById('graph-inspector-close').addEventListener('click',function(){inspector.hidden=true;document.querySelectorAll('.graph-node').forEach(function(el){el.classList.remove('is-selected')})});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!inspector.hidden){inspector.hidden=true;document.querySelectorAll('.graph-node').forEach(function(el){el.classList.remove('is-selected')})}});
  document.querySelectorAll('[data-toggle-lane]').forEach(function(button){button.addEventListener('click',function(){
    var lane=button.dataset.toggleLane;visible[lane]=!visible[lane];button.setAttribute('aria-pressed',String(visible[lane]));place();
  })});
  place();
})();
"""
