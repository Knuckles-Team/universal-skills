---
name: load-balancer-setup
skill_type: workflow
description: >-
  Parallel execution workflow for load balancer setup using the Unified Parallel Engine
domain: system-workflows
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
tags: [system, load-balancer-setup]
concept: CONCEPT:SYS-001
metadata:
  version: '1.0.2'
---

# Load Balancer Setup Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for load balancer setup using the Unified Parallel Engine

## Steps

### Step 1: Detect Backends
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute detect backends operations for the Load Balancer Setup workflow.
Expected: `detect_backends_artifacts`

### Step 2: Configure Haproxy Nginx [depends_on: detect_backends]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute configure haproxy nginx operations for the Load Balancer Setup workflow.
Expected: `configure_haproxy_nginx_artifacts`

### Step 3: Health Checks [depends_on: configure_haproxy_nginx]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute health checks operations for the Load Balancer Setup workflow.
Expected: `health_checks_artifacts`

### Step 4: Deploy [depends_on: health_checks]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute deploy operations for the Load Balancer Setup workflow.
Expected: `deploy_artifacts`

### Step 5: KG Persistence [depends_on: deploy]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Load Balancer Setup results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Backends
- **After level 0:** Step 2 — Configure Haproxy Nginx
- **After level 1:** Step 3 — Health Checks
- **After level 2:** Step 4 — Deploy
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
