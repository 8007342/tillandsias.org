# Tasks

- [x] A person approves or rejects this proposal (and answers the open question on the floor panels)
- [x] `scripts/metrics.py render_chart`/`summary_rows`/`render`: stop drawing `cc_residual`; drop the stale-gap note; add the observatorium pointer
- [x] `scripts/metrics.py centicolon_status`: drop the last-score sentence; keep the floor count; add the pointer
- [x] Leave `extract` and `verify` reading `cc_residual` unchanged (append-only store, nothing deleted)
- [x] Add a `--reader` sentence for progress and centicolons saying where the score now lives
- [x] `checked-build.sh` green; both views checked in the built HTML (score panel, stale note and score sentence gone, observatorium link present, Progress chart still drawn); not served in a browser
