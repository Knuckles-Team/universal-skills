# Microsoft 365 MCP Reference

**Project:** `microsoft-agent`
**Entrypoint:** `microsoft-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MICROSOFT_CLIENT_ID` | Required for authentication |
| `MICROSOFT_CLIENT_SECRET` | Required for authentication |
| `MICROSOFT_TENANT_ID` | Required for authentication |

## Available Tool Tags (37)

| Env Variable | Default |
|-------------|----------|
| `ADMINTOOL` | `True` |
| `AGREEMENTSTOOL` | `True` |
| `APPLICATIONSTOOL` | `True` |
| `AUDITTOOL` | `True` |
| `AUTHTOOL` | `True` |
| `CALENDARTOOL` | `True` |
| `CHATTOOL` | `True` |
| `COMMUNICATIONSTOOL` | `True` |
| `CONNECTIONSTOOL` | `True` |
| `CONTACTSTOOL` | `True` |
| `DEVICESTOOL` | `True` |
| `DIRECTORYTOOL` | `True` |
| `DOMAINSTOOL` | `True` |
| `EDUCATIONTOOL` | `True` |
| `EMPLOYEE_EXPERIENCETOOL` | `True` |
| `FILESTOOL` | `True` |
| `GROUPSTOOL` | `True` |
| `IDENTITYTOOL` | `True` |
| `MAILTOOL` | `True` |
| `METATOOL` | `True` |
| `MISCTOOL` | `True` |
| `NOTESTOOL` | `True` |
| `ORGANIZATIONTOOL` | `True` |
| `PLACESTOOL` | `True` |
| `POLICIESTOOL` | `True` |
| `PRINTTOOL` | `True` |
| `PRIVACYTOOL` | `True` |
| `REPORTSTOOL` | `True` |
| `SEARCHTOOL` | `True` |
| `SECURITYTOOL` | `True` |
| `SITESTOOL` | `True` |
| `SOLUTIONSTOOL` | `True` |
| `STORAGETOOL` | `True` |
| `SUBSCRIPTIONSTOOL` | `True` |
| `TASKSTOOL` | `True` |
| `TEAMSTOOL` | `True` |
| `USERTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "microsoft-agent": {
      "command": "microsoft-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MICROSOFT_CLIENT_ID": "${MICROSOFT_CLIENT_ID}",
        "MICROSOFT_CLIENT_SECRET": "${MICROSOFT_CLIENT_SECRET}",
        "MICROSOFT_TENANT_ID": "${MICROSOFT_TENANT_ID}",
        "ADMINTOOL": "True",
        "AGREEMENTSTOOL": "True",
        "APPLICATIONSTOOL": "True",
        "AUDITTOOL": "True",
        "AUTHTOOL": "True",
        "CALENDARTOOL": "True",
        "CHATTOOL": "True",
        "COMMUNICATIONSTOOL": "True",
        "CONNECTIONSTOOL": "True",
        "CONTACTSTOOL": "True",
        "DEVICESTOOL": "True",
        "DIRECTORYTOOL": "True",
        "DOMAINSTOOL": "True",
        "EDUCATIONTOOL": "True",
        "EMPLOYEE_EXPERIENCETOOL": "True",
        "FILESTOOL": "True",
        "GROUPSTOOL": "True",
        "IDENTITYTOOL": "True",
        "MAILTOOL": "True",
        "METATOOL": "True",
        "MISCTOOL": "True",
        "NOTESTOOL": "True",
        "ORGANIZATIONTOOL": "True",
        "PLACESTOOL": "True",
        "POLICIESTOOL": "True",
        "PRINTTOOL": "True",
        "PRIVACYTOOL": "True",
        "REPORTSTOOL": "True",
        "SEARCHTOOL": "True",
        "SECURITYTOOL": "True",
        "SITESTOOL": "True",
        "SOLUTIONSTOOL": "True",
        "STORAGETOOL": "True",
        "SUBSCRIPTIONSTOOL": "True",
        "TASKSTOOL": "True",
        "TEAMSTOOL": "True",
        "USERTOOL": "True"
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
    "microsoft-agent": {
      "url": "http://microsoft-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `ADMINTOOL` and disable all others:

```json
{
  "mcpServers": {
    "microsoft-agent": {
      "command": "microsoft-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MICROSOFT_CLIENT_ID": "${MICROSOFT_CLIENT_ID}",
        "MICROSOFT_CLIENT_SECRET": "${MICROSOFT_CLIENT_SECRET}",
        "MICROSOFT_TENANT_ID": "${MICROSOFT_TENANT_ID}",
        "ADMINTOOL": "True",
        "AGREEMENTSTOOL": "False",
        "APPLICATIONSTOOL": "False",
        "AUDITTOOL": "False",
        "AUTHTOOL": "False",
        "CALENDARTOOL": "False",
        "CHATTOOL": "False",
        "COMMUNICATIONSTOOL": "False",
        "CONNECTIONSTOOL": "False",
        "CONTACTSTOOL": "False",
        "DEVICESTOOL": "False",
        "DIRECTORYTOOL": "False",
        "DOMAINSTOOL": "False",
        "EDUCATIONTOOL": "False",
        "EMPLOYEE_EXPERIENCETOOL": "False",
        "FILESTOOL": "False",
        "GROUPSTOOL": "False",
        "IDENTITYTOOL": "False",
        "MAILTOOL": "False",
        "METATOOL": "False",
        "MISCTOOL": "False",
        "NOTESTOOL": "False",
        "ORGANIZATIONTOOL": "False",
        "PLACESTOOL": "False",
        "POLICIESTOOL": "False",
        "PRINTTOOL": "False",
        "PRIVACYTOOL": "False",
        "REPORTSTOOL": "False",
        "SEARCHTOOL": "False",
        "SECURITYTOOL": "False",
        "SITESTOOL": "False",
        "SOLUTIONSTOOL": "False",
        "STORAGETOOL": "False",
        "SUBSCRIPTIONSTOOL": "False",
        "TASKSTOOL": "False",
        "TEAMSTOOL": "False",
        "USERTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/microsoft-agent.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command microsoft-mcp \
    --enable-tag ADMINTOOL \
    --all-tags "ADMINTOOL,AGREEMENTSTOOL,APPLICATIONSTOOL,AUDITTOOL,AUTHTOOL,CALENDARTOOL,CHATTOOL,COMMUNICATIONSTOOL,CONNECTIONSTOOL,CONTACTSTOOL,DEVICESTOOL,DIRECTORYTOOL,DOMAINSTOOL,EDUCATIONTOOL,EMPLOYEE_EXPERIENCETOOL,FILESTOOL,GROUPSTOOL,IDENTITYTOOL,MAILTOOL,METATOOL,MISCTOOL,NOTESTOOL,ORGANIZATIONTOOL,PLACESTOOL,POLICIESTOOL,PRINTTOOL,PRIVACYTOOL,REPORTSTOOL,SEARCHTOOL,SECURITYTOOL,SITESTOOL,SOLUTIONSTOOL,STORAGETOOL,SUBSCRIPTIONSTOOL,TASKSTOOL,TEAMSTOOL,USERTOOL"
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

### microsoft-admin

**Description:** "Microsoft 365 Admin — Service Health, Messages, SharePoint Admin & Delegated Admin Relationships"

## Microsoft 365 Admin

Manage tenant administration including service health, announcements, SharePoint admin, and delegated admin relationships.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_admin_sharepoint` | Get SharePoint admin settings for the tenant |
| `get_delegated_admin_relationship` | Get a specific delegated admin relationship |
| `get_service_health` | Get the health status for a specific service |
| `get_service_health_issue` | Get a specific service health issue |
| `get_service_update_message` | Get a specific service update message |
| `list_delegated_admin_relationships` | List delegated admin relationships |
| `list_service_health` | Get the service health status for all services in the tenant |
| `list_service_health_issues` | List all service health issues for the tenant |
| `list_service_update_messages` | List service update messages (message center posts) for the tenant |
| `update_admin_sharepoint` | Update SharePoint admin settings for the tenant |

### Required Permissions
- `ServiceHealth.Read.All, ServiceMessage.Read.All, Sites.Read.All, DelegatedAdminRelationship.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-agreements

**Description:** "Microsoft 365 Agreements — Terms-of-Use Agreements Management"

## Microsoft 365 Agreements

Manage terms-of-use agreements for the tenant.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_agreement` | Create a terms-of-use agreement |
| `delete_agreement` | Delete an agreement |
| `get_agreement` | Get a specific agreement |
| `list_agreements` | List terms-of-use agreements |

### Required Permissions
- `Agreement.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-applications

**Description:** "Microsoft 365 Applications — App Registrations, Service Principals & Enterprise Apps"

## Microsoft 365 Applications

Manage app registrations, service principals, credentials, and enterprise apps.

### Available Tools

| Tool | Description |
|------|-------------|
| `add_application_password` | Add a password credential (client secret) to an app |
| `create_application` | Create an app registration |
| `create_service_principal` | Create a service principal for an app |
| `delete_application` | Delete an app registration |
| `delete_service_principal` | Delete a service principal |
| `get_application` | Get a specific app registration |
| `get_service_principal` | Get a specific service principal |
| `list_applications` | List app registrations in the tenant |
| `list_service_principals` | List service principals (enterprise apps) |
| `remove_application_password` | Remove a password credential from an app |
| `update_application` | Update an app registration |
| `update_service_principal` | Update a service principal |

### Required Permissions
- `Application.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-audit

**Description:** "Microsoft 365 Audit — Directory Audits, Sign-In Logs & Provisioning Logs"

## Microsoft 365 Audit

Access directory audit logs, sign-in logs, and provisioning logs.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_directory_audit` | Get a specific directory audit entry |
| `get_sign_in_log` | Get a specific sign-in log entry |
| `list_directory_audits` | List directory audit log entries |
| `list_provisioning_logs` | List provisioning logs |
| `list_sign_in_logs` | List sign-in activity logs |

### Required Permissions
- `AuditLog.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-auth

**Description:** "Microsoft 365 Auth — Authentication & Session Management"

## Microsoft 365 Auth

Manage authentication operations including login, logout, session verification, and account listing.

### Available Tools

| Tool | Description |
|------|-------------|
| `list_accounts` | List all available Microsoft accounts |
| `login` | Authenticate with Microsoft using device code flow |
| `logout` | Log out from Microsoft account |
| `verify_login` | Check current Microsoft authentication status |

### Required Permissions
- `User.Read`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-calendar

**Description:** "Microsoft 365 Calendar — Calendar Events, Calendars & Scheduling"

## Microsoft 365 Calendar

Manage calendar events, calendars, scheduling, and meeting time suggestions.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_calendar_event` | TIP: CRITICAL: Do not try to guess the email address of the recipients |
| `create_specific_calendar_event` | TIP: CRITICAL: Do not try to guess the email address of the recipients |
| `delete_calendar_event` | delete_calendar_event: DELETE /me/events/{event-id} |
| `delete_specific_calendar_event` | delete_specific_calendar_event: DELETE /me/calendars/{calendar-id}/events/{event-id} |
| `find_meeting_times` | find_meeting_times: POST /me/findMeetingTimes |
| `get_calendar_event` | get_calendar_event: GET /me/events/{event-id} |
| `get_calendar_view` | get_calendar_view: GET /me/calendarView |
| `get_specific_calendar_event` | get_specific_calendar_event: GET /me/calendars/{calendar-id}/events/{event-id} |
| `list_calendar_events` | list_calendar_events: GET /me/events |
| `list_calendars` | list_calendars: GET /me/calendars |
| `list_specific_calendar_events` | list_specific_calendar_events: GET /me/calendars/{calendar-id}/events |
| `update_calendar_event` | TIP: CRITICAL: Do not try to guess the email address of the recipients |
| `update_specific_calendar_event` | TIP: CRITICAL: Do not try to guess the email address of the recipients |

### Required Permissions
- `Calendars.ReadWrite`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-chat

**Description:** "Microsoft 365 Chat — Chats, Messages, Replies & Group Conversations"

## Microsoft 365 Chat

Manage chats, messages, replies, and group conversations.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_chat` | get_chat: GET /chats/{chat-id} |
| `get_chat_message` | get_chat_message: GET /chats/{chat-id}/messages/{chatMessage-id} |
| `list_chat_message_replies` | list_chat_message_replies: GET /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `list_chat_messages` | list_chat_messages: GET /chats/{chat-id}/messages |
| `list_chats` | list_chats: GET /me/chats |
| `list_group_conversations` | List conversations in a Microsoft 365 group |
| `reply_to_chat_message` | reply_to_chat_message: POST /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `send_chat_message` | send_chat_message: POST /chats/{chat-id}/messages |

### Required Permissions
- `Chat.Read, ChatMessage.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-communications

**Description:** "Microsoft 365 Communications — Online Meetings, Call Records & Presence"

## Microsoft 365 Communications

Manage online meetings, call records, and user presence information.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_online_meeting` | Create a new online meeting |
| `delete_online_meeting` | Delete an online meeting |
| `get_call_record` | Get a specific call record by ID |
| `get_my_presence` | Get current user |
| `get_online_meeting` | Get a specific online meeting by ID |
| `get_presence` | Get presence for a specific user by user ID |
| `list_call_records` | List call records |
| `list_online_meetings` | List online meetings for the current user |
| `list_presences` | List presence information for multiple users |
| `update_online_meeting` | Update an existing online meeting |

### Required Permissions
- `OnlineMeetings.ReadWrite, CallRecords.Read.All, Presence.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-connections

**Description:** "Microsoft 365 Connections — Microsoft Search External Connections"

## Microsoft 365 Connections

Manage Microsoft Search external connections for custom data ingestion.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_external_connection` | Create an external connection for Microsoft Search |
| `delete_external_connection` | Delete an external connection |
| `get_external_connection` | Get a specific external connection |
| `list_external_connections` | List Microsoft Search external connections |

### Required Permissions
- `ExternalConnection.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-contacts

**Description:** "Microsoft 365 Contacts — Outlook Contact Management"

## Microsoft 365 Contacts

Manage Outlook contacts — create, read, update, and delete.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_outlook_contact` | create_outlook_contact: POST /me/contacts |
| `delete_outlook_contact` | delete_outlook_contact: DELETE /me/contacts/{contact-id} |
| `get_outlook_contact` | get_outlook_contact: GET /me/contacts/{contact-id} |
| `list_outlook_contacts` | list_outlook_contacts: GET /me/contacts |
| `update_outlook_contact` | update_outlook_contact: PATCH /me/contacts/{contact-id} |

### Required Permissions
- `Contacts.ReadWrite`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-devices

**Description:** "Microsoft 365 Devices — Directory Devices, Intune Managed Devices & Compliance"

## Microsoft 365 Devices

Manage directory devices, Intune managed devices, compliance policies, and device configurations.

### Available Tools

| Tool | Description |
|------|-------------|
| `delete_device` | Delete a device |
| `get_device` | Get a specific device |
| `get_managed_device` | Get a specific managed device |
| `list_device_compliance_policies` | List device compliance policies |
| `list_device_configurations` | List device configuration profiles |
| `list_devices` | List devices registered in the directory |
| `list_managed_devices` | List Intune managed devices |
| `retire_managed_device` | Retire a managed device (remove company data) |
| `wipe_managed_device` | Wipe a managed device (factory reset) |

### Required Permissions
- `Device.ReadWrite.All, DeviceManagementManagedDevices.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-directory

**Description:** "Microsoft 365 Directory — Directory Objects, Roles, Role Definitions & Role Assignments"

## Microsoft 365 Directory

Manage directory objects, roles, deleted items, role definitions, and role assignments.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_role_assignment` | Create a new RBAC role assignment |
| `get_directory_object` | Get a specific directory object |
| `get_directory_role` | Get a specific activated directory role |
| `get_role_assignment` | Get a specific RBAC role assignment |
| `get_role_definition` | Get a specific RBAC role definition |
| `list_deleted_items` | List recently deleted directory items (users, groups, apps) |
| `list_directory_objects` | List directory objects |
| `list_directory_role_templates` | List all directory role templates (built-in role definitions) |
| `list_directory_roles` | List activated directory roles |
| `list_role_assignments` | List RBAC directory role assignments |
| `list_role_definitions` | List RBAC directory role definitions |
| `restore_deleted_item` | Restore a recently deleted directory item |

### Required Permissions
- `Directory.ReadWrite.All, RoleManagement.ReadWrite.Directory`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-domains

**Description:** "Microsoft 365 Domains — Tenant Domain Management & DNS Configuration"

## Microsoft 365 Domains

Manage tenant domains including adding, verifying, deleting, and viewing DNS configuration records.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_domain` | Add a domain to the tenant |
| `delete_domain` | Delete a domain from the tenant |
| `get_domain` | Get properties of a specific domain |
| `list_domain_service_configuration_records` | List DNS records required by the domain for Microsoft services |
| `list_domains` | List domains associated with the tenant |
| `verify_domain` | Verify ownership of a domain |

### Required Permissions
- `Domain.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-education

**Description:** "Microsoft 365 Education — Education Classes, Schools, Users & Assignments"

## Microsoft 365 Education

Manage education classes, schools, users, and assignments.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_education_class` | Get a specific education class |
| `get_education_school` | Get a specific education school |
| `list_education_assignments` | List assignments for an education class |
| `list_education_classes` | List education classes |
| `list_education_schools` | List education schools |
| `list_education_users` | List education users |

### Required Permissions
- `EduAdministration.ReadWrite`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-employee_experience

**Description:** "Microsoft 365 Employee Experience — Learning Providers & Course Activities"

## Microsoft 365 Employee Experience

Manage learning providers and course activities for employee development.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_learning_provider` | Get a specific learning provider |
| `list_learning_course_activities` | List learning course activities for the current user |
| `list_learning_providers` | List learning providers |

### Required Permissions
- `LearningContent.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-files

**Description:** "Microsoft 365 Files — OneDrive, Excel, OneNote & SharePoint Files"

## Microsoft 365 Files

Manage OneDrive files, Excel workbooks, OneNote notebooks, and SharePoint file operations.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_excel_chart` | create_excel_chart: POST /drives/{drive-id}/items/{driveItem-id}/workbook/worksheets/{workbookWorksheet-id}/charts/add |
| `delete_onedrive_file` | delete_onedrive_file: DELETE /drives/{drive-id}/items/{driveItem-id} |
| `download_onedrive_file_content` | download_onedrive_file_content: GET /drives/{drive-id}/items/{driveItem-id}/content |
| `format_excel_range` | format_excel_range: PATCH /drives/{drive-id}/items/{driveItem-id}/workbook/worksheets/{workbookWorksheet-id}/range()/for |
| `get_drive_root_item` | get_drive_root_item: GET /drives/{drive-id}/root |
| `get_excel_table` | get_excel_table: GET /drives/{drive-id}/items/{item-id}/workbook/tables/{table-id} |
| `get_excel_workbook` | get_excel_workbook: GET /drives/{drive-id}/items/{item-id}/workbook |
| `get_excel_worksheet` | get_excel_worksheet: GET /drives/{drive-id}/items/{item-id}/workbook/worksheets/{worksheet-id} |
| `get_excel_range` | get_excel_range: GET /drives/{drive-id}/items/{driveItem-id}/workbook/worksheets/{worksheet-id}/range() |
| `get_root_folder` | get_root_folder: GET /drives/{drive-id}/root |
| `get_sharepoint_site_list_item` | get_sharepoint_site_list_item: GET /sites/{site-id}/lists/{list-id}/items/{listItem-id} |
| `get_site_drive_by_id` | get_site_drive_by_id: GET /sites/{site-id}/drives/{drive-id} |
| `get_site_item` | get_site_item: GET /sites/{site-id}/items/{baseItem-id} |
| `get_site_list` | Get a specific SharePoint site list |
| `list_calendar_events` | list_calendar_events: GET /me/events |
| `list_calendars` | list_calendars: GET /me/calendars |
| `list_channel_messages` | list_channel_messages: GET /teams/{team-id}/channels/{channel-id}/messages |
| `list_chat_message_replies` | list_chat_message_replies: GET /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `list_chat_messages` | list_chat_messages: GET /chats/{chat-id}/messages |
| `list_chats` | list_chats: GET /me/chats |
| `list_drives` | list_drives: GET /me/drives |
| `list_excel_tables` | List Excel tables in a workbook |
| `list_excel_worksheets` | list_excel_worksheets: GET /drives/{drive-id}/items/{driveItem-id}/workbook/worksheets |
| `list_folder_files` | list_folder_files: GET /drives/{drive-id}/items/{driveItem-id}/children |
| `list_group_drives` | List drives (document libraries) of a group |
| `list_joined_teams` | list_joined_teams: GET /me/joinedTeams |
| `list_mail_attachments` | list_mail_attachments: GET /me/messages/{message-id}/attachments |
| `list_mail_folder_messages` | list_mail_folder_messages: GET /me/mailFolders/{mailFolder-id}/messages |
| `list_mail_messages` | list_mail_messages: GET /me/messages |
| `list_mail_folders` | list_mail_folders: GET /me/mailFolders |
| `list_onenote_notebook_sections` | list_onenote_notebook_sections: GET /me/onenote/notebooks/{notebook-id}/sections |
| `list_onenote_notebooks` | list_onenote_notebooks: GET /me/onenote/notebooks |
| `list_onenote_section_pages` | list_onenote_section_pages: GET /me/onenote/sections/{onenoteSection-id}/pages |
| `list_outlook_contacts` | list_outlook_contacts: GET /me/contacts |
| `list_shared_mailbox_folder_messages` | list_shared_mailbox_folder_messages: GET /users/{user-id}/mailFolders/{mailFolder-id}/messages |
| `list_shared_mailbox_messages` | list_shared_mailbox_messages: GET /users/{user-id}/messages |
| `list_plan_tasks` | list_plan_tasks: GET /planner/plans/{plannerPlan-id}/tasks |
| `list_planner_tasks` | list_planner_tasks: GET /me/planner/tasks |
| `list_sharepoint_site_list_items` | List items in a SharePoint site list |
| `list_site_drives` | list_site_drives: GET /sites/{site-id}/drives |
| `list_site_items` | list_site_items: GET /sites/{site-id}/items |
| `list_site_lists` | List lists for a SharePoint site |
| `list_specific_calendar_events` | list_specific_calendar_events: GET /me/calendars/{calendar-id}/events |
| `list_team_channels` | list_team_channels: GET /teams/{team-id}/channels |
| `list_team_members` | list_team_members: GET /teams/{team-id}/members |
| `list_todo_task_lists` | list_todo_task_lists: GET /me/todo/lists |
| `list_todo_tasks` | list_todo_tasks: GET /me/todo/lists/{todoTaskList-id}/tasks |
| `list_users` | list_users: GET /users |
| `sort_excel_range` | sort_excel_range: PATCH /drives/{drive-id}/items/{driveItem-id}/workbook/worksheets/{workbookWorksheet-id}/range()/sort |
| `upload_file_content` | upload_file_content: PUT /drives/{drive-id}/items/{driveItem-id}/content |

### Required Permissions
- `Files.ReadWrite, Sites.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-groups

**Description:** "Microsoft 365 Groups — Groups, Membership, Ownership & Group Conversations"

## Microsoft 365 Groups

Manage Microsoft 365 groups, security groups, membership, ownership, and group conversations.

### Available Tools

| Tool | Description |
|------|-------------|
| `add_group_member` | Add a member to a group |
| `create_group` | Create a new Microsoft 365 group or security group |
| `delete_group` | Delete a group |
| `get_group` | Get properties and relationships of a group object |
| `list_group_conversations` | List conversations in a Microsoft 365 group |
| `list_group_drives` | List drives (document libraries) of a group |
| `list_group_members` | Get a list of the group |
| `list_group_owners` | Get owners of a group |
| `list_groups` | List all Microsoft 365 groups and security groups in the organization |
| `remove_group_member` | Remove a member from a group |
| `update_group` | Update properties of a group object |

### Required Permissions
- `Group.ReadWrite.All, GroupMember.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-identity

**Description:** "Microsoft 365 Identity — Invitations, Conditional Access, Access Reviews & Lifecycle Workflows"

## Microsoft 365 Identity

Manage identity operations including invitations, conditional access, access reviews, entitlement access packages, and lifecycle workflows.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_conditional_access_policy` | Create a conditional access policy |
| `create_invitation` | Create an invitation for an external / guest user |
| `delete_conditional_access_policy` | Delete a conditional access policy |
| `get_access_review` | Get a specific access review definition |
| `get_conditional_access_policy` | Get a specific conditional access policy |
| `list_access_reviews` | List access review schedule definitions |
| `list_conditional_access_policies` | List conditional access policies |
| `list_entitlement_access_packages` | List entitlement management access packages |
| `list_lifecycle_workflows` | List lifecycle management workflows |
| `update_conditional_access_policy` | Update a conditional access policy |

### Required Permissions
- `User.Invite.All, Policy.ReadWrite.ConditionalAccess, AccessReview.Read.All, EntitlementManagement.Read.All, LifecycleWorkflows.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-mail

**Description:** "Microsoft 365 Mail — Email Messages, Folders, Attachments, Drafts & Shared Mailboxes"

## Microsoft 365 Mail

Manage email messages, folders, attachments, shared mailboxes, drafts, and send mail.

### Available Tools

| Tool | Description |
|------|-------------|
| `add_mail_attachment` | add_mail_attachment: POST /me/messages/{message-id}/attachments |
| `create_draft_email` | create_draft_email: POST /me/messages |
| `delete_mail_attachment` | delete_mail_attachment: DELETE /me/messages/{message-id}/attachments/{attachment-id} |
| `delete_mail_message` | delete_mail_message: DELETE /me/messages/{message-id} |
| `get_channel_message` | get_channel_message: GET /teams/{team-id}/channels/{channel-id}/messages/{chatMessage-id} |
| `get_chat_message` | get_chat_message: GET /chats/{chat-id}/messages/{chatMessage-id} |
| `get_mail_attachment` | get_mail_attachment: GET /me/messages/{message-id}/attachments/{attachment-id} |
| `get_mail_message` | get_mail_message: GET /me/messages/{message-id} |
| `get_root_folder` | get_root_folder: GET /drives/{drive-id}/root |
| `get_shared_mailbox_message` | get_shared_mailbox_message: GET /users/{user-id}/messages/{message-id} |
| `list_channel_messages` | list_channel_messages: GET /teams/{team-id}/channels/{channel-id}/messages |
| `list_chat_message_replies` | list_chat_message_replies: GET /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `list_chat_messages` | list_chat_messages: GET /chats/{chat-id}/messages |
| `list_folder_files` | list_folder_files: GET /drives/{drive-id}/items/{driveItem-id}/children |
| `list_mail_attachments` | list_mail_attachments: GET /me/messages/{message-id}/attachments |
| `list_mail_folder_messages` | list_mail_folder_messages: GET /me/mailFolders/{mailFolder-id}/messages |
| `list_mail_messages` | list_mail_messages: GET /me/messages |
| `list_mail_folders` | list_mail_folders: GET /me/mailFolders |
| `list_shared_mailbox_folder_messages` | list_shared_mailbox_folder_messages: GET /users/{user-id}/mailFolders/{mailFolder-id}/messages |
| `list_shared_mailbox_messages` | list_shared_mailbox_messages: GET /users/{user-id}/messages |
| `move_mail_message` | move_mail_message: POST /me/messages/{message-id}/move |
| `reply_to_chat_message` | reply_to_chat_message: POST /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `send_channel_message` | send_channel_message: POST /teams/{team-id}/channels/{channel-id}/messages |
| `send_chat_message` | send_chat_message: POST /chats/{chat-id}/messages |
| `send_mail` | TIP: CRITICAL: Do not try to guess the email address of the recipients |
| `send_shared_mailbox_mail` | TIP: CRITICAL: Do not try to guess the email address of the recipients |
| `update_mail_message` | update_mail_message: PATCH /me/messages/{message-id} |

### Required Permissions
- `Mail.ReadWrite, Mail.Send`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-meta

**Description:** "Microsoft 365 Meta — Tool Discovery & Search"

## Microsoft 365 Meta

Discover and search available MCP tools.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_tools` | Search available Microsoft Graph API tools |

### Required Permissions
- `None`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-notes

**Description:** "Microsoft 365 Notes — OneNote Notebooks, Sections & Pages"

## Microsoft 365 Notes

Manage OneNote notebooks, sections, and pages.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_onenote_page` | create_onenote_page: POST /me/onenote/pages |
| `get_onenote_page_content` | get_onenote_page_content: GET /me/onenote/pages/{onenotePage-id}/content |
| `list_onenote_notebook_sections` | list_onenote_notebook_sections: GET /me/onenote/notebooks/{notebook-id}/sections |
| `list_onenote_notebooks` | list_onenote_notebooks: GET /me/onenote/notebooks |
| `list_onenote_section_pages` | list_onenote_section_pages: GET /me/onenote/sections/{onenoteSection-id}/pages |

### Required Permissions
- `Notes.ReadWrite`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-organization

**Description:** "Microsoft 365 Organization — Organization Profile, Branding & Configuration"

## Microsoft 365 Organization

Manage organization profile, branding, and configuration.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_org_branding` | Get organization branding properties (sign-in page customization) |
| `get_organization` | Get a specific organization by ID |
| `list_organization` | Get the properties and relationships of the currently authenticated organization |
| `update_org_branding` | Update organization branding properties |
| `update_organization` | Update organization properties |

### Required Permissions
- `Organization.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-places

**Description:** "Microsoft 365 Places — Rooms & Room Lists"

## Microsoft 365 Places

Manage rooms and room lists.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_place` | Get a specific place (room or room list) |
| `list_room_lists` | List room lists |
| `list_rooms` | List conference rooms |
| `update_place` | Update a place (room) |

### Required Permissions
- `Place.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-policies

**Description:** "Microsoft 365 Policies — Authorization, Token & Permission Grant Policies"

## Microsoft 365 Policies

Manage authorization policies, token policies, permission grant policies, and admin consent policies.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_admin_consent_policy` | Get the admin consent request policy |
| `get_authorization_policy` | Get the tenant authorization policy |
| `list_permission_grant_policies` | List permission grant policies |
| `list_token_issuance_policies` | List token issuance policies |
| `list_token_lifetime_policies` | List token lifetime policies |

### Required Permissions
- `Policy.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-print

**Description:** "Microsoft 365 Print — Printers, Print Jobs & Print Shares"

## Microsoft 365 Print

Manage printers, print jobs, and print shares.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_print_job` | Create a print job |
| `get_printer` | Get a specific printer |
| `list_print_jobs` | List print jobs for a printer |
| `list_print_shares` | List printer shares |
| `list_printers` | List printers registered in the tenant |

### Required Permissions
- `PrintJob.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-privacy

**Description:** "Microsoft 365 Privacy — Subject Rights Requests (GDPR/CCPA)"

## Microsoft 365 Privacy

Manage subject rights requests for GDPR/CCPA compliance.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_subject_rights_request` | Create a subject rights request |
| `get_subject_rights_request` | Get a specific subject rights request |
| `list_subject_rights_requests` | List subject rights requests (GDPR/CCPA) |

### Required Permissions
- `SubjectRightsRequest.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-reports

**Description:** "Microsoft 365 Reports — Usage & Activity Reports"

## Microsoft 365 Reports

Generate usage and activity reports for email, mailbox, Office 365, SharePoint, Teams, and OneDrive.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_email_activity_report` | Get email activity user detail report |
| `get_mailbox_usage_report` | Get mailbox usage detail report |
| `get_office365_active_users` | Get Office 365 active user detail report |
| `get_onedrive_usage_report` | Get OneDrive usage account detail report |
| `get_sharepoint_activity_report` | Get SharePoint activity user detail report |
| `get_teams_user_activity` | Get Teams user activity detail report |

### Required Permissions
- `Reports.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-search

**Description:** "Microsoft 365 Search — Microsoft Graph Search Queries"

## Microsoft 365 Search

Execute Microsoft Graph search queries.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_query` | search_query: POST /search/query |

### Required Permissions
- `Files.Read.All, Sites.Read.All, Mail.Read`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-security

**Description:** "Microsoft 365 Security — Alerts, Incidents, Threat Intelligence & Identity Protection"

## Microsoft 365 Security

Manage security alerts, incidents, secure scores, threat intelligence, identity protection, and information protection.

### Available Tools

| Tool | Description |
|------|-------------|
| `dismiss_risky_user` | Dismiss a risky user (mark as safe) |
| `get_risk_detection` | Get a specific risk detection |
| `get_risky_user` | Get a specific risky user |
| `get_security_alert` | Get a specific security alert by ID |
| `get_security_incident` | Get a specific security incident by ID |
| `get_sensitivity_label` | Get a specific sensitivity label |
| `get_threat_intelligence_host` | Get a specific threat intelligence host |
| `list_risk_detections` | List risk detections (sign-in anomalies, leaked credentials, etc.) |
| `list_risky_users` | List users flagged as risky |
| `list_secure_scores` | List tenant secure scores over time |
| `list_security_alerts` | List security alerts |
| `list_security_incidents` | List security incidents |
| `list_sensitivity_labels` | List sensitivity labels |
| `list_threat_intelligence_hosts` | List threat intelligence hosts |
| `run_hunting_query` | Run an advanced hunting query using Kusto Query Language (KQL) |
| `update_security_alert` | Update a security alert |
| `update_security_incident` | Update a security incident |

### Required Permissions
- `SecurityEvents.ReadWrite.All, SecurityIncident.ReadWrite.All, ThreatHunting.Read.All, IdentityRiskEvent.Read.All, IdentityRiskyUser.ReadWrite.All, InformationProtectionPolicy.Read`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-sites

**Description:** "Microsoft 365 Sites — SharePoint Sites, Lists, Drives & Items"

## Microsoft 365 Sites

Manage SharePoint sites, site lists, site drives, site items, and site administration.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_admin_sharepoint` | Get SharePoint admin settings for the tenant |
| `get_sharepoint_site_by_path` | get_sharepoint_site_by_path: GET /sites/{hostname}:/{server-relative-path} |
| `get_sharepoint_site_list_item` | get_sharepoint_site_list_item: GET /sites/{site-id}/lists/{list-id}/items/{listItem-id} |
| `get_sharepoint_sites_delta` | get_sharepoint_sites_delta: GET /sites/delta() |
| `get_site` | get_site: GET /sites/{site-id} |
| `get_site_drive_by_id` | get_site_drive_by_id: GET /sites/{site-id}/drives/{drive-id} |
| `get_site_item` | get_site_item: GET /sites/{site-id}/items/{baseItem-id} |
| `get_site_list` | Get a specific SharePoint site list |
| `list_sharepoint_site_list_items` | List items in a SharePoint site list |
| `list_site_drives` | list_site_drives: GET /sites/{site-id}/drives |
| `list_site_items` | list_site_items: GET /sites/{site-id}/items |
| `list_site_lists` | List lists for a SharePoint site |
| `list_sites` | list_sites: GET /sites |
| `update_admin_sharepoint` | Update SharePoint admin settings for the tenant |

### Required Permissions
- `Sites.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-solutions

**Description:** "Microsoft 365 Solutions — Booking Businesses, Appointments & Virtual Events"

## Microsoft 365 Solutions

Manage booking businesses, appointments, and virtual events.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_booking_appointment` | Create a booking appointment |
| `get_booking_business` | Get a specific booking business |
| `list_booking_appointments` | List appointments for a booking business |
| `list_booking_businesses` | List booking businesses |
| `list_virtual_events` | List virtual event townhalls |

### Required Permissions
- `Bookings.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-storage

**Description:** "Microsoft 365 Storage — File Storage Containers"

## Microsoft 365 Storage

Manage file storage containers.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_file_storage_container` | Create a file storage container |
| `get_file_storage_container` | Get a specific file storage container |
| `list_file_storage_containers` | List file storage containers |

### Required Permissions
- `FileStorageContainer.Selected`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-subscriptions

**Description:** "Microsoft 365 Subscriptions — Webhook Subscriptions for Change Notifications"

## Microsoft 365 Subscriptions

Manage webhook subscriptions for change notifications.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_subscription` | Create a webhook subscription for change notifications |
| `delete_subscription` | Delete a webhook subscription |
| `get_subscription` | Get a specific subscription |
| `list_subscriptions` | List active webhook subscriptions for change notifications |
| `update_subscription` | Renew a subscription by extending its expiration time |

### Required Permissions
- `Subscription varies by resource`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-tasks

**Description:** "Microsoft 365 Tasks — Planner Tasks & To-Do Task Lists"

## Microsoft 365 Tasks

Manage Planner tasks, plans, To-Do task lists, and task operations.

### Available Tools

| Tool | Description |
|------|-------------|
| `create_planner_task` | create_planner_task: POST /planner/tasks |
| `create_todo_task` | create_todo_task: POST /me/todo/lists/{todoTaskList-id}/tasks |
| `delete_todo_task` | delete_todo_task: DELETE /me/todo/lists/{todoTaskList-id}/tasks/{todoTask-id} |
| `get_planner_plan` | get_planner_plan: GET /planner/plans/{plannerPlan-id} |
| `get_planner_task` | get_planner_task: GET /planner/tasks/{plannerTask-id} |
| `get_todo_task` | get_todo_task: GET /me/todo/lists/{todoTaskList-id}/tasks/{todoTask-id} |
| `list_plan_tasks` | list_plan_tasks: GET /planner/plans/{plannerPlan-id}/tasks |
| `list_planner_tasks` | list_planner_tasks: GET /me/planner/tasks |
| `list_todo_task_lists` | list_todo_task_lists: GET /me/todo/lists |
| `list_todo_tasks` | list_todo_tasks: GET /me/todo/lists/{todoTaskList-id}/tasks |
| `update_planner_task` | update_planner_task: PATCH /planner/tasks/{plannerTask-id} |
| `update_planner_task_details` | update_planner_task_details: PATCH /planner/tasks/{plannerTask-id}/details |
| `update_todo_task` | update_todo_task: PATCH /me/todo/lists/{todoTaskList-id}/tasks/{todoTask-id} |

### Required Permissions
- `Tasks.ReadWrite, Group.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-teams

**Description:** "Microsoft 365 Teams — Teams, Channels, Messages & Membership"

## Microsoft 365 Teams

Manage teams, channels, channel messages, and team membership.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_channel_message` | get_channel_message: GET /teams/{team-id}/channels/{channel-id}/messages/{chatMessage-id} |
| `get_team` | get_team: GET /teams/{team-id} |
| `get_team_channel` | get_team_channel: GET /teams/{team-id}/channels/{channel-id} |
| `list_channel_messages` | list_channel_messages: GET /teams/{team-id}/channels/{channel-id}/messages |
| `list_joined_teams` | list_joined_teams: GET /me/joinedTeams |
| `list_team_channels` | list_team_channels: GET /teams/{team-id}/channels |
| `list_team_members` | list_team_members: GET /teams/{team-id}/members |
| `send_channel_message` | send_channel_message: POST /teams/{team-id}/channels/{channel-id}/messages |

### Required Permissions
- `Team.ReadBasic.All, Channel.ReadBasic.All, ChannelMessage.Read.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.

### microsoft-user

**Description:** "Microsoft 365 User — User Profile, Mail Operations, Meetings & Group Membership"

## Microsoft 365 User

Manage user profiles, mail operations, meetings, and group membership.

### Available Tools

| Tool | Description |
|------|-------------|
| `add_group_member` | Add a member to a group |
| `add_mail_attachment` | add_mail_attachment: POST /me/messages/{message-id}/attachments |
| `delete_mail_attachment` | delete_mail_attachment: DELETE /me/messages/{message-id}/attachments/{attachment-id} |
| `delete_mail_message` | delete_mail_message: DELETE /me/messages/{message-id} |
| `find_meeting_times` | find_meeting_times: POST /me/findMeetingTimes |
| `get_channel_message` | get_channel_message: GET /teams/{team-id}/channels/{channel-id}/messages/{chatMessage-id} |
| `get_chat_message` | get_chat_message: GET /chats/{chat-id}/messages/{chatMessage-id} |
| `get_current_user` | get_current_user: GET /me |
| `get_mail_attachment` | get_mail_attachment: GET /me/messages/{message-id}/attachments/{attachment-id} |
| `get_mail_message` | get_mail_message: GET /me/messages/{message-id} |
| `get_me` | get_me: GET /me |
| `get_shared_mailbox_message` | get_shared_mailbox_message: GET /users/{user-id}/messages/{message-id} |
| `list_channel_messages` | list_channel_messages: GET /teams/{team-id}/channels/{channel-id}/messages |
| `list_chat_message_replies` | list_chat_message_replies: GET /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `list_chat_messages` | list_chat_messages: GET /chats/{chat-id}/messages |
| `list_group_members` | Get a list of the group |
| `list_group_owners` | Get owners of a group |
| `list_mail_attachments` | list_mail_attachments: GET /me/messages/{message-id}/attachments |
| `list_mail_folder_messages` | list_mail_folder_messages: GET /me/mailFolders/{mailFolder-id}/messages |
| `list_mail_messages` | list_mail_messages: GET /me/messages |
| `list_shared_mailbox_folder_messages` | list_shared_mailbox_folder_messages: GET /users/{user-id}/mailFolders/{mailFolder-id}/messages |
| `list_shared_mailbox_messages` | list_shared_mailbox_messages: GET /users/{user-id}/messages |
| `list_team_members` | list_team_members: GET /teams/{team-id}/members |
| `list_users` | list_users: GET /users |
| `move_mail_message` | move_mail_message: POST /me/messages/{message-id}/move |
| `remove_group_member` | Remove a member from a group |
| `reply_to_chat_message` | reply_to_chat_message: POST /chats/{chat-id}/messages/{chatMessage-id}/replies |
| `send_channel_message` | send_channel_message: POST /teams/{team-id}/channels/{channel-id}/messages |
| `send_chat_message` | send_chat_message: POST /chats/{chat-id}/messages |
| `update_mail_message` | update_mail_message: PATCH /me/messages/{message-id} |

### Required Permissions
- `User.Read, Mail.ReadWrite, Chat.Read, Group.ReadWrite.All`

### Error Handling
All tools return `{"error": "<message>"}` on failure.
