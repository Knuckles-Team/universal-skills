---
name: quarterly_business_review
description: Parallel execution workflow for quarterly business review using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-data-science
---

# Parallel Workflow: Quarterly Business Review

This workflow defines the topological parallel execution steps for quarterly business review.

## Steps

### Step 1: financial
Execute the financial phase for the quarterly_business_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: financial_artifacts
### Step 2: operational
Execute the operational phase for the quarterly_business_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: operational_artifacts
### Step 3: customer
Execute the customer phase for the quarterly_business_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: customer_artifacts
### Step 4: product_metrics
Execute the product metrics phase for the quarterly_business_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: product_metrics_artifacts
### Step 5: presentation [depends_on: financial, operational, customer, product_metrics]
Execute the presentation phase for the quarterly_business_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: presentation_artifacts
