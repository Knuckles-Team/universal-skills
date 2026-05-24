---
name: daily_paper_scan
description: Parallel execution workflow for daily paper scan using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Daily Paper Scan

This workflow defines the topological parallel execution steps for daily paper scan.

## Steps

### Step 1: arxiv
Execute the arxiv phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: arxiv_artifacts
### Step 2: pmc
Execute the PMC phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: pmc_artifacts
### Step 3: biorxiv
Execute the biorxiv phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: biorxiv_artifacts
### Step 4: ssrn
Execute the SSRN phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: ssrn_artifacts
### Step 5: score [depends_on: arxiv, pmc, biorxiv, ssrn]
Execute the score phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
### Step 6: download_top [depends_on: score]
Execute the download top phase for the daily_paper_scan workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: download_top_artifacts
