---
name: workplace_safety_audit
description: Parallel execution workflow for workplace safety audit using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Workplace Safety Audit

This workflow defines the topological parallel execution steps for workplace safety audit.

## Steps

### Step 1: checklist
Execute the checklist phase for the workplace_safety_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: checklist_artifacts
### Step 2: findings [depends_on: checklist]
Execute the findings phase for the workplace_safety_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: findings_artifacts
### Step 3: remediation_plan [depends_on: findings]
Execute the remediation plan phase for the workplace_safety_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: remediation_plan_artifacts
### Step 4: follow_up [depends_on: remediation_plan]
Execute the follow-up phase for the workplace_safety_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: follow_up_artifacts
