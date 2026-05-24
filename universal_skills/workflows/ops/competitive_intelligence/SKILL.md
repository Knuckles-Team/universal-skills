---
name: competitive_intelligence
description: Parallel execution workflow for competitive intelligence using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-searxng
---

# Parallel Workflow: Competitive Intelligence

This workflow defines the topological parallel execution steps for competitive intelligence.

## Steps

### Step 1: pricing
Execute the pricing phase for the competitive_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pricing_artifacts
### Step 2: features
Execute the features phase for the competitive_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: features_artifacts
### Step 3: hiring
Execute the hiring phase for the competitive_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: hiring_artifacts
### Step 4: news
Execute the news phase for the competitive_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: news_artifacts
### Step 5: dashboard [depends_on: pricing, features, hiring, news]
Execute the dashboard phase for the competitive_intelligence workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dashboard_artifacts
