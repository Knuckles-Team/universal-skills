---
sources:
  - "Domain-Driven Design: Tackling Complexity in the Heart of Software — Eric Evans, Addison-Wesley 2003 (ISBN 978-0-321-12521-7)"
  - "Implementing Domain-Driven Design — Vaughn Vernon, Addison-Wesley 2013 (ISBN 978-0-321-83457-7)"
  - "Domain-Driven Design Distilled — Vaughn Vernon, Addison-Wesley 2016 (ISBN 978-0-134-43442-1)"
purpose: "The semantic vocabulary the existing references assume but never define. [[hard-parts-pattern-catalog]] uses 'bounded context' five times without explaining what one is. This reference fills that gap and connects DDD's strategic concepts to the architectural decisions the other files describe."
relation_to_others: "Where the others ask *how big should this service be* (Hard Parts §2) and *who owns this table* (Hard Parts §4), DDD asks *where does the business naturally divide* and *what concept does this data really belong to*. The semantic answer informs the structural one."
note_on_method: "Author distillation from working knowledge of the texts, not a primary-source extraction. DDD has a large vocabulary; this reference covers the load-bearing third that an architect skill needs, not the full surface."
---

# Evans / Vernon — Domain-Driven Design (Distilled)

## Why this reference exists

The Hard Parts catalog gives the architect mechanical levers — disintegrators, integrators, data-ownership techniques. Used alone they produce *technically* defensible boundaries that don't survive contact with the domain. DDD provides the *semantic* layer: where the business actually has joints, what vocabulary lives where, and which concepts must stay together for the system to make sense.

DDD is a large book. This reference keeps only what an architect routinely *needs to reason from* — most of it drawn from Evans's Part IV ("Strategic Design"), with the tactical building blocks (§8) coming from Part II ("The Building Blocks of a Model-Driven Design") and Vernon's distillation of aggregate design from his *Effective Aggregate Design* paper series.

## 1. Strategic vs Tactical — the two halves of DDD

| Half | What it answers | Who it's for |
|---|---|---|
| **Strategic** | Where are the boundaries? What's the vocabulary? How do bounded contexts relate? | The architect |
| **Tactical** | Inside a context, how do we model entities, value objects, aggregates, services? | The developer, with architect guidance |

**For a software architecture skill, strategic DDD is load-bearing; tactical DDD is supporting.** A skill that gets strategic DDD wrong picks the wrong service boundaries — a problem the Hard Parts catalog *cannot* fix downstream. A skill that gets tactical DDD wrong picks suboptimal aggregates — recoverable through refactoring.

This file weights accordingly: §2–§7 are strategic; §8–§10 are tactical headlines.

## 2. Ubiquitous Language — the heuristic, not the slogan

The single concept the whole methodology depends on:

> **The vocabulary used by domain experts and the vocabulary in the code must be the same vocabulary.** No translation layer in between.

When a domain expert says "order" and the code says `Cart`, every conversation needs a translator and every translator introduces drift. The cost is invisible until the system has to change — at which point every requirements discussion costs twice (once to understand the domain, once to map to the code).

**Practical tests for whether you have a ubiquitous language:**

- Can a product person read a code review and understand which behaviour is changing?
- Does the code use the words the business uses, or the words a previous engineer thought sounded better?
- When the business introduces a new term, does someone update the code's vocabulary too?

**A ubiquitous language is bounded.** It only applies *within one bounded context* (§3). The same word can mean different things in different contexts and that is *correct*, not a bug to be reconciled. (A "Customer" in Sales has a credit limit; a "Customer" in Support has an open-ticket count. Forcing them to be the same `Customer` object is the canonical DDD-going-wrong story.)

→ This is also the underlying reason for Hohpe's [[hohpe-architect-principles]] §6 phantom-sketch-artist model: the architect's job is to extract the domain expert's language and play it back. The DDD vocabulary gives the architect a name for what they're producing.

## 3. Bounded Context — the load-bearing concept

> A **bounded context** is the boundary within which a particular model — and its ubiquitous language — applies consistently.

Inside a bounded context:
- One model, one vocabulary, one team's responsibility (ideally).
- Terms have a single meaning.
- The model is internally consistent.

Across bounded context boundaries:
- The same word may mean different things, and that's fine.
- Translation is *explicit*, via the integration patterns in §5.
- Coupling is reduced because each context evolves independently.

**Bounded Context ≠ microservice** — but they often align. A bounded context is a *modeling* boundary; a microservice is a *deployment* boundary. The architectural decision in modern practice is *how closely the two should track each other*.

Heuristics for finding bounded contexts:

| Signal | What it suggests |
|---|---|
| A word has two meanings depending on who's using it | Two contexts — give each its own model |
| One team owns subdomain X, another owns subdomain Y | Likely two contexts, aligned with team boundaries (see [[skelton-pais-team-topologies]]) |
| One sub-area changes weekly, another yearly | Two contexts — Hard Parts disintegrator "code volatility" agrees |
| Two parts of the model never actually interact in the requirements | Strong signal — they don't need to share a model |
| The same entity has wildly different lifecycles in different parts of the system | The entity is being conflated across two contexts |

**The architectural payoff:** the Hard Parts catalog gives you the *technique* (Table Split, Delegate, Service Consolidation) for resolving data-ownership pain. Bounded contexts tell you *which boundary is worth the effort to enforce* — the ones that align with real semantic seams. Boundaries enforced *against* the domain semantics will leak forever.

## 4. Subdomain types — Core, Supporting, Generic

Evans' classification of subdomains by *strategic value to the business*. This is one of the most actionable parts of strategic DDD, and the one most often skipped in practice.

| Subdomain type | Definition | Architectural implication |
|---|---|---|
| **Core domain** | The differentiator. The reason the business has an edge. | Build in-house. Best engineers. Highest quality bar. **Do not** outsource, do not buy, do not adopt a generic framework that constrains it. |
| **Supporting subdomain** | Necessary for the business but not a differentiator. Custom to the business. | Build in-house if no good package exists. Solid quality, but not where the senior engineers should live. |
| **Generic subdomain** | Solved problems other companies have already commoditised. Auth, billing, observability, email delivery. | Buy or adopt OSS. **Don't build.** Every hour spent here is an hour not spent on Core. |

**Why this matters for the skill:** the catalog can recommend a sophisticated saga / sidecar / service mesh; if it's recommending sophistication for a *Generic* subdomain, the right answer is usually "use the SaaS, stop." A skill that doesn't recognise subdomain type will over-engineer the wrong things.

**Test:** if a competitor copied this subdomain's architecture exactly, would they catch up to you? If yes — it's Generic. The architectural investment shouldn't be there.

## 5. Context Map — the relationship vocabulary

Bounded contexts must integrate. The *kind* of integration is a strategic decision with long-term consequences. Evans names nine relationships; the architecturally-important ones:

### 5.1 Anticorruption Layer (ACL) — the most important pattern in this section
A translation layer that converts an upstream context's model into terms the downstream context understands. The downstream context never speaks the upstream model directly.

- **Use when:** integrating with a legacy system, a vendor system, or any context whose model would corrupt yours.
- **Cost:** maintenance — the ACL is a service of its own.
- **Payoff:** your domain model stays clean; the upstream context can change without echoing into your code.

ACLs are the canonical answer to "we depend on this legacy CRM and its data model is contagious." They are also the right answer when a generic-subdomain vendor's vocabulary leaks into the Core domain.

### 5.2 Shared Kernel
Two contexts agree to share a small piece of model. Changes require coordination across both teams.

- **Use when:** there's a small, stable, genuinely-shared concept (e.g. "User ID" — but rarely "User").
- **Cost:** every change costs two team conversations.
- **Warning:** Shared Kernels metastasise. They're the route by which a microservices estate becomes a distributed monolith.

### 5.3 Customer / Supplier
The downstream context's needs are honoured by the upstream context's prioritisation. There's a real, working dependency where the upstream team treats the downstream team as a customer.

- **Use when:** the upstream team has bandwidth and political alignment to prioritise downstream needs.
- **Failure mode:** "supplier" team doesn't actually prioritise. Becomes Conformist.

### 5.4 Conformist
The downstream context adopts the upstream model unchanged because they have no leverage to negotiate translation.

- **Use when:** the upstream is a stable, well-modelled system and translation costs more than conformance.
- **Often when:** upstream is a vendor SaaS whose model you cannot influence.

### 5.5 Open Host Service / Published Language
The upstream context provides a *deliberate*, well-designed integration surface — typically REST/gRPC plus a documented event schema — intended for many downstream consumers.

- **Published Language** is the schema/contract used by the OHS.
- This is the *good* version of multi-consumer integration. The upstream commits to a documented evolvable interface.
- → Connects to [[hard-parts-pattern-catalog]] §9 (contracts) and [[kleppmann-data-intensive-applications]] §3 (encoding evolution).

### 5.6 Partnership
Two contexts must succeed or fail together; their teams plan and release together.

- **Use when:** the two contexts have a mutual dependency neither can opt out of (e.g., a checkout flow that must coordinate with a fraud-detection context, both owned by separate teams).
- **Cost:** highest coordination overhead of any Context Map relationship. Two-way blocking dependencies on roadmaps.
- **Failure mode:** Partnership without explicit acknowledgement — the two teams are effectively one team but neither has authority over the other. Either acknowledge and structure as one team, or break the mutual dependency.

### 5.7 Separate Ways
The contexts don't integrate. They share no model, no data flow.

- The forgotten option. Often correct. If two contexts don't need to talk, the architect's job is to *defend* that and not invent integration.

### 5.8 Big Ball of Mud
Named explicitly so it can be recognised. Most legacy systems are this. The strategic move is to draw a boundary *around* a ball of mud (often via an ACL) rather than into it.

## 6. Strategic-design heuristic the skill should use

When evaluating a candidate service split or architectural boundary, walk through:

1. **What's the ubiquitous language on each side?** If the same words have the same meanings, you don't have two contexts; you have one context being torn into two.
2. **What subdomain type is each side?** Core / Supporting / Generic. The investment level for each context should match.
3. **What's the integration relationship?** Name it — ACL, Shared Kernel, OHS, Conformist, Separate Ways. Don't leave it implicit.
4. **Does the relationship match the team structure?** A Customer/Supplier relationship only works if the team relationship supports it (see [[skelton-pais-team-topologies]]).
5. **Where's the model leakage today?** If a Generic subdomain's terms appear in Core code, the ACL is missing.

This complements [[hard-parts-pattern-catalog]] §2 (granularity disintegrators/integrators): walk both lists. If the disintegrators say "split" and the DDD heuristic says "same context, same language" — *don't split*. The structural pressure is fighting the semantic reality.

## 7. Aggregates — the bridge to tactical (Vernon's distillation)

Vernon distilled aggregate design into four rules that have become the practical standard. These are the *strategic* tactical patterns — the ones that affect transaction boundaries, service boundaries, and data ownership.

> An **aggregate** is a cluster of related objects treated as a unit for data changes. The **aggregate root** is the entity through which the rest of the cluster is accessed. The aggregate is the transactional consistency boundary.

### Vernon's Four Rules of Aggregate Design

**Rule 1 — Model true invariants in consistency boundaries.**
An aggregate's boundary is determined by what must be transactionally consistent. If two pieces of data must *always* be in agreement (an order's total must equal the sum of its line items), they belong in the same aggregate.

If the business rule is "must agree eventually" or "must agree within 30 seconds," it does *not* require a single aggregate — and forcing it into one will hurt concurrency.

**Rule 2 — Design small aggregates.**
Large aggregates create concurrency bottlenecks (everyone fights for the same lock) and load issues (every read pulls a huge graph). The default is *small*: an order plus its line items, not an order plus its line items plus the customer plus the catalogue.

**Rule 3 — Reference other aggregates by identity.**
Aggregate A doesn't hold a pointer to Aggregate B; it holds B's ID. To work with B, fetch it as a separate aggregate. This:
- Keeps aggregates small.
- Forces the boundary between them to be explicit.
- Makes service boundaries easier to extract later.

**Rule 4 — Use eventual consistency outside the boundary.**
Inside an aggregate: transactional consistency. Across aggregates: eventual consistency, via domain events.

→ This directly mirrors [[hard-parts-pattern-catalog]] §5 (ACID inside the service, BASE between services). DDD names *which boundary* the transactional / eventual line should fall on. Hard Parts names *the mechanism* for crossing it.

### The architectural payoff

The aggregate rules are the **semantic underpinning of data ownership** ([[hard-parts-pattern-catalog]] §4). An aggregate's data should be owned by one service. Joint data ownership across services often signals that the aggregate boundary was drawn in the wrong place — or that the would-be aggregate is actually two aggregates.

## 8. Tactical building blocks — headline taxonomy

For completeness; the skill rarely needs more detail than this:

| Concept | One-line |
|---|---|
| **Entity** | An object whose identity matters across time. Two Orders are different even if all attributes match. |
| **Value Object** | An object whose identity *doesn't* matter — only its values. Money, Address, DateRange. Immutable. Equality by value. |
| **Aggregate** | A cluster of objects (entities + value objects) with one Root entity, treated as a consistency unit. |
| **Module** | Evans's building block for grouping related model concepts (packages/namespaces). Named with the ubiquitous language. Often skipped in casual DDD treatments — keep in mind that "module" is a *domain* concern in Evans, not just a code-organisation one. |
| **Service** (Evans's original) | A behaviour that doesn't naturally belong to any entity. Evans's 2003 book treats this as one concept; the three-way split below is from Vernon's *Implementing DDD*. |
| **Domain Service** *(Vernon IDDD)* | Domain behaviour that doesn't belong to any one entity (e.g. transferring money between accounts). Stateless. |
| **Application Service** *(Vernon IDDD)* | Orchestrates use cases. Thin; delegates to the domain. |
| **Infrastructure Service** *(Vernon IDDD)* | Concerns outside the domain — persistence, messaging, email. |
| **Repository** | A collection-like interface for retrieving and persisting an aggregate. Hides the database. |
| **Factory** | Creates complex aggregates whose construction has invariants. |
| **Domain Event** | Something that happened in the domain that's worth telling other parts of the system about. Past tense (`OrderShipped`, not `ShipOrder`). |

**The two distinctions that matter for an architect:**
- **Entity vs Value Object** — drives whether the data needs an ID column and whether equality is by-reference or by-value. Affects database design and API design.
- **Application Service vs Domain Service** — drives where business rules live. Business logic in Application Services is the canonical anaemic-domain-model anti-pattern.

## 9. Domain Events — the connection to [[kleppmann-data-intensive-applications]] §10

Domain events are the bridge between strategic DDD and event-driven architecture:

- **Event sourcing** stores the events as the system of record; current state is a projection.
- **Event-driven integration** publishes events for other bounded contexts to subscribe to.
- **CQRS** (Command Query Responsibility Segregation) separates the write model (aggregates) from the read model (queries) — read models are projections of events.

These are the implementation mechanics for Rule 4 (eventual consistency across aggregate boundaries). When the skill recommends an event-based eventual-consistency pattern from Hard Parts §6.3, the *names* of the events should be domain events from the upstream context's ubiquitous language. "OrderShipped" not "RowUpdated."

## 10. Hexagonal architecture (ports and adapters) — Cockburn's pattern, popularised for DDD by Vernon

Coined by Alistair Cockburn around 2005 (and renamed "Ports and Adapters" by him a few years later). Vernon adopted it in *Implementing DDD* as the preferred packaging for a DDD codebase, which is why it travels with DDD in modern practice. The principle:

> The **domain** is at the centre. **Ports** are interfaces declared by the domain (e.g. "we need to save an Order"). **Adapters** implement the ports for specific technologies (Postgres, Kafka, S3). Infrastructure depends on the domain, never the reverse.

This is the same shape as [[moseley-marks-tar-pit]] §6.4: Essential Logic / Essential State at the centre, Accidental State and Control on the outside, with the dependency arrows pointing inward. Hexagonal is the OO packaging of the same idea.

→ A skill that knows hexagonal architecture can recognise the failure mode: a "domain" package that imports from the persistence package. The arrows are pointing the wrong way; the domain has been contaminated by infrastructure.

---

## Pattern → Decision lookup

| If the question is… | Reach for §… |
|---|---|
| "What should we call this in the code?" | §2 — ubiquitous language; align with domain experts |
| "Where should we draw the service boundary?" | §3 — bounded context heuristics, then Hard Parts §2 |
| "Should we build, buy, or adopt OSS for this subsystem?" | §4 — Core / Supporting / Generic |
| "How should service A integrate with service B?" | §5 — Context Map relationships (ACL most often) |
| "This vendor system's vocabulary is leaking everywhere" | §5.1 — Anticorruption Layer |
| "Should these two pieces of data be in the same transaction?" | §7 — Vernon's Rule 1 |
| "Why is this row update so contended?" | §7 — Vernon's Rule 2 (aggregates too big) |
| "Should this object have an ID?" | §8 — Entity vs Value Object |
| "Where should the business rule live?" | §8 — Domain Service, not Application Service |
| "What should we name this event?" | §9 — past tense, ubiquitous language of the upstream context |
| "Why is our 'domain' code coupled to the database?" | §10 — hexagonal violation; dependency arrows reversed |

## Cheat-sheet (for skill prompts)

| Concept | One-line |
|---|---|
| **Ubiquitous Language** | One vocabulary, shared by domain experts and code, inside one context |
| **Bounded Context** | The boundary within which one model / language applies |
| **Core / Supporting / Generic** | Differentiator / necessary / commodity. Invest accordingly. |
| **Anticorruption Layer (ACL)** | Translates an upstream model into your terms; defends your domain |
| **Shared Kernel** | Small shared model across two contexts; metastasises if used loosely |
| **Open Host Service / Published Language** | Deliberate multi-consumer integration surface with documented schema |
| **Conformist** | Adopt the upstream model when negotiation isn't available |
| **Partnership** | Two contexts that must succeed or fail together; highest-coordination relationship |
| **Separate Ways** | The forgotten option. Often correct. |
| **Aggregate** | The transactional consistency boundary |
| **Aggregate Root** | The only entry point into an aggregate |
| **Vernon Rule 1** | Aggregate boundaries follow real invariants, not convenience |
| **Vernon Rule 2** | Design *small* aggregates |
| **Vernon Rule 3** | Reference other aggregates by ID, not pointer |
| **Vernon Rule 4** | Eventual consistency between aggregates |
| **Entity vs Value Object** | Identity matters vs values matter |
| **Domain Service** | Behaviour that doesn't belong to any one entity |
| **Domain Event** | Something that happened, in past tense, in the ubiquitous language |
| **Hexagonal** | Domain at the centre; infrastructure depends on it, never the reverse |
| **Anaemic Domain Model** | Logic lives in Application Services, leaving entities as dumb data bags. Anti-pattern. |

## Self-check questions

1. Can the domain expert read the code's variable names and recognise their own vocabulary?
2. Where in the system does the same word mean two different things — and is that boundary recognised as a bounded context split?
3. What subdomain type is this? Are we investing engineering effort proportional to its strategic value?
4. For each cross-context integration, can I name the Context Map relationship? (If "we just call their API" is the only answer, it's probably Conformist by default.)
5. Which third-party vocabulary is leaking into our Core domain? Is there an ACL, or should there be?
6. Does this aggregate boundary follow a *real* invariant, or just a convenient grouping?
7. Is this aggregate small enough that two users' simultaneous writes won't routinely conflict?
8. Am I referencing other aggregates by ID, or holding object pointers that will make the boundary impossible to enforce later?
9. Is this thing an Entity (identity matters across time) or a Value Object (only values matter)? Have I treated it correctly?
10. Are my domain events named in past tense in the ubiquitous language, or am I publishing technical events like `RowUpdated`?

---

## How this fits with the others

- **[[hohpe-architect-principles]]** §6 (phantom sketch artist): DDD is the methodological version. The architect extracts the domain expert's language and plays it back through the code itself.
- **[[richards-ford-architect-principles]]** §1 (everything is a trade-off): subdomain classification gives the trade-off real teeth. *Don't trade off the same way for Core and Generic.*
- **[[hard-parts-pattern-catalog]]**: walks above. Strategic DDD chooses *which boundary* to enforce; Hard Parts gives the *technique* to enforce it. Use them together.
- **[[moseley-marks-tar-pit]]** §6.4 (three-component architecture): hexagonal architecture is the OO packaging of the same dependency-direction principle.
- **[[kleppmann-data-intensive-applications]]** §3 (encoding) and §10 (streams): Open Host Service / Published Language / Domain Events are the strategic-DDD names for the structures DDIA describes mechanically.
- **[[skelton-pais-team-topologies]]**: bounded contexts and team boundaries should align. DDD provides the modeling vocabulary; Team Topologies provides the org vocabulary; together they describe Conway's Law honestly.

**Closing observation:** the other references treat the domain as a given — they show you techniques you apply *to* whatever the business asked for. DDD inverts that: it treats the domain as the thing to be *understood and modelled first*, before any technique is picked. A skill with DDD vocabulary asks "what is this system actually trying to be?" before "how should it be built."
