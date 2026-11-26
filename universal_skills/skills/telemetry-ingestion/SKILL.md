---
name: telemetry-ingestion
skill_type: workflow
description: >-
  Extracts anomalous execution traces and success rates from Langfuse, then ingests them into the Knowledge Graph as ExecutionSummary and PerformanceAnomaly nodes.
domain: ops-workflows
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
    - validator-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
    validator-agent: [graph_query]
tags: ['telemetry', 'observability', 'langfuse', 'arbora']
concept: CONCEPT:KG-2.12
metadata:
  version: '1.6.2'
---

# Telemetry Ingestion Workflow

**CONCEPT:KG-2.12**

Extracts anomalous execution traces and success rates from Langfuse, then ingests them into the Knowledge Graph as ExecutionSummary and PerformanceAnomaly nodes.

## Steps

1. Fetch recent traces with the langfuse-mcp trace tools and filter long-running or failed runs. Verify that the filtered `trace` list is returned.
2. Aggregate success rates and token averages with the `langfuse-mcp` metrics tools. Verify that success and token values are present.
3. Ingest ExecutionSummary and PerformanceAnomaly nodes using Cypher via `kg_write`. Verify that a `graph_query` returns the new nodes with their Workflow, Agent and Tool links.
4. Persist results with `graph_write` as typed nodes and edges. Verify that a `graph_query` lookup of the new nodes returns the persisted records.

### Step 0: Langfuse Trace Retrieval [skill: langfuse-mcp]
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Fetch recent execution traces and filter for long-running or failed tasks based on baseline configurations.
Expected: `trace, filter`

### Step 1: Langfuse Metrics Aggregation [skill: langfuse-mcp]
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Calculate overall success rates and token consumption averages across workflows.
Expected: `success, token`

### Step 2: Arbora
**Agent**: `validator-agent`
**Tools**: `graph_query`

Write Cypher queries using kg_write to ingest ExecutionSummary and PerformanceAnomaly nodes into LadybugDB with relationships to their respective Workflow, Agent, and Tool nodes.
Expected: `cypher, ingest`

### Step 3: KG Persistence [depends_on: arbora]
**Agent**: `validator-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Langfuse returns no traces | Wrong project or time range | Set the correct project and window, and fetch again. |
| Cypher write fails | Referenced Workflow or Agent node is missing | Create or ingest the missing node first and repeat the `kg_write` call. |
| Duplicates appear after ingest | Same run ingested twice | Use a stable id per run in the Cypher `MERGE` and remove the duplicates. |

## Output
- Telemetry Ingestion results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.

## Execution

Run this workflow as a dependency-ordered DAG. Steps with no unmet `depends_on` run in parallel; dependents run after their prerequisites complete.

- **Run first (in parallel):** Step 0 — Langfuse Trace Retrieval; Step 1 — Langfuse Metrics Aggregation; Step 2 — Arbora
- **After level 0:** Step 3 — KG Persistence

**Execution:** If arbora is reachable, offload the whole DAG via `graph_orchestrate action=execute_workflow` (or the `kg-delegate` skill) for true parallel/swarm execution. Otherwise execute the steps natively in dependency order: run steps with no unmet `depends_on` in parallel, then their dependents.
