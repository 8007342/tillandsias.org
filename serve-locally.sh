#!/usr/bin/env bash
# Rebuild the site and reuse a named Apache container. No custom image needed.
set -euo pipefail

site_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
container_name=${CONTAINER_NAME:-tillandsias-org-preview}
port=${PORT:-8080}
image=${HTTPD_IMAGE:-docker.io/library/httpd:2.4-alpine}
engine=${CONTAINER_ENGINE:-}

if [[ -z "$engine" ]]; then
    if command -v podman >/dev/null 2>&1; then
        engine=podman
    elif command -v docker >/dev/null 2>&1; then
        engine=docker
    else
        echo 'Install Podman or Docker to run the local preview.' >&2
        exit 1
    fi
fi
if [[ ! "$port" =~ ^[0-9]{1,5}$ ]] || ((10#$port < 1 || 10#$port > 65535)); then
    echo 'PORT must be a number between 1 and 65535.' >&2
    exit 1
fi
port=$((10#$port))
command -v "$engine" >/dev/null
command -v curl >/dev/null
"$engine" info >/dev/null
python3 "$site_root/scripts/build-matrix.py"

# A configuration label prevents accidental reuse of an unrelated container or
# a preview belonging to another checkout. Never remove containers implicitly.
config="$site_root|$port|$image"
label=org.tillandsias.local-preview
existing=$("$engine" container ls -a --format '{{.Names}}')
if printf '%s\n' "$existing" | grep -Fxq -- "$container_name"; then
    actual=$("$engine" inspect --format "{{index .Config.Labels \"$label\"}}" "$container_name")
    if [[ "$actual" != "$config" ]]; then
        echo "Container '$container_name' exists with a different preview configuration." >&2
        echo 'Choose another CONTAINER_NAME, or explicitly remove the old preview first.' >&2
        exit 1
    fi
    running=$("$engine" inspect --format '{{.State.Running}}' "$container_name")
    if [[ "$running" != true ]]; then
        "$engine" start "$container_name" >/dev/null
    fi
else
    "$engine" run --detach --name "$container_name" \
        --label "$label=$config" \
        --publish "127.0.0.1:$port:80" \
        --volume "$site_root/var/html:/usr/local/apache2/htdocs:ro,Z" \
        "$image" >/dev/null
fi

url="http://127.0.0.1:$port/"
for ((attempt = 0; attempt < 30; attempt++)); do
    if curl --noproxy '*' --fail --silent --max-time 2 "$url" >/dev/null; then
        printf '\nPreview ready: %s#slides\n' "$url"
        printf 'Re-run ./serve-locally.sh to rebuild and reuse this container.\n'
        printf 'Stop: %s stop %s\n' "$engine" "$container_name"
        exit 0
    fi
    sleep 1
done
echo "Preview did not become ready at $url" >&2
"$engine" logs --tail 30 "$container_name" >&2
exit 1
