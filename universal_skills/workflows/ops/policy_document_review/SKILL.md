---
name: policy_document_review
description: Parallel execution workflow for policy document review using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-stirlingpdf
---

# Parallel Workflow: Policy Document Review

This workflow defines the topological parallel execution steps for policy document review.

## Steps

### Step 1: fan_out_per_policy_check_currency
Execute the Fan-out per policy: check currency phase for the policy_document_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_policy_check_currency_artifacts
### Step 2: compare_regulations [depends_on: fan_out_per_policy_check_currency]
Execute the compare regulations phase for the policy_document_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: compare_regulations_artifacts
### Step 3: update [depends_on: compare_regulations]
Execute the update phase for the policy_document_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: update_artifacts
### Step 4: distribute [depends_on: update]
Execute the distribute phase for the policy_document_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: distribute_artifacts
