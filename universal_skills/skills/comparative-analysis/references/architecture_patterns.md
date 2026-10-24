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

## C4 Diagram Detection Patterns

The architecture analyzer scans markdown files for C4 mermaid blocks:

| Marker | C4 Level | Contains |
|--------|----------|----------|
| `C4Context` | System Context (L1) | Person, System, System_Ext, Rel |
| `C4Container` | Container (L2) | Container, ContainerDb, Container_Boundary, Rel |
| `C4Component` | Component (L3) | Component, Container_Boundary, Rel |
| `C4Deployment` | Deployment (L4) | Deployment_Node, Container, Rel |

### Element Parsing Regex
```
Person|System|System_Ext|Container|ContainerDb|Component|Container_Boundary
  → captures: (kind, id, name)
Rel(source, target, "label")
  → captures: (from, to, label)
```

## Hot Path Heuristics by Framework

| Framework | Entry Point Pattern | Priority |
|-----------|-------------------|----------|
| FastMCP | `@mcp.tool()` decorated functions | Highest |
| A2A | `async def run(self, *, messages: ...)` on Skill classes | Highest |
| FastAPI | `@app.get()`, `@router.post()` route handlers | High |
| Click/Typer | `@click.command()`, `@click.group()` | Medium |
| CLI | `if __name__ == "__main__"` with `main()` | Medium |
| Pydantic Graph | `class XNode(BaseNode)` with `run()` method | High |

### Reachability Tiers
- **Hot**: ≤3 hops from entry point
- **Warm**: 4-6 hops from entry point
- **Cold**: >6 hops or unreachable
- **Dead**: Cold + zero internal references

## Design Pattern AST Signatures

| Pattern | AST Detection | Example |
|---------|--------------|---------|
| **Mixin** | Class with ≥2 base classes | `class Engine(MemoryMixin, QueryMixin)` |
| **Dependency Injection** | `__init__` with ≥2 typed params | `def __init__(self, backend: Backend, ...)` |
| **Lazy Init** | `@property` + `None` guard | `if self._cache is None: self._cache = ...` |
| **Plugin Registry** | `register()` or dict of callables | `REGISTRY[name] = handler` |
| **Event-Driven** | `emit()`, `publish()`, `subscribe()` | `event_bus.emit("task_complete", data)` |
| **Protocol-Oriented** | `class X(Protocol):` or `class X(ABC):` | Abstract interface contracts |
| **Factory** | `create_*()`, `build_*()`, `make_*()` | `create_mcp_server(config)` |
| **Strategy** | Swappable callable fields | `self.search_fn = hybrid_search` |

## Wiring Audit Checklist

Before implementing any feature recommended by comparative analysis:

1. **Entry Point**: Does an MCP/A2A/API handler exist that exposes this feature?
2. **Engine Method**: Is there an engine/mixin method that calls this?
3. **Hot Path Reachable**: Can you trace entry → engine → this code in ≤3 hops?
4. **C4 Updated**: Is the new component in the architecture diagram?
5. **Concept Map**: Is there a CONCEPT:ID for this feature?
6. **Pattern Consistent**: Does it follow the same patterns (mixin, DI, lazy) as siblings?
7. **Test Coverage**: At least one test exercises the full entry→feature path?

If items 1-3 fail, the feature needs architectural redesign before implementation.
