#!/usr/bin/env bash
# Print the release tag each level pins, one `slug<TAB>tag` per line, read from
# the LEVELS table of scripts/build-matrix.py. Nothing else in that block looks
# like a tag, so slug and tag pair up in order.
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
out=$(awk '/^LEVELS = \[/{f=1;next} f&&/^\]/{exit} f' "$ROOT/scripts/build-matrix.py" \
  | grep -oE '"level-[a-z0-9-]+"|"v[0-9]+(\.[0-9]+){3}"' | tr -d '"' | paste - -)
if [ -z "$out" ]; then
  echo "blocked:no-levels-parsed"
  exit 2
fi
echo "$out"
