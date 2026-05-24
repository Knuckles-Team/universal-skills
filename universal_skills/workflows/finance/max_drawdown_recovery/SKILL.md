---
name: max_drawdown_recovery
description: Parallel execution workflow for max drawdown recovery using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-emerald-exchange
---

# Parallel Workflow: Max Drawdown Recovery

This workflow defines the topological parallel execution steps for max drawdown recovery.

## Steps

### Step 1: detect_dd
Execute the detect DD phase for the max_drawdown_recovery workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: detect_dd_artifacts
### Step 2: pause_strategies [depends_on: detect_dd]
Execute the pause strategies phase for the max_drawdown_recovery workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pause_strategies_artifacts
### Step 3: hedge [depends_on: pause_strategies]
Execute the hedge phase for the max_drawdown_recovery workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: hedge_artifacts
### Step 4: monitor_recovery [depends_on: hedge]
Execute the monitor recovery phase for the max_drawdown_recovery workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monitor_recovery_artifacts
### Step 5: resume [depends_on: monitor_recovery]
Execute the resume phase for the max_drawdown_recovery workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: resume_artifacts
