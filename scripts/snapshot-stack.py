#!/usr/bin/env python3
"""Copy the runtime's stack ledger (docs/credits/stack.v1.json) into the site.

  snapshot-stack.py /path/to/runtime/checkout

The ledger is generated in the runtime repository by
scripts/lua/build-stack-ledger.lua from cargo metadata, the Containerfiles,
the lockfiles and the model licence register; this script only copies it and
records WHICH checkout it came from (tag when the checkout sits on a numbered
release tag, else the branch and commit), so the Powered By page can say so.

A checkout that predates the ledger has no file to copy: the committed copy
is kept and the last line says `skip:stack-ledger:absent-at:<ref>` (exit 0),
so refresh.py keeps going. Last line otherwise: `snapshot-stack: <n> nodes,
<m> edges at <ref>`.
"""
import json
import pathlib
import re
import subprocess
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent / "docs/powered-by/stack.v1.json"
SOURCE = "docs/credits/stack.v1.json"


def describe(checkout):
    tags = subprocess.check_output(
        ["git", "-C", str(checkout), "tag", "--points-at", "HEAD"], text=True
    ).splitlines()
    tag = checkout.name if checkout.name in tags else next(
        (name for name in tags if re.fullmatch(r"v\d+(?:\.\d+)+", name)), None)
    commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    branch = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    return tag, branch if branch != "HEAD" else None, commit


def main(checkout):
    tag, branch, commit = describe(checkout)
    ref = tag or branch or commit[:12]
    source = checkout / SOURCE
    if not source.exists():
        print("skip:stack-ledger:absent-at:%s" % ref)
        return 0
    ledger = json.loads(source.read_text())
    if ledger.get("schema") != "tillandsias-stack/v1":
        sys.exit("blocked:stack-ledger:unknown-schema:%s" % ledger.get("schema"))
    ledger["snapshot"] = {
        "tag": tag, "branch": branch, "commit": commit,
        "source": "https://github.com/8007342/tillandsias/blob/%s/%s" % (tag or commit, SOURCE),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print("snapshot-stack: %d nodes, %d edges at %s" % (len(ledger["nodes"]), len(ledger["edges"]), ref))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: snapshot-stack.py /path/to/runtime/checkout")
    sys.exit(main(pathlib.Path(sys.argv[1]).resolve()))
