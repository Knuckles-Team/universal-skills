---
name: vendor_evaluation_pipeline
description: Parallel execution workflow for vendor evaluation pipeline using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-searxng
---

# Parallel Workflow: Vendor Evaluation Pipeline

This workflow defines the topological parallel execution steps for vendor evaluation pipeline.

## Steps

### Step 1: fan_out_per_vendor_capabilities
Execute the Fan-out per vendor: capabilities phase for the vendor_evaluation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_vendor_capabilities_artifacts
### Step 2: pricing
Execute the pricing phase for the vendor_evaluation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pricing_artifacts
### Step 3: reviews
Execute the reviews phase for the vendor_evaluation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: reviews_artifacts
### Step 4: risk
Execute the risk phase for the vendor_evaluation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: risk_artifacts
### Step 5: scorecard [depends_on: fan_out_per_vendor_capabilities, pricing, reviews, risk]
Execute the scorecard phase for the vendor_evaluation_pipeline workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scorecard_artifacts
