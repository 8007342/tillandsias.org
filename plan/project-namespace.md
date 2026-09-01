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

> **Superseded — the split is THREE tiers, not two. See §4.4**, which adds the
> per-project named volume and states the rule: *the repo keeps only what
> genuinely needs history; anything that merely needs to survive a container
> goes to the project cache volume.*

---

### 2.2 Blast radius — the free hand is narrower than it looks

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

## 4. Runtime-side rulings (host, 2026-09-01)

### 4.1 The fork: **(b)**, reframed — and the reframe is the point

**Ledger migration is not feasible now.** The runtime `plan/` is a 31k-line
folded index plus hundreds of append-only fragments, loop-status dirs and
attestation ledgers — and the real cost is that the **entire tooling surface
pins those paths**: the `tillandsias-plan` binary, the fold, `build.sh` gates,
litmus fixtures, the plan-only push lane, mo-full attestation checks. It is a
tooling migration mid-flight on the thing that coordinates the fleet. *"Not this
week, honestly not this month."*

**And (b) is not the dual-source-of-truth trap.** This is the correction worth
keeping — the objection recorded in §2.2 was wrong, and here is why:

> The trap is **two copies of ONE policy** (seven `pids` sites; two launchers).
> This is **two policies for two different KINDS of thing**: the runtime's own
> native ledger (**self-state**) versus Tillandsias state inside repos it does
> not own (**customer-state**).
>
> A detection reading *"runtime repo → native `plan/`; everything else →
> namespaced layout"* carries **one honest distinction**, not two drifting
> copies.

**Revisit trigger (the expiry clause, reframed):** if a **second in-repo
consumer of the native layout** ever appears, the distinction is dead and (a)
becomes due. Write the rule as the distinction, not as an exception.

### 4.2 Dual-path probe: yes, emphatically

Image rebuild costs ~15–20 min host-native, at effectively every install — so
cutover cadence is not the bottleneck. **Build both-paths acceptance in from the
start.** A customer repo carrying the new layout against an old baked engine is
exactly the delivery-gap class that appeared three times this week.

### 4.3 `init` is EXPLICIT — and it is precedent, not taste

Launch-time writes into a checkout are **already filed as a defect** on the
runtime ledger (`955-fgh7`, the opsx re-materialization arm: 22 files silently
rewritten 11s after clone — *"no guest runs pristine stable"*). Auto-bootstrap
on a stranger's repo is the same class with worse optics.

> **Launch detects, reports `not initialized` with the one command that fixes
> it, and mutates nothing.** If a specific flow ever wants auto, that is an
> opt-in flag **on the launch**, never a default.

### 4.4 The split is THREE tiers, not two

The missing mount already exists: **`~/.cache/tillandsias-project`**, the
per-project named volume `tillandsias-forge-cache-<project>` — mounted in every
forge, surviving container recycles, host-reachable.

| Tier | Where | Committed? | What |
|---|---|---|---|
| **Tillandsias-wide** | `/opt`, `/var` mounts | no | methodology, shared tooling, expert binaries, cheatsheets |
| **Per-project runtime** | `~/.cache/tillandsias-project` (named volume) | **no** | caches, staging, last-good artifacts (npm prefix and cargo target already live here) |
| **Per-project durable** | **the repo** | **yes** | plan, state, coordination notes |

> **The rule this yields:** the repo keeps only what genuinely needs *history*.
> Anything that merely needs to *survive a container* goes to the project cache
> volume. That is the test to apply to a new artifact type.

---

## 5. The "don't touch their repo" steelman — priced, and REJECTED on evidence

The alternative to committing into a customer repo is to keep state outside the
working tree: `git notes`, an orphan branch, or a custom ref namespace like
`refs/tillandsias/*`. **Tested empirically 2026-09-01 rather than argued.**

### 5.1 What the mirror actually does

| Test | Result |
|---|---|
| Push `refs/notes/*` to the mirror | ✅ **accepted**, and relayed upstream to GitHub |
| `git ls-remote` shows it | ✅ present on the mirror |
| **Fresh `git clone` receives it** | 🔴 **NO** — refs absent, `git notes show` errors |
| Clone's default fetch refspec | `+refs/heads/*:refs/remotes/origin/*` — **heads only** |
| Explicit `fetch 'refs/notes/*:refs/notes/*'` | ✅ works |

### 5.2 Why this kills the steelman

The mirror is not the problem — **the clone is**, and that is worse.

> Every forge starts from a **fresh clone**. A notes/custom-ref convention would
> therefore give every forge **no state and no error** — indistinguishable from
> "this project has no state". Silent, and wrong in the safe-looking direction.

It *is* fixable by configuring the forge's clone with an extra refspec. But then
**the durability of customer state depends on launcher configuration rather than
on the repo's own contents** — precisely the failure class this fleet hit three
times in one week (env var set but socket absent; mount present but socket
absent; code fixed but binary stale). A convention that is correct only when the
launcher is configured correctly is the wrong shape for a durability mechanism.

### 5.3 Two further nails

- **`refs/tillandsias/*` is already taken.** The mirror carries a live
  `refs/tillandsias/upstream-auth/authorized/*` namespace. Putting plan state
  there would collide with an existing runtime convention.
- **🔴 Ref deletion is disabled on the mirror.** Verified:
  `[pre-receive] REJECT: ref deletion is disabled: refs/notes/commits` /
  *"transaction or receive hardening policy failed before upstream relay"*.
  **Any ref namespace you create is permanent.** A ref-based convention cannot
  be cleaned up, renamed, or backed out — which is disqualifying for something
  meant to be initialized into strangers' repos, where getting it wrong once is
  forever.

> **Verdict: reject.** Committed files in the working tree survive a plain
> clone with no configuration, can be inspected by a human who has never heard
> of Tillandsias, and can be deleted. None of those is true of refs here.
>
> *Cost of the rejection, stated honestly:* customer repos carry files they did
> not ask for. That is a real cost, and it is what §3's naming question is for —
> it is a design problem, not a reason to choose a mechanism that fails silently.

### 5.4 Residue from the test

The probe left `refs/notes/commits` on the mirror (and relayed to GitHub) and it
**cannot be deleted** — deletion is disabled. Content is self-describing
(`tillandsias mirror-refspec probe b908ce1`) and nothing fetches it by default.
Reported to the host, who has container-level access to the git service if they
want it pruned.

## 6. Research in flight

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

## 7. Findings and decision

*(empty — research had not landed when this was written)*

---

## 8. Log

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

### 2026-09-01 (third) — runtime rulings landed; steelman tested and rejected
- Host ruled on all four open questions (§4). **Conceded the fork argument**:
  my dual-source-of-truth objection was wrong — (b) is two policies for two
  *kinds* of thing (self-state vs customer-state), not two copies of one policy.
  Recorded with the revisit trigger.
- **Learned the split is three-tier, not two** (§4.4) — the per-project named
  volume `~/.cache/tillandsias-project` already exists and is the intended home
  for uncommitted per-project runtime state. The repo now keeps only what needs
  *history*, which materially narrows what a customer repo has to carry.
- **Tested the steelman instead of arguing it** (§5). The mirror accepts and
  relays `refs/notes/*`, but a **fresh clone does not fetch them** — so a
  ref-based convention gives every forge no state and no error. Rejected on
  evidence, with the cost of rejecting stated.
- Two findings from that test that stand on their own: `refs/tillandsias/*` is
  **already a live namespace** (upstream-auth), and **ref deletion is disabled**
  on the mirror, so any ref namespace created is permanent.
- The test left an undeletable `refs/notes/commits` probe on the mirror (§5.4);
  reported to the host.
