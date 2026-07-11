---
name: capability-discovery
skill_type: workflow
description: >-
  Discovery workflow that probes available capabilities across MCP servers. Tests tool introspection, not execution — useful for building capability maps.
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
  tool_assignments:
    scanner-agent: [tun_tm_system, tun_tm_remote]
    analyzer-agent: [graph_analyze, tun_tm_security]
    remediator-agent: [tun_tm_remote, tun_tm_inventory]
tags: ['discovery', 'capabilities', 'introspection', 'meta']
concept: CONCEPT:SYS-001
metadata:
  version: '1.2.0'
---

# Capability Discovery Workflow

**CONCEPT:SYS-001**

Discovery workflow that probes available capabilities across MCP servers. Tests tool introspection, not execution — useful for building capability maps.

## Steps

### Step 0: Audio Transcriber
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Describe the capabilities of the transcribe_audio tool
Expected: `transcribe, audio`

### Step 1: Data Science Mcp
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Describe the available data science tools and their parameters
Expected: `dataset, tool`

### Step 2: Scholarx Mcp
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

List available research paper sources
Expected: `source`

### Step 3: KG Persistence [depends_on: scholarx-mcp]
**Agent**: `remediator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Capability Discovery results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Audio Transcriber; Step 1 — Data Science Mcp; Step 2 — Scholarx Mcp
- **After level 0:** Step 3 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
