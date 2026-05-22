---
name: research_discovery_pipeline
description: Search for papers, explore categories, and download relevant publications for offline analysis.
domain: research
tags: ['arxiv', 'papers', 'discovery', 'summarization']
requires: ['scholarx-mcp']
---

# research_discovery_pipeline Workflow

Search for papers, explore categories, and download relevant publications for offline analysis.

### Step 0: scholarx-mcp
List available research paper sources and their categories
Expected: source, categories

### Step 1: scholarx-mcp
Search for recent papers on multi-agent orchestration systems
Expected: paper, agent
Depends On: Step 0

### Step 2: scholarx-mcp
Get details on the most relevant paper from the search results
Expected: abstract, author
Depends On: Step 1
