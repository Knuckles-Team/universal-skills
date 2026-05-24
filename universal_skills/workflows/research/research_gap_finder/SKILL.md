---
name: research_gap_finder
description: Parallel execution workflow for research gap finder using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Research Gap Finder

This workflow defines the topological parallel execution steps for research gap finder.

## Steps

### Step 1: survey_literature
Execute the survey literature phase for the research_gap_finder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: survey_literature_artifacts
### Step 2: identify_gaps [depends_on: survey_literature]
Execute the identify gaps phase for the research_gap_finder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: identify_gaps_artifacts
### Step 3: rank_by_impact [depends_on: identify_gaps]
Execute the rank by impact phase for the research_gap_finder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: rank_by_impact_artifacts
### Step 4: report [depends_on: rank_by_impact]
Execute the report phase for the research_gap_finder workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
