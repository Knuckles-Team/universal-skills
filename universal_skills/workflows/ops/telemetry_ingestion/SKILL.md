---
name: telemetry_ingestion
description: Extracts anomalous execution traces and success rates from Langfuse, then ingests them into the Knowledge Graph as ExecutionSummary and PerformanceAnomaly nodes.
domain: operations
tags: ['telemetry', 'observability', 'langfuse', 'graph-os']
requires: ['langfuse-mcp', 'graph-os']
---

# telemetry_ingestion Workflow

Extracts anomalous execution traces and success rates from Langfuse, then ingests them into the Knowledge Graph as ExecutionSummary and PerformanceAnomaly nodes.

### Step 0: langfuse-mcp
Fetch recent execution traces and filter for long-running or failed tasks based on baseline configurations.
Expected: trace, filter

### Step 1: langfuse-mcp
Calculate overall success rates and token consumption averages across workflows.
Expected: success, token
Depends On: Step 0

### Step 2: graph-os
Write Cypher queries using kg_write to ingest ExecutionSummary and PerformanceAnomaly nodes into LadybugDB with relationships to their respective Workflow, Agent, and Tool nodes.
Expected: cypher, ingest
Depends On: Step 1
