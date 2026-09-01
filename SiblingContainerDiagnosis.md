> [!IMPORTANT]
> **SUPERSEDED — 2026-09-01. Its central conclusion is no longer true.**
>
> This document reports the sibling-container publish path as BLOCKED. **It is
> not.** The site now serves at
> `http://www.tillandsias.org.localhost:8080/var/html/index.html`.
>
> The control-socket root cause was later found (the live launcher never calls
> `start_mcp_socket_server_for_lane`) and **fixed on trunk `19057a9e3`**. The
> suggested host-side fix below — bind-mount the socket and export
> `TILLANDSIAS_CONTROL_SOCKET` — was diagnosed from the symptom and is not the
> actual fix; both were already in place while the socket was still absent.
>
> **For current state, read [`plan/local-https-serve.md`](plan/local-https-serve.md).**
> This file is kept for provenance only.

# Sibling Container Launch — Smoke Test Diagnosis

**Project**: tillandsias.org (static Apache-hosted site)
**Date**: 2026-08-28
**Tester role**: first forge-session user (`TILLANDSIAS_HOST_KIND=forge`, lane `forge-tillandsias-org`,
agent `opencode/big-pickle`)
**Test intent**: launch this project as a **sibling httpd container** on the enclave host, per the
`host-browser` MCP publish flow — and, since the infra may not be fully wired, push as far as possible
and record every shortcoming for the stack owner.

## Bottom line

> **The sibling-container publish path is BLOCKED, and the blocker is infrastructural, not in this repo.**
> The only sanctioned bridge to the host container runtime (the `host-browser` MCP server, backed by the
> host control socket) failed to connect in this session. Everything that could be verified without it is
> healthy. Fix: the host must bind-mount this lane's MCP control socket into the forge container and export
> `TILLANDSIAS_CONTROL_SOCKET` (details under "For the stack owner" below).

Status per component:

| Component | Expected | Observed | Verdict |
|---|---|---|---|
| `host-browser` MCP server (`publish_local` / `service_status` / `service_stop`) | Sibling-container control plane | **Not connected; zero tools available** | 🔴 BLOCKED |
| Host control socket (`/run/host/tillandsias-mcp/mcp.sock`) | Bind-mounted into forge | **Does not exist** | 🔴 MISSING |
| `TILLANDSIAS_CONTROL_SOCKET` env var | Set by host at launch | **Unset** | 🔴 MISSING |
| podman CLI in forge | Absent by design (no direct podman) | Absent | ✅ as-designed |
| Site content (`var/html/index.html`) | Servable | Serves 200 over enclave network | ✅ OK |
| CONTAINERFILE / entrypoint / vhost config | Buildable on host | Present in repo; not buildable here (no podman) | ✅ repo-side OK |
| Git mirror | Accessible | `git-emn6m230crot42l60mpg:9418` OPEN | ✅ OK |
| Inference (Ollama) | Up | Up (per startup context, 2 models) | ✅ OK |
| Enclave proxy (`proxy:3128`) | Up | Reachable; CONNECT to external host reset | ⚠️ see findings |
| Cheatsheets + `tellme` | Index at `/opt/cheatsheets/INDEX.md` | `/opt/cheatsheets` empty; `tellme` errors | 🔴 BROKEN |
| Dev-server fallback | Framework URL via router | Router exposes **no** services for this forge | 🔴 no route |

## What was attempted

1. **Inspect the sanctioned publish path** (`.forge-startup-context.md`, `web-services.md`, OpenCode
   `config.json`). The flow is: `host-browser` MCP → `publish_local {"category":"WEB"}` → host launches a
   sibling `tillandsias-tillandsias.org-web` container → returns
   `http://www.tillandsias.org.localhost:8080`. `service_status` / `service_stop` manage it.
2. **Inventory the MCP servers actually connected.** Tools present this session are from `forge-plan`,
   `git-tools`, `project-info` only. **`host-browser` delivered no tools** despite being `enabled: true` in
   `/home/forge/.config/opencode/config.json`.
3. **Run the bridge directly** to capture its failure message:
   ```json
   {"jsonrpc":"2.0","error":{"code":-32000,"message":"TILLANDSIAS_CONTROL_SOCKET not set"}}
   ```
   (`host-browser.sh` exits before touching the socket when the env var is absent; it also hard-fails if
   `$TILLANDSIAS_CONTROL_SOCKET` does not exist.)
4. **Confirmed the environment**:
   - `TILLANDSIAS_CONTROL_SOCKET` — **not set** (checked `env`, entrypoint scripts, `/usr/local/sbin/entrypoint-forge-opencode.sh`, `lib-common.sh`).
   - `/run/host/tillandsias-mcp/` — **does not exist**.
   - No `*.sock` files anywhere on the root filesystem except the OpenCode client's own `/tmp/cc-socks/492.sock`.
   - No `vsock` device; no podman/docker/nerdctl/buildah binaries.
5. **Confirmed the host never intended these absent** — the forge-entrypoint chain never sets the variable
   or mounts the socket; it must be injected by the host's container-launch code, and this launch did not do it.
6. **Probed the routed `*.localhost` URLs** (would be the user-facing surface of any published service):
   all failed to connect — `www.tillandsias.org.localhost:8080`, `opencode.tillandsias.org.localhost:8080`,
   `tillandsias.org.python-http.localhost`, `tillandsias.org.web.localhost`. No service route exists for this
   forge, consistent with "nothing was ever published".
7. **Bare-metal proof that the failure is infra-only**: served `var/html` from inside the forge bound to
   `0.0.0.0:8000`, then curled the forge's own enclave IP → HTTP 200 with the real page; `Host: www.tillandsias.org`
   also 200. The static content, vhost notion, and Node file-service all behave. Then tore the server down.
   (Note: an in-forge server is a **dev-server fallback** only — the sanctioned "host/publish" flow is
   `publish_local`, and a raw forge-bound port is not registered on the host router.)

## Root cause (for the stack owner)

This lane's forge container was launched **without the host-browser control-socket mount and without the
environment injection that pairs with it**:

| Thing | Expected | Found |
|---|---|---|
| Socket path | `/run/host/tillandsias-mcp/mcp.sock` (per `host-browser.sh` provenance, "this lane's own socket", order 505) | absent directory |
| Env var | `TILLANDSIAS_CONTROL_SOCKET` pointing at that socket | unset |

Since `host-browser.sh` is a pure socat bridge to that socket, **MCP initialization fails at `initialize`
time**, OpenCode silently drops the server's tools, and every sibling-container capability
(`publish_local`, `service_status`, `service_stop`, plus the `host-browser-mcp` CDP/browser methods)
is invisible — which is exactly what a first user experiences as "can't launch a sibling container".

### Suggested fix (host side)

- Bind-mount the lane's control socket into the forge container at **`/run/host/tillandsias-mcp/mcp.sock`**
  (e.g. podman `--mount type=bind,source=<host-path>/mcp.sock,target=/run/host/tillandsias-mcp/mcp.sock`),
  and export **`TILLANDSIAS_CONTROL_SOCKET=/run/host/tillandsias-mcp/mcp.sock`** in the container env.
- Verify with the doc'd readiness probe: `TILLANDSIAS_CONTROL_SOCKET=/run/host/tillandsias-mcp/mcp.sock socat - UNIX-CONNECT:"$SOCK"`.
- After relaunch, the smoke-test acceptance criteria are:
  - `publish_local {"category":"WEB"}` returns a `URL` (expected `http://www.tillandsias.org.localhost:8080`);
  - `curl http://www.tillandsias.org.localhost:8080/` returns the placeholder page;
  - `Host: www.tillandsias.org` returns **HTTP 301 → `http://tillandsias.org/…`** (the vhost redirect in
    `container/tillandsias-vhost.conf`);
  - `service_status {}` reports the SIBLING container running;
  - `service_stop {"category":"WEB"}` stops it cleanly.

## Secondary findings

### 1. `tellme` is broken — cheatsheet hot path not populated
`tellme about web` → `Error: Cheatsheet index not found at /opt/cheatsheets/INDEX.md`.
`/opt/cheatsheets` exists but is **empty**; the real bundle lives at `/opt/cheatsheets-image/` (bundled
lower layer). The entrypoint calls `populate_hot_paths` to copy image cheatsheets into the `/opt/cheatsheets`
tmpfs hot mount, but the mount came up empty this session (writable, zero files). Worth checking whether the
tmpfs mount is created before/after `populate_hot_paths`, and whether `populate_hot_paths` actually copied.

### 2. Outbound proxy CONNECT is being reset
`curl -x http://proxy:3128 https://example.com` → `Connection reset by peer`. The proxy answers but refuses
external CONNECTs this session. Enclave-internal services (git mirror, inference, CA) are unaffected. If
outbound browsing is expected in this lane, the proxy allowlist/CONNECT policy is the suspect.

### 3. `/run/secrets` is empty
The CONTAINERFILE/entrypoint expect a podman secret mounted at `/run/secrets/cf-token` for the Cloudflare
dynamic-DNS. In this lane `/run/secrets` exists but has no `cf-token`. For a *local* (non-public) publish
this is cosmetic (entrypoint already logs a warning and serves anyway), but the DNS-update half of the
sibling container cannot be exercised end-to-end until a secret is mounted.

### 4. Mount catalog — what *is* wired (for reference)
From `/proc/1/mountinfo`: host is a podman-on-btrfs Fedora host (host user `lenovinha`). Mounted into this
forge:
- host `…/containers/storage/volumes/tillandsias-forge-cache-tillandsias.org/_data` → `~/.cache/tillandsias-project`
- host `~/.cache/tillandsias/forge-gitconfig/tillandsias.org.config` → `~/.gitconfig`
- CA chain → `/run/tillandsias/ca-chain.crt` and `/tillandsias-ca/intermediate.crt`
- `/run/secrets`, `/run/user/1000` (stdout empty)
Notably **absent from the catalog**: any `mcp.sock` / control-socket bind mount.

## What already works (verified)

- Git mirror reachable; GitHub routing via the mirror (no credential config needed).
- Inference endpoint present per startup context (not exercised in this smoke test).
- Site content correct and servable; repo tooling (`scripts/dev-run.sh`, `scripts/cloudflare-ddns`,
  `CONTAINERFILE`, `container/tillandsias-vhost.conf`) present and internally consistent (spec:
  `openspec/changes/add-container-framework`).

## Suggested re-test checklist once the owner fixes the wiring

```bash
# from the forge, after relaunch:
TILLANDSIAS_CONTROL_SOCKET="${TILLANDSIAS_CONTROL_SOCKET:?}" \
  socat - UNIX-CONNECT:"$TILLANDSIAS_CONTROL_SOCKET"
# then, over MCP:
#   publish_local {"category":"WEB"}            -> URL http://www.tillandsias.org.localhost:8080
#   HTTP GET http://www.tillandsias.org.localhost:8080/                     -> 200 placeholder
#   HTTP GET http://www.tillandsias.org.localhost:8080/ with Host: www....   -> 301 to apex
#   service_status {}                          -> sibling running
#   service_stop {"category":"WEB"}            -> sibling gone
```