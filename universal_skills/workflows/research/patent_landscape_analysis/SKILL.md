---
name: patent_landscape_analysis
description: Parallel execution workflow for patent landscape analysis using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-searxng
---

# Parallel Workflow: Patent Landscape Analysis

This workflow defines the topological parallel execution steps for patent landscape analysis.

## Steps

### Step 1: search_patents
Execute the search patents phase for the patent_landscape_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: search_patents_artifacts
### Step 2: classify [depends_on: search_patents]
Execute the classify phase for the patent_landscape_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 3: competitor_mapping [depends_on: classify]
Execute the competitor mapping phase for the patent_landscape_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: competitor_mapping_artifacts
### Step 4: report [depends_on: competitor_mapping]
Execute the report phase for the patent_landscape_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
