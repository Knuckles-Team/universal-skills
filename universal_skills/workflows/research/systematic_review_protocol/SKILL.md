---
name: systematic_review_protocol
description: Parallel execution workflow for systematic review protocol using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Systematic Review Protocol

This workflow defines the topological parallel execution steps for systematic review protocol.

## Steps

### Step 1: define_pico
Execute the define PICO phase for the systematic_review_protocol workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: define_pico_artifacts
### Step 2: search [depends_on: define_pico]
Execute the search phase for the systematic_review_protocol workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: search_artifacts
### Step 3: screen [depends_on: search]
Execute the screen phase for the systematic_review_protocol workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: screen_artifacts
### Step 4: extract [depends_on: screen]
Execute the extract phase for the systematic_review_protocol workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_artifacts
### Step 5: meta_analyze [depends_on: extract]
Execute the meta-analyze phase for the systematic_review_protocol workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: meta_analyze_artifacts
