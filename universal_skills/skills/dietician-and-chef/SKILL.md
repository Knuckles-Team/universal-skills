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
  version: '1.7.0'
---

# Dietician And Chef Workflow

**CONCEPT:HEALTH-001**

Generates a customized healthy meal plan, adds selected recipes, and compiles an organized, scaled household shopping list in Mealie using mealie-mcp tools.

## Steps

1. Generate the weekly meal plan for the calorie targets and add the recipes to Mealie with `mealie_recipes` and `mealie_organizer` (Step 0). Verify that `mealplan` lists every planned day and that each recipe is found in Mealie.
2. Compile the household shopping list with the `mealie_households` tools (Step 1). Verify that `shopping_list` contains the scaled ingredients of every planned recipe, in categories.
3. Persist the plan and list with `graph_write` (Step 2). Verify that `graph_query` returns the stored meal plan node.

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

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Recipe is not created in Mealie | The recipe name duplicates an existing one or the API token is invalid | Search the existing recipes with `mealie_recipes`, reuse the match, or rename the recipe and add it again |
| Shopping list lacks ingredients | A recipe has no structured ingredient list | Edit the recipe to add structured ingredients and regenerate the list in Step 1 |
| Plan misses the calorie target | The target was not passed to the planner | Restate the daily calorie target and regenerate the plan before the Mealie step |


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

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
