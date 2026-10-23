# CONN-MATTERMOST-MCP-SDK-CENTRALIZATION requirements

Each row defines one requirement. [`status.json`](status.json) holds the generated state.

| ID | Requirement | Verification |
|---|---|---|
| `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R001` | **Requests use the governed SDK client.** mattermost-mcp must send every vendor request through the SDK governed HTTP client with its resolved TLS profile and SDK auth. It must not build its own session. This row follows `SDK-CENTRALIZED-CAPABILITIES-R001`, `SDK-CENTRALIZED-CAPABILITIES-R003`, `SDK-CENTRALIZED-CAPABILITIES-R008`. | A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport |
| `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R002` | **SDK floor and dependency set.** The package must require the current agent-connector-sdk floor and must not pin requests or httpx while nothing imports them directly. Optional drivers come from SDK extras. This row follows `SDK-CENTRALIZED-CAPABILITIES-R040`, `SDK-CENTRALIZED-CAPABILITIES-R001`. | pyproject.toml shows the floor and no unused requests pin |
| `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R003` | **Production wiring and hot path.** `ApiClientBase.__init__` in `mattermost_mcp/api/api_client_base.py` calls `create_http_client`, and every domain client reaches it through `request`. A transient 503 is retried by the SDK policy. This row follows `SDK-CENTRALIZED-CAPABILITIES-R001`, `SDK-CENTRALIZED-CAPABILITIES-R003`, `SDK-CENTRALIZED-CAPABILITIES-R008`. | A test builds the client with a mock transport, sees a 503 then a 200, and gets one result |
