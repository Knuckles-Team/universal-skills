---
name: meal-plan-and-shop
description: >-
  Parallel execution workflow for meal plan and shop using the Unified Parallel Engine
domain: ops
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
    - report-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
    report-agent: [graph_write, document_tools]
tags: [ops, meal-plan-and-shop]
concept: CONCEPT:KG-2.12
---

# Meal Plan And Shop Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for meal plan and shop using the Unified Parallel Engine

## Steps

### Step 1: Preferences
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute preferences operations for the Meal Plan And Shop workflow.
Expected: `preferences_artifacts`

### Step 2: Generate Plan [depends_on: preferences]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute generate plan operations for the Meal Plan And Shop workflow.
Expected: `generate_plan_artifacts`

### Step 3: Scale Recipes [depends_on: generate_plan]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute scale recipes operations for the Meal Plan And Shop workflow.
Expected: `scale_recipes_artifacts`

### Step 4: Shopping List [depends_on: scale_recipes]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute shopping list operations for the Meal Plan And Shop workflow.
Expected: `shopping_list_artifacts`

### Step 5: Add To Mealie [depends_on: shopping_list]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute add to mealie operations for the Meal Plan And Shop workflow.
Expected: `add_to_mealie_artifacts`

### Step 6: KG Persistence [depends_on: add_to_mealie]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Meal Plan And Shop results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Preferences
- **After level 0:** Step 2 — Generate Plan
- **After level 1:** Step 3 — Scale Recipes
- **After level 2:** Step 4 — Shopping List
- **After level 3:** Step 5 — Add To Mealie
- **After level 4:** Step 6 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
