# Architecture Discovery Reference

## C4 Diagram Detection

### Mermaid Syntax Markers

Scan markdown files for these mermaid C4 block markers:

| Marker | C4 Level | Priority |
|--------|----------|----------|
| `C4Context` | System Context | L1 |
| `C4Container` | Container | L2 |
| `C4Component` | Component | L3 |
| `C4Deployment` | Deployment | L4 |

### Detection Procedure

1. Scan `**/*.md` for files containing any C4 marker inside fenced code blocks
2. Parse each mermaid block to extract:
   - `Person(id, "name", "desc")` — actors
   - `System(id, "name", "desc")` — internal systems
   - `System_Ext(id, "name", "desc")` — external systems
   - `Container(id, "name", "tech", "desc")` — containers
   - `Component(id, "name", "tech", "desc")` — components
   - `Rel(from, to, "label")` — relationships
   - `Container_Boundary(id, "label")` — boundary groups
3. Build a structured topology from parsed elements

### Common Locations

Check these paths first (ordered by likelihood):
- `docs/pillars/architecture_c4.md`
- `docs/architecture.md`
- `docs/design/*.md`
- `.specify/design/*/design.md`
- `README.md` (may contain inline C4)

## KG-Based Architecture Reconstruction

When no C4 diagram exists, reconstruct architecture from the Knowledge Graph:

### Step 1: Query Module Graph
```cypher
MATCH (m:Module)-[r:IMPORTS|DEPENDS_ON|CONTAINS]->(d:Module)
WHERE m.source_path CONTAINS $codebase_name
RETURN m.name, type(r), d.name
```

### Step 2: Identify Boundaries
Group modules by top-level package (e.g., `graph/`, `knowledge_graph/`, `mcp/`).
Each top-level package becomes a C4 Container boundary.

### Step 3: Identify Entry Points
```cypher
MATCH (f:Function)
WHERE f.source_path CONTAINS $codebase_name
  AND (f.name = 'main' OR f.decorators CONTAINS '@mcp.tool'
       OR f.decorators CONTAINS '@app.get')
RETURN f.name, f.source_path, f.module
```

### Step 4: Generate C4 Mermaid
Template:
```mermaid
C4Component
    title {codebase_name} — Auto-Generated Component Diagram

    Container_Boundary(pkg, "{package_name}") {
        Component(comp_id, "{module_name}", "Python", "{description}")
    }

    Rel(source, target, "{relationship_type}")
```

### Step 5: Save to `.specify/reports/generated_c4.md`
Always persist generated C4 diagrams for versioned history.

## Hot Path Identification

### Entry Point Patterns by Framework

| Framework | Entry Pattern | AST/Regex |
|-----------|---------------|-----------|
| FastMCP | `@mcp.tool()` decorated functions | `@mcp\\.tool\\(\\)` |
| A2A | `async def run(self, messages, ...)` on Skill classes | Class method with `messages: list` param |
| FastAPI | `@app.get()`, `@router.post()` etc. | `@(app\|router)\\.(get\|post\|put\|delete)` |
| CLI | `def main()` + `if __name__` | `def main` at module level |
| Click | `@click.command()`, `@click.group()` | `@click\\.(command\|group)` |
| Pydantic Graph | `class Node(BaseNode)` with `run()` | Subclass of `BaseNode` |

### KG-Based Import Tracing

The KG ingestion pipeline creates `IMPORTS` edges between modules. Use these for
reachability analysis instead of re-parsing AST:

```cypher
-- Find all modules reachable from entry points
MATCH path = (entry:Function)-[:DEFINED_IN]->(m:Module)-[:IMPORTS*1..10]->(dep:Module)
WHERE entry.is_entry_point = true
  AND m.source_path CONTAINS $codebase_name
RETURN DISTINCT dep.name, length(path) AS depth
ORDER BY depth
```

For projects not yet in the KG, fall back to AST-based `import` statement parsing.

### Reachability Classification

| Category | Definition | Score Impact |
|----------|-----------|--------------|
| **Hot Path** | Reachable from ≥1 entry point within 3 hops | Baseline |
| **Warm Path** | Reachable from entry point within 4-6 hops | -5 |
| **Cold Code** | Not reachable from any entry point | -15 |
| **Dead Code** | Cold + no internal references | -25 |

## Architecture Differential Analysis

### Dimensions

1. **Component Topology**: Which C4 components exist in source but not target?
2. **Data Flow Patterns**: How do components communicate (sync, async, event, queue)?
3. **Design Choices**: Mixin vs composition, DI vs direct, lazy vs eager init
4. **Integration Surface**: Public APIs, MCP tools, A2A skills, CLI commands
5. **Hot Path Breadth**: What % of codebase is reachable from entry points?

### Design Pattern Signatures

| Pattern | AST Signature |
|---------|--------------|
| Mixin | Multiple base classes: `class X(MixinA, MixinB)` |
| Dependency Injection | Constructor params typed as ABC/Protocol |
| Lazy Init | `@property` + `self._field is None` guard |
| Plugin Registry | Dict/list of callables, `register()` method |
| Event-Driven | `emit()`, `on()`, `subscribe()`, `publish()` |
| Protocol-Oriented | `class X(Protocol):` or `class X(ABC):` |
| Factory | `create_*()` or `build_*()` class methods |
| Strategy | Swappable callable fields on Pydantic models |

## Wiring Audit Checklist

For each new feature recommended by comparative analysis:

- [ ] **Entry Point Exists**: Is there an MCP tool, A2A skill, or API route that exposes this?
- [ ] **Engine Integration**: Is the feature callable from the core engine or a mixin?
- [ ] **Hot Path Reachable**: Can you trace from an entry point to this code in ≤3 hops?
- [ ] **C4 Diagram Updated**: Is the component shown in the architecture diagram?
- [ ] **Concept Map Updated**: Is the CONCEPT:ID present and accurate?
- [ ] **Design Consistent**: Does the implementation follow the same patterns as sibling modules?
- [ ] **Tests Exist**: Is there at least one test that exercises the hot path through this feature?
