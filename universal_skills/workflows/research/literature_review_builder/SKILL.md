---
name: literature_review_builder
description: Parallel execution workflow for literature review builder using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Literature Review Builder

This workflow defines the topological parallel execution steps for literature review builder.

## Steps

### Step 1: define_scope
Execute the define scope phase for the literature_review_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: define_scope_artifacts
### Step 2: parallel_search [depends_on: define_scope]
Execute the parallel search phase for the literature_review_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: parallel_search_artifacts
### Step 3: dedupe [depends_on: parallel_search]
Execute the dedupe phase for the literature_review_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dedupe_artifacts
### Step 4: summarize [depends_on: dedupe]
Execute the summarize phase for the literature_review_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: summarize_artifacts
### Step 5: bibliography [depends_on: summarize]
Execute the bibliography phase for the literature_review_builder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: bibliography_artifacts
