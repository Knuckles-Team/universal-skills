---
name: adguard_stats_collector
description: Queries metrics and stats from AdGuard Home, parses recent query log entries using adguard-home-agent, and compiles a comprehensive DNS traffic, health, and block-rate dashboard report.
domain: infra
tags: ['adguard', 'metrics', 'stats', 'query-log', 'adguard-home-agent']
requires: ['adguard-home-agent']
---

# adguard_stats_collector Workflow

Queries metrics and stats from AdGuard Home, parses recent query log entries using adguard-home-agent, and compiles a comprehensive DNS traffic, health, and block-rate dashboard report.

### Step 0: adguard-home-agent
Fetch DNS statistics metrics using adguard_home_stats get_stats tool. Retrieve recent dns query log events using adguard_home_query_log get_query_log tool.
Expected: stats_metrics, query_logs

### Step 1: user-interaction
Analyze retrieved metrics and query entries. Compile a premium, formatted DNS traffic dashboard summarizing total queries, blocked trackers percentage, top queried domains, and local network client traffic stats.
Expected: dns_health_report
Depends On: Step 0
