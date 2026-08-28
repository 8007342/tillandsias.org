#!/usr/bin/env bash
# Container entrypoint for tillandsias.org
#
# On every start:
#   1. Take the CloudFlare API token from the podman secret /run/secrets/cf-token
#      (never baked into the image).
#   2. Ensure A records for tillandsias.org and www.tillandsias.org point at the
#      current public IP (creating them if absent) so the domain serves this
#      container.
#   3. Start Apache httpd serving the site at the apex.
set -euo pipefail

log() { echo "[entrypoint] $*"; }

CF_TOKEN_FILE="${CF_TOKEN_FILE:-/run/secrets/cf-token}"
# live (default) updates DNS; dry-run prints only; skip does nothing.
CF_DDNS_MODE="${CF_DDNS_MODE:-live}"

if [ "$CF_DDNS_MODE" = "skip" ]; then
  log "dynamic DNS skipped (CF_DDNS_MODE=skip)"
elif [ -f "$CF_TOKEN_FILE" ]; then
  log "CloudFlare token present ($CF_TOKEN_FILE); mode=$CF_DDNS_MODE"
  # Run dynamic DNS: keep apex + www A records pointed at the current public IP.
  args=("--token-file" "$CF_TOKEN_FILE")
  [ "$CF_DDNS_MODE" = "dry-run" ] && args+=(--dry-run)
  /usr/local/bin/cloudflare-ddns "${args[@]}" || {
    log "cloudflare-ddns failed; continuing to serve (DNS may be stale)"
  }
else
  log "warning: no CloudFlare token at $CF_TOKEN_FILE; skipping dynamic DNS"
fi

log "starting httpd"
exec httpd -DFOREGROUND
