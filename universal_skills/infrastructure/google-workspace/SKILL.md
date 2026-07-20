---
name: google-workspace
skill_type: skill
description: >-
  Interact with Gmail, Google Calendar, Google Chat, Google Docs, Google Drive,
  Google Sheets, and Google Slides. Use for searching or managing Workspace
  content, messages, files, events, documents, spreadsheets, or presentations.
---
# Google Workspace

## Overview

This skill consolidates all Google Workspace integrations into a single interface.

## Authentication

Configure `GOOGLE_WORKSPACE_OAUTH_CLIENT_ID` and
`GOOGLE_WORKSPACE_OAUTH_BROKER_URL` through AgentConfig or the process
environment. The broker must use HTTPS and must not contain embedded
credentials, a query, or a fragment. Keep its client secret in the broker's
secret manager; never place it in this skill or a generated config.

Each service has a scoped `auth.py` helper. Run
`python scripts/<service>/auth.py status`, then `login` when needed. Tokens are
stored only in the system keyring. The `token` command reports availability and
never prints token material. Never copy authorization URLs, OAuth state, or
tokens into logs, traces, reports, or chat.

Outbound API calls are restricted to the exact Google service hosts, reject
redirects and ambient proxies, use finite timeouts and bounded responses, and
verify TLS. For a managed trust chain, configure `SSL_CERT_FILE`, `SSL_CERT_DIR`,
or `REQUESTS_CA_BUNDLE` at runtime; the skill never persists those paths or the
certificate material. File and attachment uploads are limited to 32 MiB.

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
- Resolve scripts relative to this skill root; do not persist machine-specific absolute paths.
