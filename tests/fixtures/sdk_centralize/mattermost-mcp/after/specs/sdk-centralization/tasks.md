# CONN-MATTERMOST-MCP-SDK-CENTRALIZATION tasks

| Task | Deliverable | Proof |
|---|---|---|
| T01 | Requests use the governed SDK client | A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport |
| T02 | SDK floor and dependency set | pyproject.toml shows the floor and no unused requests pin |
| T03 | Production wiring and hot path | A test builds the client with a mock transport, sees a 503 then a 200, and gets one result |
