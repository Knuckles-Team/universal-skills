---
name: market_regime_report
description: Parallel execution workflow for market regime report using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Market Regime Report

This workflow defines the topological parallel execution steps for market regime report.

## Steps

### Step 1: volatility_regime
Execute the volatility regime phase for the market_regime_report workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: volatility_regime_artifacts
### Step 2: trend_regime
Execute the trend regime phase for the market_regime_report workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trend_regime_artifacts
### Step 3: correlation_regime
Execute the correlation regime phase for the market_regime_report workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: correlation_regime_artifacts
### Step 4: daily_brief [depends_on: volatility_regime, trend_regime, correlation_regime]
Execute the daily brief phase for the market_regime_report workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: daily_brief_artifacts
