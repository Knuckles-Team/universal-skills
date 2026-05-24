---
name: crypto_onchain_analytics
description: Parallel execution workflow for crypto onchain analytics using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Crypto Onchain Analytics

This workflow defines the topological parallel execution steps for crypto onchain analytics.

## Steps

### Step 1: whale_wallets
Execute the whale wallets phase for the crypto_onchain_analytics workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: whale_wallets_artifacts
### Step 2: exchange_flows
Execute the exchange flows phase for the crypto_onchain_analytics workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: exchange_flows_artifacts
### Step 3: dex_volume
Execute the DEX volume phase for the crypto_onchain_analytics workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dex_volume_artifacts
### Step 4: staking
Execute the staking phase for the crypto_onchain_analytics workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: staking_artifacts
### Step 5: signals [depends_on: whale_wallets, exchange_flows, dex_volume, staking]
Execute the signals phase for the crypto_onchain_analytics workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: signals_artifacts
