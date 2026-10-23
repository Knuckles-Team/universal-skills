# CONN-MATTERMOST-MCP-SDK-CENTRALIZATION test specification

Tests use synthetic credentials and mock transports. They need no network.

| Scenario | Requirements | Expected result |
|---|---|---|
| Requests use the governed SDK client | `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R001` | A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport |
| SDK floor and dependency set | `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R002` | pyproject.toml shows the floor and no unused requests pin |
| Production wiring and hot path | `CONN-MATTERMOST-MCP-SDK-CENTRALIZATION-R003` | A test builds the client with a mock transport, sees a 503 then a 200, and gets one result |
