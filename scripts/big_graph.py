"""A source-linked goal-state system map. Coordinates move; typography does not scale."""
import html
import json
import pathlib

BASE = "https://github.com/8007342/tillandsias/blob/{tag}/openspec/specs/{slug}/spec.md"

# id, lane, column, row, title, current state, concise role, expanded explanation, specs
NODES = [
    ("person", "host", 0, 0, "Operator", "implemented", "Chooses project, model and permissions.", "The person starts or tears down a local region, grants host access, reviews changes and owns the external account. A website checkout does not give the agent host authority by itself.", "app-lifecycle"),
    ("host", "host", 1, 0, "Host orchestrator", "partial", "Creates and supervises the region.", "The tray and headless controller provision networks, containers, routes and lifecycle. They bridge host privileges to the runtime; this is a trust boundary, not a container inside the enclave.", "podman-orchestration"),
    ("keychain", "host", 2, 0, "Host keychain", "partial", "Protects the Vault unseal material.", "The host credential store is intended to own the unseal key. Guest and cache copies and reset verification remain relevant limits; keychain isolation is not equivalent to an uncompromised host.", "tillandsias-vault"),
    ("browser", "host", 3, 0, "Personal browser", "implemented", "Operator-facing application.", "The personal browser is outside the enclave. Opening a local preview crosses a route from host to project web service; arbitrary host browsing is not the agent's browser capability.", "host-browser-mcp"),
    ("kernel", "host", 4, 0, "Kernel / VM boundary", "partial", "Linux host or Linux guest.", "On Linux, rootless containers share the host kernel. macOS and Windows use a Linux VM (Windows via WSL2). The VM is a boundary with host integrations, not a guarantee against host compromise.", "podman-orchestration"),
    ("github", "external", 5, 0, "GitHub remote", "implemented", "Durable upstream refs and release source.", "The mirror pushes accepted refs outward. Remote acceptance, not a local commit, establishes that this example's work survived the disposable forge. GitHub and its credentials remain external dependencies.", "git-mirror-service"),
    ("checkout", "forge", 0, 1, "tillandsias.org checkout", "implemented", "Project files mounted in the forge.", "Example path: this website source checkout enters a project forge. The agent edits scripts, OpenSpec changes and generated HTML, runs the checked build, then commits and pushes. The source tree and the generated site have different roles.", "forge-as-only-runtime"),
    ("agent", "forge", 1, 1, "Agent + tool process", "implemented", "Reads, edits, runs commands and tests.", "The coding agent lives in the forge container with scoped project and tool access. It can observe its checkout and invoke project commands. Its prompt and tool outputs are untrusted data with respect to host authority.", "forge-as-only-runtime"),
    ("forgefs", "forge", 2, 1, "Forge writable layer", "implemented", "Disposable tool and process state.", "The rootless forge has an image, writable container layer, project mount and cache mounts. Recreating it discards container-local state; only explicitly durable mounts and pushed git refs should be treated as surviving.", "default-image"),
    ("projectfs", "forge", 3, 1, "Project / worktree mount", "partial", "Source tree and generated page.", "The website checkout is the working tree, including docs, scripts, OpenSpec files and var/html output. Mount policy is a filesystem boundary; a writable mount permits file changes and does not authenticate those changes.", "forge-as-only-runtime"),
    ("cache", "forge", 4, 1, "Cache volumes", "partial", "Models and build caches across rebuilds.", "Caches can outlive a forge or VM. Survival is useful for model downloads but complicates reset, credential cleanup and provenance. Mac cache migration and end-to-end rebuild evidence are incomplete.", "forge-cache-architecture"),
    ("commit", "forge", 5, 1, "Commit + local push", "implemented", "Transparent history from the checkout.", "The agent commits the reviewed website diff and pushes to the local git mirror. A checked build can gate the generated output. A commit is a record of edits, not proof of security or upstream delivery.", "git-mirror-service"),
    ("network", "enclave", 0, 2, "Private enclave network", "partial", "Rootless siblings share internal DNS.", "The desired network has no direct route to the internet. Shell creation paths use Podman's internal network flag, while the Rust path's gate is file-scoped. Membership is reachability, not identity or mutual authentication.", "podman-orchestration"),
    ("proxy", "enclave", 1, 2, "Egress proxy", "partial", "One policy-controlled exit.", "HTTP egress should flow through allowlist and policy checks. A permissive listener is loopback-bound, but namespace and alternate-path gaps remain. The proxy is a chokepoint only if every launch and route actually uses it.", "proxy-container"),
    ("mirror", "enclave", 2, 2, "Git mirror", "partial", "Local git receiver and upstream relay.", "The forge pushes to a local sibling; the mirror holds the upstream credential and relays refs to GitHub. Agent-facing push is anonymous within the enclave, so network membership remains a material trust assumption.", "git-mirror-service"),
    ("vault", "enclave", 3, 2, "Vault service", "partial", "Scoped secrets for sibling services.", "Vault should release only the credential needed by a service after unseal. Host keychain, guest copies and reset paths define the true secret boundary. A compromised sibling can still exercise whatever token it receives.", "tillandsias-vault"),
    ("inference", "enclave", 4, 2, "Local inference", "partial", "Model service near the forge.", "A pinned, digest-checked engine may run locally; readiness remains best effort. The desired router chooses usable host CPU/GPU/NPU lanes from measured capabilities, rather than inferring safety or performance from device presence.", "inference-engine-slots"),
    ("web", "enclave", 5, 2, "Project web sibling", "partial", "Serves generated website preview.", "The website's var/html output is served by a sibling httpd and routed to the host browser. Document root, dotfile handling and lifecycle rules remain incomplete; the web service should never imply that the checkout itself is safely public.", "web-image"),
    ("rootless", "boundary", 0, 3, "Rootless container boundary", "partial", "User namespace, mounts, caps and labels.", "Containers separate processes and files under a non-root identity. Every launch path must apply checked settings; several raw paths do not yet share the validator. Linux forge SELinux/MCS confinement is a desired future boundary.", "podman-orchestration"),
    ("certs", "boundary", 1, 3, "Local CA + certificates", "partial", "TLS trust for proxy and local routes.", "A persistent local CA key, trust distribution and service certificates define where TLS terminates. Current parent-directory creation is not private by construction. Trusting a CA expands authority; it does not authenticate every enclave peer.", "certificate-authority"),
    ("wire", "boundary", 2, 3, "Encrypted control wire", "partial", "Protects host-to-runtime control traffic.", "The secure setting defaults on, but an explicit plaintext override and release-key limits remain. Channel encryption does not establish container isolation or the integrity of downloaded artifacts.", "host-guest-transport"),
    ("supply", "boundary", 3, 3, "Artifact provenance", "partial", "Verify images, installers and releases.", "Desired state: signed release artifacts and ordinary-install signature verification across platforms. Current signing is uneven; ordinary install can proceed without a checksum and does not verify a cosign bundle.", "binary-signing"),
    ("policy", "boundary", 4, 3, "Policy / allowlists", "partial", "Gate tools, routes and egress.", "Filesystem, browser and network allowlists should be checked at their actual invocation sites. A rule in a spec or shell test is not enforcement if a separate launch path bypasses it.", "proxy-container"),
    ("audit", "boundary", 5, 3, "Audit and evidence", "partial", "Tie claims to requirements and checks.", "Stable requirement IDs and model property checks exist in part. The website's source-linked levels and findings record are an audit layer, not live telemetry or proof of all runtime validators.", "spec-traceability"),
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
    ("person", "host", "starts", "control"), ("host", "kernel", "provisions", "control"),
    ("host", "keychain", "unseals", "secret"), ("host", "network", "creates", "control"),
    ("host", "browser", "opens preview", "web"), ("browser", "web", "routed request", "web"),
    ("checkout", "agent", "read/write", "file"), ("agent", "forgefs", "tools", "file"),
    ("agent", "projectfs", "edits", "file"), ("forgefs", "cache", "mounts", "file"),
    ("projectfs", "web", "generated output", "web"), ("agent", "commit", "commit", "git"),
    ("commit", "mirror", "push", "git"), ("mirror", "github", "relay refs", "git"),
    ("mirror", "vault", "fetch token", "secret"), ("vault", "keychain", "unseal chain", "secret"),
    ("mirror", "proxy", "HTTPS", "network"), ("proxy", "github", "allowlisted", "network"),
    ("agent", "inference", "model request", "network"), ("agent", "proxy", "egress", "network"),
    ("network", "rootless", "isolation", "boundary"), ("proxy", "policy", "allowlist", "boundary"),
    ("proxy", "certs", "TLS trust", "boundary"), ("host", "wire", "control", "boundary"),
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


def render(tag):
    catalog = json.loads((pathlib.Path(__file__).resolve().parent.parent /
                          "docs/progress/runtime-specs.json").read_text())
    if catalog["tag"] != tag:
        raise ValueError("Big Graph spec sources do not match the website pin")
    valid_specs = {s["id"] for s in catalog["specs"]}
    ids = [n[0] for n in NODES]
    if len(ids) != len(set(ids)):
        raise ValueError("Big Graph has duplicate component IDs")
    for n in NODES:
        if n[5] not in ("implemented", "partial", "goal"):
            raise ValueError("Big Graph has an unknown current-state label: " + n[0])
        for slug in n[-1].split():
            if slug not in valid_specs:
                raise ValueError("Big Graph source is absent at %s: %s" % (tag, slug))
    for source, target, _, _ in EDGES:
        if source not in ids or target not in ids:
            raise ValueError("Big Graph edge has a missing component")
    cards = []
    data = []
    for id_, lane, col, row, title, status, short, long, specs in NODES:
        refs = [BASE.format(tag=tag, slug=s) for s in specs.split()]
        data.append(dict(id=id_, lane=lane, x=col, y=row, title=title, status=status,
                         short=short, detail=long, specs=refs))
        cards.append('<button type="button" class="graph-node status-%s" id="graph-%s" '
                     'data-node="%s" data-lane="%s" aria-label="%s: %s. Open details">'
                     '<span class="graph-node-top"><small>%s</small><small>%s</small></span>'
                     '<strong>%s</strong><span class="graph-short">%s</span>'
                     '<span class="graph-extra">%s</span></button>' %
                     tuple(html.escape(str(v), quote=True) for v in
                           (status, id_, id_, lane, title, status, lane, status, title, short, long)))
    chips = ''.join('<button type="button" class="graph-lane-toggle" data-toggle-lane="%s" '
                    'aria-pressed="true">%s</button>' % (id_, title) for id_, title in LANES)
    return ('<section class="view" id="view-big-graph" role="tabpanel" aria-labelledby="nav-big-graph">'
            '<div class="graph-head"><p class="eyebrow">Tillandsias · system map</p>'
            '<h2>Big Graph</h2><p>The desired architecture of a tillandsias.org checkout '
            'inside a project forge. Drag the map or scroll in both directions. Open any '
            'component for rationale, limits and pinned specifications.</p>'
            '<p class="graph-honesty"><b>Reading key:</b> solid green = implemented at the pinned '
            'release; amber dashed = partial; gray dotted = goal only. These are editorial '
            'assessments from the <a href="https://github.com/8007342/tillandsias.org/blob/main/docs/audit/2026-09-22-v56.9.21.1.md" '
            'target="_blank" rel="noopener">stable audit</a>, not runtime telemetry. '
            'The enclosing map shows desired interactions; an edge does not prove enforcement.</p>'
            '<div class="graph-controls"><button type="button" id="graph-out" aria-label="Spread less">−</button>'
            '<label for="graph-zoom">Spacing <output id="graph-zoom-value">100%%</output></label>'
            '<input id="graph-zoom" type="range" min="90" max="180" step="5" value="100">'
            '<button type="button" id="graph-in" aria-label="Spread more">+</button>'
            '<button type="button" id="graph-reset">Reset view</button></div>'
            '<div class="graph-lanes" role="group" aria-label="Show or hide system layers">%s</div>'
            '</div><div class="graph-shell"><div class="graph-viewport" id="graph-viewport" '
            'aria-label="Scrollable architecture graph"><div class="graph-canvas" id="graph-canvas">'
            '<svg id="graph-lines" aria-hidden="true"></svg>%s</div></div>'
            '<aside class="graph-inspector" id="graph-inspector" aria-live="polite">'
            '<h3>Inspect a component</h3><p>Choose any box to see its trust assumptions, '
            'current limitations and source specifications.</p></aside></div>'
            '<script type="application/json" id="graph-data">%s</script></section>' %
            (chips, ''.join(cards), json.dumps({"nodes": data, "edges": EDGES}).replace("<", "\\u003c")))


CSS = r"""
/* --- Big Graph: geometry changes on zoom, typography stays fixed --- */
#view-big-graph{padding:64px 0 50px}
.graph-head{padding:0 24px;max-width:1500px;margin:auto}
.graph-head h2{font-size:clamp(32px,5vw,54px);line-height:1.1;margin:0 0 12px}
.graph-head>p:not(.eyebrow){max-width:90ch;color:var(--ink-dim);margin:0 0 16px}
.graph-honesty{font-size:13px;line-height:1.6;padding:12px 16px;border:1px solid var(--line);border-radius:9px;background:var(--bg-2)}
.graph-honesty a,.graph-inspector a{color:var(--leaf)}
.graph-controls,.graph-lanes{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin:12px 0}
.graph-controls button,.graph-lane-toggle{border:1px solid var(--line-2);background:var(--panel);color:var(--ink);border-radius:7px;cursor:pointer;padding:7px 11px;font:500 12px var(--sans)}
.graph-controls button:hover,.graph-lane-toggle:hover{border-color:var(--leaf)}
.graph-controls label{font:500 12px var(--mono);color:var(--ink-dim)}
.graph-controls input{width:140px;accent-color:var(--leaf)}
.graph-lane-toggle[aria-pressed="false"]{opacity:.43;text-decoration:line-through}
.graph-shell{display:grid;grid-template-columns:minmax(0,1fr) 320px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);min-height:70vh}
.graph-viewport{overflow:auto;height:min(75vh,900px);background:radial-gradient(circle at 1px 1px,#202b38 1px,transparent 0) 0 0/24px 24px,#0a0e13;cursor:grab;overscroll-behavior:contain}
.graph-viewport.is-dragging{cursor:grabbing}
.graph-canvas{position:relative;min-width:100%;min-height:100%}
#graph-lines{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}
#graph-lines path{fill:none;stroke:#436474;stroke-width:1.7;opacity:.55;marker-end:url(#graph-arrow)}
#graph-lines path.edge-secret{stroke:#a48bf0}#graph-lines path.edge-git{stroke:#5fd6a4}
#graph-lines path.edge-boundary{stroke:#e6b45e;stroke-dasharray:5 5}
#graph-lines path.edge-goal{stroke:#777;stroke-dasharray:4 7}
.graph-node{position:absolute;width:260px;min-height:126px;padding:12px 14px;text-align:left;color:var(--ink);background:#111b24;border:1px solid var(--leaf-dim);border-left:4px solid var(--leaf);border-radius:10px;box-shadow:0 8px 26px #0008;cursor:pointer;font:400 12px/1.4 var(--sans);z-index:1}
.graph-node:hover,.graph-node:focus-visible,.graph-node.is-selected{outline:2px solid var(--sky);outline-offset:2px;z-index:3}
.graph-node.status-partial{border-color:#866a3d;border-left-color:var(--amber);border-style:dashed;background:#1b1a17}
.graph-node.status-goal{border-color:#4c535b;border-left-color:#87909b;border-style:dotted;background:#16191d;color:#b0bac4}
.graph-node-top{display:flex;justify-content:space-between;gap:8px;text-transform:uppercase;letter-spacing:.11em;color:var(--ink-faint);font:600 10px var(--mono)}
.graph-node strong{display:block;font-size:15px;line-height:1.25;margin:8px 0 5px}
.graph-short,.graph-extra{display:block;color:var(--ink-dim)}
.graph-extra{display:none;font-size:11px;line-height:1.45;margin-top:8px;color:var(--ink-faint)}
.graph-canvas.is-detailed .graph-extra{display:block}
.graph-node[hidden]{display:none}
.graph-inspector{position:sticky;top:0;align-self:start;max-height:75vh;overflow:auto;padding:22px;border-left:1px solid var(--line);background:var(--bg-2)}
.graph-inspector h3{margin:0 0 10px;font-size:18px}.graph-inspector h4{margin:20px 0 5px;color:var(--leaf);font-size:12px;text-transform:uppercase;letter-spacing:.1em}
.graph-inspector p,.graph-inspector li{color:var(--ink-dim);font-size:13px;line-height:1.6}
.graph-inspector .graph-state{font:600 11px var(--mono);text-transform:uppercase;color:var(--amber)}
.graph-inspector ul{padding-left:18px}
@media(max-width:850px){.graph-shell{grid-template-columns:1fr}.graph-viewport{height:58vh}.graph-inspector{position:static;max-height:none;border-left:0;border-top:1px solid var(--line)}}
"""

JS = r"""
(function(){
  var dataEl=document.getElementById('graph-data'); if(!dataEl) return;
  var data=JSON.parse(dataEl.textContent), nodes=data.nodes, edges=data.edges;
  var byId={}; nodes.forEach(function(n){byId[n.id]=n});
  var canvas=document.getElementById('graph-canvas'), viewport=document.getElementById('graph-viewport');
  var svg=document.getElementById('graph-lines'), inspector=document.getElementById('graph-inspector');
  var slider=document.getElementById('graph-zoom'), output=document.getElementById('graph-zoom-value');
  var selected=null, visible={}; nodes.forEach(function(n){visible[n.lane]=true});
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function place(){
    var spread=Number(slider.value)/100, xGap=295*spread, yGap=205*spread;
    var width=260+5*xGap+180, height=160+5*yGap+160;
    canvas.style.width=width+'px';canvas.style.height=height+'px';svg.setAttribute('viewBox','0 0 '+width+' '+height);
    output.textContent=slider.value+'%';canvas.classList.toggle('is-detailed',spread>=1.4);
    nodes.forEach(function(n){
      var el=document.getElementById('graph-'+n.id);el.hidden=!visible[n.lane];
      el.style.left=(70+n.x*xGap)+'px';el.style.top=(70+n.y*yGap)+'px';
    });
    var out='<defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#6e8b98"/></marker></defs>';
    edges.forEach(function(e){
      var a=byId[e[0]],b=byId[e[1]];if(!visible[a.lane]||!visible[b.lane])return;
      var x1=200+a.x*xGap,y1=133+a.y*yGap,x2=200+b.x*xGap,y2=133+b.y*yGap;
      var mid=(y1+y2)/2;
      var d='M'+x1+','+y1+' C'+x1+','+mid+' '+x2+','+mid+' '+x2+','+y2;
      var goal=a.status==='goal'||b.status==='goal';
      out+='<path class="edge-'+esc(goal?'goal':e[3])+'" d="'+d+'"><title>'+esc(a.title+' → '+b.title+': '+e[2])+'</title></path>';
    });svg.innerHTML=out;
  }
  function inspect(id){
    selected=id;var n=byId[id];
    document.querySelectorAll('.graph-node').forEach(function(el){el.classList.toggle('is-selected',el.dataset.node===id)});
    var links=n.specs.map(function(url){var name=url.split('/').slice(-2,-1)[0];return '<li><a target="_blank" rel="noopener" href="'+esc(url)+'">'+esc(name)+'</a></li>'}).join('');
    var contacts=edges.filter(function(e){return e[0]===id||e[1]===id}).map(function(e){
      var other=byId[e[0]===id?e[1]:e[0]];return '<li>'+esc(e[0]===id?'To ':'From ')+esc(other.title)+' · '+esc(e[2])+'</li>'}).join('');
    inspector.innerHTML='<p class="graph-state">'+esc(n.status)+' now · '+esc(n.lane)+' layer</p><h3>'+esc(n.title)+'</h3><p>'+esc(n.detail)+'</p><h4>Interactions</h4><ul>'+contacts+'</ul><h4>Goal-state specifications</h4><ul>'+links+'</ul><p><a href="#progress">See the accountability ledger</a></p>';
  }
  document.querySelectorAll('.graph-node').forEach(function(el){el.addEventListener('click',function(){inspect(el.dataset.node)})});
  slider.addEventListener('input',place);
  document.getElementById('graph-in').addEventListener('click',function(){slider.value=Math.min(180,Number(slider.value)+10);place()});
  document.getElementById('graph-out').addEventListener('click',function(){slider.value=Math.max(90,Number(slider.value)-10);place()});
  document.getElementById('graph-reset').addEventListener('click',function(){slider.value=100;viewport.scrollTo(0,0);place()});
  document.querySelectorAll('[data-toggle-lane]').forEach(function(button){button.addEventListener('click',function(){
    var lane=button.dataset.toggleLane;visible[lane]=!visible[lane];button.setAttribute('aria-pressed',String(visible[lane]));place();
  })});
  var drag=null;
  viewport.addEventListener('pointerdown',function(e){if(e.target.closest('button'))return;drag={x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop};viewport.setPointerCapture(e.pointerId);viewport.classList.add('is-dragging')});
  viewport.addEventListener('pointermove',function(e){if(!drag)return;viewport.scrollLeft=drag.left-(e.clientX-drag.x);viewport.scrollTop=drag.top-(e.clientY-drag.y)});
  viewport.addEventListener('pointerup',function(){drag=null;viewport.classList.remove('is-dragging')});
  viewport.addEventListener('pointercancel',function(){drag=null;viewport.classList.remove('is-dragging')});
  place();
})();
"""
