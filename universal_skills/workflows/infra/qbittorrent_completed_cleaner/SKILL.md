---
name: qbittorrent_completed_cleaner
description: Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).
domain: infra
tags: ['qbittorrent', 'torrents', 'cleaner', 'pruning', 'qbittorrent-agent']
requires: ['qbittorrent-agent']
---

# qbittorrent_completed_cleaner Workflow

Discovers completed downloads, prompts the user to select torrents to remove, and securely prunes the active dashboard list (optionally deleting files).

### Step 0: qbittorrent-agent
Fetch all completed torrents that are currently seeding or finished downloading using qbittorrent_torrents with the get_torrent_list action.
Expected: completed_torrent_list

### Step 1: user-interaction
Display completed torrents. Prompt the user to select which completed items should be deleted, and confirm if actual data files should also be erased.
Expected: selected_hashes, delete_files_flag
Depends On: Step 0

### Step 2: qbittorrent-agent
Remove the chosen torrents using qbittorrent_torrents with the delete_torrents action, passing the target hashes and deletion options.
Expected: pruning_results
Depends On: Step 1
