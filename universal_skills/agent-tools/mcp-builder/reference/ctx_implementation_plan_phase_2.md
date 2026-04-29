# Implementation Plan: ctx Helpers in All mcp_server.py Tool Bodies (Phase 2)

Phase 1 (previous session) injected `ctx: Context` parameters and imports into all 32 projects. This plan covers **Phase 2**: actually _calling_ the helpers inside tool function bodies to provide destructive op guards, progress reporting, diagnostic logging, state caching, and LLM-enhanced tools.

## User Review Required

> [!IMPORTANT]
> **Sync → Async Conversion Required**: 12 projects use `def` (sync) tool functions. The `ctx_progress()` and `ctx_confirm_destructive()` helpers are `async`. These tools must be converted to `async def` to use them. FastMCP handles async tools natively — this is a supported pattern and shouldn't break anything. However, it's a signature-level change.

> [!IMPORTANT]
> **Scope & Prioritization**: There are ~1,750 tool functions across 32 projects. We will NOT instrument every single tool. Instead, we'll apply helpers strategically:
> - `ctx_confirm_destructive()` → **only** on delete/remove/destroy/stop/purge/revoke/kill/reset/shutdown/wipe tools
> - `ctx_progress()` → **only** on tools with loops, bulk operations, or known long-running calls
> - `ctx_log()` → **only** on tools that already have `logger.*()` calls (augment, don't add new logging)
> - `ctx_set_state()` → **only** on `authenticate`/`login` tools to cache tokens
> - `ctx_sample()` → **only** on search/summarize tools that would benefit from LLM post-processing (opt-in, few targets)

> [!WARNING]
> **Projects with existing `ctx.*` calls (10 projects)** already use `await ctx.report_progress()` / `await ctx.elicit()` directly. We have two choices:
> 1. **Migrate** them to use the standardized helpers (`ctx_progress`, `ctx_confirm_destructive`, etc.)
> 2. **Leave them as-is** since they already work, and only add helpers to net-new instrumentation
>
> **Recommendation**: Option 2 — leave existing implementations alone. Only add standardized helpers to tools that currently lack any ctx usage. This minimizes risk.

## Open Questions

> [!IMPORTANT]
> **Q1**: For `ctx_sample()` — should we add it to search/summarize tools now, or defer to a later phase? It requires client-side sampling support and is the most experimental helper. **My recommendation**: Let's do it now.

> [!IMPORTANT]
> **Q2**: For projects with 100+ tools (jellyfin-mcp: 368, microsoft-agent: 266, mealie-mcp: 246), should we instrument ALL destructive tools or just the top-priority ones? Instrumenting all would be thorough but creates a large diff. We want all to be thorough.

---

## Audit Summary

### Helper → Project Mapping

| Helper | Projects Affected | Tools to Modify | Pattern |
|:---|:---|:---|:---|
| `ctx_confirm_destructive` | 8 projects | ~100 tools | delete/remove/stop/kill/revoke/prune/shutdown |
| `ctx_progress` | 10 projects | ~40 tools | loops, bulk ops, multi-step operations |
| `ctx_log` | 12 projects | ~400 logger calls | augment existing `logger.*()` calls |
| `ctx_set_state` | 4 projects | ~6 tools | authenticate/login tools |
| `ctx_sample` | 3 projects (deferred) | ~5 tools | search/summarize tools |

### Projects Requiring Sync→Async Conversion

These projects have sync `def` tools that need destructive guards or progress reporting:

| Project | Sync Tools | Destructive Tools | Needs Conversion |
|:---|:---:|:---:|:---:|
| portainer-agent | 110 | 17 | ✅ (17 tools) |
| home-assistant-agent | 31 | 1 | ✅ (1 tool) |
| jellyfin-mcp | 370 | 40 | ✅ (40 tools) |
| owncast-agent | 123 | 13 | ✅ (13 tools) |
| wger-agent | 60 | 6 | ✅ (6 tools) |
| postiz-agent | 19 | 3 | ✅ (3 tools) |
| qbittorrent-agent | 87 | 0 | ❌ |
| plane-agent | 57 | 0 | ❌ |
| uptime-kuma-agent | 10 | 1 | ✅ (1 tool) |
| langfuse-agent | 88 | 15 | ✅ (15 tools) |
| documentdb-mcp | 29 | 0 | ❌ |
| gitlab-api | 132 | 0 | ❌ (already async=0 but needs review) |

---

## Proposed Changes

### Execution Strategy

We will use a **Python script** (similar to the Phase 1 sweep) that programmatically modifies tool bodies. For each tool function, the script will:

1. **Detect** if the tool name matches a destructive pattern → inject `ctx_confirm_destructive`
2. **Detect** if the tool body has loops/bulk patterns → inject `ctx_progress`
3. **Detect** if the tool body has `logger.*()` calls → add `ctx_log` alongside
4. **Detect** if the tool name is `authenticate`/`login` → add `ctx_set_state` after successful auth
5. **Convert** `def` → `async def` where async helpers are needed

---

### Component 1: `ctx_confirm_destructive` — Destructive Operation Guards

#### Target Projects & Tools

##### portainer-agent
17 destructive tools: `delete_endpoint`, `delete_endpoint_group`, `docker_stop_container`, `docker_restart_container`, `docker_remove_container`, `delete_stack`, `stop_stack`, `delete_helm_release`, `delete_edge_group`, `delete_edge_stack`, `delete_edge_job`, `delete_custom_template`, `delete_user`, `delete_team`, `delete_registry`, `delete_tag`, `logout`

**Pattern** (applied to each):
```python
# BEFORE
def delete_endpoint_tool(endpoint_id, ctx):
    return get_client().delete_endpoint(endpoint_id)

# AFTER
async def delete_endpoint_tool(endpoint_id, ctx):
    if not await ctx_confirm_destructive(ctx, f"delete endpoint {endpoint_id}"):
        return {"status": "cancelled", "message": "Operation cancelled by user"}
    return get_client().delete_endpoint(endpoint_id)
```

##### home-assistant-agent
1 tool: `ha-delete-state`

##### jellyfin-mcp
40 destructive tools including: `delete_device`, `delete_items`, `delete_item`, `delete_user`, `remove_from_collection`, `remove_virtual_folder`, `remove_media_path`, `uninstall_plugin`, `stop_task`, `restart_application`, `shutdown_application`, `cancel_timer`, `cancel_series_timer`, `revoke_key`, etc.

##### microsoft-agent
23 destructive tools including: `delete_mail_message`, `delete_onedrive_file`, `delete_calendar_event`, `delete_todo_task`, `delete_group`, `remove_group_member`, `delete_domain`, `wipe_managed_device`, `delete_application`, `dismiss_risky_user`, etc.

##### owncast-agent
13 destructive tools including: `ban-ipaddress`, `delete-custom-emoji`, `delete-webhook`, `delete-external-apiuser`, `delete-prometheus-api`, `auto-update-force-quit`, etc.

##### langfuse-agent
15 destructive tools including: `delete-queue-item`, `delete-blob-storage-integration`, `dataset-items-delete`, `delete-run`, `delete-api-key`, `delete-project`, `prompts-delete`, `delete-user`, `trace-delete`, `trace-delete-multiple`

##### wger-agent
6 destructive tools: `delete_routine`, `delete_day`, `delete_workout_session`, `delete_workout_log`, `delete_nutrition_plan`, `delete_weight_entry`

##### postiz-agent
3 destructive tools: `postiz-delete-channel`, `postiz-delete-post`, `postiz-delete-post-by-group`

##### uptime-kuma-agent
1 destructive tool: `uptime-kuma-delete-monitor`

---

### Component 2: `ctx_progress` — Long-Running Operations

#### Target: Tools with loops or known multi-step operations

##### container-manager-mcp
Tools: `run_container`, `pull_image`, `prune_images`, `prune_containers`, `prune_volumes`, `prune_networks`

**Pattern**:
```python
async def pull_image_tool(image_name, ctx):
    await ctx_progress(ctx, 0, 100)
    result = get_client().pull_image(image_name)
    await ctx_progress(ctx, 100, 100)
    return result
```

##### portainer-agent
Tools with multi-step patterns: auth tools, stack operations

##### audio-transcriber
Long-running transcription tool — already has ctx usage but could add finer progress tracking

##### Other projects with loop patterns
- `gitlab-api` (94 loops) — bulk operations
- `microsoft-agent` (14 loops) — batch operations
- `documentdb-mcp` (7 loops) — database operations
- `servicenow-api` (37 loops) — bulk CMDB/ticket operations

---

### Component 3: `ctx_log` — Dual-Logging

#### Target: Tools that already have `logger.*()` calls

Top candidates by existing logger call count:

| Project | Logger Calls | Priority |
|:---|:---:|:---:|
| tunnel-manager | 150 | ⬛ Already has ctx |
| container-manager-mcp | 65 | 🟢 **High** |
| systems-manager | 62 | ⬛ Already has ctx |
| vector-mcp | 33 | ⬛ Already has ctx |
| audio-transcriber | 11 | 🟢 Medium |
| searxng-mcp | 11 | ⬛ Already has ctx |
| media-downloader | 9 | ⬛ Already has ctx |
| adguard-home-agent | 8 | 🟢 Medium |
| gitlab-api | 8 | 🟢 Medium |
| github-agent | 6 | 🟢 Medium |
| documentdb-mcp | 5 | 🟢 Medium |
| servicenow-api | 4 | 🟢 Medium |

**Pattern** (augmentation, not replacement):
```python
# BEFORE
logger.debug(f"Pulling image: {image_name}")

# AFTER
ctx_log(ctx, logger, "debug", f"Pulling image: {image_name}")
```

This replaces `logger.debug(msg)` with `ctx_log(ctx, logger, "debug", msg)`, which internally still calls `logger.debug(msg)` **plus** streams it to the MCP client.

---

### Component 4: `ctx_set_state` — Auth/Session Caching

#### Target: Projects with explicit `authenticate`/`login` tools

##### portainer-agent
Tool: `authenticate` — cache JWT token after successful login

```python
async def authenticate_tool(username, password, ctx):
    result = get_client().authenticate(username=username, password=password)
    await ctx_set_state(ctx, "portainer", "auth_token", result.get("jwt"))
    return result
```

##### microsoft-agent
Tool: `logout` — clear cached state

##### atlassian-agent
Tool: If auth tools exist — cache connection state

##### adguard-home-agent
Tool: Auth-related tools if present

---

### Component 5: `ctx_sample` — LLM-Enhanced Tools (Deferred)

> [!NOTE]
> **Recommendation**: Defer to Phase 3. The following tools are candidates but require validation that the deployment clients support sampling:
> - `microsoft-agent`: `summarize_email`, `search_query`
> - `searxng-mcp`: Search result summarization
> - `jellyfin-mcp`: `search_media` enrichment
> - `postiz-agent`: `get-missing-content` analysis

---

## Implementation Approach: Automated Script

Given the volume (~120 destructive tools + ~60 progress tools + ~400 logger calls), we'll implement this with a Python script that performs AST-aware transformations:

### Script Capabilities
1. **Destructive guard injection**: Match tool names against a destructive keyword list → inject `ctx_confirm_destructive()` as the first line of the function body
2. **Progress injection**: Wrap the main operation in tools with loops/bulk patterns with `ctx_progress()` calls (before/after)
3. **Logger augmentation**: Replace `logger.{level}(msg)` with `ctx_log(ctx, logger, "{level}", msg)` inside tool functions only
4. **Auth state injection**: For `authenticate`/`login` tools, add `ctx_set_state()` after the result line
5. **Sync→Async conversion**: Convert `def` → `async def` for any tool that now needs `await`

### Safety Guardrails
- **Skip** tools that already have `ctx.elicit`, `ctx.report_progress`, `ctx_confirm_destructive`, or `ctx_progress` calls
- **Skip** projects in the "already adopted" list (10 projects with existing ctx patterns) for destructive/progress helpers
- **Only modify** logger calls that are inside `@mcp.tool` decorated functions (not module-level logging)
- **Preserve** all existing return types, docstrings, and error handling
- **Syntax validation**: Run `ast.parse()` on every modified file before writing

---

## Verification Plan

### Automated Tests
```bash
# 1. Syntax validation across all 37 files
python3 -c "import ast; [ast.parse(open(f).read()) for f in files]"

# 2. Run existing unit tests
uv run pytest tests/unit/test_ctx_helpers.py -v
uv run pytest tests/unit/test_mcp_utilities.py -v

# 3. Verify no regressions — grep for common issues
# Check all async tools still have 'await' on ctx calls
grep -rn 'ctx_confirm_destructive\|ctx_progress\|ctx_set_state' agents/*/mcp_server.py | grep -v 'await'

# 4. Spot-check key projects
uv run python -c "from portainer_agent.mcp_server import *"
uv run python -c "from container_manager_mcp.mcp_server import *"
```

### Manual Verification
- Start 2-3 MCP servers and invoke a destructive tool to confirm elicitation fires
- Invoke a long-running tool to confirm progress appears in client
- Check server logs to confirm dual-logging works
