---
name: finrl_training_pipeline
description: Parallel execution workflow for finrl training pipeline using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Finrl Training Pipeline

This workflow defines the topological parallel execution steps for finrl training pipeline.

## Steps

### Step 1: setup_env
Execute the setup env phase for the finrl_training_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: setup_env_artifacts
### Step 2: train_ppo_dqn [depends_on: setup_env]
Execute the train PPO/DQN phase for the finrl_training_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: train_ppo_dqn_artifacts
### Step 3: evaluate [depends_on: train_ppo_dqn]
Execute the evaluate phase for the finrl_training_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: evaluate_artifacts
### Step 4: paper_trade [depends_on: evaluate]
Execute the paper trade phase for the finrl_training_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: paper_trade_artifacts
### Step 5: report [depends_on: paper_trade]
Execute the report phase for the finrl_training_pipeline workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
