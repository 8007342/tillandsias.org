#!/usr/bin/env python3
"""A release happened: do everything that needs no judgement, then stop.

  refresh.py [--tag vX.Y.Z.B] [--offline] [--history DIR] [--learned SURFACE:NOTE]...

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
"""
import json
import os
import pathlib
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
HELP = ROOT / "skills" / "update-website" / "scripts"
CLONE_DIR = pathlib.Path(os.environ.get("TILLANDSIAS_CLONE_DIR")
                         or pathlib.Path.home() / ".cache/tillandsias-org/clones")
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
    tag, offline, history, learned = None, False, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--tag":
            tag, i = argv[i + 1], i + 2
        elif a == "--offline":
            offline, i = True, i + 1
        elif a == "--history":
            history, i = argv[i + 1], i + 2
        elif a == "--learned":
            surface, _, note = argv[i + 1].partition(":")
            learned.append({"surfaces": [surface], "note": note.strip()})
            i += 2
        else:
            print("blocked:bad-argument:%s" % a)
            return 2
    history = pathlib.Path(history or os.environ.get("TILLANDSIAS_HISTORY_REPO") or CLONE_DIR / ".history")
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    steps = {}

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
    pins_before = anchors.level_pins()
    site_before = anchors.site_ref()
    print("refresh to %s (site pin %s)" % (tag, site_before))

    # 2. checkouts
    if offline:
        need = sorted(set(pins_before.values()) | {tag})
        missing = [t for t in need if not (CLONE_DIR / t).is_dir()]
        if missing:
            print("blocked:missing-checkouts:%s" % ",".join(missing))
            return 2
        steps["fetch"] = {"verdict": "offline:%d checkouts present" % len(need), "secs": 0}
    else:
        rc, out, last, secs = run([str(HELP / "fetch-checkouts.sh"), tag])
        steps["fetch"] = {"verdict": last, "secs": secs}
        say("fetch", last, secs)
        if rc != 0:
            print(last)
            return 2

    # 3. anchors
    report_path = ROOT / "var" / "refresh-anchors.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rc, out, last, secs = run([sys.executable, "scripts/anchors.py", "apply", "--to", tag,
                               "--json", str(report_path)])
    say("anchors", last, secs)
    if rc not in (0, 3):
        print(out)
        return 2
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
        return 2

    # 5. metrics
    if (history / ".git").exists() or (history / "HEAD").exists():
        rc, out, last, secs = run([sys.executable, "scripts/metrics.py", "extract", "--repo", str(history),
                                   "--ref", site_ref])
        say("metrics", last, secs)
        if rc != 0:
            print(out)
            return 2
        steps["metrics"] = {"verdict": last, "secs": secs}
        rc, out, last, secs = run([sys.executable, "scripts/metrics.py", "verify", "--repo", str(history),
                                   "--ref", site_ref])
        say("replay", last, secs)
        steps["metrics_verify"] = {"verdict": last, "secs": secs}
        if rc != 0:
            print(out)
            return 2
    else:
        print("blocked:no-history-repo:%s (a full clone of the runtime; set --history or "
              "TILLANDSIAS_HISTORY_REPO)" % history)
        return 2

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
        return 1
    if judgement:
        for j in judgement:
            print("  ask: %s %s %s" % (j.get("level") or j.get("file") or j.get("proposal"),
                                       j.get("target", ""), j["why"]))
        print("ask:judgement:%d" % len(judgement))
        return 3
    print("ok:refreshed:%s" % tag)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
