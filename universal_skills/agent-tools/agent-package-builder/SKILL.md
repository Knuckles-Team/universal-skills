---
name: agent-package-builder
description: >-
  Scaffold a complete agent-package project with all config files, Docker
  infrastructure, MCP server, A2A agent, and API client stubs. Use when creating a
  brand-new agent-package from scratch, bootstrapping a new MCP/agent/api-client
  project, or when the user says "create a new agent package". This delegates
  domain-specific implementation to existing skills (api-client-builder, mcp-
  builder, agent-builder, skill-graph-builder). Do NOT use for modifying an
  existing agent package — use the individual skills directly.
license: MIT
tags: [agent, package, scaffold, bootstrap, project, mcp, api-client, builder]
metadata:
  author: Genius
  version: '0.31.0'
---

# Agent Package Builder

Scaffolds a complete, production-ready agent-package project following the standardized ecosystem conventions. The generated project includes all hidden config files (`.pre-commit-config.yaml`, `.bumpversion.cfg`, `.gitignore`, `.gitattributes`, `.env`, `.dockerignore`), Docker infrastructure (`docker/Dockerfile`, `docker/debug.Dockerfile`, `docker/compose.yml`, `docker/mcp.compose.yml`), Python packaging (`pyproject.toml`, `requirements.txt`), documentation (`README.md`, `CHANGELOG.md`, `AGENTS.md`, `docs/`), and agent workspace files (`prompts/main_agent.md`). All state, logs, memory, and chat history are handled natively via the **Knowledge Graph**.

---

## Workflow

### Step 1: gather-requirements

Collect the following from the user. Ask only for what is missing — do not re-ask for values already provided.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `package-name` | ✅ | — | Kebab-case name (e.g., `jellyfin-mcp`) |
| `--display-name` | ❌ | Derived from package name | Human-readable name (e.g., `Jellyfin MCP`) |
| `--description` | ❌ | `"Agent package for {display_name}"` | One-line description |
| `--type` | ❌ | `api_client,mcp,agent` | Comma-separated: `api_client`, `mcp`, `agent` |
| `--output-dir` | ❌ | Current directory | Where to create the project |
| `--author` | ❌ | `"Audel Rouhi"` | Author name |
| `--email` | ❌ | `"knucklessg1@gmail.com"` | Author email |
| `--service-url-env` | ❌ | `"{UPPER_NAME}_URL"` | Env var for the service URL |
| `--auth-env` | ❌ | `"{UPPER_NAME}_TOKEN"` | Env var for the auth token |
| `--concept-prefix` | ❌ | Derived from name | Unique CONCEPT ID prefix (e.g., `PORT` for portainer) |
| `--doc-urls` | ❌ | — | Comma-separated documentation URLs for skill-graph |

### Step 2: scaffold-tree [depends_on: gather-requirements]

Generate the complete directory tree. The standard project structure is:

```
{project_dir}/
├── .bumpversion.cfg
├── .dockerignore
├── .env
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── docker/
│   ├── Dockerfile
│   ├── debug.Dockerfile
│   ├── compose.yml
│   └── mcp.compose.yml
├── docs/
│   ├── index.md              # Navigation hub
│   ├── overview.md            # Full technical overview
│   └── concepts.md            # CONCEPT ID registry
├── prompts/
│   └── main_agent.md
├── tests/
│   ├── conftest.py
│   ├── test_init_dynamics.py
│   ├── test_auth.py
│   ├── test_mcp_handlers.py
│   ├── test_mcp_registration.py
│   ├── test_api_client.py
│   ├── test_agent_integration.py
│   ├── test_concept_parity.py
│   └── test_startup.py
└── {pkg_dir}/
    ├── __init__.py
    ├── __main__.py
    ├── agent_server.py
    ├── auth.py
    ├── mcp_server.py           # Entrypoint (imports from mcp/)
    ├── api_client.py            # Facade re-export from api/
    ├── models.py
    ├── mcp_config.json
    ├── api/
    │   ├── __init__.py
    │   ├── api_client_base.py
    │   └── api_client_{domain}.py
    ├── mcp/
    │   ├── __init__.py
    │   └── mcp_{domain}.py
    └── agent_data/
        └── IDENTITY.md
```

### Step 3: api-client [depends_on: scaffold-tree]

Read the `api-client-builder` skill and follow its instructions to:
1. Populate `{pkg_dir}/api/` sub-package:
   - `{pkg_dir}/api/api_client_base.py` — The HTTP/REST client base wrapper.
   - `{pkg_dir}/api/api_client_{domain}.py` — Domain-specific subclasses with API endpoint methods.
   - `{pkg_dir}/api/__init__.py` — Expose base and domain clients.
2. Create `{pkg_dir}/api_client.py` — **Facade file** that re-exports from `api/` for backward compatibility.
3. Create `{pkg_dir}/models.py` — Pydantic input/output models for standard API schemas.
4. Update `{pkg_dir}/auth.py` — Configure authentication using **standard env var names**:
   - `{SERVICE}_URL` — Service endpoint (NOT `_BASE_URL` or `_INSTANCE`)
   - `{SERVICE}_TOKEN` — API token (NOT `_API_KEY`)
   - `{SERVICE}_SSL_VERIFY` — TLS verification (NOT `_VERIFY` or `_AGENT_VERIFY`)
   - `{SERVICE}_USERNAME` / `{SERVICE}_PASSWORD` — For basic auth

### Step 4: mcp-server [depends_on: scaffold-tree]

Read the `mcp-builder` skill and follow its instructions to:
1. Implement modular tool registrations inside `{pkg_dir}/mcp/` sub-package:
   - `{pkg_dir}/mcp/mcp_{domain}.py` — Houses dynamic action-routed tools per domain tag.
   - `{pkg_dir}/mcp/__init__.py` — Expose `register_{domain}_tools` functions.
2. Implement `{pkg_dir}/mcp_server.py` as the entrypoint:
   - Import `register_*_tools` from `{pkg_dir}/mcp/`
   - Gate each domain with env var toggles: `DEFAULT_{DOMAIN}TOOL`
   - Add CONCEPT ID to tool descriptions (e.g., `CONCEPT:{PREFIX}-001`)
3. **Tag Rules**: All MCP tool tags MUST be strictly lowercase with hyphens (e.g. `tag="user-management"`). No camelCase or underscores.
4. **Action-Routed Dynamic Generation**: ALL new agents use dynamic runtime generation. No monolithic static `@mcp.tool` files.
5. **Field Optimization**: All parameters use `pydantic.Field(default=..., description=...)`. No positional args in Field().

### Step 5: agent-server [depends_on: scaffold-tree]

Read the `agent-builder` skill and follow its instructions to:
1. Configure `{pkg_dir}/agent_server.py` with proper identity loading.
2. Update `{pkg_dir}/agent_data/IDENTITY.md` with standard YAML frontmatter.
3. Suppress known fastmcp/urllib3 warnings, print startup telemetry to `sys.stderr`.
4. Create `{pkg_dir}/__main__.py` invoking `agent_server()`.

### Step 6: docs-generation [depends_on: api-client, mcp-server, agent-server]

Generate all required documentation:

#### 6a. docs/concepts.md (REQUIRED)
Every project must have a CONCEPT ID registry:
```markdown
# Concept Registry — {package-name}

> **Prefix**: `CONCEPT:{PREFIX}-*`
> **Bridge**: `CONCEPT:ECO-4.0` (Unified Toolkit Ingestion)

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:{PREFIX}-001` | {Domain 1} | MCP tool domain `{tag}` |
| `CONCEPT:{PREFIX}-002` | {Domain 2} | MCP tool domain `{tag}` |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |
```

#### 6b. docs/overview.md
Standard technical overview with architecture, tool descriptions, and concept references.

#### 6c. docs/index.md
Navigation hub linking to all other docs.

#### 6d. CHANGELOG.md

### Step 7: verify-build [depends_on: docs-generation]

Validate build syntax and entry points:
- **Validate syntax**: Run syntax checking `python -c "import tomllib; ..."`
- **Test entry points**: Run dynamic verification helper `pip install -e . && python -m {pkg_dir}.mcp --help`

### Step 8: run-pre-commit [depends_on: verify-build]

Run all formatting and style hooks across the scaffold:
- **Run pre-commit**: `pre-commit run --all-files`

### Step 9: drift-check [depends_on: run-pre-commit]

Run a drift audit against the ecosystem standard to confirm 100% compliance before marking the package as complete. This ensures no files were missed and all conventions are met.

```bash
cd {project_dir} && echo "=== Drift Audit ===" \
  && for f in README.md CHANGELOG.md AGENTS.md pyproject.toml requirements.txt \
    .pre-commit-config.yaml .bumpversion.cfg .gitignore .gitattributes \
    .dockerignore .env mcp_config.json; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docs/index.md docs/overview.md docs/concepts.md; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docker/Dockerfile docker/compose.yml; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in {pkg_dir}/__init__.py {pkg_dir}/__main__.py {pkg_dir}/mcp_server.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && [ -d "{pkg_dir}/mcp" ] && echo "✅ mcp/ subdir" || echo "❌ mcp/ MISSING" \
  && for f in tests/conftest.py tests/test_concept_parity.py \
    tests/test_init_dynamics.py tests/test_startup.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && grep -q "ECO-4.0" docs/concepts.md && echo "✅ ECO-4.0 bridge" \
    || echo "❌ ECO-4.0 bridge MISSING"
```

If ANY item shows ❌, fix it before completing the build. The `ecosystem_standardizer` workflow can also be run for a deeper audit with scoring.
```
Trigger: "run ecosystem standardizer" with scope={package-name}
```

> [!IMPORTANT]
> A new package is not complete until it passes the drift check with 0 missing items. This is a hard gate.

## Environment Variable Standard

All new agent packages MUST use these naming patterns:

| Pattern | Example | Notes |
|---------|---------|-------|
| `{SERVICE}_URL` | `PORTAINER_URL` | NOT `_BASE_URL` or `_INSTANCE` |
| `{SERVICE}_TOKEN` | `PORTAINER_TOKEN` | Prefer over `_API_KEY` |
| `{SERVICE}_SSL_VERIFY` | `PORTAINER_SSL_VERIFY` | NOT `_VERIFY` or `_AGENT_VERIFY` |
| `{SERVICE}_USERNAME` | `PORTAINER_USERNAME` | For basic auth |
| `{SERVICE}_PASSWORD` | `PORTAINER_PASSWORD` | For basic auth |

Preserve first-party env var names when they exist (e.g., `GITHUB_TOKEN`, `LANGFUSE_PUBLIC_KEY`).

## CONCEPT ID Prefix Registry

When assigning a prefix, check this registry to avoid collisions:

| Prefix | Project | | Prefix | Project |
|--------|---------|---|--------|---------|
| `ABOX` | archivebox-api | | `ARR` | arr-mcp |
| `ATL` | atlassian-agent | | `AU` | agent-utilities |
| `ANSIBLE` | ansible-tower-mcp | | `AUDIO` | audio-transcriber |
| `CMGR` | container-manager-mcp | | `DSCI` | data-science-mcp |
| `EE` | emerald-exchange | | `GENIUS` | genius-agent |
| `GH` | github-agent | | `GL` | gitlab-api |
| `HASS` | home-assistant-agent | | `JELLYFIN` | jellyfin-mcp |
| `LF` | langfuse-agent | | `LIX` | leanix-agent |
| `LM` | listmonk-api | | `MEAL` | mealie-mcp |
| `MDLD` | media-downloader | | `MSFT` | microsoft-agent |
| `NC` | nextcloud-agent | | `OC` | owncast-agent |
| `PA` | postiz-agent | | `PLANE` | plane-agent |
| `PORT` | portainer-agent | | `QBT` | qbittorrent-agent |
| `RM` | repository-manager | | `SNOW` | servicenow-api |
| `SRX` | searxng-mcp | | `SX` | scholarx |
| `SYS` | systems-manager | | `STIRLINGPDF` | stirlingpdf-agent |
| `TUI` | agent-terminal-ui | | `TUN` | tunnel-manager |
| `UKA` | uptime-kuma-agent | | `VEC` | vector-mcp |
| `WEBUI` | agent-webui | | `WGER` | wger-agent |
