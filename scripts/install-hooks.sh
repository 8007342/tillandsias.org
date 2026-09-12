#!/usr/bin/env bash
# Use the repository's tracked hooks for this checkout.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
git -C "$ROOT" config core.hooksPath .githooks
echo "ok:hooks:.githooks"
