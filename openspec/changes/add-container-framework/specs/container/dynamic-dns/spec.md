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
