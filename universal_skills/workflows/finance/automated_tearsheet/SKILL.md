---
name: automated_tearsheet
description: Parallel execution workflow for automated tearsheet using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Automated Tearsheet

This workflow defines the topological parallel execution steps for automated tearsheet.

## Steps

### Step 1: pull_performance
Execute the pull performance phase for the automated_tearsheet workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pull_performance_artifacts
### Step 2: calc_metrics [depends_on: pull_performance]
Execute the calc metrics phase for the automated_tearsheet workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: calc_metrics_artifacts
### Step 3: generate_charts [depends_on: calc_metrics]
Execute the generate charts phase for the automated_tearsheet workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_charts_artifacts
### Step 4: email_report [depends_on: generate_charts]
Execute the email report phase for the automated_tearsheet workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: email_report_artifacts
