---
name: pnl_attribution
description: Parallel execution workflow for pnl attribution using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Pnl Attribution

This workflow defines the topological parallel execution steps for pnl attribution.

## Steps

### Step 1: fetch_trades
Execute the fetch trades phase for the pnl_attribution workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fetch_trades_artifacts
### Step 2: decompose_by_strategy [depends_on: fetch_trades]
Execute the decompose by strategy phase for the pnl_attribution workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: decompose_by_strategy_artifacts
### Step 3: alpha_vs_beta [depends_on: decompose_by_strategy]
Execute the alpha vs beta phase for the pnl_attribution workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: alpha_vs_beta_artifacts
### Step 4: report [depends_on: alpha_vs_beta]
Execute the report phase for the pnl_attribution workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
