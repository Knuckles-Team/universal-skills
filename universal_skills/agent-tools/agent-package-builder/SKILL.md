---
name: agent-package-builder
domain: agent-tools
skill_type: skill
description: >-
  Scaffold a new Agent Utilities provider package with a governed API client,
  intent-routed MCP server, optional agent runtime, mandatory full epistemic-graph,
  reference-only AgentConfig, portable TLS profiles, documentation, and release gates.
  Use for brand-new provider packages; use focused builder skills for existing repos.
license: MIT
tags: [agent, package, scaffold, mcp, api-client, agentconfig, tls]
metadata:
  version: '1.2.1'
---

# Agent Package Builder

Create one current Agent Utilities provider package without carrying deployment,
identity, endpoint, credential, certificate, or host-specific assumptions into source.
The definitive generated-file contract is
[`PARITY_MANIFEST.md`](PARITY_MANIFEST.md).

## Invocation

```bash
python3 scripts/scaffold_package.py <package-name> \
  [--type api_client,mcp,agent[,graphql]] \
  [--display-name ...] [--description ...] \
  [--concept-prefix XYZ] [--output-dir ...] [--in-place]
```

The generator never requests or writes a person's name or email. It does not generate
a `.env` file, connection profile, credential value, certificate path, deployment
hostname, or customized ontology. Provider-specific values are operator inputs resolved
from `AgentConfig` only at runtime.

## Workflow

### 1. Gather requirements

Collect only:

| Input | Required | Default |
|---|---:|---|
| package name | yes | — |
| display name | no | derived from package name |
| one-line description | no | generated |
| package types | no | `api_client,mcp,agent` |
| unique concept prefix | no | derived, then collision-checked |
| output directory | no | current directory |

Check distribution-name availability before publishing. Network access and creation of
remote repositories are separate, explicit operator actions; scaffolding itself is local.

### 2. Scaffold

Run the script and generate `uv.lock` with the repository's normal dependency workflow.
The scaffold includes:

- current Python packaging, immutable supply-chain workflows, and pre-commit gates;
- one canonical `api/` package—no facade alias or compatibility layer;
- one intent-routed MCP surface with an optional verbose operation surface;
- one A2A agent entry point using `agent-runtime`;
- provider-contributed skills, prompts, ontology, and source-connector presets;
- mandatory native knowledge-graph ingestion backed by `epistemic-graph[full]`;
- a strict MkDocs site and generated deployment/readme markers;
- least-privilege container and runtime configuration templates.

### 3. Enforce the dependency contract

Every generated distribution uses bounded current ranges:

```toml
[project]
dependencies = [
  "agent-utilities[mcp]>=1.27.1,<2.0.0",
  "epistemic-graph[full]>=2.23.1,<3.0.0",
]

[project.optional-dependencies]
mcp = ["agent-utilities[mcp]>=1.27.1,<2.0.0"]
agent = ["agent-utilities[agent-runtime,logfire]>=1.27.1,<2.0.0"]
all = ["agent-utilities[mcp,agent-runtime,logfire]>=1.27.1,<2.0.0"]
```

GraphQL packages add `gql[requests]>=4.0.0` directly to the applicable dependency
lists. The `all` extra must never reference the package itself. Both MCP and agent
images contain the mandatory full graph engine; the MCP target omits only the optional
agent orchestration stack.

### 4. Use reference-only provider configuration

`auth.py` resolves a named `provider_configs.<provider>` profile through
`resolve_provider_runtime_profile`. Durable configuration contains references only:

```json
{
  "provider_configs": {
    "provider-name": {
      "enabled": true,
      "endpoint_ref": "env://PROVIDER_ENDPOINT_RUNTIME",
      "credential_refs": {"token": "env://PROVIDER_TOKEN_RUNTIME"},
      "tls_profile": "provider-trust"
    }
  }
}
```

This shape illustrates reference syntax, not values to commit. A secret provider may
replace the `env://` references. Use either `tls_profile` or `tls_profile_ref`, never a
boolean verification switch. `ResolvedTLSProfile` supplies CA chains, mTLS, system
trust, proxy policy, and library-specific adapters while preserving hostname and peer
verification. Resolved material must not enter logs, traces, reports, or generated JSON.

OIDC token exchange uses the MCP/OIDC runtime profile; it must not reuse a downstream
provider's TLS profile. Fixed provider tokens are the referenced fallback.

### 5. Build the API and GraphQL clients

- Validate the configured base URL, reject embedded credentials, and restrict cleartext
  HTTP to loopback through the shared provider-runtime resolver.
- Keep request paths on the configured origin; disable redirects.
- Apply finite time and response-size limits.
- Pass `ResolvedTLSProfile` to all HTTP transports; never accept `verify=False` or a
  raw `SSL_VERIFY` setting.
- Keep `api/` as the only public client module. Do not generate legacy import aliases.
- For GraphQL, use the same TLS profile and bounded input/response behavior. Partial
  error handling must be explicit per operation.

### 6. Build the MCP and agent surfaces

`mcp_server.py` calls `load_config()`, `create_mcp_server()`, and exactly one
`register_tool_surface(...)`. `MCP_TOOL_MODE=intent` is the default; `verbose` is the
explicit operation surface. Do not generate retired mode aliases or per-domain mode
branches.

Each domain lives in `mcp/mcp_<domain>.py`, exposes one bounded action router, uses
lowercase hyphenated tags, validates parameters, and carries a concept ID. Add domains
by exporting `register_<domain>_tools` from `mcp/__init__.py`; the shared registrar
discovers them.

The agent entry point uses the `agent-runtime` extra and canonical prompt schema. Agent
instructions, skills, and provider configuration remain package data—not process-local
paths.

### 7. Contribute native knowledge

Every package ships:

- an OWL/RDF module containing only the provider's out-of-the-box domain model;
- a native ingestion mapper for typed entities, documents, and applicable media;
- at least one atomic, provider-prefixed skill;
- a domain-specialist structured prompt;
- neutral source-connector presets that require operator mapping before use.

The full engine is mandatory, so ingestion imports the shared native primitive directly.
Do not add a no-engine compatibility path. Never embed a customized deployment schema;
consume a discovered schema or generate a mapping policy at runtime.

### 8. Generate secure deployment documentation

Local MCP usage defaults to stdio or loopback. A local container runs as a
least-privilege stdio child with a reviewed immutable digest, read-only filesystem,
dropped capabilities, no-new-privileges, bounded PIDs, and no published port.

Network MCP is documented only behind direct TLS or an operator-owned authenticated
HTTPS ingress with exact `MCP_ALLOWED_HOSTS` and trusted-proxy policy. Endpoint,
credential, identity, and TLS-profile references live in `AgentConfig`. Generated docs
must not assume a particular proxy, DNS domain, certificate authority, filesystem, or
orchestrator.

Compose templates mount an operator-selected AgentConfig directory read-only and never
load a generated `.env` file. Container inputs use immutable digests.

### 9. Validate before handoff

Run the repository's deterministic, non-network gates:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python -m mkdocs build --strict
python -m agent_utilities.mcp.check_env_var_drift --check
python -m agent_utilities.mcp.readme_mcp_examples --check
```

Also verify:

- every file in `PARITY_MANIFEST.md` exists;
- generated blocks are idempotent;
- dependency metadata contains current bounded ranges and mandatory
  `epistemic-graph[full]`;
- no recursive extra, legacy alias, generated `.env`, raw credential, verification
  boolean, mutable image tag, environment endpoint, personal identifier, or real local
  path appears;
- documentation links resolve and MkDocs has no orphaned pages;
- skills pass atomicity, frontmatter portability, privacy, and direct-execution tests.

Do not publish, push, deploy, or create remote resources without the user's explicit
authorization.
