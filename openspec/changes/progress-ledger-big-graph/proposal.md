# A complete, inspectable website ledger and system map

## Why

Live progress currently renders only findings and gives each finding a short face. Readers cannot discover the canonical runtime specs, completed archived change checklists, or the evidence behind a finding from the page. Slide 6 deliberately compresses architecture into a presentation frame; a security reviewer needs the fuller target topology, its current gaps, and source links.

## What Changes

- Capture all canonical runtime specs and archived changes, including changes with no task record, at the site's release pin in a committed, deterministic snapshot.
- Render findings, specs, archived runtime changes and local website changes as collapsed, searchable records with full details and explicit status semantics.
- Add Big Graph as a fifth menu page and link to it from slide 6. Its map shows desired interactions and current implementation limits separately, with scroll, fixed-text-size spacing zoom, layer toggles and an inspector.
- Keep a plain Python and browser-native implementation so the generated site remains static and portable.

## Scope and limits

The snapshot is a release-pinned source inventory, not a live status feed. A checked archived task list is not evidence that every resulting behavior works now. Graph edges describe intended interactions; enforcement claims require the linked specs and the current stable audit. New runtime capabilities are not implemented by this website change.
