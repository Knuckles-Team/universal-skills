---
name: google-workspace
description: "Use this skill to interact with the Google Workspace ecosystem, including Gmail, Google Calendar, Google Chat, Google Docs, Google Drive, Google Sheets, and Google Slides. You can search for files, read emails, manage calendar events, send messages, read/write docs and sheets, and interact with slides."
categories: [Productivity]
tags: [google, workspace, gmail, calendar, chat, docs, drive, sheets, slides, api]
---

# Google Workspace

## Overview

This skill consolidates all Google Workspace integrations into a single interface.

## Authentication
Each tool has its own `auth.py` script in its respective subdirectory to handle OAuth authentication for the required scopes. Before using a tool, you may need to run its `auth.py status` to ensure it is authenticated. If not, inform the user they need to run `python scripts/<tool>/auth.py login`.

## Capabilities/Tools

### 1. Gmail (`scripts/gmail/`)
- **Usage**: `python scripts/gmail/gmail.py [command]`
- **Commands**: `search`, `read`, `send`, `reply`, `trash`

### 2. Google Calendar (`scripts/calendar/`)
- **Usage**: `python scripts/calendar/gcal.py [command]`
- **Commands**: `today`, `list`, `search`, `create`, `delete`

### 3. Google Chat (`scripts/chat/`)
- **Usage**: `python scripts/chat/chat.py [command]`
- **Commands**: `list-spaces`, `read-space`, `send-message`, `search`

### 4. Google Docs (`scripts/docs/`)
- **Usage**: `python scripts/docs/docs.py [command]`
- **Commands**: `read`, `create`, `append`, `replace`

### 5. Google Drive (`scripts/drive/`)
- **Usage**: `python scripts/drive/drive.py [command]`
- **Commands**: `search`, `list`, `find-folder`, `download`, `upload`, `create-folder`, `move`, `copy`, `rename`, `trash`

### 6. Google Sheets (`scripts/sheets/`)
- **Usage**: `python scripts/sheets/sheets.py [command]`
- **Commands**: `read`, `read-range`, `list-sheets`, `write`, `append`, `create`, `clear`

### 7. Google Slides (`scripts/slides/`)
- **Usage**: `python scripts/slides/slides.py [command]`
- **Commands**: `read`, `create`, `add-slide`, `add-text`

## Usage Notes
- When working with files (Docs, Sheets, Slides), it's often best to use the **Drive** tool to search for the file and get its `ID` first, then pass that `ID` to the respective tool.
- Always use the absolute path or correct relative path to the scripts (e.g. `scripts/drive/drive.py`).
