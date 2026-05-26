---
name: infrastructure_as_code_sync
description: >-
  Parallel execution workflow for infrastructure as code sync using the Unified Parallel Engine
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
tags: [system, infrastructure-as-code-sync]
concept: CONCEPT:SYS-001
---

# Infrastructure As Code Sync Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for infrastructure as code sync using the Unified Parallel Engine

## Steps

### Step 1: Git Pull
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute git pull operations for the Infrastructure As Code Sync workflow.
Expected: `git_pull_artifacts`

### Step 2: Diff [depends_on: git_pull]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute diff operations for the Infrastructure As Code Sync workflow.
Expected: `diff_artifacts`

### Step 3: Plan [depends_on: diff]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute plan operations for the Infrastructure As Code Sync workflow.
Expected: `plan_artifacts`

### Step 4: Apply [depends_on: plan]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute apply operations for the Infrastructure As Code Sync workflow.
Expected: `apply_artifacts`

### Step 5: Verify [depends_on: apply]
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute verify operations for the Infrastructure As Code Sync workflow.
Expected: `verify_artifacts`

### Step 6: KG Persistence [depends_on: verify]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Infrastructure As Code Sync results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
