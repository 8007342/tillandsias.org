---
name: file-findings
description: Record audit findings so they survive the forge, and get the ones that belong to the Tillandsias runtime in front of that project, from a session that has no GitHub credentials by design.
---

# File findings

**The constraint.** A Tillandsias forge holds no GitHub token: the credential
separation the security page describes is real, and `gh` is unusable inside
one on purpose. `git push` works, through the enclave mirror, for this
repository only. So a finding is filed in two moves: first durably in this
repo, then relayed to where it belongs.

## 1. Record in-repo (always, before anything else)

Write `docs/audit/<YYYY-MM-DD>-<tag>.md` with the per-level tables and, beside
it, one file per destination:

- `docs/audit/<date>-issues-tillandsias.md` — findings about the runtime
  (spec-versus-code gaps, stale plan entries, defects), one section per issue
  in the template below, ready to paste.
- `docs/audit/<date>-issues-tillandsias.org.md` — findings about this site.

Commit and push. The forge is ephemeral; an unpushed finding is destroyed with
it. Do not create `plan/issues/` or `plan/index.yaml` here: those names are
detection surface for the runtime's tooling (see `plan/README.md`).

## 2. Relay

Pick whichever the operator has authorised:

- **A host session with credentials** (for example the bare-metal session
  named in `plan/host-notes.md`) files them as GitHub Issues or as
  `plan/issues/` write-ups in the runtime repo, crediting the auditing
  session. Send the in-repo file's path and the issue sections by
  cross-session message; do not ask it to do anything your own session was
  denied.
- **The operator** pastes them from the in-repo file.
- **Any agent with `gh` on a host** (Claude, OpenCode, Codex, or a human) runs
  `gh issue create --repo 8007342/tillandsias --title … --body-file …` per
  section. Nothing about this is harness-specific; the template is plain
  Markdown.

A future runtime rung could add an enclave "issue mirror" that accepts an issue
body from a forge and files it with a scoped token, the way the git mirror
relays pushes. Until then the relay is a person or a host session.

## Issue template

```
## <one-line title: what is wrong, where, at which tag>

- Tag: v56.9.5.1 (commit …)
- Area: <spec name / crate / script>
- Class: spec-vs-code | stale-plan-entry | defect | doc-drift
- Found by: tillandsias.org audit <date>, level <n>

**Claim on the site / in the spec.** <quote>

**What the code does.** <path#Lx-Ly> — <quote>

**Why it matters.** <one paragraph>

**Smallest fix.** <one sentence>
```
