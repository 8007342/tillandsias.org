## Purpose

The "I'm a power user" page (`docs/matrix/level-3-power.md`) is the anatomy: what
runs where, what survives a teardown, and where the sharp edges are. Its audience
understands containers, networking and CI, and expects the architecture plus its
honest failure list.

## ADDED Requirements

### Requirement: Enclave anatomy accuracy
The page MUST describe the current enclave membership accurately. The "Five
members" list is stale — the live enclave has ten-plus attach sites (proxy, git,
ssh-lane sidecar, inference, router, nix cache, catalog service, observatorium
web, opencode forge, forge agent-with-vault, vault). The next editor MUST pull
the roster from `scripts/check-enclave-membership-documented.sh` or stop labeling
the list exhaustive; the project itself documents this failure mode (an earlier
hand-maintained list went stale by six members).

#### Scenario: Anatomy matches the live guard
- **WHEN** the page enumerates enclave members
- **THEN** the list matches the documented-membership guard's roster or is
  explicitly non-exhaustive, and the `--internal` network + single-dual-homed
  proxy claim stays intact

### Requirement: Survivorship claims are current
The page MUST state what survives a stop, `podman system reset`, and
`--reset-guest` per the pinned code: mirror volume + fast-forwarded working copy,
keychain-backed vault auto-unseal, model cache as a host bind mount, and the
`--reset-guest` wipe set that keeps the cache. The vault "share only ever lands on
tmpfs" line MUST be qualified by the shipped fallback share file at
`/root/.cache/tillandsias/fallback_vault-shamir-share-v1`.

#### Scenario: Survivorship lines match the pin
- **WHEN** an editor changes a survivorship bullet
- **THEN** each artifact's fate (stop / `podman system reset` / `--reset-guest`)
  matches the pinned code, including the fallback share file

### Requirement: RED findings MUST be current against the pin
Each RED MUST reflect the pinned code, not a stale plan entry. Known doctoring
burden from the 2026-09-04 audit:

- **[^13] global proxy block:** order 923-rmtw is COMPLETED — `--init` deletes the
  global `[engine] env` proxy block (`main.rs:7364-7400`). The RED must be scoped
  to legacy hosts not yet re-run through `--init` plus the still-open
  "failure names the proxy" follow-up, or re-verified against 892-pfnd.
- **[^11] macOS destroyers:** 804-bpke is COMPLETED — the shipped
  `scripts/uninstall.sh` preserves the VM unless `--wipe` (`uninstall.sh:124-128`).
  Re-count the destroyers (effectively three), drop or qualify "the shipped
  uninstaller included".
- **[^3] orchestrate-enclave.sh creates the enclave network WITHOUT `--internal`**
  remains TRUE and is the page's most important live RED — keep it.

#### Scenario: A stale RED is caught before publish
- **WHEN** the page is edited and the checked build is run
- **THEN** each RED line traces to current code or a re-verified open packet, with
  no plan entry the code has already outrun

### Requirement: Gate and CI statements
The local-gate description (litmus + traces, eleven grandfathered files,
dispatch-only `release.yml` as the sole workflow) MUST stay accurate and sourced
to `methodology/ci.yaml` and `openspec/litmus-tests/unbound-grandfathered.txt`.

#### Scenario: Gate claims stay sourced
- **WHEN** the gate or CI section is edited
- **THEN** the count of grandfathered litmus files and the single-workflow claim
  still match the pinned tree

## ADDED Artifacts

### Artifact: Level-3 audit annotations
`docs/matrix/level-3-power.audit.md` — agent-facing annotations from the
2026-09-04 audit. Companion to the page; never rendered by the build.