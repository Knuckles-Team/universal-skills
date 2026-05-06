---
name: agent-package-builder
description: Scaffold a complete agent-package project with all config files, Docker infrastructure, MCP server, A2A agent, and API client stubs. Use when creating a brand-new agent-package from scratch, bootstrapping a new MCP/agent/api-client project, or when the user says "create a new agent package". This delegates domain-specific implementation to existing skills (api-client-builder, mcp-builder, agent-builder, skill-graph-builder). Do NOT use for modifying an existing agent package — use the individual skills directly.
tags: [agent, package, scaffold, bootstrap, project, mcp, api-client, builder]
version: '0.6.0'
---

# Agent Package Builder

Scaffolds a complete, production-ready agent-package project matching the `jellyfin-mcp` gold standard. The generated project includes all hidden config files (`.pre-commit-config.yaml`, `.bumpversion.cfg`, `.gitignore`, `.gitattributes`, `.env`, `.dockerignore`), Docker infrastructure (`Dockerfile`, `debug.Dockerfile`, `compose.yml`), Python packaging (`pyproject.toml`, `requirements.txt`), and agent workspace files (`prompts/main_agent.md`). Flat-file logging, memory, and local data storage (`MEMORY.md`, `USER.md`, `HEARTBEAT.md`, `CRON.md`, `agent_data/`) have been deprecated; all state, logs, memory, and chat history are handled natively via the **Knowledge Graph**. It also includes a best-in-class `AGENTS.md` in the project root to optimize for AI coding tools.

---

## Workflow

### Phase 1: Gather Requirements

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
| `--doc-urls` | ❌ | — | Comma-separated documentation URLs for skill-graph |

### Phase 2: Scaffold the Project

Run the scaffolding script to generate the full project:

```bash
python scripts/scaffold_package.py <package-name> \
  --output-dir <path> \
  --type <types> \
  --display-name "<name>" \
  --description "<desc>" \
  --author "<author>" \
  --email "<email>" \
  --service-url-env "<env>" \
  --auth-env "<env>"
```

This generates the complete directory tree with all config files, Docker files, Python package stubs, and agent workspace files.

### Phase 3: Build Domain Logic

After scaffolding, implement the domain-specific code by delegating to the appropriate existing skills. Follow the skills in order:

#### 3a. API Client (if type includes `api_client`)

Read the `api-client-builder` skill and follow its instructions to:
1. Create `{pkg_dir}/api_client.py` — The API client class.
2. Create `{pkg_dir}/models.py` — Pydantic input/output models.
3. Update `{pkg_dir}/auth.py` — Configure authentication for the target service. Ensure you follow the standardized pattern: wrap API instantiation in a `try...except (AuthError, UnauthorizedError)` block and raise a descriptive `RuntimeError` with troubleshooting advice.

#### 3b. MCP Server (if type includes `mcp`)

Read the `mcp-builder` skill and follow its instructions to:
1. Implement tool registrations in `{pkg_dir}/mcp_server.py`.
2. Wire tools to the API wrapper methods created in 3a.
3. Register tools by tag with env-var-based enable/disable pattern.
4. **IMPORTANT**: All MCP tool tags MUST be strictly lowercase and use hyphens to separate words (e.g. `tag="user-management"`, env var=`USER_MANAGEMENTTOOL`). No camelCase or underscores are allowed in tags.
5. **Scale Pattern (Option 3)**: For agents with >50 API calls (e.g. `arr-mcp`, `leanix-agent`), use **Dynamic Runtime Generation**.
   - **Tag Prefixing**: For Option 3, prefix tool tags with the API/Service name (e.g. `leanix-pathfinder`).
   - **No Duplicates**: Ensure tool tags are unique across the entire registration.
   - Do not write massive `mcp_server.py` files with hundreds of static `@mcp.tool` decorators.
   - Use metaprogramming (e.g. `exec()` mapping python method signatures to FastMCP Pydantic schemas) similar to the `arr-mcp` pattern.
   - Feed the router a `tool_tags.json` mapping of `{"service": {"method_name": "lowercasetag"}}`.
   - **CRITICAL**: Even when dynamically generating tools, you MUST explicitly define static environment variables for *each* tag block in `mcp_server.py` so the users can clearly see and disable them:
     ```python
     DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
     if DEFAULT_MISCTOOL:
         register_misc_tools(mcp)
     ```
     For a purely dynamic loading loop, you should still hardcode the env variables checking before enabling specific categories inside the dynamic router or at the server root.

#### 3c. Agent (if type includes `agent`)

Read the `agent-builder` skill and follow its instructions to:
1. Configure `{pkg_dir}/agent_server.py` with proper identity loading.
2. Update `{pkg_dir}/prompts/main_agent.md` with the new standard frontmatter:
   - The agent's `name`, `type`, `skills`, and `description` in the YAML frontmatter.
   - Instructions to run `list_skills` first in the markdown body.
   - Instructions to use the `mcp-client` skill and check `{package_name}.md` reference.
3. Configure the graph execution tools to log telemetry and cron tasks directly to the **Knowledge Graph** (no `CRON.md` or `HEARTBEAT.md`).
4. Ensure the root directory contains `icon.png` (moved from agent_data). Long-term memory is managed via the **Knowledge Graph** tool suite (`search_knowledge_graph`, `add_knowledge_memory`, etc.). A standardized `{pkg_dir}/__main__.py` will also be created to invoke the agent server.

#### 3d. GraphQL Wrapper (if type includes `graphql`)

Read the `api-client-builder` skill (Step 5 — GraphQL) and follow its instructions to:
1. Customize `{pkg_dir}/gql_client.py` — The GraphQL client class (stub generated by scaffold).
2. Adjust the GraphQL endpoint path in `__init__` (e.g., `/api/graphql`, `/graphql`).
3. Implement domain-specific query and mutation methods mirroring the REST API wrapper.
4. Use cursor-based pagination (`first`/`after`) for list queries.

#### 3e. Graph Agent (for agents with ≥3 tool tags)

Agents with many tool tags benefit from **graph orchestration** — a pydantic-graph based router that classifies queries and executes them with only the relevant domain tools loaded, saving LLM context.

**Upgrade Criteria:**
| Tag Count | Action |
|-----------|--------|
| ≥10 tags | Strongly recommended |
| 5–9 tags | Recommended |
| 3–4 tags | Optional |
| ≤2 tags | Do not upgrade |

**Implementation requires only 2 files:**

1. **Create `{pkg_dir}/graph_config.py`** — Maps each tag to a domain prompt and env var:
   ```python
   TAG_PROMPTS: dict[str, str] = {
       "incidents": "You are a ServiceNow Incident Management specialist...",
       "cmdb": "You are a ServiceNow CMDB specialist...",
       # One entry per register_*_tools tag from mcp_server.py
   }
   TAG_ENV_VARS: dict[str, str] = {
       "incidents": "INCIDENTSTOOL",
       "cmdb": "CMDBTOOL",
       # Maps tag → the env var that toggles it in mcp_server.py
   }
   ```

    2. **Modify `{pkg_dir}/agent_server.py`** — Replace `create_agent_server()` with `create_graph_agent_server()`. The standardized `agent_server()` entry point must include warning suppression and version printing to `sys.stderr`:
        ```python
        import warnings
        import sys
        from agent_utilities import (
            build_system_prompt_from_workspace,
            create_agent_parser,
            create_graph_agent_server,
            initialize_workspace,
            load_identity,
        )

        initialize_workspace()
        meta = load_identity()

        DEFAULT_AGENT_NAME = os.getenv("DEFAULT_AGENT_NAME", meta.get("name", "MyAgent"))

        def agent_server():
            # Suppress known warnings
            warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
            warnings.filterwarnings("ignore", category=DeprecationWarning, module="fastmcp")

            print(f"{DEFAULT_AGENT_NAME} v{__version__}", file=sys.stderr)

            parser = create_agent_parser()
            args = parser.parse_args()

            create_graph_agent_server(
                mcp_url=args.mcp_url,
                mcp_config=args.mcp_config or "mcp_config.json",
                host=args.host,
                port=args.port,
                provider=args.provider,
                model_id=args.model_id,
                base_url=args.base_url,
                api_key=args.api_key,
                enable_web_ui=args.web,
                debug=args.debug,
            )
        ```

    `create_graph_agent_server()` handles everything internally: graph construction, mermaid diagram logging, system prompt enhancement with domain list, and agent lifecycle. No manual graph setup needed.

No changes to `mcp_server.py` are required — the existing env-var gating handles per-domain tool filtering.

### Phase 4: Build Skill-Graph (Optional)

If documentation URLs or PDF files were provided via `--doc-urls`:

1. Read the `skill-graph-builder` skill.
2. Run `generate_skill.py` with `--output-dir` pointing to the agent package's `skills/` directory:
   ```bash
   python <skill-graph-builder>/scripts/generate_skill.py "<urls>" {package-name}-docs \
     --description "Documentation for {display_name}" \
     --output-dir {project_dir}/{pkg_dir}/skills
   ```
   This creates `{pkg_dir}/skills/{package-name}-docs/` directly inside the agent package.
   The generated `pyproject.toml` already includes `skills/**` in `package-data`, so the skill-graph ships with the distribution.
3. Update `prompts/main_agent.md` to reference the generated documentation skill.

### Phase 5: Register in MCP-Client References

Every new agent package **must** be registered in the `mcp-client` skill so that agents can discover and use it. This involves creating two reference files and updating the SKILL.md table.

Locate the `mcp-client` skill directory:
```
universal-skills/universal_skills/skills/mcp-client/
├── SKILL.md              ← Update the References table
├── references/
│   ├── {package-name}.md   ← NEW: Full reference doc
│   └── {package-name}.json ← NEW: mcp_config.json
└── scripts/
```

#### 5a. Create `references/{package-name}.md`

Create the reference markdown file following the established pattern (see existing files like `jellyfin-mcp.md` or `servicenow-api.md` for reference). The file must contain these sections:

```markdown
# {Display Name} MCP Reference

**Project:** `{package-name}`
**Entrypoint:** `{mcp-cmd}`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `{SERVICE_URL_ENV}` | Required for authentication |
| `{AUTH_ENV}` | Required for authentication |

## Available Tool Tags ({count})

| Env Variable | Default |
|-------------|----------|
| `{TAG}TOOL` | `True` |
...

## Stdio Connection (Default)

{mcp_config.json with all tags enabled}

## HTTP Connection

{HTTP connection example}

## Single-Tag Config Example

{mcp_config.json with only one tag enabled, others False}

## CLI Usage

{Example mcp_client.py commands}
```

Once MCP tools are implemented (Phase 3b), populate the "Available Tool Tags" with the actual `register_*_tools` env var names from `mcp_server.py`, and add a "Tailored Skills Reference" section documenting each tool tag group and its tools with parameters.

#### 5b. Create `references/{package-name}.json`

Create the `mcp_config.json` file for stdio connection with all tool tags enabled:

```json
{
  "mcpServers": {
    "{package-name}": {
      "command": "{mcp-cmd}",
      "args": ["--transport", "stdio"],
      "env": {
        "{SERVICE_URL_ENV}": "${SERVICE_URL_ENV}",
        "{AUTH_ENV}": "${AUTH_ENV}",
        "{TAG1}TOOL": "True",
        "{TAG2}TOOL": "True"
      }
    }
  }
}
```

#### 5c. Update `mcp-client/SKILL.md` References Table

Add a new row to the `## References` table in the `mcp-client/SKILL.md`:

```markdown
| {Display Name} | [{package-name}.md](references/{package-name}.md) | [{package-name}.json](references/{package-name}.json) | {tool_tag_count} |
```

The row must be inserted alphabetically by MCP Server name in the existing table.

### Phase 6: Verify & Finalize

1. **Validate syntax**:
   ```bash
   python -c "import tomllib; tomllib.load(open('{project_dir}/pyproject.toml', 'rb'))"
   python -c "import yaml; yaml.safe_load(open('{project_dir}/compose.yml'))"
   ```

2. **Test entry points** (if stubs are complete enough):
   ```bash
   cd {project_dir} && pip install -e . && python -m {pkg_dir}.mcp --help
   ```

3. **Run pre-commit** (if installed):
   ```bash
   cd {project_dir} && pre-commit run --all-files
   ```

4. **Review README.md** for accuracy and completeness.

5. **Verify mcp-client references** — Confirm the new `.md` and `.json` files exist in `mcp-client/references/` and the SKILL.md table has been updated.
