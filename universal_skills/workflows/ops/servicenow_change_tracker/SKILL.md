---
name: servicenow_change_tracker
description: Fetch active ServiceNow Change Requests sorted chronologically
tags:
  - ops
  - servicenow
  - change-management
requires:
  - servicenow-api
---

# ServiceNow Change Tracker Workflow

Retrieve and schedule reviews for the latest active Change Requests (CHGs) across ITIL environment pipelines.

## Steps

### Step 0: servicenow-api
Retrieve a list of active change requests using the `servicenow_change_management` action with `action='get_change_requests'`. Specify a chronological descending query via `params_json` (e.g. `{"sysparm_query": "active=true^ORDERBYdescsys_created_on"}`).

### Step 1: user-interaction
Display the chronological change log and scheduled maintenance windows to the user. Ask if they wish to inspect a specific change ticket or analyze scheduling conflicts.

### Step 2: servicenow-api
Retrieve comprehensive details for the selected change request ID using `servicenow_change_management` with `action='get_change_request'` and `action='get_change_request_conflict'` to detect environmental schedule clashes.

### Step 3: user-interaction
Present the detailed change payload, risk factors, conflict scan report, and approval paths to the user.
