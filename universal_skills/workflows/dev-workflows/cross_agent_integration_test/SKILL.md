---
name: cross_agent_integration_test
description: Parallel execution workflow for cross agent integration test using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-repository-manager
---

# Parallel Workflow: Cross Agent Integration Test

This workflow defines the topological parallel execution steps for cross agent integration test.

## Steps

### Step 1: agent_a_calls_agent_b
Execute the agent A calls agent B phase for the cross_agent_integration_test workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: agent_a_calls_agent_b_artifacts
### Step 2: verify_e2e [depends_on: agent_a_calls_agent_b]
Execute the verify E2E phase for the cross_agent_integration_test workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: verify_e2e_artifacts
### Step 3: report [depends_on: verify_e2e]
Execute the report phase for the cross_agent_integration_test workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
