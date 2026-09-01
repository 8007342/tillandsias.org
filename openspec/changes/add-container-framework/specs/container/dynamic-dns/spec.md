## Purpose

Defines how the deployment keeps its own CloudFlare DNS records pointed at the
current public IP as that IP changes: which records are in scope, how short
their TTL is, how missing records are created, the safety modes that prevent
accidental writes, and the fallback when no public IP exists at all.

## ADDED Requirements

### Requirement: Keep DNS current as IP changes
The image MUST include a `cloudflare-ddns` updater that detects the current
public IPv4 and IPv6 addresses and keeps the zone's A (IPv4) and AAAA (IPv6)
records for `tillandsias.org` and `www.tillandsias.org` current via the
CloudFlare API.

#### Scenario: Public IP changes
- **WHEN** the container detects that a public IPv4 or IPv6 address has changed
- **THEN** it updates the corresponding A/AAAA records for the apex and www
  hostnames

#### Scenario: IP unchanged
- **WHEN** the public addresses are unchanged since the last check
- **THEN** no update is made to the DNS records

#### Scenario: No public address of a family
- **WHEN** a public IPv6 (or IPv4) address cannot be determined
- **THEN** the updater skips that record type and does not error

### Requirement: Short TTL for dynamic records
Because the site is served from dynamic addresses, the A and AAAA records MUST
be created and refreshed with a short TTL (1 hour / 3600 seconds).

#### Scenario: Records use short TTL
- **WHEN** the updater creates or updates an A/AAAA record
- **THEN** the record carries a TTL of 3600

### Requirement: Auto-create missing records
The updater MUST create an A/AAAA record when none exists for a managed host,
rather than only updating existing records.

#### Scenario: No record for host
- **WHEN** a managed host (apex or www) has no A/AAAA record
- **THEN** the updater creates the record pointing at the current address

### Requirement: Restricted DNS scope
The dynamic DNS updater MUST only manage this project's own records within the
zone, not arbitrary zone records.

#### Scenario: Restricted to own records
- **WHEN** the updater runs
- **THEN** it only reads/updates the records for tillandsias.org and
  www.tillandsias.org

### Requirement: Non-destructive safety modes
The `cloudflare-ddns` script MUST provide a `--validate` mode (verifies token
and zone resolution with no writes) and a `--dry-run` mode (prints what it would
change without calling any write API), so it can be exercised safely during
development.

#### Scenario: Validate mode
- **WHEN** the updater runs with `--validate`
- **THEN** it confirms the token is valid and the zone resolves, making no
  changes to DNS records

#### Scenario: Dry-run mode
- **WHEN** the updater runs with `--dry-run`
- **THEN** it prints the record updates it would make without writing them

### Requirement: Tunnel fallback when no public IP
When the host has no reachable public IPv4 or IPv6 address (e.g. behind
NAT/CGNAT), dynamic DNS alone cannot point the domain here. In that case the
deployment MUST fall back to a Cloudflare Tunnel so the container remains
reachable via the domain.

#### Scenario: No public IP
- **WHEN** the host has no public IPv4 or IPv6 address
- **THEN** the deployment uses a Cloudflare Tunnel (cloudflared) to expose the
  site through Cloudflare, instead of relying on dynamic DNS

#### Scenario: Tunnel credentials available
- **WHEN** a Cloudflare Tunnel token/credential is available
- **THEN** cloudflared routes the site to the tunnel from this host