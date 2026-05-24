---
name: overnight_research_loop
description: Runs overnight crawling of news/publications to generate factor hypotheses, runs backtests in parallel, debates findings, and generates a morning briefing.
domain: finance
tags: [overnight, research, backtest, factor]
---
# Overnight Research Loop Workflow

This workflow coordinates multi-agent parallel executions of Runs overnight crawling of news/publications to generate factor hypotheses, runs backtests in parallel, debates findings, and generates a morning briefing.

### Step 1: hypothesis-crawlers [depends_on: none]
Scans academic publications, social feeds, and market tickers overnight to find potential factor ideas.
Expected: factor-hypothesis-list

### Step 2: parallel-backtester [depends_on: hypothesis-crawlers]
Runs backtests concurrently across 50 parameter configurations.
Expected: multi-config-backtest-results

### Step 3: factor-debater [depends_on: parallel-backtester]
Analyzes return profile, drawdown, and transaction cost impact in a swarm debate.
Expected: approved-factor-signals

### Step 4: report-compiler [depends_on: factor-debater]
Compiles findings into a formatted dashboard report for the morning review.
Expected: morning-research-tearsheet

