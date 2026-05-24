---
name: risk_dashboard_refresh
description: Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.
domain: finance
tags: [risk, dashboard, var, drawdown]
---
# Risk Dashboard Refresh Workflow

This workflow coordinates multi-agent parallel executions of Pulls daily assets returns, computes Value-at-Risk parameters, extracts maximum drawdown ratios, and updates dashboard.

### Step 1: portfolio-returns-fetcher [depends_on: none]
Fetches daily rolling returns logs for active holdings.
Expected: historical-daily-returns

### Step 2: var-calculator [depends_on: portfolio-returns-fetcher]
Computes Parametric and Monte Carlo Value-at-Risk (VaR) parameters.
Expected: value-at-risk-metrics

### Step 3: drawdown-tracker [depends_on: portfolio-returns-fetcher]
Measures rolling drawdown, Sharpe, and Sortino statistics.
Expected: drawdown-and-performance-stats

### Step 4: dashboard-synthesis [depends_on: var-calculator, drawdown-tracker]
Compiles metrics and updates dashboard files.
Expected: fused-risk-tearsheet

