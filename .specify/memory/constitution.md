# Universal skills constitution

This repository inherits the [organization constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) version 1.0.0. Every article of that constitution applies here. This file adds only the rules and limits of this repository.

**Inherits**: organization constitution v1.0.0 | **Version**: 1.0.0 | **Ratified**: 2026-10-31 | **Last amended**: 2026-10-31

## Organization standards

- [Spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, computed states, `Spec:` trailers.
- [Ecosystem boundaries](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md): which repository owns which requirement.
- [Wording standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ste.md): sentences of 20 words or fewer, with `must`, `should`, or `may`.

## Repository articles

### R-I. A skill is atomic and portable

Each skill does one job, has valid portable frontmatter and a clear trigger. Skill content is free of private data.

**Enforced by:** Pre-commit hooks `check-atomicity`, `check-frontmatter-portability`, `skill-catalog-structure` and `security-sanitizer`.

**Plan check:** Does the skill do one job, with portable frontmatter and no private data?

### R-II. Paths are legal on every platform

Tracked paths stay within the path and name length limits below and hold no character that is illegal on a supported platform.

**Enforced by:** Pre-commit hook `check-path-portability` (`scripts/check_path_portability.py`).

**Plan check:** Do all new paths stay within the length limits?

### R-III. The connector scaffold is the only connector generator

The `mcp-builder` scaffold writes new connectors: one SDK dependency, one tool per API operation, fastmcp-native skills, prompts and resources, and the connector constitution. A connector copies none of the SDK or pipelines files.

**Enforced by:** `scripts/scaffold_connector.py` and `scripts/check_connector_contract.py` in the `mcp-builder` skill; the connector gates of pipelines.

**Plan check:** Does a new or regenerated connector come from the scaffold, with its constitution?

## Repository limits

The skill scaffold ships the organization KISS limits unchanged. These limits are specific to this repository.

| Limit | Value | Source |
|---|---|---|
| Path length | 200 | `.pre-commit-config.yaml` (`check-path-portability`) |
| File name length | 100 | `.pre-commit-config.yaml` (`check-path-portability`) |
| Path violations allowed | 0 | `.pre-commit-config.yaml` |

Amend this file in a reviewed change. State the impact in the pull request. When the organization constitution changes its version, update the **Inherits** line in the same change.
