# Workstream: local serve from a sibling container

**Status:** 🟢 **HTTP rung LIVE** (via host proxy) · 🟡 **HTTPS rung HELD** pending adjudication · 🟡 **MCP socket** fixed on trunk, undelivered to this lane
**Opened:** 2026-09-01
**Last updated:** 2026-09-01 by forge session `tillandsias.org-forge-claude`

> **Cold-start? Read this box.**
> The site **is serving right now** at
> `http://www.tillandsias.org.localhost:8080/var/html/index.html` from a sibling
> container the host runs. You do **not** need to rebuild that. The three open
> threads are: (1) the lane MCP socket, so a forge can drive `publish_local`
> itself instead of asking the host — fixed on trunk, needs a relaunch (§3);
> (2) HTTPS — **do not build this repo-side**, it is under adjudication (§5);
> (3) the docroot convention, so `/` works and `/.git/` does not (§6.1).

---

## 1. Goal

Serve this repo's `./var/html` from a **sibling container** — started, stopped
and statused *by a forge agent* through the Tillandsias Runtime MCP servers —
reachable from a browser on the bare-metal host. The end state is:

> **https://www.tillandsias.org.localhost**

with a **browser-trusted certificate and a genuine secure context**, so the real
JavaScript CORS and mixed-content rules apply. A page that only works behind
`--ignore-certificate-errors` has not been tested.

The sibling serves plain HTTP; the host's Caddy router terminates TLS in front
of it. That is deliberately the same shape Cloudflare will have when we go
public, so **the origin config does not change when the tunnel rung lands**.

### Rungs
| Rung | State |
|---|---|
| HTTP sibling serve via host `publish_local` | ✅ **live** (host-proxied, §2) |
| Forge drives `publish_local` itself over MCP | 🟡 fixed on trunk, needs relaunch (§3) |
| Docroot convention (`/` works, `/.git/` doesn't) | 🟡 filed host-side (§6.1) |
| Local HTTPS | 🟡 **held — do not build repo-side** (§5) |
| Public `https://www.tillandsias.org` via Cloudflare Tunnel | ⚪ later |

---

## 2. What is live today

The host agent (`macuahuitl-fedora`) replicated the sanctioned publish path
host-side rather than making this forge wait on the MCP socket:

- Sibling container **`tillandsias-tillandsias.org-web`**, curated busybox httpd
  image, on the enclave network, hostname `web-tillandsias.org`.
- Route registered in Caddy and reloaded.

**Live URL:** `http://www.tillandsias.org.localhost:8080/var/html/index.html`

Independently verified from inside the forge on 2026-09-01 — `200`,
`Via: 1.1 Caddy`, `Content-Length: 306`, body byte-identical to
`var/html/index.html`.

> ### ⚠️ Verifying from inside a forge — the trap that fooled an earlier pass
> From inside a forge container, `www.tillandsias.org.localhost` **does not
> resolve to the router** — `.localhost` is this container's own loopback. You
> must send the Host header to the router directly:
>
> ```sh
> curl -H 'Host: www.tillandsias.org.localhost' \
>      http://10.0.42.91:8080/var/html/index.html
> ```
>
> `container-diagnostics.md` (2026-09-01, Codex) read an in-forge `200` from its
> own local Apache as evidence of a host route. It was not. **An in-forge 200
> proves nothing about host reachability.**

### 2.1 The content loop — how an edit reaches the browser

`publish_local` **bind-mounts the host worktree `~/src/tillandsias.org`
read-only**. It never sees this forge's checkout, which lives in container
overlay (§4.1). So:

```
forge: edit -> commit -> push to enclave mirror
                              │
host:  ~/src/tillandsias.org  ├─ pull        (host agent/operator; not yet automated)
                              ▼
       ro bind-mount into tillandsias-<project>-web  ->  reflects instantly
```

**Propagation canary.** `/plan/local-https-serve.md` through the mount returns
`404` before the host has pulled and `200` after. One request answers "is the
loop closed?" with no guessing:

```sh
curl -o /dev/null -w '%{http_code}\n' -H 'Host: www.tillandsias.org.localhost' \
     http://10.0.42.91:8080/plan/local-https-serve.md
```

---

## 3. The MCP socket — root-caused and fixed on trunk

**A forge cannot yet drive `publish_local` itself.** Until the fix lands, the
host agent *is* `publish_local` by proxy — message it for start/stop/status.

### Root cause (found from this forge's mountinfo forensics)

The live launcher `build_forge_agent_run_args_with_vault` creates the lane
directory, mounts it, and sets `TILLANDSIAS_CONTROL_SOCKET` — but **never calls
`start_mcp_socket_server_for_lane`**. The legacy tray path does call it, but the
tray-boot enumeration only covers projects that exist at startup, and
`tillandsias.org` was created after the last tray boot. A dual-source-of-truth
bug; the host reports two other partial fixes of the same class this week.

**Fix is on trunk: `19057a9e3`.**

### Delivery costs a relaunch — an open decision

Delivering the fix to this lane requires a tray relaunch, and forge containers
are killed in the stack's shutdown sweep. So either:

- **(a) Accept a relaunch now** — state is committed and pushed, so this is
  cheap; or
- **(b) Do nothing** — the socket simply arrives on the next fresh launch, and
  the host proxies `publish_local` meanwhile.

There is little pressure toward (a) while the host is proxying. **This is the
operator's call, not an agent's.**

### Evidence trail (what a forge sees when the socket is missing)

| Component | State | Evidence |
|---|---|---|
| `TILLANDSIAS_CONTROL_SOCKET` | ✅ set → `/run/host/tillandsias-mcp/mcp.sock` | `env` |
| Lane dir mount | ✅ present, `ro` | `/proc/self/mountinfo` |
| `mcp.sock` inside it | 🔴 absent | `ls /run/host/tillandsias-mcp/` → empty |
| `host-browser.sh` bridge | ✅ correct (`socat - UNIX-CONNECT`) | read the script |
| `socat` | ✅ `/usr/sbin/socat` | `command -v socat` |
| MCP registration | ✅ registered | `~/.config-overlay/claude/mcp.json` |
| Resulting MCP state | 🔴 `CONNECTION_CLOSED` | session startup |

Host-side source dir, derived from the tmpfs device shared with `/run/secrets`:
`/run/user/1000/tillandsias/mcp/tillandsias.org-default/`. The mount is `ro` on
the forge side, so **only the host can bind the socket** — a forge never can.

> This supersedes `SiblingContainerDiagnosis.md` (2026-08-28, env var *and* dir
> missing) and `container-diagnostics.md` (2026-09-01, env var set, dir
> missing). Both are kept for provenance; neither reflects current state.

---

## 4. Environment facts

Verified from inside the forge, 2026-09-01. Anything not listed is **not** proven.

### 4.1 The forge checkout is ephemeral — the fact that shapes everything

`/home/forge/src/tillandsias.org` does **not** appear in
`/proc/self/mountinfo`. It is container overlay and dies with the container.

> **Nothing is durable until committed *and pushed*.** And a sibling container
> can never bind-mount this working tree — hence the git loop in §2.1.

### 4.2 The router

`tillandsias-router` = `10.0.42.91`, **Caddy**. Port **8080 open**; **80, 443,
8443 closed**; **admin API 2019 closed**. With the admin API closed a forge
**cannot self-register a route** — that is necessarily host work. There is
currently **no TLS listener at all**.

### 4.3 Identity (for host-side lookup)

| | |
|---|---|
| Forge container | `tillandsias-tillandsias.org-forge-claude` / `forge-tillandsias-org` |
| Container id | `d9aac43c43b6303276f72152051f60a157bf228e1388fcef3d3236a10f276a53` |
| Forge IP | `10.0.42.94` on `dns.podman` (10.0.42.0/24) |
| Sibling | `tillandsias-<project>-web`, hostname `web-tillandsias.org` |
| Host user | `tlatoani` — rootless podman, Fedora, btrfs, SELinux `seclabel` |
| Lane dir name | `tillandsias.org-default` |
| Forge uid/gid | `1000:1000` (`forge`) |

### 4.4 Other enclave services

`vault` `10.0.42.87:8200` (token `/run/secrets/vault-token`) ·
`inference` `10.0.42.93:11434` · `proxy` `10.0.42.88:3128` ·
git mirror `git-8orb1dgc88nrr5e892rg` (push/fetch verified; relays to
`github.com/8007342/tillandsias.org`). No podman/docker client in the forge —
by design.

---

## 5. HTTPS — HELD, do not build repo-side

**Do not add TLS configuration to this repo.** An operator directive of
**2026-07-24** already commissioned local HTTPS on an **enclave-CA** basis, with
a proposed `images/apache`. This forge's alternative proposal — *Caddy
terminates TLS at the router, origin stays plain HTTP, i.e. the Cloudflare
shape* — has been filed as **adjudication input against that design**, together
with these requirements:

- a real green padlock, no click-through, no `-k`;
- secure-context fidelity, so `window.isSecureContext === true` and ordinary
  CORS preflight rules govern `fetch()`;
- loopback `:443` publish from the router container;
- a defined cert-trust route into the bare-metal browser/NSS store.

A relaunched session must **not** helpfully "finish" this — it would cut across
a pending decision. Await the adjudication.

### Design notes retained as adjudication input

- **`.localhost` resolution.** RFC 6761 reserves `.localhost`; systemd-resolved
  and major browsers map it to loopback, so publishing `127.0.0.1:443` suffices
  for bare-metal browsers. Multi-label `.localhost` names have historically been
  weaker in Firefox than Chrome — worth explicit verification, not assumption.
- **HSTS on a `.localhost` origin is a trap.** `Strict-Transport-Security` is
  stored **per host** and would pin `www.tillandsias.org.localhost` to HTTPS on
  the developer's machine long after the container is gone;
  `includeSubDomains` can poison *other* projects' `.localhost` hosts. Set HSTS
  only on the real public origin, never the local one.
- **SELinux.** Fedora + rootless podman + `seclabel` mounts: bind mounts into a
  sibling need `:z`/`:Z` relabelling or the server 403s with a cause that is not
  obvious from the error.
- **uid/gid.** The forge writes as `1000:1000`; container images commonly run
  workers as `www-data`/`daemon`. Content must be world-readable.

---

## 6. Open findings

### 6.1 The document root is the repo root — `/.git/` is served 🔴

Through the mount, `/.git/config` returns **200**. So do `/README.md`,
`/CONTAINERFILE`, `/plan/`. The curated busybox image serves the **project
root** at `/var/www`, which is why `/` 404s — but the same cause exposes the
whole repository, including `.git/` (full history reconstruction; `config`
carries remote URLs).

Local-only today → **low severity, high blast radius later**: this is the same
container shape the Cloudflare tunnel rung makes publicly reachable, and a
served `.git/` on a public origin is a standard, actively-scanned finding.

The host has filed the **docroot-convention rung** (serve `var/html/` when
present), which fixes both symptoms without this repo changing shape. Reported
to the host with a suggestion that a Caddy-layer dotfile deny would cap the
exposure cheaply if the rung queues.

> **Deliberately not done:** a root `index.html` redirect stub. It would be
> exactly the repo-shape change the rung exists to avoid, and cruft afterwards.

### 6.2 Only `www.` is routed; the apex `.localhost` is not

```
Host: www.tillandsias.org.localhost  -> 200
Host: tillandsias.org.localhost      -> 404  (Caddy: "no route for ...")
```

That 404 is **Caddy's**, so the apex host genuinely has no route. The production
vhost 301s `www.tillandsias.org` → apex, so once HTTPS lands, anything
exercising that redirect locally lands on an unrouted host. Reported.

### 6.3 The production CONTAINERFILE cannot ride `publish_local` — by design

`publish_local` uses a **curated catalog with a frozen busybox image**. This
repo's `CONTAINERFILE` (Apache, vhosts, cf-token secret) is the **public rung's**
container. Local preview rides the catalog; the two are separate paths and are
not expected to converge.

---

## 7. Runtime contract (answers from the host, 2026-09-01)

| Question | Answer |
|---|---|
| `publish_local` return shape | `http://www.<project>.localhost:<router_host_port>` — **HTTP, port-ful** today. The `https` no-port shape arrives with the TLS work. Match the current contract. |
| Sibling container name | The **Runtime mints** it: `tillandsias-<project>-web`. |
| Content channel | **Bind-mounts the host worktree** `~/src/tillandsias.org` read-only. Not the forge checkout, not a named volume. |
| Streaming a bundle over the socket | **Unimplemented.** |
| Lifecycle tools | `publish_local {"category":"WEB"}` · `service_status {}` · `service_stop {"category":"WEB"}` |

---

## 8. Acceptance criteria

### HTTP rung — ✅ met (2026-09-01)

```sh
# from inside the forge (Host header to the router; see the §2 trap)
curl -i -H 'Host: www.tillandsias.org.localhost' \
     http://10.0.42.91:8080/var/html/index.html          # -> 200, body == var/html/index.html
```

### HTTPS rung — pending adjudication (§5)

All of these, run **from the bare-metal host**:

```sh
curl -sS -D- https://www.tillandsias.org.localhost/ -o /dev/null   # 200, NO -k / --insecure
curl -sS -D- http://www.tillandsias.org.localhost/  -o /dev/null   # 301/308 -> https://
curl -sS     https://www.tillandsias.org.localhost/ | diff - var/html/index.html
```

Plus, in a **real browser** — the part `curl` cannot prove:

- padlock closed, no interstitial, no click-through;
- `window.isSecureContext === true`;
- a cross-origin `fetch()` governed by ordinary CORS preflight — i.e. a genuine
  secure origin, not a `localhost`-exemption artefact.

> The no-`-k` criterion is what separates a real result from a fake one. If it
> needs `-k`, the browser's secure-context and CORS behaviour will not match
> production — which was the entire point.

### Lifecycle round-trip — pending the MCP socket (§3)

`publish_local` → URL · `service_status` → running · `service_stop` → gone and
the URL stops answering. Today: ask the host agent, which proxies these.

---

## 9. OpenSpec state — read before writing any spec

This repo is `schema: spec-driven`. A survey on 2026-09-01 found the following,
which changes how the local-serve capability must be recorded.

### 9.1 There are no main specs yet

`openspec/specs/` is **empty**, and so is `openspec/changes/archive/`. Every
requirement in this project exists only as an unarchived delta under
`openspec/changes/add-container-framework/specs/`.

> **Consequence:** a `## MODIFIED Requirements` delta **cannot** be written
> today. The MODIFIED workflow requires copying the requirement block out of
> `openspec/specs/container/https/spec.md`, which does not exist until
> `add-container-framework` is synced or archived. Any attempt produces a
> partial-content MODIFIED — the exact pitfall that loses detail at archive time.
>
> **Sequence:** add a `## Purpose` section to each of the six delta specs
> (none has one, so archiving now would leave six main specs carrying
> `TBD … Update Purpose after archive`), *then* sync, *then* write the new change.

### 9.2 🔴 Pre-existing defect: the repo contradicts itself on canonical host

**This is independent of the local-serve work and predates it.**

| Says **www** is canonical | Says **apex** is canonical |
|---|---|
| `proposal.md:3-4`, `:25-26` | `design.md` |
| `tasks.md:18-19` ("apex :80 301 redirect to www") | `specs/container/https/spec.md:3-14` |
| | `container/tillandsias-vhost.conf:26-28` (shipped code) |

The shipped code and the normative delta agree on **apex-canonical**; the
proposal and the task list say the opposite. A future implementer following
`tasks.md` will build the redirect backwards. Worth fixing as an
`/opsx:update` on `add-container-framework` (planning artifacts only — that
workflow must not touch code).

*Not fixed unilaterally: it is outside the scope this session was given, and
reversing the wrong way would invalidate the CONTAINERFILE, the vhost,
`dev-run.sh` and `design.md`.*

### 9.3 What the local serve collides with

- **Canonical host** (`specs/container/https/spec.md:3-14`) mandates a
  scheme-preserving 301 from `www.tillandsias.org` → apex. The shipped regex
  `^www\.tillandsias\.org$` is anchored, so `www.tillandsias.org.localhost`
  **escapes it** and is served — correct behaviour, but *accidental*. The right
  delta **scopes** the rule (public zone hosts redirect; `.localhost` hosts
  serve directly) rather than reversing it.
- **Automatic wildcard certificate** (`:16-25`) specifies Let's Encrypt DNS-01
  for the zone. `.localhost` is special-use, outside the zone, uncovered by
  `*.tillandsias.org`, and **not issuable by Let's Encrypt**. This requirement
  cannot stretch — local TLS needs a *new* requirement, not a MODIFIED one.
  (Blocked behind the §5 adjudication regardless.)
- **Rootless Podman deployment** (`specs/container/deploy/spec.md:3-14`) is an
  unconditional MUST for Quadlet + host ports 80/443. As written, a
  host-launched sibling on 8080 is **non-conforming**. Needs scoping to
  production.
- **Development mount** (`specs/site/release/spec.md:29-35`) already mandates
  that `./var/html` be mountable directly as the document root with no bundle.
  **This is the one existing requirement the local serve extends rather than
  fights** — build on it.
- Nothing in any OpenSpec artifact mentions `.localhost`, a sibling container, a
  router, or port 8080.

### 9.4 Convention: never hand-scaffold a change

`openspec new change "<name>"` creates required metadata (`.openspec.yaml`)
before any artifact is written. Creating the directory by hand is explicitly
forbidden by the repo's own skills. This work is **new intent**, not a
refinement of `add-container-framework`, so it belongs in its own change.

> **Held.** The new change is *not* created yet: its central content is the
> canonical-host and TLS deltas, which are exactly what is under adjudication
> in §5. Writing it now would commit the repo to a design the operator has not
> settled. Do this once the adjudication lands.

## 10. Session log

Append; do not rewrite.

### 2026-09-01 — `tillandsias.org-forge-claude` (Claude Code, Opus 5)

- Established the §4 environment facts.
- **Narrowed the socket blocker to one missing host-side bind** and derived the
  exact host path from the tmpfs device shared with `/run/secrets`. The host
  used this to root-cause a **real launcher bug** (`build_forge_agent_run_args_with_vault`
  never calls `start_mcp_socket_server_for_lane`); **fixed on trunk `19057a9e3`**.
- First to record that the router is **Caddy on :8080 only with the admin API
  closed** — so HTTPS needs host work independent of the socket, and a forge can
  never self-register a route.
- Host stood up the sibling + route by proxy; **verified the serve independently**
  (200, `Via: 1.1 Caddy`, byte-identical body).
- Found **`/.git/` is served** (§6.1) and the **apex `.localhost` is unrouted**
  (§6.2); reported both.
- Corrected this plan's content-handoff design — the earlier named-volume idea
  was wrong; the real mechanism is the git loop in §2.1.
- Recorded the runtime contract (§7) and the HTTPS hold (§5).
- Fixed `scripts/dev-run.sh` so `--mode=skip` needs no CloudFlare token
  (`ee96f9d`), from the host's report.
- Surveyed the OpenSpec state (§9). Found a **pre-existing contradiction**
  between `proposal.md`/`tasks.md` (www-canonical) and
  `design.md`/`specs/container/https`/the shipped vhost (apex-canonical) —
  reported, not fixed unilaterally.
- Added supersession banners to `SiblingContainerDiagnosis.md` and
  `container-diagnostics.md`; both asserted the path was blocked, which is no
  longer true, and the Codex one recorded an in-forge 200 as evidence of a host
  route. Content kept for provenance.
