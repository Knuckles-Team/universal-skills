---
name: esg_screening_pipeline
description: Parallel execution workflow for esg screening pipeline using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-scholarx
---

# Parallel Workflow: Esg Screening Pipeline

This workflow defines the topological parallel execution steps for esg screening pipeline.

## Steps

### Step 1: esg_score_lookup
Execute the ESG score lookup phase for the esg_screening_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: esg_score_lookup_artifacts
### Step 2: controversy_check [depends_on: esg_score_lookup]
Execute the controversy check phase for the esg_screening_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: controversy_check_artifacts
### Step 3: exclusion_filter [depends_on: controversy_check]
Execute the exclusion filter phase for the esg_screening_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: exclusion_filter_artifacts
