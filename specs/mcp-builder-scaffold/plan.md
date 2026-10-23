# US-MCP-BUILDER-SCAFFOLD — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

`scaffold_package.py` and `connector_templates.py` wrote the package name into the manifest, the fingerprints, the server content and the ingest binding. The fleet uses the console script name.

## Architecture

The scaffold writes the fleet name once, as the SDK entry point. The manifest and fingerprints receive the same name. Runtime code resolves it through the SDK.
