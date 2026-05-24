---
name: company_quarterly_review
description: Parallel execution workflow for company quarterly review using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-ALL MCPs
---

# Parallel Workflow: Company Quarterly Review

This workflow defines the topological parallel execution steps for company quarterly review.

## Steps

### Step 1: each_dept_produces_report
Execute the each dept produces report phase for the company_quarterly_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: each_dept_produces_report_artifacts
### Step 2: dept_heads_synthesize [depends_on: each_dept_produces_report]
Execute the dept heads synthesize phase for the company_quarterly_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dept_heads_synthesize_artifacts
### Step 3: ceo_summary [depends_on: dept_heads_synthesize]
Execute the CEO summary phase for the company_quarterly_review workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ceo_summary_artifacts
