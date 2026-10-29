# CONN-MATTERMOST-MCP-SDK-CENTRALIZATION design and implementation plan

## Existing system and reuse

The SDK owns every capability named in the rows (`SCION-CENTRALIZED-CAPABILITIES-R001`, `SCION-CENTRALIZED-CAPABILITIES-R003`, `SCION-CENTRALIZED-CAPABILITIES-R008`). mattermost-mcp adds no module that repeats one. Each row deletes connector code and calls the SDK module.

## Live call path

`ApiClientBase.__init__` in `mattermost_mcp/api/api_client_base.py` calls `create_http_client`. Every domain client and MCP tool calls `ApiClientBase.request`.

## Compatibility

Tool names, arguments, URL joining, error types and result shapes stay identical.
