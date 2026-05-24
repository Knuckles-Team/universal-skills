---
name: liquidity_risk_assessment
description: Parallel execution workflow for liquidity risk assessment using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Liquidity Risk Assessment

This workflow defines the topological parallel execution steps for liquidity risk assessment.

## Steps

### Step 1: volume_profile
Execute the volume profile phase for the liquidity_risk_assessment workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: volume_profile_artifacts
### Step 2: bid_ask_spread
Execute the bid-ask spread phase for the liquidity_risk_assessment workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: bid_ask_spread_artifacts
### Step 3: market_impact
Execute the market impact phase for the liquidity_risk_assessment workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: market_impact_artifacts
### Step 4: score [depends_on: volume_profile, bid_ask_spread, market_impact]
Execute the score phase for the liquidity_risk_assessment workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
