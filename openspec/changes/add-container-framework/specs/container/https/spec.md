## Purpose

Defines how the site is served over HTTPS: which host is canonical and how the
alias redirects to it, how the certificate covering those names is issued and
renewed without inbound port 80, and what the server treats as its document
root.

## ADDED Requirements

### Requirement: Canonical host and alias redirect
The site MUST be served at the canonical apex host `tillandsias.org` (the
shortest URL for users), and `www.tillandsias.org` MUST return an HTTP 301
redirect to `tillandsias.org`, preserving the scheme.

#### Scenario: Request to apex
- **WHEN** a client requests `tillandsias.org`
- **THEN** it receives the static site over HTTPS at the apex

#### Scenario: Request to www over HTTPS
- **WHEN** a client requests `https://www.tillandsias.org`
- **THEN** it receives a 301 redirect to `https://tillandsias.org`

### Requirement: Automatic wildcard certificate
The image MUST issue and automatically renew a Let's Encrypt certificate
covering `tillandsias.org` (apex) and `www.tillandsias.org` (via the wildcard)
using the DNS-01 challenge through certbot's CloudFlare plugin, without requiring
inbound port 80 for issuance.

#### Scenario: Initial certificate issuance
- **WHEN** the container starts without a valid certificate
- **THEN** certbot issues a wildcard certificate covering the apex and
  `*.tillandsias.org` using the CloudFlare DNS-01 challenge

#### Scenario: Automatic renewal
- **WHEN** the certificate approaches expiration
- **THEN** certbot renews it and Apache httpd reloads the updated certificate

### Requirement: Serve site content
The httpd server MUST serve the versioned site bundle (see site/release) as the
document root.

#### Scenario: Serving the site
- **WHEN** a client requests the site root
- **THEN** httpd serves the files from the installed site bundle