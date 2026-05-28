---
name: unified-ticket-fetcher
description: >
  Unified Ticket Fetcher atomic skill. Connects to Jira, Plane, and ServiceNow,
  aggregates assigned tickets, and outputs standardized tasks.
domain: ops
license: MIT
tags: [tickets, jira, plane, servicenow, management]
metadata:
  author: Genius
  version: '0.1.0'
requires:
  - unified_task_tracker
---

# Unified Ticket Fetcher Skill

Stateless atomic operation to securely query multiple project management and enterprise ticketing platforms (Jira, Plane, ServiceNow), aggregate assigned work items, resolve credentials gracefully, and produce a single normalized task schema.

## Prerequisites

- `unified_task_tracker` — for orchestrating multi-provider authentication and issuing high-fidelity API requests to ticketing backends.

## Steps

### Step 1: poll_assigned_tickets
Identify and query active ticketing endpoints for the current user session:
- Locate active credentials and connection properties for:
  - **Jira**: Resolve URL, username, and API token.
  - **Plane**: Resolve workspace name, project IDs, and API key.
  - **ServiceNow**: Resolve instance URL, client ID, and credential pairs.
- Execute parallel or sequential queries to each active ticketing platform:
  - Call Jira endpoint (e.g., query `assignee = currentUser() AND statusCategory != Done`).
  - Call Plane endpoint (e.g., retrieve active issues assigned to user profile identifier).
  - Call ServiceNow incident tracker (e.g., retrieve incidents where `assigned_to` matches user ID and state is not resolved/closed).
- Output parameters:
  - `raw_payloads`: Dictionary mapping provider name (`jira`, `plane`, `servicenow`) to lists of raw ticket metadata.

### Step 2: aggregate_ticket_payloads [depends_on: poll_assigned_tickets]
Collate raw records, manage connection failures, and extract core ticket attributes:
- Handle execution faults:
  - If a specific provider API request fails (e.g., due to timeout or bad credentials), capture the exception, register a warning diagnostic, and continue processing other available backends (graceful degradation).
- Consolidate raw ticket listings:
  - Merge the raw JSON arrays into a single in-memory collection.
  - Apply global filter logic to remove completed, archived, or resolved issues.
- Output parameters:
  - `aggregated_list`: Consolidated list of active raw ticket metadata objects.
  - `failed_providers`: List of providers that failed to respond.

### Step 3: normalize_tasks [depends_on: aggregate_ticket_payloads]
Transform heterogeneous ticket schemas into a single, standardized, unified task list:
- Standardize fields into the target schema:
  - `id`: Normalized ticket identifier string (e.g. `JIRA-101`, `PLANE-402`, `SN-INC00123`).
  - `source`: Provider identifier ("jira", "plane", or "servicenow").
  - `title`: Short title or summary string.
  - `description`: Main description body, stripped of platform-specific HTML/formatting where appropriate.
  - `status`: Normalized workflow state ("TODO", "IN_PROGRESS", "BLOCKED").
  - `priority`: Standardized severity level ("LOW", "MEDIUM", "HIGH", "CRITICAL").
  - `due_date`: ISO-8601 due date string (null if unspecified).
  - `created_date`: ISO-8601 creation timestamp.
- Sort and deduplicate:
  - Remove duplicate records if any exist.
  - Sort the task collection by priority descending, then by created_date ascending.
- Output parameters:
  - `status`: "SUCCESS" or "FAILED"
  - `normalized_tasks`: List of standard task objects containing all normalized keys.
  - `task_count`: Total number of active tickets retrieved.
