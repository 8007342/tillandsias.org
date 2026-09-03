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
`/run/secrets/cf-token`. It keeps **A** (IPv4) and **AAAA** (IPv6) records for
`tillandsias.org` and `www.tillandsias.org` pointing at the current public
addresses, **creating** records that don't exist and refreshing them with a short
TTL (1 hour) since we serve from dynamic IPs.

To build and run the site container locally:

```sh
./scripts/dev-run.sh --mode=skip    # serve + verify, no DNS writes
./scripts/dev-run.sh --mode=dry-run # run, show DNS changes, don't write
./scripts/dev-run.sh --mode=live    # run and update DNS to your public IP
```

## Cloudflare Tunnel fallback

When there's no reachable public IPv4/IPv6 (e.g. a mobile/shared connection
behind NAT/CGNAT), dynamic DNS alone can't point the domain here. In that case
we fall back to a Cloudflare Tunnel. A tunnel needs its own credential (a
remotely-managed tunnel token or an Origin CA certificate from
`cloudflared tunnel login`) — the `Zone:DNS:Edit` token alone is not sufficient.
The `dev-run.sh` public-IP check reports when a tunnel would be required.

## References

- Architecture: `openspec/changes/add-container-framework/design.md`
- Secrets spec: `openspec/changes/add-container-framework/specs/container/secrets/spec.md`
- Dynamic DNS spec: `openspec/changes/add-container-framework/specs/container/dynamic-dns/spec.md`

## Deploying the site (Workers Builds)

The site is static: one generated `var/html/index.html`, no framework, no
bundler, nothing to compile. Cloudflare's Workers & Pages flow still wants two
commands when you connect the repo — here is what they should be, and why.

| Field | Value |
|---|---|
| Build command | *(leave empty)* |
| Deploy command | `npx wrangler deploy` |

**Build command is empty on purpose.** `var/html/index.html` is committed, so
there is nothing for the build step to produce. Regenerating it on Cloudflare
would mean depending on a Python toolchain in their build image to rebuild a
file we already have, and a failure there would block a deploy for no gain. If
you ever *do* want it regenerated remotely, the command is
`python3 scripts/build-matrix.py` — but keep the generated file committed either
way, so the deployable artifact never depends on the build succeeding.

**The default deploy command already works** — `wrangler.jsonc` in the repo root
is what makes it work. It declares a Worker with `assets.directory` pointing at
`./var/html` and no `main`, which is the supported shape for "serve these files
and run no code". Only that directory is uploaded, so `docs/`, `plan/`,
`scripts/` and the rest of the repo never reach the edge.

`package.json` pins Wrangler rather than letting `npx` pull whatever is latest
at build time; Workers Builds runs `npm install` automatically when it sees it.

### Custom domains

Serving is on `*.workers.dev` until you attach the domain. In the Worker's
**Settings → Domains & Routes**, add `tillandsias.org`. Cloudflare creates the
DNS record itself, so no manual A/AAAA entry is needed for this path.

For `www` → apex, do **not** add `www.tillandsias.org` as a second custom domain
(that serves the site at both names, which splits canonical URLs). Add a
**Redirect Rule** instead: match hostname `www.tillandsias.org`, redirect to
`https://tillandsias.org${uri.path}`, status 301, preserve query string.

### Relationship to the dynamic-DNS path above

These are two different ways to serve the same domain and they conflict. The
`scripts/cloudflare-ddns` flow points `tillandsias.org` at a machine you are
running; a Workers custom domain points it at Cloudflare's edge. Pick one per
hostname. If you move to Workers, the DDNS updater should stop managing the
records it would otherwise fight over.
