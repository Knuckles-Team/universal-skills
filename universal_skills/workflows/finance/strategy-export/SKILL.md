---
name: strategy-export
description: >-
  Cross-platform strategy deployment: Convert → Validate → Deploy.
tags: [finance, strategy, export, deployment]
team_config: trading_department
agent: chief_trading_officer
metadata:
  author: agent-utilities
  version: '1.0.0'
  concept: 'CONCEPT:KG-2.6'
---
# Strategy Export Workflow

## Workflow Execution Steps

### Step 1: select-strategy
Pick a validated strategy from the Knowledge Graph.
Tool: `emerald_strategy(action="list")`

### Step 2: export
Convert to target format (PineScript/MQL5/TDX).
Tool: `emerald_strategy(action="export", strategy_id=..., format="pinescript")`

### Step 3: deploy-freqtrade
Deploy to freqtrade in paper mode for validation.
Tool: Route to freqtrade backend for dry-run.

### Step 4: share
Publish to community strategy registry.
Tool: Route to agent-utilities `strategy_sharing.py`.
