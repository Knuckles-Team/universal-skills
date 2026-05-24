---
name: slippage_analysis
description: Parallel execution workflow for slippage analysis using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Slippage Analysis

This workflow defines the topological parallel execution steps for slippage analysis.

## Steps

### Step 1: pull_fills
Execute the pull fills phase for the slippage_analysis workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pull_fills_artifacts
### Step 2: compare_to_signal_price [depends_on: pull_fills]
Execute the compare to signal price phase for the slippage_analysis workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_to_signal_price_artifacts
### Step 3: calc_slippage_stats [depends_on: compare_to_signal_price]
Execute the calc slippage stats phase for the slippage_analysis workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: calc_slippage_stats_artifacts
### Step 4: optimize [depends_on: calc_slippage_stats]
Execute the optimize phase for the slippage_analysis workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: optimize_artifacts
