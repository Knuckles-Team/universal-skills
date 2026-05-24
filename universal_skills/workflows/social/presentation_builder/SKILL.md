---
name: presentation_builder
description: Parallel execution workflow for presentation builder using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Presentation Builder

This workflow defines the topological parallel execution steps for presentation builder.

## Steps

### Step 1: research
Execute the research phase for the presentation_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: research_artifacts
### Step 2: outline [depends_on: research]
Execute the outline phase for the presentation_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: outline_artifacts
### Step 3: generate_slides [depends_on: outline]
Execute the generate slides phase for the presentation_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_slides_artifacts
### Step 4: design [depends_on: generate_slides]
Execute the design phase for the presentation_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: design_artifacts
### Step 5: export [depends_on: design]
Execute the export phase for the presentation_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: export_artifacts
