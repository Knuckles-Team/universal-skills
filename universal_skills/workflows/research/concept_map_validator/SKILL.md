---
name: concept_map_validator
description: Parallel execution workflow for concept map validator using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-graph-os
---

# Parallel Workflow: Concept Map Validator

This workflow defines the topological parallel execution steps for concept map validator.

## Steps

### Step 1: fan_out_per_concept_verify_code_exists
Execute the Fan-out per concept: verify code exists phase for the concept_map_validator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_concept_verify_code_exists_artifacts
### Step 2: check_docs [depends_on: fan_out_per_concept_verify_code_exists]
Execute the check docs phase for the concept_map_validator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_docs_artifacts
### Step 3: check_tests [depends_on: check_docs]
Execute the check tests phase for the concept_map_validator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: check_tests_artifacts
### Step 4: report_drift [depends_on: check_tests]
Execute the report drift phase for the concept_map_validator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_drift_artifacts
