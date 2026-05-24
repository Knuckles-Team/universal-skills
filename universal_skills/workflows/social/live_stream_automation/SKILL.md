---
name: live_stream_automation
description: Parallel execution workflow for live stream automation using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-owncast
---

# Parallel Workflow: Live Stream Automation

This workflow defines the topological parallel execution steps for live stream automation.

## Steps

### Step 1: prepare_title
Execute the prepare title phase for the live_stream_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: prepare_title_artifacts
### Step 2: configure_obs [depends_on: prepare_title]
Execute the configure OBS phase for the live_stream_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: configure_obs_artifacts
### Step 3: announce [depends_on: configure_obs]
Execute the announce phase for the live_stream_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: announce_artifacts
### Step 4: engage_chat [depends_on: announce]
Execute the engage chat phase for the live_stream_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: engage_chat_artifacts
### Step 5: post_stream_summary [depends_on: engage_chat]
Execute the post-stream summary phase for the live_stream_automation workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: post_stream_summary_artifacts
