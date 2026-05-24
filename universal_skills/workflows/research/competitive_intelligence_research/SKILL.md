---
name: competitive_intelligence_research
description: Parallel execution workflow for competitive intelligence research using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-searxng
---

# Parallel Workflow: Competitive Intelligence Research

This workflow defines the topological parallel execution steps for competitive intelligence research.

## Steps

### Step 1: products
Execute the products phase for the competitive_intelligence_research workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: products_artifacts
### Step 2: patents
Execute the patents phase for the competitive_intelligence_research workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: patents_artifacts
### Step 3: papers
Execute the papers phase for the competitive_intelligence_research workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: papers_artifacts
### Step 4: hiring
Execute the hiring phase for the competitive_intelligence_research workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: hiring_artifacts
### Step 5: swot_report [depends_on: products, patents, papers, hiring]
Execute the SWOT report phase for the competitive_intelligence_research workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: swot_report_artifacts
