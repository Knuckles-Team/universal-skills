# US-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The SDK finds content by convention under the package named by its `agent_connector_sdk.connector` entry point and serves `skills/<name>/SKILL.md` through fastmcp's `SkillsDirectoryProvider`. This package adds no server code.

## Architecture

`universal_skills/skills/<name>/SKILL.md` plus supporting files in the same folder. The SDK builds the server and the pytest plugin generates the conformance checks.

## Interfaces and data model

The only interface is the entry point `universal-skills = "universal_skills"`. Layout follows fastmcp's `SkillsDirectoryProvider`, which wins over the raw MCP spec.

## Upstream skill sources

`upstream-sources.toml` pins each source at a full commit SHA. `scripts/sync_upstream_skills.py` fetches the pin into a throwaway git repository, reads blobs with `cat-file` and never runs them. It stores a pristine snapshot in `universal_skills/upstream/<source>/`, renders each skill into `universal_skills/skills/<name>/` and merges `universal_skills/overlays/<name>/*.md` after the render. The pre-commit hook runs `--check` offline against the snapshot, so a hand edit to a vendored file fails the commit. `--update` moves the pin; the `universal-installer` skill carries the procedure.

## Live integration path

arbora resolves the installed distribution through the entry point and serves its skills.

## Quality and release gates

The repository pre-commit hooks, `tests/test_catalog_content.py` and the SDK plugin checks must pass.

## Risks, alternatives, and decisions

Hard cutover: the former nested category layout and the `agent_utilities.skill_providers` entry point are gone, with no compatibility path. A skill's category is its `domain`/metadata, not a directory.
