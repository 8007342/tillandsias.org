> [!IMPORTANT]
> **SUPERSEDED — 2026-09-01. Contains a conclusion that is actively misleading.**
>
> This document reports the sibling container as unlaunchable. It now runs, and
> the site serves at
> `http://www.tillandsias.org.localhost:8080/var/html/index.html`.
>
> **The trap to avoid repeating:** the in-forge `HTTP 200` recorded below came
> from this container's *own* loopback, because `.localhost` resolves to the
> forge's loopback from inside a forge. An in-forge 200 proves nothing about
> host reachability. To test a host route from inside a forge, send the Host
> header to the router directly:
> `curl -H 'Host: www.tillandsias.org.localhost' http://10.0.42.91:8080/var/html/index.html`
>
> The socket root cause was later found (the live launcher never calls
> `start_mcp_socket_server_for_lane`) and **fixed on trunk `19057a9e3`** — not
> the two launch defects hypothesised below.
>
> **For current state, read [`plan/local-https-serve.md`](plan/local-https-serve.md).**
> This file is kept for provenance only.

# Container launch diagnostics

Date: 2026-09-01 UTC

Project: `tillandsias.org`

Runtime project: `8007342/tillandsias`

## Outcome

The requested sibling `httpd` container could not be launched because this
Codex session has no `host-browser` MCP server and the host control socket named
by `TILLANDSIAS_CONTROL_SOCKET` is not mounted. A user-local Apache 2.4.68
fallback is running successfully on `0.0.0.0:8080` and serves `var/html`.

Reachable only from inside this forge:

`http://www.tillandsias.org.localhost:8080/`

This is not a host-accessible route. A host-side request to the same URL reaches
the Tillandsias router and returns:

`tillandsias-router: no route for www.tillandsias.org.localhost`

The in-forge HTTP 200 occurred because the `.localhost` name resolved to this
forge's own loopback/listener context; it does not demonstrate router
registration. The pretty no-port HTTP and HTTPS URLs are likewise not routed in
this session.

An issue-creation attempt against `8007342/tillandsias` was made through the
connected GitHub integration. Repository issue search succeeded and found no
matching open issue, but creation failed with HTTP 403, `Resource not accessible
by integration`. The CLI fallback is also unavailable: its configuration is
root-owned and unreadable, and an isolated `gh` configuration has no login.

## Sibling-container control path

Expected flow (documented in `.forge-startup-context.md`):

`host-browser.publish_local({"category":"WEB"})` -> host launches sibling
container -> host router returns the local URL.

Observed:

- Codex registered only `forge-plan` and `project-info` in
  `/home/forge/.codex/config.toml`; there is no `host-browser` entry or launch
  tool in the active tool inventory.
- The image does contain
  `/home/forge/.config-overlay/mcp/host-browser.sh`, and the Claude/OpenCode
  overlay configurations register it.
- `TILLANDSIAS_CONTROL_SOCKET` is now set to
  `/run/host/tillandsias-mcp/mcp.sock`, which is an improvement over the
  2026-08-28 diagnosis in `SiblingContainerDiagnosis.md`.
- `stat /run/host/tillandsias-mcp/mcp.sock` returns `No such file or directory`.
- The bridge itself exits with the JSON-RPC error
  `TILLANDSIAS_CONTROL_SOCKET does not exist` before it can contact the host.
- No `podman`, `docker`, or `buildah` client exists inside the forge, which is
  expected if the MCP bridge is healthy.

The current failure therefore has two independent Codex launch defects:

1. the lane control socket is not mounted at the exported path; and
2. the Codex MCP configuration does not register the shipped `host-browser`
   bridge.

## Apache fallback

The documented fallback could not be installed system-wide:

- session identity: `uid=1000(forge) gid=1000(forge)`;
- `sudo` is absent, despite the intended passwordless-sudo forge contract;
- `dnf -y install httpd` fails with `requires superuser privileges`.

Fedora RPMs were instead downloaded with `dnf download --resolve --alldeps`,
and the required Apache/APR RPM payloads were unpacked beneath
`/home/forge/.local/httpd-root`. The resulting binary reports:

`Apache/2.4.68 (Fedora Linux)`

Because `net.ipv4.ip_unprivileged_port_start = 1024`, UID 1000 cannot bind port
80. The attempt fails with:

`(13)Permission denied: AH00072: make_sock: could not bind to address 0.0.0.0:80`

Apache was therefore started on `0.0.0.0:8080`. Verification:

- `GET http://127.0.0.1:8080/` -> `HTTP/1.1 200 OK`;
- response bytes exactly match `var/html/index.html` (`cmp` succeeds);
- `ss` shows Apache listening on `0.0.0.0:8080`;
- `GET http://www.tillandsias.org.localhost:8080/` -> HTTP 200;
- the same request from the host reaches `tillandsias-router` but returns
  `no route for www.tillandsias.org.localhost`;
- `http://www.tillandsias.org.localhost/` -> connection refused;
- `https://www.tillandsias.org.localhost/` -> connection refused;
- candidate no-port service routes (`tillandsias.org.httpd.localhost` and
  `tillandsias.org.web.localhost`) -> connection refused.

Runtime artifacts are intentionally outside the repository under
`/home/forge/.local` and `/tmp`. The main Apache launch PID is recorded at
`/tmp/tillandsias-httpd-launch.pid`.

## Runtime fixes and acceptance test

1. Bind-mount the lane socket at
   `/run/host/tillandsias-mcp/mcp.sock` and keep
   `TILLANDSIAS_CONTROL_SOCKET` pointed there.
2. Add the shipped bridge to Codex configuration, equivalent to:

   ```toml
   [mcp_servers.host-browser]
   command = "/home/forge/.config-overlay/mcp/host-browser.sh"
   ```

3. Restore the stated forge privilege contract by including `sudo` and a
   passwordless rule for `forge`, or amend the runtime documentation to state
   that system package installation is unavailable.
4. Relaunch a Codex forge and verify that `publish_local`, `service_status`, and
   `service_stop` are present.
5. Call `publish_local({"category":"WEB"})`, confirm the returned no-port URL
   serves `var/html/index.html`, then stop the sibling cleanly.

## What is needed from the owner

No project-content decision is needed. The next useful input is a forge
relaunch after the runtime socket mount and Codex MCP registration are fixed.
If port 80 inside the forge is meant to be a supported fallback, the relaunched
image also needs working passwordless `sudo` or a lower
`net.ipv4.ip_unprivileged_port_start`/appropriate bind capability.

To let this forge file the runtime bug autonomously, the GitHub app also needs
Issues write permission for `8007342/tillandsias` (or a usable `gh` credential).
