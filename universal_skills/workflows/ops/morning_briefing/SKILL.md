---
name: morning_briefing
description: Parallel execution workflow for morning briefing using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-nextcloud
---

# Parallel Workflow: Morning Briefing

This workflow defines the topological parallel execution steps for morning briefing.

## Steps

### Step 1: calendar
Execute the calendar phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: calendar_artifacts
### Step 2: weather
Execute the weather phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: weather_artifacts
### Step 3: news
Execute the news phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: news_artifacts
### Step 4: inbox
Execute the inbox phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: inbox_artifacts
### Step 5: tasks
Execute the tasks phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: tasks_artifacts
### Step 6: digest [depends_on: calendar, weather, news, inbox, tasks]
Execute the digest phase for the morning_briefing workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: digest_artifacts
