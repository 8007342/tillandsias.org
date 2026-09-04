<!-- ============================================================ -->
<!-- level-3-power.audit.md — AGENT ANNOTATIONS, NOT PAGE CONTENT. -->
<!-- Build pipeline does NOT read this file (only level-*.md       -->
<!-- slugs listed in scripts/build-matrix.py LEVELS are rendered). -->
<!-- Audit scope: tillandsias runtime repo at v56.9.2.1. Run       -->
<!-- 2026-09-04. No page content was modified.                     -->
<!-- ============================================================ -->

# Agent audit annotations — level 3 ("I'm a power user")

Audited against `github.com/8007342/tillandsias` @ `v56.9.2.1`. Verdict:
mostly well-anchored, but TWO RED flags reproduce plan entries the code has
already outrun, and the "Five members" anatomy is stale by the project's own
standard. This page needs real editing before the next publish.

## Per-footnote verdicts

| Ref | Verdict | Note |
|-----|---------|------|
| [^1] | OK | enclave-network/spec.md#L17-L69 — `--internal` creation, proxy-only egress, both-directions membership guard. |
| [^2] | OK | subdomain-routing-via-reverse-proxy/spec.md#L2-L42 — 80→8080→--port fallback + 2026-09-02 audit story. Naming convention `<service>.<project>.localhost` matches the ACTIVE flip spec (subdomain-naming-flip/spec.md; e.g. opencode.java.localhost); router-sidecar parses that shape. The routing spec has leftover old-shape examples at L128/L130 (its own cleanup debt — do not copy them). |
| [^3] | OK (RED confirmed) | scripts/orchestrate-enclave.sh#L81-L84 — `podman network create --driver bridge --subnet 10.0.42.0/24` WITHOUT `--internal`, no later isolation check. "No path to green" verified via plan grep. |
| [^4] | OK | forge-as-only-runtime/spec.md#L49-L67 (+L105-106 refuse-not-fallback). |
| [^5] | OK | main.rs:18844 test walks argv, asserts no host `$HOME`/`.config`/`.cache` mount. Nits: skip when host HOME==/home/forge; forge-owned ro gitconfig + tmpfs exempt. |
| [^6] | OK | git-mirror-service/spec.md#L18-L38 — bare mirror, named volume. Prose's clone/sync-skip claims live elsewhere in the same spec (L53, L168-179, L335-379) — outside the cited range. |
| [^7] | OK | AGENTS.md#L47 — verbatim. |
| [^8] | OK w/ caveat | tillandsias-vault/spec.md#L76-L95 — keychain share, tmpfs-only is the SPEC invariant; the shipped runtime also writes a fallback share file at /root/.cache/tillandsias/fallback_vault-shamir-share-v1 (plan/index.yaml#L27952/L27961). "only ever lands on tmpfs" is not observed on every path. |
| [^9] | OK | inference-container/spec.md#L28-L30 — host bind mount, NOT named volume. |
| [^10] | OK (weak anchor) | cited main.rs#L1377-L1381 is `--help` TEXT; real behavior is run_reset_guest at main.rs:8309-8393, cache exclusion pinned by test at L25121+. Recommend re-anchoring. |
| [^11] | **DRIFT (RED)** | macOS cache-in-VM physics still true (one virtiofs share, engine payload in rootfs.img, ~2.47 GB floor, partial-cache-worse-than-none). BUT "four code paths delete it, the shipped uninstaller included" is STALE: 804-bpke is COMPLETED; scripts/uninstall.sh:124-128 preserves the VM unless `--wipe` (plan/loop_status.md:1236). Default destroyers are effectively three (two SKILL.md paths + vz.rs wipe). The PATH's "gated behind a related uninstaller fix" is directionally stale — that gate landed. |
| [^12] | OK | plan/index.yaml#L27914-L27960 — Windows stale unseal share; Part A landed, reconcile half blocked on no accept/reject signal. Verbatim match. |
| [^13] | **DRIFT (RED, most serious)** | Packet 892-pfnd says containers.conf hardcodes proxy env unconditionally — but at the tag order 923-rmtw is COMPLETED: `--init` runs ensure_containers_conf_no_proxy_env which DELETES the global [engine] env proxy block (main.rs:7364-7400; plan/archive/packets-2026-08.yaml:46813-46820). "Once a host is initialised… all registry traffic through the enclave proxy unconditionally" is FALSE for hosts initialized by v56.9.2.1. Residual truth: legacy hosts not yet re-run through `--init`, and the packet's "fail with a verdict naming the proxy" deliverable is still open. |
| [^14] | OK | unbound-grandfathered.txt — exactly 11 entries, never executed, shrink-only. |
| [^15] | OK | methodology/ci.yaml#L286-L324 — ONE workflow (release), dispatch-only; .github/workflows/ contains ONLY release.yml (verified). |

## Prose points that need editing

1. **"Five members" anatomy (line 5) is wrong as exhaustive.** The live enclave
   has ten-plus attach sites (spec: proxy, git, ssh-lane sidecar, inference, router,
   nix cache, catalog service, observatorium web, opencode forge, forge agent-with-vault,
   vault). The page omits inference — while the "What survives" section discusses its
   cache. The project itself documents this failure mode (enclave-network spec: "a
   hand-maintained prose list went stale by SIX members"). Fix: enumerate the current
   roster from `scripts/check-enclave-membership-documented.sh`, or stop labeling it
   exhaustive. Note: this is a LIVE denylist — the spec forbids a prose list drifting.
2. **RED [^13]** — rewrite to the converged reality: `--init` removes the global proxy
   block (923-rmtw); the defect is legacy-host-only + the "name the proxy in the
   failure verdict" follow-up. Or re-verify 892-pfnd status before re-publishing.
3. **RED [^11]** — re-count the destroyers (3, not 4) and drop "shipped uninstaller
   included" or qualify it with `--wipe`.
4. **[^8] caveat** — add the fallback share file to the survivorship line, or change
   "the share only ever lands on tmpfs" to "the spec requires the share only on tmpfs".

## Recommended changes for the next editor

- Correct the anatomy to the live enclave membership (pull from
  scripts/check-enclave-membership-documented.sh) — this is the highest-value edit.
- Rewrite RED [^13] against 923-rmtw; rewrite RED [^11] against 804-bpke.
- Add the [^8] fallback-share caveat.
- Everything else (networks, router, mounts, mirror, vault, gate, CI budget) survives
  hard verification at the pin; keep as-is.

## Ownership

This page (level 3) is owned for content by the website editors. These annotations
are advisory; the explanation text was intentionally not edited.