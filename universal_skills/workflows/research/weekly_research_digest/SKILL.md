---
name: weekly_research_digest
description: Parallel execution workflow for weekly research digest using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-scholarx
---

# Parallel Workflow: Weekly Research Digest

This workflow defines the topological parallel execution steps for weekly research digest.

## Steps

### Step 1: scan
Execute the scan phase for the weekly_research_digest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_artifacts
### Step 2: score [depends_on: scan]
Execute the score phase for the weekly_research_digest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: score_artifacts
### Step 3: summarize_top_5 [depends_on: score]
Execute the summarize top 5 phase for the weekly_research_digest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: summarize_top_5_artifacts
### Step 4: email_newsletter [depends_on: summarize_top_5]
Execute the email newsletter phase for the weekly_research_digest workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: email_newsletter_artifacts
