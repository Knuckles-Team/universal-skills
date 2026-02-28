---
name: product-management
description: Guiding the lifecycle of a product from discovery and requirements through execution and delivery. Use when creating Product Requirements Documents (PRDs), writing user stories, prioritizing features, or planning roadmaps. Incorporates best practices for stakeholder alignment and engineering context.
categories: [Productivity]
tags: [product-management, prd, user-stories, prioritization, roadmap, agile]
---

# Product Management & Execution

Drive product initiatives from ambiguous ideas to clear, executable requirements that align teams and deliver customer value.

---

## 1. Product Requirements Document (PRD)

A PRD is a living source of truth that defines the **"Why"** and **"What"** of a feature before engineering begins the **"How"**.

### Standard PRD Structure
1. **Executive Summary**: One-paragraph "Elevator Pitch" (Problem + Solution + Impact).
2. **Problem Statement**: Who has the problem? What is it? Why is it painful? (Include data/evidence).
3. **Target Users**: Reference specific personas and their Jobs-to-be-Done (JTBD).
4. **Solution Overview**: High-level functional description (not pixel-perfect UI specs).
5. **Success Metrics**: Define the Primary Metric (what we optimize) and Guardrail Metrics (what shouldn't break).
6. **Requirements & User Stories**: The granular executable units of work.
7. **Out of Scope**: Explicitly list what we are NOT building to prevent scope creep.
8. **Risks & Open Questions**: Acknowledge unknowns and technical dependencies.

---

## 2. User Stories & Acceptance Criteria

User stories bridge the gap between business value and technical implementation.

**Format**: "As a [persona], I want to [action], so that [value/benefit]."

### Acceptance Criteria (AC) Guidelines:
- Use **Checklist format** for clarity.
- Define **Pass/Fail** boundaries.
- Cover **Edge Cases** (e.g., "What if the user is offline?").
- Avoid implementation details (Focus on the behavior).

---

## 3. Prioritization & Roadmapping

When managing multiple requests, use a structured framework to decide what to build next.

### Prioritization Frameworks:
- **RICE**: Reach × Impact × Confidence ÷ Effort.
- **Value vs. Effort Matrix**: Focus on "Quick Wins" (High Value, Low Effort) and "Big Bets" (High Value, High Effort).
- **MoSCoW**: Must-have, Should-have, Could-have, Won't-have (this time).

### Roadmapping:
- Move from **Fixed Dates** to **Outcome Buckets** (Now, Next, Later).
- Align roadmap items to business OKRs (Objectives and Key Results).

---

## 4. Best Practices

- **Avoid Isolation**: Never write a PRD in a vacuum. Collaborate with Design and Engineering early for feasibility.
- **Evidence-Led**: Every problem statement should be backed by customer quotes, support tickets, or analytics.
- **Keep it Lean**: Don't write 50-page specs. Focus on clear framing and unambiguous requirements.
- **Iterate**: The PRD should evolve as discovery continues and technical constraints are revealed.

---

## Component Workflows

- For **User Research & Discovery**: Use the `user-research` skill.
- For **Market & Pricing Strategy**: Use the `product-strategy` skill.
- For **Technical Specifications**: Collaborate with Engineering using standard markdown design docs.
