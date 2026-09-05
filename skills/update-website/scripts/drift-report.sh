#!/usr/bin/env bash
# What would break if every level were re-pinned to the stable channel's tag,
# and what has the daily channel already changed under the pages' feet?
#
# For each level: the cited files that changed between the level's pin and
# the stable tag (a footnote into a changed file needs re-verification even
# when its line range still resolves). Then the exact broken-target list from
# a trial build pinned to the stable tag: missing paths, line ranges outside
# the file, quotes not found in their range. The trial build writes to a temp
# file; nothing in the repository is edited. Finally, informationally, the
# cited files the newest daily has changed since each pin: those are the
# places where a RED may already be fixed upstream of the stable channel.
#
# Last line: `ok:up-to-date`, `drift:<levels-affected>:<broken-targets>`, or
# `blocked:<why>`.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
CLONE_DIR=${TILLANDSIAS_CLONE_DIR:-$HOME/.cache/tillandsias-org/clones}
BASE="$CLONE_DIR/.repo"

stable=$("$HERE/latest-release.sh" | tail -1)
case "$stable" in blocked:*) echo "$stable"; exit 2;; esac
daily=$("$HERE/latest-release.sh" --channel unstable | tail -1)
case "$daily" in blocked:*) echo "$daily"; exit 2;; esac
for t in "$stable" "$daily"; do
  [ -d "$CLONE_DIR/$t" ] || { echo "blocked:missing-checkout:$t (run fetch-checkouts.sh)"; exit 2; }
done

cited_paths() {
  sed -n 's/^\[\^[0-9]*\]:.*| *\([^ #]*\).*$/\1/p' "$ROOT/docs/matrix/$1.md" | grep -vE '^https?://' | sort -u
}
changed_between() {  # $1 paths (newline separated), $2 from-tag, $3 to-tag
  [ -n "$1" ] || return 0
  git -C "$BASE" rev-parse -q --verify "refs/tags/$2^{commit}" >/dev/null 2>&1 || return 0
  echo "$1" | xargs git -C "$BASE" diff --name-only "$2" "$3" -- 2>/dev/null
}

echo "stable channel: $stable   newest daily: $daily"
echo
affected=0
repin_needed=0
while IFS=$'\t' read -r slug pin; do
  paths=$(cited_paths "$slug")
  total=$(echo "$paths" | grep -c .)
  if [ "$pin" = "$stable" ]; then
    echo "$slug: pinned to stable $stable"
  else
    repin_needed=1
    changed=$(changed_between "$paths" "$pin" "$stable")
    n=$(echo "$changed" | grep -c .)
    echo "$slug: pinned $pin; $n of $total cited files changed by stable $stable"
    [ -n "$changed" ] && echo "$changed" | sed 's/^/    /'
    [ "$n" -gt 0 ] && affected=$((affected + 1))
  fi
  if [ "$daily" != "$pin" ]; then
    dchanged=$(changed_between "$paths" "$pin" "$daily")
    dn=$(echo "$dchanged" | grep -c .)
    echo "    daily $daily has changed $dn of $total cited files since $pin"
  fi
done < <("$HERE/pinned-refs.sh")

broken=0
if [ "$repin_needed" -eq 1 ]; then
  tmp=$(mktemp)
  trial=$(cd "$ROOT" && TILLANDSIAS_PIN_OVERRIDE="$stable" TILLANDSIAS_OUT="$tmp" \
          TILLANDSIAS_CLONE_DIR="$CLONE_DIR" python3 scripts/build-matrix.py 2>&1)
  rm -f "$tmp"
  broken=$(echo "$trial" | grep -cE '^\s{4}level-')
  echo
  echo "trial build pinned to stable $stable:"
  echo "$trial" | grep -E 'BROKEN|^\s{4}level-|all checked' | sed 's/^/  /'
fi

if [ "$repin_needed" -eq 0 ] || { [ "$affected" -eq 0 ] && [ "$broken" -eq 0 ]; }; then
  echo "ok:up-to-date"
else
  echo "drift:$affected:$broken"
fi
