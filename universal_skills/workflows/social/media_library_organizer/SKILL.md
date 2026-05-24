---
name: media_library_organizer
description: Parallel execution workflow for media library organizer using the Unified Parallel Engine
domain: research
tags:
  - parallel-workflow
  - research
  - mcp-jellyfin
---

# Parallel Workflow: Media Library Organizer

This workflow defines the topological parallel execution steps for media library organizer.

## Steps

### Step 1: scan_library
Execute the scan library phase for the media_library_organizer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scan_library_artifacts
### Step 2: metadata_extraction [depends_on: scan_library]
Execute the metadata extraction phase for the media_library_organizer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: metadata_extraction_artifacts
### Step 3: categorize [depends_on: metadata_extraction]
Execute the categorize phase for the media_library_organizer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: categorize_artifacts
### Step 4: dedupe [depends_on: categorize]
Execute the dedupe phase for the media_library_organizer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: dedupe_artifacts
### Step 5: report [depends_on: dedupe]
Execute the report phase for the media_library_organizer workflow under the research domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: report_artifacts
