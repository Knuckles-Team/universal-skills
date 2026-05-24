---
name: api_documentation_gen
description: Parallel execution workflow for api documentation gen using the Unified Parallel Engine
domain: dev-workflows
tags:
  - parallel-workflow
  - dev-workflows
  - mcp-github-mcp
---

# Parallel Workflow: Api Documentation Gen

This workflow defines the topological parallel execution steps for api documentation gen.

## Steps

### Step 1: fan_out_per_endpoint_extract_schema
Execute the Fan-out per endpoint: extract schema phase for the api_documentation_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: fan_out_per_endpoint_extract_schema_artifacts
### Step 2: generate_docs [depends_on: fan_out_per_endpoint_extract_schema]
Execute the generate docs phase for the api_documentation_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_docs_artifacts
### Step 3: examples [depends_on: generate_docs]
Execute the examples phase for the api_documentation_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: examples_artifacts
### Step 4: publish [depends_on: examples]
Execute the publish phase for the api_documentation_gen workflow under the dev-workflows domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
