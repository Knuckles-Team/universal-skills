---
name: adguard_dns_orchestrator
description: Interacts with AdGuard Home using adguard-home-agent to list existing DNS rewrites, request user specifications for new rules, and dynamically add or update DNS rewrite records.
domain: infra
tags: ['adguard', 'dns', 'dns-rewrites', 'network', 'adguard-home-agent']
requires: ['adguard-home-agent']
---

# adguard_dns_orchestrator Workflow

Interacts with AdGuard Home using adguard-home-agent to list existing DNS rewrites, request user specifications for new rules, and dynamically add or update DNS rewrite records.

### Step 0: adguard-home-agent
Retrieve current DNS rewrite mapping records using adguard_home_rewrites list_rewrites tool.
Expected: rewrite_records

### Step 1: user-interaction
Present a summary of current DNS rewrite rules to the user. Prompt the user to input the target domain name and mapping answer IP they want to register or modify.
Expected: rewrite_instructions

### Step 2: adguard-home-agent
Apply requested rewrite rules to AdGuard Home. If rule already exists, update it by deleting the existing rule using delete_rewrite and adding the new mapping via add_rewrite tool.
Expected: adguard_sync_status
Depends On: Step 1
