---
name: port_scan_audit
description: >-
  Parallel execution workflow for port scan audit using the Unified Parallel Engine
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
  tool_assignments:
    data-collector: [graph_query]
    analyzer-agent: [graph_analyze]
    planner-agent: [graph_write]
tags: [health, port-scan-audit]
concept: CONCEPT:HEALTH-001
---

# Port Scan Audit Workflow

**CONCEPT:HEALTH-001**

Parallel execution workflow for port scan audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host Nmap Scan
**Agent**: `data-collector`
**Tools**: `graph_query`

Execute fan out per host nmap scan operations for the Port Scan Audit workflow.
Expected: `fan_out_per_host_nmap_scan_artifacts`

### Step 2: Compare Against Expected [depends_on: fan_out_per_host_nmap_scan]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze`

Execute compare against expected operations for the Port Scan Audit workflow.
Expected: `compare_against_expected_artifacts`

### Step 3: Flag Anomalies [depends_on: compare_against_expected]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Execute flag anomalies operations for the Port Scan Audit workflow.
Expected: `flag_anomalies_artifacts`

### Step 4: KG Persistence [depends_on: flag_anomalies]
**Agent**: `planner-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Port Scan Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
