---
name: voice_message_transcriber
description: Detects new local voice notes or audio files, triggers Whisper transcriptions, and prepares structured text outputs for conversational agent consumption.
domain: ops
tags: ['voice', 'audio', 'transcription', 'whisper', 'speech-to-text', 'audio-transcriber-mcp']
requires: ['audio-transcriber-mcp']
---

# voice_message_transcriber Workflow

Detects new local voice notes or audio files, triggers Whisper transcriptions, and prepares structured text outputs for conversational agent consumption.

### Step 0: audio-transcriber-mcp
Transcribe an audio file or capture live microphone input using the transcribe_audio tool.
Expected: raw_transcript

### Step 1: user-interaction
Present the raw transcript to the user. Ask if they want to translate it, format it, or route it directly to another specialist agent for text response.
Expected: structured_transcript, target_agent
Depends On: Step 0
