---
name: lead_generation_pipeline
description: Parallel execution workflow for lead generation pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-searxng
---

# Parallel Workflow: Lead Generation Pipeline

This workflow defines the topological parallel execution steps for lead generation pipeline.

## Steps

### Step 1: identify_icp
Execute the identify ICP phase for the lead_generation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_icp_artifacts
### Step 2: scrape_prospects [depends_on: identify_icp]
Execute the scrape prospects phase for the lead_generation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scrape_prospects_artifacts
### Step 3: score [depends_on: scrape_prospects]
Execute the score phase for the lead_generation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
### Step 4: enrich [depends_on: score]
Execute the enrich phase for the lead_generation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: enrich_artifacts
### Step 5: outreach [depends_on: enrich]
Execute the outreach phase for the lead_generation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: outreach_artifacts
