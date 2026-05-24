---
name: compliance_framework_deploy
description: Parallel execution workflow for compliance framework deploy using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Compliance Framework Deploy

This workflow defines the topological parallel execution steps for compliance framework deploy.

## Steps

### Step 1: select_framework
Execute the select framework phase for the compliance_framework_deploy workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: select_framework_artifacts
### Step 2: gap_analysis [depends_on: select_framework]
Execute the gap analysis phase for the compliance_framework_deploy workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gap_analysis_artifacts
### Step 3: parallel_impl_per_control [depends_on: gap_analysis]
Execute the parallel impl per control phase for the compliance_framework_deploy workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_impl_per_control_artifacts
### Step 4: audit [depends_on: parallel_impl_per_control]
Execute the audit phase for the compliance_framework_deploy workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: audit_artifacts
