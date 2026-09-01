#!/usr/bin/env bash
# dev-run.sh - build and run the tillandsias.org container locally.
#
# Serves the site at the apex tillandsias.org (www redirects to it). On start the
# container takes the CloudFlare token from a podman secret and updates DNS
# (apex + www A records) to the current public IP via cloudflare-ddns.
#
# Usage:
#   ./scripts/dev-run.sh --mode=live    # build + run; update DNS to public IP (default)
#   ./scripts/dev-run.sh --mode=dry-run # run; check DNS changes but do not write
#   ./scripts/dev-run.sh --mode=skip    # run; do NOT touch DNS (verify serving only, no token needed)
#   ./scripts/dev-run.sh --dry-run      # one-shot cloudflare-ddns dry-run, no serve
#   ./scripts/dev-run.sh --logs         # follow logs of the running container
#   ./scripts/dev-run.sh --stop         # stop and remove the dev container
set -euo pipefail

NAME="tillandsias-web-dev"
IMAGE="tillandsias-web:latest"
CONTAINERFILE="$(dirname "$0")/../CONTAINERFILE"
CF_TOKEN_FILE="${CF_TOKEN_FILE:-$HOME/.config/tillandsias/cf-token}"
SECRET_NAME="tillandsias-cf-token"
SECRET_TARGET="/run/secrets/cf-token"

# DNS behavior on container start: live (update DNS), dry-run (no writes), skip.
DDNS_MODE="live"
action="${1:-run}"

stop_ctr() {
  if podman container exists "$NAME" 2>/dev/null; then
    podman rm -f "$NAME" >/dev/null && echo "removed container $NAME"
  fi
}

public_ip4() {
  local ip
  for p in "https://api.ipify.org" "https://api4.ipify.org"; do
    if ip="$(curl -fsSL --max-time 10 "$p" 2>/dev/null)" && [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "$ip"; return 0
    fi
  done
  return 1
}

public_ip6() {
  local ip
  for p in "https://api6.ipify.org" "https://api64.ipify.org"; do
    if ip="$(curl -fsSL --max-time 10 "$p" 2>/dev/null)" && [[ "$ip" =~ : ]]; then
      echo "$ip"; return 0
    fi
  done
  return 1
}

case "$action" in
  --stop)
    stop_ctr
    exit 0
    ;;
  --logs)
    exec podman logs -f "$NAME"
    ;;
esac

# parse --mode after the action
for arg in "$@"; do
  case "$arg" in
    --mode=*) DDNS_MODE="${arg#--mode=}" ;;
  esac
done
case "$DDNS_MODE" in
  live|dry-run|skip) ;;
  *) echo "error: --mode must be live|dry-run|skip (got $DDNS_MODE)" >&2; exit 1 ;;
esac

# Only the DNS-touching modes need a CloudFlare token. --mode=skip exists to
# verify serving alone, so it must run on a machine that has no token at all.
needs_token=yes
if [ "$DDNS_MODE" = "skip" ] && [ "$action" != "--dry-run" ]; then
  needs_token=no
fi

if [ "$needs_token" = yes ] && [ ! -f "$CF_TOKEN_FILE" ]; then
  echo "error: CloudFlare token not found at $CF_TOKEN_FILE" >&2
  echo "       create it in the CF dashboard and store it there (chmod 600)." >&2
  echo "       (to serve without touching DNS, use --mode=skip — no token needed)" >&2
  exit 1
fi

if [ "$needs_token" = yes ]; then
  echo "==> Public IP check"
  ip4="$(public_ip4 2>/dev/null || true)"
  ip6="$(public_ip6 2>/dev/null || true)"
  [ -n "$ip4" ] && echo "    public IPv4: $ip4"
  [ -n "$ip6" ] && echo "    public IPv6: $ip6"
  if [ -z "$ip4" ] && [ -z "$ip6" ]; then
    echo "WARNING: no reachable public IP detected (you're likely behind NAT/CGNAT)." >&2
    echo "         Dynamic DNS cannot point the domain here from this host." >&2
    echo "         Without a public IP, use a Cloudflare Tunnel (requires extra" >&2
    echo "         account-level token permissions). Continuing anyway." >&2
  else
    echo "    (cloudflare-ddns will keep tillandsias.org + www pointed here, TTL=1h)"
  fi

  echo "==> Ensuring podman secret '$SECRET_NAME'"
  if ! podman secret exists "$SECRET_NAME" 2>/dev/null; then
    podman secret create "$SECRET_NAME" "$CF_TOKEN_FILE" >/dev/null
    echo "    created podman secret from $CF_TOKEN_FILE"
  else
    echo "    podman secret '$SECRET_NAME' already exists"
  fi
  secret_args=(--secret "$SECRET_NAME,type=mount,target=$SECRET_TARGET")
else
  echo "==> mode=skip: no DNS work, so no CloudFlare token or podman secret needed"
  secret_args=()
fi

echo "==> Building image"
podman build -f "$CONTAINERFILE" -t "$IMAGE" .

stop_ctr

if [ "$action" = "--dry-run" ]; then
  echo "==> Running cloudflare-ddns in dry-run (no DNS writes)"
  podman run --rm --name "$NAME" \
    -e CF_DDNS_MODE=dry-run \
    "${secret_args[@]}" \
    "$IMAGE" /usr/local/bin/cloudflare-ddns --dry-run --token-file "$SECRET_TARGET"
  exit 0
fi

echo "==> Starting container (serving http://tillandsias.org), ddns mode=$DDNS_MODE"
podman run -d --name "$NAME" \
  -p 80:80 \
  -e "CF_DDNS_MODE=$DDNS_MODE" \
  "${secret_args[@]}" \
  "$IMAGE" >/dev/null
echo "    started $NAME"
sleep 2
podman ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'NAMES|web-dev' || true
echo
echo "    site:    http://<host-ip>/   (apex tillandsias.org)"
echo "    www:     http://<host-ip>/   (redirects to apex)"
echo "    logs:    ./scripts/dev-run.sh --logs"
echo "    stop:    ./scripts/dev-run.sh --stop"
