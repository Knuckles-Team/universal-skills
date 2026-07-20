---
name: strategy-code-review
skill_type: workflow
description: >-
  Loads strategy script files, audits logic for lookahead bias, checks index variables leaks, and generates quality reviews.
domain: finance-workflows
agent: quant_analyst
team_config:
  name: quantitative_trading_team
  task_pattern: quantitative analysis and financial computation
  execution_mode: parallel
  specialist_ids:
    - data-fetcher
    - compute-engine
    - risk-assessor
    - report-generator
  tool_assignments:
    data-fetcher: [graph_query, sx_search]
    compute-engine: [graph_analyze]
    risk-assessor: [graph_query, graph_analyze]
    report-generator: [graph_write, document_tools]
tags: [code-review, static-analysis, leakage-bias, qa]
concept: CONCEPT:EE-011
metadata:
  version: '1.2.1'
---

# Strategy Code Review Workflow

**CONCEPT:EE-011**

Loads strategy script files, audits logic for lookahead bias, checks index variables leaks, and generates quality reviews.

## Steps

### Step 1: Strategy Parser
**Agent**: `data-fetcher`
**Tools**: `graph_query, sx_search`

Loads strategy code files and extracts methods and properties.
Expected: `strategy-abstract-syntax-tree`

### Step 2: Static Logic Reviewer [depends_on: strategy-parser]
**Agent**: `compute-engine`
**Tools**: `graph_analyze`

Audits trading logic for common bugs (like lookahead bias, divide-by-zero).
Expected: `logic-anomaly-records`

### Step 3: Leak Detector [depends_on: static-logic-reviewer]
**Agent**: `risk-assessor`
**Tools**: `graph_query, graph_analyze`

Tests execution logic for information leakage or bad indexing.
Expected: `information-leakage-verdicts`

### Step 4: Quality Report Compiler [depends_on: leak-detector]
**Agent**: `report-generator`
**Tools**: `graph_write, document_tools`

Compiles performance and security review report.
Expected: `strategy-review-dashboard`

### Step 5: KG Persistence [depends_on: quality-report-compiler]
**Agent**: `report-generator`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Strategy Code Review results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 1 — Strategy Parser
- **After level 0:** Step 2 — Static Logic Reviewer
- **After level 1:** Step 3 — Leak Detector
- **After level 2:** Step 4 — Quality Report Compiler
- **After level 3:** Step 5 — KG Persistence

**Execution:** If graph-os is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
