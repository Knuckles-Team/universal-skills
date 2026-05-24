---
name: servicenow_trm_tracker
description: Fetch active ServiceNow TRM (Technology Reference Model) Requests
tags:
  - ops
  - servicenow
  - trm-requests
requires:
  - servicenow-api
---

# ServiceNow TRM Requests Tracker Workflow

Retrieve and track active Technology Reference Model (TRM) evaluation requests using the ServiceNow Table API or portfolio systems.

## Steps

### Step 0: servicenow-api
Query the ServiceNow TRM requests table (typically `u_trm_request` or relevant `dmn_demand` table) using the `servicenow_table_api` action with `action='get_table'`. Order by creation date descending via `params_json` containing a query like `{"sysparm_query": "active=true^ORDERBYdescsys_created_on", "sysparm_limit": 20}`.

### Step 1: user-interaction
Present the latest TRM compliance evaluation queue to the user. Prompt them to select a request for deep tech stack compliance analysis.

### Step 2: servicenow-api
Fetch full fields and developer requirements for the selected TRM record using `servicenow_table_api` with `action='get_table_record'`.

### Step 3: user-interaction
Display the architecture evaluation logs, software categories status, and next assessment workflow steps to the user.
