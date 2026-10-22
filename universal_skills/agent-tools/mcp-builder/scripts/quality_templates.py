"""Consume reviewed pipeline contracts instead of copying their implementation."""

PIPELINES_THEME_REV = "3c6158a5fd7c938ed57347279401e0991c174448"

# Verbatim templates: GitHub expressions and YAML braces are not str.format input.
PRECOMMIT_CONFIG = """\
default_language_version:
  python: python3
default_install_hook_types: [pre-commit, pre-push]
default_stages: [pre-commit]

repos:
- repo: https://github.com/Knuckles-Team/pipelines
  rev: main
  hooks:
  # Shared scanner policy follows the approved pipelines main branch.
  # Use the reviewed, already-provisioned toolchain; hooks never install it.
  - id: scanner-versions
  - id: complexity-staged
  - id: kiss-staged
  - id: dupehound-changed
  - id: complexity-census
    stages: [pre-push]
  - id: kiss-census
    stages: [pre-push]
  - id: jscpd-differential
    stages: [pre-push]
  - id: jscpd-census
    stages: [pre-push]
  - id: public-surface
  - id: security-sanitizer
  - id: secret-history
  - id: supply-chain
  - id: import-cycles
  - id: env-sprawl
  - id: stdout-writes
  - id: swallowed-errors
  - id: event-loop-blocking
  - id: no-stub
  - id: spec-decomposition
  - id: spec-standard
  - id: spec-status
  # Inherit the upstream manual stage; ordinary code checks do not call it.
  - id: dependency-readiness

- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: 3e8a8703264a2f4a69428a0aa4dcb512790b2c8c
  hooks:
  - id: check-ast
  - id: check-yaml
    args: [--unsafe]
  - id: check-toml
  - id: check-json
  - id: check-merge-conflict
  - id: detect-private-key
  - id: trailing-whitespace
  - id: end-of-file-fixer

- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: 6fec9b7edb08fd9989088709d864a7826dc74e80
  hooks:
  - id: ruff-check
  - id: ruff-format

- repo: local
  hooks:
  - id: connector-sdk-contract
    name: SDK connector dependency and import contract
    entry: python scripts/check_connector_contract.py . --package __PACKAGE__
    language: system
    pass_filenames: false
    always_run: true
  - id: connector-tool-schemas
    name: Live SDK input and output schema contracts
    entry: python scripts/generate_tool_schemas.py --check
    language: system
    pass_filenames: false
    always_run: true
  - id: pytest
    name: Generated connector contracts
    entry: python -m pytest tests -q
    language: system
    pass_filenames: false
    always_run: true
    stages: [pre-push]
"""

SCANNER_CI_YML = """\
name: Connector quality

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  checks:
    # The runner supplies bootstrap Python, uv, pre-commit and approved scanners.
    # Prepare project dependencies separately; never build scanners here.
    runs-on: self-hosted
    env:
      MCP_FLEET_REGISTRATION: 'false'
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
        with:
          fetch-depth: 0
          persist-credentials: false
      - name: Capture provisioned hook runner
        shell: bash
        run: |
          hook_runner="$(realpath "$(command -v pre-commit)")"
          test -x "$hook_runner"
          echo "CONNECTOR_PRE_COMMIT=$hook_runner" >> "$GITHUB_ENV"
      - name: Select provisioned Python baseline
        run: python scripts/select_python.py
      - name: Prepare frozen project test environment
        run: '"$CONNECTOR_BOOTSTRAP_PYTHON" scripts/bootstrap_environment.py --github'
      - name: Validate hooks
        run: '"$CONNECTOR_PRE_COMMIT" validate-config'
      - name: Commit checks
        run: '"$CONNECTOR_PRE_COMMIT" run --all-files --show-diff-on-failure'
      - name: Push checks and generated connector tests
        env:
          PRE_COMMIT_FROM_REF: ${{ github.event.pull_request.base.sha || github.event.before }}
          PRE_COMMIT_TO_REF: ${{ github.event.pull_request.head.sha || github.sha }}
        run: '"$CONNECTOR_PRE_COMMIT" run --all-files --hook-stage pre-push --show-diff-on-failure'
"""

PIPELINE_YML = """\
name: Release Python package

on:
  push:
    tags: ['v*']

permissions:
  contents: read

jobs:
  publish-pypi:
    if: startsWith(github.ref, 'refs/tags/v')
    uses: Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main
    permissions:
      contents: write
    # Configure this existing publishing secret through the repository's
    # approved release process. The scaffold does not create credentials.
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
"""

PAGES_YML = """\
name: Deploy GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  publish-pages:
    uses: Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main
    with:
      content_source: docs
      shared_theme_enabled: true
      agent_readiness_enabled: true
      readiness_input: docs/agent-readiness.json
      readiness_schema: docs/agent-readiness.schema.json
      spec_dashboard_enabled: true
      spec_dashboard_config: .config/spec-dashboard.json
    permissions:
      contents: read
      pages: write
      id-token: write
"""

SPEC_DASHBOARD_CONFIG = """\
{
  "version": 1,
  "sources": [{"glob": "specs/*/status.json", "kind": "spec"}]
}
"""

SPEC_DELIVERY_MD = """\
# Spec delivery

[Open the published delivery dashboard](https://knuckles-team.github.io/{package_name}/spec-delivery/).

The shared Pages pipeline builds this dashboard from canonical
`specs/*/status.json` files selected by `.config/spec-dashboard.json`.
The repository owns the source configuration; the pinned shared pipeline owns
rendering and validation. Update source specs through the reviewed spec process.

The starter capability is **SPECIFIED** with empty delivery receipts. Missing or
unverified evidence does not establish delivery, release, or deployment.
Regenerate status with the shared `pipelines-hook spec-status --write` command
after reviewed implementation commits and test bindings exist; commit the
resulting source status. Read the [spec index](https://github.com/Knuckles-Team/{package_name}/blob/main/specs/README.md)
and [architecture](architecture.md) for source mappings and declared dependencies.
The dashboard is a build-time snapshot, refreshed on every push to main or an
explicit Pages workflow run. Agent readiness uses the separate canonical
`docs/agent-readiness.json` and its packaged schema.
"""

# Scanner versions and thresholds are owned by the pinned pipelines package.
# Consumers only declare package/scope inputs under [tool.pipelines_hooks].
PYPROJECT_SCANNERS = ""
