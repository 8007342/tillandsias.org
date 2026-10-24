#!/usr/bin/env bash
# Fixture for `release-refresh.sh --unattended`, the forge run with no
# operator. A copy of this checkout in a scratch dir, an empty HOME, a local
# "runtime" repo with one tag, a local bare origin, and a git wrapper on PATH
# that records every push. TILLANDSIAS_REFRESH_STUB stands in for the
# mechanical steps (see scripts/refresh.py), so no runtime checkout is needed.
#
#   1  clones default inside the checkout (var/unattended/), never ~/.cache,
#      and the full-history clone is bootstrapped from the runtime remote
#   2  a clean run pushes website/update-<tag> and auto-merges it into main,
#      but only after the checked build passes; a red build leaves main alone
#   3  an unsettled judgement item stops the run (ask:judgement, no push);
#      the same item named in a docs/audit/*-issues-*.md record is pushed to
#      the branch and never merged
#
# Last line: `ok:unattended-refresh:<n> case(s)` or `violation:unattended-refresh:<n>`.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
REAL_GIT=$(command -v git)
T=$(mktemp -d "$ROOT/var/unattended-fixture.XXXXXX")
trap 'rm -rf "$T"' EXIT
TAG=v1.2.3.4
BR=website/update-$TAG
fails=0; cases=0
check() { cases=$((cases + 1)); if eval "$2"; then echo "ok:   $1"; else echo "FAIL: $1"; fails=$((fails + 1)); fi; }

mkdir -p "$T/home" "$T/bin"
cat > "$T/bin/git" <<WRAP
#!/usr/bin/env bash
for a in "\$@"; do [ "\$a" = push ] && { printf '%s\n' "\$*" >> "$T/push.log"; break; }; done
exec "$REAL_GIT" "\$@"
WRAP
chmod +x "$T/bin/git"
G() { "$REAL_GIT" -c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false "$@"; }

# the runtime remote: one tag, so the history clone has something to clone
G init -q "$T/runtime" && G -C "$T/runtime" commit -q --allow-empty -m runtime && G -C "$T/runtime" tag "$TAG"
# the site: this working tree (uncommitted changes included) on main, origin a local bare
mkdir "$T/site"
tar -C "$ROOT" --exclude=./.git --exclude=./var/unattended --exclude="./var/$(basename "$T")" -cf - . | tar -C "$T/site" -xf -
G init -q -b main "$T/site" && G -C "$T/site" add -A && G -C "$T/site" commit -q -m site
G init -q --bare "$T/origin.git" && G -C "$T/site" remote add origin "$T/origin.git" && G -C "$T/site" push -q origin main
main_before=$(G -C "$T/origin.git" rev-parse main)
build() { printf '#!/bin/sh\necho %s\n' "$1" > "$T/build"; chmod +x "$T/build"; }

run() {  # $1 = stub json; prints output, returns the exit code
  printf '%s\n' "$1" > "$T/stub.json"
  (cd "$T/site" && env -u TILLANDSIAS_CLONE_DIR -u TILLANDSIAS_HISTORY_REPO HOME="$T/home" PATH="$T/bin:$PATH" \
     GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@invalid GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@invalid \
     TILLANDSIAS_REPO_URL="$T/runtime" TILLANDSIAS_REFRESH_STUB="$T/stub.json" TILLANDSIAS_CHECKED_BUILD="$T/build" \
     skills/update-website/scripts/release-refresh.sh --tag "$TAG" --unattended 2>&1)
}

# 2a: a red checked build stops before main
build blocked:build-warnings
echo '{"fixture": 1}' > "$T/site/refresh.d/00000000T000000Z-fixture.json"
out=$(run '{"rc": 0, "judgement": []}'); rc=$?
check "a red build ends blocked:checked-build-before-merge (rc=$rc)" '[ $rc != 0 ] && [ "$(printf "%s" "$out" | tail -1)" = "blocked:checked-build-before-merge" ]'
check "and main did not move" '[ "$(G -C "$T/origin.git" rev-parse main)" = "$main_before" ]'
check "nothing went to main" '! grep -q "refs/heads/main" "$T/push.log" 2>/dev/null'

# 1 + 2: a clean refresh, green build
build ok:checked-build
: > "$T/push.log"
out=$(run '{"rc": 0, "judgement": []}'); rc=$?
check "clean run ends ok:merged:$TAG (rc=$rc)" '[ $rc = 0 ] && [ "$(printf "%s" "$out" | tail -1)" = "ok:merged:$TAG" ]'
check "history clone bootstrapped under var/unattended/clones" '[ -d "$T/site/var/unattended/clones/.history/.git" ]'
check "nothing written under HOME" '[ -z "$(ls -A "$T/home")" ]'
check "the checkout is on $BR, not main" '[ "$(G -C "$T/site" rev-parse --abbrev-ref HEAD)" = "$BR" ]'
check "the refresh was committed and pushed to $BR" '[ "$(G -C "$T/origin.git" rev-parse "$BR" 2>/dev/null)" = "$(G -C "$T/site" rev-parse HEAD)" ]'
check "main was auto-merged to the branch head" '[ "$(G -C "$T/origin.git" rev-parse main)" = "$(G -C "$T/site" rev-parse HEAD)" ]'
check "pushes go only to $BR, and main last" '[ "$(awk "{print \$NF}" "$T/push.log" | sort -u | tr "\n" " ")" = "HEAD:refs/heads/main HEAD:refs/heads/$BR " ] && [ "$(tail -1 "$T/push.log" | awk "{print \$NF}")" = HEAD:refs/heads/main ]'
main_before=$(G -C "$T/origin.git" rev-parse main)

# 3: judgement must end settled or filed
: > "$T/push.log"
item='{"rc": 3, "judgement": [{"level": "level-2", "n": 4, "target": "crates/x/src/lib.rs#L10-L12@v1.2.3.4", "why": "quote-gone"}]}'
out=$(run "$item"); rc=$?
check "an unfiled judgement item stops with ask:judgement:1 (rc=$rc)" '[ $rc = 3 ] && [ "$(printf "%s" "$out" | tail -1)" = "ask:judgement:1" ]'
check "and nothing is pushed" '[ ! -s "$T/push.log" ]'
mkdir -p "$T/site/docs/audit"
printf '## crates/x/src/lib.rs#L10-L12@v1.2.3.4 quote gone at %s\n' "$TAG" > "$T/site/docs/audit/2000-01-01-issues-tillandsias.md"
out=$(run "$item"); rc=$?
check "the same item filed via file-findings is delivered (rc=$rc)" '[ $rc = 0 ] && [ "$(printf "%s" "$out" | tail -1)" = "ok:pushed:$BR:filed:1" ]'
check "the finding record went out with the push" 'G -C "$T/origin.git" cat-file -e "$BR:docs/audit/2000-01-01-issues-tillandsias.md"'
check "a run with judgement never merges" '[ "$(G -C "$T/origin.git" rev-parse main)" = "$main_before" ] && ! grep -q "refs/heads/main" "$T/push.log"'

if [ "$fails" -gt 0 ]; then echo "violation:unattended-refresh:$fails"; exit 1; fi
echo "ok:unattended-refresh:$cases case(s)"
