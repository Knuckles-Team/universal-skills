# Ansible Tower MCP Reference

**Project:** `ansible-tower-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ANSIBLE_TOWER_URL` | Required for authentication |
| `ANSIBLE_TOWER_TOKEN` | Required for authentication |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "ansible-tower-mcp": {
      "command": "ansible-tower-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "ANSIBLE_TOWER_URL": "${ANSIBLE_TOWER_URL}",
        "ANSIBLE_TOWER_TOKEN": "${ANSIBLE_TOWER_TOKEN}"
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
    "ansible-tower-mcp": {
      "url": "http://ansible-tower-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/ansible-tower-mcp.json --action list-tools

# Generate a single-tag config
# (No tool tags — all tools are always enabled)
```

## Tailored Skills Reference

### test-skill

**Description:** A test skill.

## test-skill Skill

### When to use
For testing.

### How to use
Call it.

### Examples
- Example 1: ...

### ansible-tower-mcp-ad-hoc-commands

**Description:** Ansible Tower Mcp Ad Hoc Commands capabilities for A2A Agent.

#### Overview
This skill provides access to ad_hoc_commands operations.

#### Capabilities
- **run_ad_hoc_command**: Runs an ad hoc command on hosts in Ansible Tower. Returns a dictionary with the command job's details, including its ID.
- **get_ad_hoc_command**: Fetches details of a specific ad hoc command by ID from Ansible Tower. Returns a dictionary with command information such as status and module_args.
- **cancel_ad_hoc_command**: Cancels a running ad hoc command in Ansible Tower. Returns a dictionary confirming the cancellation status.

#### Common Tools
- `run_ad_hoc_command`: Runs an ad hoc command on hosts in Ansible Tower. Returns a dictionary with the command job's details, including its ID.
- `get_ad_hoc_command`: Fetches details of a specific ad hoc command by ID from Ansible Tower. Returns a dictionary with command information such as status and module_args.
- `cancel_ad_hoc_command`: Cancels a running ad hoc command in Ansible Tower. Returns a dictionary confirming the cancellation status.

#### Usage Rules
- Use these tools when the user requests actions related to **ad_hoc_commands**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please run ad hoc command"
- "Please get ad hoc command"
- "Please cancel ad hoc command"

### ansible-tower-mcp-credentials

**Description:** Ansible Tower Mcp Credentials capabilities for A2A Agent.

#### Overview
This skill provides access to credentials operations.

#### Capabilities
- **list_credentials**: Retrieves a paginated list of credentials from Ansible Tower. Returns a list of dictionaries, each with credential details like id, name, and type. Display in a markdown table.
- **get_credential**: Fetches details of a specific credential by ID from Ansible Tower. Returns a dictionary with credential information such as name and inputs (masked).
- **list_credential_types**: Retrieves a paginated list of credential types from Ansible Tower. Returns a list of dictionaries, each with type details like id and name. Display in a markdown table.
- **create_credential**: Creates a new credential in Ansible Tower. Returns a dictionary with the created credential's details, including its ID.
- **update_credential**: Updates an existing credential in Ansible Tower. Returns a dictionary with the updated credential's details.
- **delete_credential**: Deletes a specific credential by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_credentials`: Retrieves a paginated list of credentials from Ansible Tower. Returns a list of dictionaries, each with credential details like id, name, and type. Display in a markdown table.
- `get_credential`: Fetches details of a specific credential by ID from Ansible Tower. Returns a dictionary with credential information such as name and inputs (masked).
- `list_credential_types`: Retrieves a paginated list of credential types from Ansible Tower. Returns a list of dictionaries, each with type details like id and name. Display in a markdown table.
- `create_credential`: Creates a new credential in Ansible Tower. Returns a dictionary with the created credential's details, including its ID.
- `update_credential`: Updates an existing credential in Ansible Tower. Returns a dictionary with the updated credential's details.
- `delete_credential`: Deletes a specific credential by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **credentials**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please create credential"
- "Please delete credential"
- "Please list credentials"
- "Please update credential"
- "Please get credential"

### ansible-tower-mcp-groups

**Description:** Ansible Tower Mcp Groups capabilities for A2A Agent.

#### Overview
This skill provides access to groups operations.

#### Capabilities
- **list_groups**: Retrieves a paginated list of groups in a specified inventory from Ansible Tower. Returns a list of dictionaries, each with group details like id, name, and variables. Display in a markdown table.
- **get_group**: Fetches details of a specific group by ID from Ansible Tower. Returns a dictionary with group information such as name, variables, and inventory.
- **create_group**: Creates a new group in a specified inventory in Ansible Tower. Returns a dictionary with the created group's details, including its ID.
- **update_group**: Updates an existing group in Ansible Tower. Returns a dictionary with the updated group's details.
- **delete_group**: Deletes a specific group by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- **add_host_to_group**: Adds a host to a group in Ansible Tower. Returns a dictionary confirming the association.
- **remove_host_from_group**: Removes a host from a group in Ansible Tower. Returns a dictionary confirming the disassociation.

#### Common Tools
- `list_groups`: Retrieves a paginated list of groups in a specified inventory from Ansible Tower. Returns a list of dictionaries, each with group details like id, name, and variables. Display in a markdown table.
- `get_group`: Fetches details of a specific group by ID from Ansible Tower. Returns a dictionary with group information such as name, variables, and inventory.
- `create_group`: Creates a new group in a specified inventory in Ansible Tower. Returns a dictionary with the created group's details, including its ID.
- `update_group`: Updates an existing group in Ansible Tower. Returns a dictionary with the updated group's details.
- `delete_group`: Deletes a specific group by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- `add_host_to_group`: Adds a host to a group in Ansible Tower. Returns a dictionary confirming the association.
- `remove_host_from_group`: Removes a host from a group in Ansible Tower. Returns a dictionary confirming the disassociation.

#### Usage Rules
- Use these tools when the user requests actions related to **groups**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please list groups"
- "Please remove host from group"
- "Please update group"
- "Please delete group"
- "Please get group"

### ansible-tower-mcp-hosts

**Description:** Ansible Tower Mcp Hosts capabilities for A2A Agent.

#### Overview
This skill provides access to hosts operations.

#### Capabilities
- **list_hosts**: Retrieves a paginated list of hosts from Ansible Tower, optionally filtered by inventory. Returns a list of dictionaries, each with host details like id, name, and variables. Display in a markdown table.
- **get_host**: Fetches details of a specific host by ID from Ansible Tower. Returns a dictionary with host information such as name, variables, and inventory.
- **create_host**: Creates a new host in a specified inventory in Ansible Tower. Returns a dictionary with the created host's details, including its ID.
- **update_host**: Updates an existing host in Ansible Tower. Returns a dictionary with the updated host's details.
- **delete_host**: Deletes a specific host by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_hosts`: Retrieves a paginated list of hosts from Ansible Tower, optionally filtered by inventory. Returns a list of dictionaries, each with host details like id, name, and variables. Display in a markdown table.
- `get_host`: Fetches details of a specific host by ID from Ansible Tower. Returns a dictionary with host information such as name, variables, and inventory.
- `create_host`: Creates a new host in a specified inventory in Ansible Tower. Returns a dictionary with the created host's details, including its ID.
- `update_host`: Updates an existing host in Ansible Tower. Returns a dictionary with the updated host's details.
- `delete_host`: Deletes a specific host by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **hosts**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please create host"
- "Please get host"
- "Please delete host"
- "Please list hosts"
- "Please update host"

### ansible-tower-mcp-inventory

**Description:** Ansible Tower Mcp Inventory capabilities for A2A Agent.

#### Overview
This skill provides access to inventory operations.

#### Capabilities
- **list_inventories**: Retrieves a paginated list of inventories from Ansible Tower. Returns a list of dictionaries, each containing inventory details like id, name, and description. Display results in a markdown table for clarity.
- **get_inventory**: Fetches details of a specific inventory by ID from Ansible Tower. Returns a dictionary with inventory information such as name, description, and hosts count.
- **create_inventory**: Creates a new inventory in Ansible Tower. Returns a dictionary with the created inventory's details, including its ID.
- **update_inventory**: Updates an existing inventory in Ansible Tower. Returns a dictionary with the updated inventory's details.
- **delete_inventory**: Deletes a specific inventory by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_inventories`: Retrieves a paginated list of inventories from Ansible Tower. Returns a list of dictionaries, each containing inventory details like id, name, and description. Display results in a markdown table for clarity.
- `get_inventory`: Fetches details of a specific inventory by ID from Ansible Tower. Returns a dictionary with inventory information such as name, description, and hosts count.
- `create_inventory`: Creates a new inventory in Ansible Tower. Returns a dictionary with the created inventory's details, including its ID.
- `update_inventory`: Updates an existing inventory in Ansible Tower. Returns a dictionary with the updated inventory's details.
- `delete_inventory`: Deletes a specific inventory by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **inventory**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please get inventory"
- "Please delete inventory"
- "Please list inventories"
- "Please update inventory"
- "Please create inventory"

### ansible-tower-mcp-job-templates

**Description:** Ansible Tower Mcp Job Templates capabilities for A2A Agent.

#### Overview
This skill provides access to job_templates operations.

#### Capabilities
- **list_job_templates**: Retrieves a paginated list of job templates from Ansible Tower. Returns a list of dictionaries, each with template details like id, name, and playbook. Display in a markdown table.
- **get_job_template**: Fetches details of a specific job template by ID from Ansible Tower. Returns a dictionary with template information such as name, inventory, and extra_vars.
- **create_job_template**: Creates a new job template in Ansible Tower. Returns a dictionary with the created template's details, including its ID.
- **update_job_template**: Updates an existing job template in Ansible Tower. Returns a dictionary with the updated template's details.
- **delete_job_template**: Deletes a specific job template by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- **launch_job**: Launches a job from a template in Ansible Tower, optionally with extra variables. Returns a dictionary with the launched job's details, including its ID.

#### Common Tools
- `list_job_templates`: Retrieves a paginated list of job templates from Ansible Tower. Returns a list of dictionaries, each with template details like id, name, and playbook. Display in a markdown table.
- `get_job_template`: Fetches details of a specific job template by ID from Ansible Tower. Returns a dictionary with template information such as name, inventory, and extra_vars.
- `create_job_template`: Creates a new job template in Ansible Tower. Returns a dictionary with the created template's details, including its ID.
- `update_job_template`: Updates an existing job template in Ansible Tower. Returns a dictionary with the updated template's details.
- `delete_job_template`: Deletes a specific job template by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- `launch_job`: Launches a job from a template in Ansible Tower, optionally with extra variables. Returns a dictionary with the launched job's details, including its ID.

#### Usage Rules
- Use these tools when the user requests actions related to **job_templates**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please update job template"
- "Please launch job"
- "Please delete job template"
- "Please list job templates"
- "Please get job template"

### ansible-tower-mcp-jobs

**Description:** Ansible Tower Mcp Jobs capabilities for A2A Agent.

#### Overview
This skill provides access to jobs operations.

#### Capabilities
- **list_jobs**: Retrieves a paginated list of jobs from Ansible Tower, optionally filtered by status. Returns a list of dictionaries, each with job details like id, status, and elapsed time. Display in a markdown table.
- **get_job**: Fetches details of a specific job by ID from Ansible Tower. Returns a dictionary with job information such as status, start time, and artifacts.
- **cancel_job**: Cancels a running job in Ansible Tower. Returns a dictionary confirming the cancellation status.
- **get_job_events**: Retrieves a paginated list of events for a specific job from Ansible Tower. Returns a list of dictionaries, each with event details like type, host, and stdout. Display in a markdown table.
- **get_job_stdout**: Fetches the stdout output of a job in the specified format from Ansible Tower. Returns a dictionary with the output content.

#### Common Tools
- `list_jobs`: Retrieves a paginated list of jobs from Ansible Tower, optionally filtered by status. Returns a list of dictionaries, each with job details like id, status, and elapsed time. Display in a markdown table.
- `get_job`: Fetches details of a specific job by ID from Ansible Tower. Returns a dictionary with job information such as status, start time, and artifacts.
- `cancel_job`: Cancels a running job in Ansible Tower. Returns a dictionary confirming the cancellation status.
- `get_job_events`: Retrieves a paginated list of events for a specific job from Ansible Tower. Returns a list of dictionaries, each with event details like type, host, and stdout. Display in a markdown table.
- `get_job_stdout`: Fetches the stdout output of a job in the specified format from Ansible Tower. Returns a dictionary with the output content.

#### Usage Rules
- Use these tools when the user requests actions related to **jobs**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please get job stdout"
- "Please list jobs"
- "Please get job events"
- "Please cancel job"
- "Please get job"

### ansible-tower-mcp-organizations

**Description:** Ansible Tower Mcp Organizations capabilities for A2A Agent.

#### Overview
This skill provides access to organizations operations.

#### Capabilities
- **list_organizations**: Retrieves a paginated list of organizations from Ansible Tower. Returns a list of dictionaries, each with organization details like id and name. Display in a markdown table.
- **get_organization**: Fetches details of a specific organization by ID from Ansible Tower. Returns a dictionary with organization information such as name and description.
- **create_organization**: Creates a new organization in Ansible Tower. Returns a dictionary with the created organization's details, including its ID.
- **update_organization**: Updates an existing organization in Ansible Tower. Returns a dictionary with the updated organization's details.
- **delete_organization**: Deletes a specific organization by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_organizations`: Retrieves a paginated list of organizations from Ansible Tower. Returns a list of dictionaries, each with organization details like id and name. Display in a markdown table.
- `get_organization`: Fetches details of a specific organization by ID from Ansible Tower. Returns a dictionary with organization information such as name and description.
- `create_organization`: Creates a new organization in Ansible Tower. Returns a dictionary with the created organization's details, including its ID.
- `update_organization`: Updates an existing organization in Ansible Tower. Returns a dictionary with the updated organization's details.
- `delete_organization`: Deletes a specific organization by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **organizations**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please list organizations"
- "Please get organization"
- "Please delete organization"
- "Please update organization"
- "Please create organization"

### ansible-tower-mcp-projects

**Description:** Ansible Tower Mcp Projects capabilities for A2A Agent.

#### Overview
This skill provides access to projects operations.

#### Capabilities
- **list_projects**: Retrieves a paginated list of projects from Ansible Tower. Returns a list of dictionaries, each with project details like id, name, and scm_type. Display in a markdown table.
- **get_project**: Fetches details of a specific project by ID from Ansible Tower. Returns a dictionary with project information such as name, scm_url, and status.
- **create_project**: Creates a new project in Ansible Tower. Returns a dictionary with the created project's details, including its ID.
- **update_project**: Updates an existing project in Ansible Tower. Returns a dictionary with the updated project's details.
- **delete_project**: Deletes a specific project by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- **sync_project**: Syncs (updates from SCM) a project in Ansible Tower. Returns a dictionary with the sync job's details.

#### Common Tools
- `list_projects`: Retrieves a paginated list of projects from Ansible Tower. Returns a list of dictionaries, each with project details like id, name, and scm_type. Display in a markdown table.
- `get_project`: Fetches details of a specific project by ID from Ansible Tower. Returns a dictionary with project information such as name, scm_url, and status.
- `create_project`: Creates a new project in Ansible Tower. Returns a dictionary with the created project's details, including its ID.
- `update_project`: Updates an existing project in Ansible Tower. Returns a dictionary with the updated project's details.
- `delete_project`: Deletes a specific project by ID from Ansible Tower. Returns a dictionary confirming the deletion status.
- `sync_project`: Syncs (updates from SCM) a project in Ansible Tower. Returns a dictionary with the sync job's details.

#### Usage Rules
- Use these tools when the user requests actions related to **projects**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please delete project"
- "Please update project"
- "Please create project"
- "Please list projects"
- "Please get project"

### ansible-tower-mcp-schedules

**Description:** Ansible Tower Mcp Schedules capabilities for A2A Agent.

#### Overview
This skill provides access to schedules operations.

#### Capabilities
- **list_schedules**: Retrieves a paginated list of schedules from Ansible Tower, optionally filtered by template. Returns a list of dictionaries, each with schedule details like id, name, and rrule. Display in a markdown table.
- **get_schedule**: Fetches details of a specific schedule by ID from Ansible Tower. Returns a dictionary with schedule information such as name and rrule.
- **create_schedule**: Creates a new schedule for a template in Ansible Tower. Returns a dictionary with the created schedule's details, including its ID.
- **update_schedule**: Updates an existing schedule in Ansible Tower. Returns a dictionary with the updated schedule's details.
- **delete_schedule**: Deletes a specific schedule by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_schedules`: Retrieves a paginated list of schedules from Ansible Tower, optionally filtered by template. Returns a list of dictionaries, each with schedule details like id, name, and rrule. Display in a markdown table.
- `get_schedule`: Fetches details of a specific schedule by ID from Ansible Tower. Returns a dictionary with schedule information such as name and rrule.
- `create_schedule`: Creates a new schedule for a template in Ansible Tower. Returns a dictionary with the created schedule's details, including its ID.
- `update_schedule`: Updates an existing schedule in Ansible Tower. Returns a dictionary with the updated schedule's details.
- `delete_schedule`: Deletes a specific schedule by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **schedules**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please get schedule"
- "Please delete schedule"
- "Please list schedules"
- "Please update schedule"
- "Please create schedule"

### ansible-tower-mcp-system

**Description:** Ansible Tower Mcp System capabilities for A2A Agent.

#### Overview
This skill provides access to system operations.

#### Capabilities
- **get_ansible_version**: Retrieves the Ansible version information from Ansible Tower. Returns a dictionary with version details.
- **get_dashboard_stats**: Fetches dashboard statistics from Ansible Tower. Returns a dictionary with stats like host counts and recent jobs.
- **get_metrics**: Retrieves system metrics from Ansible Tower. Returns a dictionary with performance and usage metrics.

#### Common Tools
- `get_ansible_version`: Retrieves the Ansible version information from Ansible Tower. Returns a dictionary with version details.
- `get_dashboard_stats`: Fetches dashboard statistics from Ansible Tower. Returns a dictionary with stats like host counts and recent jobs.
- `get_metrics`: Retrieves system metrics from Ansible Tower. Returns a dictionary with performance and usage metrics.

#### Usage Rules
- Use these tools when the user requests actions related to **system**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please get ansible version"
- "Please get metrics"
- "Please get dashboard stats"

### ansible-tower-mcp-teams

**Description:** Ansible Tower Mcp Teams capabilities for A2A Agent.

#### Overview
This skill provides access to teams operations.

#### Capabilities
- **list_teams**: Retrieves a paginated list of teams from Ansible Tower, optionally filtered by organization. Returns a list of dictionaries, each with team details like id and name. Display in a markdown table.
- **get_team**: Fetches details of a specific team by ID from Ansible Tower. Returns a dictionary with team information such as name and organization.
- **create_team**: Creates a new team in a specified organization in Ansible Tower. Returns a dictionary with the created team's details, including its ID.
- **update_team**: Updates an existing team in Ansible Tower. Returns a dictionary with the updated team's details.
- **delete_team**: Deletes a specific team by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_teams`: Retrieves a paginated list of teams from Ansible Tower, optionally filtered by organization. Returns a list of dictionaries, each with team details like id and name. Display in a markdown table.
- `get_team`: Fetches details of a specific team by ID from Ansible Tower. Returns a dictionary with team information such as name and organization.
- `create_team`: Creates a new team in a specified organization in Ansible Tower. Returns a dictionary with the created team's details, including its ID.
- `update_team`: Updates an existing team in Ansible Tower. Returns a dictionary with the updated team's details.
- `delete_team`: Deletes a specific team by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **teams**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please update team"
- "Please create team"
- "Please delete team"
- "Please list teams"
- "Please get team"

### ansible-tower-mcp-users

**Description:** Ansible Tower Mcp Users capabilities for A2A Agent.

#### Overview
This skill provides access to users operations.

#### Capabilities
- **list_users**: Retrieves a paginated list of users from Ansible Tower. Returns a list of dictionaries, each with user details like id, username, and email. Display in a markdown table.
- **get_user**: Fetches details of a specific user by ID from Ansible Tower. Returns a dictionary with user information such as username, email, and roles.
- **create_user**: Creates a new user in Ansible Tower. Returns a dictionary with the created user's details, including its ID.
- **update_user**: Updates an existing user in Ansible Tower. Returns a dictionary with the updated user's details.
- **delete_user**: Deletes a specific user by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Common Tools
- `list_users`: Retrieves a paginated list of users from Ansible Tower. Returns a list of dictionaries, each with user details like id, username, and email. Display in a markdown table.
- `get_user`: Fetches details of a specific user by ID from Ansible Tower. Returns a dictionary with user information such as username, email, and roles.
- `create_user`: Creates a new user in Ansible Tower. Returns a dictionary with the created user's details, including its ID.
- `update_user`: Updates an existing user in Ansible Tower. Returns a dictionary with the updated user's details.
- `delete_user`: Deletes a specific user by ID from Ansible Tower. Returns a dictionary confirming the deletion status.

#### Usage Rules
- Use these tools when the user requests actions related to **users**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please list users"
- "Please delete user"
- "Please create user"
- "Please get user"
- "Please update user"

### ansible-tower-mcp-workflow-jobs

**Description:** Ansible Tower Mcp Workflow Jobs capabilities for A2A Agent.

#### Overview
This skill provides access to workflow_jobs operations.

#### Capabilities
- **list_workflow_jobs**: Retrieves a paginated list of workflow jobs from Ansible Tower, optionally filtered by status. Returns a list of dictionaries, each with job details like id and status. Display in a markdown table.
- **get_workflow_job**: Fetches details of a specific workflow job by ID from Ansible Tower. Returns a dictionary with job information such as status and start time.
- **cancel_workflow_job**: Cancels a running workflow job in Ansible Tower. Returns a dictionary confirming the cancellation status.

#### Common Tools
- `list_workflow_jobs`: Retrieves a paginated list of workflow jobs from Ansible Tower, optionally filtered by status. Returns a list of dictionaries, each with job details like id and status. Display in a markdown table.
- `get_workflow_job`: Fetches details of a specific workflow job by ID from Ansible Tower. Returns a dictionary with job information such as status and start time.
- `cancel_workflow_job`: Cancels a running workflow job in Ansible Tower. Returns a dictionary confirming the cancellation status.

#### Usage Rules
- Use these tools when the user requests actions related to **workflow_jobs**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please cancel workflow job"
- "Please list workflow jobs"
- "Please get workflow job"

### ansible-tower-mcp-workflow-templates

**Description:** Ansible Tower Mcp Workflow Templates capabilities for A2A Agent.

#### Overview
This skill provides access to workflow_templates operations.

#### Capabilities
- **list_workflow_templates**: Retrieves a paginated list of workflow templates from Ansible Tower. Returns a list of dictionaries, each with template details like id and name. Display in a markdown table.
- **get_workflow_template**: Fetches details of a specific workflow template by ID from Ansible Tower. Returns a dictionary with template information such as name and extra_vars.
- **launch_workflow**: Launches a workflow from a template in Ansible Tower, optionally with extra variables. Returns a dictionary with the launched workflow job's details, including its ID.

#### Common Tools
- `list_workflow_templates`: Retrieves a paginated list of workflow templates from Ansible Tower. Returns a list of dictionaries, each with template details like id and name. Display in a markdown table.
- `get_workflow_template`: Fetches details of a specific workflow template by ID from Ansible Tower. Returns a dictionary with template information such as name and extra_vars.
- `launch_workflow`: Launches a workflow from a template in Ansible Tower, optionally with extra variables. Returns a dictionary with the launched workflow job's details, including its ID.

#### Usage Rules
- Use these tools when the user requests actions related to **workflow_templates**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please list workflow templates"
- "Please launch workflow"
- "Please get workflow template"
