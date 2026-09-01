# Host notes

**This file is for the bare-metal host agent** (e.g. `macuahuitl-fedora`), or
anyone with podman access on the machine running the Tillandsias Runtime.

A forge session cannot see your filesystem, cannot run `podman`, and cannot read
your terminal. Cross-session chat does not survive a forge relaunch. **This file
is the only durable channel back.** Append a dated entry, commit, push.

Working context lives in [`local-https-serve.md`](local-https-serve.md) — its §2
records what a forge can see from the inside, and §3 lists what is being asked
of you.

## What would be most useful to record here

- **The lane MCP socket.** Whether
  `/run/user/1000/tillandsias/mcp/tillandsias.org-default/mcp.sock` is bound,
  what component owns the listener, and how it is started. A relaunched forge
  hits this same wall every time; naming the owning component turns a
  half-session of rediscovery into one command.
- **The content-handoff decision** (`local-https-serve.md` §4.2, options a/b/c)
  and any host-side path a forge should stage into.
- **The Caddy config** — where the Caddyfile or JSON config lives, how routes
  are added, and whether the router publishes host ports.
- **The certificate story** — which CA signs `*.localhost` leaves, and whether
  it is already in the bare-metal browser/NSS trust store.
- **Anything that surprised you.** Especially SELinux relabelling, rootless
  port-binding limits, or uid/gid mismatches on shared volumes — those are
  invisible from inside a forge and cost the most to rediscover.

## Notes

<!-- Append below. Newest last. Date every entry. -->

_(none yet — awaiting first host reply)_
