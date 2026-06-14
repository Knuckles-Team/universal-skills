---
source: "Out of the Tar Pit — Ben Moseley & Peter Marks, February 6, 2006 (paper, ~65pp). Free; circulated as the canonical statement that complexity, not lines-of-code, is the architect's enemy."
purpose: "A complexity-first lens for design decisions. The reference the architect skill should pull from when the question is 'where is the *avoidable* difficulty in this system?' rather than 'which pattern fits?'"
relation_to_others: "Sits underneath [[hohpe-architect-principles]] — Hohpe's §3 (inherent vs accidental complexity) is the same distinction, applied to the architect's posture. Sits alongside [[richards-ford-architect-principles]] §1–2 (trade-offs and modularity) — Moseley/Marks tells you *which* trade-offs actually buy simplicity. Critiques most of the choices catalogued in [[hard-parts-pattern-catalog]] from one axis: how much state and control does this pattern force into the system?"
note_on_paradigm: "The paper's positive proposal (Functional-Relational Programming / FRP) is not widely adopted and is **not** what to mine here. The *diagnostic* — what causes complexity and what to do about it — is what makes the paper canonical."
---

# Out of the Tar Pit — Complexity as the Architect's First Concern

## Why this reference exists

Hohpe gives the architect a posture. Richards/Ford gives a process. The Hard Parts gives a catalogue of patterns. None of them, on their own, tells you *what makes one design simpler than another*. This paper does. It is the most disciplined statement in the literature of the claim:

> **Complexity is the only significant problem in software. Everything else (unreliability, late delivery, poor security, even poor performance) is downstream of it.**

The paper has two halves. The first half — the diagnosis — is the part the architect skill should know. The second half (the Functional-Relational Programming proposal) is the authors' positive sketch; it is not load-bearing for the architect's day job and is summarized only briefly at the end.

## 1. The central claim

Brooks' "No Silver Bullet" listed four hard properties of software: Complexity, Conformity, Changeability, Invisibility. Moseley & Marks argue the other three either *are* forms of complexity or matter *because* of complexity. **Complexity is the single root problem.** They part from Brooks on one critical point: Brooks held that most remaining complexity is essential. **Moseley & Marks disagree** — they argue most of the complexity in real systems is accidental, and the goal of software engineering should be its elimination.

> "Simplicity is **Hard**." — restated three times in the paper.

The kind of complexity at issue is **what makes large systems hard to understand**. This has nothing to do with complexity theory (Big-O). A trivially short program can be in the highest complexity class but be entirely understandable; a 200KLOC enterprise system can have low computational complexity and still be impossible to reason about.

## 2. Why complexity is the right target — the understanding argument

Two mechanisms exist for understanding a system:

- **Testing** — black-box, from the outside. "A test of any kind on a system using one set of inputs tells you *nothing at all* about its behaviour given a different set of inputs." Testing can show the presence of bugs, never their absence (Dijkstra).
- **Informal reasoning** — white-box, from the inside. Always used (it's how you write code), inherently imprecise, prone to error.

Both have hard limits. Therefore:

> "Improvements in *informal reasoning* will lead to **less errors being created**, whilst all that improvements in testing can do is to lead to **more errors being detected**."

Architects should care *more* about decisions that improve informal reasoning than about decisions that improve testability — even though both matter. **Simplicity is more important than either testing or reasoning**, because it improves *all future attempts* to understand the system, by any method.

→ Lines up with the closing line of [[hard-parts-pattern-catalog]] ("a pattern without a test is folklore"): both are true. Test the claims; but reach for designs whose claims are *easy to reason about in the first place*.

## 3. The three causes of complexity

### 3.1 State — the single biggest contributor

> "The single biggest remaining cause of complexity in most contemporary large systems is **state**, and the more we can do to *limit* and *manage* state, the better."

Why state is so corrosive:

- **State doubles the state space per bit.** Every bit of state added doubles the number of possible system configurations. Mental case-by-case simulation buckles as states multiply.
- **Tests in state A tell you nothing about behaviour in state B.** This compounds with the existing problem that tests with input X tell you nothing about behaviour with input Y. The two combine "horribly."
- **Contamination.** A stateless procedure that *indirectly* calls a stateful one becomes contaminated — all bets are off. "When you let the nose of the camel into the tent, the rest of him tends to follow."
- **Tester's-and-supporter's anecdote** — "try it again," "reboot," "restart the program," "reinstall." Every one of those is the system getting into a hidden bad state.

The paper distinguishes **mutable state** (the villain) from **immutable single-assignment values** (not the villain).

### 3.2 Control — the order in which things happen

Control is "basically about the order in which things happen." The trouble:

- Most languages **force you to specify order** (statement sequencing) even when the order is irrelevant. You over-specify *how* when you only meant to specify *what*.
- A reader of the code must mentally re-run the would-be compiler to figure out whether the textual ordering is significant.
- Concurrency makes it worse: tests can no longer be assumed reproducible. "Things can't really get any worse than that."

### 3.3 Code volume

Mostly a secondary effect — most code exists to manage state or specify control. But it deserves its own slot because it's the *only* form of complexity that's easy to measure, and because volume interacts badly with the other two. Dijkstra's hope (that intellectual effort can grow *linearly* with code length if abstraction is used well) only holds once you've controlled state and control first.

### 3.4 Secondary / "other" causes

Three folk laws the paper names. These are useful aphorisms for skill prompts:

- **Complexity breeds complexity.** Duplicated code, missed abstractions, dead code, poor modularity — all caused by *prior* complexity making the existing system unclear. Time pressure plus opacity = duplication, every time.
- **Simplicity is Hard.** The first solution is rarely the simple one. Simplicity must be **recognised, sought, and prized.** Don't expect it to fall out by accident.
- **Power corrupts.** "In the absence of language-enforced guarantees, mistakes and abuses *will* happen." This is why garbage collection is good — it *removes* a power (manual memory management) that experience showed people would misuse. **The more a language permits, the harder it is to understand systems built in it.** Restraint at the language/framework boundary is the architect's friend.

→ Hohpe's §3 ("respect inherent complexity but conquer the rest") names the destination; this section names the *mechanisms* by which complexity actually accumulates.

## 4. Essential vs Accidental — the definitions

The paper's definitions are **stricter than Brooks'** and stricter than common usage. They are the load-bearing piece of vocabulary for the rest of the argument:

- **Essential complexity** is inherent in, and the essence of, **the problem as seen by the users**.
- **Accidental complexity** is *all the rest* — every bit of difficulty the team would not have to deal with in an ideal world.

Strict reading: **bits, bytes, transistors, computers themselves are not essential** — they have nothing to do with the user's problem. Threads, loop counters, caches — if the user doesn't know what these things are, they cannot be essential.

Corollary (the test): if there is *any possible way* a team could deliver a system the users would consider correct *without* dealing with a given form of complexity, that complexity is **not essential**.

→ Use this strict definition in skill prompts. Loose usage of "essential" lets engineers smuggle in convenience.

## 5. Critique of the existing paradigms

### 5.1 OOP

Verdict: OOP is **essentially an imperative approach** descended from the von Neumann machine. It suffers heavily from state-derived and control-derived complexity.

Specific problems the paper raises:

- OOP couples state tightly with behaviour. Encapsulation (the ADT-style strength of OOP) is biased toward *single-object* constraints; *multi-object* constraints are awkward to enforce — and unclear where they should live.
- **Object identity** is *intensional* (two objects are different even if all their attributes are equal). Architects must mentally switch between intensional identity and the extensional equivalence the domain often actually wants — "serious errors can result from confusion between the two."
- OOP shared-state concurrency carries every standard problem in the book.

> "All forms of OOP rely on state (contained within objects) and in general all behaviour is affected by this state. As a result, OOP suffers directly from the problems associated with state… it does not provide an adequate foundation for avoiding complexity."

→ This is the paper at its most provocative. Use sparingly in skill prompts. The architectural takeaway is **not** "stop using OOP" — it is "when you reach for OOP, you are *defaulting to a state-heavy paradigm*. Be conscious of that, and limit state aggressively within it."

### 5.2 Functional Programming

Verdict: avoids state-derived complexity entirely (in pure FP). The system gains **referential transparency** — the result of any expression depends only on its arguments, never on anything else.

Two consequences the paper highlights:

- The **biggest weakness of testing is *partly* obliterated.** Tests on one state still mean nothing — but the "state" problem disappears, leaving only the input-space problem.
- Informal reasoning becomes "much more effective" because you can look at a function's arguments and *know* you've seen everything that can affect its result.

The honest weaknesses the paper names:

- Pure FP makes you **thread state through every call site** instead of mutating in place. There's a real ergonomic cost. (The `getNextCounter` example.) This is "a one-off up-front cost for continuing future gains."
- Monads "have not been sufficient to give rise to widespread adoption of functional techniques," and "can very easily be abused to create a stateful, side-effecting sub-language" — re-introducing the very problems you switched paradigms to escape.
- Most functional languages still **specify control** (implicit left-to-right argument evaluation), so the control-complexity problem remains.

→ The architect-skill takeaway is paradigm-neutral: **the *functional style* (avoiding hidden mutable state, preferring expressions over statements) is adoptable in stateful languages and pays the reasoning dividend wherever applied.**

### 5.3 Logic Programming

Verdict: the most interesting paradigm for *control*. Pure logic programming makes no commitment to order; the runtime infers it. Prolog gives up some of this (it specifies a depth-first, left-to-right operational order), but the *idea* of separating logic from control is the deepest takeaway from this section.

Cited approvingly: Kowalski's 1979 equation — **"Algorithm = Logic + Control"** — which becomes one of the paper's organising ideas.

## 6. The Recommended Approach — Avoid and Separate

Given accidental complexity is the target, what is the strategy?

> **AVOID** state and control where they are not essential.
>
> **SEPARATE** the residue (essential state, essential logic, accidental state and control) into distinct components, each expressed in a restricted language.

That is the entire recommendation. Everything else in the paper supports those two verbs.

### 6.1 The Ideal World — what is unavoidable?

Even in an ideal world with a perfect language and infrastructure, you still need:

```
Informal requirements  →  Formal requirements  →  (executed directly)
```

The formal requirements **must be derived with no view to execution whatsoever.** Their job is only to remove relevant ambiguity from the informal ones. This is the essence of declarative programming.

**State in the ideal world.** Classify every piece of data:

| Essentiality | Data Type | Mutability | Classification |
|---|---|---|---|
| Essential | Input | — | **Essential State** |
| Essential | Derived | Immutable | Accidental State |
| Essential | Derived | Mutable | Accidental State |
| Accidental | Derived | — | Accidental State |

*Translation:* the only state that is genuinely essential is **input data the system must still be able to refer to later.** Everything else — caches, denormalisations, materialised views, snapshots of derived data — is *accidental* in the strict sense, because logic can always re-derive it.

This single move (treating derived data as something to *re-derive* rather than to *store and synchronise*) is the architect's biggest leverage point in any system carrying a lot of state. It is the paper's deepest cut.

**Control in the ideal world.** Mostly accidental. The user does not mention sequencing in the requirements; therefore the system should not be expressing it as part of the logic.

### 6.2 Required Accidental Complexity — two legitimate reasons

Even after avoidance, *some* accidental complexity is justified. The paper names exactly two reasons:

1. **Performance.** Re-deriving a cached calculation on every read may be too slow.
2. **Ease of expression.** Some logic is most naturally written against accidental derived state (e.g. a game opponent's position is more easily expressed as evolving state than as a function of all prior inputs since `t=0`).

If accidental state must exist, it **must be declared, not procedurally managed.** The system specifies *what* the accidental state should be; the infrastructure maintains it. This eliminates the risk of state inconsistency creeping in through the system logic.

### 6.3 The four-row complexity table — the operational lens

| Complexity | Type | Recommendation |
|---|---|---|
| Essential Logic | — | **Separate** |
| Essential Complexity | State | **Separate** |
| Accidental Useful Complexity | State / Control | **Separate** |
| Accidental Useless Complexity | State / Control | **Avoid** |

When reviewing a design, walk a piece of complexity through this table and ask:

1. Is this essential to the *user's problem* (strict definition)? If yes → keep, separate.
2. If accidental, does it earn its keep through performance or ease-of-expression? If yes → keep, separate, but **declare don't procedurally manage.**
3. Otherwise → eliminate.

### 6.4 The recommended architecture — three components

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Accidental    →   Essential Logic              │
│  State and          ↓                           │
│  Control       →   Essential State              │
│                                                 │
└─────────────────────────────────────────────────┘
                  Language and Infrastructure
```

The arrows are **static references** — strict directionality:

- **Essential State** — the foundation. **Makes no reference to either of the other components.** Changes here may force changes in both other components; changes elsewhere never force changes here.
- **Essential Logic** — the heart. Expressed in terms of state — *what must be true*, not how or when state changes. May reference essential state. **Makes no reference to accidental state/control.**
- **Accidental State and Control** — the periphery. Performance hacks, control hints, derived caches. May reference the other two; the other two may never reference *it*. **Changes here are conceptually safe** — they cannot affect the meaning of the system.

> "The logic component determines the **meaning**… whereas the control component only affects its **efficiency**." (Kowalski, quoted approvingly.)

### 6.5 Restricted languages

A consequence the paper emphasises: each of the three components should ideally be expressed in a **different, restricted language** — restricted to the goal of that component, with no superfluous power.

> The weaker the language, the simpler it is to reason about. **Restraint at the language boundary is what makes the separation pay off.**

This is the §3.4 "power corrupts" principle applied as a constructive design rule. A skill that recognises this principle can call it out anywhere it sees a system using a single general-purpose language to express requirements *and* derivations *and* control flow *and* performance tweaks — typically a sign that none of them will be easy to reason about.

## 7. The positive proposal — Functional-Relational Programming (briefly)

Pages 37 onward sketch a possible implementation of the three-component architecture, called **Functional-Relational Programming (FRP)**:

- **Essential State** is expressed using the **relational model** (Codd 1970) — relations as sets of records, with declared integrity constraints. Stored data is **base relations**; derived data is **derived relations (views)**.
- **Essential Logic** is expressed as pure functions plus relational manipulations and integrity declarations.
- **Accidental State and Control** is expressed in a small "feeders / observers" layer that handles I/O and gives the runtime hints about which derived relations to materialise.

The interesting moves are:

- **Data independence** (Codd) — clean separation between logical schema and physical storage. The paper treats this as a templated example of restrained, restricted languages.
- **Derived relations** are the official answer to "what about caches and projections?" — declared, not procedurally maintained.
- **Integrity** as a first-class part of the essential layer (not validation sprinkled through controllers).

FRP is **not** widely adopted, and the skill should not advocate for it as a target architecture. What's worth lifting from this section into general practice:

- **Treat derived data as a query against base data**, not as a synchronised copy. Use materialisation as a performance hint, not a domain concept.
- **Declare integrity constraints in the layer that owns the state**, not in calling code.
- **Push subjective access-path decisions out of the data model.** OOP's `employee.department` and `department.employees` choices are access-path decisions disguised as schema — they look harmless and constrain the future system shape badly.

## Cheat-sheet (for skill prompts)

| Concept | One-line |
|---|---|
| **Complexity is the root cause** | Reliability, security, late delivery, even perf — all downstream |
| **Essential vs Accidental (strict)** | Essential = inherent to the *user's* problem; everything else is accidental |
| **State is the worst offender** | Doubles state space per bit; contaminates anything that touches it |
| **Power corrupts** | The more a language permits, the harder its programs are to reason about |
| **Simplicity is Hard** | The first solution isn't simple; simplicity must be sought |
| **Complexity breeds complexity** | Duplication, dead code, missed abstractions are *symptoms*, not causes |
| **Algorithm = Logic + Control** | Kowalski 1979; the deepest separation principle in the paper |
| **Avoid + Separate** | The whole recommendation, in two verbs |
| **Derived data is accidental** | Caches/views are *re-derivable*; treat them as queries, not as state |
| **Essential State / Logic / Accidental** | The three-component architecture; static references go one way |
| **Restricted languages per component** | Power-removal is a constructive design tool, not just a critique |
| **Performance and Ease of Expression** | The only two reasons to *keep* accidental complexity |
| **Declare, don't procedurally manage** | When accidental state is required, the system specifies *what*, infrastructure maintains *how* |

## Self-check questions for an "architect mode" skill

1. Where is the mutable state in this design, and is *any* of it strictly essential (would the *user* still recognise the system as correct without it)?
2. Which derived data am I storing that the system could re-derive on demand? What does keeping it stored cost me in consistency-management code?
3. Where is sequencing being specified that the *requirements* don't mention?
4. Is the language we're using here more powerful than the component needs? (If so, what could go wrong that a weaker language would have prevented?)
5. Does the essential logic of this system reference anything in the accidental layer? (It shouldn't.)
6. When this accidental state is wrong, will it cause an incorrect *result*, or only a slow one? If incorrect — separation has been violated.
7. Am I about to add complexity for performance? Is the performance need measured, or anticipated? (Premature optimisation is the paper's named trap.)
8. Which complexity in this system is the team merely *coping* with, when it could be *avoided* instead?
9. Are integrity constraints declared next to the state they govern, or scattered through the procedures that change the state?
10. If I removed the "accidental but useful" parts of this system, would it still produce correct results, just slowly? (If no — they aren't actually accidental.)

---

## How this fits with the other three references

- **[[hohpe-architect-principles]]** §3 — "respect inherent complexity but conquer the rest." Moseley & Marks supplies *the definition* of inherent (essential) and the *mechanisms* by which the rest accumulates.
- **[[richards-ford-architect-principles]]** §1–2 (Two Laws, trade-offs). Tar Pit gives a sharper axis to score trade-offs on: *which choice creates more accidental state and control?*
- **[[hard-parts-pattern-catalog]]** — every pattern in that catalogue can be reread through this lens. Orchestration adds essential state (workflow position). Choreography pushes state into the contract (stamp coupling — explicit accidental state). Caches and projections are *accidental state* the catalogue often treats as architectural primitives — Tar Pit insists they should be *re-derivable from base state* whenever possible.

The combined effect: when a skill prompt uses Tar Pit alongside the other three, it can recognise a class of mistake the others alone can't — adding accidental complexity in the *name* of architecture (more services, more events, more views, more orchestrators) because the catalogue listed it. *Not every pattern in the Hard Parts pays for its state.*

**Closing line from the paper:**

> "If complexity is not controlled it spreads. The *only* way to escape this risk is to place the goals of **avoid** and **separate** at the top of the design objectives for a system. It is not sufficient simply to pay heed to these two objectives — it is crucial that they be the *overriding* consideration."
