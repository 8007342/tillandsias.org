#!/usr/bin/env bash
# Print the newest Tillandsias release tag on a channel.
#
#   latest-release.sh                    stable channel (default)
#   latest-release.sh --channel unstable newest daily build
#
# Two channels come out of one release stream (methodology/versioning.yaml in
# the runtime repo): every daily is published as a GitHub PRE-release, and
# `/releases/latest` — what the site's install commands resolve — moves only
# when scripts/promote-stable.sh promotes a vetted daily. The prerelease bit
# is the channel. So:
#   stable   = the tag `/releases/latest` serves, read with cache-busting
#              headers because the enclave proxy caches API responses; it is
#              cross-checked against the newest non-prerelease tag and against
#              the runtime repo's `stable` git tag, with a warning on stderr
#              when they disagree (GitHub's make_latest is sticky).
#   unstable = the newest version tag over git; no API needed.
#
# Last line: the tag, or `blocked:<why>` with a non-zero exit.
set -uo pipefail

REPO_URL=${TILLANDSIAS_REPO_URL:-https://github.com/8007342/tillandsias}
API_URL=${TILLANDSIAS_API_URL:-https://api.github.com/repos/8007342/tillandsias}
channel=stable
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) channel=${2:-stable}; shift 2 ;;
    *) echo "blocked:bad-argument:$1"; exit 2 ;;
  esac
done

refs=$(git ls-remote --tags "$REPO_URL" 2>/dev/null)
if [ -z "$refs" ]; then
  echo "blocked:no-tags-readable:$REPO_URL"
  exit 2
fi
versions=$(echo "$refs" | awk '{print $2}' | sed 's#^refs/tags/##; s#\^{}$##' \
  | grep -E '^v[0-9]+(\.[0-9]+){3}$' | sort -u | sort -V)
newest=$(echo "$versions" | tail -1)

if [ "$channel" = "unstable" ]; then
  echo "$newest"
  exit 0
fi
if [ "$channel" != "stable" ]; then
  echo "blocked:unknown-channel:$channel"
  exit 2
fi
if ! command -v curl >/dev/null || ! command -v jq >/dev/null; then
  echo "blocked:stable-needs-curl-and-jq"
  exit 2
fi

api() { curl -fsS -m 20 -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "$API_URL/$1" 2>/dev/null; }

stable=$(api releases/latest | jq -r '.tag_name // empty')
if [ -z "$stable" ]; then
  echo "blocked:api-unreachable:releases/latest"
  exit 2
fi

# Cross-check 1: the newest non-prerelease tag, walking back from the newest.
for tag in $(echo "$versions" | tail -8 | tac); do
  rel=$(api "releases/tags/$tag") || continue
  if [ "$(jq -r '.draft' <<<"$rel")" = "false" ] && [ "$(jq -r '.prerelease' <<<"$rel")" = "false" ]; then
    [ "$tag" != "$stable" ] && echo "warn: newest non-prerelease is $tag but /releases/latest serves $stable (sticky make_latest)" >&2
    break
  fi
done
# Cross-check 2: the runtime repo's `stable` git tag, which promotion moves.
stable_sha=$(echo "$refs" | awk '$2=="refs/tags/stable^{}"{print $1}')
[ -n "$stable_sha" ] || stable_sha=$(echo "$refs" | awk '$2=="refs/tags/stable"{print $1}')
release_sha=$(echo "$refs" | awk -v t="refs/tags/$stable^{}" '$2==t{print $1}')
[ -n "$release_sha" ] || release_sha=$(echo "$refs" | awk -v t="refs/tags/$stable" '$2==t{print $1}')
if [ -n "$stable_sha" ] && [ "$stable_sha" != "$release_sha" ]; then
  # Observed 2026-09-05: the tag sat eleven days behind the promoted release
  # because promotion tagged the promoting checkout's local main. Fixed at the
  # script upstream; moving the published tag is an operator decision. Derive
  # the channel from the releases endpoint, never from this tag.
  echo "warn: git tag 'stable' (${stable_sha:0:9}) is not at $stable (${release_sha:0:9}); using the releases endpoint, which is authoritative" >&2
fi

echo "$stable"
