---
name: deploy-dev-environment
skill_type: workflow
description: >-
  Parallel execution workflow for deploy dev environment using the Unified Parallel Engine
domain: infrastructure-workflows
agent: infrastructure_operator
team_config:
  name: infrastructure_ops_team
  task_pattern: infrastructure deployment and operations
  execution_mode: parallel
  specialist_ids:
    - discovery-agent
    - deployer-agent
    - verifier-agent
    - dns-configurator
  tool_assignments:
    discovery-agent: [tun_tm_system, tun_tm_hosts]
    deployer-agent: [pt_stack, cnt_cm_compose_operations]
    verifier-agent: [pt_docker, cnt_cm_container_operations]
    dns-configurator: [adg_rewrites, td_zones]
tags: [infra, deploy-dev-environment]
concept: CONCEPT:INFRA-001
metadata:
  version: '1.0.2'
---

# Deploy Dev Environment Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy dev environment using the Unified Parallel Engine

## Steps

### Step 1: Gitea Gitlab
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute gitea gitlab operations for the Deploy Dev Environment workflow.
Expected: `gitea_gitlab_artifacts`

### Step 2: Registry
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute registry operations for the Deploy Dev Environment workflow.
Expected: `registry_artifacts`

### Step 3: Runner
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute runner operations for the Deploy Dev Environment workflow.
Expected: `runner_artifacts`

### Step 4: Ci Pipeline [depends_on: gitea_gitlab, registry, runner]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute ci pipeline operations for the Deploy Dev Environment workflow.
Expected: `ci_pipeline_artifacts`

### Step 5: KG Persistence [depends_on: ci_pipeline]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Dev Environment results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Gitea Gitlab; Step 2 — Registry; Step 3 — Runner
- **After level 0:** Step 4 — Ci Pipeline
- **After level 1:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
