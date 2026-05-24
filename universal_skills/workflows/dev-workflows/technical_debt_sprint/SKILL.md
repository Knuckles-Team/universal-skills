---
name: technical_debt_sprint
description: Parallel execution workflow for technical debt sprint using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Technical Debt Sprint

This workflow defines the topological parallel execution steps for technical debt sprint.

## Steps

### Step 1: lint_fixes
Execute the lint fixes phase for the technical_debt_sprint workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: lint_fixes_artifacts
### Step 2: dead_code
Execute the dead code phase for the technical_debt_sprint workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dead_code_artifacts
### Step 3: type_coverage
Execute the type coverage phase for the technical_debt_sprint workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: type_coverage_artifacts
### Step 4: doc_gaps
Execute the doc gaps phase for the technical_debt_sprint workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: doc_gaps_artifacts
### Step 5: parallel_prs [depends_on: lint_fixes, dead_code, type_coverage, doc_gaps]
Execute the parallel PRs phase for the technical_debt_sprint workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_prs_artifacts
