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
