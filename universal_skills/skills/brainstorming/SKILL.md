---
name: brainstorming
domain: research
skill_type: skill
description: >-
  Structured ideation and design workflow for clarifying requirements before
  implementation. Use when starting any new feature, component, or significant
  behavior change to explore options, gather requirements, and get user approval
  on a design before writing code. Do NOT use for pure documentation tasks, minor
  bug fixes, or when the user explicitly wants immediate implementation.
license: MIT
tags: [planning, design, ideation, requirements, architecture]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# Brainstorming & Design Workflow

## Overview

Turn ideas into fully-formed designs through structured collaborative dialogue. Explore the project context, ask clarifying questions one at a time, propose approaches with trade-offs, present a design, then get approval before any implementation begins.

> [!IMPORTANT]
> Do NOT write any code, scaffold any project, or take any implementation action until a design has been presented and the user has approved it — regardless of how simple the task appears.

---

## When This Applies

This skill applies to **every** implementation task, including:
- New features or components
- Significant refactors
- Architectural changes
- New integrations or workflows

Simple tasks still require a design — it can be short (a few sentences), but it must be presented and approved.

---

## Checklist

Work through these steps in order:

1. **Explore project context** — read relevant files, docs, recent git history
2. **Ask clarifying questions** — one at a time until purpose, constraints, and success criteria are understood
3. **Propose 2–3 approaches** — present trade-offs and a recommended option with reasoning
4. **Present design** — section by section, confirm each section before moving on
5. **Write design doc** — save to `docs/plans/YYYY-MM-DD-<topic>-design.md`
6. **Transition to implementation** — create a detailed implementation plan before writing code

---

## Process

### Step 1: explore-context

Before asking anything, check:
- Relevant source files and modules
- Existing documentation or ADRs
- Recent commits related to the area of change
- Any established patterns or conventions

### Step 2: analogy-scan [depends_on: explore-context]

Before proposing any new designs, you MUST use the `kg_analogy_search` MCP tool from `meristem-kg` to scan the Knowledge Graph for structurally similar concepts, past designs, or existing solutions within the ecosystem. This ensures we "Extend-Before-Invent".

### Step 3: clarify-requirements [depends_on: analogy-scan]

- Ask **one question at a time**
- Prefer multiple-choice questions when possible; open-ended when needed
- Focus on: purpose, constraints, success criteria, non-goals
- Apply YAGNI ruthlessly — remove unnecessary complexity from the design

#### Scrutiny Mode
When triggered or when the plan is highly complex/ambiguous, activate **Scrutiny Mode**:
- Interview the user relentlessly about every aspect of the plan until a shared understanding is reached.
- Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.
- For each question, provide your recommended answer.
- Do not let vague answers pass. Push for clarity.

### Step 4: propose-approaches [depends_on: clarify-requirements]

Once the problem is understood (and informed by the `kg_analogy_search` results):
- Present 2–3 distinct approaches with clear trade-offs
- Lead with the recommended option and explain why
- Keep proposals conversational, not exhaustive

### Step 5: present-design [depends_on: propose-approaches]

After approaches are agreed on:
- Present design section by section (architecture → components → data flow → error handling → testing)
- Scale each section to its complexity: a few sentences for simple cases, 200–300 words for nuanced ones
- Ask for confirmation after each section before proceeding
- Be ready to revise and revisit

### Step 6: write-design-doc [depends_on: present-design]

After design approval:
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit the design document to git

### Step 7: kg-dual-write [depends_on: write-design-doc]

**KG Dual-Write**: Use the `kg_memory_store` MCP tool to save the core design decisions back into the Knowledge Graph as `semantic` memory, ensuring future agents can discover this architectural decision during their own analogy scans.

### Step 8: transition-implementation [depends_on: kg-dual-write]

- Create a stepwise implementation plan before writing production code
- Do NOT begin implementation until the plan is approved

---

## Steps

1. Explore the context with `git log --oneline -n 20` and `ls docs/`. Verify that you can name the relevant modules, docs and recent commits.
2. Scan the KG for analogies with `kg_analogy_search`. Verify that the results are summarized, or that an empty result is noted explicitly.
3. Ask clarifying questions one at a time and record the answers with `grep -n "" docs/plans/<topic>-notes.md` style notes. Verify that purpose, constraints and success criteria are each confirmed by the user.
4. Present 2-3 approaches with trade-offs and a recommendation, and get the design approved section by section via `git status` showing no code changes yet. Verify that the user explicitly approved the design before any code is written.
5. Write the design with `docs/plans/YYYY-MM-DD-<topic>-design.md` and commit it. Verify that `git log -1 --stat` lists the design file.
6. Save the decisions with `kg_memory_store` as semantic memory. Verify that the tool returns a stored memory id.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Implementation started before approval | Design step was skipped as "too simple" | Stop, present a short design, and get explicit approval before continuing. |
| `kg_analogy_search` unavailable | meristem-kg MCP server not connected | Note the gap, proceed from repository evidence, and retry the scan later. |
| Design doc commit rejected | Pre-commit hook or wrong path | Fix the reported issue and use the exact `docs/plans/YYYY-MM-DD-<topic>-design.md` path. |

## Key Principles

- **One question at a time** — don't overwhelm with multiple questions in a single message
- **YAGNI** — ruthlessly eliminate scope that isn't explicitly required
- **Explore before committing** — always propose multiple approaches before settling
- **Incremental validation** — confirm each section of the design, not just the whole
- **Be flexible** — go back and clarify when new information changes the design
