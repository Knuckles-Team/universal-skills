# SDK context helpers

Use the public SDK helpers; do not copy helper implementations into a connector.

    from agent_connector_sdk.mcp.context import ctx_confirm_destructive, ctx_log
    from agent_connector_sdk.progress import ctx_progress

## Destructive operations

The SDK action dispatcher applies confirmation to actions it classifies as
destructive. Preserve that contract and separate policy/authorization checks.
For a direct handler outside that dispatcher, required confirmation can use:

    if not await ctx_confirm_destructive(ctx, "delete the selected record"):
        return {"status": "cancelled"}

The helper denies when context is absent, elicitation fails or the user does not
accept. Unsupported elicitation and unattended execution are not write permission.
Confirmation does not replace verified authorization, optimistic source versions
or the write-back contract.

## Progress and logging

    await ctx_progress(ctx, 0, 1, message="reading records")
    await ctx_log(ctx, "Read completed", logger=logger, level="info")
    await ctx_progress(ctx, 1, 1)

ctx_log is asynchronous and accepts the message second, with logger and level as
keyword arguments. Keep credentials, raw provider responses and private endpoint
details out of server and client logs. Report bounded progress.

Session state and model sampling are optional framework capabilities, not required
connector scaffolding. Never cache raw credentials in general MCP context state;
use the SDK credential resolver and provider runtime contract.
