## 1. Site content & release

- [ ] 1.1 Initialize `var/html/` with placeholder `index.html`
- [ ] 1.2 Add release tooling producing a durable zip of `var/html/*` with the
      monotonic version scheme v<Major>.<Minor>.<YYMMDD>.<DailyBuild>
- [ ] 1.3 Wire release artifact consumption into the image build

## 2. Container image (CONTAINERFILE)

- [ ] 2.1 Author multi-stage CONTAINERFILE based on `httpd:2.4`
- [ ] 2.2 Install certbot + certbot-dns-cloudflare
- [ ] 2.3 Add `cloudflare-ddns` updater script
- [ ] 2.4 Add entrypoint scripts (cert issuance/renewal, ddns loop, httpd start)
- [ ] 2.5 Run as non-root runtime user; seal code/config layers

## 3. HTTP/HTTPS configuration

- [ ] 3.1 Apache config: `www.tillandsias.org` 301 redirect to the apex, with
      the target scheme hard-coded to https (never %{REQUEST_SCHEME}, which
      resolves to http behind a TLS terminator and downgrades the visitor)
- [ ] 3.2 Apache config: apex :443 virtual host with managed cert
- [ ] 3.3 certbot DNS-01 wildcard issuance + renewal timer + httpd reload

## 4. Secrets

- [ ] 4.1 Document CloudFlare token scope (Zone:DNS:Edit) and creation
- [ ] 4.2 Inject token at runtime via Podman secret, read-only, SELinux-labeled

## 5. Deployment

- [ ] 5.1 Rootless Podman + systemd Quadlet unit, ports 80/443, SELinux enabled
- [ ] 5.2 Validate on Fedora Silverblue; prep amd64; plan arm64 manifest
