# Design: add-container-framework

## Overview

A single immutable Podman image serves the www.tillandsias.org static site over
HTTPS, keeps its CloudFlare DNS current, and issues/renews its Let's Encrypt
wildcard certificate. Image is amd64 for now (arm64 later). Deployed rootless on
Fedora Silverblue and Fedora Cloud.

```
                        +-----------------------------+
   Internet <--80/443-->|  PODMAN ROOTLESS CONTAINER  |
                        |  +------------------------+ |
                        |  | Apache httpd (httpd:2.4)| |
                        |  |  - :80 apex redirect    | |
                        |  |  - :443 www vhost       | |
                        |  +------------------------+ |
                        |  | certbot (LE, DNS-01)    | |
                        |  +------------------------+ |
                        |  | cloudflare-ddns updater | |
                        |  +------------------------+ |
                        |  | site bundle (zip) mount | |
                        |  +------------------------+ |
                        +-------------+----------------+
                                      |
                    secret: CF API token (Zone:DNS:Edit)
                                      |
                               CloudFlare API
```

## Image (CONTAINERFILE)

- Base: `httpd:2.4` (official).
- Multi-stage: build/validation stage assembles the versioned site zip; the
  final stage installs httpd config, certbot + certbot-dns-cloudflare,
  cloudflare-ddns, and entrypoint scripts.
- Image is sealed/immutable for code and configuration; only ephemeral writable
  state (certificates, LE account, site bundle extracted at start) lives in a
  writable layer/volume.
- Minimal set of packages; non-root runtime user; seccomp/AppArmor/SELinux
  profiles applied at deploy.

## HTTPS

- Canons: `www.tillandsias.org` serves content; apex `tillandsias.org` issues a
  301 redirect to `www.tillandsias.org`.
- certbot issues one wildcard cert covering `*.tillandsias.org` and
  `tillandsias.org` using the **DNS-01** challenge via the CloudFlare plugin, so
  no public port 80 inbound is required for issuance.
- Apache config loads the managed cert bundle; renewal runs on a timer via the
  entrypoint, reloading httpd after renewal.
- Port 80 still serves the redirect + ACME/HTTP bootstrap where reachable.

## Dynamic DNS

- `cloudflare-ddns` script polls the public IP (e.g. via a resolver) and, when
  it changes, updates the zone's A/AAAA records for `tillandsias.org`,
  `www.tillandsias.org`, and `*.tillandsias.org` using the CloudFlare API.
- Scope: only this zone's own records (not arbitrary zone management).

## Secrets

- CloudFlare API token scoped to `Zone:DNS:Edit` for the zone.
- Injected at runtime as a Podman secret (`--secret`), mounted read-only into
  the container, never baked into the image or committed to the repo.
- Token passed to certbot-dns-cloudflare and cloudflare-ddns via env/file with
  restrictive file permissions and SELinux labels.

## Deployment (Podman)

- Rootless Podman, managed by a systemd Quadlet unit.
- SELinux enabled; containerized SELinux policies confine the image and mounts.
- Ports 80/443 published from the host to the container.
- Target hosts: Fedora Silverblue (system container) and Fedora Cloud image on
  a Raspberry Pi (arm64 later).
- amd64 image now; multi-arch (amd64 + arm64) via `podman manifest` when arm64
  is needed.

## Site content & release

- Source of truth: `var/html/` in this repo (currently a placeholder
  `index.html`).
- Development: mount `./var/html` into the container as the DocumentRoot.
- Release: produce a durable zip bundle of `var/html/*`.
- Version scheme: `v<Major>.<Minor>.<YYMMDD>.<DailyBuild>`, monotonically
  incremental (e.g. `v1.0.260827.1`).
- The image consumes the versioned zip artifact at build/start for reproducible
  deployments.
