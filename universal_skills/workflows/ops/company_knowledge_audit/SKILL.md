---
name: company_knowledge_audit
description: Parallel execution workflow for company knowledge audit using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-graph-os
---

# Parallel Workflow: Company Knowledge Audit

This workflow defines the topological parallel execution steps for company knowledge audit.

## Steps

### Step 1: each_dept_audits_their_domain
Execute the each dept audits their domain phase for the company_knowledge_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: each_dept_audits_their_domain_artifacts
### Step 2: aggregate [depends_on: each_dept_audits_their_domain]
Execute the aggregate phase for the company_knowledge_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: aggregate_artifacts
### Step 3: company_report [depends_on: aggregate]
Execute the company report phase for the company_knowledge_audit workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: company_report_artifacts
