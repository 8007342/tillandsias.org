# Workstream: local serve from a sibling container

**Status:** 🟢 **HTTP rung LIVE and verified** · 🟡 **HTTPS rung HELD** — blocked on a durable trust root · 🟡 **MCP socket** fix built, relaunch in flight
**Opened:** 2026-09-01
**Last updated:** 2026-09-01 by forge session `tillandsias.org-forge-claude`

> **Cold-start? Read this box.**
>
> The site **is serving right now**, on **both** hosts:
> `http://www.tillandsias.org.localhost:8080/var/html/index.html` and
> `http://tillandsias.org.localhost:8080/var/html/index.html`. You do **not**
> need to rebuild that.
>
> **If you are a relaunched session:** the operator accepted a tray relaunch on
> 2026-09-01 to deliver the MCP socket fix, on a tray binary rebuilt to carry it
> (§3). **The socket is expected to work — check it first.** Does
> `/run/host/tillandsias-mcp/mcp.sock` exist, and does `host-browser` connect?
> If yes, the socket rung is DONE: verify with `publish_local {"category":"WEB"}`
> and record it in §10. If no, that is a genuine surprise the host needs told —
> the fix fires on every launch by two independent paths, so a miss means
> something new.
>
> **The three remaining threads:** (1) the MCP socket, above; (2) HTTPS —
> **do not build this repo-side**, it is under adjudication, and it is now
> blocked on something concrete: the enclave CA is a 30-day root on tmpfs that
> the browser does not trust, so a **durable trust root** must come first (§5.1);
> (3) the docroot convention so `/` works (§6.1) — host-side, this repo declares
> nothing.
>
> **Do not** re-derive the environment from scratch: §4 has it, with evidence.
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
| Forge drives `publish_local` itself over MCP | 🟡 fix built; tray relaunch in flight (§3) |
| Docroot convention (`/` works, `/.git/` doesn't) | 🟡 filed host-side (§6.1) |
| Local HTTPS | 🟡 **held** — needs a durable trust root first (§5.1) |
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

### The real delivery gap — the running tray binary predates the fix

A plausible worry was that the fix might only fire at lane *creation*, leaving
an already-created lane socket-less forever. **The host checked: it does not.**
The call sits inside `create_dir_all`, which succeeds on existing directories,
so it fires on **every launch of every lane** — and the tray-boot enumeration
*independently* binds all existing projects at startup. Two paths, either
sufficient.

> **The actual gap was one neither side had named: the running tray binary
> predates both fixes.** Shipping the code was never going to be enough.

Sequence in flight (2026-09-01): host-native rebuild + install → tray relaunch
on the new binary → this lane re-minted → socket bound two independent ways.
This container goes down at the relaunch step.

### 🔴 Host ask #5 — rootless low-port bind (added 2026-09-01)

**This would block the HTTPS serve even after the socket and the route both
land, and it was missing from the original four asks.**

A port-less `https://www.tillandsias.org.localhost` requires the router to
publish `127.0.0.1:443` (and `:80`). Under rootless podman that host-side bind
**fails by default**. Fix on the host:

```sh
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee /etc/sysctl.d/99-rootless-lowports.conf
```

**✅ CONFIRMED BLOCKING (host, 2026-09-01):** the host really is at
`net.ipv4.ip_unprivileged_port_start=1024`, so the `:443`/`:80` loopback publish
**fails today**. Filed as an operator-level host ask (a `sysctl.d` drop-in) on
the adjudication.

> **Do not work around this with `https_port 8443`.** That reintroduces a port
> into the URL and defeats the whole point of the exercise. Recorded with the
> ask.

### Delivery costs a relaunch — ✅ DECIDED: relaunch now (2026-09-01)

Delivering the fix to this lane requires a tray relaunch, and forge containers
are killed in the stack's shutdown sweep. The alternative was to do nothing and
let the socket arrive on the next fresh launch, with the host proxying
`publish_local` meanwhile.

**The operator chose to relaunch now.** All state was committed and pushed
first, which is what made the choice cheap — this document *is* the handoff.

> **To the session reading this after the relaunch:** verify the socket landed
> (see the cold-start box at the top). Until you have confirmed
> `host-browser` connects, assume it did **not** and keep using the host agent
> as `publish_local` proxy.

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
- secure-context fidelity, so ordinary CORS preflight rules govern `fetch()`;
- loopback `:443` publish from the router container;
- a defined cert-trust route into the bare-metal browser/NSS store.

A relaunched session must **not** helpfully "finish" this — it would cut across
a pending decision. Await the adjudication.

### 5.1 Cert-issuance investigation (adjudication input, 2026-09-01)

Investigated from inside the forge and requested by the host for the packet.

#### 🔴 The CA is a 30-day root on tmpfs, and the browser does not trust it

**Answered by the host 2026-09-01, and it reshapes this whole section.**

- **Self-signed 30-day root**, born 2026-08-30, expires **2026-09-29**.
  `subject == issuer` — the file named `intermediate.crt` **is the root**.
- It lives at **`/tmp/tillandsias-ca`**, i.e. **on tmpfs**. It **dies on host
  reboot and regenerates**.
- It is **NOT in the bare-metal NSS store**.

> **So the worst case is the actual case.** Hand-installed browser trust would
> break silently on every regeneration — a reboot, and the padlock is gone with
> no error that points at the cause.
>
> **Consequence for the adjudication: local HTTPS needs a DURABLE TRUST ROOT
> before any leaf-minting question matters.** Either the enclave CA moves to a
> persistent location with real validity and a one-time trust install, or Caddy
> uses `tls internal` with a *persisted* Caddy root. Choosing a minting strategy
> on top of an ephemeral root would be building on sand.

The unconstrained-CA finding below **stands**, and is precisely what makes the
durable-root option viable: the CA *can* sign these names, so the only thing
missing is somewhere permanent to keep it.

#### The enclave CA can legitimately sign a `.localhost` leaf — this is the key finding

`/run/tillandsias/ca-chain.crt` is a **self-signed RSA-2048 root**:
`CN=Tillandsias CA, O=Tillandsias, L=Local, ST=Privacy, C=US`,
`sha256WithRSAEncryption`, serial `0x3a793bb9…f0806`.

It carries **exactly three extensions**: `subjectKeyIdentifier`,
`authorityKeyIdentifier`, and `basicConstraints CA=TRUE` (critical, **no
pathlen**). There is **no `nameConstraints`, no `keyUsage`, no
`extendedKeyUsage`**.

> **It is therefore unconstrained**: it can sign a leaf for any DNS name —
> multi-label `.localhost` names included — and can also sign an intermediate.

And this is the **established pattern, not a novel one**: Vault's own serving
cert is `CN=vault, O=Tillandsias`, issued by `CN=Tillandsias CA`, with
`SAN: DNS:vault, DNS:localhost, IP:127.0.0.1` — it **already contains a
localhost SAN**. So the operator directive's enclave-CA basis is technically
sound for `.localhost`; nothing about the special-use TLD obstructs it.

#### Corroborating detail: the per-batch mint

30-day total lifetime, `notAfter 2026-09-29T23:34:31Z` — **28 days out**. The CA
and Vault's leaf share an identical `notBefore` (`2026-08-30T23:34:31Z`), so the
enclave PKI is minted in one batch at tray start. It predates this container, so
it is **per-tray-session, not per-container**: it survives forge relaunches but
**not a tray restart**.

> Any leaf minted from it must clamp `notAfter` to the CA's own. The durability
> problem is stated in full above — it is now answered, not open.

#### Vault cannot issue this today (from a forge token)

Vault is **HTTPS on 8200, not HTTP** — probes using `http://vault:8200` fail
misleadingly with a 400 rather than an auth error. It is live, initialized,
unsealed, v1.18.5, and its TLS chains cleanly to the Tillandsias CA with no `-k`.

The injected token is an **AppRole service token**, `role_name=claude-forge`,
policies `['claude-forge-policy','default']`, TTL 3600, renewable. It **cannot
reach a PKI mount**.

> **Unprovable from here:** whether a PKI engine exists *at all*. Vault returns
> an identical `403 permission denied` for a nonexistent mount and a denied one
> — a deliberately bogus control mount name returned the same 403 as `pki`. Only
> a root/admin token or the operator running `vault secrets list` settles it.
> **Do not record "Vault has no PKI" as a fact.**

#### Three wiring options, in preference order

**Option A — Caddy `pki` with the Tillandsias CA as root.** Caddy mints its own
intermediate under that root (valid: the CA has no pathlen constraint), giving
`Tillandsias CA → Caddy intermediate → leaf`, auto-renewed. The HTTP→HTTPS 308
is inserted automatically; no redirect block needed. Requires mounting the CA
**key** into the router — a real trust decision for the operator, and the main
argument against A.

**Option B — host mints a static leaf; Caddy just serves it.** `tls <crt> <key>`,
where the `.crt` is leaf + Tillandsias CA (full chain). SAN should cover
`www.tillandsias.org.localhost`, `tillandsias.org.localhost`, `127.0.0.1`, `::1`
with `serverAuth` EKU, and `notAfter` **clamped to the CA's**. Simplest to reason
about; someone must re-mint on every CA rotation.

> ⚠️ **A working minting script was produced during this investigation but is
> deliberately NOT committed** — it is Python, and `methodology.yaml`
> (`tlatoani_hard_no_python`) forbids Python for committed automation. Its
> presence on PATH is not permission. If option B is chosen, the minting step
> belongs to the host's own tooling, not to this repo.

**Option C — `tls internal` (fallback).** Only if the Tillandsias CA key cannot
be mounted. Two caveats that will bite: the browser must trust **Caddy's own**
root (`/data/caddy/pki/authorities/local/root.crt`) — a *second* CA to install,
not the Tillandsias one; and the router **must** have a persistent `/data`
volume or that root regenerates on restart and browser trust silently breaks.

#### ✅ The load-bearing unknown — answered, and the answer is "no"

**Is the Tillandsias CA already in the bare-metal browser/NSS trust store?**
**No.** Answered by the host 2026-09-01. Combined with the tmpfs/30-day facts
above, this is what turns "mint a leaf" into "establish a durable trust root
first" — see the top of §5.1. It is the reason local HTTPS is a real piece of
work rather than a one-command fix.

### 5.2 Design notes retained as input

- **`.localhost` resolution.** RFC 6761 reserves `.localhost`; systemd-resolved
  and major browsers map it to loopback, so publishing `127.0.0.1:443` suffices.
  Multi-label `.localhost` names have historically been weaker in Firefox than
  Chrome — verify, do not assume. **Note this forge does *not* resolve
  multi-label `.localhost` at all**, which is why §8's HTTPS checks must run
  host-side.
- **HSTS on a `.localhost` origin is a trap.** `Strict-Transport-Security` is
  stored **per host** and would pin `www.tillandsias.org.localhost` to HTTPS on
  the developer's machine long after the container is gone; `includeSubDomains`
  can poison *other* projects' `.localhost` hosts. Set HSTS only on the real
  public origin. Caddy adds none on its own — but if a production header block is
  ever copy-pasted down, guard it mechanically with
  `header /* { -Strict-Transport-Security }` in the local site block.
- **Rootless low ports.** See host ask #5 in §3 — this blocks the serve even
  after the socket and route land.
- **SELinux.** Fedora + rootless podman + `seclabel` mounts: bind mounts into a
  sibling need `:z`/`:Z` relabelling or the server 403s with a non-obvious cause.
- **uid/gid.** The forge writes as `1000:1000`; images commonly run workers as
  `www-data`/`daemon`. Content must be world-readable.
- **Keep the canonical-host anchor.** `container/tillandsias-vhost.conf`'s
  `RewriteCond ^www\.tillandsias\.org$` is anchored, so the local name escapes
  the 301 — but that safety is *accidental*. It **must not** be relaxed to cover
  `.localhost` suffixes: doing so would 301 a local browser to the public apex.

## 6. Findings

### 6.1 ✅ RESOLVED — the document root is the repo root, so `/.git/` was served

**Was:** `/.git/config` returned **200** through the mount, as did `/README.md`,
`/CONTAINERFILE`, `/plan/`. The curated busybox image serves the **project root**
at `/var/www` — the same cause as the `/` 404, but it exposed the whole
repository, including `.git/` (full history reconstruction; `config` carries
remote URLs).

Local-only, so low severity *today* — but **high blast radius**: this is the
same container shape the Cloudflare tunnel rung makes publicly reachable, and a
served `.git/` on a public origin is a standard, actively-scanned finding.

**Now:** the host capped it at the Caddy layer — `/.git/config` → **403** on
both hosts, verified from the forge 2026-09-01. The dotfile deny is **permanent
packet scope** for generated public routes, and the severity framing is filed on
the docroot packet: that rung is not a 404 nicety, it is *what stops the
document root being the repo root*.

**Still open:** `/` returns 404 until the docroot rung lands. `var/html/` will be
the **default** convention — **this repo declares nothing** and must not add
config for it yet.

> **Deliberately not done:** a root `index.html` redirect stub. It would be
> exactly the repo-shape change the rung exists to avoid, and cruft afterwards.
> The host confirmed this restraint was right.

### 6.2 ✅ RESOLVED — the apex `.localhost` was unrouted

**Was:** `tillandsias.org.localhost` → 404 (**Caddy's** "no route for…"), while
only `www.` was registered. The production vhost 301s `www.tillandsias.org` →
apex, so once HTTPS lands, anything exercising that redirect locally would land
on an unrouted host.

**Now:** both hosts serve — verified from the forge 2026-09-01. `publish_local`
registering **both** hosts is now packet scope, with the production
apex-canonical reasoning attached.

### 6.3 The production CONTAINERFILE cannot ride `publish_local` — by design

`publish_local` uses a **curated catalog with a frozen busybox image**. This
repo's `CONTAINERFILE` (Apache, vhosts, cf-token secret) is the **public rung's**
container. Local preview rides the catalog; the two are separate paths and are
not expected to converge.

### 6.4 Git is the only sanctioned content channel

There is no host-side staging path for a forge to write build output into.
`publish_local`'s bundle-streaming option is unimplemented, and the public
rung's release contract is this repo's own **versioned-zip-of-`var/html`** spec
(`specs/site/release`), which rides the release machinery rather than a side
channel. **Do not invent a staging directory.**

### 6.5 ✅ RESOLVED — the www→apex 301 downgraded HTTPS to plaintext

**A production bug in shipped code, on exactly the path the Cloudflare rung
takes.** Found and fixed 2026-09-01 (`73f015a`).

`container/tillandsias-vhost.conf:28` redirects with `%{REQUEST_SCHEME}`:

```apache
RewriteCond %{HTTP_HOST} ^www\.tillandsias\.org$ [NC]
RewriteRule ^(.*)$ %{REQUEST_SCHEME}://tillandsias.org$1 [R=301,L]
```

`%{REQUEST_SCHEME}` resolves to `ap_http_scheme(r)`, which — with **no mod_ssl
and no scheme on `ServerName`** — is hard-coded to `http`. The file has a single
`<VirtualHost *:80>` and never reads `X-Forwarded-Proto`.

> **Result:** a client arriving at `https://www.tillandsias.org` through a
> TLS-terminating proxy is 301'd to **`http://tillandsias.org/`** — downgraded
> to plaintext for a round trip, on the canonical-host redirect, for every
> `www` visitor.
>
> The comment at line 25 — *"preserving scheme (works for http dev and https
> prod)"* — is **factually wrong**. This is precisely the topology both the
> Cloudflare tunnel rung and the proposed Caddy termination create.

The fix is to trust the forwarded scheme (`X-Forwarded-Proto`, with `mod_remoteip`
and a trusted-proxy list) rather than `%{REQUEST_SCHEME}`, or to hard-code
`https://` in the redirect target.

**Fixed 2026-09-01 in `73f015a`:** the target scheme is now hard-coded to
`https`, with the `mod_remoteip` + `X-Forwarded-Proto` alternative recorded in
the conf as the upgrade path (and a note that its trusted-proxy list is not
optional, since a forwarded header is client-controlled otherwise).

> The rule matches only `Host: www.tillandsias.org` — a public hostname always
> reached through a terminator — so hard-coding is correct here and local dev,
> which never presents that Host, is unaffected.
>
> **The restraint protocol worked as intended.** It was reported rather than
> patched on discovery, precisely because it touched a redirect under
> adjudication; the host then gave an explicit go, and the owner independently
> confirmed apex-canonical. A deliberate go, not a drive-by.

### 6.6 The vhost is the default for `*:80`, so it answers for any Host

`<VirtualHost *:80>` is the **only** vhost in the config, which makes it the
default for that port: every request on :80 lands in it regardless of Host, and
`ServerName`/`ServerAlias` do not gate anything. `Host: anything.example.com`
returns **200** with the site.

**Host ruling 2026-09-01: accepted as a deliberate-decision item, filed to the
packet — do NOT change it yet.** Behind Cloudflare the tunnel config constrains
hostnames anyway, and the local serve currently **relies** on this behaviour:
it is *why* `www.tillandsias.org.localhost` is served at all.

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

> These **cannot be run from a forge** — this container does not resolve
> multi-label `.localhost` names at all. Host-side only.

Plus, in a **real browser** — the part `curl` cannot prove:

- padlock closed, no interstitial, no click-through;
- `location.protocol === 'https:'`;
- DevTools → Security shows the connection **encrypted**, issuer
  **`Tillandsias CA`** (or whichever CA the adjudication picks);
- a cross-origin `fetch()` governed by ordinary CORS preflight.

> ### ⚠️ `window.isSecureContext` is NOT a valid check here — corrected 2026-09-01
> An earlier draft of this plan listed `window.isSecureContext === true`. **That
> criterion is worthless for this task.** Both Chrome and Firefox treat *every*
> `.localhost` origin as a secure context **over plain HTTP**, so it returns
> `true` whether or not TLS is working. It cannot distinguish a real HTTPS serve
> from the HTTP one we already have.
>
> The no-`-k` curl and the DevTools issuer check are the criteria that actually
> discriminate. If `curl` needs `-k`, the certificate is untrusted and the
> browser's CORS behaviour will not match production — which was the entire point.

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

### 9.2 ✅ RESOLVED — the repo contradicted itself on canonical host

**This is independent of the local-serve work and predates it.**

| Says **www** is canonical | Says **apex** is canonical |
|---|---|
| `proposal.md:3-4`, `:25-26` | `design.md` |
| `tasks.md:18-19` ("apex :80 301 redirect to www") | `specs/container/https/spec.md:3-14` |
| | `container/tillandsias-vhost.conf:26-28` (shipped code) |

The shipped code and the normative delta agreed on **apex-canonical**; the
proposal and task list said the opposite. Nothing was broken at runtime, but
`tasks.md:18-19` would have had an implementer build the redirect **backwards**.

**Ruling: the project owner confirmed APEX IS CANONICAL** (2026-09-01), which is
also what three of the five sources and the running config already said.

**Aligned in `069fdea`:** `proposal.md` Why and What Changes rewritten, `tasks.md`
3.1/3.2 flipped, and the same drift fixed in the `container/image` delta (it
described the image as serving "the www.tillandsias.org static site"). `tasks.md`
3.1 now also carries *why* the redirect scheme is hard-coded, so the §6.5 bug
cannot be reintroduced by someone implementing the task from its description.
The six missing `## Purpose` sections were added in the same pass.

> **Deliberately NOT synced.** The local-serve delta does not exist yet, and
> syncing now would mean scoping the canonical-host rule twice instead of once.
> `openspec validate --changes` passes.

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
- Host capped `/.git/` (403) and routed the apex; **verified both from the
  forge**, plus the propagation canary green (`/plan/local-https-serve.md` →
  200 carrying the OpenSpec section). The content loop is **proven closed**.
- Folded the cert-issuance investigation into §5.1 as adjudication input, at the
  host's request: **the enclave CA is unconstrained and can legitimately sign a
  `.localhost` leaf** — and already signs one (Vault's cert carries a
  `localhost` SAN). Also recorded its **2026-09-29 expiry / per-tray rotation**
  risk, that Vault is **HTTPS not HTTP**, and that a PKI mount is *unprovable*
  from a forge rather than absent.
- **Corrected a defect in this plan's own acceptance criteria** (§8):
  `window.isSecureContext === true` is worthless here — it is `true` over plain
  HTTP on any `.localhost` origin in both Chrome and Firefox, so it cannot tell
  a real TLS serve from the HTTP one already running. Replaced with
  `location.protocol` + the DevTools issuer check.
- **Added host ask #5** (§3): the rootless low-port bind for `127.0.0.1:443`.
  It was missing from the original four and would have blocked the HTTPS serve
  even after the socket and route both landed.
- Operator chose to **relaunch now** to deliver the socket fix; checkpointed
  everything and handed off to this document.
- Found a **production bug in the shipped vhost** (§6.5): the www→apex 301 uses
  `%{REQUEST_SCHEME}`, which is hard-coded to `http` without mod_ssl, so a
  client arriving over HTTPS through a TLS terminator is **downgraded to
  plaintext**. Exactly the Cloudflare topology. Reported, not fixed — it touches
  the redirect under adjudication.

### 2026-09-01 (later) — same session, after the host's rulings

- **Owner ruled: apex is canonical.** Aligned the planning artifacts in
  `069fdea` — `proposal.md`, `tasks.md` 3.1/3.2, and the `container/image`
  drift — and added the six missing `## Purpose` sections. Not synced, by the
  host's instruction, so the canonical-host rule gets scoped once rather than
  twice. `openspec validate --changes` passes (§9.2).
- **Host gave the go on §6.5**; fixed in `73f015a`. The scheme is hard-coded to
  `https` in the www→apex redirect, with the `mod_remoteip` upgrade path
  recorded in the conf.
- **§6.6 accepted as a deliberate-decision item** and filed to the packet — not
  changed, because the local serve currently relies on it.
- **Socket hypothesis checked and closed:** the fix fires on every launch by two
  independent paths, so my "only at lane creation" worry was wrong. The real
  gap was the **running tray binary predating both fixes** — neither side had
  named it. Rebuild + relaunch in flight (§3).
- **CA answers landed and reshaped §5.1.** The enclave CA is a self-signed
  30-day root **on tmpfs** (`/tmp/tillandsias-ca`) that **dies on host reboot**,
  and it is **not in the bare-metal NSS store**. The worst case was the actual
  case. Local HTTPS now blocks on establishing a **durable trust root**, before
  any leaf-minting question matters. The unconstrained-CA finding stands and is
  what makes that option viable.
- **Host ask #5 confirmed blocking**: the host is at
  `net.ipv4.ip_unprivileged_port_start=1024`, so the `:443` loopback publish
  fails today. Filed as an operator-level ask.
