---
name: competitive_content_analysis
description: Parallel execution workflow for competitive content analysis using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-searxng
---

# Parallel Workflow: Competitive Content Analysis

This workflow defines the topological parallel execution steps for competitive content analysis.

## Steps

### Step 1: scrape_content
Execute the scrape content phase for the competitive_content_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scrape_content_artifacts
### Step 2: analyze_frequency_topics [depends_on: scrape_content]
Execute the analyze frequency/topics phase for the competitive_content_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: analyze_frequency_topics_artifacts
### Step 3: gap_report [depends_on: analyze_frequency_topics]
Execute the gap report phase for the competitive_content_analysis workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: gap_report_artifacts
