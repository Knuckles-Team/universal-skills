---
name: qbittorrent_download_adder
description: Prompts the user for a torrent/magnet download link and custom save parameters, then schedules and starts the download on qBittorrent.
domain: infra
tags: ['qbittorrent', 'torrents', 'adder', 'downloads', 'qbittorrent-agent']
requires: ['qbittorrent-agent']
---

# qbittorrent_download_adder Workflow

Prompts the user for a torrent/magnet download link and custom save parameters, then schedules and starts the download on qBittorrent.

### Step 0: user-interaction
Prompt the user for the magnet link, torrent URL, custom save path category, and queue priorities.
Expected: download_link, save_category, start_immediately

### Step 1: qbittorrent-agent
Schedule the new download by calling qbittorrent_torrents with the add_new_torrent action, passing the target link and parameters.
Expected: addition_result
Depends On: Step 0
