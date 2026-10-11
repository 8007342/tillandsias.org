#!/usr/bin/env bash
# The one entry command for "a release happened". Everything that needs no
# judgement, in order: re-pin by content, regenerate Progress and CentiColon
# data, rebuild the metrics history, checked build, append the run to
# refresh.d/. See scripts/refresh.py for the steps and skills/update-website.
#
#   release-refresh.sh [--tag vX.Y.Z.B] [--offline] [--history DIR] [--learned SURFACE:NOTE]
#
# Last line: `ok:refreshed:<tag>`, `ask:judgement:<n>` (exit 3) or `blocked:<why>`.
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
exec python3 "$ROOT/scripts/refresh.py" "$@"
