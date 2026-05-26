---
name: full_ecosystem_health
description: >-
  End-to-end ecosystem health check across containers, system resources, workspace, and observability stack. This is the "canary" workflow that validates all infrastructure layers are operational.
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
tags: ['ecosystem', 'health', 'canary', 'full-stack']
concept: CONCEPT:KG-2.12
---

# Full Ecosystem Health Workflow

**CONCEPT:KG-2.12**

End-to-end ecosystem health check across containers, system resources, workspace, and observability stack. This is the "canary" workflow that validates all infrastructure layers are operational.

## Steps

### Step 0: Systems Manager
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Get system memory, CPU, and disk stats
Expected: `memory, cpu`

### Step 1: Container Manager Mcp
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

List all running Docker containers and their health status
Expected: `container, running`

### Step 2: Langfuse Mcp
**Agent**: `validator-agent`
**Tools**: `graph_query`

Check Langfuse health and list recent traces
Expected: `health`

### Step 3: Repository Manager Mcp
**Agent**: `report-agent`
**Tools**: `graph_write, document_tools`

List workspace actions and verify workspace configuration
Expected: `workspace, list`

### Step 4: KG Persistence [depends_on: repository-manager-mcp]
**Agent**: `report-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Full Ecosystem Health results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
