---
source: "Software Architecture: The Hard Parts — Neal Ford, Mark Richards, Pramod Sadalage, Zhamak Dehghani, O'Reilly 2022 (ISBN 978-1-492-08689-5)"
purpose: "Distributed-systems pattern catalog. The lookup table the architect skill reaches for when a decision is actually about a pattern, not a principle. Complements [[hohpe-architect-principles]] (posture) and [[richards-ford-architect-principles]] (process)."
how_to_use: "This is a reference, not a manifesto. When a skill prompt needs to name a saga pattern, a reuse pattern, a workflow style, or a contract level, pull the specific entry — don't dump the whole file."
---

# Hard Parts — Distributed Architecture Pattern Catalog

## How to navigate this file

This is structured as **decision → options → trade-offs**. Each section starts with the question an architect is actually trying to answer, then enumerates the named patterns, then summarizes when each one is the right choice.

The three coupling dimensions from Ch. 2 (also in [[richards-ford-architect-principles#11]]) run through everything:

- **Communication** — synchronous / asynchronous
- **Consistency** — atomic / eventual
- **Coordination** — orchestrated / choreographed

## 1. Architectural Modularity — *should I break this monolith apart?*

> Architects shouldn't break a system into smaller parts unless clear business drivers exist.

**Business drivers:** speed-to-market, competitive advantage.
**Architectural drivers** (these are what you actually engineer for):

1. **Maintainability** — ease of adding/changing/removing features.
2. **Testability** — ease and completeness of testing; modularity shrinks the testing scope per change.
3. **Deployability** — frequency, ceremony, and risk of deploy. (Watch out: communicating services *erode* deployability — Matt Stine: "If your microservices must be deployed as a complete set in a specific order, please put them back in a monolith and save yourself some pain.")
4. **Scalability** — responsiveness as load grows.
5. **Elasticity** — responsiveness during *spikes*. Function of granularity + MTTS (mean time to start), not just modularity.
6. **Availability / fault tolerance** — partial failure doesn't kill the whole system.

**Change-scope progression** (the picture that sells modularity to executives):
- Layered monolith → **application-level** change scope
- Service-based → **domain-level** change scope
- Microservices → **function-level** change scope

Modularity ≠ distribution. **Modular monolith** and **microkernel** are both modular without being distributed; reach for them when maintainability/testability/deployability matter but scalability/elasticity don't.

> Scalability is more about **modularity**. Elasticity is more about **granularity**.

## 2. Service Granularity — *how big should this service be?*

> Modularity is breaking up. **Granularity** is the *size* of each piece. Most distributed-system pain is granularity pain, not modularity pain.

The decision is an equilibrium between two opposing forces:

### Granularity Disintegrators — when to break a service smaller (6)

| Driver | The question | Notes |
|---|---|---|
| **Service scope & function** | Is the service doing too many unrelated things? | Cohesion-based. "Single responsibility" is too subjective alone — combine with other drivers. |
| **Code volatility** | Are changes isolated to one part? | If one sub-function changes weekly and the rest yearly, the volatile part forces unnecessary retest/redeploy of the stable parts. |
| **Scalability & throughput** | Do parts need to scale differently? | SMS 220k/min vs postal letter 1/min → independent services. |
| **Fault tolerance** | Are there errors in one area that kill the whole service? | Isolate the OOM-prone code so it can't take down its neighbors. Check that the leftover has a self-descriptive name. |
| **Security** | Do parts need different security postures? | Credit-card access lives in its own service so profile-fetch endpoints can't reach it. |
| **Extensibility** | Is the service always growing to add new contexts? | Apply only when expansion is *known*, not "might happen someday." |

### Granularity Integrators — when to put services back together (4)

| Driver | The question |
|---|---|
| **Database transactions** | Is an ACID transaction required across separate services? |
| **Workflow & choreography** | Do they have to constantly talk to one another? Implementation coupling rising? |
| **Shared code** | Do they need to share code at a level that creates a distributed monolith? |
| **Data relationships** | Can the data they each need actually be broken apart? |

**The discipline:** most teams over-index on disintegrators and ignore integrators. The right granularity is *equilibrium*, not minimum.

## 3. Reuse Patterns — *how do I handle shared code across services?*

Four options, in order of common preference:

### 3.1 Code Replication
Copy the code into every service.
- **Use when:** Tiny, highly static code — annotations, marker interfaces, simple utilities — that you're confident won't need updating.
- **Trade-off:** preserves bounded context, zero sharing. Bug fixes are nightmare to propagate.

### 3.2 Shared Library (JAR/DLL/etc., compile-time)
- **Use when:** Homogeneous environments, low-to-moderate shared-code change rate. Compile-binding means runtime characteristics (perf, scalability, fault tolerance) are unaffected.
- **Always version.** No exceptions. The authors call versioning "the ninth fallacy of distributed computing." Avoid the `LATEST` tag.
- **Granularity rule:** prefer many **fine-grained** libraries (security.jar, formatters.jar, calculators.jar) over one coarse-grained `SharedStuff.jar`. Coarse libraries force every consumer to redeploy on every change. Fine ones are easier to manage but produce a dependency matrix that can degenerate into a "distributed monolith."

### 3.3 Shared Service (runtime)
- **Use when:** Highly polyglot environments, OR when the shared functionality changes often (versioning headache moves from libraries to API endpoints — still painful but more agile).
- **Trade-off:** Runtime changes mean a "simple" shared-service change can break every dependent service at once. Adds network/security latency, scalability coupling, fault-tolerance coupling.
- **Must use composition over inheritance** — there's no inheritance across the network.

### 3.4 Sidecars and Service Mesh (Hexagonal / Ports-and-Adapters)
- **Use when:** Shared **operational** concerns (monitoring, logging, auth, circuit breakers) where you want **consistency without coupling the domain code**.
- The Sidecar pattern decouples *technical* infrastructure from *domain* logic. The collection of sidecars across services forms the **service plane**, controlled centrally without touching domain code.
- **The microservices answer to "duplicate or couple?":** for *domain* concerns — duplicate. For *operational* concerns — couple via sidecar.

## 4. Data Ownership — *which service owns which table?*

> **The general rule of thumb:** the service that performs *write* operations to a table owns that table. Joint ownership makes that simple rule complex.

Three scenarios:

### 4.1 Single Ownership
Only one service writes to the table. Easy — assign ownership; the table becomes part of the service's bounded context. **Resolve all single-ownership cases first** to clear the deck for the hard ones.

### 4.2 Common Ownership (most or all services write)
Audit tables are the canonical example. The technique:

- Create a **dedicated owner service** (e.g., Audit Service) that becomes the sole writer.
- Other services send writes asynchronously via a **persistent queue** (fire-and-forget) — no caller blocking, durable through broker failures.
- If a response is needed: use REST / gRPC / request-reply messaging (pseudo-synchronous).

### 4.3 Joint Ownership (a handful of same-domain services write the same table) — 4 techniques

| Technique | Mechanics | When to use |
|---|---|---|
| **Table split** | Decompose the shared table into multiple tables, one owned per service. Sync data via async/sync messaging between owners. | Preserves bounded context; cost is data sync logic and possible duplication. |
| **Data domain** (shared schema) | Both services share a broader bounded context that includes the table; no service "owns" — the *domain* owns. | Performance and consistency are good; deployment/testing coupling rises with any schema change. |
| **Delegate** | One service is the sole writer (the delegate); others communicate with the delegate to update. Choose delegate by **primary domain priority** (default) or **operational characteristics priority** (when the non-domain service has much higher throughput). | When data must remain ACID-consistent within one owner; cost is high service coupling. |
| **Service consolidation** | Combine the two services back into one. Moves joint → single ownership. | When the joint-ownership pain consistently outweighs the disintegrator drivers. Always reconsider granularity *after* discovering joint ownership. |

## 5. ACID vs BASE — *the framework for understanding distributed transactions*

**ACID** (single-service, single database):
- **A**tomicity — all-or-nothing.
- **C**onsistency — no constraint violation during transaction.
- **I**solation — uncommitted changes invisible to other transactions.
- **D**urability — committed data survives failure.

**Distributed transactions do NOT support ACID.** Each service commits its own writes; if a later step fails, the earlier writes are already committed and visible. What you get instead is **BASE**:

- **Ba**sic availability — all services are expected to be reachable.
- **S**oft state — the system is in an in-progress, incomplete state during the transaction.
- **E**ventual consistency — given time and successful retries, the data will converge.

## 6. Eventual Consistency Patterns — *how do I keep data in sync without ACID?*

Three patterns; pick by responsiveness vs consistency vs error-handling tolerance.

### 6.1 Background Synchronization
A separate background process (batch job or periodic service) polls and reconciles.
- **Advantages:** services stay decoupled at runtime; user response is fast.
- **Disadvantages:** *worst* eventual consistency lag; the sync process needs write access to every owning table → **breaks every bounded context** and duplicates business logic.
- **Use when:** closed, self-contained heterogeneous systems that don't otherwise talk to each other (contractor order entry → invoicing). **Do NOT use** in microservices where bounded contexts matter.

### 6.2 Orchestrated Request-Based
A dedicated orchestrator service synchronizes the data *during* the user's request.
- **Advantages:** services stay decoupled (knowledge lives in the orchestrator); consistency is fast.
- **Disadvantages:** slower responsiveness (the user waits for the full transaction); **compensating-transaction error handling is brutal** — what do you do when the compensating update *itself* fails? Usually requires human intervention.
- **Use when:** business explicitly requires the transaction complete in-request and the workflow is small enough to make compensation tractable.

### 6.3 Event-Based (recommended default for microservices)
The owning service publishes an event (pub/sub topic or event stream); subscribers react asynchronously.
- **Advantages:** highly decoupled, good responsiveness, *short* eventual-consistency lag in practice.
- **Mandatory mechanics:** durable subscribers (RabbitMQ/ActiveMQ) or persistent message log (Kafka). Otherwise a temporary subscriber outage = silent data loss.
- **Use when:** modern microservices / event-driven architecture. Most popular and reliable today.

## 7. Workflow Coordination — *orchestration vs choreography*

The dynamic-coupling axis: who owns the workflow state?

### 7.1 Orchestration Communication Style
A dedicated **orchestrator** (mediator) component drives the workflow. Microservices use one orchestrator *per workflow*, not a global one (a global mediator = ESB = bad coupling point).

| Advantages | Disadvantages |
|---|---|
| Centralized workflow | Reduced responsiveness (mediator bottleneck) |
| Error handling | Fault tolerance (single point of failure) |
| Recoverability (retries) | Lower scalability (fewer parallelism opportunities) |
| State management (queryable) | Higher service coupling |

### 7.2 Choreography Communication Style
No coordinator. Each service knows the next step. Higher scale, no central state.

| Advantages | Disadvantages |
|---|---|
| Higher responsiveness | Distributed workflow (no central narrator) |
| Higher scalability | State management is hard |
| Better fault tolerance | Error handling is hard |
| Service decoupling | Recoverability is hard |

### 7.3 State management in choreography — three options
- **Front Controller** — first service in the chain owns the state. Pseudo-orchestrator within choreography.
- **Stateless choreography** — query each service when state is needed. Maximum decoupling, high chatter.
- **Stamp coupling** — pass workflow state in the message contract itself, each service updates its slice. See §9.

### 7.4 The deciding rule

> **As workflow complexity rises, the usefulness of orchestration rises proportionally.**

- **Choreography fits:** high-throughput, low-error-rate workflows; fire-and-forget pipelines (ingest, bulk).
- **Orchestration fits:** complex workflows with multiple boundary/error conditions.

And the deeper truth:

> An architect can never *reduce* semantic coupling via implementation, but they can make it worse.

Implementation should *match* the semantics of the workflow. Modeling a domain-cohesive workflow with technically-partitioned services *increases* implementation complexity.

## 8. Transactional Saga Patterns — *the eight named combinations*

Saga = a sequence of local transactions where failure triggers compensating transactions. The three-axis matrix produces 8 patterns. Superscripts indicate `(communication, consistency, coordination)` in alphabetical order.

| Pattern | Comm | Consist | Coord | Coupling | Complexity | Resp/Avail | Scale/Elast | When |
|---|---|---|---|---|---|---|---|---|
| **Epic Saga**⁽ˢᵃᵒ⁾ | Sync | Atomic | Orchestrated | Very high | Low | Low | Very low | The "traditional saga." Default that mimics monolith behavior. Familiar — and the most highly coupled pattern in the catalog. Compensating-transaction nightmares. Avoid if possible. |
| **Phone Tag Saga**⁽ˢᵃᶜ⁾ | Sync | Atomic | Choreographed | High | High | Low | Low | Sync calls in a chain (front-controller coordinates atomicity). Rare combination. Use only for simple workflows with infrequent errors where you can use idempotence + retries to recover. |
| **Fairy Tale Saga**⁽ˢᵉᵒ⁾ | Sync | Eventual | Orchestrated | High | **Very low** | Medium | High | **The popular default for microservices.** Orchestrator coordinates request/response/error handling but each service owns its own transactional state. Eventual consistency removes the hardest constraint. |
| **Time Travel Saga**⁽ˢᵉᶜ⁾ | Sync | Eventual | Choreographed | Medium | Low | Medium | High | Chain-of-responsibility / pipes-and-filters style. Each service owns its own transactionality and passes forward. Great for fire-and-forget pipelines (ingest, bulk). An on-ramp to the Anthology Saga for teams who find sync easier to reason about. |
| **Fantasy Fiction Saga**⁽ᵃᵃᵒ⁾ | Async | Atomic | Orchestrated | High | Very high | Low | Low | Implausible combination — async + atomic fight each other. Use only when responsiveness must look high *and* you truly need atomicity, and you're willing to pay the orchestration overhead. |
| **Horror Story**⁽ᵃᵃᶜ⁾ | Async | Atomic | Choreographed | High | Very high | Low | Medium | **Anti-pattern.** All three dimensions are at their most difficult combination — async, atomic, and no coordinator. Named to teach by counter-example. If you find yourself here, redesign. |
| **Parallel Saga**⁽ᵃᵉᵒ⁾ | Async | Eventual | Orchestrated | **Low** | Low | High | High | Best balance when you need an orchestrator's error handling but want async throughput and eventual consistency. |
| **Anthology Saga**⁽ᵃᵉᶜ⁾ | Async | Eventual | Choreographed | **Very low** | High | High | **Very high** | Fully decoupled. Maximum scale and elasticity. Pay in complexity — each service must encode workflow knowledge. Use when scale dominates other concerns. |

### The default-picking heuristic

- **Simple workflow, business demands atomicity?** Start at **Epic Saga**, but explore Fairy Tale first — eventual consistency usually removes the real pain.
- **Microservices, normal workflow?** **Fairy Tale Saga** is the popular sweet spot.
- **Throughput pipeline?** **Time Travel** or **Anthology**.
- **Need orchestrator's safety but want throughput?** **Parallel Saga**.
- **You've drawn Horror Story?** Redesign.

> Transactional coordination is one of the **hardest parts of architecture**, and the broader the scope, the worse it becomes. — Gregor Hohpe's "Starbucks Does Not Use Two-Phase Commit" applies here verbatim.

### Compensating-update trade-offs

| Advantages | Disadvantages |
|---|---|
| All data restored to prior state | No transaction isolation |
| Allows retries and restart | Side effects may occur during compensation |
|  | Compensation itself may fail |
|  | Poor responsiveness for the end user |

## 9. Contracts — strict to loose, and the stamp-coupling trap

### 9.1 The contract spectrum

```
STRICT ←────────────────────────────────────────→ LOOSE
XML Schema      GraphQL                  Value-driven contracts
JSON Schema     REST                     Simple JSON
Object                                   KVP arrays (maps)
RPC (incl. gRPC)
```

### 9.2 Strict contracts

| Advantages | Disadvantages |
|---|---|
| Guaranteed contract fidelity | Tight coupling |
| Versioned | Versioned (cuts both ways) |
| Easier to verify at build time |  |
| Better documentation |  |

### 9.3 Loose contracts

| Advantages | Disadvantages |
|---|---|
| Highly decoupled | Contract management (typos, missing fields) |
| Easier to evolve | Requires fitness functions to recover the safety net |

### 9.4 Consumer-driven contracts (the synthesis)

Instead of the *provider* pushing a contract to consumers, the *consumers* publish what they need; the provider includes those tests in its CI pipeline and must keep them green.

- **Allows loose contract coupling between services.**
- **Allows variability in strictness** — beyond what a schema can encode (e.g., acceptable numeric ranges).
- **Evolvable** — implementations can change without breaking consumers.
- **Cost:** *requires engineering maturity* — teams must actually run the contract tests and respond to failures. *Two interlocking mechanisms* (name-value pairs + consumer-driven tests) instead of one.

### 9.5 Stamp Coupling — anti-pattern *or* legitimate workflow tool

**Stamp coupling** = passing a large data structure between services where each service touches only a small part.

**The anti-pattern:** over-specifying the contract "just in case" — e.g., Wishlist needs only `name` but the contract serializes the full Profile (10 fields). When Profile adds `state`, Wishlist breaks for no reason. Also: bandwidth waste (500KB per request × 2,000 rps = 1 GB/s wasted).

> Keep contracts at a "**need to know**" level — semantic coupling minus needless fragility.

**The legitimate use — stamp coupling for workflow management:**
- In a *choreographed* workflow with no orchestrator, you can carry workflow state *in the contract itself*. Each service updates its slice and passes the document forward.
- Trade-off: higher coupling, larger messages, but enables complex choreographed workflows that would otherwise need an orchestrator.

### 9.6 The contract-selection heuristic

| Situation | Use |
|---|---|
| Internal RPC-style integration, single team controls both ends, change rate low | Strict (gRPC, JSON Schema) |
| Microservices boundaries, decoupling is the goal | Loose (REST with selective JSON Schema overlays) |
| Loose contracts + need for fidelity guarantees | **Consumer-driven contracts** |
| Choreographed workflow, no orchestrator, complex state | Stamp coupling — deliberately, not accidentally |

---

## Pattern → Decision lookup (for skill prompts)

| If the question is… | Reach for §… |
|---|---|
| "Should we break this monolith apart?" | §1 Modularity drivers |
| "How small should this microservice be?" | §2 Disintegrators vs Integrators |
| "Where should this shared code live?" | §3 Reuse Patterns |
| "Who owns this table?" | §4 Data Ownership |
| "Why isn't this distributed transaction working?" | §5 ACID vs BASE |
| "How do I keep these databases in sync?" | §6 Eventual Consistency Patterns |
| "Should this workflow have a coordinator?" | §7 Orchestration vs Choreography |
| "How do I implement this distributed transaction?" | §8 The 8 Sagas |
| "Should this contract be strict or loose?" | §9 Contracts |

## How this fits with the other two references

- **[[hohpe-architect-principles]]** — *Why* the architect is in the room. Posture, framing, political navigation.
- **[[richards-ford-architect-principles]]** — *How* the architect works. Definitions, laws, ADRs, fitness functions, trade-off methodology.
- **This file** — *What* patterns the architect actually picks between, with the criteria. The lookup table the other two reference.

A skill that has all three can: recognize when a problem is hard (Hohpe), set up the trade-off analysis rigorously (Richards/Ford), and name the candidate patterns with their trade-offs ready (this file).

**One closing reminder from the book:**

> Testing is the engineering rigor of software development.

The patterns in this catalog are claims about how systems behave under specific conditions. Use **fitness functions** ([[richards-ford-architect-principles#8]]) to verify those claims hold in *your* system. A pattern without a test is folklore.
