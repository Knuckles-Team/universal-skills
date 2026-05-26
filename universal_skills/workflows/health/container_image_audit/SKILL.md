---
name: container_image_audit
description: >-
  Parallel execution workflow for container image audit using the Unified Parallel Engine
domain: health
agent: health_wellness_coordinator
team_config:
  name: health_wellness_team
  task_pattern: health monitoring and wellness optimization
  execution_mode: sequential
  specialist_ids:
    - data-collector
    - analyzer-agent
    - planner-agent
    - tracker-agent
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
    tracker-agent: [nc_calendar, graph_write]
tags: [health, container-image-audit]
concept: CONCEPT:HEALTH-001
---

# Container Image Audit Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for container image audit using the Unified Parallel Engine

## Steps

### Step 1: List Images
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute list images operations for the Container Image Audit workflow.
Expected: `list_images_artifacts`

### Step 2: Check For Cves [depends_on: list_images]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute check for cves operations for the Container Image Audit workflow.
Expected: `check_for_cves_artifacts`

### Step 3: Prune Unused [depends_on: check_for_cves]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute prune unused operations for the Container Image Audit workflow.
Expected: `prune_unused_artifacts`

### Step 4: Report [depends_on: prune_unused]
**Agent**: `tracker-agent`
**Tools**: `nc_calendar, graph_write`

Execute report operations for the Container Image Audit workflow.
Expected: `report_artifacts`

### Step 5: KG Persistence [depends_on: report]
**Agent**: `tracker-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Container Image Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
