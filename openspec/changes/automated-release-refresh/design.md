## The mechanical test

A citation `path#Lx-Ly` (with an optional quote) moves from tag A to tag B by
the first rule below that applies:

1. **ok.** At B the range still holds the quote. For an unquoted citation, the
   range holds the same lines it held at A.
2. **block.** The exact lines of the range at A occur exactly once in the file
   at B. The range shifts by the offset.
3. **quote.** The verbatim quote occurs exactly once in the file at B. The
   matching is whitespace-collapsed and accepts comment leaders, as the
   checked build does. The range keeps the context the author chose around
   the quote.
4. Otherwise the citation is a **judgement** item: the path is gone, the quote
   is gone, the text changed under an unquoted citation, or the match is
   ambiguous.

A level whose citations are all `ok`, `block` or `quote` moves. A level with
any judgement item keeps its pin. Its old citations are still true at the old
tag, so the site stays consistent while the item waits. A site-wide citation
(Big Graph, CentiColons) that cannot be re-anchored is held at its old tag by
an `@vTAG` suffix, so its link still lands on the text it was written against.

## What a mechanical move does not prove

A RED claims that something is absent. A fix can land beside an unchanged
quoted line, and the RED's evidence still resolves. The refresh therefore
asserts only that every cited text still exists at the new tag. It does not
assert that each claim is still the whole truth. The footnote note says when a
level's claims were last read by a person, and `review_queue` lists every flag
whose cited file changed.

## Why archive-gated

The operator's decision should be one act with a durable record. Archiving
this change is that act, and the gate reads it: `anchors.rule_accepted()`
looks for the change under `openspec/changes/archive/`.
