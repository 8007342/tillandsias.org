# Host notes

**This file is for the bare-metal host agent** (e.g. `macuahuitl-fedora`), or
anyone with podman access on the machine running the Tillandsias Runtime.

A forge session cannot see your filesystem, cannot run `podman`, and cannot read
your terminal. **Cross-session chat does not survive a forge relaunch — this
file does.** Append a dated entry, commit, push.

Working context is in [`local-https-serve.md`](local-https-serve.md).

## What is most useful to record here

- **The lane MCP socket** — whether it is bound, which component owns the
  listener, how it is started.
- **Content-handoff** decisions and any host path a forge should stage into.
- **The Caddy config** — where it lives, how routes are added, whether the
  router publishes host ports.
- **The certificate story** — which CA signs `*.localhost` leaves and whether it
  is already in the bare-metal browser/NSS trust store.
- **Anything that surprised you** — SELinux relabelling, rootless port-binding
  limits, uid/gid mismatches on shared volumes. Those are invisible from inside
  a forge and cost the most to rediscover.

---

## Notes

<!-- Append below. Newest last. Date every entry. -->

### 2026-09-01 — `macuahuitl-fedora` (runtime host)

*Recorded by the forge session from a cross-session reply, because chat does not
survive a relaunch. Paraphrased; the host is welcome to correct it.*

**Site is serving.** Replicated the sanctioned publish path host-side without
waiting on the socket: sibling `tillandsias-tillandsias.org-web` (curated
busybox httpd image, enclave network, hostname `web-tillandsias.org`), route
registered, Caddy reloaded. Live at
`http://www.tillandsias.org.localhost:8080/var/html/index.html`.
Root 404s because the frozen catalog image serves the **project root** at
`/var/www` — predicted by order 353's ledger note. **Docroot-convention rung
filed** (serve `var/html/` when present) so `/` works without the repo changing
shape.

**Socket root cause.** The live launcher
`build_forge_agent_run_args_with_vault` creates the lane dir, mounts it and sets
`TILLANDSIAS_CONTROL_SOCKET`, but **never calls
`start_mcp_socket_server_for_lane`**. The legacy tray path does; the tray-boot
enumeration only covers projects existing at startup, and `tillandsias.org` was
born after the last tray boot. Same dual-source-of-truth class as two other
partial fixes this week. **Fix on trunk: `19057a9e3`.** Delivery to a lane needs
one tray relaunch, which kills forge containers via the shutdown sweep — so it
happens at a moment the operator chooses. **Until then the host is
`publish_local` by proxy**: message it for start/stop/status.

**Contract answers.** `publish_local` returns
`http://www.<project>.localhost:<router_host_port>` — HTTP and port-ful today;
the https no-port shape arrives with the TLS work. The Runtime **mints** the
sibling name `tillandsias-<project>-web`. Content is a **read-only bind mount of
the host worktree `~/src/tillandsias.org`** — never the forge's overlay
checkout; the forge's named-volume proposal is not what the tool does, and
streaming a bundle over the socket is unimplemented. Edit loop: forge
commits → pushes to the enclave mirror → host worktree pulls → the ro mount
reflects it instantly.

**HTTPS is under adjudication.** An operator directive of **2026-07-24** already
commissioned local HTTPS on an enclave-CA basis (proposed `images/apache`). The
forge's Caddy-terminates-at-the-router proposal (origin stays plain HTTP — the
Cloudflare shape) is filed as **adjudication input against it**, along with the
forge's requirements (real green padlock, secure-context fidelity, loopback
`:443` publish, cert-trust route). **Do not build TLS repo-side yet.**

**Also filed:** this repo's production `CONTAINERFILE` (Apache, vhosts,
cf-token secret) **cannot ride `publish_local` by design** — the catalog is
curated and its image frozen. That CONTAINERFILE is the **public rung's**
container; local preview rides the catalog.
