---
name: deploy_ai_inference_stack
description: >-
  Parallel execution workflow for deploy ai inference stack using the Unified Parallel Engine
domain: infra
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
tags: [infra, deploy-ai-inference-stack]
concept: CONCEPT:INFRA-001
---

# Deploy Ai Inference Stack Workflow

**CONCEPT:INFRA-001**

Parallel execution workflow for deploy ai inference stack using the Unified Parallel Engine

## Steps

### Step 1: Gpu Drivers
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

Execute gpu drivers operations for the Deploy Ai Inference Stack workflow.
Expected: `gpu_drivers_artifacts`

### Step 2: Vllm Ollama [depends_on: gpu_drivers]
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

Execute vllm ollama operations for the Deploy Ai Inference Stack workflow.
Expected: `vllm_ollama_artifacts`

### Step 3: Model Download [depends_on: vllm_ollama]
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

Execute model download operations for the Deploy Ai Inference Stack workflow.
Expected: `model_download_artifacts`

### Step 4: Load Test [depends_on: model_download]
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Execute load test operations for the Deploy Ai Inference Stack workflow.
Expected: `load_test_artifacts`

### Step 5: KG Persistence [depends_on: load_test]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Deploy Ai Inference Stack results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Gpu Drivers
- **After level 0:** Step 2 — Vllm Ollama
- **After level 1:** Step 3 — Model Download
- **After level 2:** Step 4 — Load Test
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
