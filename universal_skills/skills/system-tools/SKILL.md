---
name: system-tools
description: "Hardware and OS-level operations including capturing screenshots, webcam photos, Bluetooth management, and remote-controlling tmux sessions."
categories: [System & Infrastructure]
tags: [os, hardware, screenshot, webcam, bluetooth, tmux, system]
---

# System Tools

## Overview

This skill combines various low-level operating system and hardware interaction tools.

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
