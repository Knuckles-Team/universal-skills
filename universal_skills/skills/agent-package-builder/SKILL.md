---
name: agent-package-builder
description: Scaffold a complete agent-package project with all config files, Docker infrastructure, MCP server, A2A agent, and API wrapper stubs. Use when creating a brand-new agent-package from scratch, bootstrapping a new MCP/agent/api-wrapper project, or when the user says "create a new agent package". This delegates domain-specific implementation to existing skills (api-wrapper-builder, mcp-builder, agent-builder, skill-graph-builder). Do NOT use for modifying an existing agent package — use the individual skills directly.
categories: [Development, Core]
tags: [agent, package, scaffold, bootstrap, project, mcp, api-wrapper, builder]
---

# Agent Package Builder

Scaffolds a complete, production-ready agent-package project matching the `jellyfin-mcp` gold standard. The generated project includes all hidden config files (`.pre-commit-config.yaml`, `.bumpversion.cfg`, `.gitignore`, `.gitattributes`, `.env`, `.dockerignore`), Docker infrastructure (`Dockerfile`, `debug.Dockerfile`, `compose.yml`), Python packaging (`pyproject.toml`, `requirements.txt`), and agent workspace files (`IDENTITY.md`, `CRON.md`, `HEARTBEAT.md`, `MEMORY.md`, `USER.md`). It also includes a best-in-class `AGENTS.md` in the project root to optimize for AI coding tools.

---

## Workflow

### Phase 1: Gather Requirements

Collect the following from the user. Ask only for what is missing — do not re-ask for values already provided.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `package-name` | ✅ | — | Kebab-case name (e.g., `jellyfin-mcp`) |
| `--display-name` | ❌ | Derived from package name | Human-readable name (e.g., `Jellyfin MCP`) |
| `--description` | ❌ | `"Agent package for {display_name}"` | One-line description |
| `--type` | ❌ | `api_wrapper,mcp,agent` | Comma-separated: `api_wrapper`, `mcp`, `agent` |
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

#### 3a. API Wrapper (if type includes `api_wrapper`)

Read the `api-wrapper-builder` skill and follow its instructions to:
1. Create `{pkg_dir}/{name}_api.py` — The API wrapper class.
2. Create `{pkg_dir}/{name}_models.py` — Pydantic input/output models.
3. Update `{pkg_dir}/auth.py` — Configure authentication for the target service.

#### 3b. MCP Server (if type includes `mcp`)

Read the `mcp-builder` skill and follow its instructions to:
1. Implement tool registrations in `{pkg_dir}/mcp.py`.
2. Wire tools to the API wrapper methods created in 3a.
3. Register tools by tag with env-var-based enable/disable pattern.
4. **IMPORTANT**: All MCP tool tags MUST be strictly lowercase and use hyphens to separate words (e.g. `tag="user-management"`, env var=`USER_MANAGEMENTTOOL`). No camelCase or underscores are allowed in tags.
5. **Scale Pattern (Option 3)**: For agents with >50 API calls (e.g. `arr-mcp`, `leanix-agent`), use **Dynamic Runtime Generation**.
   - **Tag Prefixing**: For Option 3, prefix tool tags with the API/Service name (e.g. `leanix-pathfinder`).
   - **No Duplicates**: Ensure tool tags are unique across the entire registration.
   - Do not write massive `mcp.py` files with hundreds of static `@mcp.tool` decorators.
   - Use metaprogramming (e.g. `exec()` mapping python method signatures to FastMCP Pydantic schemas) similar to the `arr-mcp` pattern.
   - Feed the router a `tool_tags.json` mapping of `{"service": {"method_name": "lowercasetag"}}`.
   - **CRITICAL**: Even when dynamically generating tools, you MUST explicitly define static environment variables for *each* tag block in `mcp.py` so the users can clearly see and disable them:
     ```python
     DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
     if DEFAULT_MISCTOOL:
         register_misc_tools(mcp)
     ```
     For a purely dynamic loading loop, you should still hardcode the env variables checking before enabling specific categories inside the dynamic router or at the server root.

#### 3c. Agent (if type includes `agent`)

Read the `agent-builder` skill and follow its instructions to:
1. Configure `{pkg_dir}/agent.py` with proper identity loading.
2. Update `{pkg_dir}/agent/IDENTITY.md` with:
   - The agent's name, role, and emoji.
   - Instructions to run `list_skills` first.
   - Instructions to use the `mcp-client` skill and check `{package_name}.md` reference.
3. Update `{pkg_dir}/agent/CRON.md` with appropriate scheduled tasks.
4. Update `{pkg_dir}/agent/HEARTBEAT.md` with domain-specific health checks.

#### 3d. GraphQL Wrapper (if type includes `graphql`)

Read the `api-wrapper-builder` skill (Step 5 — GraphQL) and follow its instructions to:
1. Customize `{pkg_dir}/{name}_gql.py` — The GraphQL wrapper class (stub generated by scaffold).
2. Adjust the GraphQL endpoint path in `__init__` (e.g., `/api/graphql`, `/graphql`).
3. Implement domain-specific query and mutation methods mirroring the REST API wrapper.
4. Use cursor-based pagination (`first`/`after`) for list queries.

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
3. Update `IDENTITY.md` to reference the generated documentation skill.

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

Once MCP tools are implemented (Phase 3b), populate the "Available Tool Tags" with the actual `register_*_tools` env var names from `mcp.py`, and add a "Tailored Skills Reference" section documenting each tool tag group and its tools with parameters.

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
