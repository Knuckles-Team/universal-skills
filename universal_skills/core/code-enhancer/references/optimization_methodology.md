# Code Optimization Methodology

Industry-proven methodologies for identifying and resolving code quality issues.

## Code Smell Taxonomy (Fowler/Beck)

### Bloaters
| Smell | Symptom | Threshold | Remediation |
|-------|---------|-----------|-------------|
| Long Method | Function too large to understand | >50 lines | Extract Method |
| Large Class | Class doing too much | >15 methods, >500 lines | Extract Class |
| Long Parameter List | Too many function args | >5 parameters | Introduce Parameter Object |
| Data Clumps | Same group of data appears together | 3+ fields repeated | Extract Class |

### Object-Orientation Abusers
| Smell | Symptom | Remediation |
|-------|---------|-------------|
| Switch Statements | Complex conditional logic | Replace with Polymorphism |
| Refused Bequest | Subclass ignores parent | Replace Inheritance with Delegation |
| Temporary Field | Fields only used in certain cases | Extract Class |

### Change Preventers
| Smell | Symptom | Remediation |
|-------|---------|-------------|
| Divergent Change | One class changed for many reasons | Extract Class (SRP) |
| Shotgun Surgery | One change requires many edits | Move Method, Inline Class |
| Parallel Inheritance | Creating subclass requires another | Move Method |

### Dispensables
| Smell | Symptom | Remediation |
|-------|---------|-------------|
| Dead Code | Unreachable or unused code | Remove (use vulture) |
| Speculative Generality | Unused abstractions | Collapse Hierarchy |
| Duplicate Code | Same structure in multiple places | Extract Method/Class |

## Complexity Thresholds

| Metric | Low Risk | Moderate | High Risk | Critical |
|--------|----------|----------|-----------|----------|
| Cyclomatic Complexity | 1–5 | 6–10 | 11–20 | >20 |
| Function Length (lines) | 1–20 | 21–50 | 51–100 | >100 |
| Nesting Depth | 1–2 | 3–4 | 5–6 | >6 |
| Class Methods | 1–8 | 9–15 | 16–25 | >25 |
| Module Lines | 1–200 | 201–500 | 501–1000 | >1000 |

## Incremental Optimization Process

1. **Discover** — Inventory all modules, measure baseline metrics
2. **Classify** — Map code smells to categories above
3. **Prioritize** — Rank by: (a) bug frequency, (b) change frequency, (c) complexity
4. **Isolate** — Draw dependency boundaries around target code
5. **Refactor** — Apply specific remediation pattern
6. **Verify** — Run tests, re-measure metrics, confirm improvement
7. **Repeat** — Move to next highest-priority item

## Duplication Analysis

### Detection Methods
- **Exact clone** — Identical code blocks (hash comparison)
- **Near clone** — Same structure, different identifiers (AST comparison)
- **Semantic clone** — Different implementation, same logic (requires deeper analysis)

### Acceptable Duplication
- Test setup code (each test should be self-contained)
- Protocol/interface boilerplate
- Configuration declarations

## Python-Specific Optimizations

| Technique | When | Impact |
|-----------|------|--------|
| `__slots__` | Data classes with many instances | Memory -40% |
| Generator expressions | Large data processing | Memory -90% |
| `functools.lru_cache` | Pure function called repeatedly | Speed +100x |
| `collections.defaultdict` | Dictionary with default values | Speed +20%, readability |
| `dataclasses.dataclass` | Simple data containers | Readability, less boilerplate |
| Lazy imports | Heavy modules rarely used | Startup time -50% |
