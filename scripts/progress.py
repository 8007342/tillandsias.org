"""The site's build-time accountability ledger, rendered without runtime fetches."""
import html
import json
import pathlib
import re

import issues

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/progress/runtime-specs.json"
SEVERITY = {"high": 0, "medium": 1, "low": 2}


def esc(value):
    return html.escape(str(value or ""), quote=True)


def paragraphs(value):
    if not value:
        return ""
    if isinstance(value, list):
        value = "\n".join(str(part) for part in value)
    return "".join("<p>%s</p>" % esc(part) for part in re.split(r"\n\s*\n", str(value)) if part.strip())


def field(label, value):
    return ('<div class="ledger-field"><h5>%s</h5>%s</div>' % (esc(label), paragraphs(value))) if value else ""


def finding(f):
    events = f.get("events", [])
    when = events[-1].get("ts", "")[:10] if events else "undated"
    detail = "".join(field(label, f.get(key)) for label, key in (
        ("Claim", "claim"), ("Code / observed behavior", "code"),
        ("Why it matters", "why"), ("Remedy / check", "fix")))
    evidence = f.get("evidence", [])
    if evidence:
        evidence_rows = []
        for item in evidence:
            if isinstance(item, dict):
                path = item.get("path", "")
                ref = f.get("tag", "")
                href = "https://github.com/8007342/tillandsias/blob/%s/%s" % (ref, path)
                evidence_rows.append('<li><a href="%s" target="_blank" rel="noopener">%s</a>'
                                     '%s</li>' % (esc(href), esc(path),
                                                 (" — “%s”" % esc(item.get("quote"))) if item.get("quote") else ""))
            else:
                evidence_rows.append("<li>%s</li>" % esc(item))
        detail += '<div class="ledger-field"><h5>Evidence</h5><ul>%s</ul></div>' % "".join(evidence_rows)
    if f.get("depends_on"):
        detail += field("Depends on", ", ".join(f["depends_on"]))
    if f.get("upstream"):
        detail += '<p><a href="%s" target="_blank" rel="noopener">Upstream issue ↗</a></p>' % esc(f["upstream"])
    elif f.get("repo") == "tillandsias":
        detail += '<p class="muted">No upstream issue filed.</p>'
    if events:
        detail += '<div class="ledger-field"><h5>History</h5><ol>%s</ol></div>' % "".join(
            "<li><time>%s</time> · %s%s</li>" %
            (esc(e.get("ts", "")), esc(e.get("type", "event")),
             (" — " + esc(e.get("note"))) if e.get("note") else "") for e in events)
    detail += field("Classification and release", "%s · %s · %s" %
                    (f.get("class", ""), f.get("tag", ""), f.get("commit", "")))
    return ('<details class="ledger-card finding sev-%s" data-ledger-item data-search="%s">'
            '<summary><span class="ledger-code">%s</span><span class="ledger-title">%s</span>'
            '<span class="ledger-badge">%s</span><span class="ledger-meta">%s · %s · %s</span></summary>'
            '<div class="ledger-detail">%s</div></details>' %
            (esc(f.get("severity", "low")), esc(" ".join(str(f.get(k, "")) for k in ("id", "title", "area", "repo", "severity"))),
             esc(f["id"]), esc(f.get("title", "Untitled finding")), esc(f.get("severity", "")),
             esc(f.get("repo", "")), esc(f.get("area", "")), esc(when), detail))


def runtime_spec(s):
    status = s["status"]
    lowered = status.lower()
    lifecycle = ("retired" if any(word in lowered for word in ("obsolete", "deprecated", "retired"))
                 else "draft" if any(word in lowered for word in ("draft", "proposed", "unspecified"))
                 else "current")
    requirements = s["requirements"]
    req_html = ('<div class="ledger-field"><h5>Requirements (%d)</h5><ol>%s</ol></div>' %
                (len(requirements), "".join("<li>%s</li>" % esc(name) for name in requirements))) if requirements else ""
    return ('<details class="ledger-card spec %s" data-ledger-item data-search="%s">'
            '<summary><span class="ledger-code">spec</span><span class="ledger-title">%s</span>'
            '<span class="ledger-badge">%s</span><span class="ledger-meta">%d requirements</span></summary>'
            '<div class="ledger-detail"><p>%s</p><p class="muted">Document status: %s. '
            'This describes the spec’s lifecycle, not verified implementation.</p>'
            '%s<p><a href="%s" target="_blank" rel="noopener">Read full pinned spec ↗</a></p></div></details>' %
            (lifecycle, esc(s["id"] + " " + s["purpose"] + " " + status + " " + " ".join(requirements)), esc(s["id"]),
             esc(status), len(requirements), esc(s["purpose"]), esc(status), req_html, esc(s["url"])))


def change(c, site=False):
    complete = c["open"] == 0 and c["done"] > 0
    has_tasks = c.get("has_tasks", True)
    label = "No checklist" if not has_tasks else "Checklist complete" if complete else "Open tasks"
    tasks = c.get("tasks", [])
    task_html = ('<div class="ledger-field"><h5>Task record</h5><ul class="task-list">%s</ul></div>' %
                 "".join('<li><span aria-label="%s">%s</span> %s</li>' %
                         ("checked" if t["checked"] else "open", "☑" if t["checked"] else "☐", esc(t["text"]))
                         for t in tasks)) if tasks else ""
    return ('<details class="ledger-card change %s" data-ledger-item data-search="%s">'
            '<summary><span class="ledger-code">%s</span><span class="ledger-title">%s</span>'
            '<span class="ledger-badge">%s</span><span class="ledger-meta">%d checked · %d open</span></summary>'
            '<div class="ledger-detail"><p>%s</p><p class="muted">%s</p>'
            '%s<p><a href="%s" target="_blank" rel="noopener">Read source record ↗</a></p></div></details>' %
            ("complete" if complete else "partial", esc(c["id"] + " " + c["title"] + " " + c.get("summary", "")),
             "site" if site else "change", esc(c["title"]), label, c["done"], c["open"],
             esc(c.get("summary") or c["id"]),
             "No task record was present in this archived change." if not has_tasks else
             "A checked archival task list records work, not proof that every goal-state behavior still works now.",
             task_html, esc(c["url"])))


def site_changes():
    base = "https://github.com/8007342/tillandsias.org/blob/main/"
    rows = []
    for path in sorted((ROOT / "openspec/changes").glob("*/tasks.md")):
        source = path.read_text()
        proposal = path.with_name("proposal.md")
        proposal_source = proposal.read_text() if proposal.exists() else ""
        heading = re.search(r"^#\s+(.+)$", proposal_source, re.M)
        paragraphs = [re.sub(r"\s+", " ", block).strip() for block in re.split(r"\n\s*\n", proposal_source)
                      if block.strip() and not block.lstrip().startswith(("#", "- "))]
        tasks = [{"checked": mark.lower() == "x", "text": title.strip()}
                 for mark, title in re.findall(r"^\s*- \[([ xX])\]\s*(.+)$", source, re.M)]
        rows.append({"id": path.parent.name, "title": heading.group(1) if heading else path.parent.name,
                     "summary": paragraphs[0][:360] if paragraphs else "",
                     "done": sum(t["checked"] for t in tasks),
                     "open": sum(not t["checked"] for t in tasks), "tasks": tasks,
                     "url": base + path.relative_to(ROOT).as_posix()})
    return rows


def render(site_ref):
    catalog = json.loads(CATALOG.read_text())
    if catalog["tag"] != site_ref:
        raise ValueError("spec snapshot %s does not match site pin %s" % (catalog["tag"], site_ref))
    state = issues.fold()
    cols = {"red": [], "yellow": [], "green": []}
    for f in state.values():
        cols[f.get("column", "red")].append(f)
    for rows in cols.values():
        rows.sort(key=lambda f: (SEVERITY.get(f.get("severity"), 3), f["id"]))
    archived = catalog["changes"]
    local = site_changes()
    complete_changes = [c for c in archived if c["open"] == 0 and c["done"] > 0]
    other_changes = [c for c in archived if c not in complete_changes]
    complete = len(complete_changes)
    sections = []
    for key, title, desc in (
        ("red", "Waiting", "Found findings needing a supported remedy."),
        ("yellow", "Tracked", "Triaged, filed, active, blocked or terminal without a verified fix."),
        ("green", "Resolved", "Remedies checked in this website’s audit record.")):
        sections.append('<section class="ledger-group" data-ledger-group><h3>%s <span>%d</span></h3>'
                        '<p>%s</p><div class="ledger-list">%s</div></section>' %
                        (title, len(cols[key]), desc, "".join(finding(f) for f in cols[key])))
    sections.append('<section class="ledger-group" data-ledger-group><h3>Runtime specifications '
                    '<span>%d</span></h3><p>All canonical specs at %s, including retired documents. '
                    'Status here is the document’s own lifecycle label.</p><div class="ledger-list">%s</div></section>' %
                    (len(catalog["specs"]), esc(site_ref), "".join(runtime_spec(s) for s in catalog["specs"])))
    sections.append('<section class="ledger-group" data-ledger-group><h3>Completed change checklists '
                    '<span>%d</span></h3><p>Every recorded task was checked before archive. '
                    'Current runtime behavior still needs separate evidence.</p><div class="ledger-list">%s</div></section>' %
                    (complete, "".join(change(c) for c in complete_changes)))
    sections.append('<section class="ledger-group" data-ledger-group><h3>Other archived changes '
                    '<span>%d</span></h3><p>Open tasks or no checklist were recorded. '
                    'These records remain part of the source history.</p><div class="ledger-list">%s</div></section>' %
                    (len(other_changes), "".join(change(c) for c in other_changes)))
    sections.append('<section class="ledger-group" data-ledger-group><h3>Website changes '
                    '<span>%d</span></h3><p>Local site contracts and their task records, including this page’s change.</p>'
                    '<div class="ledger-list">%s</div></section>' %
                    (len(local), "".join(change(c, True) for c in local)))
    return ('<section class="view" id="view-progress" role="tabpanel" aria-labelledby="nav-progress">'
            '<div class="wrap ledger"><h2 class="view-h">Live progress</h2>'
            '<p class="view-lede">The accountability ledger: findings, the full pinned runtime spec '
            'inventory, and recorded change checklists. Every entry starts collapsed; open it for '
            'evidence or source. This is a build-time snapshot, not live telemetry.</p>'
            '<div class="ledger-stats"><span><b>%d</b> findings</span><span><b>%d</b> resolved</span>'
            '<span><b>%d</b> runtime specs</span><span><b>%d</b> archived changes</span>'
            '<span><b>%d</b> checklists complete</span></div>'
            '<p class="ledger-note">“Complete” means all tasks in that archived checklist are checked. '
            'It does not certify current runtime behavior. The canonical spec status (“active”, '
            '“obsolete”, etc.) describes document lifecycle. See the '
            '<a href="https://github.com/8007342/tillandsias.org/blob/main/docs/audit/2026-09-22-v56.9.21.1.md" '
            'target="_blank" rel="noopener">stable audit</a> for checked capability limits.</p>'
            '<label class="ledger-search-label" for="ledger-search">Find a spec, change or finding</label>'
            '<input id="ledger-search" class="ledger-search" type="search" autocomplete="off" '
            'placeholder="Search titles, IDs and summaries"><p class="ledger-results" id="ledger-results" aria-live="polite"></p>'
            '%s</div></section>' % (len(state), len(cols["green"]), len(catalog["specs"]),
                                   len(archived), complete, "".join(sections)))
