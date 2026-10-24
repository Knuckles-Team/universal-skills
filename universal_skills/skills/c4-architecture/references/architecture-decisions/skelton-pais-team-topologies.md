---
source: "Team Topologies: Organizing Business and Technology Teams for Fast Flow — Matthew Skelton & Manuel Pais, IT Revolution Press 2019 (ISBN 978-1-942-78828-5)"
purpose: "The organisational lens the other references assume but don't articulate. [[hard-parts-pattern-catalog]] tells you how to split services; Team Topologies tells you how to split teams — and why getting the second wrong makes the first impossible to sustain."
relation_to_others: "Conway's Law as a first-class architectural force. Hohpe's political-capital model addresses the architect's individual posture; this addresses the *structural* effect of team layout on system shape. The two halves of the same problem."
note_on_method: "Author distillation from working knowledge of the text, not a primary-source extraction. Verify load-bearing claims against the book before relying on them in production skill output."
---

# Skelton & Pais — Team Topologies (Distilled)

## Why this reference exists

> Organizations which design systems… are constrained to produce designs which are copies of the communication structures of these organizations. — **Melvin Conway, "How Do Committees Invent?", *Datamation*, 1968**

(The "inevitably produce" paraphrase that circulates widely is Conway's own later restatement on melconway.com, not the 1968 paper's wording.)

Conway's Law is cited in every architecture book, including the others in this directory. It's then usually treated as a curiosity rather than a constraint. Team Topologies makes the opposite move: treats it as the *first* constraint — if you don't choose your team structure intentionally, the team structure will choose your architecture for you.

The architectural payoff: in modern distributed systems, **most of the failures the Hard Parts catalog tries to fix are downstream of misaligned team boundaries.** A microservices estate where deployments must coordinate across teams isn't a bad microservices implementation — it's the right implementation of a team structure that needed a monolith.

## 1. Conway's Law as architectural force

Two operational consequences the architect must internalise:

**Forward Conway:** the team structure today *will* shape the system tomorrow. Three teams will produce three subsystems, regardless of the architect's diagrams.

**Inverse Conway Maneuver** (term coined by Jonny Leroy & Matt Simons, ThoughtWorks, *Cutter IT Journal* 2010; adopted and operationalised by Skelton & Pais): *deliberately* shape the team structure to produce the architecture you want. If you want loosely-coupled services, you need loosely-coupled teams. If you want one cohesive product, you need one cohesive team.

> **The architect's leverage is highest at team-design time, not at architecture-design time.** Choosing how teams are bounded *is* choosing how the system will be bounded. Six months later, the architect is just describing what the org has already decided.

This is the missing piece in Hard Parts §2 (granularity disintegrators/integrators): the structural pressure the catalog catalogues is *also* organisational pressure. The architect who applies disintegrators without also splitting teams produces a service estate that the team can't operate. The architect who applies integrators without consolidating teams creates a "monolith" that's still three teams pretending to be one.

## 2. Cognitive load — the resource being allocated

The book's most under-used contribution: treating cognitive load as a *measurable, finite* architectural constraint.

> A team has a fixed cognitive capacity. The system it owns must fit within that capacity, or the team will fail to maintain it sustainably.

Three categories (from cognitive science, applied to software):

| Cognitive load type | What it covers | Architectural lever |
|---|---|---|
| **Intrinsic** | The inherent difficulty of the problem domain | Team selection (hire/grow expertise) |
| **Extraneous** | Accidental difficulty — toolchains, deployment, environment quirks | Platform team can absorb this |
| **Germane** | The "good" load — building mental models of the domain | What you *want* the team focused on |

The architect's job: **maximise germane load, minimise extraneous load, match intrinsic load to team capacity.** A team carrying three repositories' worth of toolchain quirks (high extraneous) has less capacity left for the actual domain (germane).

**Cognitive-load test for service ownership:** if the team that owns a service can't, in a one-hour conversation, describe its responsibilities, dependencies, and failure modes — the team owns too much. The architect's options: shrink the service, split the team, or move some responsibility to a platform (§3.2).

→ This is the empirical lens behind Hard Parts §2's modularity drivers. "Maintainability" and "deployability" are *cognitive-load* concerns at heart. Naming them as such gives the trade-off conversation actual teeth.

## 3. The four fundamental team types

Skelton & Pais argue that almost every team in a software organisation should fit one of four patterns. Other shapes (architecture team, DBA team, devops team, QA team) are usually anti-patterns — they create handoffs that destroy flow.

### 3.1 Stream-aligned team
The default and most common. Owns end-to-end flow for a slice of value — usually a product, feature area, or business capability.

| Property | Description |
|---|---|
| **Owns** | A value stream — code, deployment, runtime, on-call, customer feedback |
| **Cognitive load** | Bounded to *one* domain area; the team can fit it in their heads |
| **Long-lived** | Yes — teams don't disband when "the project ships" |
| **Optimised for** | Speed of flow from idea to production |

In a healthy org, **most teams are stream-aligned.** The other three types exist to *support* stream-aligned teams, not to replace them.

### 3.2 Platform team
Provides internal self-service capabilities that stream-aligned teams consume on demand.

| Property | Description |
|---|---|
| **Owns** | A platform — e.g. a deployment system, an observability stack, a data pipeline runtime |
| **Customers** | Other internal teams (the stream-aligned ones) |
| **Interaction** | Mostly X-as-a-Service (§4) — clear API, low-touch |
| **Mission** | Reduce extraneous cognitive load for the stream-aligned teams |

The book's term **"the thinnest viable platform" (TVP)** is the most important platform-design heuristic in the catalog:

> A platform should be only as big as it needs to be to remove extraneous load from stream-aligned teams. Build the platform when teams are repeatedly solving the same problem; not before. Resist the platform's natural drift toward generality.

→ Maps onto Hard Parts §3.4 (sidecars / service mesh): a platform team is the *organisational* answer to "shared operational concerns." Sidecars are the *technical* implementation.

### 3.3 Enabling team
Short-lived, expert helpers. Pair with a stream-aligned team for weeks to months to lift their capability in a specific area (e.g. observability, performance tuning, security hardening).

| Property | Description |
|---|---|
| **Lifecycle** | Joins a stream-aligned team, transfers skill, leaves |
| **Mission** | Make stream-aligned teams *more autonomous*, not dependent |
| **Anti-pattern** | An enabling team that becomes a permanent gatekeeper |

The "architecture team" should usually be an enabling team, not a separate ongoing organisation. The architect's role often *is* an enabling role: parachute in, level up the stream-aligned team's understanding, withdraw.

### 3.4 Complicated-subsystem team
Owns a system whose inherent complexity is so high it would dominate any stream-aligned team's cognitive budget. Examples: a numerical solver, a video codec, a machine-learning model, a real-time pricing engine.

| Property | Description |
|---|---|
| **Owns** | One small, deep system with high intrinsic complexity |
| **Composition** | Specialists — the system genuinely requires their expertise |
| **Interaction with stream-aligned teams** | X-as-a-Service — the stream-aligned team consumes through an API |
| **Test for whether you actually need one** | A regular team has tried, struggled, and the complexity is genuinely inherent (not extraneous) |

Distinguish carefully from a *platform team*. Platform teams package common-but-difficult work (CI/CD, deployment). Complicated-subsystem teams own *uncommon-and-difficult* work (the pricing model, the optimiser). Mistaking one for the other is common.

## 4. The three interaction modes

How teams *interact* matters as much as how they're structured. Naming the interaction mode prevents the silent mode-drift that produces dysfunction.

### 4.1 Collaboration
Two teams work closely together for a defined period.

- **Bandwidth:** high. Conversations daily; shared planning.
- **Use when:** discovering new domain territory; integrating two systems for the first time.
- **Cost:** cognitive load on both teams goes up.
- **Failure mode:** "temporary" collaboration becomes permanent. The two teams effectively become one without the structural acknowledgement.

### 4.2 X-as-a-Service
One team consumes a capability from another team via a clear contract.

- **Bandwidth:** low. The contract does the talking.
- **Use when:** the provider team's capability is well-understood and stable.
- **Cost:** less for the consumer than collaboration; more for the provider (they must maintain the service quality).
- **The default for platform teams.**

### 4.3 Facilitating
One team coaches another for a defined period — the enabling team's natural mode.

- **Bandwidth:** medium.
- **Use when:** lifting capability, not delivering features.
- **Failure mode:** the facilitating team starts *doing the work* instead of teaching it.

**The book's central operational discipline:** name the interaction mode for each team-to-team relationship, write it down, revisit it quarterly. Modes drift silently — a Collaboration that worked for the first 3 months should usually have transitioned to X-as-a-Service by month 6.

→ Connects to [[hard-parts-pattern-catalog]] §9 (contracts): X-as-a-Service interactions require contracts. Choose the contract style (strict, loose, consumer-driven) deliberately based on the interaction mode and the teams' coordination cost.

## 5. Fracture planes — where to split

When decomposing a monolith or designing a new system, *where* should the boundaries fall? The book's list of **fracture planes** is a checklist of legitimate splitting criteria:

| Fracture plane | When it applies |
|---|---|
| **Business domain** | The system has clear subdomains (the [[evans-vernon-ddd-distilled]] case) |
| **Change cadence** | Some parts change weekly, others yearly — Hard Parts disintegrator "code volatility" |
| **Team location** | Geographically distributed teams; reduce cross-timezone coordination |
| **Risk** | Regulated parts (PCI, HIPAA) isolated from general-purpose code |
| **Performance isolation** | Latency-critical paths protected from batch workloads |
| **Technology** | An ML component naturally lives in Python regardless of the rest of the stack |
| **User persona** | Internal admin tools vs end-user experience |
| **Compliance** | Different audit/sovereignty requirements per region |

**The discipline:** when proposing a service split, *name the fracture plane*. If you can't name one — or if the named one is weak — the split is probably premature. Hard Parts disintegrators are a subset of these fracture planes, framed technically; Team Topologies adds the organisational ones.

→ This is the strongest direct complement to Hard Parts §2. A skill checking a granularity proposal should walk both lists.

## 6. Team-first architecture

*("Team-first architecture" is this file's framing of Skelton & Pais's "team-first approach" / "team-first thinking." The substantive claim — architecture should follow team structure — is theirs; the phrase is the author's gloss.)*

The reversal at the heart of the book:

> **Don't design the architecture and then assign teams to it. Design the teams and then let the architecture emerge to fit them.**

Practical consequences:

- **Team size is a hard constraint.** Dunbar's number (~150 for any group; ~15 for close working trust; ~5–9 for a single team) puts a ceiling on what one team can own. Architecture must respect this.
- **A team is long-lived.** If the architecture requires teams to disband and re-form for each project, the architecture is fighting the org.
- **Service ownership defaults to one team.** Two teams co-owning a service is a smell — it usually means one team should own it and the other should consume it via a contract.

The architect's posture under this principle:

- Before recommending an N-service split, ask: *do we have N teams? Will we?*
- Before recommending a platform team, ask: *do we have enough stream-aligned teams that the platform team has customers?*
- Before recommending a complicated-subsystem team, ask: *do we have the specialists, and is the complexity actually inherent?*

This is the principle behind the most common ill-fated re-org: "we want to do microservices" leads to a service estate the team count can't sustain. Three teams cannot operate fifteen services. The catalog will not save them.

## 7. The Inverse Conway Maneuver — when and how

The deliberate counterforce to Conway's Law. Used when the *current* team structure is producing the wrong architecture.

**The move:**
1. Identify the target architecture (what coupling pattern do you want?).
2. Design the team structure that would naturally produce that architecture.
3. Restructure the teams.
4. *Then* let the architecture follow.

**When it works:**
- Senior leadership has the authority and willingness to restructure.
- The change is communicated as deliberate (not a downsizing).
- New team boundaries align with skill clusters that already exist.

**When it doesn't:**
- Team boundaries cut across required skill sets — every team now has gaps.
- The restructure is done for political reasons and architecture is the justification.
- The new team boundaries don't match the domain boundaries — Conway's Law works against you in a different direction.

→ Pair with [[hohpe-architect-principles]] §9 (political capital): the Inverse Conway Maneuver is *expensive* in political capital. It's the right place to spend a year's worth, not a routine move.

## 8. Connecting Team Topologies to the other references

### 8.1 To Hard Parts (the catalog)
- **§1 Modularity** — "modular monolith" is a valid topology choice for a small team count. Don't recommend microservices unless team structure supports it.
- **§2 Granularity** — pair granularity disintegrators with fracture planes. A service granularity that no stream-aligned team can own is wrong granularity.
- **§3 Reuse** — sidecars/service mesh maps to platform team ownership. If there's no platform team, sidecars become an orphaned concern.
- **§4 Data ownership** — single ownership maps to "one team owns the writer." Joint ownership often signals two teams should be one, or the bounded context was split wrong.
- **§7 Workflow coordination** — orchestration's "central narrator" service needs an owner team; choreography distributes ownership across teams that must all be capable.

### 8.2 To DDD ([[evans-vernon-ddd-distilled]])
Bounded contexts and team boundaries should usually align. This is the underlying claim of "team-first architecture":
- One team per bounded context (default).
- One context per team (default — a team can own more *if* the cognitive load fits).
- Cross-context integration (§5 of DDD) is *also* cross-team interaction (§4 of this file).

### 8.3 To Richards/Ford
- §3 (8 expectations) → the architect's role itself is mostly an enabling-team mission.
- §9 (architect personalities) → the Control Freak/Armchair calibration applies *within* a team; Team Topologies applies *between* teams.

### 8.4 To Hohpe
- §9 (political capital) → Inverse Conway is one of the big political-capital expenditures.
- §6 (phantom sketch artist) → enabling teams operate the same way as the phantom sketch artist: extract the team's knowledge, play it back sharper, leave.

---

## Pattern → Decision lookup

| If the question is… | Reach for §… |
|---|---|
| "Should we adopt microservices?" | §1 — only if team structure can sustain them |
| "Why isn't this team shipping?" | §2 — likely overloaded cognitive budget |
| "Where should this responsibility live?" | §3 — match to one of the four team types |
| "Should we build an internal platform?" | §3.2 — TVP test; only if teams are repeatedly solving the same problem |
| "Do we need an architecture / DBA / devops team?" | §3 — usually no; it's enabling-team work or stream-aligned ownership |
| "How should team A and team B work together?" | §4 — name the interaction mode |
| "Where do we split this monolith?" | §5 — fracture planes checklist |
| "We have N services but only M teams" | §6 — one team per service is the floor; revisit decomposition |
| "How do we move from monolith to microservices?" | §7 — Inverse Conway Maneuver |
| "Our 'platform' keeps growing" | §3.2 — TVP discipline; resist generality |
| "We have a co-owned service" | §6 — almost always wrong; fix ownership |

## Cheat-sheet (for skill prompts)

| Concept | One-line |
|---|---|
| **Conway's Law** | Org structure shapes system structure |
| **Inverse Conway Maneuver** | Deliberately design org to produce the desired architecture |
| **Cognitive load (intrinsic / extraneous / germane)** | Finite team resource; minimise extraneous, match intrinsic |
| **Stream-aligned team** | Default. Owns end-to-end flow for a value stream. |
| **Platform team** | Provides self-service capability to stream-aligned teams |
| **Enabling team** | Short-term coach; lifts a stream-aligned team's capability |
| **Complicated-subsystem team** | Owns a deep, intrinsically-complex subsystem; specialists |
| **Thinnest Viable Platform (TVP)** | Build the platform only as big as needed to remove load |
| **Collaboration mode** | High bandwidth, time-bounded |
| **X-as-a-Service mode** | Clear API, low bandwidth, the platform-team default |
| **Facilitating mode** | Coaching by enabling team for a defined period |
| **Fracture plane** | A legitimate criterion for splitting (domain, cadence, risk, etc.) |
| **Team-first architecture** | Architecture follows team structure, not the reverse |
| **Dunbar's numbers** | ~5–9 per team; ~15 trust; ~150 total org |
| **Team longevity** | A team is a long-lived organism, not a project assignment |

## Self-check questions

1. Could every team I'm proposing fit its system in its head — operationally, in code, and on-call?
2. How many stream-aligned teams do we actually have? Does the proposed architecture work at that team count?
3. For each team-to-team relationship in this design, can I name the interaction mode (Collaboration / X-as-a-Service / Facilitating)?
4. Has any "temporary" Collaboration become permanent, signalling those teams should be merged?
5. Is the platform team I'm proposing supporting actual repeated needs, or building on speculation?
6. For each service split, can I name the fracture plane? Is it strong enough to justify the split, or am I splitting from architectural fashion?
7. Am I assigning two teams to co-own a service or system? What's the path back to single ownership?
8. Where is extraneous cognitive load high, and could a platform absorb it?
9. Does this architecture require team reorganization (Inverse Conway), and have I priced in the political-capital cost?
10. Are the team boundaries aligned with the bounded contexts ([[evans-vernon-ddd-distilled]] §3), or are we forcing teams across semantic seams?

---

## How this fits with the others

The four prior references describe the system the architect is building. This reference describes the *people* who will build and operate it. The system has properties; the team has properties; the two must match.

- **[[hohpe-architect-principles]]**: Hohpe is about the *individual architect's* posture. Team Topologies is about the *organisational structure* the architect operates within. Together: who you are, and what you're working within.
- **[[richards-ford-architect-principles]]**: §9 (team boundary calibration) applies *within* a team; this reference applies *between* teams. Use both.
- **[[hard-parts-pattern-catalog]]**: every pattern recommendation should be sanity-checked against team capacity. A sophisticated saga choreography only works if every team in the chain has the capability to participate.
- **[[evans-vernon-ddd-distilled]]**: bounded contexts and team boundaries are two views of the same boundary. DDD names the semantic side; Team Topologies names the organisational side. They should align.
- **[[kleppmann-data-intensive-applications]]**: the data-systems mechanics in DDIA are *operated* by teams. A complicated-subsystem team often owns the stream-processing infrastructure; a platform team often owns the data plane. Without a team type analysis, the data architecture has no operating model.
- **[[moseley-marks-tar-pit]]**: "power corrupts" applied to team structure — the more teams a system depends on for any single change, the harder it is to keep simple. Team Topologies makes team coupling visible, the same way Tar Pit makes complexity visible.

**Closing observation:** the other references can be applied in any order. This one has a privilege: if the team structure is wrong, no application of the other four will save the architecture. Recommend Team Topologies analysis *first* when the system is large enough that more than one team will own pieces of it. Recommend it *last* (as a check) when validating an architecture proposal someone else has made.
