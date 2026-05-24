---
name: operational_risk_audit
description: Parallel execution workflow for operational risk audit using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-uptime-kuma
---

# Parallel Workflow: Operational Risk Audit

This workflow defines the topological parallel execution steps for operational risk audit.

## Steps

### Step 1: api_uptime
Execute the API uptime phase for the operational_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: api_uptime_artifacts
### Step 2: latency
Execute the latency phase for the operational_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: latency_artifacts
### Step 3: error_rates
Execute the error rates phase for the operational_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: error_rates_artifacts
### Step 4: failover_test
Execute the failover test phase for the operational_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: failover_test_artifacts
### Step 5: report [depends_on: api_uptime, latency, error_rates, failover_test]
Execute the report phase for the operational_risk_audit workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
