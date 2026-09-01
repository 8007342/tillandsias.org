# Workstream: where Tillandsias state lives inside a foreign repo

**Status:** 🔵 **RESEARCH IN FLIGHT** — no decision yet, do not implement
**Opened:** 2026-09-01
**Owner:** operator (`bulloncito`), raised 2026-09-01

---

## 1. The question

Tillandsias opens **arbitrary git projects** in ephemeral forge containers. The
checkout is thrown away, so any durable state — plans, findings, cross-session
memory, host↔agent coordination — **must be committed into the project's own
repo** or it is destroyed. (This document exists because of that rule; see
[`local-https-serve.md`](local-https-serve.md) §4.1.)

So: **what should that directory be called, and where should it sit, in a repo
Tillandsias does not own?**

Today it is a bare top-level `plan/`. Two problems with that:

### 1.1 `plan/index.yaml` collides with Tillandsias's own project detection

Verified 2026-09-01: `project-info.sh:397` probes `$PWD/plan/index.yaml`, and
`forge-plan.sh:293-294` states that *"a non-Tillandsias project has no
`$PWD/plan/index.yaml` and falls through"*. So the presence of that one file is
what makes a project *look* Tillandsias-native.

> That is **by design** — the operator confirms projects opened in Tillandsias
> are *meant* to carry a plan directory. The collision is not that the concept
> is wrong; it is that the **generic name `plan/` is doing load-bearing
> detection work**, and a foreign project may already have a `plan/` directory
> meaning something else entirely.

### 1.2 A bare top-level `plan/` is invasive

It claims a very generic name at the root of someone else's repo. But the
opposite instinct — `.tillandsias/` everywhere — is *also* unwanted: we do not
want to pollute other people's projects with vendor-branded dirs and files.

**Both instincts are in tension and the research is meant to resolve it, not
split the difference.**

---

## 2. Constraints the answer must satisfy

| Constraint | Detail |
|---|---|
| **Source-controlled** | The project's own plan/state **must** be committed. This is non-negotiable — it is the whole durability mechanism. |
| **Non-invasive** | A repo owner who has never heard of Tillandsias must not be surprised, broken, or annoyed by what appears. |
| **No collisions** | Must not clash with the host project's own conventions, filenames, build globs, or packaging. |
| **Discoverable** | By both agents (cold-start) and humans (a maintainer reading the repo). |
| **Bootstrappable** | Most projects have **none** of the structure we need. `tillandsias init` must create it safely in a foreign repo. |

### 2.1 The committed/mounted split

Not everything goes in the repo. The intended division:

- **Committed to the project repo** — that project's own plan, state and
  coordination notes.
- **Mounted into the forge** (at `/var`, `/opt`) — methodology, shared tooling,
  expert binaries, caches. These are Tillandsias-wide, not project-specific, and
  have no business in a customer's git history.

**The research must produce a *rule* for this split**, not just a list, so a
future implementer can classify a new artifact type without asking.

---

## 2.2 Blast radius — the free hand is narrower than it looks

The operator (2026-09-01): **tillandsias.org is the only Tillandsias project in
the world**, so customer-project migration is a non-issue (n=1, this repo), and
forges can be initialized however the design needs.

**But the detection probe targets three paths, not one** (`project-info.sh:397-399`):

```
$PWD/plan/index.yaml
$HOME/src/tillandsias/plan/index.yaml
$HOME/tillandsias/plan/index.yaml
```

So the **runtime repo's own `plan/`** is detection surface too — and that is the
live ledger (packets, orders, attestations). It is *not* a break-freely target.

> **The real constraint is the runtime ledger, not the customer projects.**
> That gives a fork, owned by the runtime side:
>
> - **(a) One convention, both sides.** The runtime ledger migrates too. Clean
>   end state; real migration cost on a large live ledger.
> - **(b) Two shapes.** Runtime keeps `plan/`; customers get the new layout.
>   Cheaper now — but detection carries two cases forever and "where does state
>   live" gets no single answer. That is the same dual-source-of-truth shape
>   that produced the MCP socket bug and two other partial fixes the same week.
>
> Preference is **(a)** for that reason; if migration is not sane mid-flight,
> **(b) with a written expiry** beats pretending. Asked of the host 2026-09-01.

### 2.3 Moving detection requires an IMAGE REBUILD

`project-info.sh` lives in `~/.config-overlay/mcp/` and the answer engine is
**image-baked** — "unlike the launch-built plan engine no relaunch rebuilds it".
It is writable inside a forge, but such an edit dies with the container and
reaches nothing.

> So a namespace change is **not a repo change**. It is an image rebuild plus a
> coordinated cutover, with a window where a project could carry the new layout
> while the baked engine still probes the old path. **Proposed de-risk: make the
> probe accept BOTH paths during the transition**, so the image and the repo can
> land independently. Cheap now, expensive to retrofit.

---

## 3. Candidates under consideration

`plan/` (status quo) · `.tillandsias/` · `.config/tillandsias/` ·
`.local/state/tillandsias/` · `var/tillandsias/` · `docs/tillandsias/` ·
riding an emerging agent convention (`AGENTS.md` / `.agent/`) · or keeping it
out of the repo entirely (orphan branch, `git notes`, `refs/tillandsias/*`).

### 3.1 The crux, stated early so it is not lost

> `.github/` is **committed** and universally accepted. `.idea/` is
> **gitignored** and frequently resented. Both are vendor dotdirs at the root,
> so hiddenness is not what separates them.
>
> **Tillandsias state MUST be committed — so the naming choice has to land on
> the `.github/` side of whatever line that is.** Identifying that line is the
> central research question; everything else follows from it.

Also worth noting: this repo already carries **both** precedents — `var/html`
(FHS-flavoured, non-dot) and `openspec/` (vendor, non-dot, committed) — so
neither dot nor non-dot is foreclosed here.

---

## 4. Research in flight

Launched 2026-09-01 from this forge. Six parallel sweeps:

1. **Vendor dotdirs** — what real ecosystems do, and *why* some are committed
   and others gitignored.
2. **The in-repo `.config/` movement** — whether it is an adopted standard or
   folklore (nodejs/tooling#79 and descendants).
3. **XDG + FHS** — whether `XDG_STATE_HOME` semantics (`~/.local/state`, the
   closest match to what we store) or FHS `var/` transplant into a repo.
4. **Agent-era conventions 2025-2026** — `AGENTS.md`, `.claude/`, `.cursor/`,
   MCP config locations, and any prior art on *persisted agent state* in-repo.
5. **Invasiveness + collision avoidance** — the concrete breakage a new
   top-level dir causes (packaging, build globs, linters, monorepo workspaces),
   whether a leading dot changes it, and namespace-reservation patterns
   (RFC 8615 `.well-known/`, reverse-DNS).
6. **Bootstrap mechanics** — how `copier`, `pre-commit`, `husky`, `openspec init`
   et al. scaffold into a repo they do not own: idempotency, conflict handling,
   `.gitignore` policy, versioning, uninstall.

Then a synthesis (one opinionated layout, the migration for *this* repo, and
the bootstrap design) and an adversarial critique — including a steelman of
"do not touch their repo at all".

> **Note for whoever picks this up:** the research output may not have survived
> the container it ran in. If §5 below is still empty, **re-run it** rather than
> guessing — the workflow script is reproducible from this section's sweep list.

---

## 5. Findings and decision

*(empty — research had not landed when this was written)*

---

## 6. Log

### 2026-09-01 — `tillandsias.org-forge-claude`
- Operator raised the question after this session's `plan/index.yaml` warning;
  confirmed a plan directory **is** intended, but the naming and placement are
  open, and `.tillandsias`-style pollution is explicitly not wanted.
- Recorded constraints and launched the six-sweep research above.
- **Tillandsias.org is the first customer**: it is itself a non-Tillandsias-shaped
  project, so whatever is decided gets migrated here first (§7 of the eventual
  decision doc).

### 2026-09-01 (later) — operator granted a free hand; scope clarified
- Operator: tillandsias.org is the **only** Tillandsias project, so break freely
  and coordinate forge init as needed.
- **Tested that premise rather than taking it:** the probe also targets
  `~/src/tillandsias/plan/index.yaml`, the runtime's own live ledger. The free
  hand is real for customer projects (n=1) but the ledger is the binding
  constraint (§2.2).
- Established that moving detection needs an **image rebuild**, not a repo edit
  (§2.3), and proposed a both-paths transition so image and repo can land
  independently.
- Asked the host: ledger migration feasibility, rebuild cadence, whether
  `tillandsias init` should be automatic at launch or explicit opt-in, and
  whether an existing `/var` or `/opt` mount is the intended home for
  per-project runtime state.
