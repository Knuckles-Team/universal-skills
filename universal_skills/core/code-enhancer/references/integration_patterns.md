# Cross-Project Integration Patterns Reference

Standards and evaluation criteria for multi-project integration analysis.

## Dependency Graph Analysis

### Version Alignment
Projects sharing common dependencies should use compatible version ranges:

| Risk Level | Pattern | Example |
|-----------|---------|---------|
| **Critical** | Major version conflict | Project A: `pydantic>=2.0`, Project B: `pydantic<2` |
| **Warning** | Minor version gap >3 | Project A: `httpx>=0.27`, Project B: `httpx>=0.24` |
| **Info** | Patch-level differences | Normal — no action needed |

### Circular Dependency Detection
Circular dependencies between projects create tight coupling and build complexity:

```
A → B → C → A  ← CYCLE DETECTED
```

**Remediation strategies:**
1. Extract shared interface to a separate package
2. Use dependency inversion (depend on abstractions)
3. Merge tightly-coupled packages

### Unused Internal Dependencies
A project that declares a dependency on another workspace project but never imports from it:
- May indicate stale configuration
- Or may use it transitively (acceptable)

## Interface Stability Indicators

| Indicator | Good | Poor |
|-----------|------|------|
| `__all__` exports | Explicit public API | Everything exposed |
| Type annotations | Stable contracts | Implicit interfaces |
| Version pinning | Compatible ranges | Exact pins |
| Changelog | Documents breaking changes | No changelog |

## Integration Cohesiveness Score

Scoring dimensions:
1. **Version alignment** (25 pts): No conflicts → full marks
2. **No circular deps** (25 pts): Clean DAG → full marks
3. **Import tracing** (25 pts): All declared deps are actually used
4. **Interface clarity** (25 pts): `__all__`, type hints, versioning
