## 1. Change scaffolding

- [x] 1.1 Create change directory `openspec/changes/add-level-page-specs/` with
      `.openspec.yaml` (schema `spec-driven`, created 2026-09-04; the date is
      quoted so the push hook's YAML `safe_load` accepts it)
- [x] 1.2 Write `proposal.md`, `design.md`, `tasks.md`
- [x] 1.3 Create delta spec directories `specs/site/level-common/` and
      `specs/site/level-{1,2,3,4,5}/`

## 2. Page specs

- [x] 2.0 `specs/site/level-common/spec.md` — rules shared by every level:
      per-level pin, pin equals stable or the lag is recorded, checked build
      with verbatim quotes, RED lifecycle at a pin bump, audit records, argument
      markers
- [x] 2.1 `specs/site/level-1/spec.md` — "Like I'm 5" purpose/content contract
- [x] 2.2 `specs/site/level-2/spec.md` — "I barely understand my phone" contract
- [x] 2.3 `specs/site/level-3/spec.md` — "I'm a power user" contract
- [x] 2.4 `specs/site/level-4/spec.md` — "I'm a Cyber Security expert" contract
- [x] 2.5 `specs/site/level-5/spec.md` — "I'm a MathWiz / Hacker" contract: own
      pin that may lag, every change through an OpenSpec change with evidence,
      verdicts re-derived at each pin bump
- [x] 2.6 Strip dated findings, order ids, ledger line numbers, file counts and
      mandated verdicts out of every requirement and Purpose paragraph; file
      them as the work items in section 4 (revision of 2026-09-05)

## 3. Verification

- [x] 3.1 `openspec validate --changes` passes. Recorded 2026-09-05 (last run,
      after the skeptic's revision): `✓ change/add-container-framework` /
      `✓ change/add-level-page-specs` / `✓ change/level-5-stable-pin-deltas` /
      `Totals: 3 passed, 0 failed (3 items)`, exit 0, no warnings
- [ ] 3.2 `var/html/index.html` rebuilds byte-identical. The check:
      `sha256sum var/html/index.html`, then
      `TILLANDSIAS_OUT=<private file> TILLANDSIAS_CLONE_DIR=<clones> python3 scripts/build-matrix.py`
      and `sha256sum <private file>`; the two hashes must be equal on a tree
      whose `docs/matrix/level-*.md` are unmodified. Run 2026-09-05: committed
      page `79a9b2e849a7f148b9a14c660594a0eef57f80554a93a400dcd9dc610a97afff`,
      private build `36c97e6c3cf56976021e6be6aaea120dbf9c5c2c599f12808cd86f0992db851d`
      — not comparable, because levels 1, 2 and 5 were being edited in the same
      working tree at the time. Left unchecked; re-run on a clean tree.
- [ ] 3.3 (optional, on adoption) sync specs to `openspec/specs/site/level-<n>/`
      and `openspec/specs/site/level-common/`, then archive the change

## 4. Findings of the 2026-09-04 audit at v56.9.2.1

Dated findings lifted out of the specs, from `docs/matrix/level-{1,2,3,4}-*.audit.md`
and the 2026-09-05 critique of this change, re-checked against the stable
checkout (v56.9.2.1) and the newest daily (v56.9.5.1). Paths only: the line
numbers live in the page footnotes, which the checked build verifies. Items
marked "applied 2026-09-05" were resolved on the pages by the per-level editing
agents of that session; the dated audit record of that run is the evidence.

### Level 1

- [x] 4.1 Doorman-key RED/PATH pair. The world-readable CA key exposure is
      closed at the pin: the key travels as a podman secret and is clamped and
      healed to owner-only permissions (`crates/tillandsias-headless/src/main.rs`,
      `scripts/clamp-ca-material.sh`; the packet is closed in
      `plan/archive/packets-2026-08.yaml`). "Nobody has done it" was false at
      the pin. Rewritten as a past-tense flag stating what remains. Applied
      2026-09-05.
- [ ] 4.2 Badge word-list premise. The cited issue span reasons from two menu
      builders; the tree has one (`crates/tillandsias-host-shell/src/menu_state.rs`).
      The PATH claim survives; re-point the span when the footnote is next
      touched.

### Level 2

- [x] 4.3 Credential-store wording. The login token lands in the guest Vault,
      and Linux/headless hosts have a keychain-backed file fallback
      (`crates/tillandsias-headless/src/vault_bootstrap.rs`); the page said
      "your operating system's own password store". Reworded to the local secret
      store with the fallback noted. Applied 2026-09-05.
- [x] 4.4 Unsigned-package scoping. The release workflow withholds only the
      unsigned MSIX; the unsigned EXE and ZIP still publish with a warning when
      the signing account is unset (`.github/workflows/release.yml`). Sentence
      scoped to the MSIX and the workflow cited. Applied 2026-09-05.

### Level 3

- [x] 4.5 Anatomy. The "five members" list was stale against the
      documented-membership guard (`scripts/check-enclave-membership-documented.sh`),
      omitting inference among others. Roster made to match the guard or
      labelled non-exhaustive. Applied 2026-09-05.
- [x] 4.6 Global proxy block RED. At the pin `--init` deletes the global engine
      proxy environment (`crates/tillandsias-headless/src/main.rs`; the order is
      archived in `plan/archive/packets-2026-08.yaml`), so "all registry traffic
      through the proxy unconditionally" held only for hosts not re-initialised;
      the "failure verdict names the proxy" follow-up is still open. RED
      rescoped. Applied 2026-09-05.
- [x] 4.7 macOS cache destroyers RED. The shipped uninstaller preserves the VM
      unless `--wipe` (`scripts/uninstall.sh`); the page counted it among the
      destroyers. Count corrected and the uninstaller qualified. Applied
      2026-09-05.
- [x] 4.8 Enclave network RED. At the pin `scripts/orchestrate-enclave.sh`
      creates the enclave network without `--internal`; the daily channel passes
      `--internal` and refuses a pre-existing network that is not internal.
      Stays RED at the pin; its PATH names the daily with an `@v56.9.5.1`
      footnote. Applied 2026-09-05.
- [ ] 4.9 Vault share caveat. The runtime also writes a fallback share file
      under the cache directory (`crates/tillandsias-headless/src/vault_bootstrap.rs`);
      "the share only ever lands on tmpfs" is the spec invariant, not observed
      on every path. Qualify the survivorship line.
- [ ] 4.10 Reset-guest anchor. The footnote for what `--reset-guest` keeps
      cites `--help` text; the behaviour and its cache-exclusion test live in
      `crates/tillandsias-headless/src/main.rs`. Re-anchor when next touched.

### Level 4

- [x] 4.11 Linux boundary PATH. "Nothing is recorded at all" overstated: the
      escape blast radius is recorded
      (`openspec/specs/podman-idiomatic-patterns/spec.md`); what is missing is a
      record framing the absent hypervisor as a design tradeoff. Applied
      2026-09-05.
- [x] 4.12 Corpus count. "415 litmus files" was the directory-entry count, not
      the file count, and changes with every release; replaced by the count at
      the pin or "the litmus corpus". Applied 2026-09-05.
- [x] 4.13 Provenance-research footnote. The verifier-needs-no-identity claim
      lives in the ledger (`plan/index.yaml`), not in the cited research file;
      re-pointed to a target whose quote verifies at the pin. Prefer
      `plan/archive/` over `plan/index.yaml` when the claim allows: the ledger
      is the most volatile file in the runtime. Applied 2026-09-05.
- [x] 4.14 Bar-raise follow-up. The diff-scoped false-pass bar-raise the PATH
      describes was uncited; footnoted (`plan/index.yaml`). Applied 2026-09-05.
- [x] 4.15 Push-validation scope. "Nothing validating a push server-side" is
      unverifiable from the repository (branch protection is external); scoped
      to what this repository shows. Applied 2026-09-05.
- [ ] 4.16 Hardening section at the next pin bump. At the pin the launch-argv
      policy is called only from a debug assertion and the hardening litmus
      echoes the same token on both branches, so both REDs hold. The daily
      channel enforces the policy in release builds
      (`crates/tillandsias-podman/src/container_spec.rs`), and the litmus file
      no longer carries the same-token pattern
      (`openspec/litmus-tests/litmus-podman-idiomatic-security-flags.yaml`);
      only the advisory scanner (`scripts/scan-litmus-false-pass.sh`) is
      unchanged. The PATH lines may name the daily now; at the pin bump
      re-derive both verdicts, and note that the debug-assertion call site no
      longer exists in the daily, so a past-tense flag needs a new target (the
      doc comment that replaced it) and the "five occurrences, all in this
      file" sweep result is zero there.

### Level 5

- [x] 4.17 Delta change at the current pin. The 2026-09-05 re-verification of
      level 5 against the newest daily is filed as its own OpenSpec change,
      `openspec/changes/level-5-stable-pin-deltas/`: the pin stays at v56.9.2.1,
      one statement false at the pin is corrected, and the shortcomings fixed
      only in the daily channel keep their REDs with the daily named on their
      PATH lines through `@v56.9.5.1` footnotes. Filed 2026-09-05; lands when
      the operator approves it.
- [ ] 4.18 Delta change at the next pin bump, as its own OpenSpec change: the
      REDs on property tests and on requirement identifiers are outrun in the
      daily channel (`crates/tillandsias-plan/Cargo.toml`,
      `crates/tillandsias-plan/src/obligation.rs`, `crates/tillandsias-plan/src/obligation_props.rs`,
      requirement-id comments under `openspec/specs/`); the footnotes into
      `crates/tillandsias-plan/src/fragments.rs`, `scripts/local-ci.sh` and
      `methodology/proximity.yaml` drift between the tags; the measured numbers
      in the prose are re-measured. One delta per item with `path#L` evidence
      and a verbatim quote at the target tag.
