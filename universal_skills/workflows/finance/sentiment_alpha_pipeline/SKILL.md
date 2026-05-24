---
name: sentiment_alpha_pipeline
description: Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.
domain: finance
tags: [sentiment, crawler, social, nlp]
---
# Sentiment Alpha Pipeline Workflow

This workflow coordinates multi-agent parallel executions of Crawls web news, evaluates social posts sentiment spikes, fuses sentiment signals, and backtests correlation results.

### Step 1: web-news-scraper [depends_on: none]
Scrapes recent news feeds, financial blogs, and academic search articles.
Expected: raw-news-and-publications-logs

### Step 2: social-sentiment-analyzer [depends_on: none]
Monitors social platforms for ticker sentiment spikes.
Expected: raw-social-mentions-counts

### Step 3: signal-score-fuser [depends_on: web-news-scraper, social-sentiment-analyzer]
Combines news and social signals into a unified sentiment score.
Expected: fused-sentiment-signals

### Step 4: backtest-verifier [depends_on: signal-score-fuser]
Tests the sentiment signal returns profile in historical backtests.
Expected: sentiment-backtest-metrics

