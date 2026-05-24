---
name: test_coverage_campaign
description: Parallel execution workflow for test coverage campaign using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Test Coverage Campaign

This workflow defines the topological parallel execution steps for test coverage campaign.

## Steps

### Step 1: analyze_gaps
Execute the analyze gaps phase for the test_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_gaps_artifacts
### Step 2: generate_tests [depends_on: analyze_gaps]
Execute the generate tests phase for the test_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_tests_artifacts
### Step 3: run [depends_on: generate_tests]
Execute the run phase for the test_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: run_artifacts
### Step 4: report [depends_on: run]
Execute the report phase for the test_coverage_campaign workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
