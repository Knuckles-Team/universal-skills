---
name: reverse_proxy_setup
description: >-
  Parallel execution workflow for reverse proxy setup using the Unified Parallel Engine
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
tags: [system, reverse-proxy-setup]
concept: CONCEPT:SYS-001
---

# Reverse Proxy Setup Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for reverse proxy setup using the Unified Parallel Engine

## Steps

### Step 1: Detect Services
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute detect services operations for the Reverse Proxy Setup workflow.
Expected: `detect_services_artifacts`

### Step 2: Generate Traefik Config [depends_on: detect_services]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute generate traefik config operations for the Reverse Proxy Setup workflow.
Expected: `generate_traefik_config_artifacts`

### Step 3: Deploy [depends_on: generate_traefik_config]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute deploy operations for the Reverse Proxy Setup workflow.
Expected: `deploy_artifacts`

### Step 4: Ssl Certs [depends_on: deploy]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute ssl certs operations for the Reverse Proxy Setup workflow.
Expected: `ssl_certs_artifacts`

### Step 5: KG Persistence [depends_on: ssl_certs]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Reverse Proxy Setup results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Detect Services
- **After level 0:** Step 2 — Generate Traefik Config
- **After level 1:** Step 3 — Deploy
- **After level 2:** Step 4 — Ssl Certs
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegation-router` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
