---
name: compliance_audit_sweep
description: Parallel execution workflow for compliance audit sweep using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Compliance Audit Sweep

This workflow defines the topological parallel execution steps for compliance audit sweep.

## Steps

### Step 1: gdpr
Execute the GDPR phase for the compliance_audit_sweep workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gdpr_artifacts
### Step 2: soc2
Execute the SOC2 phase for the compliance_audit_sweep workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: soc2_artifacts
### Step 3: hipaa
Execute the HIPAA phase for the compliance_audit_sweep workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: hipaa_artifacts
### Step 4: check_controls [depends_on: gdpr, soc2, hipaa]
Execute the check controls phase for the compliance_audit_sweep workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_controls_artifacts
### Step 5: gap_report [depends_on: check_controls]
Execute the gap report phase for the compliance_audit_sweep workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gap_report_artifacts
