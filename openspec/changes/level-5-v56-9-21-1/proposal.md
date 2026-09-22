# Refresh level 5 citations for stable v56.9.21.1

Level 5's argument remains supported at the new stable release. Move its pin from
`v56.9.12.2` to `v56.9.21.1` only after the checked build resolves every
footnote. The only page edits authorized by this change are the eight citation
range corrections below; quoted text and explanatory prose stay as they are.

| Footnote | Old range | New range | Evidence at v56.9.21.1 |
| --- | --- | --- | --- |
| 8 | `methodology/convergence.yaml#L410-L432` | `#L413-L437` | The bar-raise rule and operator decision remain in this range. |
| 27 | `scripts/local-ci.sh#L384-L403` | `#L390-L414` | The check-weight table remains in this range. |
| 30 | `methodology/convergence.yaml#L329-L342` | `#L340-L357` | The complexity ratio and 5000-line warning remain in this range. |
| 34 | `crates/tillandsias-plan/src/fragments.rs#L2853-L2886` | `#L2971-L3005` | The commutativity test remains in this range. |
| 35 | `crates/tillandsias-plan/src/fragments.rs#L307-L320` | `#L339-L353` | The status-ladder discussion remains in this range. |
| 38 | `methodology/provenance.yaml#L179-L192` | `#L167-L180` | The quoted CRDT precondition is in this range. |
| 43 | `scripts/local-ci.sh#L542-L544` | `#L565-L569` | The shell still delegates score arithmetic. |
| 45 | `scripts/local-ci.sh#L591-L599` | `#L612-L620` | The shell still reports a broken comparison regime. |

These are source and quote checks at the tagged tree, not a live validation of
the mathematical model. External scholarly references are unchanged.
