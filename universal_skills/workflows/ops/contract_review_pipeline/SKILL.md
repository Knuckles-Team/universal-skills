---
name: contract_review_pipeline
description: Parallel execution workflow for contract review pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-stirlingpdf
---

# Parallel Workflow: Contract Review Pipeline

This workflow defines the topological parallel execution steps for contract review pipeline.

## Steps

### Step 1: ingest_contract
Execute the ingest contract phase for the contract_review_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ingest_contract_artifacts
### Step 2: extract_clauses [depends_on: ingest_contract]
Execute the extract clauses phase for the contract_review_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_clauses_artifacts
### Step 3: risk_analysis [depends_on: extract_clauses]
Execute the risk analysis phase for the contract_review_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: risk_analysis_artifacts
### Step 4: recommend [depends_on: risk_analysis]
Execute the recommend phase for the contract_review_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: recommend_artifacts
### Step 5: summary [depends_on: recommend]
Execute the summary phase for the contract_review_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: summary_artifacts
