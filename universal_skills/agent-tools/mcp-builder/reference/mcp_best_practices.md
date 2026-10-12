# MCP design decisions

Follow the [SDK server contract](python_mcp_server.md) for ecosystem integration.
Check the current [MCP specification](https://modelcontextprotocol.io/specification/)
when protocol behavior affects the change.

- Keep tools focused, with stable names, bounded schemas, accurate descriptions
  and effect annotations. Follow existing connector naming.
- Respect explicit limits and the provider's pagination model. Return resumable
  cursors where available; do not load an entire service into memory.
- Return structured results for machine use. Add human representations when they
  help consumers; do not invent a second response mode for every endpoint.
- Use stdio for local processes and streamable HTTP for requested network
  deployments. Keep stdio logs on stderr.
- Apply SDK authentication, exposure, TLS and credential-reference boundaries.
  Tool annotations describe behavior; they never replace authorization.
- Sanitize and bound errors while preserving useful status/retry information.
  Test origin changes, redirects, oversized responses and invalid parameters.
- Publish prompts and resources through explicit ConnectorContent and test
  discovery. Do not infer served capabilities from package files alone.

Read-only task evaluations can supplement deterministic checks through
[the evaluation guide](evaluation.md), using an authorized fixture or service.
