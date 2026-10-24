---
source: "Designing Data-Intensive Applications — Martin Kleppmann, O'Reilly 2017 (ISBN 978-1-449-37332-0)"
purpose: "The mechanics layer underneath [[hard-parts-pattern-catalog]]. When the skill needs to reason about *what kind* of eventual consistency, *what happens* during a leader failover, *which isolation level* the saga assumes — this is the reference."
relation_to_others: "Hard Parts gives the saga pattern; DDIA gives the consistency model the saga is implicitly choosing. Tar Pit names state as the architect's enemy; DDIA tells you the actual cost of the kinds of state you can't avoid. Richards/Ford §11 names the three coupling dimensions; DDIA tells you the concrete mechanism behind each one."
note_on_method: "Author distillation from working knowledge of the text, not a primary-source extraction. Verify load-bearing claims against the book before relying on them in production skill output."
---

# Kleppmann — Data Systems Mechanics

## Why this reference exists

[[hard-parts-pattern-catalog]] tells you to pick a saga; it doesn't tell you what to do when the orchestrator restarts mid-saga or when two services see different orderings of the same events. [[richards-ford-architect-principles]] §12 lists the 8 fallacies of distributed computing as a checklist; this reference is the next level down — *what specifically goes wrong* and *what techniques actually work*. Kleppmann's book is dense; this distillation keeps only what an architect needs to reason from, not to implement from.

## 1. The three goals — reliability, scalability, maintainability

The book's frame for any data system. Kleppmann is sharper than the generic "-ilities" list because he insists on operational definitions:

| Goal | Operational definition |
|---|---|
| **Reliability** | The system continues to perform its function *correctly* even when things go wrong. Things-that-go-wrong = faults; the system is **fault-tolerant**, never "fault-free." A fault becomes a *failure* only when it stops the system from delivering its service. |
| **Scalability** | The system has reasonable ways of *coping with increased load*. Not "is fast" — "has options when load grows." Requires a definition of load (RPS, ratio of reads/writes, simultaneous active users, cache hit rate) and a definition of performance (latency *distribution*, not mean — always report percentiles, especially p95/p99). |
| **Maintainability** | Three sub-properties: *operability* (easy for ops to keep running), *simplicity* (easy for new engineers to understand), *evolvability* (easy to change). |

**Two warnings from this chapter that recur throughout the book:**

- **Latency averages lie.** Always reason in *percentiles*. The user who experiences p99 latency is the user who is angry about your system. *Head-of-line blocking* means a slow request can hold up many fast ones behind it.
- **"Scalable" is meaningless without load and metric.** "Scale horizontally" means nothing until you say *which* metric, *which* load profile, *which* latency target. This pairs with [[richards-ford-architect-principles]] §8 — fitness functions force the metric to be named.

## 2. Data models — relational, document, graph

The trade-off isn't ideological; it's about *the shape of your relationships*.

| Model | Strength | Pain point |
|---|---|---|
| **Relational** | Joins are cheap and explicit; query planner re-optimises as data grows | Object-relational impedance mismatch; schema migrations expensive at scale |
| **Document** (JSON) | Locality (one read = one document); schema flexibility for self-contained records | Joins are application-level; many-to-many is painful; shred-and-reassemble appears once relationships outgrow one document |
| **Graph** | Many-to-many relationships and variable-depth traversals are first-class | Operational maturity is lower than relational; tooling thinner |

**Kleppmann's most quoted observation:** *the document model is appealing for the same reason the network/hierarchical models of the 1960s were appealing — and abandoned for the same reason.* Document models suit data with **tree-shape and no shared references**. The moment your data has many-to-many relationships, you're either denormalising (and now you own the consistency problem) or re-inventing joins in application code.

**Schema-on-write vs schema-on-read.** Document stores let you skip schema declaration; you do not skip *having* a schema, you skip *enforcing* it at write time. The schema is now distributed across all the code that reads the data. Trade: write flexibility vs read predictability. Often the right answer for heterogeneous data (e.g. event payloads), often the wrong answer for the system-of-record.

## 3. Encoding and schema evolution — the contract layer under [[hard-parts-pattern-catalog]]#9

A field on a service contract is *also* a field in a database row, *also* a field in a message payload. All three need the same property: **schema can change without breaking consumers that haven't been redeployed.**

| Format | Forward compat (old reader, new writer) | Backward compat (new reader, old writer) | Notes |
|---|---|---|---|
| **JSON / XML** | Possible but informal | Possible but informal | No schema enforcement; relies on convention |
| **Protocol Buffers** | Yes — unknown fields ignored | Yes — fields are optional, identified by tag number | Tag numbers are the load-bearing detail; never reuse one |
| **Avro** | Yes via schema resolution at read time | Yes via schema resolution at read time | Writer's schema embedded or named; reader's schema may differ — Avro reconciles |
| **Thrift** | Similar to Protobuf | Similar to Protobuf | Older Facebook stack |

**Why this matters for [[hard-parts-pattern-catalog]]#9:** "loose contracts" is not a single technique. The trade-off is encoded in *which compatibility direction* the schema format guarantees and how. A consumer-driven contract test for a Protobuf service guards different invariants than one for a REST/JSON service.

**The most under-appreciated point in Ch. 4:** *data outlives code.* A database row written today will be read by code that doesn't exist yet. The encoding choice is a 5-year commitment, sometimes more. The skill should treat encoding format as a high-coupling architectural decision, not a serialisation detail.

## 4. Replication strategies — the actual mechanics

Three flavours of replication, with sharply different consistency / availability / latency trade-offs:

### 4.1 Single-leader (primary-replica)
All writes go to the leader; reads can go to leader or followers. Replication is **synchronous** (writes blocked until replicas confirm) or **asynchronous** (writes commit at leader, replicate later).

| Property | Sync replication | Async replication |
|---|---|---|
| **Durability after leader crash** | Strong | Weak (may lose committed writes) |
| **Write latency** | Higher (RTT to replicas) | Lower |
| **Availability for writes during replica failure** | Lower | Higher |

**Semi-synchronous** (one replica sync, others async) is the common compromise.

**Failover is the dangerous moment.** Choosing a new leader can cause: split-brain (two leaders), data loss (the new leader didn't have the latest writes), or write blackout (no leader for 30s+). This is where 90% of "we lost data in production" stories actually start.

### 4.2 Multi-leader
Each datacentre / region has its own leader; leaders replicate to each other. Better latency for geo-distributed writes; introduces **conflict resolution** as a first-class problem (two leaders accept conflicting writes for the same row).

**Conflict resolution strategies** (none are free):
- **Last write wins (LWW)** — based on timestamp. Loses data when clocks disagree (and clocks always disagree — see §7).
- **Application-level merge** — application code receives both versions and merges. CouchDB and Riak made this idiomatic.
- **CRDTs (Conflict-free Replicated Data Types)** — data types whose operations commute, so concurrent edits merge automatically. Practical for counters, sets, some text.

### 4.3 Leaderless (Dynamo-style)
Clients write to multiple replicas in parallel; reads query multiple replicas and reconcile. **Quorum reads/writes** (w + r > n) guarantee that reads see the last write — *if no failures, no clock skew, no network partitions*. In practice, the guarantee is weaker than the headline.

**Replication lag is not a bug, it's a property.** Whichever style you pick, a follower can be behind. The user experience consequences are named:
- **Read-your-writes** — you read after writing and don't see your write. Fix: read your own writes from the leader.
- **Monotonic reads** — you read v3 then v2. Fix: route a user always to the same replica.
- **Consistent-prefix reads** — you see an answer before its question. Fix: causal ordering or session pinning.

→ The skill should map these to user-experience failures. When a stakeholder says "the UI shows old data after refresh," the architect should be reaching for *read-your-writes* as the named problem.

## 5. Partitioning — sharding without the marketing

Two strategies; everything else is a variation:

| Strategy | How keys map to partitions | Hot-spot risk |
|---|---|---|
| **Key range** | Sorted by key; partition by range | High — sequential keys (timestamps, autoincrement IDs) hammer one partition |
| **Hash of key** | Hash the key; partition by hash range | Lower — but range queries become scatter-gather |
| **Hybrid (compound key)** | Hash first column, range on remaining | The Cassandra pattern; useful for time-series per user |

**Secondary indexes are the painful part.** Two approaches:
- **Document-partitioned** (local) — index lives on the same partition as the data. Writes are cheap (one partition), reads are scatter-gather (all partitions queried).
- **Term-partitioned** (global) — index is partitioned by the indexed term. Reads are cheap (one partition), writes are distributed (multiple partitions updated per write).

**Rebalancing** — adding a node forces some keys to move. Strategies (fixed number of partitions, dynamic partitioning, partitioning proportional to nodes) are operational details; the architecturally relevant fact is **rebalancing happens, and it is the source of a lot of operational surprise**.

## 6. Consistency models — the spectrum that matters

The most under-used vocabulary in distributed-system arguments. Ranked strongest to weakest:

| Model | Guarantee | Cost |
|---|---|---|
| **Linearizability** | The system appears to have a single, up-to-date copy. Reads see the latest committed write. | Requires consensus; rules out high availability under partition |
| **Sequential consistency** | All processes see operations in the same order, but that order need not match real time | Slightly cheaper than linearizable; rarely used in distributed practice |
| **Causal consistency** | Causally-related operations appear in the same order to everyone; concurrent operations may differ | Achievable without consensus; the strongest practical model under partition |
| **Read-your-writes / Monotonic reads** | Session-level guarantees within one client's perspective | Cheap; implementable via session-pinning |
| **Eventual consistency** | If writes stop, replicas eventually converge | Cheapest; "eventually" is unbounded |

**Kleppmann is famously skeptical of CAP as a useful tool.** His preferred framing: *under network partition, you choose between linearizability and availability — and the system has to make this choice on every single operation.* He prefers explicit named consistency levels over the "CP / AP" labels, which encourage the false sense that "we're CP" is a one-time architectural choice.

> **For [[hard-parts-pattern-catalog]] users:** "eventual consistency" in §6 is a label for a *family* of consistency models. Background sync, orchestrated request, and event-based each typically land at *eventual* but differ in whether they preserve causal order. When a skill prompt names a saga, also name the consistency level — otherwise the trade-off discussion is one click too coarse.

## 7. The trouble with distributed systems — why everything is harder

Three categories of trouble. Memorise these — they're the *why* behind every fallacy in [[richards-ford-architect-principles]] §12.

### 7.1 Unreliable networks
- Packets are dropped, duplicated, reordered, delayed arbitrarily.
- **Timeouts are the only practical failure detector** — and you cannot distinguish "slow node" from "dead node" by timeout alone.
- Tail latency on networks is *much* worse than mean (long-tail GC pauses, network congestion, retries).

### 7.2 Unreliable clocks
- **Time-of-day clocks** (NTP-synced) jump backward and forward; useless for ordering.
- **Monotonic clocks** never jump backward but aren't comparable across machines.
- **Logical clocks** (Lamport timestamps, vector clocks) impose ordering without physical time — the right tool for ordering events across machines.
- **Process pauses** (GC, VM live migration, OS preemption) can hold a process for *seconds*; locks based on real-time leases can expire silently during a pause.

→ Any algorithm that depends on "this must happen within X seconds" is one GC pause away from a correctness bug. **Fencing tokens** (monotonically-increasing IDs validated by the resource being protected) are the canonical fix.

### 7.3 Knowledge, truth, and lies
- **A node cannot trust its own judgment about anything.** It might be the only one declared dead by a partitioned cluster.
- **The truth is decided by a majority** — quorum vote. Single-node decisions are not authoritative in distributed systems.
- **Byzantine faults** (nodes lying actively, not just being slow or dead) are a different threat model — usually only relevant for adversarial environments (blockchains, multi-org systems). Most enterprise systems can assume nodes are honest-but-broken.

## 8. Transactions — the isolation-level taxonomy

The single most-misunderstood area in application development. Memorise the anomalies each level prevents:

| Isolation level | Dirty read | Lost update | Read skew | Phantom | Write skew |
|---|---|---|---|---|---|
| **Read uncommitted** | Allowed | Allowed | Allowed | Allowed | Allowed |
| **Read committed** | Prevented | Allowed | Allowed | Allowed | Allowed |
| **Snapshot isolation** | Prevented | Not prevented by SI itself; some implementations (Postgres, Oracle, SQL Server) add automatic detection — MySQL InnoDB does not | Prevented | Prevented for read-only queries; **allowed in read-write transactions** (this is what enables write skew) | **Still allowed** |
| **Serializable** | Prevented | Prevented | Prevented | Prevented | Prevented |

**Note on lost update:** Kleppmann is explicit that lost-update prevention is *orthogonal* to the standard isolation ladder. The flat table format hides this; the prose to remember is "SI as specified does not prevent lost updates; specific databases add detection on top."

**Snapshot isolation** is the modern default in PostgreSQL and many others. The skill should know its blind spot: **write skew**. Example: a hospital rule that "at least one doctor must be on call." Two doctors simultaneously try to clock off. Both reads see "two on call" (snapshot). Both writes succeed. Now zero are on call.

**Serializable isolation implementations:**
- **Actual serial execution** — one thread, in-memory (Redis, VoltDB). Possible because RAM and CPU got fast enough.
- **2PL (two-phase locking)** — classical; pessimistic; can deadlock.
- **Serializable Snapshot Isolation (SSI)** — optimistic; PostgreSQL has it. Detects serialization conflicts after the fact and aborts the offender.

**For distributed transactions:** the book gives 2PC (two-phase commit) honest treatment. Coordinator failure is the operational nightmare. Most modern systems avoid 2PC because of the cost. The saga patterns in [[hard-parts-pattern-catalog]] §8 are the answer to "we'd like atomicity but cannot afford 2PC."

## 9. Consensus and total order — when you actually need it

Consensus is *expensive* — you only want it where genuinely required. Kleppmann's list of places where consensus is unavoidable:

- **Linearizable storage** (compare-and-swap registers across nodes).
- **Uniqueness constraints** across partitions (username assignment, slot booking).
- **Atomic transaction commit** across multiple nodes (2PC's coordinator decision).
- **Leader election** (without consensus, you can have split-brain).
- **Total order broadcast** — equivalent to consensus; the foundation of state machine replication.

**ZooKeeper / etcd / Consul** exist for this. Architectural pattern: **don't reimplement consensus.** Outsource it to a system that has done the proofs.

**Total order broadcast** is the single most useful primitive in this space — every node receives every message in the same order. State machine replication: have every replica apply the same operations in the same order, they end up in the same state. This is *also* the conceptual foundation of event sourcing and log-based architectures (§10).

## 10. Batch, streams, and derived data — the log-centric perspective

Part III is the most architectural section of the book. The central claim:

> **The log (an append-only, totally-ordered sequence of events) is the underlying primitive most data systems can be built on.** Replication is a log. Stream processing is a log. Event sourcing is a log. The transaction WAL is a log. CDC is a log read out of a database into a stream.

### 10.1 Batch processing (MapReduce lineage)
- **Inputs are immutable**, outputs are new files. Re-running a job is safe.
- **Joins** in MapReduce: sort-merge join, broadcast hash join, partitioned hash join.
- **The Unix philosophy applied to data** — small composable tools, log-and-pipe interfaces. Influential beyond Hadoop.

### 10.2 Stream processing
- **Events as the unit of data movement** between systems.
- **Change Data Capture (CDC)** — turning database writes into a stream other systems can subscribe to. The escape hatch from the dual-write problem (two systems written to atomically — which fails by §8).
- **Event sourcing** — store the log of events as the system of record; derive current state by replaying. The current state is a *cache* over the events.
- **Stream-table duality** (Jay Kreps / Confluent, popularised by Kleppmann) — a table is a snapshot of a stream; a stream is a sequence of changes to a table.
- **Stream joins** are *temporal* — windowed, with attention to event time vs processing time, watermarks for late-arriving data.

### 10.3 Effectively-once and end-to-end correctness
- **"Exactly-once delivery" is a misnomer** — Kleppmann's preferred framing is *effectively-once* achieved through **idempotent operations** (operations safe to retry) plus end-to-end design. Where idempotence isn't natural, transactional writes + offset commits in the same transaction are the alternative. The property must hold across the entire pipeline, not just at the broker.
- **The end-to-end argument** (Saltzer/Reed/Clark, 1984): if you need a property guaranteed end-to-end, you must implement it end-to-end. Lower-layer "best-effort" guarantees don't compose.

→ This connects directly to [[hard-parts-pattern-catalog]]#6.3 ("event-based eventual consistency"). The skill should treat "durable subscribers / persistent log" as the entry point and *exactly-once delivery* as a downstream architectural concern requiring explicit design.

## 11. The unbundled database

Kleppmann's closing claim, which has shaped a decade of architectural thinking:

> **A traditional database bundles transactions, indexing, replication, caching, full-text search, materialised views, and durability into one box. Modern distributed systems unbundle these into separate, specialised systems composed via a shared log.**

The log (Kafka / Pulsar / Kinesis) becomes the integration layer. Each downstream system (search index, cache, OLAP store, materialised view) is a derived projection over the log. The "system of record" is the log itself.

The architectural implication: **derived data is the cheapest thing in a well-designed system.** Need a new query shape? Build a new index off the log. Need analytics? Stream the log into an OLAP store. The cost of a new view is *just the projection logic*, not new I/O contention on the OLTP store.

→ This is the same insight as [[moseley-marks-tar-pit]] §6.1 — derived data is *accidental*, re-derive don't store-and-sync — applied at the distributed-systems scale. Kleppmann's log-centric architecture is the operational mechanism that makes the Tar Pit principle practical.

---

## Pattern → Decision lookup

| If the question is… | Reach for §… |
|---|---|
| "What latency target should we set?" | §1 — percentiles, not means |
| "Should this be a JSON store or a relational store?" | §2 — relationship shape decides |
| "How do we evolve this contract without breaking consumers?" | §3 — schema evolution by format |
| "What happens when the leader fails?" | §4 — sync vs async; failover hazards |
| "Why is one partition slow?" | §5 — hot-spot risk by partition strategy |
| "We need stronger consistency — what does that cost?" | §6 — name the consistency model first |
| "What's actually unreliable here?" | §7 — networks, clocks, knowledge |
| "Will this transaction handle concurrent updates correctly?" | §8 — isolation levels and anomalies |
| "Do we need ZooKeeper / etcd for this?" | §9 — consensus is expensive; outsource it |
| "How do we build derived views without dual-write?" | §10 — log + CDC + stream processing |
| "How do we organize this data platform?" | §11 — the log as the integration layer |

## Cheat-sheet (for skill prompts)

| Concept | One-line |
|---|---|
| **Reliability = fault-tolerant** | Faults are normal; failures are when faults propagate to the user |
| **Always quote p95/p99** | Means lie; the angry user lives in the tail |
| **Schema is implicit if not explicit** | Schemaless = schema in every reader |
| **Data outlives code** | Encoding choice is a 5+ year commitment |
| **Replication lag is a property, not a bug** | Read-your-writes, monotonic reads, consistent prefix |
| **CAP is too coarse** | Name the consistency model: linearizable, causal, eventual |
| **Linearizability requires consensus** | Outsource consensus to ZK/etcd; don't reimplement |
| **Clocks are unreliable** | Use logical clocks for ordering; fencing tokens for locks |
| **Snapshot isolation has write skew** | Serializable is the only level that prevents all anomalies |
| **2PC ≈ avoid in practice** | The saga patterns exist because 2PC operationally hurts |
| **The log is the primitive** | Replication, event sourcing, CDC, stream processing — all logs |
| **Stream-table duality** | A table is a snapshot of a stream; a stream is changes to a table |
| **End-to-end argument** | If you need exactly-once, design the whole pipeline for it |
| **Derived data is free** | New views are projections; the cost is logic, not contention |

## Self-check questions

1. What's my latency target, and at what percentile?
2. What's the consistency model this design needs — strictly linearizable, causal, or eventual? Have I named it?
3. Where is data flowing through the network, and what happens to each step under partition?
4. Which clocks am I depending on, and have I assumed they agree?
5. What isolation level does this transaction actually run at, and which anomalies can still occur?
6. Am I about to reimplement consensus? Should this be ZooKeeper / etcd instead?
7. Where in this design am I writing to two systems? Is one of them a log (CDC, event) or am I about to invent the dual-write problem?
8. What replica lag will the user experience, and which UX anomaly will appear?
9. If this leader crashes right now, what data could be lost? What's the failover blackout window?
10. Is this derived data, and could I just re-project it from the log instead of storing it?

---

## How this fits with the others

- **[[hohpe-architect-principles]]** §2 (risk reduction): Kleppmann gives the architect concrete vocabulary for *which* risks. "We have replication lag" is sharper than "we have a consistency risk."
- **[[richards-ford-architect-principles]]** §12 (the 8 fallacies): DDIA §7 is the *why* behind every fallacy. The skill should pair them — fallacy on the checklist, DDIA chapter as the deeper read.
- **[[hard-parts-pattern-catalog]]** §6–8 (consistency, workflow, sagas): Hard Parts names the pattern; DDIA names the consistency model the pattern lands at. Always pair them in a recommendation.
- **[[moseley-marks-tar-pit]]** §6.1 (derived data is accidental state): DDIA §10–11 is the operational mechanism. Kleppmann's log-centric architecture is the engineering pattern that makes the Tar Pit principle practical at scale.

**Closing observation:** the four other references treat data as something that *exists* in the system. DDIA treats data as something that *flows* through it. That shift — from data-at-rest to data-in-motion — is the single most important reframe DDIA gives the architect.
