---
name: autonomous_content_pipeline
description: Parallel execution workflow for autonomous content pipeline using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-searxng
---

# Parallel Workflow: Autonomous Content Pipeline

This workflow defines the topological parallel execution steps for autonomous content pipeline.

## Steps

### Step 1: trend_discovery
Execute the trend discovery phase for the autonomous_content_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trend_discovery_artifacts
### Step 2: research [depends_on: trend_discovery]
Execute the research phase for the autonomous_content_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: research_artifacts
### Step 3: script [depends_on: research]
Execute the script phase for the autonomous_content_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: script_artifacts
### Step 4: assets [depends_on: script]
Execute the assets phase for the autonomous_content_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: assets_artifacts
### Step 5: publish [depends_on: assets]
Execute the publish phase for the autonomous_content_pipeline workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
