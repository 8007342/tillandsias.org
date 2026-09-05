#!/usr/bin/env bash
# Ensure a checkout of the Tillandsias runtime exists for every tag the levels
# pin, for the stable channel's tag, and for the newest daily, as
# `$TILLANDSIAS_CLONE_DIR/<tag>`. Extra tags may be passed as arguments.
#
# One shallow object store (`$TILLANDSIAS_CLONE_DIR/.repo`) with a worktree per
# tag, so `git -C .repo diff <old> <new>` works across tags while each fetch
# stays one commit deep. Put the dir on real disk: the forge's /tmp is a
# 256 MB tmpfs and a checkout is ~70 MB.
#
# Last line: `ok:checkouts:<dir>` or `blocked:<why>`.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO_URL=${TILLANDSIAS_REPO_URL:-https://github.com/8007342/tillandsias}
CLONE_DIR=${TILLANDSIAS_CLONE_DIR:-$HOME/.cache/tillandsias-org/clones}
BASE="$CLONE_DIR/.repo"

pins=$("$HERE/pinned-refs.sh" | cut -f2 | sort -u)
stable=$("$HERE/latest-release.sh" | tail -1)
case "$stable" in blocked:*) echo "$stable"; exit 2;; esac
daily=$("$HERE/latest-release.sh" --channel unstable | tail -1)
case "$daily" in blocked:*) echo "$daily"; exit 2;; esac
tags=$(printf '%s\n%s\n%s\n%s\n' "$pins" "$stable" "$daily" "$*" | tr ' ' '\n' | grep -E '^v[0-9]' | sort -u)

mkdir -p "$CLONE_DIR"
if [ ! -e "$BASE/.git" ]; then
  first=$(echo "$tags" | head -1)
  git clone --quiet --depth 1 --no-checkout --branch "$first" "$REPO_URL" "$BASE" \
    || { echo "blocked:clone-failed:$REPO_URL"; exit 2; }
fi
for tag in $tags; do
  if ! git -C "$BASE" rev-parse -q --verify "refs/tags/$tag^{commit}" >/dev/null; then
    git -C "$BASE" fetch --quiet --depth 1 origin "tag" "$tag" \
      || { echo "blocked:fetch-failed:$tag"; exit 2; }
  fi
  if [ ! -d "$CLONE_DIR/$tag" ]; then
    git -C "$BASE" worktree add --quiet "$CLONE_DIR/$tag" "$tag" \
      || { echo "blocked:worktree-failed:$tag"; exit 2; }
  fi
  role=""
  [ "$tag" = "$stable" ] && role="stable"
  [ "$tag" = "$daily" ] && role="${role:+$role,}newest-daily"
  echo "  $tag  $(git -C "$CLONE_DIR/$tag" rev-parse --short HEAD)  $CLONE_DIR/$tag  ${role:+($role)}"
done
echo "ok:checkouts:$CLONE_DIR"
