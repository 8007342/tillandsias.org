## ADDED Requirements

### Requirement: Rootless Podman deployment
The container MUST be deployed with rootless Podman, managed by a systemd
Quadlet unit, with SELinux enabled and host ports 80/443 published into the
container.

#### Scenario: Start via Quadlet
- **WHEN** the systemd Quadlet unit is started on a Podman host
- **THEN** the rootless container starts and publishes ports 80/443

#### Scenario: SELinux enabled
- **WHEN** the container runs
- **THEN** SELinux policies confine the container and its mounts

### Requirement: Supported hosts
The image and deployment MUST run on Fedora Silverblue (as a system container)
and on a Fedora Cloud image, with arm64 support added later for Raspberry Pi.

#### Scenario: Runs on Silverblue
- **WHEN** deployed to Fedora Silverblue
- **THEN** the rootless Quadlet container starts and serves the site

#### Scenario: Multi-arch for later arm64
- **WHEN** arm64 is required (e.g. Raspberry Pi)
- **THEN** an arm64 image variant is provided via a Podman manifest
