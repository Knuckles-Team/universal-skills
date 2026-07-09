---
name: dietician-and-chef
skill_type: workflow
description: >-
  Generates a customized healthy meal plan, adds selected recipes, and compiles an organized, scaled household shopping list in Mealie using mealie-mcp tools.
domain: health-workflows
agent: health_wellness_coordinator
team_config:
  name: health_wellness_team
  task_pattern: health monitoring and wellness optimization
  execution_mode: sequential
  specialist_ids:
    - data-collector
    - analyzer-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
tags: ['health', 'diet', 'recipes', 'mealie-mcp']
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.0.2'
---

# Dietician And Chef Workflow

**CONCEPT:HEALTH-001**

Generates a customized healthy meal plan, adds selected recipes, and compiles an organized, scaled household shopping list in Mealie using mealie-mcp tools.

## Steps

### Step 0: Dietician Chef
**Agent**: `data-collector`
**Tools**: `graph_query`

Generate a customized weekly meal plan matching the user's calorie targets. Register/add the planned meals to Mealie using the mealie_recipes and mealie_organizer tools.
Expected: `mealplan, recipes`

### Step 1: Mealie Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Compile and organize a consolidated grocery shopping list for the planned weekly meals. Use the mealie_households tools to add the required recipe ingredients scaled for the household into a clean, categorized Mealie shopping list.
Expected: `shopping_list, ingredients`

### Step 2: KG Persistence [depends_on: mealie-mcp]
**Agent**: `analyzer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dietician And Chef results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Dietician Chef; Step 1 — Mealie Mcp
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
