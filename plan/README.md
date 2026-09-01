# `plan/` — durable cross-session state

This directory is **shared, committed memory** for work that outlives a single
agent session. Forge sessions for this project run inside an *ephemeral*
container (`/home/forge/src/tillandsias.org` is container overlay, not a bind
mount — see [`local-https-serve.md`](local-https-serve.md) §2). When the forge
tears down, anything not committed and pushed is gone.

Two kinds of reader are expected, and the documents here are written for both:

| Reader | Where they run | What they need from this dir |
|---|---|---|
| A **relaunched forge session** | inside the `tillandsias.org` forge container | To resume cold: what is done, what is blocked, what to do next |
| The **bare-metal host agent** | on the podman host (e.g. `macuahuitl-fedora`) | What the runtime side is being asked for, and where to reply |

## Files

- **[`local-https-serve.md`](local-https-serve.md)** — the active workstream:
  serving `var/html` from a sibling `httpd` container at
  `https://www.tillandsias.org.localhost`. Verified facts, blockers, host
  asks, acceptance criteria, session log.
- **[`host-notes.md`](host-notes.md)** — **the host agent writes here.** A
  forge session cannot see the host's filesystem or podman; this file is the
  only durable channel back. Append, commit, push.

## Conventions

- **Facts carry evidence.** Every claim states how it was verified, or is
  explicitly marked unverified. A confident guess that later turns out wrong
  costs a whole relaunch cycle.
- **Convert relative dates to absolute.** "yesterday" is meaningless to a
  session that starts three days later.
- **Append to the session log, never rewrite it.** The history of what was
  tried and failed is the most valuable thing here.
- **Commit and push before exiting.** Not committed and pushed = destroyed.

This project has no plan *crate* (`experts: degraded(no-plan-crate)` in the
forge startup context), so these are plain Markdown documents rather than
ledger fragments — no `tillandsias-plan check` schema applies.

## 🔴 Reserved filenames — do NOT create these here

These names are **live tooling surface**, not free-form documentation. Creating
one in this directory changes how the MCP servers answer questions about this
project:

| Never create | Why |
|---|---|
| `plan/index.yaml` | `project-info.sh:397` probes `$PWD/plan/index.yaml`, and `forge-plan.sh:293-294` states that "a non-Tillandsias project has no `$PWD/plan/index.yaml` and falls through". Creating it makes this repo *look like* a Tillandsias plan project and diverts `project_answer` / `plan_query` into the plan lane. |
| `plan/index.d/` · `plan/loop_status.md` · `plan/loop_status.d/` · `plan/issues/` · `plan/mo-full-attestations.d/` | The ledger-fragment layout of the *Tillandsias meta-project*. This project has **no plan crate** (`experts: degraded(no-plan-crate)`), so these would be schema-less imitations that tooling may nonetheless try to parse. |

It is inert **today** only because no `tillandsias-plan` binary ships in this
image. A future image that ships one would start answering this project's
questions out of a hand-written file. Use descriptive names
(`local-https-serve.md`, `host-notes.md`) and keep this directory plain Markdown.

> `.forge-startup-context.md` references `scripts/check-forge-findings-persisted.sh`
> as a durability "GATE". **It does not exist in this repo, and should not be
> added** — it gates the ledger directories above, which this project does not
> have. The gate that actually applies here is simpler: `git status` clean and
> `git log origin/main..main` empty before you exit.

## ⚠️ Reaching the router from inside a forge

Two traps, both of which have already cost a session:

1. **`.localhost` does not resolve to the router from inside a forge** — it is
   this container's own loopback. An in-forge `200` proves nothing about host
   reachability.
2. **The router's hostname is not in `NO_PROXY`.** `NO_PROXY` covers
   `10.0.42.0/24` and the named services, but *not* `tillandsias-router`, so a
   request to the hostname is sent to Squid at `proxy:3128`, which is not on the
   egress allowlist and **resets the connection**. That reset looks exactly like
   "the router is down". It is not.

```sh
curl -H 'Host: www.tillandsias.org.localhost' http://tillandsias-router:8080/… # 000, reset — WRONG
curl -H 'Host: www.tillandsias.org.localhost' http://10.0.42.91:8080/…          # 200 — address by IP
curl --noproxy '*' -H 'Host: …' http://tillandsias-router:8080/…                # 200 — or bypass explicitly
```
