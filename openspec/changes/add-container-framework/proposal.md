## Why

tillandsias.org hosts a mostly-static HTML website (www.tillandsias.org as the
canonical host; the apex `tillandsias.org` redirects to it) on infrastructure
that may live anywhere in the world, on a host whose public IP can change. The
site must be served over HTTPS with automatic certificate issuance and renewal,
and the DNS must stay pointed at the current public IP even when it changes.

We need a reproducible, immutable CONTAINERFILE image (Podman, rootless) that:

- Runs Apache httpd serving the static site over HTTPS.
- Owns the CloudFlare DNS for its own records (updating A/AAAA as the public IP
  changes, and driving Let's Encrypt via DNS-01).
- Keeps CloudFlare API credentials out of the image (runtime secret).
- Fetches site content from a versioned, durable release bundle (zip) rather
  than ad-hoc files, so deployments are reproducible and versioned.

This change captures the full container framework architecture and its
requirements as OpenSpec specs.

## What Changes

- A multi-stage `CONTAINERFILE` producing an immutable, sealed image built on
  the official `httpd:2.4` image.
- Image includes: Apache httpd config (HTTP→HTTPS for the apex, HTTPS virtual
  host for `www.tillandsias.org`), certbot with the CloudFlare DNS-01 plugin for
  wildcard `*.tillandsias.org` + apex certificates, a `cloudflare-ddns` dynamic
  DNS updater, and tooling to install a versioned zip site bundle.
- Site content is released as a durable zip artifact (`var/html/*` bundled with
  version `v<Major>.<Minor>.<YYMMDD>.<DailyBuild>`); development mounts
  `./var/html` directly.
- CloudFlare API credentials are injected as a Podman secret at runtime (not
  baked into the image).
- Rootless Podman deployment on Fedora Silverblue and Fedora Cloud (RPi5 later),
  with SELinux enabled. amd64 for now; arm64 later.
- Corresponding documentation/config in-repo alongside the new specs.

## Capabilities

### New Capabilities

- `container/image`: The immutable Podman CONTAINERFILE image definition.
- `container/https`: Apache httpd serving the site over HTTPS with certbot +
  Let's Encrypt wildcard (DNS-01) issuance and renewal.
- `container/dynamic-dns`: cloudflare-ddns updater keeping A/AAAA records
  current as the public IP changes.
- `container/secrets`: Runtime injection of CloudFlare API credentials via
  Podman secret; credentials never baked into the image.
- `container/deploy`: Rootless Podman + systemd Quadlet deployment with SELinux,
  targeting Fedora Silverblue and Fedora Cloud.
- `site/release`: Versioned durable release artifact (zip) consumed by the
  image; version scheme v<Major>.<Minor>.<YYMMDD>.<DailyBuild>; development
  mount of `./var/html`.

### Modified Capabilities

None (new project, no pre-existing specs).

## Impact

- New `CONTAINERFILE` and related config files in the repo.
- New `var/html/` static site content (currently a placeholder `index.html`).
- New release/versioning tooling producing a durable zip artifact.
- Requires a CloudFlare API token scoped to `Zone:DNS:Edit` for the zone.
- Deployment requires a Podman host (rootless) with SELinux; ports 80/443.
