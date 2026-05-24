---
name: alpha-discovery
description: >-
  Automated alpha mining: Scan market data → Generate factors → Score → Fuse signals.
tags: [finance, alpha, signals, research]
team_config: trading_department
agent: quant_research_analyst
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---
# Alpha Discovery Workflow

## Workflow Execution Steps

### Step 1: data-ingest
Fetch market data for target universe.
Tool: `emerald_market_data(action="historical", symbol=..., period="1y")`

### Step 2: feature-engineering
Generate alpha factors with IC/IR scoring.
Tool: `emerald_signals(action="alpha", ticker=...)`

### Step 3: regime-detection
Classify current market regime (Bull/Bear/Sideways/Crisis).
Tool: `emerald_signals(action="regime", ticker=...)`

### Step 4: signal-fusion
Bayesian fusion of all signal sources.
Tool: `emerald_signals(action="fuse", ticker=...)`

### Step 5: kg-persist
Store AlphaFactor and TradingSignal nodes in KG.
Tool: `graph_write(action="add_node", node_type="AlphaFactor", ...)`
