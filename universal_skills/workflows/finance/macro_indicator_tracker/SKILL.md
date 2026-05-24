---
name: macro_indicator_tracker
description: Parallel execution workflow for macro indicator tracker using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Macro Indicator Tracker

This workflow defines the topological parallel execution steps for macro indicator tracker.

## Steps

### Step 1: gdp
Execute the GDP phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gdp_artifacts
### Step 2: cpi
Execute the CPI phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: cpi_artifacts
### Step 3: pmi
Execute the PMI phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pmi_artifacts
### Step 4: yields
Execute the yields phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: yields_artifacts
### Step 5: employment
Execute the employment phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: employment_artifacts
### Step 6: dashboard [depends_on: gdp, cpi, pmi, yields, employment]
Execute the dashboard phase for the macro_indicator_tracker workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dashboard_artifacts
