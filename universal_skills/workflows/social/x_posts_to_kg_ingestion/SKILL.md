---
name: x_posts_to_kg_ingestion
description: Searches X (formerly Twitter) posts for a given query (e.g. model launches, framework updates, or tech trends) and ingests the post content, author metadata, and engagement statistics directly into the Knowledge Graph as TweetNode entries with relevant concept relationships.
domain: social
tags: ['social', 'x', 'ingestion', 'graph-os']
requires: ['graph-os']
---

# x_posts_to_kg_ingestion Workflow

Searches X (formerly Twitter) posts for a given query (e.g. model launches, framework updates, or tech trends) and ingests the post content, author metadata, and engagement statistics directly into the Knowledge Graph as TweetNode entries with relevant concept relationships.

### Step 0: x-search-agent
Search X (formerly Twitter) using x_search, or browse a specific X post status URL using browse_x_post. Target/Query: {{task}} Retrieve the text, author metadata, and engagement statistics.
Expected: posts, authors, content

### Step 1: graph-os
Write Cypher queries using kg_write to ingest each search result as a TweetNode containing the status ID, text content, author handle, and engagement metrics into the Knowledge Graph.
Expected: cypher, ingest
Depends On: Step 0
