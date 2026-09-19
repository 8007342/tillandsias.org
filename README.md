# tillandsias.org
Website for the Tillandsias project. Pretty landing page, instructions, about, help, etc.

## Local preview

Run `./serve-locally.sh`, then open <http://127.0.0.1:8080/#slides>.
Requires Python 3, curl, and Podman or Docker. The script rebuilds the static
site and creates an official Apache `httpd:2.4-alpine` container on first use;
later runs reuse it, starting it if stopped. Only `var/html` is mounted, read-only.

Edit `scripts/slides.py` and `scripts/figures.py`, then run the script again and
refresh your browser. Override `PORT`, `CONTAINER_NAME`, `CONTAINER_ENGINE`, or
`HTTPD_IMAGE` as needed; use a new container name when changing configuration.
Stop the default preview with `podman stop tillandsias-org-preview` (or `docker stop`
when using Docker).
