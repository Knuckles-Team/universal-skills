---
name: blog_post_generator
description: Parallel execution workflow for blog post generator using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-searxng
---

# Parallel Workflow: Blog Post Generator

This workflow defines the topological parallel execution steps for blog post generator.

## Steps

### Step 1: research_topic
Execute the research topic phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: research_topic_artifacts
### Step 2: outline [depends_on: research_topic]
Execute the outline phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: outline_artifacts
### Step 3: draft [depends_on: outline]
Execute the draft phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: draft_artifacts
### Step 4: edit [depends_on: draft]
Execute the edit phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: edit_artifacts
### Step 5: seo_optimize [depends_on: edit]
Execute the SEO optimize phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: seo_optimize_artifacts
### Step 6: publish [depends_on: seo_optimize]
Execute the publish phase for the blog_post_generator workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
