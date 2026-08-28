## ADDED Requirements

### Requirement: Credentials not baked into image
The CloudFlare API credentials MUST NOT be baked into the image or committed to
source control; they MUST be injected at runtime via a Podman secret, mounted
read-only inside the container.

#### Scenario: Provide credentials at runtime
- **WHEN** the container is deployed
- **THEN** the CloudFlare API token is supplied as a Podman secret and mounted
  read-only inside the container

#### Scenario: Image contains no credentials
- **WHEN** the image is inspected or built
- **THEN** it contains no CloudFlare API token or credential material

### Requirement: Least-privilege token
The CloudFlare API token MUST be scoped to only what is needed for the zone and
MUST be shared with certbot-dns-cloudflare and the cloudflare-ddns updater with
restrictive file permissions and SELinux labels.

#### Scenario: Token scope
- **WHEN** a CloudFlare API token is created
- **THEN** it is scoped to Zone:DNS:Edit for the tillandsias.org zone only

#### Scenario: Restrictive handling
- **WHEN** the secret is used by certbot or cloudflare-ddns
- **THEN** the token is read from a read-only restricted file/label and is not
  written to logs or image layers

### Requirement: Development credentials kept out of the repo
For local development the CloudFlare token MUST be stored outside the repo (in
`~/.config/tillandsias/cf-token` on the dev host, or a Podman secret) and the
repo MUST ignore any credential files.

#### Scenario: Dev token storage
- **WHEN** running cloudflare-ddns locally in development
- **THEN** the token is read from `~/.config/tillandsias/cf-token`, a Podman
  secret, or an environment variable, never from the repository

#### Scenario: No credentials committed
- **WHEN** the repository is scanned
- **THEN** no credential files or token material are tracked by source control

### Requirement: Dev tooling availability
The project MUST document the minimal development tooling needed to work with
CloudFlare: `cloudflared` (installed via Homebrew on Silverblue) plus `curl` and
`jq`, which are sufficient to exercise the dynamic DNS flow.

#### Scenario: Dev tools present
- **WHEN** a developer works on dynamic DNS locally
- **THEN** `cloudflared`, `curl`, and `jq` are available, and the token is
  provided outside the repo

### Requirement: Cloudflare Tunnel credentials
The `Zone:DNS:Edit` API token alone MUST NOT be assumed sufficient for Cloudflare
Tunnels. Running a tunnel requires a tunnel token (remotely-managed tunnel) or an
Origin CA certificate from `cloudflared tunnel login`, and creating/configuring a
tunnel via API additionally requires account-level `Cloudflare Tunnel: Edit`
permission.

#### Scenario: Tunnel requires its own credential
- **WHEN** a Cloudflare Tunnel is used
- **THEN** separate tunnel credentials (tunnel token or Origin CA certificate)
  are provided, distinct from the zone DNS token

#### Scenario: API-managed tunnel permissions
- **WHEN** a tunnel is created or configured via the CloudFlare API
- **THEN** the API token includes account-level `Cloudflare Tunnel: Edit`
  permission (or an equivalent Cloudflare One connectors permission)
