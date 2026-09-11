---
name: agent-commit
description: Format git commits per the agent-commit AGENTS.md convention and gate them with the npx agent-commit CLI (init, check, merge-draft, log, show). Use for every commit or commit-message task in this repo.
---

Every commit in this repo follows the `agent-commit` trailer format. The
canonical rule block lives at the repository root in `AGENTS.md` (section
"Commit messages"); `CLAUDE.md` imports it. Read `AGENTS.md` before your
first commit — it is the source of truth, not this file.

## The CLI

Run it via npx; it is not a registered harness tool, so run it as a shell
command. The package does **not** generate messages — it gates, reads, and
drafts the `Agent-Context: {json}` git trailer that the AGENTS.md block
defines. Use the subcommands that fit the task:

- `npx agent-commit init .` — write/refresh the AGENTS.md block and its
  CLAUDE.md import. Refuses to overwrite an unrelated existing convention.
- `npx agent-commit check --range <range>` or `--count <n>` — advisory
  gate: reports `OK` / `MISS` (no trailer) / `MISPLACED` (trailer present
  but git didn't recognize it as one) per commit. Exits non-zero when any
  checked commit is not `OK`. Run it after committing or before pushing.
- `npx agent-commit merge-draft <range>` — draft starting point for the
  condensed Agent-Context of a squash-merge commit: unions
  `touches`/`refs`/`breaking`, lists each commit's `why` as a candidate.
  Use when squash-merging a PR; condense the candidates yourself, never
  synthesize a `why` the tool didn't list.
- `npx agent-commit log` / `show` — read history / individual commits
  filtered by the trailer fields.

## The message shape (from AGENTS.md)

1. A normal, clear one-line summary.
2. Optionally a blank line and a body.
3. Optionally, if the summary and body don't carry the context (a rejected
   alternative, a non-obvious constraint, the real cause behind a fix),
   add a **single-line** trailer as the very last part of the message:

   `Agent-Context: {"why":"...","refs":["TICKET-123"]}`

Only include a field when it carries real content; an absent `why` is
honest, a fabricated one isn't. Keep `touches` and `refs` repo-relative
(`src/auth`, not `auth` or `./src/auth`) and use the tracker's short form
(`#123`, never a full URL).

## Building the message

Always build via `git commit -F -` (heredoc with a quoted delimiter like
`<<'EOF'`) or `git commit -F <file>` — never hand-escape the JSON's quotes
inside a `-m` argument, that's a common way to corrupt the trailer.

## Gate

Run `npx agent-commit check --range origin/main..HEAD` before pushing a
branch, and after any squash-merge. Never reword historical commits just
to add trailers — that falsifies authorship/timestamps.