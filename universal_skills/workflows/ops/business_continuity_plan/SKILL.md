---
name: business_continuity_plan
description: Parallel execution workflow for business continuity plan using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-servicenow
---

# Parallel Workflow: Business Continuity Plan

This workflow defines the topological parallel execution steps for business continuity plan.

## Steps

### Step 1: risk_assessment
Execute the risk assessment phase for the business_continuity_plan workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: risk_assessment_artifacts
### Step 2: recovery_priorities [depends_on: risk_assessment]
Execute the recovery priorities phase for the business_continuity_plan workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: recovery_priorities_artifacts
### Step 3: procedures [depends_on: recovery_priorities]
Execute the procedures phase for the business_continuity_plan workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: procedures_artifacts
### Step 4: test [depends_on: procedures]
Execute the test phase for the business_continuity_plan workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: test_artifacts
### Step 5: update [depends_on: test]
Execute the update phase for the business_continuity_plan workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_artifacts
