# Architecture Patterns Reference

## Pattern Classification

### Monolithic Architecture
- Single deployable unit
- Shared database
- **Signals**: Single `main.py`/`app.py`, no service boundaries, direct DB access
- **Score Impact**: -10 for large codebases (> 10k LOC), neutral for small projects

### Modular Monolith
- Single deployment, but clear module boundaries
- Internal APIs between modules
- **Signals**: Distinct package directories, internal protocol/interface layers
- **Score Impact**: +5 for clean separation, +10 if module boundaries enforced

### Microservices
- Independent deployable services
- Service-to-service communication (HTTP/gRPC/messaging)
- **Signals**: Multiple `Dockerfile`/`docker-compose.yml`, service discovery, API gateways
- **Score Impact**: +10 for appropriate scale, -5 if over-engineered for small scope

### Plugin/Extension Architecture
- Core + extensible plugin system
- Hook/event-based composition
- **Signals**: Plugin registries, hook systems, `entry_points` in `pyproject.toml`
- **Score Impact**: +15 for well-designed extension points

### Event-Driven Architecture
- Asynchronous event processing
- Decoupled producers/consumers
- **Signals**: Event bus, message queues, pub/sub patterns, `asyncio` usage
- **Score Impact**: +10 for appropriate async patterns

## Protocol Detection Matrix

| Protocol | File Signals | Code Signals | Score Bonus |
|----------|-------------|--------------|-------------|
| MCP | `mcp_config.json`, `fastmcp` dep | `@mcp.tool()`, `MCPServer` | +15 |
| A2A | `a2a_config.json` | `A2AClient`, JSON-RPC handlers | +15 |
| ACP | `pydantic-acp` dep | `acp_adapter`, session handlers | +15 |
| REST | `openapi.json/yaml` | `@app.get()`, `@router.post()` | +5 |
| GraphQL | `schema.graphql` | `@strawberry.type`, resolvers | +10 |
| gRPC | `.proto` files | `grpc` dep, stub generation | +10 |
| WebSocket | None specific | `websocket`, `ws://` patterns | +5 |

## Type System Analysis

| Level | Description | Score |
|-------|-------------|-------|
| **None** | No type annotations | 0 |
| **Minimal** | < 25% annotation coverage | 20 |
| **Partial** | 25-50% coverage | 40 |
| **Good** | 50-75% coverage | 60 |
| **Strong** | 75-90% coverage, mypy passes | 80 |
| **Strict** | 90%+ coverage, strict mode enabled | 100 |

## Configuration Patterns (12-Factor Compliance)

| Factor | Detection Method | Score |
|--------|-----------------|-------|
| Config in env | `os.environ`, `python-dotenv`, `.env` | +10 |
| Explicit deps | `pyproject.toml`, `requirements.txt` with pins | +10 |
| Stateless processes | No filesystem state, no global mutable state | +10 |
| Port binding | `--port` CLI flag, `PORT` env var | +5 |
| Disposability | Signal handlers, graceful shutdown | +10 |
| Dev/prod parity | Docker, consistent env handling | +5 |
| Logs as streams | `logging` module, structured logging | +5 |
