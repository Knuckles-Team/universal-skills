---
name: postiz_scheduler
description: Automatically lists active social integrations, discovers slot availabilities, prompts the user for text/media content, and schedules posts via the Postiz MCP server.
domain: ops
tags: ['postiz', 'social-media', 'marketing', 'scheduling', 'postiz-agent']
requires: ['postiz-agent']
---

# postiz_scheduler Workflow

Automatically lists active social integrations, discovers slot availabilities, prompts the user for text/media content, and schedules posts via the Postiz MCP server.

### Step 0: postiz-agent
Retrieve active integration accounts and check for slot time recommendations using postiz_integrations with list_integrations or check_connection actions.
Expected: active_integrations, recommended_slots

### Step 1: user-interaction
Present active channels and slot suggestions. Prompt the user for post body text, image/video attachment URLs, and schedule parameters.
Expected: post_content, file_url, release_time
Depends On: Step 0

### Step 2: postiz-agent
Create and schedule the post (uploading the file attachment if provided) using the postiz_posts and postiz_uploads tools.
Expected: post_creation_result
Depends On: Step 1
