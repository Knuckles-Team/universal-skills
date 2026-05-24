---
name: qlib_factor_backtest
description: Parallel execution workflow for qlib factor backtest using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Qlib Factor Backtest

This workflow defines the topological parallel execution steps for qlib factor backtest.

## Steps

### Step 1: prepare_data
Execute the prepare data phase for the qlib_factor_backtest workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prepare_data_artifacts
### Step 2: fit_model [depends_on: prepare_data]
Execute the fit model phase for the qlib_factor_backtest workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fit_model_artifacts
### Step 3: backtest [depends_on: fit_model]
Execute the backtest phase for the qlib_factor_backtest workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: backtest_artifacts
### Step 4: ic_analysis [depends_on: backtest]
Execute the IC analysis phase for the qlib_factor_backtest workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ic_analysis_artifacts
