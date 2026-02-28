---
name: c4-architecture
description: Generate software architecture documentation using the C4 model with Mermaid diagram syntax. Use when creating architecture diagrams, documenting system design, visualizing software structure, or creating Context/Container/Component/Deployment diagrams. Triggers include "architecture diagram", "C4 diagram", "system context", "container diagram", "component diagram", "deployment diagram", "document architecture". Do NOT use for general flowcharts or ERD — use mermaid-diagrams instead.
categories: [Development, Productivity]
tags: [c4, architecture, mermaid, diagrams, system-design, documentation]
---

# C4 Architecture Documentation

Generate software architecture documentation using the C4 model. C4 describes architecture at four zoom levels: Context → Container → Component → Code (deployment). Use Mermaid syntax for all diagrams.

---

## C4 Diagram Levels

Select the appropriate level based on the audience and documentation need:

| Level | Diagram Type | Audience | Shows | When to Create |
|-------|-------------|----------|-------|----------------|
| 1 | **C4Context** | Everyone | System + external actors | Always (required) |
| 2 | **C4Container** | Technical | Apps, databases, services | Always (required) |
| 3 | **C4Component** | Developers | Internal components | Only when it adds value |
| 4 | **C4Deployment** | DevOps | Infrastructure nodes | For production systems |
| - | **C4Dynamic** | Technical | Request flows (numbered) | For complex workflows |

> [!TIP]
> **Context + Container diagrams are sufficient for most software development teams.** Only create Component/Code diagrams when they genuinely add value.

---

## Quick Start Examples

### Level 1: System Context

```mermaid
C4Context
  title System Context - E-Commerce Platform

  Person(customer, "Customer", "Places and tracks orders")
  Person(admin, "Admin", "Manages products and orders")
  System(store, "E-Commerce Platform", "Handles product browsing, orders, and payments")
  System_Ext(payment, "Payment Gateway", "Stripe — processes card payments")
  System_Ext(email, "Email Service", "SendGrid — sends order notifications")

  Rel(customer, store, "Browses and orders")
  Rel(admin, store, "Manages catalog and orders")
  Rel(store, payment, "Processes payments", "HTTPS")
  Rel(store, email, "Sends notifications", "HTTPS")
```

### Level 2: Container Diagram

```mermaid
C4Container
  title Container Diagram - E-Commerce Platform

  Person(customer, "Customer", "Places orders")

  Container_Boundary(app, "E-Commerce Platform") {
    Container(spa, "Web App", "React, TypeScript", "Single-page storefront")
    Container(api, "API Service", "Python/FastAPI", "REST API for business logic")
    ContainerDb(db, "Database", "PostgreSQL", "Orders, products, users")
    ContainerQueue(queue, "Message Queue", "Redis", "Async job processing")
  }

  System_Ext(payment, "Payment Gateway", "Stripe")

  Rel(customer, spa, "Uses", "HTTPS")
  Rel(spa, api, "API calls", "JSON/HTTPS")
  Rel(api, db, "Reads/writes", "SQL")
  Rel(api, queue, "Enqueues jobs")
  Rel(api, payment, "Charges cards", "HTTPS")
```

### Level 3: Component Diagram

```mermaid
C4Component
  title Component Diagram - API Service

  Container_Boundary(api, "API Service") {
    Component(auth, "Auth Controller", "FastAPI router", "Handles login and JWT")
    Component(orders, "Order Controller", "FastAPI router", "CRUD for orders")
    Component(orderSvc, "Order Service", "Business logic", "Validates and processes orders")
    Component(repo, "Order Repository", "SQLAlchemy", "Database access layer")
  }

  ContainerDb(db, "Database", "PostgreSQL")

  Rel(auth, orderSvc, "Authenticates requests")
  Rel(orders, orderSvc, "Delegates to")
  Rel(orderSvc, repo, "Reads/writes")
  Rel(repo, db, "Queries", "SQL")
```

### Dynamic Diagram (Request Flow)

```mermaid
C4Dynamic
  title Dynamic Diagram - Order Checkout Flow

  Container(spa, "Web App", "React")
  Container(api, "API Service", "FastAPI")
  Container(db, "Database", "PostgreSQL")
  System_Ext(payment, "Payment Gateway", "Stripe")

  Rel(spa, api, "1. POST /orders", "JSON/HTTPS")
  Rel(api, db, "2. Save order", "SQL")
  Rel(api, payment, "3. Charge card", "HTTPS")
  Rel(api, spa, "4. Return order ID", "JSON/HTTPS")
```

### Deployment Diagram

```mermaid
C4Deployment
  title Deployment - Production on AWS

  Deployment_Node(browser, "Customer Browser", "Chrome/Firefox") {
    Container(spa, "Web App", "React", "Hosted on CloudFront")
  }

  Deployment_Node(aws, "AWS us-east-1") {
    Deployment_Node(ecs, "ECS Fargate") {
      Container(api, "API Service", "FastAPI", "REST API")
    }
    Deployment_Node(rds, "RDS db.r5.large") {
      ContainerDb(db, "Database", "PostgreSQL", "Application data")
    }
  }

  Rel(spa, api, "API calls", "HTTPS")
  Rel(api, db, "Reads/writes", "TCP/SSL")
```

---

## Element Syntax

### People and Systems

```
Person(alias, "Label", "Description")
Person_Ext(alias, "Label", "Description")       # External person
System(alias, "Label", "Description")
System_Ext(alias, "Label", "Description")       # External system
SystemDb(alias, "Label", "Description")         # Database system
SystemQueue(alias, "Label", "Description")      # Queue system
```

### Containers

```
Container(alias, "Label", "Technology", "Description")
Container_Ext(alias, "Label", "Technology", "Description")
ContainerDb(alias, "Label", "Technology", "Description")
ContainerQueue(alias, "Label", "Technology", "Description")
```

### Components

```
Component(alias, "Label", "Technology", "Description")
Component_Ext(alias, "Label", "Technology", "Description")
ComponentDb(alias, "Label", "Technology", "Description")
```

### Boundaries

```
Enterprise_Boundary(alias, "Label") { ... }
System_Boundary(alias, "Label") { ... }
Container_Boundary(alias, "Label") { ... }
```

### Relationships

```
Rel(from, to, "Label")
Rel(from, to, "Label", "Technology")
BiRel(from, to, "Label")                        # Bidirectional
Rel_U(from, to, "Label")                        # Upward
Rel_D(from, to, "Label")                        # Downward
Rel_L(from, to, "Label")                        # Leftward
Rel_R(from, to, "Label")                        # Rightward
```

### Styling and Layout

```
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
UpdateElementStyle(alias, $fontColor="red", $bgColor="grey", $borderColor="red")
UpdateRelStyle(from, to, $textColor="blue", $lineColor="blue", $offsetX="5", $offsetY="-10")
```

---

## Best Practices

1. **Every element must have** — name, technology (where applicable), and description
2. **Use unidirectional arrows** — bidirectional arrows create ambiguity; use two arrows if truly bidirectional
3. **Label arrows with action verbs** — "Sends events to", "Reads from", "Authenticates via"
4. **Include technology labels** — "JSON/HTTPS", "SQL", "gRPC"
5. **Stay under 20 elements per diagram** — split complex systems into multiple diagrams
6. **Always include a title** — `title System Context diagram for [System Name]`
7. **Start at Level 1** — context diagrams frame the scope before drilling into containers

### Common Mistakes to Avoid

- Confusing containers (deployable units) with components (non-deployable logical parts)
- Modeling shared libraries as containers
- Showing a message broker (Kafka) as a single box instead of individual topics
- Adding undefined abstraction levels (e.g., "subcomponents")
- Removing type labels to "simplify" — they communicate essential technology context

---

## Output Location

Write architecture documentation to `docs/architecture/` with this naming convention:

- `c4-context.md` — System context diagram
- `c4-containers.md` — Container diagram
- `c4-components-{feature}.md` — Component diagrams per feature
- `c4-deployment.md` — Deployment diagram
- `c4-dynamic-{flow}.md` — Dynamic diagrams for specific flows

---

## Audience-Appropriate Detail

| Audience | Recommended Diagrams |
|----------|---------------------|
| Executives | System Context only |
| Product Managers | Context + Container |
| Architects | Context + Container + key Components |
| Developers | All levels as needed |
| DevOps | Container + Deployment |
