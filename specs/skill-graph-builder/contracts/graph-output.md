# Seam: graph output

Provider: universal-skills US-SKILL-GRAPH-BUILDER-R003
Consumer: skill-graphs SG-CONTENT-R002

## Wire shape

A folder `<name>-docs` with `SKILL.md` (`skill_type: graph`), `index.json`, `sources.json` and a flat `reference/<hash>.md`, plus an optional `ontology/<name>-docs.ttl`. Field lists are in the `SG-CONTENT` data model.

## Refusal codes

None. The builder exits non-zero with a message. The consumer gate names each violation.

## Authoritative types

`SOURCES_SCHEMA` and `SOURCE_KINDS` in `scripts/validate_skill_graphs.py` of `skill-graphs`.

## Test vectors

`tests/test_validate_skill_graphs.py` of `skill-graphs` and `tests/test_skill_graph_builder.py` here.
