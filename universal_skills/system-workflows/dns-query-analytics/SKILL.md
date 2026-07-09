---
name: dns-query-analytics
description: >-
  Parallel execution workflow for dns query analytics using the Unified Parallel Engine
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
tags: [system, dns-query-analytics]
concept: CONCEPT:SYS-001
---

# Dns Query Analytics Workflow

**CONCEPT:SYS-001**

Parallel execution workflow for dns query analytics using the Unified Parallel Engine

## Steps

### Step 1: Sequential Pull Logs
**Agent**: `scanner-agent`
**Tools**: `tun_tm_system, tun_tm_remote`

Execute sequential pull logs operations for the Dns Query Analytics workflow.
Expected: `sequential_pull_logs_artifacts`

### Step 2: Parse Patterns [depends_on: sequential_pull_logs]
**Agent**: `analyzer-agent`
**Tools**: `graph_analyze, tun_tm_security`

Execute parse patterns operations for the Dns Query Analytics workflow.
Expected: `parse_patterns_artifacts`

### Step 3: Top Domains [depends_on: parse_patterns]
**Agent**: `remediator-agent`
**Tools**: `tun_tm_remote, tun_tm_inventory`

Execute top domains operations for the Dns Query Analytics workflow.
Expected: `top_domains_artifacts`

### Step 4: Block Recommendations [depends_on: top_domains]
**Agent**: `reporter-agent`
**Tools**: `graph_write, document_tools`

Execute block recommendations operations for the Dns Query Analytics workflow.
Expected: `block_recommendations_artifacts`

### Step 5: KG Persistence [depends_on: block_recommendations]
**Agent**: `reporter-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Dns Query Analytics results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Sequential Pull Logs
- **After level 0:** Step 2 — Parse Patterns
- **After level 1:** Step 3 — Top Domains
- **After level 2:** Step 4 — Block Recommendations
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
