# Audit records

One record per run of the [`update-website`](../../skills/update-website/SKILL.md)
loop, named `<YYYY-MM-DD>-<release tag>.md`, plus the issue drafts that run
produced (`<date>-issues-tillandsias.md`, `<date>-issues-tillandsias.org.md`).

A record answers, per level: footnotes total, re-verified, drifted and
corrected; flags confirmed and flags flipped, each with its evidence; the pin
before and after. And, for the site as a whole, the completeness tables: one
row per capability the pages advertise, with
`implemented | partial | spec-only | absent` at the release and a citation.

The per-level annotation files under `docs/matrix/*.audit.md` are the
predecessors of these records (written 2026-09-04 against v56.9.2.1); new
runs write here.
