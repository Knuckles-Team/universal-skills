---
name: crypto-arbitrage
description: >-
  Cross-market statistical arbitrage: Cointegration → Threshold → Execute.
tags: [finance, crypto, arbitrage, stat-arb]
team_config: trading_department
agent: quant_research_analyst
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---
# Crypto Arbitrage Workflow

## Workflow Execution Steps

### Step 1: pair-scan
Identify cointegrated pairs across exchanges.
Tool: Route to agent-utilities `cross_market_arb.py` CointegrationAnalyzer.

### Step 2: ou-estimate
Ornstein-Uhlenbeck parameter estimation for mean-reversion speed.

### Step 3: on-chain-check
Check whale alerts, funding rates, DEX volumes.
Tool: Route to agent-utilities `crypto_connector.py` OnChainAnalytics.

### Step 4: risk-check
Pre-trade risk validation.
Tool: `emerald_risk(action="drawdown_check")`

### Step 5: execute-arb
Submit paired orders via exchange backend.
Tool: `emerald_orders(action="submit", ...)` for both legs.
