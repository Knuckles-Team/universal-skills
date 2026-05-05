# Architecture Patterns Reference

Industry-standard architecture patterns evaluated by the code-enhancer skill.

## Hexagonal Architecture (Ports & Adapters)

**Core Principle**: Business logic is isolated from external concerns through ports (interfaces) and adapters (implementations).

```text
┌─────────────────────────────────────┐
│            Application              │
│  ┌───────────────────────────────┐  │
│  │         Domain Core           │  │
│  │  (business logic, entities)   │  │
│  └──────────┬────────────────────┘  │
│       ┌─────┴──────┐                │
│    Ports        Ports               │
│  (inbound)    (outbound)            │
│       │            │                │
│  Adapters     Adapters              │
│  (REST,CLI)   (DB, API)             │
└─────────────────────────────────────┘
```

**Python Indicators**: `domain/`, `ports/`, `adapters/` directories; abstract base classes for ports; dependency injection in constructors.

## SOLID Principles

| Principle | Description | Python Smell |
|-----------|-------------|-------------|
| **S**ingle Responsibility | One reason to change | Files >500 lines, classes >15 methods |
| **O**pen/Closed | Open for extension, closed for modification | No base classes, no protocols |
| **L**iskov Substitution | Subtypes must be substitutable | Type errors in subclass overrides |
| **I**nterface Segregation | No client depends on unused methods | Large abstract base classes |
| **D**ependency Inversion | Depend on abstractions | Direct instantiation of dependencies |

## Clean Architecture

**Layers** (inside-out):
1. **Entities** — Core business objects
2. **Use Cases** — Application-specific business rules
3. **Interface Adapters** — Controllers, presenters, gateways
4. **Frameworks & Drivers** — Web frameworks, databases

**Python Indicators**: `entities/`, `use_cases/`, `adapters/`, `infrastructure/` directories.

## Event-Driven Architecture

**Patterns**:
- **Event Sourcing** — Store state as sequence of events
- **CQRS** — Separate read and write models
- **Pub/Sub** — Decouple producers from consumers

**Python Indicators**: `Event` classes, `emit()`/`publish()` calls, callback registrations, signal libraries.

## Dependency Injection

**Benefits**: Testability, flexibility, loose coupling.

**Python Pattern**:
```python
class Service:
    def __init__(self, repository: Repository, logger: Logger):
        self._repo = repository
        self._logger = logger
```

**Anti-pattern**:
```python
class Service:
    def __init__(self):
        self._repo = PostgresRepository()  # Hardcoded dependency
        self._logger = FileLogger()
```

## Large Codebase Scaling Patterns

| Pattern | When to Apply | Indicator |
|---------|---------------|-----------|
| **Module Cohesion** | >20 files in single package | High inter-module imports |
| **Domain Boundaries** | >5 distinct business domains | Mixed concerns in single module |
| **Plugin Architecture** | >10 similar components | Repetitive registration code |
| **Lazy Loading** | Heavy imports slow startup | Import time >2s |
| **Feature Flags** | Gradual rollout needed | Environment variable toggles |
| **Package Extraction** | Reusable component identified | Shared utility across projects |

## Dependency Rule Verification (Clean Architecture)

Automated checks derived from *Clean Architecture* (Martin) decision rules:

| Check | What It Detects | Violation Signal |
|-------|----------------|------------------|
| Domain→infrastructure imports | `from infrastructure import ...` in domain modules | Dependency rule violation |
| Framework types in core | HTTP/ORM/SDK types used in business logic | Domain impurity |
| Layer-oriented top dirs | controllers/services/repos as top-level packages | Structure anti-pattern |
| Cross-layer shortcuts | Direct DB calls from handlers bypassing use cases | Boundary violation |

**Trigger rules** (from agent-rules-books):
- When framework or ORM types appear in domain code → move translation to adapter
- When a controller carries business rules → move policy inward to use case
- When adding external dep → introduce a port if core would learn vendor details

## Deep Module Metric (A Philosophy of Software Design)

**Principle**: A small interface hiding meaningful internal complexity beats extra pass-through layers.

**Measurable indicator**: Public-to-private interface ratio per module.

```
Module Depth = 1 - (public_symbols / total_symbols)
```

| Depth | Assessment | Action |
|-------|-----------|--------|
| >0.7 | Deep (good) | Module hides complexity well |
| 0.5-0.7 | Moderate | Acceptable for most modules |
| 0.3-0.5 | Shallow | Consider whether extra layers add value |
| <0.3 | Very shallow | Likely pass-through — consolidate or deepen |

**Trigger rules** (from agent-rules-books):
- When adding a module/layer, prove it hides real complexity instead of forwarding
- When one change spreads across many files, look for missing information hiding
