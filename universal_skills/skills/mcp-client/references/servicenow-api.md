# ServiceNow MCP Reference

**Project:** `servicenow-api`
**Entrypoint:** `servicenow-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SERVICENOW_INSTANCE` | Required for authentication |
| `SERVICENOW_USERNAME` | Required for authentication |
| `SERVICENOW_PASSWORD` | Required for authentication |

## Available Tool Tags (30)

| Env Variable | Default |
|-------------|----------|
| `ACCOUNTTOOL` | `True` |
| `ACTIVITY_SUBSCRIPTIONSTOOL` | `True` |
| `AGGREGATETOOL` | `True` |
| `APPLICATIONTOOL` | `True` |
| `ATTACHMENTTOOL` | `True` |
| `AUTHTOOL` | `True` |
| `BATCHTOOL` | `True` |
| `CHANGE_MANAGEMENTTOOL` | `True` |
| `CICDTOOL` | `True` |
| `CILIFECYCLETOOL` | `True` |
| `CMDBTOOL` | `True` |
| `CUSTOM_APITOOL` | `True` |
| `DATA_CLASSIFICATIONTOOL` | `True` |
| `DEVOPSTOOL` | `True` |
| `EMAILTOOL` | `True` |
| `FLOWSTOOL` | `True` |
| `HRTOOL` | `True` |
| `IMPORT_SETSTOOL` | `True` |
| `INCIDENTSTOOL` | `True` |
| `KNOWLEDGE_MANAGEMENTTOOL` | `True` |
| `METRICBASETOOL` | `True` |
| `MISCTOOL` | `True` |
| `PLUGINSTOOL` | `True` |
| `PPMTOOL` | `True` |
| `PRODUCT_INVENTORYTOOL` | `True` |
| `SERVICE_QUALIFICATIONTOOL` | `True` |
| `SOURCE_CONTROLTOOL` | `True` |
| `TABLE_APITOOL` | `True` |
| `TESTINGTOOL` | `True` |
| `UPDATE_SETSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "command": "servicenow-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "SERVICENOW_INSTANCE": "${SERVICENOW_INSTANCE}",
        "SERVICENOW_USERNAME": "${SERVICENOW_USERNAME}",
        "SERVICENOW_PASSWORD": "${SERVICENOW_PASSWORD}",
        "ACCOUNTTOOL": "True",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "True",
        "AGGREGATETOOL": "True",
        "APPLICATIONTOOL": "True",
        "ATTACHMENTTOOL": "True",
        "AUTHTOOL": "True",
        "BATCHTOOL": "True",
        "CHANGE_MANAGEMENTTOOL": "True",
        "CICDTOOL": "True",
        "CILIFECYCLETOOL": "True",
        "CMDBTOOL": "True",
        "CUSTOM_APITOOL": "True",
        "DATA_CLASSIFICATIONTOOL": "True",
        "DEVOPSTOOL": "True",
        "EMAILTOOL": "True",
        "FLOWSTOOL": "True",
        "HRTOOL": "True",
        "IMPORT_SETSTOOL": "True",
        "INCIDENTSTOOL": "True",
        "KNOWLEDGE_MANAGEMENTTOOL": "True",
        "METRICBASETOOL": "True",
        "MISCTOOL": "True",
        "PLUGINSTOOL": "True",
        "PPMTOOL": "True",
        "PRODUCT_INVENTORYTOOL": "True",
        "SERVICE_QUALIFICATIONTOOL": "True",
        "SOURCE_CONTROLTOOL": "True",
        "TABLE_APITOOL": "True",
        "TESTINGTOOL": "True",
        "UPDATE_SETSTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "url": "http://servicenow-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `ACCOUNTTOOL` and disable all others:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "command": "servicenow-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "SERVICENOW_INSTANCE": "${SERVICENOW_INSTANCE}",
        "SERVICENOW_USERNAME": "${SERVICENOW_USERNAME}",
        "SERVICENOW_PASSWORD": "${SERVICENOW_PASSWORD}",
        "ACCOUNTTOOL": "True",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "False",
        "AGGREGATETOOL": "False",
        "APPLICATIONTOOL": "False",
        "ATTACHMENTTOOL": "False",
        "AUTHTOOL": "False",
        "BATCHTOOL": "False",
        "CHANGE_MANAGEMENTTOOL": "False",
        "CICDTOOL": "False",
        "CILIFECYCLETOOL": "False",
        "CMDBTOOL": "False",
        "CUSTOM_APITOOL": "False",
        "DATA_CLASSIFICATIONTOOL": "False",
        "DEVOPSTOOL": "False",
        "EMAILTOOL": "False",
        "FLOWSTOOL": "False",
        "HRTOOL": "False",
        "IMPORT_SETSTOOL": "False",
        "INCIDENTSTOOL": "False",
        "KNOWLEDGE_MANAGEMENTTOOL": "False",
        "METRICBASETOOL": "False",
        "MISCTOOL": "False",
        "PLUGINSTOOL": "False",
        "PPMTOOL": "False",
        "PRODUCT_INVENTORYTOOL": "False",
        "SERVICE_QUALIFICATIONTOOL": "False",
        "SOURCE_CONTROLTOOL": "False",
        "TABLE_APITOOL": "False",
        "TESTINGTOOL": "False",
        "UPDATE_SETSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/servicenow-api.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command servicenow-mcp \
    --enable-tag ACCOUNTTOOL \
    --all-tags "ACCOUNTTOOL,ACTIVITY_SUBSCRIPTIONSTOOL,AGGREGATETOOL,APPLICATIONTOOL,ATTACHMENTTOOL,AUTHTOOL,BATCHTOOL,CHANGE_MANAGEMENTTOOL,CICDTOOL,CILIFECYCLETOOL,CMDBTOOL,CUSTOM_APITOOL,DATA_CLASSIFICATIONTOOL,DEVOPSTOOL,EMAILTOOL,FLOWSTOOL,HRTOOL,IMPORT_SETSTOOL,INCIDENTSTOOL,KNOWLEDGE_MANAGEMENTTOOL,METRICBASETOOL,MISCTOOL,PLUGINSTOOL,PPMTOOL,PRODUCT_INVENTORYTOOL,SERVICE_QUALIFICATIONTOOL,SOURCE_CONTROLTOOL,TABLE_APITOOL,TESTINGTOOL,UPDATE_SETSTOOL"
```

## Tailored Skills Reference

### servicenow-account

**Description:** Capabilities for managing CSM Accounts in ServiceNow.

## ServiceNow Account

This skill allows the agent to retrieve Customer Service Management (CSM) Account information.

### Tools

#### `get_account`

- **Description**: Retrieves CSM account information.
- **Parameters**:
    - `sys_id` (Optional[str]): Account Sys ID.
    - `name` (Optional[str]): Account name.
    - `number` (Optional[str]): Account number.

### Usage

#### Getting Account by Name

```python
result = get_account(name="Acme Corp")
```

### servicenow-activity-subscriptions

**Description:** Capabilities for managing activity subscriptions in ServiceNow.

## ServiceNow Activity Subscriptions

This skill allows the agent to retrieve activity subscriptions for records.

### Tools

#### `get_activity_subscriptions`

- **Description**: Retrieves activity subscriptions.
- **Parameters**:
    - `sys_id` (Optional[str]): Activity Subscription Sys ID.

### Usage

#### Getting All Activity Subscriptions

```python
result = get_activity_subscriptions()
```

### servicenow-aggregate

**Description:** Capabilities for computing aggregate statistics on ServiceNow tables.

## ServiceNow Aggregate

This skill allows the agent to compute aggregate statistics (counts, min, max, etc.) on ServiceNow tables.

### Tools

#### `get_stats`

- **Description**: Retrieves aggregate statistics for a table.
- **Parameters**:
    - `table_name` (str): Table name to aggregate on.
    - `query` (Optional[str]): Encoded query string.
    - `groupby` (Optional[str]): Field to group by.
    - `stats` (Optional[str]): Statistics function.

### Usage

#### Getting Incident Counts Grouped by Priority

```python
result = get_stats(
    table_name="incident",
    groupby="priority",
    stats="count"
)
```

### servicenow-application

**Description:** Manages ServiceNow applications. Use for retrieving application details. Triggers - app info, sys_id queries.

#### Overview
Handles application records via MCP.

#### Key Tools
- `get_application`: Get app by ID. Params: application_id (required).

#### Usage Instructions
1. Use application_id (sys_id).
2. Call for single apps.

#### Examples
- Get app: `get_application` with application_id="abc123".

#### Error Handling
- 404: Invalid ID—verify sys_id.

### servicenow-attachment

**Description:** Capabilities for managing attachments in ServiceNow.

## ServiceNow Attachment

This skill allows the agent to upload, retrieve, and delete attachments in ServiceNow.

### Tools

#### `get_attachment`

- **Description**: Retrieves attachment metadata.
- **Parameters**:
    - `sys_id` (str): Attachment Sys ID.

#### `upload_attachment`

- **Description**: Uploads an attachment to a record.
- **Parameters**:
    - `file_path` (str): Absolute path to the file to upload.
    - `table_name` (str): Table name associated with the attachment.
    - `table_sys_id` (str): Sys ID of the record in the table.
    - `file_name` (str): Name of the file.
    - `content_type` (Optional[str]): MIME type of the file.

#### `delete_attachment`

- **Description**: Deletes an attachment.
- **Parameters**:
    - `sys_id` (str): Attachment Sys ID.

### Usage

#### Uploading an Attachment

```python
result = upload_attachment(
    file_path="/path/to/file.txt",
    table_name="incident",
    table_sys_id="sys_id_of_incident",
    file_name="file.txt"
)
```

### servicenow-auth

**Description:** Manages ServiceNow auth. Use for token refresh. Triggers - sessions, auth issues.

#### Overview
Auth utils via MCP.

#### Key Tools
- `refresh_auth_token`.

#### Usage Instructions
1. Call when token expires.

#### Examples
- Refresh: `refresh_auth_token`.

#### Error Handling
- Invalid creds: Re-auth.

### servicenow-batch

**Description:** Manages batch requests in ServiceNow. Use for sending multiple REST API requests in a single call.

#### Overview
Handles batch processing of REST API requests via MCP.

#### Key Tools
- `batch_request`: Sends multiple REST API requests in a single call. Params: batch_request_id (optional), rest_requests (required list).

#### Usage Instructions
1. Construct a list of `BatchRequestItem` objects (method, url, body, etc.).
2. Call `batch_request` with the list.

#### Examples
- Batch request: `batch_request` with rest_requests=[{"method": "GET", "url": "/api/now/table/incident"}]

#### Error Handling
- 400: Invalid parameters or request structure.

### servicenow-change-management

**Description:** "Manages ServiceNow Change Requests (CRs). Use this skill to create, read, update, and delete CRs, tasks, and models, and to manage conflicts, schedules, and approvals."

#### Overview
This skill provides comprehensive access to the ServiceNow Change Management API via MCP tools. You can manage the entire lifecycle of a change request, from creation (Standard, Normal, Emergency) to closure, including task management and conflict detection.

#### Tool Usage Reference

##### 1. Retrieval
- **`get_change_requests`**: Search for CRs.
    - `change_type` (str): 'emergency', 'normal', 'standard', 'model'.
    - `sysparm_query` (str): Encoded query string (e.g., `active=true^ORDERBYnumber`).
    - `sysparm_limit` (int): Max records (default 5).
    - `sysparm_offset` (int): Pagination offset.
    - `name_value_pairs` (str): Key-value pairs for equality matching.
    - `text_search` (str): Free text search.
- **`get_change_request`**: Get a single CR.
    - `change_request_sys_id` (str): The CR sys_id.
    - `change_type` (str, optional): 'emergency', 'normal', 'standard'.
- **`get_change_request_tasks`**: Get tasks for a CR.
    - `change_request_sys_id` (str): Target CR sys_id.
    - `sysparm_query`, `sysparm_limit`, `order`, etc.
- **`get_change_request_ci`**: Get CIs associated with a CR.
    - `change_request_sys_id` (str): Target CR sys_id.
- **`get_change_request_schedule`**: Get schedule for a CI.
    - `cmdb_ci_sys_id` (str): Config Item sys_id.
- **`get_change_request_nextstate`**: detailed state transition info.
    - `change_request_sys_id` (str).
- **`get_change_request_worker`**: Get worker details.
    - `worker_sys_id` (str).

##### 2. Templates & Models
- **`get_standard_change_request_templates`**: List standard change templates.
    - `name_value_pairs`, `sysparm_query`, `text_search`.
- **`get_standard_change_request_template`**: Get specific template.
    - `template_sys_id` (str).
- **`get_change_request_models`**: List change models.
    - `change_type` (str), `sysparm_query`, etc.
- **`get_standard_change_request_model`**: Get specific model.
    - `model_sys_id` (str).
- **`calculate_standard_change_request_risk`**: Risk assessment.
    - `change_request_sys_id` (str): **Standard** CR sys_id only.

##### 3. Creation
- **`create_change_request`**: Create a new CR.
    - `change_type` (str): Default 'normal'. Use 'standard' or 'emergency' as needed.
    - `name_value_pairs` (str): JSON-like string or dict str of fields (e.g., `{"short_description": "Fix DB", "cmdb_ci": "..."}`).
    - `standard_change_template_id` (str): Required if `change_type` is 'standard'.
- **`create_change_request_task`**: Add a task to a CR.
    - `change_request_sys_id` (str).
    - `data` (dict): Fields for the task (e.g., `{"short_description": "Deploy code"}`).
- **`create_change_request_ci_association`**: Associate CIs (Affected/Impacted).
    - `change_request_sys_id` (str).
    - `cmdb_ci_sys_ids` (List[str]): List of CI sys_ids.
    - `association_type` (str): 'affected', 'impacted', 'offering'.
    - `refresh_impacted_services` (bool): Optional refresh trigger.

##### 4. Modification
- **`update_change_request`**: Update CR fields.
    - `change_request_sys_id` (str).
    - `name_value_pairs` (str): Fields to update.
    - `change_type` (str): If changing type.
- **`update_change_request_task`**: Update a task.
    - `change_request_sys_id` (str).
    - `change_request_task_sys_id` (str).
    - `name_value_pairs` (str).
- **`approve_change_request`**: Approve/Reject.
    - `change_request_sys_id` (str).
    - `state` (str): 'approved' or 'rejected'.
- **`update_change_request_first_available`**: Move to next state.
    - `change_request_sys_id` (str).

##### 5. Conflict Management
- **`check_change_request_conflict`**: Run conflict detection.
    - `change_request_sys_id` (str).
- **`get_change_request_conflict`**: detailed conflict info.
    - `change_request_sys_id` (str).
- **`delete_change_request_conflict_scan`**: Cancel/Delete scan.
    - `change_request_sys_id` (str).
    - `task_sys_id` (str): Task ID associated with conflict (if required by tool definition).

##### 6. Deletion
- **`delete_change_request`**: Delete a CR.
    - `change_request_sys_id` (str).
    - `change_type` (str).
- **`delete_change_request_task`**: Delete a creation task.
    - `change_request_sys_id` (str).
    - `task_sys_id` (str).

#### Important Notes
- **Name-Value Pairs**: When providing `name_value_pairs`, ensure you use valid field names (e.g., `short_description`, `assignment_group`, `start_date`).
- **Standard Changes**: Always require `standard_change_template_id`.
- **Dates**: Use UTC strings (e.g., "2023-10-01 12:00:00").

#### Examples

**Search for Open Normal Changes**:
```python
get_change_requests(
    change_type="normal",
    sysparm_query="active=true^state=1"
)
```

**Create a Normal Change**:
```python
create_change_request(
    change_type="normal",
    name_value_pairs="{'short_description': 'Upgrade Server', 'priority': '2', 'cmdb_ci': 'sys_id_here'}"
)
```

**Check Conflicts**:
```python
check_change_request_conflict(change_request_sys_id="...")
```

### servicenow-cicd

**Description:** Manages ServiceNow CI/CD. Use for batches, scans, installs, publishes. Triggers - deployments, testing, pipelines.

#### Overview
CI/CD operations via MCP. Reference `tools-reference.md` for schemas.

#### Key Tools
- `batch_install_result` / `instance_scan_progress` / `progress`: Query statuses.
- `batch_install` / `batch_rollback`: Batch ops.
- `app_repo_install` / `publish` / `rollback`: App repo.
- `full_scan` / `point_scan` / `combo_suite_scan` / `suite_scan`: Scans.

#### Usage Instructions
1. Use IDs for queries/actions.
2. For installs: scopes, versions.

#### Examples
- Batch install: `batch_install` with name="deploy", packages="pkg1,pkg2".
- Full scan: `full_scan`.

#### Error Handling
- Invalid IDs: Check existence.
- Failures: Retry or check logs.

### servicenow-cilifecycle

**Description:** Manages CI Lifecycle Management in ServiceNow. Use for checking compatibility of CI actions and registering operators.

#### Overview
Handles CI Lifecycle Management operations via MCP.

#### Key Tools
- `check_ci_lifecycle_compat_actions`: Determines whether two specified CI actions are compatible. Params: actionName, otherActionName.
- `register_ci_lifecycle_operator`: Registers an operator for a non-workflow user.
- `unregister_ci_lifecycle_operator`: Unregisters an operator for non-workflow users. Params: req_id.

#### Usage Instructions
1. Use `check_ci_lifecycle_compat_actions` before applying concurrent actions.
2. Register an operator if needed for non-workflow contexts.

#### Examples
- Check compatibility: `check_ci_lifecycle_compat_actions` with actionName="retire", otherActionName="install"

#### Error Handling
- 400: Invalid action names or parameters.

### servicenow-cmdb

**Description:** Manages ServiceNow CMDB. Use for fetching CMDB records. Triggers - configuration items, CI queries.

#### Overview
Queries CMDB via MCP.

#### Key Tools
- `get_cmdb`: Get record by ID. Params: cmdb_id (required).

#### Usage Instructions
1. Provide cmdb_id (sys_id).

#### Examples
- Get CI: `get_cmdb` with cmdb_id="def456".

#### Error Handling
- Missing ID: Required param.

### servicenow-custom-api

**Description:** Handles custom ServiceNow API requests. Use for uncategorized endpoints. Triggers - advanced calls.

#### Overview
Arbitrary API via MCP.

#### Key Tools
- `api_request`: Custom HTTP.

#### Usage Instructions
1. Method, endpoint, data/json.

#### Examples
- GET: `api_request` with method="GET", endpoint="custom/endpoint".

#### Error Handling
- Validate responses.

### servicenow-data-classification

**Description:** Capabilities for managing data classifications in ServiceNow.

## ServiceNow Data Classification

This skill allows the agent to retrieve data classification information for tables and columns in ServiceNow.

### Tools

#### `get_data_classification`

- **Description**: Retrieves data classification information.
- **Parameters**:
    - `sys_id` (Optional[str]): Classification record Sys ID.
    - `table_name` (Optional[str]): Table name.
    - `column_name` (Optional[str]): Column name.

### Usage

#### Getting Classification for a Column

```python
result = get_data_classification(
    table_name="incident",
    column_name="short_description"
)
```

### servicenow-devops

**Description:** Manages DevOps integration in ServiceNow. Use for checking change control and registering artifacts.

#### Overview
Handles DevOps integration tasks via MCP.

#### Key Tools
- `check_devops_change_control`: Checks if the orchestration task is under change control. Params: toolId (required), orchestrationTaskName (optional).
- `register_devops_artifact`: Registers artifacts into a ServiceNow instance. Params: artifacts (list), pipelineName etc.

#### Usage Instructions
1. Use `check_devops_change_control` to verify if a task requires change management.
2. Use `register_devops_artifact` to push build artifacts to ServiceNow.

#### Examples
- Check change control: `check_devops_change_control` with toolId="jenkins-1".

#### Error Handling
- 400: Invalid tool ID or parameters.

### servicenow-email

**Description:** Capabilities for sending and retrieving emails in ServiceNow.

## ServiceNow Email

This skill allows the agent to interact with the ServiceNow Email API to send and retrieve email messages.

### Tools

#### `send_email`

- **Description**: Sends an email via ServiceNow.
- **Parameters**:
    - `to` (Union[str, List[str]]): Recipient email addresses.
    - `subject` (Optional[str]): Email subject.
    - `text` (Optional[str]): Email body text.
    - `html` (Optional[str]): Email body HTML.

### Usage

#### Sending an Email

```python
result = send_email(
    to=["user@example.com"],
    subject="Test Email",
    text="This is a test email sent from ServiceNow Agent."
)
```

### servicenow-flows

**Description:** Manages and visualizes ServiceNow Flow Designer workflows. Use for generating Mermaid diagrams of flows and subflows. Triggers - flows, flow designer, subflows, flow diagrams.

#### Overview
The `servicenow-flows` skill provides advanced capabilities for analyzing and visualizing ServiceNow Flow Designer workflows. It leverages the `workflow_to_mermaid` tool to perform recursive subflow traversal and generate professional Markdown reports with embedded Mermaid diagrams.

#### Key Tools
- `workflow_to_mermaid`: Generates a unified Mermaid diagram and rich Markdown report for multiple flows.
  - **Params**:
    - `flow_identifiers` (required): List of flow names or sys_ids.
    - `save_to_file` (optional, default: True): Saves a .md file.
    - `output_dir` (optional, default: "./servicenow_flow_reports"): Folder for saved reports.
    - `mermaid_name` (optional): Basename for the generated file.
    - `max_depth` (optional, default: 5): Recursion depth for subflows.

#### Usage Instructions
1. Use `workflow_to_mermaid` when a user wants to "see", "visualize", or "diagram" a Flow Designer workflow.
2. The agent will recursively follow subflows and represent them in Mermaid `subgraph` blocks.
3. Branching logic (If, Switch, For Each) is automatically detected and labeled where possible.

#### Examples
- Visualize a flow: `workflow_to_mermaid` with `flow_identifiers=["Order Laptop"]`.
- Recursive analysis: `workflow_to_mermaid` with `flow_identifiers=["ParentFlow"]` and `max_depth=3`.

#### Error Handling
- **No Flows Found**: If the identifier doesn't match a name or sys_id in `sys_hub_flow`, the tool returns a summary indicating zero flows found.
- **Deep Recursion**: Max depth is capped to prevent infinite loops (default 5).

### servicenow-hr

**Description:** Capabilities for retrieving HR Profile information in ServiceNow.

## ServiceNow HR

This skill allows the agent to retrieve HR Profile information.

### Tools

#### `get_hr_profile`

- **Description**: Retrieves HR profile information.
- **Parameters**:
    - `sys_id` (Optional[str]): HR Profile Sys ID.
    - `user` (Optional[str]): User Sys ID.

### Usage

#### Getting HR Profile for a User

```python
result = get_hr_profile(user="sys_id_of_user")
```

### servicenow-import-sets

**Description:** Manages ServiceNow import sets. Use for getting/inserting records. Triggers - data imports, ETL.

#### Overview
Import set ops via MCP.

#### Key Tools
- `get_import_set` / `insert_import_set` / `insert_multiple_import_sets`.

#### Usage Instructions
1. Table name, data dicts.

#### Examples
- Insert: `insert_import_set` with table="import_table", data={"field1": "val"}.

#### Error Handling
- Validation errors: Check data.

### servicenow-incidents

**Description:** "Manages ServiceNow incidents. Use for getting/creating incidents. Triggers - tickets, issues."

#### Overview
Incident mgmt via MCP.

#### Key Tools
- `get_incidents`: List/get by ID.
- `create_incident`: Create.

#### Usage Instructions
1. Filters: sysparm_query.

#### Examples
- Create: `create_incident` with data={"short_description": "Outage"}.
- Get: `get_incidents` with sysparm_query="number=INC001".

#### Error Handling
- No results: Empty valid.

### servicenow-knowledge-management

**Description:** Manages ServiceNow KB. Use for articles, attachments, featured/most viewed. Triggers - docs, self-help.

#### Overview
KB queries via MCP.

#### Key Tools
- Get articles, attachments, featured, most viewed.

#### Usage Instructions
1. Filters: kb, language.

#### Examples
- Get article: `get_knowledge_article` with article_sys_id="kb1".
- Most viewed: `get_most_viewed_knowledge_articles`.

#### Error Handling
- No access: Check KB perms.

### servicenow-metricbase

**Description:** Capabilities for interacting with ServiceNow MetricBase for time series data.

## ServiceNow MetricBase

This skill allows the agent to insert time series data into MetricBase.

### Tools

#### `metricbase_insert`

- **Description**: Inserts time series data into MetricBase.
- **Parameters**:
    - `table_name` (str): Table name.
    - `sys_id` (str): Record Sys ID.
    - `metric_name` (str): Metric name.
    - `values` (List[Any]): Values to insert.
    - `start_time` (Optional[str]): Start time.
    - `end_time` (Optional[str]): End time.

### Usage

#### Inserting Metric Data

```python
result = metricbase_insert(
    table_name="incident_metric",
    sys_id="sys_id",
    metric_name="cpu_usage",
    values=[{"timestamp": "2023-10-27T10:00:00Z", "value": 50}]
)
```

### servicenow-plugins

**Description:** Manages ServiceNow plugins. Use for activating/rolling back plugins. Triggers - extensions, activations.

#### Overview
Plugin lifecycle via MCP.

#### Key Tools
- `activate_plugin`: Activate by ID.
- `rollback_plugin`: Rollback by ID.

#### Usage Instructions
1. Provide plugin_id.

#### Examples
- Activate: `activate_plugin` with plugin_id="plugin123".

#### Error Handling
- Already active: Idempotent.

### servicenow-ppm

**Description:** Manage Project Portfolio Management cost plans and project tasks.

## Project Portfolio Management (PPM)

This skill allows the agent to interact with the ServiceNow PPM API.

### Capabilities

- **Insert Cost Plans**: Create multiple cost plans in a batch.
- **Insert Project Tasks**: Create a project structure with tasks and dependencies.

### Tools

#### `insert_cost_plans`
Creates cost plans.

**Parameters:**
- `plans` (list): List of cost plan dictionaries.

#### `insert_project_tasks`
Creates a project and associated project tasks.

**Parameters:**
- `short_description` (string): Project description.
- `start_date` (string, optional): Start date (YYYY-MM-DD HH:MM:SS).
- `end_date` (string, optional): End date.
- `child_tasks` (list, optional): Recursive list of child tasks.
- `dependencies` (list, optional): Dependencies between tasks.

### Examples

#### Create Cost Plans
```python
insert_cost_plans(plans=[
    {
        "name": "Hardware Cost",
        "resource_type": "resource_type_sys_id",
        "start_fiscal_period": "period_sys_id",
        "end_fiscal_period": "period_sys_id",
        "task": "project_sys_id",
        "unit_cost": 5000.0
    }
])
```

#### Create Project Structure
```python
insert_project_tasks(
    short_description="New Infrastructure Project",
    start_date="2024-01-01 09:00:00",
    child_tasks=[
        {"short_description": "Phase 1: Planning"},
        {"short_description": "Phase 2: Execution"}
    ]
)
```

### servicenow-product-inventory

**Description:** Manage and query product inventory.

## Product Inventory

This skill allows the agent to interact with the ServiceNow Product Inventory API.

### Capabilities

- **Get Product Inventory**: Retrieve product inventory records with various filters.
- **Delete Product Inventory**: Delete a product inventory record.

### Tools

#### `get_product_inventory`
Retrieves product inventory.

**Parameters:**
- `customer` (optional): Filter by customer ID.
- `place_id` (optional): Filter by location ID.
- `status` (optional): Filter by status (e.g., 'active').
- `limit` (optional): Max records.
- `offset` (optional): Pagination offset.

#### `delete_product_inventory`
Deletes a product inventory record.

**Parameters:**
- `id`: The Sys ID of the product inventory record.

### Examples

#### List Active Products for Customer
```python
get_product_inventory(customer="customer_sys_id", status="active")
```

#### Delete Product
```python
delete_product_inventory(id="product_sys_id")
```

### servicenow-service-qualification

**Description:** Validates technical service availability and eligibility.

## Service Qualification

This skill allows the agent to interact with the ServiceNow Technical Service Qualification API.

### Capabilities

- **Check Service Qualification**: Create a qualification request to check if a service can be provided.
- **Get Service Qualification**: Retrieve the details and status of a qualification request.
- **Process Qualification Result**: (Advanced) Process the results of a qualification check.

### Tools

#### `check_service_qualification`
Creates a technical service qualification request.

**Parameters:**
- `description` (optional): Description of the request.
- `externalId` (optional): External reference ID.
- `relatedParty` (list): List of related parties (Customer, etc.).
- `serviceQualificationItem` (list): List of items to qualify.

#### `get_service_qualification`
Retrieves a qualification request.

**Parameters:**
- `id` (optional): The Sys ID or External ID of the qualification request.
- `state` (optional): Filter by state.

#### `process_service_qualification_result`
Processes the result of a qualification.

**Parameters:**
- `serviceQualificationItem` (list): The items with qualification results.
- `description` (optional): Description.

### Examples

#### Check Qualification
```python
check_service_qualification(
    description="Check feasibility for SD-WAN",
    relatedParty=[
        {"id": "customer_sys_id", "@referredType": "Customer", "@type": "RelatedParty"}
    ],
    serviceQualificationItem=[
        {
            "id": "item_1",
            "service": {
                "serviceSpecification": {
                    "id": "sd_wan_spec_id"
                }
            }
        }
    ]
)
```

#### Get Qualification Status
```python
get_service_qualification(id="qual_req_sys_id")
```

### servicenow-source-control

**Description:** Manages ServiceNow source control. Use for applying changes, importing repos. Triggers - git integration, SCM.

#### Overview
Source control ops via MCP.

#### Key Tools
- `apply_remote_source_control_changes`: Apply branch changes.
- `import_repository`: Import repo.

#### Usage Instructions
1. Use sys_ids, branches.

#### Examples
- Apply: `apply_remote_source_control_changes` with app_sys_id="app1", scope="global", branch_name="main".

#### Error Handling
- Conflicts: Resolve manually.

### servicenow-table-api

**Description:** Manages ServiceNow tables. Use for CRUD on any table. Triggers - generic data ops.

#### Overview
Table API via MCP.

#### Key Tools
- Delete/get/patch/update/add records.

#### Usage Instructions
1. Table name, sys_id, data.

#### Examples
- Add: `add_table_record` with table="custom", data={"field": "val"}.
- Update: `update_table_record` with sys_id="rec1", data=updates.

#### Error Handling
- Table not found: Verify name.

### servicenow-testing

**Description:** Manages ServiceNow testing. Use for running test suites. Triggers - ATF, automated tests.

#### Overview
Testing via MCP.

#### Key Tools
- `run_test_suite`: Run suite with browser/OS.

#### Usage Instructions
1. Provide suite sys_id/name.

#### Examples
- Run: `run_test_suite` with test_suite_sys_id="suite1", browser_name="chrome".

#### Error Handling
- Failures: Check results.

### servicenow-update-sets

**Description:** Manages ServiceNow update sets. Use for creating, retrieving, previewing, committing. Triggers - customizations, deployments.

#### Overview
Update set ops via MCP.

#### Key Tools
- `update_set_create` / `retrieve` / `preview` / `commit` / `commit_multiple` / `back_out`.

#### Usage Instructions
1. Use IDs for actions.

#### Examples
- Create: `update_set_create` with update_set_name="fix1", scope="global".

#### Error Handling
- Preview conflicts: Resolve before commit.
