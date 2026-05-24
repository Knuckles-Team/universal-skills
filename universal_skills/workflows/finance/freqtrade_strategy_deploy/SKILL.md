---
name: freqtrade_strategy_deploy
description: Scaffolds standard-compliant Python strategy files for Freqtrade, runs parallel hyperparameter optimizations, dry-runs them, and elevates to live webhook monitoring.
domain: finance
tags: [freqtrade, deploy, hyperopt, automation]
---
# Freqtrade Strategy Deploy Workflow

This workflow coordinates multi-agent parallel executions of Scaffolds standard-compliant Python strategy files for Freqtrade, runs parallel hyperparameter optimizations, dry-runs them, and elevates to live webhook monitoring.

### Step 1: strategy-coder [depends_on: none]
Code a syntax-valid Freqtrade python strategy subclass.
Expected: freqtrade-strategy-file

### Step 2: hyperparameter-tuner [depends_on: strategy-coder]
Run Freqtrade hyperopt parameter sweeps in parallel.
Expected: optimized-hyperparameters

### Step 3: dry-run-verify [depends_on: hyperparameter-tuner]
Deploy to dry-run container stack and assert correct connection states.
Expected: dry-run-stability-metrics

### Step 4: live-enable-trigger [depends_on: dry-run-verify]
Elevate to live exchange endpoints and register with Telegram webhook.
Expected: live-deployment-logs

