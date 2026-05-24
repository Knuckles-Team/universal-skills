---
name: social_media_campaign
description: Parallel execution workflow for social media campaign using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-postiz
---

# Parallel Workflow: Social Media Campaign

This workflow defines the topological parallel execution steps for social media campaign.

## Steps

### Step 1: draft_post
Execute the draft post phase for the social_media_campaign workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: draft_post_artifacts
### Step 2: format [depends_on: draft_post]
Execute the format phase for the social_media_campaign workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: format_artifacts
### Step 3: schedule [depends_on: format]
Execute the schedule phase for the social_media_campaign workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: schedule_artifacts
### Step 4: monitor_engagement [depends_on: schedule]
Execute the monitor engagement phase for the social_media_campaign workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: monitor_engagement_artifacts
