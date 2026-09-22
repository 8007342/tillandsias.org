#!/usr/bin/env python3
"""Capture the runtime's complete OpenSpec inventory at the website pin.

Run with a tagged checkout path. The generated JSON is committed so ordinary
website builds never depend on a local runtime clone or on network access.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "progress" / "runtime-specs.json"


def section(source, heading):
    match = re.search(r"^## " + re.escape(heading) + r"\s*$", source, re.M)
    if not match:
        return ""
    following = re.search(r"^## ", source[match.end():], re.M)
    return source[match.end():match.end() + following.start() if following else None].strip()


def first_paragraph(source):
    for block in re.split(r"\n\s*\n", source):
        block = re.sub(r"<!--.*?-->", "", block, flags=re.S).strip()
        if block and not block.startswith(("#", "- ", "|", "```")):
            return re.sub(r"\s+", " ", block)[:360]
    return ""


def main(checkout):
    tags = subprocess.check_output(
        ["git", "-C", str(checkout), "tag", "--points-at", "HEAD"], text=True
    ).splitlines()
    tag = checkout.name if checkout.name in tags else next(
        (name for name in tags if re.fullmatch(r"v\d+(?:\.\d+)+", name)), None)
    if not tag:
        raise ValueError("checkout must be at a numbered release tag")
    commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    base = "https://github.com/8007342/tillandsias/blob/%s/" % tag
    specs = []
    for path in sorted((checkout / "openspec/specs").glob("*/spec.md")):
        source = path.read_text(errors="replace")
        status = first_paragraph(section(source, "Status")) or "unspecified"
        purpose = first_paragraph(section(source, "Purpose"))
        if not purpose:
            purpose = first_paragraph(section(source, "Deprecation Notice"))
        requirements = re.findall(r"^### Requirement:\s*(.+)$", source, re.M)
        specs.append({"id": path.parent.name, "status": status,
                      "purpose": purpose or "No purpose recorded in this spec.",
                      "requirements": requirements,
                      "url": base + path.relative_to(checkout).as_posix()})
    changes = []
    for directory in sorted((checkout / "openspec/changes/archive").iterdir()):
        if not directory.is_dir():
            continue
        path = directory / "tasks.md"
        if not path.exists():
            path = next(iter(sorted(directory.glob("*/tasks.md"))), path)
        source = path.read_text(errors="replace") if path.exists() else ""
        tasks = [{"checked": mark.lower() == "x", "text": title.strip()}
                 for mark, title in re.findall(r"^\s*- \[([ xX])\]\s*(.+)$", source, re.M)]
        done = sum(task["checked"] for task in tasks)
        open_ = len(tasks) - done
        proposal = path.with_name("proposal.md") if path.exists() else directory / "proposal.md"
        if not proposal.exists():
            proposal = next(iter(sorted(directory.glob("*/proposal.md"))), proposal)
        title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", directory.name).replace("-", " ").capitalize()
        summary = ""
        if proposal.exists():
            proposal_source = proposal.read_text(errors="replace")
            heading = re.search(r"^#\s+(.+)$", proposal_source, re.M)
            if heading:
                title = heading.group(1).strip()
            summary = first_paragraph(proposal_source)
        metadata = directory / ".openspec.yaml"
        if not metadata.exists():
            metadata = next(iter(sorted(directory.glob("*/.openspec.yaml"))), metadata)
        source_path = path if path.exists() else proposal if proposal.exists() else metadata
        if not source_path.exists():
            raise ValueError("archived change has no source file: " + directory.name)
        changes.append({"id": directory.name, "title": title, "summary": summary, "done": done,
                        "open": open_, "tasks": tasks, "has_tasks": path.exists(),
                        "url": base + source_path.relative_to(checkout).as_posix()})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"tag": tag, "commit": commit, "specs": specs,
                               "changes": changes}, indent=2, ensure_ascii=False) + "\n")
    print("snapshot: %s specs, %s archived changes at %s" % (len(specs), len(changes), tag))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: snapshot-specs.py /path/to/tagged/runtime/checkout")
    main(pathlib.Path(sys.argv[1]).resolve())
