# Refresh level 5 citations for stable v56.9.27.2

Level 5's argument remains supported at the new stable release. Move its pin from
`v56.9.21.1` to `v56.9.27.2` only after the checked build resolves every
footnote. The page edits authorized by this change are the six citation range
corrections below and one added paragraph; all other prose and every quoted
line stay as they are.

## Citation corrections

| Footnote | Old range | New range | Evidence at v56.9.27.2 |
| --- | --- | --- | --- |
| 8 | `methodology/convergence.yaml#L413-L437` | `#L470-L472` | The bar-raise rule and the operator-approval sentence remain in this range. |
| 27 | `scripts/local-ci.sh#L390-L414` | `#L413-L418` | The check-weight table remains in this range. |
| 30 | `methodology/convergence.yaml#L340-L357` | `#L388-L392` | The complexity ratio and 5000-line red flag remain in this range. |
| 34 | `crates/tillandsias-plan/src/fragments.rs#L2971-L3005` | `#L3086-L3087` | The commutativity test remains in this range. |
| 43 | `scripts/local-ci.sh#L565-L569` | `#L571-L573` | The shell still delegates score arithmetic. |
| 45 | `scripts/local-ci.sh#L612-L620` | `#L624-L624` | The shell still reports a broken comparison regime. |

Six of the page's thirty-three in-repo citations moved; the other twenty-seven
resolve at the new pin without a line-number change, and every quoted line is
still present verbatim.

## D1 — what a closure does and does not buy

The CentiColon page argues how close a full set of centicolon closures brings the
methodology's promise. This page has already conceded the missing adjunction and
already recorded that closure in the obligation lattice implies nothing about the
program, but it never says what the closures are worth once that concession is
made. Add one paragraph after `It is bookkeeping over evidence, and is labelled
as such.`:

> A closure is one column of that lattice reaching its top. Worth saying plainly
> what that does and does not buy, because the site's centicolon page reads a
> full set of them as how close the methodology's promise now sits: close on the
> coverage axis, every obligation carried to $\texttt{evidence\_bundled}$, and no
> closer on the truth axis, because the step from lattice height to program
> behaviour is the adjunction the repository declines to define[^22]. What stays
> unproven after a closure is what stayed unproven before it: that the chosen
> obligation set is the right one[^4].

Justification: the paragraph introduces no new claim. Both sentences restate
the section's own argument and cite the two footnotes that already carry it —
[^22] records that no adjunction is defined between program semantics and spec
obligations, and [^4] is the repository's own statement that its result proves
monotonicity of the model, not truth of the modeled requirement or adequacy of
the chosen obligation set. It is the sharpest place the page can challenge the
framing without contradicting it.

## Out of scope

- The RED/PATH pair on the shell scorer's weights stays as it is: `check_weight`
  still maps CI check names to weights, the scorer still delegates its
  arithmetic, and neither was changed at this pin.
- The complexity-constraint RED stays RED: no enforcing implementation of the
  methodology-to-codebase ratio exists in the scripts at `v56.9.27.2`.
- The CentiColon Grader (`1395-88tp`) and the Advisory R line (`1395-ue3i`) did
  land in `scripts/local-ci.sh` between the pins, so the PATH line that already
  names them is now backed by gates rather than by the ledger alone. That is an
  improvement in enforcement, not a change in the claim, and needs no text.

These are source and quote checks at the tagged tree, not a live validation of
the mathematical model. External scholarly references are unchanged.
