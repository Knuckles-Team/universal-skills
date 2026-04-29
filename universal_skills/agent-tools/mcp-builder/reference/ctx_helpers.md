# Implementation Guide: MCP Context Helpers (ctx)

This guide covers the standardized patterns for using MCP context helpers to provide destructive operation guards, progress reporting, diagnostic logging, and state caching within tool bodies.

## Standard Helpers

The following helpers are available in `agent_utilities.mcp_utilities` (or should be implemented according to these patterns) to standardize common MCP tool interactions.

### 1. `ctx_confirm_destructive()` — Destructive Operation Guards

**Purpose**: Prevent accidental execution of destructive actions (delete, remove, stop, etc.) by requiring explicit user confirmation.

**Pattern**:
```python
async def delete_item_tool(item_id, ctx):
    if not await ctx_confirm_destructive(ctx, f"delete item {item_id}"):
        return {"status": "cancelled", "message": "Operation cancelled by user"}
    return get_client().delete_item(item_id)
```

**Usage**:
- Apply to all tools matching patterns: `delete`, `remove`, `destroy`, `stop`, `purge`, `revoke`, `kill`, `reset`, `shutdown`, `wipe`, `prune`.
- **Note**: Requires the tool to be `async def`.

### 2. `ctx_progress()` — Progress Reporting

**Purpose**: Provide visual feedback to the user during long-running or multi-step operations.

**Pattern**:
```python
async def bulk_operation_tool(items, ctx):
    total = len(items)
    for i, item in enumerate(items):
        await ctx_progress(ctx, i, total)
        # perform operation
    await ctx_progress(ctx, total, total)
    return {"status": "success"}
```

**Usage**:
- Apply to tools with loops, bulk operations, or known long-running calls.
- **Note**: Requires the tool to be `async def`.

### 3. `ctx_log()` — Dual-Logging (Server + Client)

**Purpose**: Augment standard server-side logging with client-side streaming so users/agents can see progress/diagnostics in real-time.

**Pattern**:
```python
async def run_operation_tool(ctx):
    ctx_log(ctx, logger, "info", "Starting operation...")
    # ... logic ...
```

**Internals**: Calls `logger.{level}(msg)` AND streams the log to the MCP client via `ctx.info()` / `ctx.debug()`.

### 4. `ctx_set_state()` — Auth/Session Caching

**Purpose**: Persist important session state (like JWT tokens) across tool calls.

**Pattern**:
```python
async def authenticate_tool(username, password, ctx):
    result = get_client().authenticate(username=username, password=password)
    if token := result.get("jwt"):
        await ctx_set_state(ctx, "service_name", "auth_token", token)
    return result
```

**Usage**:
- Apply to `authenticate` or `login` tools.

### 5. `ctx_sample()` — LLM-Enhanced Tools

**Purpose**: Use the LLM to post-process tool results (summarize, extract, etc.) before returning to the main agent.

**Usage**:
- Search or summarize tools (experimental).

---

## Migration & Implementation Strategy

### Sync → Async Conversion
If a sync `def` tool needs to use `ctx_progress()` or `ctx_confirm_destructive()`, it **must** be converted to `async def`. FastMCP handles async tools natively.

### Strategic Instrumentation
We do not instrument every single tool. Focus on:
1. **Destructive Guards**: All tools that delete or stop resources.
2. **Progress**: Tools with loops or multi-step API calls.
3. **Logging**: Augment existing `logger.*()` calls inside tool functions.
4. **State**: Auth/Login tools only.

### Safety Guardrails
- Skip tools that already use `ctx.elicit`, `ctx.report_progress`, etc. directly.
- Preserve all existing return types and error handling.
- Ensure `ctx: Context` is in the function signature.
