"""A source-linked goal-state system map with left-to-right journeys."""
import html
import json
import os
import pathlib
import re

BASE = "https://github.com/8007342/tillandsias/blob/{tag}/openspec/specs/{slug}/spec.md"
RUNTIME_FILE_BASE = "https://github.com/8007342/tillandsias/blob/{tag}/"
SITE_FILE_BASE = "https://github.com/8007342/tillandsias.org/blob/main/"

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
         ("enclave", "Shared enclave services"), ("external", "External remote"),
         ("boundary", "Security boundaries"),
         ("lifecycle", "Lifecycle events"), ("method", "Requirements and evidence")]

BANDS = [
    ("Build and publish", "Operator → forge → git mirror → guarded exit → GitHub"),
    ("Preview and files", "Runtime boundary → mounted output → web sibling → browser"),
    ("Internal services", "Host keys → control wire → enclave → secrets, inference and cache"),
    ("Security review", "Certificates, policy, provenance and evidence support the flows above"),
    ("Lifecycle", "Install → create → edit → publish → teardown → rebuild"),
    ("Accountability", "Requirements → obligations → checks → ledger → score → review"),
]

FLOWS = [
    ("person", "host", "checkout", "agent", "commit", "mirror", "proxy", "github"),
    ("projectfs", "web", "browser"),
    ("install", "create", "edit", "publish", "teardown", "rebuild"),
    ("spec", "plan", "tests", "ledger", "score", "review"),
]

# These notes interpret the pinned audit. A checked task list is linked as a
# historical work record, never as a substitute for current runtime evidence.
# Each entry: observed behavior, unfinished boundary/scope, supporting records.
NOTES = {
    "person": ("The operator initiates project and app actions from the host side. This is the real decision-maker in the diagram, not an agent-owned service.", "The green actor does not certify that every confirmation, permission, or host cleanup path is complete. Those checks belong to the host orchestrator and security rows.", [("Application lifecycle contract", "runtime:openspec/specs/app-lifecycle/spec.md")]),
    "host": ("The headless controller launches the Linux runtime and siblings and brokers host integrations.", "Audit every launch path for the same checked container settings, failed-start cleanup, and route teardown. Several raw sibling launch paths do not share the forge validator.", [("Forge launch evidence", "runtime:crates/tillandsias-headless/src/main.rs#L15906-L15909")]),
    "keychain": ("Host credentials are used to seed Vault's unseal chain; app reset now refuses incomplete host credential cleanup.", "A Linux clean-room path still treats a failed clear or cold probe as best effort. Copies of unseal material in guests and caches must be accounted for before claiming a fully cold reset.", [("App reset refusal", "runtime:crates/tillandsias-headless/src/main.rs#L9834-L9850"), ("Linux clean-room gap", "runtime:scripts/e2e-step2-linux.sh#L30-L38")]),
    "browser": ("A person can use a host browser to view a routed project preview. It remains outside the enclave.", "This green box denotes the external actor. It does not mark the host-browser tool complete; the stable audit still records a missing consumer for its installer.", [("Host browser tool limit", "runtime:scripts/install-chromium.sh#L10-L16")]),
    "kernel": ("Linux rootless containers share the host kernel; macOS and Windows place a Linux runtime behind a VM boundary.", "The boundary still depends on host and guest integration, route policy, and launch validation. A VM is not a blanket guarantee against host compromise.", [("Container orchestration contract", "runtime:openspec/specs/podman-orchestration/spec.md")]),
    "github": ("An accepted upstream ref gives the disposable forge a recovery point beyond the local mirror.", "The green remote box represents an external service, not evidence that every local push reached it. No-upstream pushes can remain local only; verify the upstream transaction before teardown.", [("Mirror pre-receive gate", "runtime:images/git/pre-receive-hook.sh#L6-L8")]),
    "checkout": ("The website source tree is mounted into the project forge and is the agent's working set.", "The mount's presence does not make edits trusted. Review the diff and run source checks before committing and pushing.", [("Completed remote-project clone checklist", "runtime:openspec/changes/archive/2026-03-24-remote-project-clone/tasks.md"), ("Forge runtime contract", "runtime:openspec/specs/forge-as-only-runtime/spec.md")]),
    "agent": ("The agent can inspect files, edit code, run tools, and operate the website's checked build inside the forge.", "This green covers the tool process, not unlimited host authority. Prompts, repository content, and tool outputs can be adversarial inputs; host and network permissions need independent checks.", [("Completed forge shell-tools checklist", "runtime:openspec/changes/archive/2026-03-24-forge-shell-tools/tasks.md")]),
    "forgefs": ("The forge image and writable container layer hold tools and transient process state.", "Only explicitly mounted data and accepted git refs should be expected after replacement. Cache and project mounts have different retention and trust rules.", [("Completed versioned-forge-images checklist", "runtime:openspec/changes/archive/2026-03-26-versioned-forge-images/tasks.md"), ("Default image contract", "runtime:openspec/specs/default-image/spec.md")]),
    "projectfs": ("The checkout contains source, OpenSpec changes, scripts, and the generated var/html page.", "The project mount remains writable by the forge; mount scope, dotfile handling, and the web sibling's document root need consistent policy before claiming safe publication.", [("Web service plan gap", "runtime:plan/index.yaml#L51819")]),
    "cache": ("Approved caches can preserve models and builds across forge replacement; the Mac VM mounts a host share.", "Mac cache migration and end-to-end rebuild proof remain incomplete. A cache may retain sensitive material, so reset and provenance claims must inspect it as well.", [("Mac cache mount", "runtime:crates/tillandsias-vm-layer/src/vz.rs#L874-L880"), ("Remaining cache work", "runtime:plan/index.yaml#L31158")]),
    "commit": ("The website workflow records a reviewed diff in git and pushes to the local mirror. The mirror gate participates in durable-ref handling.", "A local commit or local-only push is not upstream durability; the relay must report remote acceptance. A successful commit also does not certify that every runtime claim is true.", [("Durable push path", "runtime:crates/tillandsias-headless/src/main.rs#L15906-L15909"), ("Mirror receive gate", "runtime:images/git/pre-receive-hook.sh#L6-L8")]),
    "network": ("Shell creators request an internal Podman network for enclave siblings.", "The Rust gate remains file-scoped rather than a proof of every future create path. Network membership grants reachability, not service identity or mutual authentication.", [("Internal-network gate", "runtime:scripts/check-enclave-network-internal.sh#L113-L181")]),
    "proxy": ("The proxy has policy listeners and the permissive listener is loopback-bound at this release.", "Strict allowlisting still admits broad publishable namespaces, and every alternate egress path needs to be closed before calling this a single checked exit.", [("Proxy listener configuration", "runtime:images/proxy/squid.conf#L70-L78")]),
    "mirror": ("The mirror receives an agent-facing push, obtains an upstream credential, and relays refs outward.", "The agent-facing endpoint is anonymous inside the enclave, so a sibling with network access can attempt a push. Credential isolation and upstream acceptance remain separate checks.", [("Credential helper host check", "runtime:images/git/git-credential-tillandsias.sh#L58-L83"), ("Anonymous local receive path", "runtime:images/git/entrypoint.sh#L413-L420")]),
    "vault": ("Vault holds secrets used by siblings, while the host keychain participates in its unseal chain.", "Prove reset clears all guest and cache copies, and limit each service token's authority. A compromised consumer may still exercise a token it legitimately receives.", [("Host cleanup behavior", "runtime:crates/tillandsias-headless/src/main.rs#L9834-L9850")]),
    "inference": ("The inference entrypoint pins and checks an engine artifact before starting the local service.", "Readiness remains best effort. The desired CPU/GPU/NPU routing needs measured capability and end-to-end evidence, not mere device discovery.", [("Pinned engine download", "runtime:images/inference/entrypoint.sh#L329-L383"), ("Best-effort readiness", "runtime:crates/tillandsias-headless/src/main.rs#L15301-L15308")]),
    "web": ("A project web sibling can expose the generated website preview through a host route.", "Document-root containment, dotfile behavior, and lifecycle cleanup are not complete at the pinned release. Preview is not the same thing as public deployment.", [("Web sibling plan gap", "runtime:plan/index.yaml#L51819"), ("Completed web-image checklist", "runtime:openspec/changes/archive/2026-03-22-web-image/tasks.md")]),
    "rootless": ("The forge is launched rootless and checked serialization applies to its configuration.", "Raw proxy, mirror, observatory, and browser paths do not all call the same validator. Linux forge SELinux/MCS confinement is still future work.", [("Current label-disable setting", "runtime:openspec/specs/podman-orchestration/spec.md#L110"), ("Planned MCS label", "runtime:openspec/specs/default-image/spec.md#L768-L769")]),
    "certs": ("The runtime creates a persistent proxy CA and clamps the key file's mode.", "The parent directory is not private by construction; establish directory ownership/mode before writing key material, then test the trust distribution and rotation path.", [("CA creation and key mode", "runtime:crates/tillandsias-headless/src/main.rs#L3155-L3220")]),
    "wire": ("Secure host-to-runtime control traffic defaults on.", "An explicit plaintext override and release-key limits remain. The goal is to make downgrade and identity assumptions visible and testable across ordinary launches.", [("Host–guest transport contract", "runtime:openspec/specs/host-guest-transport/spec.md")]),
    "supply": ("The release workflow signs a fixed list of Mac artifacts; other platforms have broader transitive checks.", "Ordinary install does not verify a cosign bundle and Linux may continue without an available checksum. Close that gap before claiming signed distribution end to end.", [("Release signing list", "runtime:.github/workflows/release.yml#L500-L517"), ("Installer checksum behavior", "runtime:scripts/install.sh#L226-L239")]),
    "policy": ("There are browser and proxy allowlists and checked forge launch settings.", "Apply policy at every real invocation path. The strict proxy port and raw sibling launches still leave bypass or overbroad-namespace questions.", [("Browser dotted-name check", "runtime:crates/tillandsias-browser-mcp/src/allowlist.rs#L250-L257"), ("Proxy strict/permissive ports", "runtime:images/proxy/squid.conf#L70-L78")]),
    "audit": ("The site pins line citations and the runtime has some stable requirement-ID and model-property checks.", "The tested model does not cover every live validator, and the site's checked build does not execute the runtime or verify public deployment.", [("Requirement ID check", "runtime:scripts/check-requirement-ids.sh#L5-L35"), ("Model property checks", "runtime:crates/tillandsias-plan/src/obligation_props.rs#L172-L219")]),
    "install": ("Stable installers provision the application and default to reset/reprovision in current releases.", "Ordinary install needs stronger artifact signature verification; reset also needs a complete host, guest, and cache cleanup proof.", [("Linux reset path", "runtime:scripts/install.sh#L313-L314"), ("Installer verification gap", "runtime:scripts/install.sh#L226-L239")]),
    "create": ("The controller can create the Linux runtime, enclave network, shared services, and project forge.", "Partial failures and alternate launch paths must preserve the intended internal network, validated container settings, and cleanup order.", [("Internal network creator", "runtime:scripts/run-forge-project.sh#L127-L130")]),
    "edit": ("For this site, source edits, finding validation, generated HTML, and release-pinned citation checks are explicit build steps.", "This green describes the site workflow and its checked output, not a live browser or public Cloudflare deployment test.", [("Website checked-build gate", "site:skills/update-website/scripts/checked-build.sh"), ("Website source generator", "site:scripts/build-matrix.py")]),
    "publish": ("A local mirror can relay accepted refs to GitHub, and the website deploy path consumes the pushed repository.", "The public deployment and project preview are separate surfaces. If no upstream is configured, a successful local push has not made the work durable off-host.", [("Mirror receive gate", "runtime:images/git/pre-receive-hook.sh#L6-L8")]),
    "teardown": ("App reset refuses to reprovision when host credentials cannot be cleared.", "The Linux clean-room step still logs and continues after a failed clear or cold probe. Caches, routes, and guest copies require lifecycle-specific evidence.", [("App reset refusal", "runtime:crates/tillandsias-headless/src/main.rs#L9834-L9850"), ("Cold-probe limit", "runtime:scripts/e2e-step2-linux.sh#L30-L38")]),
    "rebuild": ("Approved git refs and cache mounts can be used to recreate a forge after teardown.", "Demonstrate cache survival and secret removal separately on each host OS. An unpushed commit cannot be reconstructed from GitHub.", [("Mac cache mount", "runtime:crates/tillandsias-vm-layer/src/vz.rs#L874-L880"), ("Remaining migration work", "runtime:plan/index.yaml#L31158")]),
    "spec": ("The pinned runtime release contains the canonical OpenSpec set; this site snapshots every spec into Progress.", "The green denotes source documents that exist, not that every active spec requirement is implemented. A change checklist and a runtime test answer different questions.", [("Runtime traceability contract", "runtime:openspec/specs/spec-traceability/spec.md"), ("Site spec inventory", "site:docs/progress/runtime-specs.json")]),
    "plan": ("The runtime has an obligation model and property checks for part of its methodology.", "Bridge every requirement to the live validator actually used, then establish denominator stability before claiming application-wide completion.", [("Obligation property checks", "runtime:crates/tillandsias-plan/src/obligation_props.rs#L172-L219")]),
    "tests": ("The website checked build verifies quoted release targets, and the runtime has source/model checks.", "Platform installers, runtime isolation, and public deployment need distinct execution evidence; a passing source check cannot substitute for them.", [("Website checked-build gate", "site:skills/update-website/scripts/checked-build.sh"), ("Runtime requirement check", "runtime:scripts/check-requirement-ids.sh#L5-L35")]),
    "ledger": ("Append-only issue fragments fold into found, tracked, and resolved columns; the site also lists pinned specs and archived changes.", "This green is about the website ledger's implemented mechanics. Finding counts and checked checklists are not a measured application-completion percentage.", [("Website issue fold", "site:scripts/issues.py"), ("Progress page contract", "site:openspec/changes/progress-ledger-big-graph/specs/site/progress/spec.md")]),
    "score": ("The runtime has a bounded local obligation score; no comparable application-wide series is published here.", "Define and verify a stable denominator, connect all live validators, and handle a broken scoring regime before plotting cross-release convergence. This node remains dotted until that evidence exists.", [("Non-comparability after broken regime", "runtime:scripts/local-ci.sh#L612-L620")]),
    "review": ("The site records findings, source links, and correction events; security review already exposes boundary gaps.", "A complete closed-loop review needs each important boundary linked to its enforcement point, adversarial test, owner, and resolved-or-retracted history. The aspiration is broader than the current audit record.", [("Website issue fold", "site:scripts/issues.py"), ("Runtime traceability contract", "runtime:openspec/specs/spec-traceability/spec.md")]),
}


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
    if set(ids) != set(NOTES):
        raise ValueError("Big Graph explanatory notes must cover every component")
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
    for flow in FLOWS:
        for source, target in zip(flow, flow[1:]):
            if (source, target) not in pairs or positions[source][0] >= positions[target][0] or positions[source][1] != positions[target][1]:
                raise ValueError("Big Graph primary journey must flow left to right: %s → %s" % (source, target))
    cards = []
    data = []
    clone_dir = os.environ.get("TILLANDSIAS_CLONE_DIR")
    runtime_checkout = pathlib.Path(clone_dir) / tag if clone_dir else None
    for id_, lane, col, row, title, status, short, long, specs in NODES:
        refs = [BASE.format(tag=tag, slug=s) for s in specs.split()]
        current, pending, source_records = NOTES[id_]
        evidence = []
        for label, source in source_records:
            kind, path = source.split(":", 1)
            if kind == "site":
                if not (pathlib.Path(__file__).resolve().parent.parent / path).exists():
                    raise ValueError("Big Graph site source is absent: " + path)
                url = SITE_FILE_BASE + path
            elif kind == "runtime":
                if runtime_checkout is not None:
                    file_path, _, anchor = path.partition("#")
                    source_file = runtime_checkout / file_path
                    if not source_file.exists():
                        raise ValueError("Big Graph runtime source is absent: " + path)
                    if anchor:
                        match = re.fullmatch(r"L(\d+)(?:-L(\d+))?", anchor)
                        limit = len(source_file.read_text(errors="replace").splitlines())
                        if not match or int(match.group(1)) < 1 or int(match.group(2) or match.group(1)) > limit or int(match.group(2) or match.group(1)) < int(match.group(1)):
                            raise ValueError("Big Graph runtime source range is invalid: " + path)
                url = RUNTIME_FILE_BASE.format(tag=tag) + path
            else:
                raise ValueError("Big Graph has an unknown source kind: " + kind)
            evidence.append(dict(label=label, url=url))
        data.append(dict(id=id_, lane=lane, x=col, y=row, title=title, status=status,
                         short=short, detail=long, current=current, pending=pending,
                         evidence=evidence, specs=refs))
        cards.append('<button type="button" class="graph-node status-%s" id="graph-%s" '
                     'data-node="%s" data-lane="%s" aria-label="%s: %s. Open details" '
                     'aria-expanded="false" aria-controls="graph-inspector">'
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
            'assessments from the <a href="https://github.com/8007342/tillandsias.org/blob/main/docs/audit/2026-09-24-v56.9.21.1.md" '
            'target="_blank" rel="noopener">stable audit</a>, not runtime telemetry. '
            'Edges show intended interactions; dotted shortcut edges pass through hidden layers and do not prove a direct connection or enforcement.</p>'
            '<div class="graph-lanes" role="group" aria-label="Show or hide system layers">%s</div>'
            '</div><div class="graph-shell"><div class="graph-viewport" id="graph-viewport" '
            'aria-label="Scrollable architecture graph"><div class="graph-canvas" id="graph-canvas">'
            '%s<svg id="graph-lines" aria-hidden="true"></svg>%s</div></div>'
            '<aside class="graph-inspector" id="graph-inspector" aria-live="polite" hidden>'
            '<button type="button" class="graph-inspector-close" id="graph-inspector-close" '
            'aria-label="Close component details">×</button><div id="graph-inspector-body"></div></aside></div>'
            '<script type="application/json" id="graph-data">%s</script></section>' %
            (chips, bands, ''.join(cards), json.dumps({"nodes": data, "edges": EDGES,
                                                      "flows": FLOWS}).replace("<", "\\u003c")))


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
.graph-lane-toggle:disabled{cursor:wait}
.graph-shell{position:relative;flex:1;min-height:0;min-width:0}
.graph-viewport{width:100%;height:100%;overflow:auto;overscroll-behavior:contain;background:radial-gradient(circle at 1px 1px,#202b38 1px,transparent 0) 0 0/24px 24px,#0a0e13}
.graph-canvas{position:relative;min-width:100%;min-height:100%;transition:width .44s ease,height .44s ease}
.graph-band{position:absolute;left:0;right:0;height:210px;padding:8px 12px;border-top:1px solid #263442;background:linear-gradient(180deg,#14212b44,transparent 65%);pointer-events:none;z-index:0;transition:top .44s ease,opacity .2s ease}
.graph-band[hidden]{display:none}
.graph-band span{display:block;color:#8fb8cb;font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.12em}
.graph-band small{display:block;margin-top:3px;max-width:150px;color:var(--ink-faint);font:10px/1.4 var(--sans)}
#graph-lines{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:1;transition:opacity .18s ease}
#graph-lines.is-changing{opacity:0}
#graph-lines path{fill:none;stroke:#527384;stroke-width:2;opacity:.7;marker-end:url(#graph-arrow)}
#graph-lines path.edge-secret{stroke:#a48bf0}#graph-lines path.edge-git{stroke:#5fd6a4}
#graph-lines path.edge-boundary{stroke:#e6b45e;stroke-dasharray:5 5}
#graph-lines path.edge-goal{stroke:#777;stroke-dasharray:4 7}
#graph-lines path.edge-abstract{stroke:#7d99a7;stroke-dasharray:3 6;opacity:.6}
.graph-node{position:absolute;width:260px;min-height:126px;padding:12px 14px;text-align:left;color:var(--ink);background:#111b24;border:1px solid var(--leaf-dim);border-left:4px solid var(--leaf);border-radius:10px;box-shadow:0 8px 26px #0008;cursor:pointer;font:400 12px/1.4 var(--sans);z-index:2;transition:left .44s cubic-bezier(.2,.7,.2,1),top .44s cubic-bezier(.2,.7,.2,1),opacity .2s ease,transform .2s ease}
.graph-node.is-leaving,.graph-node.is-entering{opacity:0;transform:scale(.88);pointer-events:none}
.graph-node:hover,.graph-node:focus-visible,.graph-node.is-selected{outline:2px solid var(--sky);outline-offset:2px;z-index:3}
.graph-node.status-partial{border-color:#866a3d;border-left-color:var(--amber);border-style:dashed;background:#1b1a17}
.graph-node.status-goal{border-color:#4c535b;border-left-color:#87909b;border-style:dotted;background:#16191d;color:#b0bac4}
.graph-node-top{display:flex;justify-content:space-between;gap:8px;text-transform:uppercase;letter-spacing:.11em;color:var(--ink-faint);font:600 10px var(--mono)}
.graph-node strong{display:block;font-size:15px;line-height:1.25;margin:8px 0 5px}
.graph-short{display:block;color:var(--ink-dim)}
.graph-node[hidden]{display:none}
.graph-inspector{position:absolute;z-index:5;top:12px;right:16px;width:min(390px,calc(100vw - 32px));max-height:calc(100% - 24px);overflow:auto;padding:20px;border:1px solid var(--line-2);border-radius:11px;background:#0d151edc;backdrop-filter:blur(16px);box-shadow:0 16px 44px #000b}
.graph-inspector.is-left{left:16px;right:auto}
.graph-inspector[hidden]{display:none}
.graph-inspector-close{float:right;cursor:pointer;border:1px solid var(--line-2);background:var(--panel);border-radius:6px;color:var(--ink);font:20px/1 var(--sans);width:30px;height:30px}
.graph-inspector h3{margin:0 0 10px;font-size:18px}.graph-inspector h4{margin:20px 0 5px;color:var(--leaf);font-size:12px;text-transform:uppercase;letter-spacing:.1em}
.graph-inspector p,.graph-inspector li{color:var(--ink-dim);font-size:13px;line-height:1.6}
.graph-inspector .graph-state{font:600 11px var(--mono);text-transform:uppercase;color:var(--amber)}
.graph-inspector ul{padding-left:18px}
.graph-inspector .graph-detail-goal{padding:10px 12px;border-left:2px solid var(--sky);background:#12202b}
.graph-inspector .graph-pending{padding:10px 12px;border-left:2px dashed var(--amber);background:#261e14}
.graph-inspector .graph-source-list{list-style:none;padding:0}
.graph-inspector .graph-source-list li{margin:0 0 8px}
.graph-inspector .graph-source-list a{overflow-wrap:anywhere}
@media(max-width:700px){.graph-head{padding-right:10px}.graph-title{display:block}.graph-title h2{font-size:22px}.graph-title p{font-size:11px}.graph-honesty{font-size:10.5px}.graph-band small{display:none}.graph-inspector{top:auto;bottom:8px;right:8px;max-height:min(55vh,480px)}.graph-inspector.is-top{top:8px;bottom:auto}}
@media(prefers-reduced-motion:reduce){.graph-canvas,.graph-band,.graph-node,#graph-lines{transition:none}}
"""

JS = r"""
(function(){
  var dataEl=document.getElementById('graph-data'); if(!dataEl) return;
  var data=JSON.parse(dataEl.textContent), nodes=data.nodes, edges=data.edges, flows=data.flows;
  var byId={}; nodes.forEach(function(n){byId[n.id]=n});
  var canvas=document.getElementById('graph-canvas');
  var svg=document.getElementById('graph-lines'), inspector=document.getElementById('graph-inspector');
  var inspectorBody=document.getElementById('graph-inspector-body');
  var visible={}; nodes.forEach(function(n){visible[n.lane]=true});
  var selected=null, positions={}, animating=false;
  var buttons=[].slice.call(document.querySelectorAll('[data-toggle-lane]'));
  var bands=[].slice.call(document.querySelectorAll('[data-band]'));
  var reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fadeMs=reduced?0:210,moveMs=reduced?0:460;
  var raf=window.requestAnimationFrame||function(fn){setTimeout(fn,0)};
  var CARD_W=260,CARD_H=126,X_GAP=322,Y_GAP=220,LEFT=180,TOP=65;
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function layout(){
    var shownRows=[], placed={}, maxInRow=0;
    for(var row=0;row<bands.length;row++){
      var members=nodes.filter(function(n){return n.y===row&&visible[n.lane]});
      if(!members.length)continue;
      members.sort(function(a,b){return a.x-b.x});
      var compactRow=shownRows.length;shownRows.push(row);maxInRow=Math.max(maxInRow,members.length);
      members.forEach(function(n,col){placed[n.id]={col:col,row:compactRow,
        left:LEFT+col*X_GAP,top:TOP+compactRow*Y_GAP}});
    }
    return {positions:placed,rows:shownRows,
      width:LEFT+Math.max(0,maxInRow-1)*X_GAP+CARD_W+70,
      height:TOP+Math.max(0,shownRows.length-1)*Y_GAP+CARD_H+80};
  }
  function place(next){
    positions=next.positions;
    canvas.style.width=next.width+'px';canvas.style.height=next.height+'px';
    svg.setAttribute('viewBox','0 0 '+next.width+' '+next.height);
    bands.forEach(function(band){
      var row=Number(band.dataset.band),compactRow=next.rows.indexOf(row);
      band.hidden=compactRow<0;
      if(compactRow>=0)band.style.top=(TOP-35+compactRow*Y_GAP)+'px';
    });
    nodes.forEach(function(n){
      var el=document.getElementById('graph-'+n.id),point=positions[n.id];
      if(!point){el.hidden=true;return}
      if(el.hidden)el.classList.add('is-entering');
      el.hidden=false;el.style.left=point.left+'px';el.style.top=point.top+'px';
    });
    raf(function(){raf(function(){document.querySelectorAll('.graph-node.is-entering').forEach(function(el){el.classList.remove('is-entering')})})});
  }
  function edgePath(a,b){
    var ax=a.left,ay=a.top,bx=b.left,by=b.top,d;
    if(b.col>a.col){
      var x1=ax+CARD_W,y1=ay+CARD_H/2,x2=bx,y2=by+CARD_H/2;
      d='M'+x1+','+y1+' C'+(x1+40)+','+y1+' '+(x2-40)+','+y2+' '+x2+','+y2;
    }else if(b.col===a.col){
      var down=b.row>a.row,x1=ax+CARD_W/2,y1=ay+(down?CARD_H:0),x2=bx+CARD_W/2,y2=by+(down?0:CARD_H);
      d='M'+x1+','+y1+' C'+x1+','+((y1+y2)/2)+' '+x2+','+((y1+y2)/2)+' '+x2+','+y2;
    }else{
      var x1=ax+CARD_W/2,y1=ay,x2=bx+CARD_W/2,y2=by,turn=Math.min(y1,y2)-38;
      d='M'+x1+','+y1+' C'+x1+','+turn+' '+x2+','+turn+' '+x2+','+y2;
    }
    return d;
  }
  function drawEdges(){
    var out='<defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#6e8b98"/></marker></defs>';
    edges.forEach(function(e){
      var a=byId[e[0]],b=byId[e[1]],from=positions[a.id],to=positions[b.id];if(!from||!to)return;
      var goal=a.status==='goal'||b.status==='goal';
      var main=from.row===to.row&&to.col===from.col+1;
      out+='<path class="edge-'+esc(goal?'goal':e[3])+(main?' edge-main':'')+'" d="'+edgePath(from,to)+'"><title>'+esc(a.title+' → '+b.title+': '+e[2])+'</title></path>';
    });
    var direct={};edges.forEach(function(e){direct[e[0]+'>'+e[1]]=true});
    flows.forEach(function(flow){
      var shown=flow.filter(function(id){return !!positions[id]});
      for(var i=1;i<shown.length;i++){
        var fromId=shown[i-1],toId=shown[i];if(direct[fromId+'>'+toId])continue;
        out+='<path class="edge-abstract" d="'+edgePath(positions[fromId],positions[toId])+'"><title>'+esc(byId[fromId].title+' → '+byId[toId].title+': through hidden steps')+'</title></path>';
      }
    });
    svg.innerHTML=out;
  }
  function closeInspector(focusNode){
    var previous=selected;selected=null;inspector.hidden=true;
    document.querySelectorAll('.graph-node').forEach(function(el){el.classList.remove('is-selected');el.setAttribute('aria-expanded','false')});
    if(focusNode&&previous){var el=document.getElementById('graph-'+previous);if(el&&!el.hidden)el.focus()}
  }
  function inspect(id){
    if(selected===id&&!inspector.hidden){closeInspector(false);return}
    var n=byId[id];selected=id;inspector.hidden=false;
    var selectedBox=document.getElementById('graph-'+id).getBoundingClientRect();
    inspector.classList.toggle('is-left',selectedBox.left+selectedBox.width/2>window.innerWidth/2);
    inspector.classList.toggle('is-top',selectedBox.top+selectedBox.height/2>window.innerHeight/2);
    document.querySelectorAll('.graph-node').forEach(function(el){var on=el.dataset.node===id;el.classList.toggle('is-selected',on);el.setAttribute('aria-expanded',String(on))});
    var links=n.specs.map(function(url){var name=url.split('/').slice(-2,-1)[0];return '<li><a target="_blank" rel="noopener" href="'+esc(url)+'">'+esc(name)+'</a></li>'}).join('');
    var evidence=n.evidence.map(function(item){return '<li><a target="_blank" rel="noopener" href="'+esc(item.url)+'">'+esc(item.label)+'</a></li>'}).join('');
    var contacts=edges.filter(function(e){return e[0]===id||e[1]===id}).map(function(e){
      var other=byId[e[0]===id?e[1]:e[0]];return '<li>'+esc(e[0]===id?'To ':'From ')+esc(other.title)+' · '+esc(e[2])+'</li>'}).join('');
    var status=n.status==='goal'?'goal only':n.status+' at pinned release';
    var scopeHeading=n.status==='implemented'?'Scope and limits':'What is incomplete or pending';
    inspectorBody.innerHTML='<p class="graph-state">'+esc(status)+' · '+esc(n.lane)+' layer</p><h3>'+esc(n.title)+'</h3>'+
      '<h4>Goal-state role</h4><p class="graph-detail-goal">'+esc(n.detail)+'</p>'+
      '<h4>What exists now</h4><p>'+esc(n.current)+'</p>'+
      '<h4>'+esc(scopeHeading)+'</h4><p class="graph-pending">'+esc(n.pending)+'</p>'+
      '<h4>Source and work records</h4><ul class="graph-source-list">'+evidence+'</ul>'+
      '<h4>Interactions</h4><ul>'+contacts+'</ul>'+
      '<h4>Goal-state specifications</h4><ul class="graph-source-list">'+links+'</ul>'+
      '<p><a href="#progress">See the accountability ledger</a></p>';
  }
  document.querySelectorAll('.graph-node').forEach(function(el){el.addEventListener('click',function(){inspect(el.dataset.node)})});
  document.getElementById('graph-inspector-close').addEventListener('click',function(){closeInspector(true)});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!inspector.hidden)closeInspector(true)});
  buttons.forEach(function(button){button.addEventListener('click',function(){
    if(animating)return;
    var lane=button.dataset.toggleLane;visible[lane]=!visible[lane];button.setAttribute('aria-pressed',String(visible[lane]));
    if(selected&&!visible[byId[selected].lane])closeInspector(false);
    var leaving=nodes.filter(function(n){return !visible[n.lane]&&!document.getElementById('graph-'+n.id).hidden});
    animating=true;buttons.forEach(function(b){b.disabled=true});svg.classList.add('is-changing');
    leaving.forEach(function(n){document.getElementById('graph-'+n.id).classList.add('is-leaving')});
    setTimeout(function(){
      leaving.forEach(function(n){var el=document.getElementById('graph-'+n.id);el.hidden=true;el.classList.remove('is-leaving')});
      place(layout());
      setTimeout(function(){drawEdges();svg.classList.remove('is-changing');animating=false;buttons.forEach(function(b){b.disabled=false})},moveMs);
    },fadeMs);
  })});
  place(layout());drawEdges();
})();
"""
