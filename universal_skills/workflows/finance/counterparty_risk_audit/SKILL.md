---
name: counterparty_risk_audit
description: Parallel execution workflow for counterparty risk audit using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-emerald-exchange
---

# Parallel Workflow: Counterparty Risk Audit

This workflow defines the topological parallel execution steps for counterparty risk audit.

## Steps

### Step 1: volume
Execute the volume phase for the counterparty_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: volume_artifacts
### Step 2: insurance_fund
Execute the insurance fund phase for the counterparty_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: insurance_fund_artifacts
### Step 3: withdrawal_test
Execute the withdrawal test phase for the counterparty_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: withdrawal_test_artifacts
### Step 4: score [depends_on: volume, insurance_fund, withdrawal_test]
Execute the score phase for the counterparty_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
