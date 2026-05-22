---
name: portfolio-analysis
description: >-
  Analyzes a financial portfolio and extracts key risk metrics, exposures, and
  returns against a benchmark.
tags: [finance, analysis, portfolio]
metadata:
  author: agent-utilities
  version: '1.0.0'
---
# Portfolio Analysis Workflow

> [!NOTE]
> This workflow was migrated from the legacy WorkflowBundle preset system.

## Workflow Execution Steps

### Step 1: data-extractor
Extract the latest holding data from the portfolio system and fetch benchmark data.

### Step 2: risk-analyzer
Calculate risk metrics, exposures, and VaR based on the extracted holding data.

### Step 3: report-generator
Synthesize the risk metrics and holding data into a formatted markdown report.
