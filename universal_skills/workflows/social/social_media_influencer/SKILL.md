---
name: social_media_influencer
description: Prepares a live stream broadcast title, updates style details, announces the live stream, and engages the audience using owncast-agent tools.
domain: social
tags: ['social', 'streaming', 'broadcast', 'owncast-agent']
requires: ['owncast-agent']
---

# social_media_influencer Workflow

Prepares a live stream broadcast title, updates style details, announces the live stream, and engages the audience using owncast-agent tools.

### Step 0: social-media-influencer
Update the live stream broadcast title, welcome message text, and style customization details using the owncast_objects and owncast_internal tools.
Expected: stream_status, metadata

### Step 1: owncast-agent
Announce stream live status to connected social networks. Trigger an initial welcome notification message in the live stream chat using owncast_external and owncast_chat tools.
Expected: system_chat_post, notification
Depends On: Step 0
