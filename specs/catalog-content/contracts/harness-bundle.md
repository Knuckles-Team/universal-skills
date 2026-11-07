# Harness bundle

Seam between `US-CONTENT` and arbora. Owner rows: `US-CONTENT-R007` in this repository and `ARBORA-HARNESS-PLUGINS-R001.2` in arbora.

Provider: universal-skills US-CONTENT-R007
Consumer: arbora ARBORA-HARNESS-PLUGINS-R001.2

## Wire shape

The package serves `skill://<name>/SKILL.md` for each skill folder through the SDK content convention. Arbora reads `arbora-door`, `session-handoff` and each skill of its declared list. It copies each folder unchanged into the bundle tree. Each frontmatter holds `name`, `description` and keys under `metadata` only.

## Refusal codes

- `SKILL_NOT_PORTABLE`: the frontmatter fails the strictest contract; arbora refuses the bundle.
- `SKILL_MISSING`: a declared skill folder is absent.

## Test vectors

- `tests/test_harness_portable_skills.py::test_every_skill_frontmatter_is_portable`.
