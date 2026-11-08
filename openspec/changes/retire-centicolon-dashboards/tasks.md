# Tasks

- [ ] A person approves or rejects this proposal (and answers the open question on the floor panels)
- [ ] `scripts/metrics.py render_chart`/`summary_rows`/`render`: stop drawing `cc_residual`; drop the stale-gap note; add the observatorium pointer
- [ ] `scripts/metrics.py centicolon_status`: drop the last-score sentence; keep the floor count; add the pointer
- [ ] Leave `extract` and `verify` reading `cc_residual` unchanged (append-only store, nothing deleted)
- [ ] Add a `--reader` sentence for progress and centicolons saying where the score now lives
- [ ] `checked-build.sh` green; serve locally and confirm both views render
