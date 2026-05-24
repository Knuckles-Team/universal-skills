---
name: full_workspace_kg_ingest
description: Parallel execution workflow for full workspace kg ingest using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: Full Workspace Kg Ingest

This workflow defines the topological parallel execution steps for full workspace kg ingest.

## Steps

### Step 1: parse
Execute the parse phase for the full_workspace_kg_ingest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parse_artifacts
### Step 2: extract_concepts [depends_on: parse]
Execute the extract concepts phase for the full_workspace_kg_ingest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_concepts_artifacts
### Step 3: ingest [depends_on: extract_concepts]
Execute the ingest phase for the full_workspace_kg_ingest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ingest_artifacts
### Step 4: build_edges [depends_on: ingest]
Execute the build edges phase for the full_workspace_kg_ingest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: build_edges_artifacts
