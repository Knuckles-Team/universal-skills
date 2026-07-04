---
name: hardware_sweep
description: >-
  OS and hardware information sweep across all inventory hosts. Collects CPU, memory, disk, GPU, and OS details for each machine and ingests them into the Knowledge Graph for troubleshooting and service designation decisions.
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
tags: ['hardware', 'sweep', 'discovery', 'os', 'system-info']
concept: CONCEPT:INFRA-001
---

# Hardware Sweep Workflow

**CONCEPT:INFRA-001**

OS and hardware information sweep across all inventory hosts. Collects CPU, memory, disk, GPU, and OS details for each machine and ingests them into the Knowledge Graph for troubleshooting and service designation decisions.

## Steps

### Step 0: Tunnel Manager Mcp
**Agent**: `discovery-agent`
**Tools**: `tun_tm_system, tun_tm_hosts`

List all hosts from inventory with their connectivity status
Expected: `host, inventory`

### Step 1: Systems Manager Mcp
**Agent**: `deployer-agent`
**Tools**: `pt_stack, cnt_cm_compose_operations`

For each reachable host, collect CPU model and core count, total and available RAM, disk partitions and usage, OS distribution and kernel version
Expected: `cpu, memory, disk, os`

### Step 2: Systems Manager Mcp
**Agent**: `verifier-agent`
**Tools**: `pt_docker, cnt_cm_container_operations`

For each reachable host, detect GPU/accelerator hardware via lspci or nvidia-smi and collect driver versions
Expected: `gpu, accelerator, driver`

### Step 3: Graph Os
**Agent**: `dns-configurator`
**Tools**: `adg_rewrites, td_zones`

Update HardwareNode entries in the KG with collected hardware metadata and create GPUAccelerator nodes with HAS_ACCELERATOR relationships
Expected: `update, hardware, gpu`

### Step 4: KG Persistence [depends_on: graph-os]
**Agent**: `dns-configurator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Hardware Sweep results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Tunnel Manager Mcp; Step 1 — Systems Manager Mcp; Step 2 — Systems Manager Mcp; Step 3 — Graph Os
- **After level 0:** Step 4 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
