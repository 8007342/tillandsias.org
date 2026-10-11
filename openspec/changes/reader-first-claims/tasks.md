# Tasks

## 1. Rules
- [x] 1.1 Add the reader rule and the plain no-remedy sentence to `docs/matrix/README.md`.
- [x] 1.2 Write the spec deltas under `specs/site/`.

## 2. Rendering
- [x] 2.1 Use the reader's words for the flag labels in `scripts/build-matrix.py`.
- [x] 2.2 Collapse each level's source list under "How we know", keeping the
      numbers in the text linked to their sources.
- [x] 2.3 Rewrite the home positioning line, the hero, the lede and the footer
      in plain words. Remove "folded through your hypervisor", which is false
      on Linux, and "nothing left behind", which is false while the cached
      image and models are kept.

## 3. Pages
- [x] 3.1 Level 1: take every block through the reader rule.
- [x] 3.2 Level 2: take every block through the reader rule.
- [x] 3.3 Level 3: plain PATH wording, the gate section rewritten, dated
      anecdotes removed, plan vocabulary translated in the labels.
- [x] 3.4 Level 4: meta NOTEs and developer-only REDs removed, PATH and label
      wording made plain.
- [x] 3.5 Level 5: apply D1 to D3, and nothing else.
- [x] 3.6 Remove the footnotes nothing references any more.

## 4. Verification
- [x] 4.1 Run the checked build (`skills/update-website/scripts/checked-build.sh`).
- [ ] 4.2 Re-check the Mac reset PATH ("a fix is being written") against the
      runtime at the next audit.
- [ ] 4.3 Operator review before archival. Archive `add-level-page-specs` first,
      or fold these deltas into it.
