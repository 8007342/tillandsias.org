# CloudFlare development guide

This project keeps CloudFlare credentials **out of the repository and out of the
container image**. They are injected at runtime (Podman secret in production) and
stored outside the repo for local development.

## Development tools

Minimal set needed to exercise the dynamic-DNS flow locally:

- `cloudflared` — CloudFlare CLI. Install on Fedora Silverblue via Homebrew:
  `brew install cloudflared`
- `curl` and `jq` — used by `scripts/cloudflare-ddns`; normally already present.

## CloudFlare API token (create once)

1. CloudFlare dashboard → My Profile → API Tokens → Create Token.
2. Use the **Edit zone DNS** template, restricted to the `tillandsias.org` zone.
3. Resulting token scope: `Zone:DNS:Edit` for `tillandsias.org` only.

Store the token for development **outside the repo**:

```sh
install -m 0600 /dev/null ~/.config/tillandsias/cf-token
# paste the token, then:
chmod 600 ~/.config/tillandsias/cf-token
```

Or use a Podman secret (`podman secret create cf-token <file>`).

Never commit a token. The repo `.gitignore` ignores credential files (`.cf-token`,
`.env`, etc.).

## Running the updater safely

`scripts/cloudflare-ddns` never writes without being told to.

```sh
# Verify token + zone resolve (no writes)
./scripts/cloudflare-ddns --validate --token-file ~/.config/tillandsias/cf-token

# Show what it would change (no writes)
./scripts/cloudflare-ddns --dry-run --token-file ~/.config/tillandsias/cf-token

# Live update (only when ready)
./scripts/cloudflare-ddns --token-file ~/.config/tillandsias/cf-token
```

The script reads the token from `--token-file`, `--token`,
`$CLOUDFLARE_API_TOKEN`/`$CF_API_TOKEN`, or the podman secret mount
`/run/secrets/cf-token`. It updates A/AAAA records for `tillandsias.org`,
`www.tillandsias.org`, and `*.tillandsias.org` only when the public IP changes.

## References

- Architecture: `openspec/changes/add-container-framework/design.md`
- Secrets spec: `openspec/changes/add-container-framework/specs/container/secrets/spec.md`
- Dynamic DNS spec: `openspec/changes/add-container-framework/specs/container/dynamic-dns/spec.md`
