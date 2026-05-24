---
name: servicenow_incident_tracker
description: Fetch active ServiceNow incidents ordered with higher priority showing first
tags:
  - ops
  - servicenow
  - incidents
requires:
  - servicenow-api
---

# ServiceNow Incident Tracker Workflow

Retrieve and display active ITIL incidents sorted with highest priority (Critical/High) at the top of the queue.

## Steps

### Step 0: servicenow-api
Retrieve the list of active incidents using the `servicenow_incidents` action with `action='get_incidents'`. Pass `params_json` containing a query like `{"sysparm_query": "active=true^ORDERBYpriority"}` to ensure critical priority incidents appear first.

### Step 1: user-interaction
Present the list of prioritized incidents to the user. Request selection of a specific incident for deeper inspection or action.

### Step 2: servicenow-api
Fetch full details for the selected incident ID using the `servicenow_incidents` action with `action='get_incident'` and the incident's sys_id.

### Step 3: user-interaction
Display the comprehensive incident history, comments, SLA status, and proposed remediation plan to the user.
