---
name: portfolio_tearsheet_gen
description: Parallel execution workflow for portfolio tearsheet gen using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Portfolio Tearsheet Gen

This workflow defines the topological parallel execution steps for portfolio tearsheet gen.

## Steps

### Step 1: returns
Execute the returns phase for the portfolio_tearsheet_gen workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: returns_artifacts
### Step 2: drawdown
Execute the drawdown phase for the portfolio_tearsheet_gen workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: drawdown_artifacts
### Step 3: monthly_heatmap
Execute the monthly heatmap phase for the portfolio_tearsheet_gen workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monthly_heatmap_artifacts
### Step 4: monte_carlo
Execute the monte carlo phase for the portfolio_tearsheet_gen workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monte_carlo_artifacts
### Step 5: pdf_report [depends_on: returns, drawdown, monthly_heatmap, monte_carlo]
Execute the PDF report phase for the portfolio_tearsheet_gen workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pdf_report_artifacts
