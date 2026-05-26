---
name: cron_job_audit
description: >-
  Parallel execution workflow for cron job audit using the Unified Parallel Engine
domain: system
agent: systems_engineer
team_config:
  name: systems_operations_team
  task_pattern: system administration and management
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - analyzer-agent
    - remediator-agent
    - reporter-agent
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
    reporter-agent: [graph_write, document_tools]
tags: [system, cron-job-audit]
concept: CONCEPT:SYS-001
---

# Cron Job Audit Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for cron job audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Host List Crontabs
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute fan out per host list crontabs operations for the Cron Job Audit workflow.
Expected: `fan_out_per_host_list_crontabs_artifacts`

### Step 2: Classify [depends_on: fan_out_per_host_list_crontabs]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute classify operations for the Cron Job Audit workflow.
Expected: `classify_artifacts`

### Step 3: Find Overlaps [depends_on: classify]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute find overlaps operations for the Cron Job Audit workflow.
Expected: `find_overlaps_artifacts`

### Step 4: Optimize [depends_on: find_overlaps]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute optimize operations for the Cron Job Audit workflow.
Expected: `optimize_artifacts`

### Step 5: KG Persistence [depends_on: optimize]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Cron Job Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
