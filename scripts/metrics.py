#!/usr/bin/env python3
"""Residual-obligation history: extracted from runtime git history, kept as an
append-only evidence file, drawn at build time on a logarithmic time axis.

Every row is recomputable from the runtime repository: it names the commit and
path it was read from. The extract never rewrites or deletes a stored row; a
row found to be wrong is withdrawn by appending a `retract` row with a reason,
the way issues.d withdraws a published claim. So the series is a grow-only set
keyed by (series, t, key), the same CRDT shape as the findings ledger, and a
re-run over the same history is a no-op.

Sources (all read at, or before, the pinned release tag):

  cc_residual       docs/convergence/centicolon-dashboard.json, the union of
                    the `history[]` rows across every committed revision (the
                    file keeps a sliding window, so one revision is not the
                    history). residual_cc with total_cc as its budget. This is
                    what the runtime's observatorium plotted.
  floor:<name>      scripts/portability/<name>-floor.txt, one row per revision:
                    the count of entries in a ratchet floor, i.e. the carried
                    obligations a gate refuses to let grow (methodology
                    convergence.yaml `carried_obligations`).
  openspec_open     unchecked `- [ ]` tasks across active (unarchived)
                    openspec/changes/*/tasks.md, newest first-parent commit per
                    day: declared scope still open. Context, not a residual.

Milestones: the first release tag of each version series, the pinned tag,
and each `approved_bar_raises` entry in methodology/convergence.yaml.

  metrics.py extract --repo DIR --ref vTAG   append new rows; prints counts
  metrics.py verify  --repo DIR --ref vTAG   every stored row reproduces
Last line: `ok:metrics:<added>` / `ok:metrics-verified:<n>` or `blocked:<why>`.
"""
import html
import json
import math
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERIES = ROOT / "docs" / "metrics" / "series.jsonl"
REFRESH = ROOT / "refresh.d"
REPO_SLUG = "8007342/tillandsias"
DASHBOARD = "docs/convergence/centicolon-dashboard.json"
FLOORS = ("shell-decider", "pipe-site", "jq-callsite")


# --- extraction ---------------------------------------------------------------

def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True,
                          text=True, check=True).stdout


def utc(ts):
    """Any ISO-8601 timestamp -> `YYYY-MM-DDTHH:MM:SSZ`."""
    d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def revisions(repo, ref, path):
    """(commit, committer-date) of every revision of `path` reachable from ref, oldest first."""
    out = git(repo, "log", "--reverse", "--format=%H %cI", ref, "--", path)
    return [tuple(line.split()) for line in out.splitlines() if line.strip()]


def src(commit, path):
    return {"repo": REPO_SLUG, "commit": commit, "path": path}


def extract_dashboard(repo, ref):
    rows, seen = [], {}
    for commit, _ in revisions(repo, ref, DASHBOARD):
        try:
            doc = json.loads(git(repo, "show", "%s:%s" % (commit, DASHBOARD)))
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            continue
        for h in doc.get("history") or []:
            if not isinstance(h, dict) or h.get("residual_cc") is None or not h.get("date"):
                continue
            t = utc(h["date"])
            key = "%s|%s" % (h.get("release", ""), h.get("commit", ""))
            # First sighting wins: the oldest revision that recorded the row
            # is its provenance, and later windows repeat it.
            if (t, key) in seen:
                continue
            seen[(t, key)] = True
            rows.append({"series": "cc_residual", "t": t, "key": key, "v": h["residual_cc"],
                         "budget": h.get("total_cc"), "earned": h.get("earned_cc"),
                         "release": h.get("release", ""), "measured_at": h.get("commit", ""),
                         "src": src(commit, DASHBOARD)})
    return rows


def extract_floors(repo, ref):
    rows = []
    for name in FLOORS:
        path = "scripts/portability/%s-floor.txt" % name
        for commit, date in revisions(repo, ref, path):
            text = git(repo, "show", "%s:%s" % (commit, path))
            n = sum(1 for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#"))
            rows.append({"series": "floor:" + name, "t": utc(date), "key": commit[:12], "v": n,
                         "src": src(commit, path)})
    return rows


def extract_openspec(repo, ref):
    rows, days = [], {}
    for line in git(repo, "log", "--first-parent", "--format=%H %cI", ref).splitlines():
        commit, date = line.split()
        days.setdefault(utc(date)[:10], (commit, date))  # newest commit of each day
    for day in sorted(days):
        commit, date = days[day]
        out = subprocess.run(["git", "-C", str(repo), "grep", "-h", "-E", r"^\s*- \[ \]", commit, "--",
                              "openspec/changes/*/tasks.md", ":!openspec/changes/archive/**"],
                             capture_output=True, text=True, check=False).stdout
        rows.append({"series": "openspec_open", "t": utc(date), "key": commit[:12],
                     "v": len(out.splitlines()), "src": src(commit, "openspec/changes/*/tasks.md")})
    return rows


def extract_milestones(repo, ref):
    rows, first = [], {}
    out = git(repo, "for-each-ref", "--merged", ref, "--sort=creatordate",
              "--format=%(refname:short) %(creatordate:iso-strict) %(*objectname)%(objectname)",
              "refs/tags/v*")
    for line in out.splitlines():
        tag, date, obj = line.split()[:3]
        m = re.match(r"^(v\d+\.\d+)\.", tag)
        if m and m.group(1) not in first:
            first[m.group(1)] = tag
            rows.append({"series": "milestone", "t": utc(date), "key": tag, "kind": "series",
                         "label": "%s series" % m.group(1), "src": src(obj[:40], "refs/tags/" + tag)})
        if tag == ref:
            rows.append({"series": "milestone", "t": utc(date), "key": tag, "kind": "pin",
                         "label": "pinned %s" % tag, "src": src(obj[:40], "refs/tags/" + tag)})
    conv = "methodology/convergence.yaml"
    try:
        text = git(repo, "show", "%s:%s" % (ref, conv))
    except subprocess.CalledProcessError:
        text = ""
    block = re.search(r"^approved_bar_raises:\n((?:[ -].*\n|\n)*)", text, re.M)
    commit = git(repo, "rev-parse", ref + "^{commit}").strip()
    for m in re.finditer(r"- id: (\S+)\n(?:\s+.*\n)*?\s+approved_at: \"?([\d-]+)", block.group(1) if block else ""):
        rows.append({"series": "milestone", "t": m.group(2) + "T00:00:00Z", "key": m.group(1),
                     "kind": "bar", "label": "bar raised: " + m.group(1), "src": src(commit, conv)})
    return rows


def extract(repo, ref):
    return (extract_dashboard(repo, ref) + extract_floors(repo, ref)
            + extract_openspec(repo, ref) + extract_milestones(repo, ref))


# --- the append-only store ----------------------------------------------------

def row_id(r):
    return (r["series"], r["t"], r["key"])


def load():
    rows, retracted = [], set()
    if SERIES.exists():
        for line in SERIES.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("series") == "retract":
                retracted.add(tuple(r["of"]))
            else:
                rows.append(r)
    return [r for r in rows if row_id(r) not in retracted], rows, retracted


def append(new_rows):
    _, stored, _ = load()
    have = {row_id(r) for r in stored}
    fresh = sorted((r for r in new_rows if row_id(r) not in have), key=lambda r: (r["series"], r["t"], r["key"]))
    if fresh:
        SERIES.parent.mkdir(parents=True, exist_ok=True)
        with SERIES.open("a") as f:
            for r in fresh:
                f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    return len(fresh)


def verify(repo, ref):
    """Every stored, unretracted row whose source is reachable from ref must be
    reproduced exactly by a fresh extraction: provenance that does not replay
    is not provenance."""
    live, _, _ = load()
    fresh = {row_id(r): r for r in extract(repo, ref)}
    bad = []
    for r in live:
        f = fresh.get(row_id(r))
        if f is None and r.get("kind") == "pin":
            # A pin milestone belongs to the tag it names, not to today's ref.
            f = {row_id(x): x for x in extract_milestones(repo, r["key"])}.get(row_id(r))
        if f is None:
            reach = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                                    r["src"]["commit"], ref], capture_output=True).returncode
            if reach == 0:
                bad.append((r, "not reproduced"))
        elif json.dumps(f, sort_keys=True) != json.dumps(r, sort_keys=True):
            bad.append((r, "differs on replay"))
    return live, bad


# --- reading ------------------------------------------------------------------

def series():
    live, _, _ = load()
    out = {}
    for r in live:
        out.setdefault(r["series"], []).append(r)
    for rows in out.values():
        rows.sort(key=lambda r: (r["t"], r["key"]))
    return out


def regimes(rows):
    """The accepted-baseline view of cc_residual, derived and labelled as such.

    The dashboard interleaves runs over different scopes (a budget of 120 is a
    single gate, 750 the whole suite), and a residual is comparable only under
    one scope. Per calendar week the scope with the most runs is the dominant
    one; its runs, in order, form one regime until the dominant budget changes.
    Within a regime the line is the best residual reached so far: monotone by
    construction, which is exactly why the raw runs are drawn beside it."""
    weeks = {}
    for r in rows:
        wk = datetime.strptime(r["t"][:10], "%Y-%m-%d").isocalendar()[:2]
        weeks.setdefault(wk, {}).setdefault(r["budget"], 0)
        weeks[wk][r["budget"]] += 1
    dom = {wk: max(c.items(), key=lambda kv: (kv[1], kv[0]))[0] for wk, c in weeks.items()}
    segs = []
    for r in rows:
        wk = datetime.strptime(r["t"][:10], "%Y-%m-%d").isocalendar()[:2]
        if r["budget"] != dom[wk]:
            continue
        if not segs or segs[-1][0]["budget"] != r["budget"]:
            segs.append([])
        best = min(r["v"], segs[-1][-1]["v"]) if segs[-1] else r["v"]
        segs[-1].append(dict(r, v=best, raw=r["v"]))
    return segs


def raw_rises(rows):
    """Rises between consecutive runs of the same budget: regressions the raw
    record shows, before any baseline is taken."""
    last, n = {}, 0
    for r in rows:
        b = r["budget"]
        if b in last and r["v"] > last[b]:
            n += 1
        last[b] = r["v"]
    return n


def rises(rows):
    return sum(1 for a, b in zip(rows, rows[1:]) if b["v"] > a["v"])


def ts(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def gh(s):
    return "https://github.com/%s/blob/%s/%s" % (s["repo"], s["commit"], s["path"])


def gh_commit(s):
    return "https://github.com/%s/commit/%s" % (s["repo"], s["commit"])


# --- the refine ledger ---------------------------------------------------------

def refresh_fragments():
    out = []
    for p in sorted(REFRESH.glob("*.json")) if REFRESH.is_dir() else []:
        doc = json.loads(p.read_text())
        doc["_file"] = p.name
        out.append(doc)
    return sorted(out, key=lambda d: (d.get("ts", ""), d["_file"]))


READER = ROOT / "docs" / "progress" / "improvements.json"


def improvements_html(surface, title="How this section has improved"):
    """What changed for the reader, in plain words, newest first. This comes
    from docs/progress/improvements.json, which is written for readers and
    only grows. The refresh.d/ ledger is the internal record for the next run
    and is never displayed."""
    rows = [r for r in (json.loads(READER.read_text()) if READER.exists() else [])
            if surface in r.get("surfaces", [])]
    if not rows:
        return ""
    rows = sorted(rows, key=lambda r: r["month"], reverse=True)[:5]
    items = "".join('<li><time>%s</time> %s</li>' % (
        datetime.strptime(r["month"], "%Y-%m").strftime("%B %Y"), html.escape(r["text"])) for r in rows)
    return ('<details class="improved"><summary>%s</summary><ul>%s</ul></details>'
            % (html.escape(title), items))


def reviewed_at():
    """slug -> the release a human last reviewed that level's claims against."""
    out = {}
    for doc in refresh_fragments():
        out.update(doc.get("reviewed", {}))
    return out


# --- drawing --------------------------------------------------------------------

W, PAD_L, PAD_R = 960, 64, 150
PANEL_H, GAP, TOP = 132, 34, 46
TICKS = [(0, "pin"), (1, "1 day"), (7, "1 week"), (30, "1 month"), (91, "3 months")]
COLORS = {"floor:shell-decider": ("var(--leaf)", ""), "floor:pipe-site": ("var(--sky)", "6 4"),
          "floor:jq-callsite": ("var(--amber)", "2 3")}
LABELS = {"floor:shell-decider": "scripts to rewrite", "floor:pipe-site": "fragile pipelines",
          "floor:jq-callsite": "JSON tool calls"}
NAMES = {"floor:shell-decider": "Shell scripts still to be rewritten in Lua",
         "floor:pipe-site": "Fragile shell pipelines still to be replaced",
         "floor:jq-callsite": "Calls to an external JSON tool still to be replaced"}


def milestone_text(m):
    """(short label, tooltip) for a milestone, in plain words."""
    if m["kind"] == "series":
        v = m["key"].rsplit(".", 2)[0]
        return v, "First %s release" % v
    if m["kind"] == "bar":
        return "stricter", "The project raised its own quality bar"
    return m["key"], "This release, %s" % m["key"]
TAU = 3.0  # days of grace before the logarithm takes hold


class Axis:
    """Logarithmic in age before the pin: x = 1 - ln(1+age/TAU)/ln(1+span/TAU),
    age in days. The pin sits at the right edge and the first commit at the
    left; each step left covers more calendar time than the one before it."""

    def __init__(self, t_ref, t_first):
        self.t_ref = t_ref
        self.span = max((t_ref - t_first) / 86400.0, 1.0)
        self.k = math.log1p(self.span / TAU)

    def x(self, t):
        age = min(max((self.t_ref - t) / 86400.0, 0.0), self.span)
        return PAD_L + (W - PAD_L - PAD_R) * (1 - math.log1p(age / TAU) / self.k)


def _path(points):
    """A step path: a count holds its value until the next observation."""
    d = []
    for i, (x, y) in enumerate(points):
        if i == 0:
            d.append("M%.1f %.1f" % (x, y))
        else:
            d.append("H%.1f V%.1f" % (x, y))
    return " ".join(d)


def _panel(i, title, note, axis, lines, vmax, dots=(), vmin=0, shown=None):
    y0 = TOP + i * (PANEL_H + GAP)
    shown = shown or (lambda r: r["v"])

    def y(v):
        return y0 + PANEL_H - (PANEL_H - 10) * ((v - vmin) / (vmax - vmin) if vmax > vmin else 0)

    out = ['<g class="mx-panel">',
           '<text class="mx-title" x="%d" y="%d">%s</text>' % (PAD_L, y0 - 10, html.escape(title)),
           '<text class="mx-note" x="%d" y="%d" text-anchor="end">%s</text>' % (W - PAD_R, y0 - 10, html.escape(note))]
    for frac in (0, 0.5, 1):
        v = vmin + (vmax - vmin) * frac
        out.append('<line class="mx-grid" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>'
                   '<text class="mx-yl" x="%d" y="%.1f" text-anchor="end">%s</text>'
                   % (PAD_L, W - PAD_R, y(v), y(v), PAD_L - 8, y(v) + 4,
                      ("%+d" % round(v) if vmin < 0 else "{:,}".format(int(round(v)))) if v else "0"))
    for r in dots:
        out.append('<circle class="mx-dot" cx="%.1f" cy="%.1f" r="1.6"><title>%s: %s still open out of %s</title></circle>'
                   % (axis.x(ts(r["t"])), y(r["v"]), r["t"][:10], r["v"], r.get("budget")))
    labels = []
    for name, segs, color, dash, label in lines:
        last = None
        for seg in segs:
            pts = [(axis.x(ts(r["t"])), y(r["v"])) for r in seg]
            if not pts:
                continue
            pts.append((axis.x(axis.t_ref) if seg is segs[-1] and name != "cc_residual" else pts[-1][0], pts[-1][1]))
            out.append('<path class="mx-line" d="%s" stroke="%s"%s/>'
                       % (_path(pts), color, ' stroke-dasharray="%s"' % dash if dash else ""))
            for r in (seg if name != "cc_residual" else ()):
                out.append('<circle class="mx-hit" cx="%.1f" cy="%.1f" r="6"><title>%s · %s: %s%s</title></circle>'
                           % (axis.x(ts(r["t"])), y(r["v"]), html.escape(label), r["t"][:16].replace("T", " "),
                              "{:,}".format(shown(r)),
                              (" out of %s" % r.get("budget") if r.get("budget") else "")))
            last = pts[-1]
        if last:
            tail = segs[-1][-1]
            when = "" if name != "cc_residual" else datetime.strptime(tail["t"][:10], "%Y-%m-%d").strftime(" (%b %-d)")
            labels.append([last[1] + 4, "%s %s%s" % ("{:,}".format(shown(tail)), label, when)])
    # Direct labels never overlap: push each one below the one above it.
    labels.sort()
    for k in range(1, len(labels)):
        labels[k][0] = max(labels[k][0], labels[k - 1][0] + 12)
    for yy, text in labels:
        out.append('<text class="mx-dl" x="%.1f" y="%.1f">%s</text>' % (W - PAD_R + 8, yy, html.escape(text)))
    out.append('</g>')
    return "\n".join(out), y0


def render_chart(data, t_ref, milestones):
    firsts = [ts(rows[0]["t"]) for rows in data.values() if rows]
    axis = Axis(t_ref, min(firsts))
    panels, tops = [], []
    cc = data.get("cc_residual", [])
    segs = regimes(cc)
    vmax = max([r["v"] for r in cc] + [1])
    p, y0 = _panel(0, "Open obligations, as measured by each test run (CentiColons)",
                   "dots: each run · line: lowest reached", axis,
                   [("cc_residual", segs, "var(--violet)", "", "lowest")], vmax, dots=cc)
    panels.append(p)
    tops.append(y0)
    # Indexed to each floor's first entry: three counts of different size on
    # one axis, as change since the floor was set (one y-scale, no dual axis).
    floors = []
    for n in COLORS:
        if data.get(n):
            base = data[n][0]["v"]
            floors.append((n, [[dict(r, v=r["v"] - base, abs=r["v"]) for r in data[n]]],
                           COLORS[n][0], COLORS[n][1], LABELS[n]))
    deltas = [r["v"] for _, s, *_ in floors for r in s[0]] + [0]
    p, y0 = _panel(1, "Clean-up work the build will not let grow: change since tracking began",
                   "lower is better", axis, floors, max(deltas + [1]), vmin=min(deltas + [-1]),
                   shown=lambda r: r.get("abs", r["v"]))
    panels.append(p)
    tops.append(y0)
    op = data.get("openspec_open", [])
    p, y0 = _panel(2, "Planned work still open in the design documents",
                   "rises when new work is planned", axis, [("openspec_open", [op], "var(--ink-dim)", "", "open tasks")],
                   max([r["v"] for r in op] + [1]))
    panels.append(p)
    tops.append(y0)
    bottom = tops[-1] + PANEL_H
    ticks = []
    for days, label in TICKS:
        if days <= axis.span:
            x = axis.x(t_ref - days * 86400)
            ticks.append('<line class="mx-tick" x1="%.1f" x2="%.1f" y1="%d" y2="%d"/>'
                         '<text class="mx-xl" x="%.1f" y="%d" text-anchor="middle">%s</text>'
                         % (x, x, TOP - 4, bottom, x, bottom + 16, label + (" ago" if days else "")))
    first = datetime.fromtimestamp(axis.t_ref - axis.span * 86400, timezone.utc).strftime("%Y-%m-%d")
    ticks.append('<text class="mx-xl" x="%d" y="%d">%s</text>' % (PAD_L, bottom + 32, first))
    ticks.append('<text class="mx-xl" x="%d" y="%d" text-anchor="end">%s</text>'
                 % (W - PAD_R, bottom + 32, datetime.fromtimestamp(t_ref, timezone.utc).strftime("%Y-%m-%d")))
    marks, last_x, last_w = [], -999, 0
    for m in sorted(milestones, key=lambda r: r["t"]):
        x = axis.x(ts(m["t"]))
        cls = "mx-ms mx-ms-%s" % m["kind"]
        text, tip = milestone_text(m)
        marks.append('<line class="%s" x1="%.1f" x2="%.1f" y1="%d" y2="%d"><title>%s, %s</title></line>'
                     % (cls, x, x, 18, bottom, html.escape(tip), m["t"][:10]))
        # Labels only where they fit; every marker keeps its tooltip.
        w = 6.2 * len(text)
        if x - last_x > (w + last_w) / 2 + 8:
            marks.append('<text class="mx-msl" x="%.1f" y="14" text-anchor="middle">%s</text>'
                         % (x, html.escape(text)))
            last_x, last_w = x, w
    h = bottom + 44
    return ('<svg class="mx-svg" viewBox="0 0 %d %d" role="img" aria-labelledby="mx-cap">%s%s%s</svg>'
            % (W, h, "".join(marks), "".join(panels), "".join(ticks)))


def summary_rows(data):
    rows = []
    for name, label in [("cc_residual", "Open obligations per test run")] + \
            [(n, NAMES[n]) for n in COLORS] + [("openspec_open", "Planned work still open")]:
        s = data.get(name)
        if not s:
            continue
        if name == "cc_residual":
            segs = regimes(s)
            verdict = ("went up %d times from one run to the next; the lowest-reached line only goes down"
                       % raw_rises(s))
        elif name.startswith("floor:"):
            k = rises(s)
            verdict = "never went up" if k == 0 else "went up %s" % ("once" if k == 1 else "%d times" % k)
        else:
            verdict = "grew by %d as work was planned" % (s[-1]["v"] - s[0]["v"])
        rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td>'
                    '<td class="num">%d</td><td>%s</td><td><a href="%s" target="_blank" rel="noopener">first</a> · '
                    '<a href="%s" target="_blank" rel="noopener">last</a></td></tr>'
                    % (html.escape(label), s[0]["t"][:10], s[-1]["t"][:10], "{:,}".format(s[0]["v"]),
                       "{:,}".format(s[-1]["v"]), len(s), html.escape(verdict), gh(s[0]["src"]), gh(s[-1]["src"])))
    return "".join(rows)


def render(site_ref):
    data = series()
    if not data:
        return ""
    ms = data.pop("milestone", [])
    pins = [m for m in ms if m["kind"] == "pin" and m["key"] == site_ref]
    if not pins:
        raise ValueError("metrics: no pin milestone for %s; run metrics.py extract --ref %s" % (site_ref, site_ref))
    t_ref = ts(pins[0]["t"])
    shown = [m for m in ms if m["kind"] != "pin" or m["key"] == site_ref]
    cc = data.get("cc_residual", [])
    gap = ""
    if cc:
        stale = (t_ref - ts(cc[-1]["t"])) / 86400
        gap = ('<p class="ledger-note">The test runs stopped publishing this measure on %s, %d days before '
               'this release. The chart leaves that stretch empty rather than guess. The clean-up counts are '
               'the only measures that continue past it.</p>'
               % (datetime.strptime(cc[-1]["t"][:10], "%Y-%m-%d").strftime("%-d %B %Y"), stale))
    return ('<section class="metrics" id="metrics" aria-labelledby="metrics-h">'
            '<h3 id="metrics-h">How much work is still open</h3>'
            '<p class="view-lede" id="mx-cap">The whole history of the project up to release <code>%s</code>, '
            'from its first day. Time is squeezed toward the past: recent weeks get the most room, and older '
            'months are drawn narrower but never cut off. Dotted lines mark releases. Point at any mark to '
            'read its value. In the top chart, each grey dot is one test run. The line is the lowest '
            'value reached so far: it can only go down, while the runs themselves went up and down.</p>'
            '<div class="mx-wrap">%s</div>%s'
            '<details class="mx-table"><summary>The numbers behind the chart</summary>'
            '<table><thead><tr><th>Measure</th><th>From</th><th>To</th><th>First</th><th>Last</th><th>Points</th>'
            '<th>Direction</th><th>Source</th></tr></thead><tbody>%s</tbody></table>'
            '<p class="muted">Every number is read from the project\'s public history and links to the exact '
            'version it came from.</p></details></section>'
            % (html.escape(site_ref), render_chart(data, t_ref, shown), gap, summary_rows(data)))


def centicolon_status(site_ref):
    """The generated part of the CentiColons page: what the history says at the
    pin, then how the page itself has improved."""
    data = series()
    cc = data.get("cc_residual", [])
    floors = data.get("floor:shell-decider", [])
    if not cc and not floors:
        return improvements_html("centicolons")
    parts = []
    if cc:
        last = cc[-1]
        parts.append('<b>%s of %s</b> obligations were still open at the last test run that reported a score, on %s. '
                     'Between runs the score went up as well as down, and no run has reported one since'
                     % ("{:,}".format(last["v"]), "{:,}".format(last["budget"] or 0),
                        datetime.strptime(last["t"][:10], "%Y-%m-%d").strftime("%-d %B %Y")))
    if floors:
        parts.append('<b>%s</b> shell scripts are still to be rewritten in Lua, down from %s when the count began'
                     % ("{:,}".format(floors[-1]["v"]), "{:,}".format(floors[0]["v"])))
    return ('<h3>Where the score stands at %s</h3><p>%s.</p><p><button type="button" class="gobtn" '
            'data-go="view-progress">See the whole history →</button></p>%s'
            % (html.escape(site_ref), ". ".join(parts), improvements_html("centicolons")))

CSS = r"""
.metrics{margin:26px 0 40px}.metrics h3{font-size:19px;margin:0 0 6px}
.mx-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:8px 4px}
.mx-svg{display:block;width:100%;min-width:640px;height:auto;font-family:var(--mono)}
.mx-title{fill:var(--ink);font:600 12px var(--sans)}.mx-note,.mx-yl,.mx-xl{fill:var(--ink-faint);font-size:10px}
.mx-grid{stroke:var(--line);stroke-width:1}.mx-tick{stroke:var(--line-2);stroke-width:1;stroke-dasharray:1 3}
.mx-line{fill:none;stroke-width:2;stroke-linejoin:round}
.mx-dot{fill:var(--ink-faint);opacity:.55}.mx-hit{fill:transparent;stroke:none}.mx-hit:hover{fill:var(--ink);opacity:.5}
.mx-dl{fill:var(--ink-dim);font-size:10.5px}
.mx-ms{stroke:var(--ink-faint);stroke-width:1;stroke-dasharray:2 3;opacity:.7}
.mx-ms-bar{stroke:var(--amber)}.mx-ms-pin{stroke:var(--leaf);opacity:1}
.mx-msl{fill:var(--ink-faint);font-size:9.5px}
.mx-table{margin:12px 0}.mx-table summary,.improved summary{cursor:pointer;color:var(--ink-dim);font:600 12px var(--mono)}
.mx-table table{width:100%;border-collapse:collapse;margin:10px 0;font-size:12px}
.mx-table th,.mx-table td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:left;color:var(--ink-dim)}
.mx-table td.num{text-align:right;font-family:var(--mono)}.mx-table a,.improved a{color:var(--leaf)}
.improved{margin:14px 0 26px;padding:10px 14px;border:1px solid var(--line);border-radius:9px;background:var(--bg-2)}
.improved li,.improved p{font-size:13px;color:var(--ink-dim)}.improved time{font-family:var(--mono);color:var(--ink-faint)}
"""


def main(argv):
    if len(argv) < 5 or argv[0] not in ("extract", "verify") or argv[1] != "--repo" or argv[3] != "--ref":
        print("usage: metrics.py extract|verify --repo DIR --ref vTAG")
        print("blocked:usage")
        return 2
    repo, ref = pathlib.Path(argv[2]), argv[4]
    try:
        git(repo, "rev-parse", "--verify", ref + "^{commit}")
    except subprocess.CalledProcessError:
        print("blocked:history-repo-lacks:%s (%s)" % (ref, repo))
        return 2
    if git(repo, "rev-parse", "--is-shallow-repository").strip() == "true":
        print("blocked:history-repo-is-shallow:%s" % repo)
        return 2
    if argv[0] == "extract":
        added = append(extract(repo, ref))
        for name, rows in sorted(series().items()):
            print("  %-22s %4d rows  %s .. %s" % (name, len(rows), rows[0]["t"][:10], rows[-1]["t"][:10]))
        print("ok:metrics:%d" % added)
        return 0
    live, bad = verify(repo, ref)
    for r, why in bad[:20]:
        print("  %s %s %s: %s" % (r["series"], r["t"], r["key"], why))
    if bad:
        print("blocked:metrics-not-reproducible:%d" % len(bad))
        return 1
    print("ok:metrics-verified:%d" % len(live))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
