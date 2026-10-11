#!/usr/bin/env bash
# Report-only view of what the release refresh would do at the stable tag:
# which levels would move, which citations would be re-anchored, and which need
# a person. Nothing is edited. This is `anchors.py plan`; the older version
# counted changed files and ran a trial build, which said that something broke
# but not what to do about it (scripts/anchors.py says which rule found it).
#
#   drift-report.sh [vTAG]          default: the stable channel
#
# Last line: `ok:up-to-date` (every level already pins the tag),
# `drift:<levels-behind>:<needs-a-person>`, or `blocked:<why>`.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
tag=${1:-$("$HERE/latest-release.sh" | tail -1)}
case "$tag" in blocked:*|"") echo "${tag:-blocked:no-tag}"; exit 2;; esac
out=$(python3 "$ROOT/scripts/anchors.py" plan --to "$tag")
rc=$?
echo "$out"
[ "$rc" -eq 2 ] && exit 2
behind=$("$HERE/pinned-refs.sh" | awk -v t="$tag" '$2 != t' | grep -c .)
asks=$(echo "$out" | tail -1 | sed -n 's/^ask:anchors://p')
if [ "$behind" -eq 0 ]; then
  echo "ok:up-to-date"
else
  echo "drift:$behind:${asks:-0}"
fi
