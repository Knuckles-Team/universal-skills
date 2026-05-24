---
name: nextcloud_time_manager
description: Connects to Nextcloud using nextcloud-agent, retrieves latest calendar events and task files, interacts with the user to discover scheduling modifications, and applies updates/adds/removes to synchronize their personal schedule.
domain: ops
tags: ['nextcloud', 'calendar', 'tasks', 'personal-assistant', 'nextcloud-agent']
requires: ['nextcloud-agent']
---

# nextcloud_time_manager Workflow

Connects to Nextcloud using nextcloud-agent, retrieves latest calendar events and task files, interacts with the user to discover scheduling modifications, and applies updates/adds/removes to synchronize their personal schedule.

### Step 0: nextcloud-agent
Retrieve current calendar lists and schedule events using nextcloud_calendar list_calendars and list_calendar_events tools. Fetch active tasks using nextcloud_files list_files in the task directory.
Expected: calendars, events, tasks

### Step 1: user-interaction
Analyze the retrieved calendar events and tasks. Present a summary of the current schedule to the user, and prompt them to specify any new events/tasks to add, modify, or remove.
Expected: user_schedule_instructions

### Step 2: nextcloud-agent
Apply requested scheduling modifications to Nextcloud. Call nextcloud_calendar create_calendar_event to register new events, or call nextcloud_files tools to write/update/delete task records as instructed.
Expected: nextcloud_sync_results
Depends On: Step 1
