---
name: news_event_detector
description: Parallel execution workflow for news event detector using the Unified Parallel Engine
domain: finance
tags:
  - parallel-workflow
  - finance
  - mcp-searxng
---

# Parallel Workflow: News Event Detector

This workflow defines the topological parallel execution steps for news event detector.

## Steps

### Step 1: rss
Execute the RSS phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: rss_artifacts
### Step 2: twitter
Execute the Twitter phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: twitter_artifacts
### Step 3: reddit
Execute the Reddit phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: reddit_artifacts
### Step 4: news_apis
Execute the news APIs phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: news_apis_artifacts
### Step 5: classify [depends_on: rss, twitter, reddit, news_apis]
Execute the classify phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: classify_artifacts
### Step 6: trade_signal [depends_on: classify]
Execute the trade signal phase for the news_event_detector workflow under the finance domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: trade_signal_artifacts
