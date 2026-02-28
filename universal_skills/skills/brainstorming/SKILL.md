---
name: brainstorming
description: Structured ideation and design workflow for clarifying requirements before implementation. Use when starting any new feature, component, or significant behavior change to explore options, gather requirements, and get user approval on a design before writing code. Do NOT use for pure documentation tasks, minor bug fixes, or when the user explicitly wants immediate implementation.
categories: [Planning]
tags: [planning, design, ideation, requirements, architecture]
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

### Step 1: Explore Project Context

Before asking anything, check:
- Relevant source files and modules
- Existing documentation or ADRs
- Recent commits related to the area of change
- Any established patterns or conventions

### Step 2: Ask Clarifying Questions

- Ask **one question at a time**
- Prefer multiple-choice questions when possible; open-ended when needed
- Focus on: purpose, constraints, success criteria, non-goals
- Apply YAGNI ruthlessly — remove unnecessary complexity from the design

### Step 3: Propose Approaches

Once the problem is understood:
- Present 2–3 distinct approaches with clear trade-offs
- Lead with the recommended option and explain why
- Keep proposals conversational, not exhaustive

### Step 4: Present Design

After approaches are agreed on:
- Present design section by section (architecture → components → data flow → error handling → testing)
- Scale each section to its complexity: a few sentences for simple cases, 200–300 words for nuanced ones
- Ask for confirmation after each section before proceeding
- Be ready to revise and revisit

### Step 5: Write Design Doc

After design approval:
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commit the design document to git

### Step 6: Transition to Implementation

- Create a stepwise implementation plan before writing production code
- Do NOT begin implementation until the plan is approved

---

## Key Principles

- **One question at a time** — don't overwhelm with multiple questions in a single message
- **YAGNI** — ruthlessly eliminate scope that isn't explicitly required
- **Explore before committing** — always propose multiple approaches before settling
- **Incremental validation** — confirm each section of the design, not just the whole
- **Be flexible** — go back and clarify when new information changes the design
