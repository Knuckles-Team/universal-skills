# US-MCP-BUILDER quickstart

Run the proofs from the repository root.

## Scaffold tests

```bash
uv run pytest tests/test_mcp_builder_connector_scaffold.py
```

Expected: the generated tree, determinism, workflow, ontology, gate and conformance tests pass.

## Generate a connector by hand

```bash
python3 universal_skills/skills/mcp-builder/scripts/scaffold_connector.py example-mcp --output-dir "$(mktemp -d)"
```

Expected: the script prints the number of files written and the two gate commands to run before the first push.
