---
name: architecture_diagram_gen
description: >-
  Parallel execution workflow for architecture diagram gen using the Unified Parallel Engine
domain: dev-workflows
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
tags: [dev-workflows, architecture-diagram-gen]
concept: CONCEPT:DEV-001
---

# Architecture Diagram Gen Workflow

**CONCEPT:DEV-001**

Parallel execution workflow for architecture diagram gen using the Unified Parallel Engine

## Steps

### Step 1: Fan Out Per Component Analyze Code
**Agent**: `scanner-agent`
**Tools**: `rep_rm_workspace, rep_rm_git`

Execute fan out per component analyze code operations for the Architecture Diagram Gen workflow.
Expected: `fan_out_per_component_analyze_code_artifacts`

### Step 2: C4 Diagram [depends_on: fan_out_per_component_analyze_code]
**Agent**: `builder-agent`
**Tools**: `rep_rm_projects`

Execute c4 diagram operations for the Architecture Diagram Gen workflow.
Expected: `c4_diagram_artifacts`

### Step 3: Mermaid [depends_on: c4_diagram]
**Agent**: `validator-agent`
**Tools**: `rep_rm_projects, gl_pipelines`

Execute mermaid operations for the Architecture Diagram Gen workflow.
Expected: `mermaid_artifacts`

### Step 4: Docs [depends_on: mermaid]
**Agent**: `publisher-agent`
**Tools**: `rep_rm_git, gl_merge_requests`

Execute docs operations for the Architecture Diagram Gen workflow.
Expected: `docs_artifacts`

### Step 5: KG Persistence [depends_on: docs]
**Agent**: `publisher-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Architecture Diagram Gen results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions
