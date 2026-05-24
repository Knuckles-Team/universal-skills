---
name: author_tracker
description: Parallel execution workflow for author tracker using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Author Tracker

This workflow defines the topological parallel execution steps for author tracker.

## Steps

### Step 1: publications
Execute the publications phase for the author_tracker workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publications_artifacts
### Step 2: h_index [depends_on: publications]
Execute the h-index phase for the author_tracker workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: h_index_artifacts
### Step 3: recent_work [depends_on: h_index]
Execute the recent work phase for the author_tracker workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: recent_work_artifacts
### Step 4: collaboration_graph [depends_on: recent_work]
Execute the collaboration graph phase for the author_tracker workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: collaboration_graph_artifacts
