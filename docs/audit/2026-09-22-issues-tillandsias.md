# Runtime issue draft from the v56.9.21.1 site audit

## Linux clean-room step continues after a failed credential-cold probe

- Tag: `v56.9.21.1` (commit `2f5f2a90a7b43ecdee766e38561b8e5790c603aa`)
- Area: `scripts/e2e-step2-linux.sh`
- Class: defect
- Found by: tillandsias.org audit 2026-09-22, security level
- Local finding: `4aea5a83`

**Claim on the site / in the runbook.** A Linux clean-room test exercises
first-time Vault initialization without retained host credentials.

**What the code does.** `scripts/e2e-step2-linux.sh#L34-L38` runs both the
credential clearer and the cold-state probe through `tee` followed by
`|| true`. The run continues if either fails. The commands log their results,
so a reviewer can still inspect the actual starting state.

**Why it matters.** A later passing smoke check does not by itself establish
that the Vault began credential-cold. This audit found the source behavior but
did not run the Linux clean-room test.

**Smallest fix.** Fail the step when the clear or cold-state probe fails, or
make the final smoke verdict explicitly conditional on the recorded cold-state
result.

This draft has not been filed upstream.
