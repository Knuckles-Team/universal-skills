---
name: qbittorrent_downloads_checker
description: Connects to your qBittorrent server, lists active and completed torrents, and displays a comprehensive download progress dashboard.
domain: infra
tags: ['qbittorrent', 'torrents', 'downloads', 'media', 'qbittorrent-agent']
requires: ['qbittorrent-agent']
---

# qbittorrent_downloads_checker Workflow

Connects to your qBittorrent server, lists active and completed torrents, and displays a comprehensive download progress dashboard.

### Step 0: qbittorrent-agent
Fetch all active and completed torrents, state information, and progress rates using qbittorrent_torrents with the get_torrent_list action.
Expected: active_torrent_list

### Step 1: user-interaction
Present a clear downloading status report, highlighting items that have reached 100% completion or specific seeding ratio goals.
Expected: view_confirmation
Depends On: Step 0
