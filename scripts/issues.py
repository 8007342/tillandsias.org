#!/usr/bin/env python3
"""Fold the findings ledger in `issues.d/` and answer questions about it.

The shape is the runtime's: append-only fragments, a grow-only set of findings
keyed by id, a grow-only set of events keyed by (id, event identity), and
last-writer-wins registers per (id, field) decided by (ts, host). See
`issues.d/README.md` for why each field uses the primitive it does.

    scripts/issues.py fold        the whole folded state as YAML
    scripts/issues.py columns     the three-column view the site renders
    scripts/issues.py validate    refuse malformed, duplicated or non-idempotent
    scripts/issues.py stats       counts by column, repo, class and severity

`validate` is the gate: it exits non-zero and prints `violation:<why>`.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIR = ROOT / "issues.d"

# The monotone ladder. You climb freely; you descend only through `falsified`.
# `obsoleted` and `wontfix` are lateral terminals — an attempt ended, nothing
# completed — so they are decided by plain last-writer-wins and sit in yellow.
RUNG = {
    "found": 0,
    "triaged": 1, "filed": 1, "in_progress": 1, "blocked": 1,
    "resolved": 2, "verified": 2,
}
LATERAL = {"obsoleted", "wontfix"}
# Two ways down, and the difference is the point. `falsified` says the ledger's
# own record was wrong — a finding believed resolved was not. `retracted` says a
# claim this project PUBLISHED was withdrawn. The second is the more valuable
# datum: it is the evidence that the method catches its own errors, so it is
# counted rather than smoothed away, and it carries what was withdrawn.
DESCEND = {"falsified", "retracted"}
COLUMN = {0: "red", 1: "yellow", 2: "green"}

SCALARS = ("repo", "title", "area", "class", "severity", "tag", "commit",
           "claim", "code", "why", "fix", "upstream")
LISTS = ("evidence", "depends_on")
CLASSES = {"spec-vs-code", "defect", "doc-drift", "stale-record", "site", "process"}
REPOS = {"tillandsias", "tillandsias.org"}
SEVERITIES = {"high", "medium", "low"}
TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ID = re.compile(r"^[0-9a-f]{8}$")


# --- a small YAML reader ------------------------------------------------------
#
# The fragments use a deliberately narrow subset — mappings, lists of mappings,
# and scalars that are either plain, quoted, or a `|` block. Parsing it here
# rather than importing a library keeps the ledger readable by the build with
# nothing installed, and refuses anything outside the subset instead of
# guessing at it.

def _scalar(raw):
    raw = raw.strip()
    if raw[:1] in "\"'" and raw[-1:] == raw[:1] and len(raw) >= 2:
        return raw[1:-1]
    return raw


def parse(text, where):
    """Parse one fragment into {'issues': [...], 'events': [...]}."""
    out, stack = {}, []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()

        if indent == 0 and s.endswith(":"):
            key = s[:-1]
            if key not in ("issues", "events"):
                raise ValueError("%s: unknown top-level key %r" % (where, key))
            out.setdefault(key, [])
            stack = [out[key]]
            continue

        if s.startswith("- "):
            item = {}
            stack[0].append(item)
            s = s[2:]
            cur = item
        elif stack and stack[0]:
            cur = stack[0][-1]
        else:
            raise ValueError("%s: content outside a list: %r" % (where, s))

        if ":" not in s:
            raise ValueError("%s: expected `key: value`, got %r" % (where, s))
        k, _, v = s.partition(":")
        k, v = k.strip(), v.strip()

        if v == "|":                              # block scalar
            body, base = [], None
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent + 2 and not nxt.startswith(" " * (indent + 3)):
                    break
                if base is None and nxt.strip():
                    base = len(nxt) - len(nxt.lstrip())
                body.append(nxt[base:] if base and len(nxt) >= base else nxt.strip())
                i += 1
            cur[k] = "\n".join(body).rstrip()
        elif v == "":                             # a nested list follows
            sub = []
            cur[k] = sub
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    i += 1
                    continue
                ni = len(nxt) - len(nxt.lstrip())
                if ni <= indent or not nxt.lstrip().startswith("- "):
                    break
                entry, rest = {}, nxt.strip()[2:]
                if ":" in rest and not rest.startswith("http"):
                    kk, _, vv = rest.partition(":")
                    entry[kk.strip()] = _scalar(vv)
                    i += 1
                    while i < len(lines):
                        n2 = lines[i]
                        if not n2.strip():
                            i += 1
                            continue
                        if (len(n2) - len(n2.lstrip())) <= ni or n2.lstrip().startswith("- "):
                            break
                        k2, _, v2 = n2.strip().partition(":")
                        entry[k2.strip()] = _scalar(v2)
                        i += 1
                    sub.append(entry)
                else:
                    sub.append(_scalar(rest))
                    i += 1
        else:
            cur[k] = _scalar(v)
    return out


# --- the fold -----------------------------------------------------------------

def fragments():
    """Every fragment, in (ts, filename) order — never directory order."""
    found = []
    if not DIR.is_dir():
        return found
    for p in sorted(DIR.glob("*.yaml")):
        text = p.read_text()
        frag = parse(text, p.name)
        # A fragment's own time is the earliest event it carries, so that a
        # file whose name and contents disagree still folds by its contents.
        times = [e.get("ts", "") for e in frag.get("events", [])]
        found.append(((min(times) if times else p.name), p.name, frag, p))
    found.sort(key=lambda x: (x[0], x[1]))
    return found


def event_identity(e):
    """What makes an event the same event. Two hosts recording the same fact
    at the same moment must collapse, or a re-fold duplicates history."""
    return (e.get("id"), e.get("ts"), e.get("host"), e.get("type"), e.get("note", ""))


def fold():
    issues, events, wins = {}, {}, {}
    for ts, name, frag, _ in fragments():
        for decl in frag.get("issues", []):
            iid = decl.get("id")
            issues.setdefault(iid, {"id": iid, "evidence": [], "depends_on": []})
            # Declaration fields are last-writer-wins per (id, field). A
            # declaration with no event of its own is stamped by the fragment.
            for field in SCALARS:
                if field not in decl:
                    continue
                key = (iid, field)
                stamp = (decl.get("ts", ts), decl.get("host", ""))
                if key not in wins or stamp >= wins[key]:
                    wins[key] = stamp
                    issues[iid][field] = decl[field]
            for field in LISTS:                    # grow-only, deduplicated
                for item in decl.get(field, []) or []:
                    if item not in issues[iid][field]:
                        issues[iid][field].append(item)
        for e in frag.get("events", []):
            events.setdefault(e.get("id"), {})[event_identity(e)] = e

    for iid, issue in issues.items():
        evs = sorted(events.get(iid, {}).values(), key=lambda e: (e.get("ts", ""), e.get("host", "")))
        issue["events"] = evs
        issue["state"] = state_of(evs)
        issue["column"] = COLUMN[RUNG.get(issue["state"], 0)] if issue["state"] not in LATERAL else "yellow"
    return issues


def state_of(evs):
    """The ladder join: climb freely, descend only through `falsified`."""
    state, rung = "found", 0
    for e in evs:
        t = e.get("type")
        if t in DESCEND:
            state, rung = "found", 0
            continue
        if t in LATERAL:
            state, rung = t, 1
            continue
        if t not in RUNG:
            continue
        if RUNG[t] >= rung:                        # equal rung: later event wins
            state, rung = t, RUNG[t]
    return state


# --- commands -----------------------------------------------------------------

def cmd_validate():
    bad, seen_ids, seen_events = [], {}, set()
    for ts, name, frag, path in fragments():
        if not re.match(r"^\d{8}T\d{6}Z-[a-z0-9-]+-[a-z0-9.-]+\.yaml$", name):
            bad.append("%s: name is not <utc>-<slug>-<host>.yaml" % name)
        for d in frag.get("issues", []):
            iid = d.get("id", "")
            if not ID.match(iid or ""):
                bad.append("%s: id %r is not eight hex characters" % (name, iid))
            if "repo" in d and d["repo"] not in REPOS:
                bad.append("%s/%s: repo %r" % (name, iid, d["repo"]))
            if "class" in d and d["class"] not in CLASSES:
                bad.append("%s/%s: class %r" % (name, iid, d["class"]))
            if "severity" in d and d["severity"] not in SEVERITIES:
                bad.append("%s/%s: severity %r" % (name, iid, d["severity"]))
            if iid in seen_ids and seen_ids[iid] != name:
                pass                               # re-declaration is legal: LWW
            seen_ids[iid] = name
        for e in frag.get("events", []):
            if not TS.match(e.get("ts", "")):
                bad.append("%s: event ts %r is not UTC ISO-8601" % (name, e.get("ts")))
            if e.get("type") not in set(RUNG) | LATERAL | DESCEND:
                bad.append("%s: unknown event type %r" % (name, e.get("type")))
            if not e.get("host"):
                bad.append("%s: event with no host (the LWW tiebreak needs it)" % name)
            for k, v in e.items():
                if isinstance(v, str) and " #" in v and not (v.startswith('"') or v.startswith("'")):
                    bad.append("%s: %s carries an unquoted ' #', which a YAML reader "
                               "would treat as a comment; quote the value" % (name, k))
            if e.get("type") in DESCEND and not e.get("note"):
                bad.append("%s: a %s event must say why; going down the ladder "
                           "without a reason is how a record loses its history"
                           % (name, e.get("type")))
            seen_events.add(event_identity(e))

    state = fold()
    for iid, issue in state.items():
        if not issue.get("title"):
            bad.append("%s: declared with no title" % iid)
        if issue.get("state") in DESCEND:
            bad.append("%s: %r is a transition, not a state" % (iid, issue["state"]))
        for dep in issue.get("depends_on", []):
            if dep not in state:
                bad.append("%s: depends on %s, which is not declared" % (iid, dep))
    # Idempotence: folding twice must not change the answer.
    if repr(fold()) != repr(state):
        bad.append("the fold is not idempotent")

    bad += check_quotes(state)
    for b in bad:
        print("  " + b)

    print("violation:issues:%d" % len(bad) if bad else
          "ok:issues:%d finding(s), %d fragment(s)" % (len(state), len(fragments())))
    return 1 if bad else 0


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _norm_src(lines):
    return _norm("\n".join(re.sub(r"^\s*(?:#|//[!/]?|--|\*)(?:\s+|$)", "", x) for x in lines))


def check_quotes(state):
    """Every `quote` must be verbatim in the range it cites, at the release the
    finding names. This is the same rule the page's footnotes obey, and for the
    same reason: a citation nobody checks is a citation that drifts. Analysis
    that is ours rather than the source's belongs in `note`, which is not
    checked because it does not pretend to be a quotation.

    Where no checkout is present the quote is reported UNCHECKED, never passed
    over in silence.
    """
    import os
    clones = pathlib.Path(os.environ.get("TILLANDSIAS_CLONE_DIR",
                                         pathlib.Path.home() / ".cache/tillandsias-org/clones"))
    bad, unchecked = [], 0
    for iid, issue in sorted(state.items()):
        tag = issue.get("tag", "")
        for ev in issue.get("evidence", []) or []:
            if not isinstance(ev, dict):
                continue
            quote, path = ev.get("quote"), ev.get("path", "")
            if not quote or not path:
                continue
            target, _, anchor = path.partition("#")
            if issue.get("repo") == "tillandsias.org":
                # Read the file as it stood at the commit the finding names. The
                # working tree moves under a finding; the stamp is the claim.
                commit = issue.get("commit") or issue.get("tag") or "HEAD"
                out = subprocess.run(["git", "-C", str(ROOT), "show",
                                      "%s:%s" % (commit, target)],
                                     capture_output=True, text=True)
                if out.returncode:
                    bad.append("%s: %s does not exist at the commit this finding "
                               "stamps (%s)" % (iid, target, commit[:9]))
                    continue
                lines = out.stdout.splitlines()
            else:
                root = clones / tag
                if not (root / target).exists():
                    unchecked += 1
                    continue
                lines = (root / target).read_text(errors="replace").splitlines()
            lo, hi = 1, len(lines)
            m = re.match(r"^L(\d+)(?:-L(\d+))?$", anchor or "")
            if m:
                lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
                if hi > len(lines) or lo < 1 or lo > hi:
                    bad.append("%s: %s names a range outside the file (%d lines)"
                               % (iid, path, len(lines)))
                    continue
            span = lines[lo - 1:hi]
            if _norm(quote) not in _norm("\n".join(span)) and _norm(quote) not in _norm_src(span):
                bad.append("%s: quote is not verbatim at %s — move it to `note` if it is "
                           "our reading rather than the source's words" % (iid, path))
    if unchecked:
        print("  %d quote(s) UNCHECKED: no checkout for the release they name" % unchecked)
    return bad


def cmd_columns():
    state = fold()
    for col in ("red", "yellow", "green"):
        rows = sorted((i for i in state.values() if i["column"] == col),
                      key=lambda i: (i.get("severity", "low"), i["id"]))
        print("\n%s (%d)" % (col.upper(), len(rows)))
        for i in rows:
            up = (" -> " + i["upstream"]) if i.get("upstream") else ""
            print("  %s  %-14s %-8s %s%s" % (i["id"], i.get("repo", "?"),
                                             i.get("severity", "?"), i.get("title", "")[:88], up))
    return 0


def cmd_stats():
    state = fold()
    def tally(field):
        out = {}
        for i in state.values():
            out[i.get(field, "?")] = out.get(i.get(field, "?"), 0) + 1
        return ", ".join("%s=%d" % kv for kv in sorted(out.items()))
    print("findings: %d" % len(state))
    for f in ("column", "repo", "class", "severity", "state"):
        print("  %-9s %s" % (f, tally(f)))
    print("  filed upstream: %d" % sum(1 for i in state.values() if i.get("upstream")))
    rets = [(i["id"], e) for i in state.values() for e in i.get("events", [])
            if e.get("type") == "retracted"]
    print("  claims retracted: %d" % len(rets))
    for iid, e in sorted(rets, key=lambda x: x[1].get("ts", "")):
        print("    %s  %s  %s" % (e.get("ts", "")[:10], iid, e.get("note", "")[:80]))
    return 0


def cmd_fold():
    for iid, issue in sorted(fold().items()):
        print("- id: %s" % iid)
        for k in ("column", "state", "repo", "severity", "class", "title", "upstream"):
            if issue.get(k):
                print("  %s: %s" % (k, issue[k]))
        print("  events: %d" % len(issue.get("events", [])))
    return 0


def mint(seed):
    """A stable id from the finding's own words, so the same finding filed
    twice by two hosts collides rather than duplicating."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "mint":
        print(mint(" ".join(sys.argv[2:])))
        sys.exit(0)
    fn = {"fold": cmd_fold, "columns": cmd_columns,
          "validate": cmd_validate, "stats": cmd_stats}.get(cmd)
    if not fn:
        print(__doc__)
        sys.exit(2)
    sys.exit(fn())
