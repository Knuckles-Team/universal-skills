---
name: mcp-tool-coverage-audit
skill_type: workflow
description: >-
  Parallel execution workflow for mcp tool coverage audit using the Unified Parallel Engine
domain: development-workflows
agent: dev_ops_engineer
team_config:
  name: development_operations_team
  task_pattern: development workflow automation
  execution_mode: parallel
  specialist_ids:
    - scanner-agent
    - builder-agent
    - validator-agent
    - publisher-agent
  tool_assignments:
    scanner-agent: [rep_rm_workspace, rep_rm_git]
    builder-agent: [rep_rm_projects]
    validator-agent: [rep_rm_projects, gl_pipelines]
    publisher-agent: [rep_rm_git, gl_merge_requests]
tags: [dev-workflows, mcp-tool-coverage-audit]
concept: CONCEPT:DEV-001
metadata:
  version: '1.0.2'
---

# Mcp Tool Coverage Audit Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for mcp tool coverage audit using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Mcp List Tools
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per mcp list tools operations for the Mcp Tool Coverage Audit workflow.
Expected: `fan_out_per_mcp_list_tools_artifacts`

### Step 2: Check Tests [depends_on: fan_out_per_mcp_list_tools]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute check tests operations for the Mcp Tool Coverage Audit workflow.
Expected: `check_tests_artifacts`

### Step 3: Check Docs [depends_on: check_tests]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute check docs operations for the Mcp Tool Coverage Audit workflow.
Expected: `check_docs_artifacts`

### Step 4: Gap Report [depends_on: check_docs]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute gap report operations for the Mcp Tool Coverage Audit workflow.
Expected: `gap_report_artifacts`

### Step 5: KG Persistence [depends_on: gap_report]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Mcp Tool Coverage Audit results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Fan Out Per Mcp List Tools
- **After level 0:** Step 2 — Check Tests
- **After level 1:** Step 3 — Check Docs
- **After level 2:** Step 4 — Gap Report
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
