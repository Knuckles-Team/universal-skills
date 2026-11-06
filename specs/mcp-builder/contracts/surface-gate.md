# Contract — surface-gate

Provider: pipelines PIPE-GATES-R014
Consumer: universal-skills US-MCP-BUILDER-R011.16

## Wire shape

`pipelines-hook connector-surface-audit --root <repo> --strict` reads one connector checkout and prints JSON with one record under `connectors`. The record holds `complete` and a `gaps` list. The scaffold output must yield `complete: true` and exit 0.

## Refusal codes

Exit 1 means at least one gap, such as a missing surface element or ontology part. Exit 2 means the gate cannot produce a verdict.

## Authoritative types

[`pipelines_hooks/hygiene/connector_surface.py`](https://github.com/Knuckles-Team/pipelines/blob/main/pipelines_hooks/hygiene/connector_surface.py) produces the record.

## Test vectors

[`tests/test_mcp_builder_connector_scaffold.py`](https://github.com/Knuckles-Team/universal-skills/blob/main/tests/test_mcp_builder_connector_scaffold.py) runs the gate on a generated connector.
