---
sources:
  - "Fundamentals of Software Architecture: An Engineering Approach — Mark Richards & Neal Ford, O'Reilly 2020 (ISBN 978-1-492-04345-4)"
  - "Software Architecture: The Hard Parts — Neal Ford, Mark Richards, Pramod Sadalage, Zhamak Dehghani, O'Reilly 2022 (ISBN 978-1-492-08689-5)"
purpose: "Methodology and vocabulary that complement [[hohpe-architect-principles]]. Hohpe covers mindset, framing, and political navigation; these add the engineering discipline — definitions, laws, decision artifacts, fitness functions, trade-off methods, distributed-systems vocabulary."
relation_to_hohpe: "Pair this with hohpe-architect-principles.md. Hohpe = posture; Richards/Ford = process. Both are needed."
---

# Richards / Ford — Architect Engineering Discipline

## 1. The two Laws of Software Architecture

> **First Law:** Everything in software architecture is a trade-off.
>
> **Corollary 1:** If an architect thinks they have discovered something that *isn't* a trade-off, more likely they just haven't *identified* the trade-off yet.
>
> **Second Law:** *Why* is more important than *how*.

- "Architecture is the stuff you can't Google." There are no right or wrong answers — only trade-offs. The famous answer to every architecture question is "it depends," and it is correct.
- The Second Law is why **Architecture Decision Records** matter: a system can be reverse-engineered to recover *how*, but *why* is lost the moment the original architect leaves the room.
- Pair this with Hohpe's [[hohpe-architect-principles#10]] "suitable, not good/bad" — these laws are the engineering form of the same claim.

## 2. Definition of architecture — four dimensions

Software architecture is **not** just structure. It is the intersection of four things:

1. **Structure** — the architecture style(s) in use (layered, microkernel, microservices, etc.). Saying "it's microservices" describes structure, not architecture.
2. **Architecture characteristics** — the "-ilities" the system must support (availability, reliability, scalability, security, agility, fault tolerance, elasticity, performance, deployability, learnability, testability, recoverability…). Generally **orthogonal to functionality**.
3. **Architecture decisions** — the *rules* for how the system is constructed. (A *variance* is the formal mechanism for breaking one.)
4. **Design principles** — *guidelines* rather than rules. ("Prefer async messaging between services" is a principle; "the presentation layer cannot access the database" is a decision.)

Describing only one of the four does not describe an architecture.

## 3. The eight Expectations of an Architect

Independent of title, an architect is expected to:

1. **Make architecture decisions** — *guide* rather than *specify*. "Use a reactive frontend framework" is guidance. "Use React.js" is a technology decision; reach for it only when a specific characteristic (scalability, perf) demands it.
2. **Continually analyze the architecture** — *architecture vitality*: an architecture defined 3 years ago is today's legacy unless re-examined. Watch for *structural decay*.
3. **Keep current with latest trends** — decisions are long-lasting; out-of-date heuristics produce well-reasoned but wrong answers (echo of Hohpe's "heuristic decay").
4. **Ensure compliance with decisions** — increasingly via automated **fitness functions**, not manual review.
5. **Diverse exposure and experience** — know 10 caching products at a working level rather than one cold; **breadth beats depth**.
6. **Have business domain knowledge** — without it you can't translate requirements into characteristics, and you'll lose credibility with the C-suite fast.
7. **Possess interpersonal skills** — "no matter what they tell you, it's always a people problem." (Weinberg.)
8. **Understand and navigate politics** — *almost every decision an architect makes will be challenged*. Negotiation is not optional. (Pair with Hohpe's [[hohpe-architect-principles#9]] political-capital model.)

## 4. The Knowledge Pyramid — and why breadth wins

Partition all knowledge into:

- **Stuff you know** (your technical depth — also "stuff you must maintain")
- **Stuff you know you don't know** (heard of, can't use)
- **Stuff you don't know you don't know** (the largest tier; the perfect solution you'll never find)

Developers maximize the top. **Architects deliberately sacrifice depth to widen the middle layer** — pulling things from "don't know you don't know" into "know you don't know." Knowing five solutions exist beats being expert in one when your job is matching capabilities to constraints.

**Two failure modes:**
- *Stale expertise* — the architect who still decides by criteria from 2014.
- *Frozen Caveman Anti-Pattern* — the architect who got burned once and now treats one freak failure as a universal axiom. ("But what if we lose Italy?")

## 5. Architectural Thinking — four aspects

What distinguishes architectural thinking from "thinking about architecture":

1. **Architecture vs Design** — they are not separate phases handed off through a wall. Architect and developers must operate as one team with bidirectional flow. Decisions get lost; implementation discoveries change architecture.
2. **Technical breadth with sufficient depth** — see §4.
3. **Trade-off analysis** — see §7.
4. **Business drivers translated to characteristics** — the architect's job is to convert what the business says into measurable "-ilities."

## 6. Architecture Decision Records (ADRs)

The minimal, durable artifact for capturing *why*:

```
ADR: <short noun phrase containing the decision>

Context
  One or two sentences. The problem. The alternatives considered.

Decision
  The decision and a detailed justification.

Consequences
  What happens after this is applied. Trade-offs that were considered.
  Optionally: Fitness functions that will guard it.
```

Keep ADRs to **one or two pages**, in plain text / Markdown / AsciiDoc, in the repo. The point is not bureaucracy — it is to preserve the *why* the Second Law demands.

**Decision anti-patterns to avoid:**
- *Covering Your Assets* — refusing to decide so no decision can be wrong.
- *Groundhog Day* — same decision discussed every quarter because nobody recorded the outcome.
- *Email-Driven Architecture* — the decision lives in someone's inbox and is forgotten the day they leave.

## 7. Trade-off analysis methodology

The three-step process (from *The Hard Parts*, Ch. 15):

1. **Find what parts are entangled together.** Discover the dimensions that are actually braided in your system.
2. **Analyze how they are coupled.** Use the operational definition: *if someone changes X, will it possibly force Y to change?*
3. **Assess trade-offs by modeling impact of change to interdependent systems.**

### Techniques the authors actually use

- **Qualitative > Quantitative.** Architectures are rarely amenable to true numeric comparison. Build dimensional matrices and hone the skill of qualitative ranking. Get good at this; it is most of the job.
- **MECE lists** — *Mutually Exclusive, Collectively Exhaustive.* Don't compare a queue to an enterprise service bus (not mutually exclusive — an ESB contains a queue). Don't omit Kafka when comparing high-perf messaging (not collectively exhaustive). MECE makes apples-to-apples possible.
- **The Out-of-Context Trap.** Generic trade-off tables can favor a winner — but adding **the specific domain context** flips the answer. Trying to decide *shared service vs shared library* in the abstract favors library; the moment you add "we use four languages and care about code volatility, not performance," it flips. *Always reduce the comparison to the smallest correct context.*
- **Model relevant domain cases.** Walk specific scenarios through each candidate ("what if we add a Reward Points payment type?"). Scenario stress reveals trade-offs that generic analysis hides.
- **Prefer bottom line over overwhelming evidence.** Boil the analysis down to a few key points before presenting to nontechnical stakeholders. The synchronous-vs-async credit-card example reduces to a single question they can answer: *"Is it more important that approval is guaranteed to start, or that the system tolerates the orchestrator being down?"*
- **Avoid snake oil and evangelism.** Once you start enhancing the good and diminishing the bad about a tool, you stop being an architect. When someone tries to drag you into evangelizing one side of a debate, **refuse the frame and bring it back to trade-offs**.

> **Tongue-in-cheek but durable advice:**
> Don't try to find the *best* design in software architecture; strive for the **least worst combination of trade-offs**.

## 8. Architecture Fitness Functions — governance you can run

> A fitness function is *any mechanism that performs an objective integrity assessment of some architecture characteristic(s).*

- **Why they exist:** without them, governance is code review and architecture review boards — too late, too manual, too easy to skip under schedule pressure. Fitness functions are the **automated, runnable checklist** for the important-but-not-urgent.
- **Scope:**
  - *Atomic* — guards one characteristic (e.g., "no cyclic package dependencies" via JDepend/ArchUnit).
  - *Holistic* — guards a *combination* (security + performance, scalability + elasticity) because characteristics interact.
- **Composite characteristics:** if a desired property isn't measurable ("agility"), break it down until it is (deployability, cycle time, MTTR). If you can't measure it, you can't fitness-function it.
- **Distinguish from unit tests:** if the test requires **domain knowledge**, it's a unit/functional test. If not, it's a fitness function. (Validating a postal code = unit test. Validating elasticity = fitness function.)
- **Implementations** include: ArchUnit/NetArchTest, monitors, chaos engineering, perf tests in CI, SonarQube rules, custom integration tests, manual gated steps (for things only a human/lawyer can sign off).
- **Restraint:** fitness functions are an executable spec of architecture. They are not an excuse to build an ivory tower of nested rules that frustrates the team. Codify *important* principles, not every preference.
- **The Equifax cautionary tale:** if every project had a fitness-function slot a security team could deploy into, the Apache Struts CVE-2017-5638 vulnerability would have been caught in CI on every project, not patched 4 months later in production.

## 9. Architect personalities and team boundaries

Three archetypes (Ch. 22) — the unhealthy two and the goal:

| Type | Boundary | Behavior | Effect |
|---|---|---|---|
| **Control Freak** | Tight | Dictates class design, naming, method length, sometimes pseudo-code | Steals the art of programming; team disengages |
| **Armchair** | Loose | Disconnected from code; high-level box diagrams; "rarely available" | Team becomes the de facto architect, velocity drops |
| **Effective** | Appropriate | Sets the right constraints, removes roadblocks, available to the team | Team owns implementation; architecture is real |

### "How much control?" — five factors (calibrate per project)

1. **Team familiarity** — strangers need more control; people who've shipped together need less.
2. **Team size** — >12 ≈ big (more control); ≤4 ≈ small (less). Watch for Brook's-law process loss.
3. **Overall experience** — senior-heavy → less control / more facilitation; junior-heavy → more mentoring.
4. **Project complexity** — complex projects pull the architect in; simple ones don't.
5. **Project duration** — counter-intuitive: *shorter* projects need *less* architect control (the team already feels urgency); *longer* projects need *more* (drift sets in).

Each scored on a ±20 scale; the sum tells you which archetype to *lean* toward for *this* engagement. The scoring is a heuristic, not a metric — the point is to make the calibration *conscious*.

### Team warning signs that demand intervention

- **Process loss** (Brook's law) — frequent merge conflicts mean people are working on the same code; carve out parallel streams.
- **Pluralistic ignorance** — everyone publicly agrees with a norm they privately reject. The Emperor's New Clothes failure. Watch faces and body language; a facilitator must surface dissent.
- **Diffusion of responsibility** — as team size grows, ownership dissolves. If nobody knows who owns X, the team is too big.

## 10. Architecture vs Design — keep the definitions simple

A constant area of struggle. The Hard Parts authors' rule: **stay on the architecture side of the line by leaning on minimal, almost simplistic definitions**.

```
Service      A cohesive collection of functionality deployed as an independent executable.
Coupling     X and Y are coupled if a change in one might require a change in the other.
Component    Architectural building block — usually a package/namespace/directory.
Sync comm.   Caller waits for the response before proceeding.
Async comm.  Caller does not wait.
Orchestrated A workflow with a dedicated coordinating service.
Choreographed A workflow with no coordinator; services share responsibility.
Atomicity    All parts of a workflow maintain a consistent state at all times.
Contract     The interface between any two software parts (calls, deps, schemas, anything).
```

Why this matters: arguing about *the implementation* (Kafka vs RabbitMQ) buries the architectural question (sync vs async). Force the conversation up one level.

## 11. The three dimensions of distributed coupling

When evaluating any distributed-architecture pattern, score it on three axes:

- **Communication** — synchronous / asynchronous
- **Consistency** — atomic / eventual
- **Coordination** — orchestrated / choreographed

Plus the four trade-off concerns the analysis is for:

- **Coupling level**, **complexity**, **responsiveness/availability**, **scale/elasticity**.

Two empirical observations that fall out of the matrix:

1. **Coupling level is inversely correlated with scale/elasticity.** More coupling → harder to scale.
2. **Coupling level is inversely correlated with responsiveness/availability.** More services in the synchronous critical path → more ways for the workflow to fail.

This is *why* "loosely coupled" is a refrain — but the architect's job is still to weigh it against complexity, which loose coupling *increases*.

## 12. The 8 Fallacies of Distributed Computing

Anyone designing a distributed system who hasn't internalized these will rediscover them painfully. From Ch. 9 of *Fundamentals*:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. The topology never changes.
6. There is only one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

When making a distributed-vs-monolithic call, walk through each fallacy and write down what you're paying for it. If you can't articulate the cost, you haven't designed; you've assumed.

## 13. Checklists — small, automatable, and Hawthorne-aware

Three checklists pay for themselves:

- **Developer Code Completion** — formatting, absorbed exceptions, hardcoded values, project-specific gotchas.
- **Unit & Functional Testing** — edge cases QA tends to find that devs tend to skip.
- **Software Release** — the most volatile one; grow it from every failed deployment's post-mortem.

Rules:
- Don't list **procedural** steps (those are runbooks). Checklists are for items that get skipped *because they feel obvious or unimportant*.
- **Automate items out** of the checklist as soon as you can — a long checklist will be ignored (law of diminishing returns).
- **Hawthorne effect:** people behave better when they think they're being watched. Spot-check checklists occasionally; the team will treat them as real even when you aren't checking.

## 14. Hands-on coding — don't become the bottleneck

The architect must keep coding to keep heuristics fresh — but not *on the critical path*. Concrete patterns:

- Build **proofs-of-concept** to validate decisions — write production-quality code; throwaway POCs leak into the repo.
- Take **tech-debt and bug-fix stories** off the team's queue.
- Build **dev-experience automation** for the team's repetitive tasks.
- Write the **fitness functions** themselves — they double as governance and as coding practice.
- Do **code reviews** — both mentorship and compliance.

(This is the engineering complement to Hohpe's [[hohpe-architect-principles#8]] heuristic-decay principle.)

## 15. The 20-Minute Rule and Personal Radar

For keeping current (Ch. 24 of *Fundamentals*):

- **20-Minute Rule** — 20 minutes a day, *every* day, on something at your "stuff you know you don't know" frontier. Best slot: morning, before context-switch tax.
- **Personal Technology Radar** — your own version of the ThoughtWorks radar with **Adopt / Trial / Assess / Hold** rings. Map what you're betting on, experimenting with, watching, and refusing. Re-run quarterly. This is the structured version of Hohpe's "be the social geek."

## 16. The 4 C's of Architecture (Ch. 23)

What a software architect must be a leader in:

- **Communication** — speak to engineers, product, and execs each in their language.
- **Collaboration** — with developers (you cannot dictate), with peers (no single architect owns the whole truth), with stakeholders.
- **Clarity** — diagrams, ADRs, and trade-off tables that a reader can pick up cold.
- **Conciseness** — bottom-line over evidence-dump; one slide beats ten.

Pair with: *Be pragmatic, yet visionary.* Pragmatic = ship the thing the business needs by Friday. Visionary = make sure Friday's thing doesn't paint Tuesday's team into a corner.

---

## Cheat-sheet of definitions and frameworks (for skill prompts)

| Concept | One-line definition |
|---|---|
| **First Law of SA** | Everything in software architecture is a trade-off |
| **Second Law of SA** | Why is more important than how |
| **Architecture quantum** | An independently deployable artifact with high functional cohesion, high static coupling, and synchronous dynamic coupling |
| **Architecture characteristic** | An "-ility" the system must support — orthogonal to functionality |
| **Fitness function** | Any mechanism that performs an objective integrity assessment of an architecture characteristic |
| **ADR** | 1–2 page record: Context · Decision · Consequences |
| **MECE list** | Mutually Exclusive, Collectively Exhaustive comparison set |
| **Out-of-Context Trap** | Trade-off conclusion flips when domain-specific drivers are added back in |
| **Knowledge pyramid** | Stuff you know / know you don't know / don't know you don't know |
| **20-Minute Rule** | Daily slot at the "stuff you know you don't know" frontier |
| **Frozen Caveman Anti-Pattern** | Generalizing one historical scar into a universal axiom |
| **Brook's Law (process loss)** | Adding people to a late project makes it later |
| **Pluralistic ignorance** | Public agreement with a privately rejected norm |
| **Coupling (operational)** | X and Y are coupled if changing one *might* force the other to change |
| **Suitable, not Good/Bad** | Architectures are judged against intent and trade-offs, not a leaderboard |
| **Least-worst trade-offs** | The architect's actual job — there is no "best" |

## Architect self-check questions

1. What trade-off am I *not yet seeing* in this decision? (Corollary 1)
2. Have I written down *why*, or only *how*? If I leave, will the team be able to revisit this decision intelligently?
3. Which architecture characteristics are at stake here, and how would I measure them?
4. Is my comparison **MECE**? Am I comparing apples to apples, and have I included all the real options?
5. What domain-specific context, if added, would flip the verdict? (Out-of-Context Trap)
6. Could this rule live as a **fitness function** instead of a meeting?
7. Which of the 8 fallacies of distributed computing am I implicitly assuming away?
8. On the Control-Freak ↔ Armchair scale, am I in the right zone *for this team, right now*?
9. Where on the knowledge pyramid does my current decision sit — am I confident, or am I bluffing from "stuff I knew" in 2018?
10. If I'm being pulled into evangelizing, am I refusing the frame and bringing the conversation back to trade-offs?

## How this complements [[hohpe-architect-principles]]

| Hohpe gives you… | Richards/Ford gives you… |
|---|---|
| Amplifier mindset, jester role | The 8 expectations of the role |
| "Map the map" — framing | MECE lists, three-dim coupling matrix |
| Visual ping-pong, phantom sketch artist | Diagrams as semantically loaded artifacts; ADRs for capture |
| Cartographer → Scout (purpose-driven) | Three-step trade-off methodology, scenario modeling |
| Heuristic decay | Knowledge pyramid, 20-Minute Rule, Personal Radar |
| Political capital | "Almost every decision will be challenged"; 4 C's; team-boundary calibration |
| Suitable, not Good/Bad | First Law + Corollary 1 (trade-offs all the way down) |
| Executive elevator (story + rigor) | "Prefer bottom line over overwhelming evidence" |
| Wile E. Coyote project | Frozen Caveman Anti-Pattern, Pluralistic Ignorance |
| AI tooling as amplifier | Fitness functions as the executable spec your AI output must pass |
| Don't stumble on the finish line | "Strive for the least worst" — explicit permission to stop optimizing |

**Use both together.** Hohpe sets the **posture**; Richards/Ford gives the **process**. A skill built on either alone produces an architect that is either a clever-but-undisciplined consultant, or a rigorous-but-blind technician.
