## ADDED Requirements

### Requirement: Keep DNS current as IP changes
The image MUST include a `cloudflare-ddns` updater that detects the host's
current public IP and, when it changes, updates the zone's A/AAAA records for
`tillandsias.org`, `www.tillandsias.org`, and `*.tillandsias.org` via the
CloudFlare API.

#### Scenario: Public IP changes
- **WHEN** the container detects that the public IP has changed
- **THEN** it updates the zone's A/AAAA records for the apex, www, and wildcard
  hostnames

#### Scenario: IP unchanged
- **WHEN** the public IP is unchanged since the last check
- **THEN** no update is made to the DNS records

### Requirement: Restricted DNS scope
The dynamic DNS updater MUST only manage this project's own records within the
zone, not arbitrary zone records.

#### Scenario: Restricted to own records
- **WHEN** the updater runs
- **THEN** it only reads/updates the records for tillandsias.org,
  www.tillandsias.org, and *.tillandsias.org

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
