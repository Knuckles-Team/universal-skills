---
name: voice_message_transcriber
description: >-
  Detects new local voice notes or audio files, triggers Whisper transcriptions, and prepares structured text outputs for conversational agent consumption.
domain: ops
agent: operations_coordinator
team_config:
  name: operations_team
  task_pattern: operational process coordination
  execution_mode: sequential
  specialist_ids:
    - intake-agent
    - processor-agent
  tool_assignments:
    intake-agent: [graph_query, nc_files]
    processor-agent: [graph_analyze, document_tools]
tags: ['voice', 'audio', 'transcription', 'whisper', 'speech-to-text', 'audio-transcriber-mcp']
concept: CONCEPT:KG-2.12
---

# Voice Message Transcriber Workflow

**CONCEPT:KG-2.12**

Detects new local voice notes or audio files, triggers Whisper transcriptions, and prepares structured text outputs for conversational agent consumption.

## Steps

### Step 0: Audio Transcriber Mcp
**Agent**: `intake-agent`
**Tools**: `graph_query, nc_files`

Transcribe an audio file or capture live microphone input using the transcribe_audio tool.
Expected: `raw_transcript`

### Step 1: User Interaction
**Agent**: `processor-agent`
**Tools**: `graph_analyze, document_tools`

Present the raw transcript to the user. Ask if they want to translate it, format it, or route it directly to another specialist agent for text response.
Expected: `structured_transcript, target_agent`

### Step 2: KG Persistence [depends_on: user-interaction]
**Agent**: `processor-agent`
**Tools**: `graph_write`

Persist workflow results as nodes and edges in the Knowledge Graph.
Create appropriate typed nodes with metadata and link to existing domain entities.

## Output
- Voice Message Transcriber results persisted in KG
- Structured report (MD/PDF)
- Audit trail with timestamps and agent attributions

## Human Oversight Required
✅ Critical decisions require human review and approval.
