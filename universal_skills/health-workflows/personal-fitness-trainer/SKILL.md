---
name: personal-fitness-trainer
skill_type: workflow
description: >-
  Assesses user fitness goals, queries appropriate strength training exercises, constructs a custom workout routine, and registers it using wger-agent tools.
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
tags: ['health', 'workout', 'fitness', 'wger-agent']
concept: CONCEPT:HEALTH-001
metadata:
  version: '1.0.2'
---

# Personal Fitness Trainer Workflow

**CONCEPT:HEALTH-001**

Assesses user fitness goals, queries appropriate strength training exercises, constructs a custom workout routine, and registers it using wger-agent tools.

## Steps

### Step 0: Fitness Trainer
**Agent**: `data-collector`
**Tools**: `graph_query`

Conduct the user's fitness and muscle group intake assessment. Query the wger exercise database using wger_exercise tool with search query and muscle group parameters to discover target exercises.
Expected: `intake, exercises`

### Step 1: Wger Agent
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Create and configure a personal strength routine. Call the wger_routine tool to create a new routine, and then configure its workout days and exercises using the wger_routineconfig tool.
Expected: `routine, configuration`

### Step 2: KG Persistence [depends_on: wger-agent]
**Agent**: `analyzer-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Personal Fitness Trainer results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Fitness Trainer; Step 1 — Wger Agent
- **After level 0:** Step 2 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
