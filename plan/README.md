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
