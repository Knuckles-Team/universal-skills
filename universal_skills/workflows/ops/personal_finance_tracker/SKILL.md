---
name: personal_finance_tracker
description: Parallel execution workflow for personal finance tracker using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-data-science
---

# Parallel Workflow: Personal Finance Tracker

This workflow defines the topological parallel execution steps for personal finance tracker.

## Steps

### Step 1: collect_transactions
Execute the collect transactions phase for the personal_finance_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collect_transactions_artifacts
### Step 2: categorize [depends_on: collect_transactions]
Execute the categorize phase for the personal_finance_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: categorize_artifacts
### Step 3: budget_comparison [depends_on: categorize]
Execute the budget comparison phase for the personal_finance_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: budget_comparison_artifacts
### Step 4: report [depends_on: budget_comparison]
Execute the report phase for the personal_finance_tracker workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
