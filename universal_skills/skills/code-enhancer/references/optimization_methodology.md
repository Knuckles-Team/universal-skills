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

## Refactoring Trigger Rules (Fowler)

Automated detection patterns derived from *Refactoring* (Fowler):

| Trigger | Detectable Signal | Automated Check |
|---------|------------------|-----------------|
| Patch mixes behavior + structure | Git diff contains both test changes and structural moves | Diff analysis |
| Conditional tree keeps growing | Nesting depth increases in recent commits | AST nesting delta |
| Risky area lacks tests | Modified files with 0 test coverage | Coverage + git log |
| Rewrite urge | Large file deletion + creation in same commit | Git diff stats |
| Duplicate structure | Near-identical AST subtrees across modules | Hash-based clone detection |

**Key principle**: Refactoring preserves observable behavior.  If behavior must
change, keep the behavioral delta distinct from structural cleanup.

## Legacy Code Seam Detection (Feathers)

Patterns from *Working Effectively with Legacy Code* (Feathers) for identifying
safe modification points:

| Seam Type | Python Indicator | Opportunity |
|-----------|-----------------|-------------|
| Object seam | Constructor injection possible | Replace dependency in tests |
| Preprocessing seam | Module-level imports | Mock at import boundary |
| Link seam | Abstract base class / Protocol | Substitute implementation |
| Extract & override | Long method with testable core | Sprout method pattern |

**Detection heuristic**: Files with >100 lines, no corresponding test file,
and >3 external dependencies are candidates for seam introduction before
modification.
