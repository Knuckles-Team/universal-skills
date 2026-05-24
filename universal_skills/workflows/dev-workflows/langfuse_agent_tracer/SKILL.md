---
name: langfuse_agent_tracer
description: Automatically queries Langfuse sessions and traces to isolate agent-utilities execution runs and diagnose spawned agent orchestration errors or performance drops.
domain: dev-workflows
tags: ['langfuse', 'telemetry', 'tracing', 'monitoring', 'debugging', 'langfuse-mcp']
requires: ['langfuse-mcp']
---

# langfuse_agent_tracer Workflow

Automatically queries Langfuse sessions and traces to isolate agent-utilities execution runs and diagnose spawned agent orchestration errors or performance drops.

### Step 0: langfuse-mcp
Retrieve lists of traces or recent sessions filtered by tags representing spawned agents or the agent orchestrator using trace_list or sessions_list actions.
Expected: trace_list_data, active_sessions

### Step 1: user-interaction
Present a structured dashboard of agent executions, highlighting traces with warning levels, high latencies, or error logs. Prompt the user to select an execution trace for deep analysis.
Expected: selected_trace_id, diagnosis_notes
Depends On: Step 0

### Step 2: langfuse-mcp
Retrieve complete telemetry span trees, inputs, outputs, and prompt details for the selected execution trace using the trace_get action.
Expected: trace_span_details
Depends On: Step 1
