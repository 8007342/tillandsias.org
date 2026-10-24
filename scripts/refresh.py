#!/usr/bin/env python3
"""A release happened: do everything that needs no judgement, then stop.

  refresh.py [--tag vX.Y.Z.B] [--offline] [--history DIR]
             [--learned SURFACE:NOTE]... [--reader SURFACE:SENTENCE]...

--learned goes to the internal refresh.d/ fragment, for the next run.
--reader appends one plain-words outcome to docs/progress/improvements.json,
the only source of a page's "How this section has improved" note.

Steps, each recorded in the run's fragment under refresh.d/:

  1. target   --tag, else the stable channel (latest-release.sh)
  2. fetch    checkouts for the target and every pin (fetch-checkouts.sh);
              --offline only checks they exist
  3. anchors  re-anchor every runtime citation by content and move the pin of
              each level whose citations all re-anchored (anchors.py apply);
              list what needs a person
  4. snapshot regenerate the Progress spec inventory at the site pin
  5. metrics  append new residual-obligation history from runtime git and
              prove every stored row replays (metrics.py extract + verify)
  6. build    the checked build, which re-checks every quote at its release
  7. refine   append this run's fragment: what moved, what needs judgement,
              what the next run should know

Last line: `ok:refreshed:<tag>`, `ask:judgement:<n>` (exit 3: everything
mechanical is done; a person decides the listed items) or `blocked:<why>`.

--unattended is the forge run, with no operator and an ephemeral checkout:

  - checkouts and the full-history clone default to var/unattended/ inside
    the checkout (gitignored), never ~/.cache; a missing history clone is
    cloned in full from $TILLANDSIAS_REPO_URL, an existing one is fetched
  - every write happens on the branch website/update-<tag>, never on main
  - a judgement item ends only re-cited (it is gone from the next run) or
    filed: its target is named in a docs/audit/*-issues-*.md record
    (skills/file-findings); one that is neither keeps `ask:judgement:<n>`
  - the result leaves only through the mirror: `git push origin
    HEAD:website/update-<tag>`, then, for a clean run only, the operator's
    auto-merge (decision 2026-10-24): merge origin/main in, re-run the checked
    build, and push to main, which deploys. A run with any judgement item,
    filed or not, never merges.
  Last line: `ok:merged:<tag>` (deployed), `ok:pushed:website/update-<tag>:filed:<n>`
  (findings delivered, not merged), `ask:judgement:<n>` (exit 3) or
  `blocked:<why>`.

Fixture seam: TILLANDSIAS_REFRESH_STUB names a JSON file
{"rc": 0|3, "judgement": [{"target": ...}]} that stands in for steps 2-7, and
TILLANDSIAS_CHECKED_BUILD names the pre-merge build command, so
skills/update-website/scripts/test-release-refresh-unattended.sh can test the
unattended path without a runtime checkout.
"""
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
HELP = ROOT / "skills" / "update-website" / "scripts"
CLONE_DIR = pathlib.Path(os.environ.get("TILLANDSIAS_CLONE_DIR")
                         or pathlib.Path.home() / ".cache/tillandsias-org/clones")
SCRATCH = ROOT / "var" / "unattended"
REPO_URL = os.environ.get("TILLANDSIAS_REPO_URL") or "https://github.com/8007342/tillandsias"
REFRESH = ROOT / "refresh.d"
sys.path.insert(0, str(ROOT / "scripts"))
import anchors  # noqa: E402
import metrics  # noqa: E402


def run(cmd, **kw):
    env = dict(os.environ, TILLANDSIAS_CLONE_DIR=str(CLONE_DIR))
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env, **kw)
    out = (p.stdout + p.stderr).rstrip()
    last = out.splitlines()[-1] if out else ""
    return p.returncode, out, last, round(time.monotonic() - t0, 1)


def say(step, last, secs):
    print("  %-9s %-60s %5.1fs" % (step, last[:60], secs))


def previous():
    frags = metrics.refresh_fragments()
    runs = [f for f in frags if f.get("kind") == "run"]
    return runs[-1] if runs else None


def main(argv):
    global CLONE_DIR
    tag, offline, history, learned, reader = None, False, None, [], []
    unattended = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--tag":
            tag, i = argv[i + 1], i + 2
        elif a == "--offline":
            offline, i = True, i + 1
        elif a == "--unattended":
            unattended, i = True, i + 1
        elif a == "--history":
            history, i = argv[i + 1], i + 2
        elif a == "--reader":
            surface, _, text = argv[i + 1].partition(":")
            reader.append({"month": datetime.now(timezone.utc).strftime("%Y-%m"),
                           "surfaces": [surface], "text": text.strip()})
            i += 2
        elif a == "--learned":
            surface, _, note = argv[i + 1].partition(":")
            learned.append({"surfaces": [surface], "note": note.strip()})
            i += 2
        else:
            print("blocked:bad-argument:%s" % a)
            return 2
    if unattended and not os.environ.get("TILLANDSIAS_CLONE_DIR"):
        CLONE_DIR = SCRATCH / "clones"
    history = pathlib.Path(history or os.environ.get("TILLANDSIAS_HISTORY_REPO") or CLONE_DIR / ".history")
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    prev = previous()
    if prev:
        todo = prev.get("judgement", []) + prev.get("review_queue", [])
        print("previous run %s (%s -> %s): %d item(s) were left for a person"
              % (prev["ts"], prev.get("from", "?"), prev.get("to", "?"), len(todo)))
        for note in prev.get("next_run", []):
            print("  next-run note: %s" % note)

    # 1. target
    if not tag:
        rc, out, last, secs = run([str(HELP / "latest-release.sh")])
        if rc != 0:
            print(last)
            return 2
        tag = last
    if unattended:
        if not re.fullmatch(r"v\d+(\.\d+){3}", tag):
            print("blocked:bad-tag:%s" % tag)
            return 2
        branch = "website/update-%s" % tag
        why = on_branch(branch)
        if why:
            print("blocked:%s" % why)
            return 2
        if not offline:
            why = history_clone(history)
            if why:
                print("blocked:%s" % why)
                return 2

    stub = os.environ.get("TILLANDSIAS_REFRESH_STUB")
    if stub:
        doc = json.loads(pathlib.Path(stub).read_text())
        rc, judgement = doc.get("rc", 0), doc.get("judgement", [])
    else:
        rc, judgement = mechanical(tag, offline, history, learned, reader, started)
    if rc not in (0, 3):
        return rc
    if not unattended:
        if judgement:
            print("ask:judgement:%d" % len(judgement))
            return 3
        print("ok:refreshed:%s" % tag)
        return 0
    return deliver(tag, judgement)


def git(*args):
    p = subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def on_branch(branch):
    """Put the checkout on `branch` before anything writes; never stay on main."""
    rc, cur = git("rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0:
        return "not-a-git-checkout"
    if cur == branch:
        return None
    rc, _ = git("rev-parse", "-q", "--verify", "refs/heads/" + branch)
    rc, out = git("switch", branch) if rc == 0 else git("switch", "-c", branch)
    return None if rc == 0 else "cannot-switch-to:%s" % branch


def history_clone(history):
    """The metrics step needs the runtime's full history; a fresh forge has none."""
    if (history / ".git").exists() or (history / "HEAD").exists():
        p = subprocess.run(["git", "-C", str(history), "fetch", "--quiet", "--tags", "origin"],
                           capture_output=True, text=True)
        return None if p.returncode == 0 else "history-fetch-failed:%s" % history
    history.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["git", "clone", "--quiet", REPO_URL, str(history)], capture_output=True, text=True)
    return None if p.returncode == 0 else "history-clone-failed:%s" % REPO_URL


def filed(item):
    """A judgement item is filed when a file-findings record names its target."""
    target = item.get("target") or item.get("proposal") or ""
    if not target:
        return False
    for rec in sorted((ROOT / "docs" / "audit").glob("*-issues-*.md")):
        if target in rec.read_text(errors="replace"):
            return True
    return False


def deliver(tag, judgement):
    """The only way an unattended run's result leaves the forge."""
    branch = "website/update-%s" % tag
    open_items = [j for j in judgement if not filed(j)]
    if open_items:
        for j in open_items:
            print("  unsettled: %s %s %s" % (j.get("level") or j.get("file") or j.get("proposal"),
                                             j.get("target", ""), j.get("why", "")))
        print("ask:judgement:%d" % len(open_items))
        return 3
    rc, cur = git("rev-parse", "--abbrev-ref", "HEAD")
    if cur != branch:
        print("blocked:not-on-%s" % branch)
        return 2
    # What a refresh writes, and nothing a forge leaves beside it.
    git("add", "-u")
    git("add", "-A", "--", "docs", "refresh.d", "openspec")
    rc, _ = git("diff", "--cached", "--quiet")
    if rc != 0:
        msg = "Refresh the site to %s (unattended)\n" % tag
        if judgement:
            msg += "\n%d item(s) need a person and are filed under docs/audit/.\n" % len(judgement)
        p = subprocess.run(["git", "-C", str(ROOT), "commit", "-q", "-F", "-"], input=msg,
                           capture_output=True, text=True)
        if p.returncode != 0:
            print((p.stdout + p.stderr).strip())
            print("blocked:commit-refused")
            return 2
    rc, out = git("push", "origin", "HEAD:refs/heads/" + branch)
    if rc != 0:
        print(out)
        print("blocked:push-failed:%s" % branch)
        return 2
    if judgement:
        print("ok:pushed:%s:filed:%d" % (branch, len(judgement)))
        return 0
    return merge(tag, branch)


def merge(tag, branch):
    """Auto-merge a clean run into main (operator decision 2026-10-24); main deploys."""
    rc, out = git("fetch", "--quiet", "origin", "main")
    if rc != 0:
        print(out)
        print("blocked:fetch-main-failed")
        return 2
    rc, out = git("merge", "--quiet", "--no-edit", "-m", "Merge %s: the site at %s" % (branch, tag), "FETCH_HEAD")
    if rc != 0:
        git("merge", "--abort")
        print(out)
        print("blocked:merge-conflict:%s" % branch)
        return 2
    build = os.environ.get("TILLANDSIAS_CHECKED_BUILD") or str(HELP / "checked-build.sh")
    p = subprocess.run([build], cwd=ROOT, capture_output=True, text=True)
    lines = (p.stdout + p.stderr).strip().splitlines()
    if p.returncode != 0 or not lines or lines[-1] != "ok:checked-build":
        print("\n".join(lines[-20:]))
        print("blocked:checked-build-before-merge")
        return 1
    for ref in ("HEAD:refs/heads/" + branch, "HEAD:refs/heads/main"):
        rc, out = git("push", "origin", ref)
        if rc != 0:
            print(out)
            print("blocked:push-failed:%s" % ref)
            return 2
    print("ok:merged:%s" % tag)
    return 0


def mechanical(tag, offline, history, learned, reader, started):
    """Steps 2-7. Returns (exit code, judgement items); prints `blocked:` itself."""
    steps = {}
    pins_before = anchors.level_pins()
    site_before = anchors.site_ref()
    print("refresh to %s (site pin %s)" % (tag, site_before))

    # 2. checkouts
    if offline:
        need = sorted(set(pins_before.values()) | {tag})
        missing = [t for t in need if not (CLONE_DIR / t).is_dir()]
        if missing:
            print("blocked:missing-checkouts:%s" % ",".join(missing))
            return 2, []
        steps["fetch"] = {"verdict": "offline:%d checkouts present" % len(need), "secs": 0}
    else:
        rc, out, last, secs = run([str(HELP / "fetch-checkouts.sh"), tag])
        steps["fetch"] = {"verdict": last, "secs": secs}
        say("fetch", last, secs)
        if rc != 0:
            print(last)
            return 2, []

    # 3. anchors
    report_path = ROOT / "var" / "refresh-anchors.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rc, out, last, secs = run([sys.executable, "scripts/anchors.py", "apply", "--to", tag,
                               "--json", str(report_path)])
    say("anchors", last, secs)
    if rc not in (0, 3):
        print(out)
        return 2, []
    report = json.loads(report_path.read_text())
    steps["anchors"] = {"verdict": last, "secs": secs}
    site_ref = anchors.site_ref()

    # 4. snapshot
    rc, out, last, secs = run([sys.executable, "scripts/snapshot-specs.py", str(CLONE_DIR / site_ref)])
    steps["snapshot"] = {"verdict": last, "secs": secs}
    say("snapshot", last, secs)
    if rc != 0:
        print(out)
        print("blocked:snapshot")
        return 2, []

    # 5. metrics
    if (history / ".git").exists() or (history / "HEAD").exists():
        rc, out, last, secs = run([sys.executable, "scripts/metrics.py", "extract", "--repo", str(history),
                                   "--ref", site_ref])
        say("metrics", last, secs)
        if rc != 0:
            print(out)
            return 2, []
        steps["metrics"] = {"verdict": last, "secs": secs}
        rc, out, last, secs = run([sys.executable, "scripts/metrics.py", "verify", "--repo", str(history),
                                   "--ref", site_ref])
        say("replay", last, secs)
        steps["metrics_verify"] = {"verdict": last, "secs": secs}
        if rc != 0:
            print(out)
            return 2, []
    else:
        print("blocked:no-history-repo:%s (a full clone of the runtime; set --history or "
              "TILLANDSIAS_HISTORY_REPO)" % history)
        return 2, []

    # Reader-facing outcomes (plain words, no ids) go to the page; the
    # refresh.d/ fragment below stays internal, for the next run.
    if reader:
        rows = json.loads(metrics.READER.read_text()) if metrics.READER.exists() else []
        metrics.READER.write_text(json.dumps(rows + reader, indent=1, ensure_ascii=False) + "\n")

    # 6. checked build
    rc, out, last, secs = run([str(HELP / "checked-build.sh")])
    steps["checked_build"] = {"verdict": last, "secs": secs}
    say("build", last, secs)

    # 7. refine: append, never rewrite
    judgement = []
    for slug, lvl in report["levels"].items():
        for it in lvl["items"]:
            if it["verdict"] == "judgement":
                judgement.append({"level": slug, "n": it["n"], "target": it["target"], "why": it["why"],
                                  "quote": it.get("quote", ""), "was": it.get("was", ""),
                                  "candidates": it.get("candidates", [])})
    for it in report["site"]["items"]:
        if it["verdict"] == "judgement":
            judgement.append({"file": it["file"], "target": it["target"], "why": it["why"],
                              "held_at": it.get("held_at"), "was": it.get("was", "")})
    moved = [{"where": slug, "n": it["n"], "from": it["target"], "to": it["new_target"], "how": it["how"]}
             for slug, lvl in report["levels"].items() for it in lvl["items"] if it["verdict"] == "moved"]
    moved += [{"where": it["file"], "from": it["target"], "to": it["new_target"], "how": it["how"]}
              for it in report["site"]["items"] if it["verdict"] == "moved"]
    host = os.environ.get("TILLANDSIAS_HOST") or socket.gethostname().split(".")[0]
    frag = {"kind": "run", "ts": started, "host": host, "from": site_before, "to": tag,
            "pins_before": pins_before, "pins_after": anchors.level_pins(),
            "pins_moved": report.get("pins_moved", []), "moved": moved,
            "judgement": judgement, "review_queue": report.get("review_queue", []),
            "steps": steps, "learned": [dict(x, ts=started) for x in learned], "next_run": []}
    for d in report.get("proposals", []):
        judgement.append({"proposal": d, "why": "level 5 moves only through a reviewed OpenSpec change "
                                                 "until automated-release-refresh is accepted"})
    if judgement:
        frag["next_run"].append("%d item(s) need a person; their levels kept their pins" % len(judgement))
    REFRESH.mkdir(exist_ok=True)
    name = "%s-%s-%s.json" % (started.replace("-", "").replace(":", ""), tag, host)
    (REFRESH / name).write_text(json.dumps(frag, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print("  refine    refresh.d/%s" % name)

    if steps["checked_build"]["verdict"] != "ok:checked-build":
        print(out)
        print("blocked:checked-build")
        return 1, []
    for j in judgement:
        print("  ask: %s %s %s" % (j.get("level") or j.get("file") or j.get("proposal"),
                                   j.get("target", ""), j["why"]))
    return (3 if judgement else 0), judgement


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
