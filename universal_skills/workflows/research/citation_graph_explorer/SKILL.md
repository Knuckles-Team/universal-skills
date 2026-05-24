---
name: citation_graph_explorer
description: Parallel execution workflow for citation graph explorer using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Citation Graph Explorer

This workflow defines the topological parallel execution steps for citation graph explorer.

## Steps

### Step 1: seed_paper
Execute the seed paper phase for the citation_graph_explorer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: seed_paper_artifacts
### Step 2: forward_backward_citations [depends_on: seed_paper]
Execute the forward/backward citations phase for the citation_graph_explorer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: forward_backward_citations_artifacts
### Step 3: cluster [depends_on: forward_backward_citations]
Execute the cluster phase for the citation_graph_explorer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cluster_artifacts
### Step 4: visualize_in_kg [depends_on: cluster]
Execute the visualize in KG phase for the citation_graph_explorer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: visualize_in_kg_artifacts
