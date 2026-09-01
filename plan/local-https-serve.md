# Workstream: local HTTPS serve from a sibling container

**Status:** `BLOCKED-ON-HOST` — repo side proceeding, runtime side waiting.
**Opened:** 2026-09-01
**Last updated:** 2026-09-01 by forge session `tillandsias.org-forge-claude`

---

## 1. Goal

Serve this repo's `./var/html` from a **sibling `httpd` container** — started,
stopped and statused *by a forge agent* through the Tillandsias Runtime MCP
servers — so that a browser on the bare-metal host can visit:

> **https://www.tillandsias.org.localhost**

The serve must be a **full HTTPS serve, not an HTTP approximation**: a
browser-trusted certificate, a genuine secure context, and therefore the real
JavaScript CORS and mixed-content rules. A page that only works because someone
passed `--ignore-certificate-errors` has not been tested.

The sibling serves plain HTTP on `:80`; the host's Caddy router terminates TLS
in front of it. That is deliberately the same shape Cloudflare will have when
we go public, so **the origin config does not change when the tunnel rung
lands** — `https://www.tillandsias.org` later reuses this exact container.

### Out of scope for now
Cloudflare Tunnel and the public name. Local HTTPS first. The existing
`scripts/cloudflare-ddns` + `CONTAINERFILE` dynamic-DNS path is untouched.

---

## 2. Verified facts about this environment

Each was checked from inside the forge container on 2026-09-01. Anything not
listed here has **not** been proven.

### 2.1 The forge checkout is ephemeral — this is the fact that shapes everything

`/home/forge/src/tillandsias.org` does **not** appear in `/proc/self/mountinfo`.
It lives in the container's overlay upper layer and dies with the container.

> **Consequence:** a sibling container **cannot** bind-mount this working tree.
> Content must be handed to the host through some other channel (§4.2).
> **Consequence:** nothing is durable until it is committed *and pushed*.

### 2.2 The lane MCP socket — mount is correct, socket is absent

This is the single blocker for the whole runtime path.

From `/proc/self/mountinfo`:

```
/tillandsias/mcp/tillandsias.org-default  ->  /run/host/tillandsias-mcp   (tmpfs, ro,nosuid,nodev)
```

That tmpfs (device `0:111`) also backs `/run/secrets`, whose subpath is
`/containers/overlay-containers/<ctr>/userdata/run/secrets` — which places the
host-side source directory at:

```
/run/user/1000/tillandsias/mcp/tillandsias.org-default/
```

It is mounted, readable, and **empty**. `mcp.sock` is not bound.

| Component | State | Evidence |
|---|---|---|
| `TILLANDSIAS_CONTROL_SOCKET` | ✅ set to `/run/host/tillandsias-mcp/mcp.sock` | `env` |
| Mount of the lane dir | ✅ present, `ro` | `/proc/self/mountinfo` |
| `mcp.sock` inside it | 🔴 **absent** | `ls -la /run/host/tillandsias-mcp/` → empty |
| `host-browser.sh` bridge | ✅ correct (plain `socat - UNIX-CONNECT:$SOCK`) | read the script |
| `socat` binary | ✅ `/usr/sbin/socat` | `command -v socat` |
| MCP registration | ✅ `host-browser` registered | `~/.config-overlay/claude/mcp.json`, `~/.claude.json` |
| Resulting MCP state | 🔴 `CONNECTION_CLOSED` | session startup |

> **This is strictly better than the two prior diagnoses in this repo.**
> `SiblingContainerDiagnosis.md` (2026-08-28) found the env var unset *and* the
> directory missing. `container-diagnostics.md` (2026-09-01, Codex) found the
> env var set but the directory missing. Now the directory is mounted too.
> **Only the host-side listener remains.** The mount is `ro` on the forge side,
> so the socket must be created by the host — a forge cannot bind it.

### 2.3 The router is Caddy, HTTP-only, and closed to us

`tillandsias-router` = `10.0.42.91` on the podman `dns.podman` network.

| Port | State |
|---|---|
| 8080 | ✅ OPEN — `Server: Caddy` |
| 80 | 🔴 closed |
| 443 | 🔴 closed |
| 8443 | 🔴 closed |
| 2019 (Caddy admin API) | 🔴 closed |

Every request 404s: `tillandsias-router: no route for <host>` — including
`www.tillandsias.org.localhost`, `tillandsias.org.localhost`. Nothing is
registered for this lane.

> **Two consequences.** There is **no TLS listener at all** today, so the HTTPS
> requirement needs host work regardless of the MCP socket. And with the admin
> API closed, a forge **cannot self-register a route** — route creation is
> necessarily the host's job.

### 2.4 The shared named volume — a content channel that already exists

```
host: /home/tlatoani/.local/share/containers/storage/volumes/tillandsias-forge-cache-tillandsias.org/_data
 ->  forge: /home/forge/.cache/tillandsias-project        (rw, btrfs)
```

A second one, `tillandsias-spec-index-tillandsias.org` → `/opt/tillandsias/spec-index`.

This is a genuine bidirectional bridge between forge and host that is **already
wired**, which makes it the cheapest content-handoff candidate (§4.2 option a).

### 2.5 Container identity (for host-side lookup)

| | |
|---|---|
| Container name | `tillandsias-tillandsias.org-forge-claude` |
| Hostname | `forge-tillandsias-org` |
| Container id | `d9aac43c43b6303276f72152051f60a157bf228e1388fcef3d3236a10f276a53` |
| IP | `10.0.42.94` on `dns.podman` (10.0.42.0/24) |
| Host user | `tlatoani` (rootless podman, Fedora, btrfs, SELinux `seclabel` mounts) |
| Lane directory name | `tillandsias.org-default` |
| Forge uid/gid | `1000:1000` (`forge`) |

### 2.6 Other reachable enclave services

`vault` `10.0.42.87:8200` (token at `/run/secrets/vault-token`) ·
`inference` `10.0.42.93:11434` · `proxy` `10.0.42.88:3128` ·
git mirror `git-8orb1dgc88nrr5e892rg` (push/fetch verified working).
No `podman`/`docker`/`buildah` client in the forge — by design.

---

## 3. Asks outstanding on the host

Sent to `macuahuitl-fedora` on 2026-09-01. Replies belong in
[`host-notes.md`](host-notes.md).

1. **Bind the lane MCP socket** at
   `/run/user/1000/tillandsias/mcp/tillandsias.org-default/mcp.sock`.
   Nothing else needs to change — not the mount, not the env var, not the forge
   config. This unblocks `publish_local` / `service_status` / `service_stop`.
2. **Choose the content-handoff channel** (§4.2).
3. **Add a TLS listener and a route to Caddy** — publish `127.0.0.1:80` and
   `127.0.0.1:443` from the router container, and route
   `www.tillandsias.org.localhost` → the sibling on `:80`.
4. **Answer two contract questions** so the repo matches the Runtime rather than
   inventing: does `publish_local {"category":"WEB"}` return an `https` no-port
   URL once TLS exists (or is `http://…:8080` the contracted value today), and
   is the sibling named `tillandsias-tillandsias.org-web` or does the Runtime
   mint its own name?

---

## 4. Design

### 4.1 Shape

```
   bare-metal browser
          │  https://www.tillandsias.org.localhost   (RFC 6761 → 127.0.0.1)
          ▼
   127.0.0.1:443  ──►  tillandsias-router (Caddy)      ← terminates TLS
          │                    │
          │                    │ reverse_proxy, plain HTTP
          ▼                    ▼
     (:80 → 301 https)   tillandsias-<project>-web:80  ← sibling httpd
                                │
                                ▼
                         /usr/local/apache2/htdocs   ← var/html, read-only
```

TLS terminates at the router, exactly as Cloudflare will terminate it later.
The sibling origin is identical in both cases.

### 4.2 Content handoff — options put to the host

- **(a) Reuse the existing named volume.** Forge stages the site into a
  `web-root/` subdir of `tillandsias-forge-cache-tillandsias.org`; the sibling
  mounts that subpath read-only. **Preferred** — zero new plumbing, already
  wired, works for every future forge of this project.
- **(b) Push/pull through the git mirror.** Forge commits and pushes; the host
  keeps a checkout the sibling mounts. Cleanest provenance, slowest loop.
- **(c) `publish_local` streams a bundle** over the control socket and the
  Runtime owns the volume. Best long-term; only if already implemented.

### 4.3 Notes that will bite if forgotten

- **SELinux.** The host is Fedora with `seclabel` mounts and rootless podman.
  A bind mount into the sibling needs `:z` (shared) or `:Z` (private)
  relabelling, or Apache gets `AH00132: permission denied` and the cause is not
  obvious from the error.
- **uid/gid.** The forge writes as `1000:1000`. The official `httpd:2.4` image
  runs its workers as `www-data`/`daemon`. Content must be world-readable, or
  the sibling serves 403s.
- **HSTS on a `.localhost` origin is a trap.** `Strict-Transport-Security` is
  stored by the browser **per host**, and a `max-age` set on
  `www.tillandsias.org.localhost` would pin *that* name to HTTPS on the
  developer's machine long after this container is gone. Worse, `includeSubDomains`
  on a `.localhost` name can poison sibling projects' `.localhost` hosts. Do
  **not** set HSTS on the local origin; set it only on the real public origin.
- **The sibling outlives the forge.** Tearing down the forge does not stop a
  published sibling. `service_stop` must be called, or the next `publish_local`
  collides with a running container and a stale document root.

---

## 5. Acceptance criteria

The chain is done when **all** of these pass, run from the bare-metal host:

```sh
# 1. The socket exists and speaks JSON-RPC (run from the forge)
socat - UNIX-CONNECT:"$TILLANDSIAS_CONTROL_SOCKET"

# 2. The forge can start the sibling over MCP
#    publish_local {"category":"WEB"}  -> returns a URL

# 3. The page is served over real TLS, with a trusted chain (NO -k / --insecure)
curl -sS -D- https://www.tillandsias.org.localhost/ -o /dev/null

# 4. Plain HTTP redirects to HTTPS rather than serving
curl -sS -D- http://www.tillandsias.org.localhost/ -o /dev/null   # expect 301/308 -> https://

# 5. The bytes are ours
curl -sS https://www.tillandsias.org.localhost/ | diff - var/html/index.html

# 6. Lifecycle round-trips
#    service_status {}            -> sibling reported running
#    service_stop {"category":"WEB"} -> sibling gone; the URL stops answering
```

Plus, in a **real browser** on bare metal (the part `curl` cannot prove):

- The padlock is closed with no interstitial and no click-through.
- `window.isSecureContext === true` in the console.
- A `fetch()` to a cross-origin endpoint is governed by ordinary CORS
  preflight rules — i.e. this is a genuine secure origin, not a
  `localhost`-exemption artefact.

> Criterion 3 is the one that separates a real result from a fake one. If it
> needs `-k`, the certificate is not trusted and the browser's secure-context
> and CORS behaviour will not match production — which was the entire point.

---

## 6. Session log

Append; do not rewrite.

### 2026-09-01 — `tillandsias.org-forge-claude` (Claude Code, Opus 5)
- Established §2 facts from inside the container.
- **Advanced the known state of the blocker**: the lane directory mount is now
  present (both prior diagnoses found it missing). Narrowed the remaining
  failure to a single missing host-side socket bind, and derived the exact host
  path `/run/user/1000/tillandsias/mcp/tillandsias.org-default/mcp.sock` from
  the mountinfo device shared with `/run/secrets`.
- Newly established (neither prior diagnosis had these): the router is **Caddy
  on :8080 only, with the admin API closed** — so HTTPS needs host work
  independent of the MCP socket, and a forge can never self-register a route.
- Messaged `macuahuitl-fedora` with the four asks in §3.
- Created this `plan/` directory.
