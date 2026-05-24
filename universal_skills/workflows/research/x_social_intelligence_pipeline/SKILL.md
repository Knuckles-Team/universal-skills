---
name: x_social_intelligence_pipeline
description: Parallel execution workflow for x social intelligence pipeline using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: X Social Intelligence Pipeline

This workflow defines the topological parallel execution steps for x social intelligence pipeline.

## Steps

### Step 1: search_x
Execute the search X phase for the x_social_intelligence_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: search_x_artifacts
### Step 2: classify [depends_on: search_x]
Execute the classify phase for the x_social_intelligence_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 3: score [depends_on: classify]
Execute the score phase for the x_social_intelligence_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
### Step 4: kg_ingest [depends_on: score]
Execute the KG ingest phase for the x_social_intelligence_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: kg_ingest_artifacts
### Step 5: evolution_trigger [depends_on: kg_ingest]
Execute the evolution trigger phase for the x_social_intelligence_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: evolution_trigger_artifacts
