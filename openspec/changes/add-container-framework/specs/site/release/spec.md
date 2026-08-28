## ADDED Requirements

### Requirement: Versioned durable release artifact
The project MUST produce a durable release artifact: a zip bundle of the static
site contents under `var/html/`. The image MUST consume this versioned bundle
for reproducible releases.

#### Scenario: Produce site zip
- **WHEN** a versioned release is cut
- **THEN** a zip of the `var/html/` contents is produced as a durable release
  artifact

#### Scenario: Image consumes the bundle
- **WHEN** the image is built for a release
- **THEN** it consumes the versioned zip bundle rather than ad-hoc files

### Requirement: Monotonic version scheme
Release versions MUST follow the scheme `v<Major>.<Minor>.<YYMMDD>.<DailyBuild>`
so that versions are monotonically incremental (e.g. `v1.0.260827.1`).

#### Scenario: Version ordering
- **WHEN** two releases are cut on the same day
- **THEN** the second has a higher <DailyBuild> than the first

#### Scenario: Version format
- **WHEN** a release is versioned
- **THEN** its tag is formatted as v<Major>.<Minor>.<YYMMDD>.<DailyBuild>

### Requirement: Development mount
During development the container MUST be able to mount `./var/html` directly as
the document root, without a release bundle.

#### Scenario: Development mount
- **WHEN** running in development
- **THEN** `./var/html` is mounted into the container and served

### Requirement: Placeholder content
The project MUST initialize `var/html/` with a simple `index.html` so the
container can launch and serve, pending a richer front-end.

#### Scenario: Container serves placeholder
- **WHEN** a fresh container serves the site
- **THEN** it returns the placeholder `index.html`
