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
