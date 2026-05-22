---
name: observability_and_research
description: Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.
domain: research
tags: ['observability', 'research', 'langfuse', 'cross-domain']
requires: ['langfuse-mcp', 'scholarx-mcp']
---

# observability_and_research Workflow

Combined observability check with research discovery. Validates Langfuse is healthy while concurrently searching for papers on agent observability.

### Step 0: langfuse-mcp
Check Langfuse health, list all score configs, and list all datasets
Expected: health, score, dataset

### Step 1: scholarx-mcp
Search for recent papers on LLM observability and agent tracing
Expected: paper, observability

### Step 2: langfuse-mcp
List all current projects in the Langfuse instance
Expected: project
Depends On: Step 0
