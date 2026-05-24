---
name: regulatory_compliance_check
description: Parallel execution workflow for regulatory compliance check using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-data-science
---

# Parallel Workflow: Regulatory Compliance Check

This workflow defines the topological parallel execution steps for regulatory compliance check.

## Steps

### Step 1: position_limits
Execute the position limits phase for the regulatory_compliance_check workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: position_limits_artifacts
### Step 2: wash_sale
Execute the wash sale phase for the regulatory_compliance_check workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: wash_sale_artifacts
### Step 3: pattern_day_trader
Execute the pattern day trader phase for the regulatory_compliance_check workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pattern_day_trader_artifacts
### Step 4: report [depends_on: position_limits, wash_sale, pattern_day_trader]
Execute the report phase for the regulatory_compliance_check workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
