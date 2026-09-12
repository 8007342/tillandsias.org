#!/usr/bin/env bash
# Build the page with every pinned checkout present, so each footnote target
# and quote is verified. Refuses to pass when a checkout for a pinned tag is
# missing: an unchecked level is not a checked build.
#
# Last line: `ok:checked-build` or `blocked:<why>`; exit non-zero on anything
# that should stop a publish.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
CLONE_DIR=${TILLANDSIAS_CLONE_DIR:-$HOME/.cache/tillandsias-org/clones}

# Every release the pages cite, not only the ones they pin: a footnote may
# carry an `@vTAG` suffix for a fix that exists in a newer build, and a gate
# that demands only the pins passes while those go unopened.
cited=$( { "$HERE/pinned-refs.sh" | cut -f2
           grep -hoE '@v[0-9]+(\.[0-9]+){3}' "$ROOT"/docs/matrix/level-*.md | tr -d '@'
         } | sort -u )
missing=""
for tag in $cited; do
  [ -d "$CLONE_DIR/$tag" ] || missing="$missing $tag"
done
if [ -n "$missing" ]; then
  echo "blocked:missing-checkouts:$missing (run fetch-checkouts.sh)"
  exit 2
fi

ledger=$(cd "$ROOT" && TILLANDSIAS_CLONE_DIR="$CLONE_DIR" python3 scripts/issues.py validate 2>&1)
rc=$?
echo "$ledger"
if [ "$rc" -ne 0 ] || echo "$ledger" | grep -q 'UNCHECKED'; then
  echo "blocked:issues-not-verified"
  exit 1
fi

out=$(cd "$ROOT" && TILLANDSIAS_CLONE_DIR="$CLONE_DIR" python3 scripts/build-matrix.py 2>&1)
rc=$?
echo "$out"
if [ $rc -ne 0 ] || echo "$out" | grep -q 'BROKEN'; then
  echo "blocked:footnotes-do-not-resolve"
  exit 1
fi
if echo "$out" | grep -qE '^\s*! '; then
  echo "blocked:build-warnings"
  exit 1
fi
if echo "$out" | grep -q 'UNCHECKED'; then
  echo "blocked:targets-unchecked"
  exit 1
fi
echo "ok:checked-build"
