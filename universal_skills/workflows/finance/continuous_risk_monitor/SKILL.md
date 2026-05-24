---
name: continuous_risk_monitor
description: Parallel execution workflow for continuous risk monitor using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Continuous Risk Monitor

This workflow defines the topological parallel execution steps for continuous risk monitor.

## Steps

### Step 1: drawdown_check
Execute the drawdown check phase for the continuous_risk_monitor workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: drawdown_check_artifacts
### Step 2: daily_loss
Execute the daily loss phase for the continuous_risk_monitor workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: daily_loss_artifacts
### Step 3: regime_shift
Execute the regime shift phase for the continuous_risk_monitor workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: regime_shift_artifacts
### Step 4: position_limits
Execute the position limits phase for the continuous_risk_monitor workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: position_limits_artifacts
### Step 5: circuit_breaker [depends_on: drawdown_check, daily_loss, regime_shift, position_limits]
Execute the circuit breaker phase for the continuous_risk_monitor workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: circuit_breaker_artifacts
