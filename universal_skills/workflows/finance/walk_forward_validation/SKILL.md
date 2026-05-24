---
name: walk_forward_validation
description: Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.
domain: finance
tags: [walk-forward, validation, oversitting, backtest]
---
# Walk Forward Validation Workflow

This workflow coordinates multi-agent parallel executions of Divides historical feeds into overlapping walk-forward segments, runs parallel window fits, tests out-of-sample stability, and aggregates validation statistics.

### Step 1: window-generator [depends_on: none]
Divides historical market data into 5 overlapping training and testing segments.
Expected: segmented-walk-forward-windows

### Step 2: model-train-batch [depends_on: window-generator]
Runs parallel training sessions across all segmented windows.
Expected: window-fit-parameters

### Step 3: out-of-sample-test [depends_on: model-train-batch]
Backtests the fitted parameters on the subsequent test segments.
Expected: out-of-sample-performances

### Step 4: aggregate-validator [depends_on: out-of-sample-test]
Combines out-of-sample returns to verify strategy stability.
Expected: final-walk-forward-report

