<!-- ============================================================ -->
<!-- level-4-security.audit.md — AGENT ANNOTATIONS, NOT CONTENT.   -->
<!-- Build pipeline does NOT read this file (only level-*.md       -->
<!-- slugs listed in scripts/build-matrix.py LEVELS are rendered). -->
<!-- Audit scope: tillandsias runtime repo at v56.9.2.1. Run       -->
<!-- 2026-09-04. No page content was modified.                     -->
<!-- ============================================================ -->
Valid for pin v56.9.2.1 only; superseded by docs/audit/2026-09-05-v56.9.2.1.md once that record lands.

# Agent audit annotations — level 4 ("I'm a Cyber Security expert")

Audited against `github.com/8007342/tillandsias` @ `v56.9.2.1`. Verdict: the
strongest-verified page — all six RED footnotes are REAL at the pin, 24/26
footnotes fully OK. Two citation fixes and two prose sharpenings needed, no
material falsification.

## Per-footnote verdicts

| Ref | Verdict | Note |
|-----|---------|------|
| [^1] | OK | README.md#L52-L53 — Linux: no VM; macOS/Windows: utility VM. |
| [^2] | OK | podman-idiomatic-patterns/spec.md#L201-L203 — escape runs as invoking user's UID, $HOME-only (L204 widens the range). |
| [^3] | OK | docs/cheatsheets/enclave-architecture.md#L217-L225 — generous allowlist + DNS/header exfiltration verbatim. |
| [^4] | OK | policy.rs#L14-L22 — 4 flags + policy rejects --privileged/--cap-add=ALL/non-keep-id. |
| [^5] | OK | default-image/spec.md#L743 — SELinux MCS = planned Phase 6, no implementation. |
| [^6] | OK (RED confirmed) | container_spec.rs#L376-L383 — `debug_assert!(policy::validate_launch_argv(...))` is the ONLY production call; compiled out (no [profile.release] debug-assertions override). Flags are conditional bool fields (launch.rs L363-L365). "Not even logged" holds in the default posture (invocation logging gated on TILLANDSIAS_DEBUG=1). |
| [^7] | OK (RED confirmed) | litmus-podman-idiomatic-security-flags.yaml#L30-L53 — steps 4-8 echo the SAME token on both branches via `|| echo '<TOKEN>'`; PCRE sweep confirms exactly 5 occurrences, all this file; step 2 tests podman run, not the real argv builder. |
| [^8] | OK (cite gap) | scan-litmus-false-pass.sh#L1-L41 — advisory (L33), skips 1139/2026 steps (L19-L23), keyed on rc. The "approved bar-raise is diff-scoped, structurally incapable of flagging existing corpus" clause in the PATH is TRUE but lives at plan/index.yaml#L14302 (order 634-39ik), not in the cited range. |
| [^9] | OK | images/proxy/squid.conf#L109-L124 — SslBump peek→bump ONLY release-assets.githubusercontent.com→splice all else. |
| [^10] | OK | squid.conf#L75-L81 — system trust store verified upstream; standing no-DONT_VERIFY order. |
| [^11] | OK | scripts/clamp-ca-material.sh — dir-before-key clamp, two pre-fix hosts found world-readable after packet close. |
| [^12] | OK | proxy-container/spec.md#L63-L74 — spec promises per-launch EC P-256 tmpfs chain, no key to disk; NO stale/SUPERSEDED marker. |
| [^13] | OK (RED confirmed) | orchestrate-enclave.sh#L95-L120 — code generates single self-signed RSA-2048 30-day cert reused across restarts; spec's generate_ephemeral_certs() has ZERO code references. Spec-vs-code mismatch real. |
| [^14] | OK (RED confirmed) | git-mirror-service/spec.md#L53-L72 — `--export-all --enable=receive-pack`; "network placement SHALL NOT be described as client authentication". No dated replacement. |
| [^15] | OK | secure-channel/src/lib.rs#L64-L130 — release_root_secret = SHA-256(binary); HKDF domain-separated per release/hop. |
| [^16] | OK (RED confirmed) | vsock_server.rs#L83-L119 — absent/empty/"off"→Off; six files across five crates document/read TILLANDSIA...SECURE_CONTROL_WIRE, nothing sets it; vz.rs propagates default "off". |
| [^17] | OK | secure-channel-maturity-ladder-2026-07-04.md — M1 default-OFF active; shipped wiring matches M1. |
| [^18] | OK | encrypted-channel-perboot-key-hardening-2026-07-01.md — approved, deferred. |
| [^19] | OK | release.yml#L325-L326 — `--certificate-identity-regexp "https://github.com/.*/tillandsias/"` pins repo NAME only (org unconstrained). |
| [^20] | OK | images/git/Containerfile#L19-L21 — vault:1.18 and alpine:3.20 mutable tags, no digests. |
| [^21] | **DRIFT (citation)** | The claims (verifies with no verifier identity; ship bundles + pinned root, ~34 KB) are TRUE but live at plan/index.yaml#L12087 (order 588-ttex), NOT in homebrew-harness-distribution-research-2026-07-11.md#L28-L29 (which alone says "SLSA Build L2"). Re-point the footnote. |
| [^22] | OK | tillandsias-vault/spec.md#L85-L91 — share in host OS native keychain. |
| [^23] | OK (RED confirmed) | README.md#L115 — v0.4.260826.1 "podman system reset is not credential-cold"; 900-z3kv open (reproduced on a third host, plan/index.yaml#L45562). |
| [^24] | OK | host-browser-mcp/spec.md#L387-L404 + server.rs L376/L876 — eval visible but EVAL_DISABLED refusal. |
| [^25] | OK | philosophy.yaml#L48-L50 — falsifiability + evidence-is-not-proof. |
| [^26] | OK | math-foundations.yaml#L91-L125 — bounded ranking, not probability. |

## Prose points that need editing

1. **PATH on line 19 — "For the missing hypervisor on Linux nothing is recorded
   at all" is overstated.** The escape blast radius IS recorded
   (podman-idiomatic-patterns/spec.md#L201-L204 — invoking user's UID, $HOME-only).
   Accurate wording: "no record framing it as a design tradeoff; the blast radius
   mitigation is recorded."
2. **"415 litmus files" (NOTE, line 16)** — 415 is the directory ENTRY count
   (411 *.yaml + 4 support files). Say "411 litmus files" or "sweeping the litmus
   corpus".
3. **[^21] citation** — re-point to plan/index.yaml#L12087.
4. **[^8] PATH clause** — the diff-scoped bar-raise is real but uncited; add
   plan/index.yaml#L14302 (order 634-39ik).
5. **"Nothing validating a push server-side" (line 73)** is UNVERIFIABLE from the
   repo (GitHub branch protection is external config). Soften to "nothing in this
   repo validates a push server-side" or verify the branch settings first.

## Recommended changes for the next editor

- Fix the [^21] and [^8] citations; soften line 19 and "415"; scope line 73.
- All six RED flags are REAL and current at the pin — this is the correct, hard
  page for the project's honesty discipline. Do not remove REDs; the only edits
  needed are the citation/precision fixes above.

## Ownership

This page (level 4) is owned for content by the website editors. These
annotations are advisory; the explanation text was intentionally not edited.