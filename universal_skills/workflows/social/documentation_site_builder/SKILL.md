---
name: documentation_site_builder
description: Parallel execution workflow for documentation site builder using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-repository-manager
---

# Parallel Workflow: Documentation Site Builder

This workflow defines the topological parallel execution steps for documentation site builder.

## Steps

### Step 1: extract_from_code
Execute the extract from code phase for the documentation_site_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_from_code_artifacts
### Step 2: write_docs [depends_on: extract_from_code]
Execute the write docs phase for the documentation_site_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: write_docs_artifacts
### Step 3: generate_api_ref [depends_on: write_docs]
Execute the generate API ref phase for the documentation_site_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_api_ref_artifacts
### Step 4: deploy [depends_on: generate_api_ref]
Execute the deploy phase for the documentation_site_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: deploy_artifacts
