---
name: media_download_organizer
description: Parallel execution workflow for media download organizer using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-qbittorrent
---

# Parallel Workflow: Media Download Organizer

This workflow defines the topological parallel execution steps for media download organizer.

## Steps

### Step 1: search
Execute the search phase for the media_download_organizer workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: search_artifacts
### Step 2: download [depends_on: search]
Execute the download phase for the media_download_organizer workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: download_artifacts
### Step 3: organize [depends_on: download]
Execute the organize phase for the media_download_organizer workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: organize_artifacts
### Step 4: add_to_library [depends_on: organize]
Execute the add to library phase for the media_download_organizer workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: add_to_library_artifacts
### Step 5: clean_up [depends_on: add_to_library]
Execute the clean up phase for the media_download_organizer workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: clean_up_artifacts
