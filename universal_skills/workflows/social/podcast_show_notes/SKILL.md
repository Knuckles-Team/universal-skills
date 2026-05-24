---
name: podcast_show_notes
description: Parallel execution workflow for podcast show notes using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-audio-transcriber
---

# Parallel Workflow: Podcast Show Notes

This workflow defines the topological parallel execution steps for podcast show notes.

## Steps

### Step 1: transcribe
Execute the transcribe phase for the podcast_show_notes workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: transcribe_artifacts
### Step 2: summarize [depends_on: transcribe]
Execute the summarize phase for the podcast_show_notes workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: summarize_artifacts
### Step 3: extract_topics [depends_on: summarize]
Execute the extract topics phase for the podcast_show_notes workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: extract_topics_artifacts
### Step 4: generate_notes [depends_on: extract_topics]
Execute the generate notes phase for the podcast_show_notes workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_notes_artifacts
### Step 5: publish [depends_on: generate_notes]
Execute the publish phase for the podcast_show_notes workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: publish_artifacts
