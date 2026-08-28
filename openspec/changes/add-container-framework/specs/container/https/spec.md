## ADDED Requirements

### Requirement: Canonical host and apex redirect
The site MUST be served on HTTPS at the canonical host `www.tillandsias.org`,
and the apex `tillandsias.org` MUST return an HTTP 301 redirect to
`www.tillandsias.org`.

#### Scenario: Request to apex over HTTP
- **WHEN** a client requests `http://tillandsias.org`
- **THEN** it receives a 301 redirect to `https://www.tillandsias.org`

#### Scenario: Request to www over HTTPS
- **WHEN** a client requests `https://www.tillandsias.org`
- **THEN** it receives the static site over HTTPS

### Requirement: Automatic wildcard certificate
The image MUST issue and automatically renew a Let's Encrypt certificate
covering `*.tillandsias.org` and `tillandsias.org` using the DNS-01 challenge
via certbot's CloudFlare plugin, without requiring inbound port 80 for issuance.

#### Scenario: Initial certificate issuance
- **WHEN** the container starts without a valid certificate
- **THEN** certbot issues a wildcard certificate using the CloudFlare DNS-01
  challenge

#### Scenario: Automatic renewal
- **WHEN** the certificate approaches expiration
- **THEN** certbot renews it and Apache httpd reloads the updated certificate

### Requirement: Serve site content
The httpd server MUST serve the versioned site bundle (see site/release) as the
document root.

#### Scenario: Serving the site
- **WHEN** a client requests the site root
- **THEN** httpd serves the files from the installed site bundle
