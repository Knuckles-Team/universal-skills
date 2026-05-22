---
name: capability_discovery
description: Discovery workflow that probes available capabilities across MCP servers. Tests tool introspection, not execution — useful for building capability maps.
domain: meta
tags: ['discovery', 'capabilities', 'introspection', 'meta']
requires: ['audio-transcriber', 'data-science-mcp', 'scholarx-mcp']
---

# capability_discovery Workflow

Discovery workflow that probes available capabilities across MCP servers. Tests tool introspection, not execution — useful for building capability maps.

### Step 0: audio-transcriber
Describe the capabilities of the transcribe_audio tool
Expected: transcribe, audio

### Step 1: data-science-mcp
Describe the available data science tools and their parameters
Expected: dataset, tool

### Step 2: scholarx-mcp
List available research paper sources
Expected: source
