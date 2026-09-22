# Design

`scripts/snapshot-specs.py` reads one numbered-tag checkout and writes `docs/progress/runtime-specs.json`. It includes archived change directories even when no task file exists, marking that absence. The build rejects a snapshot with a different pin. Normal builds consume the committed JSON and local OpenSpec task files, so no network or runtime checkout is needed to render the ledger. The separate checked-build gate still validates the site's line citations against tagged sources.

`scripts/progress.py` renders the folded findings, every canonical spec and every archived change task record. Native `details/summary` elements keep all entries collapsed without JavaScript. Search only hides rendered records; source content remains in the HTML. The summary avoids treating document status or checked tasks as measured runtime completion.

`scripts/big_graph.py` holds a declarative component and interaction list. The graph canvas uses absolute positions for cards and SVG connector paths. The spacing control changes coordinates and canvas bounds, while card width and CSS font sizes stay constant. At greater spacing the cards show additional explanation; clicking opens an inspector with limitations, interactions and release-pinned spec links. Layer toggles hide related cards and edges. On a narrow screen the inspector moves below the map.

The graph deliberately includes planned boundaries in gray/dotted styling and partial ones in amber/dashed styling. The stable audit is the source for current-state labels. The pinned runtime specs are sources for target behavior. Every referenced slug is checked against the tagged checkout during this change.
