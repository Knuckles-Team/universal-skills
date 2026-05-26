---
name: fitness_program_builder
description: >-
  Parallel execution workflow for fitness program builder using the Unified Parallel Engine
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
tags: [ops, fitness-program-builder]
concept: CONCEPT:KG-2.12
---

# Fitness Program Builder Workflow

**CONCEPT:KG-2.12**

Parallel execution workflow for fitness program builder using the Unified Parallel Engine

## Steps

### Step 1: Assess Goals
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute assess goals operations for the Fitness Program Builder workflow.
Expected: `assess_goals_artifacts`

### Step 2: Select Exercises [depends_on: assess_goals]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Execute select exercises operations for the Fitness Program Builder workflow.
Expected: `select_exercises_artifacts`

### Step 3: Build Routine [depends_on: select_exercises]
**Agent**: `validator-agent`
**Tools**: `graph_query`

Execute build routine operations for the Fitness Program Builder workflow.
Expected: `build_routine_artifacts`

### Step 4: Schedule [depends_on: build_routine]
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

Execute schedule operations for the Fitness Program Builder workflow.
Expected: `schedule_artifacts`

### Step 5: Track [depends_on: schedule]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Execute track operations for the Fitness Program Builder workflow.
Expected: `track_artifacts`

### Step 6: KG Persistence [depends_on: track]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Fitness Program Builder results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
