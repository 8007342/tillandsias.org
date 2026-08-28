## ADDED Requirements

### Requirement: Immutable Podman image
The project MUST provide an immutable container image built from the official
`httpd:2.4` base, produced by a multi-stage CONTAINERFILE, that serves the
www.tillandsias.org static site. The image is sealed: code and configuration
are baked in and immutable; only ephemeral runtime state (certificates, Let's
Encrypt account, extracted site bundle) is writable.

#### Scenario: Build the image
- **WHEN** the CONTAINERFILE is built with Podman
- **THEN** it produces a sealed image based on `httpd:2.4` containing httpd
  config, certbot, the cloudflare-ddns tool, and the site bundle loader

#### Scenario: Image is amd64 for now
- **WHEN** the image is built
- **THEN** it targets linux/amd64, and is structured to add linux/arm64 later
  via a Podman manifest

### Requirement: Non-root runtime
The image MUST run the web server as a non-root user with least privilege.

#### Scenario: Container starts as non-root
- **WHEN** the container is started
- **THEN** the httpd process runs as a non-root runtime user
