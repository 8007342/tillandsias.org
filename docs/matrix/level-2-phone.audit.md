<!-- ============================================================ -->
<!-- level-2-phone.audit.md — AGENT ANNOTATIONS, NOT PAGE CONTENT. -->
<!-- Build pipeline does NOT read this file (only level-*.md       -->
<!-- slugs listed in scripts/build-matrix.py LEVELS are rendered). -->
<!-- Audit scope: tillandsias runtime repo at v56.9.2.1. Run       -->
<!-- 2026-09-04. No page content was modified.                     -->
<!-- ============================================================ -->

# Agent audit annotations — level 2 ("I barely understand my phone")

Audited against `github.com/8007342/tillandsias` @ `v56.9.2.1`. Verdict: the
most accurate of the audited pages — 14/14 footnotes verify, none missing. Two
prose overstatements worth correcting when the page is next touched.

## Per-footnote verdicts

| Ref | Verdict | Note |
|-----|---------|------|
| [^1] | OK | PRIVACY.md#L30-L41 — workspace isolation protects you from the tools. |
| [^2] | OK | PRIVACY.md#L5-L17 — no account/telemetry/analytics/server. |
| [^3] | OK (label) | PRIVACY.md#L42-L46 — "local secret store"; see prose caveat below. |
| [^4] | OK | LICENSE#L1-L2 — GPLv3. |
| [^5] | OK | ephemeral-secret-refresh/spec.md#L1-L20 — reissued at every start. |
| [^6] | OK | PRIVACY.md#L47-L48 — "designed to be wiped and rebuilt freely." |
| [^7] | OK (paraphrase) | convergence.yaml#L1-L20 — Δ(spec↔code)+Δ(code↔cheat)+Δ(cheat↔reality)+Δ(litmus↔spec) must not grow. "Measured by a machine" is not literally in the cited span (it lives at L28-L35/L57) but is a fair reading. |
| [^8] | OK | philosophy.yaml#L228-L232 — evidence, not proof. |
| [^9] | OK | math-foundations.yaml#L107-L120 — contraction explicitly not claimed. |
| [^10] | OK | README.md#L27-L45 — Gatekeeper block only for browser downloads; curl path is clean. |
| [^11] | OK | macos-gatekeeper-signing-options-2026-08-29.md — options/costs recorded, seam pre-wired (env var names). |
| [^12] | OK | store-msix-submission-blockers-2026-08-31.md#L26-L40 — unsigned MSIX uninstallable (0x800B0100), no workaround. |
| [^13] | OK (label) | windows-signing-research-2026-08-16.md#L1-L25 — SignPath decided, application chain pending. Prose caveat below re: "refuses to publish unsigned". |
| [^14] | OK | expert-serve-grounded-pipeline/proposal.md#L1-L25 — facade stamped valid with no retrieval. |
| [^15] | OK | expert-serve-grounded-pipeline/tasks.md — genuinely in progress (4.5 mlua evidence, 5.10 live session verification still open). |

## Prose points that overreach and should be tightened

1. **"any login you hand over goes into your operating system's own password
   store, not a file of the project's devising"** is overstated. The GitHub login
   token lands in the guest Vault (crates/tillandsias-headless/src/diagnose.rs:1426),
   and on Linux/headless there is an explicit fallback FILE
   (vault_bootstrap.rs:1363-1364 — "Fallback: file (populated by keychain_set_blocking
   when keyring unavailable…)"). PRIVACY.md says only "a local secret store" — use that.
2. **"the release process now refuses to publish that file unsigned"** is true but
   scoped: the gate (release.yml:652-658) withholds the MSIX only; the unsigned EXE/ZIP
   still publish with a warning when `TILLANDSIAS_SIGNING_ACCOUNT` is unset
   (release.yml:645-646). Also lives outside the cited [^13] range.

## Recommended changes for the next editor

- Re-source [^13] supporting line to `.github/workflows/release.yml#L645-L658` (or keep
  the issue ref and add the workflow line) and scope the sentence to the MSIX.
- Replace the "operating system's own password store" clause with "a local secret
  store (the platform's vault; on some hosts a keychain-backed file fallback)".
- Level 2 is otherwise fit to keep as-is; no footnotes are missing or drifted.

## Ownership

This page (level 2) is owned for content by the website editors. These annotations
are advisory; the explanation text was intentionally not edited.