---
name: system-tools
domain: system
skill_type: skill
description: >-
  Hardware and OS-level operations including capturing screenshots, webcam photos,
  Bluetooth management, and remote-controlling tmux sessions.
license: MIT
tags: [os, hardware, screenshot, webcam, bluetooth, tmux, system]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# System Tools

## Overview

This skill combines various low-level operating system and hardware interaction tools.

## Steps

1. Pick the capability (tmux, screenshot, webcam or Bluetooth) and confirm its script exists with `ls scripts/`. Verify that the named script is listed, such as `find-sessions.sh`, `wait-for-text.sh` or `take_screenshot.py`.
2. For tmux, list sessions with `scripts/find-sessions.sh -q <name>`. Verify that the target session appears in the output before sending keystrokes.
3. Wait for output instead of sleeping with `scripts/wait-for-text.sh -t <session:window.pane> -p '<pattern>' -T 30`. Verify that the script exits 0 on a match.
4. For a screenshot, run `python3 scripts/take_screenshot.py --path /var/tmp/shot.png --mode temp`. Verify with `ls -l /var/tmp/shot.png` that a non-empty PNG was written.
5. Inspect the result with `tmux capture-pane -p -t <session:window.pane>` for a session, or open the saved PNG for a screenshot. Verify that you read that output before claiming a GUI or session state.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `find-sessions.sh` lists nothing | Wrong tmux socket | Pass `-L <socket-name>` or `-S <socket-path>`, or scan with `-A` |
| `wait-for-text.sh` times out | Pattern never appeared in the pane history | Raise `-T`, widen `-l`, or use `-F` for a literal string, after checking the pane text |
| Screenshot is blank or fails on Linux | No display or screenshot tool available | Run it inside a graphical session, or use the platform script (`take_screenshot.ps1` on Windows) |
| macOS capture is denied | Screen recording permission missing | Run `scripts/ensure_macos_permissions.sh` and grant access in system settings |

## Capabilities/Tools

### 1. Tmux Controller (`scripts/tmux.py` or `scripts/tmux.sh`)
Remote-control tmux sessions for interacting with interactive TUIs/CLIs. You can send keystrokes and scrape pane outputs without attaching to the session directly.
- Useful when you need to let a blocking process run in the background while still observing its output.

### 2. Screenshot Utilities
Capture full screen, specific windows, or regions.
- Excellent for visual confirmation of GUI states or debugging headless browser issues when standard Playwright screenshots fail.

### 3. Webcam Snapshot (`scripts/camsnap.sh` or `scripts/camsnap.py`)
Take quick snapshots from connected webcams (video0, etc.) for visual validation of physical environments where required.

### 4. Bluetooth Manager (`scripts/blucli.py` or `scripts/blucli.sh`)
CLI interfaces to pair, connect, and debug Bluetooth peripherals securely.
