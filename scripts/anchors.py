#!/usr/bin/env python3
"""Re-anchor every runtime citation on the site by content, not by line number.

A citation is `path#Lstart-Lend` at a release tag, optionally with a verbatim
quote. Releases insert lines above cited spans, so line numbers drift while
the cited text does not. Moving a pin is therefore mechanical exactly when the
cited text can be found again at the new tag, and a judgement exactly when it
cannot. This script draws that line and never crosses it:

  ok        the range at the new tag still carries the quote (or, unquoted,
            the identical text it carried at the old tag);
  moved     the identical block of lines, or the verbatim quote, was found
            once elsewhere in the same file: the range is rewritten;
  judgement the path is gone, the quote is gone, the text changed under an
            unquoted citation, or the block is ambiguous. Nothing is
            rewritten; the item is reported with what was found instead.

Citations it reads (the three places runtime line numbers live):

  docs/matrix/level-*.md      `[^n]: Label | path#Lx-Ly` footnotes and their
                              `>` quotes, at the level's pin;
  scripts/big_graph.py        `"runtime:path#Lx-Ly"` evidence records;
  scripts/build-matrix.py     `rcite("path#Lx-Ly", ...)` links in site prose.

The last two follow the site-wide pin (the newest level pin). A site-prose
citation that cannot be re-anchored is held at the tag it was verified at by an
`@vTAG` suffix, so its link still lands on the text it was written against.

Usage:
  anchors.py plan  --to vNEW [--json FILE]     report only
  anchors.py apply --to vNEW [--json FILE]     rewrite moved ranges; move the
                                               pin of every level with no
                                               judgement item
Last line: `ok:anchors:<moved>`, `ask:anchors:<judgement>` (exit 3) or
`blocked:<why>` (exit 2).
"""
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATRIX = ROOT / "docs" / "matrix"
BIG_GRAPH = ROOT / "scripts" / "big_graph.py"
BUILD = ROOT / "scripts" / "build-matrix.py"
CLONE_DIR = pathlib.Path(os.environ.get("TILLANDSIAS_CLONE_DIR")
                         or pathlib.Path.home() / ".cache/tillandsias-org/clones")

FN_DEF = re.compile(r"^\[\^(\d+)\]:\s*(.+?)\s*\|\s*(\S+?)(?:\s+@(v[\d.]+))?\s*$")
GRAPH_CITE = re.compile(r'"runtime:([^"#@]+)(?:#(L\d+(?:-L\d+)?))?(?:@(v[\d.]+))?"')
PROSE_CITE = re.compile(r'rcite\("([^"#@]+)(?:#(L\d+(?:-L\d+)?))?(?:@(v[\d.]+))?"')
TAG = re.compile(r"^v\d+(?:\.\d+){3}$")


def vkey(tag):
    return tuple(int(x) for x in re.findall(r"\d+", tag))


# --- text matching ------------------------------------------------------------

def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _strip_leader(line):
    return re.sub(r"^\s*(?:#|//[!/]?|--|\*)(?:\s+|$)", "", line)


def _flat(lines, strip):
    """Whitespace-collapsed text of `lines` plus, per character, its line index."""
    text, owner = [], []
    for i, line in enumerate(lines):
        piece = _norm(_strip_leader(line) if strip else line)
        if not piece:
            continue
        if text:
            text.append(" ")
            owner.append(i)
        text.append(piece)
        owner.extend([i] * len(piece))
    return "".join(text), owner


def quote_spans(lines, quote):
    """Every (lo, hi) 1-based line span holding the whitespace-normalised quote,
    matched plain or with comment leaders stripped, as the checked build does."""
    q = _norm(quote)
    spans = set()
    if not q:
        return []
    for strip in (False, True):
        text, owner = _flat(lines, strip)
        at = text.find(q)
        while at >= 0:
            spans.add((owner[at] + 1, owner[at + len(q) - 1] + 1))
            at = text.find(q, at + 1)
    # A plain match and a stripped match of the same place are one span.
    return sorted(spans)


def in_range(lines, lo, hi, quote):
    cited = lines[lo - 1:hi]
    q = _norm(quote)
    return q in _norm("\n".join(cited)) or q in _norm("\n".join(_strip_leader(x) for x in cited))


def block_positions(lines, block):
    """1-based start lines where `block` occurs as a contiguous run of lines."""
    n = len(block)
    if n == 0:
        return []
    first = block[0]
    return [i + 1 for i in range(len(lines) - n + 1)
            if lines[i] == first and lines[i:i + n] == block]


def read_lines(tag, path):
    f = CLONE_DIR / tag / path
    if not f.is_file():
        return None
    return f.read_text(errors="replace").splitlines()


def parse_anchor(anchor, length):
    if not anchor:
        return 1, length, False
    m = re.fullmatch(r"L(\d+)(?:-L(\d+))?", anchor)
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    return lo, hi, True


def fmt_anchor(lo, hi, like=""):
    """Keep the author's spelling: `L5-L5` stays a range, `L5` stays a line."""
    return "L%d" % lo if lo == hi and "-" not in like else "L%d-L%d" % (lo, hi)


def relocate(path, anchor, quote, old, new):
    """Decide one citation. Returns a dict with `verdict` and, for `moved`,
    `anchor` (the new one)."""
    new_lines = read_lines(new, path)
    if new_lines is None:
        hint = grep_tree(new, quote) if quote else []
        return {"verdict": "judgement", "why": "path-gone", "candidates": hint}
    old_lines = read_lines(old, path) if old != new else new_lines
    if not anchor:
        if quote and not quote_spans(new_lines, quote):
            return {"verdict": "judgement", "why": "quote-gone"}
        return {"verdict": "ok"}
    lo, hi, _ = parse_anchor(anchor, len(new_lines))
    fits = 1 <= lo <= hi <= len(new_lines)
    if quote:
        if fits and in_range(new_lines, lo, hi, quote):
            return {"verdict": "ok"}
    elif fits and old_lines is not None and new_lines[lo - 1:hi] == old_lines[lo - 1:hi]:
        return {"verdict": "ok"}
    if old_lines is None:
        return {"verdict": "judgement", "why": "old-checkout-missing:%s" % old}
    if hi > len(old_lines):
        return {"verdict": "judgement", "why": "range-outside-old-file"}
    # 1. The identical block of lines moved: a pure shift.
    block = old_lines[lo - 1:hi]
    hits = block_positions(new_lines, block)
    if len(hits) == 1:
        s = hits[0]
        return {"verdict": "moved", "how": "block", "anchor": fmt_anchor(s, s + hi - lo, anchor)}
    # 2. The verbatim quote moved: keep the author's context around it.
    if quote:
        spans = quote_spans(new_lines, quote)
        if len(spans) == 1:
            nlo, nhi = spans[0]
            old_spans = [s for s in quote_spans(old_lines, quote) if lo <= s[0] and s[1] <= hi]
            if old_spans:
                before, after = old_spans[0][0] - lo, hi - old_spans[0][1]
                slo, shi = nlo - before, nhi + after
                if 1 <= slo and shi <= len(new_lines):
                    nlo, nhi = slo, shi
            return {"verdict": "moved", "how": "quote", "anchor": fmt_anchor(nlo, nhi, anchor)}
        if len(spans) > 1:
            return {"verdict": "judgement", "why": "quote-ambiguous:%d" % len(spans)}
        return {"verdict": "judgement", "why": "quote-gone"}
    if len(hits) > 1:
        return {"verdict": "judgement", "why": "block-ambiguous:%d" % len(hits)}
    return {"verdict": "judgement", "why": "unquoted-text-changed"}


def grep_tree(tag, quote):
    """Files at `tag` holding the quote's longest line-sized fragment: a hint
    for the person deciding a retarget (a port from shell to Lua, a rename)."""
    words = max(re.split(r"[.;:!?]\s", _norm(quote)), key=len)[:60].strip()
    if len(words) < 12:
        return []
    out = subprocess.run(["git", "-C", str(CLONE_DIR / tag), "grep", "-lF", words],
                         capture_output=True, text=True, check=False)
    return out.stdout.split()[:5]


# --- citation sources -----------------------------------------------------------

def level_pins():
    src = BUILD.read_text()
    block = re.search(r"^LEVELS = \[(.*?)^\]", src, re.S | re.M).group(1)
    return dict(re.findall(r'"(level-[a-z0-9-]+)".*?"(v\d+(?:\.\d+){3})"', block, re.S))


def footnotes(slug):
    """(line_index, n, target, own_tag, quote) per footnote of a level."""
    lines = (MATRIX / ("%s.md" % slug)).read_text().splitlines()
    out, in_notes, cur = [], False, None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Footnotes\s*$", line, re.I):
            in_notes = True
            continue
        if not in_notes:
            continue
        s = line.strip()
        m = FN_DEF.match(s)
        if m:
            cur = [i, m.group(1), m.group(3), m.group(4), ""]
            out.append(cur)
        elif s.startswith(">") and cur:
            cur[4] = (cur[4] + " " + s.lstrip(">").strip()).strip()
    return out


CALLOUT = re.compile(r"^>\s*(GREEN|RED|PATH|PROVEN|PLAUSIBLE|REFUTED):")


def callouts(slug):
    """(kind, first words, footnote numbers) per flag of a level's body."""
    out, cur = [], None
    for line in (MATRIX / ("%s.md" % slug)).read_text().splitlines():
        if re.match(r"^##\s+Footnotes\s*$", line, re.I):
            break
        m = CALLOUT.match(line)
        if m:
            cur = [m.group(1), " ".join(line.split()[2:10]), set()]
            out.append(cur)
        elif not line.startswith(">"):
            cur = None
        if cur is not None:
            cur[2].update(int(n) for n in re.findall(r"\[\^(\d+)\]", line))
    return out


def changed_paths(old, new, paths):
    """Paths whose content differs between two tags (the shared object store
    holds both); a path missing at either side counts as changed."""
    out = set()
    for p in sorted(paths):
        a, b = read_lines(old, p), read_lines(new, p)
        if a != b:
            out.add(p)
    return out


def review_queue(report):
    """Flags whose evidence sits in a file the release changed. Their quotes
    still resolve (or the level would not have moved), but a fix can land
    beside a quoted line without touching it, so a RED may now be false. This
    is the queue a human reviews at leisure; it never blocks a pin move."""
    queue = []
    for slug in report.get("pins_moved", []):
        old = report["levels"][slug]["from"]
        notes = {n: t for _, n, t, own, _ in footnotes(slug) if not own}
        paths = {int(n): t.partition("#")[0] for n, t in notes.items() if not t.startswith("http")}
        changed = changed_paths(old, report["to"], set(paths.values()))
        for kind, words, refs in callouts(slug):
            hit = sorted({paths[n] for n in refs if n in paths and paths[n] in changed})
            if hit and kind in ("RED", "GREEN", "PATH"):
                queue.append({"level": slug, "flag": kind, "excerpt": words, "changed": hit})
    return queue


def site_ref():
    return max(level_pins().values(), key=vkey)


def site_citations():
    """(file, start, end, path, anchor, own_tag) for big_graph and prose."""
    out = []
    for f, rx in ((BIG_GRAPH, GRAPH_CITE), (BUILD, PROSE_CITE)):
        text = f.read_text()
        for m in rx.finditer(text):
            out.append((f, m.start(1), m.end(0), m.group(1), m.group(2), m.group(3)))
    return out


def snippet(tag, path, anchor):
    lines = read_lines(tag, path)
    if lines is None or not anchor:
        return ""
    lo, hi, _ = parse_anchor(anchor, len(lines))
    return _norm(" ".join(lines[lo - 1:min(hi, lo + 2)]))[:160]


# --- plan and apply -------------------------------------------------------------

def plan(new):
    pins = level_pins()
    old_site = site_ref()
    report = {"to": new, "levels": {}, "site": {"from": old_site, "items": []}}
    for slug, pin in sorted(pins.items()):
        items = []
        for idx, n, target, own, quote in footnotes(slug):
            if target.startswith(("http://", "https://")):
                continue
            path, _, anchor = target.partition("#")
            item = {"n": int(n), "target": target, "line": idx + 1}
            if own:
                # A footnote pinned past the level: it acknowledges a daily
                # fix. Once the stable pin reaches that tag, the sentence that
                # says "not yet promoted" has changed truth value.
                if vkey(new) >= vkey(own):
                    item.update(verdict="judgement", why="daily-fix-reached-stable:@%s" % own)
                else:
                    item.update(verdict="ok", why="own-tag:@%s" % own)
            elif pin == new:
                item.update(relocate(path, anchor, quote, new, new))
            else:
                item.update(relocate(path, anchor, quote, pin, new))
            if item["verdict"] == "moved":
                item["new_target"] = path + "#" + item["anchor"]
            if item["verdict"] == "judgement":
                item["quote"] = quote
                item["was"] = snippet(pin, path, anchor) if not quote else ""
            items.append(item)
        report["levels"][slug] = {"from": pin, "items": items}
    for f, _s, _e, path, anchor, own in site_citations():
        item = {"file": f.relative_to(ROOT).as_posix(), "target": path + ("#" + anchor if anchor else ""),
                "own": own or ""}
        base = own or old_site
        item.update(relocate(path, anchor, "", base, new))
        if item["verdict"] == "moved":
            item["new_target"] = path + "#" + item["anchor"]
        if item["verdict"] == "judgement":
            item["was"] = snippet(base, path, anchor)
            item["held_at"] = base
        report["site"]["items"].append(item)
    return report


def summarise(report):
    moved = judged = 0
    for lvl in report["levels"].values():
        moved += sum(i["verdict"] == "moved" for i in lvl["items"])
        judged += sum(i["verdict"] == "judgement" for i in lvl["items"])
    moved += sum(i["verdict"] == "moved" for i in report["site"]["items"])
    judged_site = sum(i["verdict"] == "judgement" for i in report["site"]["items"])
    return moved, judged, judged_site


# Level 5 moves only through an OpenSpec change the operator reviews
# (docs/matrix/README.md). The change `automated-release-refresh` proposes that
# a move made only of mechanical re-anchors needs no review; until the operator
# accepts it, and it is archived, a level-5 move is written as a proposal
# instead of applied. Deleting the change without archiving keeps the old rule.
PROPOSAL_GATED = ("level-5-phd",)


def rule_accepted():
    return any((ROOT / "openspec" / "changes" / "archive").glob("*automated-release-refresh"))


def write_proposal(slug, lvl, new):
    """The level-5 proposal, generated: every delta with its evidence."""
    d = ROOT / "openspec" / "changes" / ("level-5-%s" % new.replace(".", "-"))
    if d.exists() and not (d / "proposal.md").read_text().startswith("# Move level 5 to %s (generated" % new):
        d = d.with_name(d.name + "-generated")  # never overwrite a hand-written proposal
    moved = [i for i in lvl["items"] if i["verdict"] == "moved"]
    judged = [i for i in lvl["items"] if i["verdict"] == "judgement"]
    rows = "\n".join("| [^%d] | `%s` | `#%s` | %s |" % (
        i["n"], i["target"], i["anchor"],
        "identical lines found once" if i["how"] == "block" else "verbatim quote found once")
        for i in moved)
    ask = "\n".join("- [^%d] `%s`: %s" % (i["n"], i["target"], i["why"]) for i in judged)
    d.mkdir(parents=True, exist_ok=True)
    (d / "proposal.md").write_text(
        "# Move level 5 to %s (generated by the release refresh)\n\n"
        "Generated by `scripts/anchors.py` from the checkouts at `%s` and `%s`. Every row below\n"
        "is mechanical: the cited text was found again, verbatim, at the new tag. No prose,\n"
        "label, quote or flag changes.\n\n"
        "| Footnote | Old target | New range | Evidence |\n| --- | --- | --- | --- |\n%s\n\n"
        "%s" % (new, lvl["from"], new, rows or "| none | | | |",
                ("## Needs a person\n\nThe text of these citations was not found again; "
                 "the pin cannot move until each is decided.\n\n%s\n" % ask) if ask else ""))
    (d / "tasks.md").write_text(
        "# Tasks\n\n- [x] Generate the delta list from the checkouts (`scripts/anchors.py`).\n"
        "- [ ] Operator review, then apply exactly these rows and move the pin.\n")
    (d / ".openspec.yaml").write_text("schema: spec-driven\ncreated: \"%s\"\n" % new)
    return d.relative_to(ROOT).as_posix()


def apply(report):
    new = report["to"]
    moved_levels = []
    report["proposals"] = []
    for slug, lvl in report["levels"].items():
        if lvl["from"] == new:
            continue
        if slug in PROPOSAL_GATED and not rule_accepted():
            report["proposals"].append(write_proposal(slug, lvl, new))
            continue
        if any(i["verdict"] == "judgement" for i in lvl["items"]):
            continue  # the level keeps its old pin; its old citations still hold there
        path = MATRIX / ("%s.md" % slug)
        lines = path.read_text().split("\n")
        for i in lvl["items"]:
            if i["verdict"] != "moved":
                continue
            j = i["line"] - 1
            lines[j] = lines[j].replace("| " + i["target"], "| " + i["new_target"], 1)
        path.write_text("\n".join(lines))
        moved_levels.append(slug)
    if moved_levels:
        src = BUILD.read_text()
        head, sep, rest = src.partition("LEVELS = [")
        body, end, tail = rest.partition("\n]\n")
        for slug in moved_levels:
            old = report["levels"][slug]["from"]
            body = re.sub(r'("%s".*?)"%s"' % (re.escape(slug), re.escape(old)),
                          lambda m: m.group(1) + '"%s"' % new, body, count=1, flags=re.S)
        BUILD.write_text(head + sep + body + end + tail)
    # Site-wide citations follow the newest pin, which only moved if a level did.
    if site_ref() != report["site"]["from"]:
        for f in (BIG_GRAPH, BUILD):
            rel = f.relative_to(ROOT).as_posix()
            text = f.read_text()
            for i in report["site"]["items"]:
                if i["file"] != rel:
                    continue
                was = i["target"] + ("@" + i["own"] if i["own"] else "")
                now = {"moved": i.get("new_target"), "ok": i["target"],
                       "judgement": i["target"] + "@" + i.get("held_at", "")}[i["verdict"]]
                text = _swap(text, was, now)
            f.write_text(text)
    return moved_levels


def _swap(text, old, new):
    """Rewrite one citation literal exactly; the closing quote stops a short
    path from matching the front of a longer one."""
    for pre in ('"runtime:', 'rcite("'):
        text = text.replace(pre + old + '"', pre + new + '"')
    return text


def main(argv):
    if len(argv) < 3 or argv[0] not in ("plan", "apply") or argv[1] != "--to" or not TAG.match(argv[2]):
        print(__doc__.split("Usage:")[1])
        print("blocked:usage")
        return 2
    new = argv[2]
    out = argv[argv.index("--json") + 1] if "--json" in argv else None
    if not (CLONE_DIR / new).is_dir():
        print("blocked:missing-checkout:%s" % new)
        return 2
    report = plan(new)
    moved, judged, judged_site = summarise(report)
    report["summary"] = {"moved": moved, "judgement_levels": judged, "judgement_site": judged_site}
    if argv[0] == "apply":
        report["pins_moved"] = apply(report)
        report["review_queue"] = review_queue(report)
    if out:
        pathlib.Path(out).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    for slug, lvl in report["levels"].items():
        c = {k: sum(i["verdict"] == k for i in lvl["items"]) for k in ("ok", "moved", "judgement")}
        print("  %-18s %s -> %s  ok %d  moved %d  judgement %d"
              % (slug, lvl["from"], new, c["ok"], c["moved"], c["judgement"]))
        for i in lvl["items"]:
            if i["verdict"] == "judgement":
                print("      [^%d] %s  %s" % (i["n"], i["target"], i["why"]))
    s = report["site"]["items"]
    print("  %-18s %s -> %s  ok %d  moved %d  judgement %d"
          % ("site-prose+graph", report["site"]["from"], new,
             sum(i["verdict"] == "ok" for i in s), sum(i["verdict"] == "moved" for i in s),
             judged_site))
    for i in s:
        if i["verdict"] == "judgement":
            print("      %s %s  %s (held at %s)" % (i["file"], i["target"], i["why"], i["held_at"]))
    for d in report.get("proposals", []):
        print("  proposal written for operator review: %s" % d)
    if judged or judged_site or report.get("proposals"):
        print("ask:anchors:%d" % (judged + judged_site + len(report.get("proposals", []))))
        return 3
    print("ok:anchors:%d" % moved)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
