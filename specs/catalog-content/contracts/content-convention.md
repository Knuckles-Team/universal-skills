# Contract: the content convention serves the catalog

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R071.1
Consumer: universal-skills US-CONTENT-R001

## Wire shape

- Declaration: the entry point `agent_connector_sdk.connector = "universal_skills"`.
- Served resource: one `skill://<name>/SKILL.md` per folder `universal_skills/skills/<name>/`.

## Refusal codes

- A second entry point or a provider group fails the conformance check.
- A skill outside the flat layout is not served and fails `tests/test_catalog_content.py`.

## Authoritative types

- `pyproject.toml` of this repository.
- The SDK content convention of `SCION-CONNECTOR-CONTROL-R071.1`.

## Test vectors

- `tests/test_catalog_content.py`.
