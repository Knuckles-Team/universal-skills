# Microsoft Agent Reference

**Project:** `microsoft-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MICROSOFT_CLIENT_ID` | Required for authentication |
| `MICROSOFT_CLIENT_SECRET` | Required for authentication |
| `MICROSOFT_TENANT_ID` | Required for authentication |

## Available Tool Tags (37)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ADMINTOOL` | `True` | get_admin_sharepoint, get_delegated_admin_relationship, get_service_health, get_service_health_issue, get_service_update_message, list_delegated_admin_relationships, list_service_health, list_service_health_issues, update_admin_sharepoint |
| `AGREEMENTSTOOL` | `True` | create_agreement, delete_agreement, get_agreement, list_agreements |
| `APPLICATIONSTOOL` | `True` | create_application, create_service_principal, delete_application, delete_service_principal, get_application, get_service_principal, list_applications, remove_application_password, update_application, update_service_principal |
| `AUDITTOOL` | `True` | get_directory_audit, get_sign_in_log, list_provisioning_logs, list_sign_in_logs |
| `AUTHTOOL` | `True` | list_accounts, login, logout, verify_login |
| `CALENDARTOOL` | `True` | create_calendar_event, create_specific_calendar_event, delete_calendar_event, delete_specific_calendar_event, find_meeting_times, get_calendar_event, get_calendar_view, get_specific_calendar_event, list_calendar_events, list_calendars, list_specific_calendar_events, update_calendar_event, update_specific_calendar_event |
| `CHATTOOL` | `True` | get_chat |
| `COMMUNICATIONSTOOL` | `True` | create_online_meeting, delete_online_meeting, get_call_record, get_my_presence, get_online_meeting, list_call_records, list_online_meetings, list_presences, update_online_meeting |
| `CONNECTIONSTOOL` | `True` | create_external_connection, delete_external_connection, get_external_connection, list_external_connections |
| `CONTACTSTOOL` | `True` | create_outlook_contact, delete_outlook_contact, get_outlook_contact, update_outlook_contact |
| `DEVICESTOOL` | `True` | delete_device, get_device, get_managed_device, list_device_compliance_policies, list_device_configurations, list_devices, list_managed_devices |
| `DIRECTORYTOOL` | `True` | create_role_assignment, get_directory_object, get_directory_role, get_role_assignment, get_role_definition, list_directory_objects, list_directory_roles, list_role_assignments, list_role_definitions, restore_deleted_item |
| `DOMAINSTOOL` | `True` | create_domain, delete_domain, get_domain, list_domain_service_configuration_records, list_domains, verify_domain |
| `EDUCATIONTOOL` | `True` | get_education_class, get_education_school, list_education_assignments, list_education_classes, list_education_schools, list_education_users |
| `EMPLOYEE_EXPERIENCETOOL` | `True` | get_learning_provider, list_learning_course_activities, list_learning_providers |
| `FILESTOOL` | `True` | create_excel_chart, delete_onedrive_file, download_onedrive_file_content, get_drive_root_item, get_excel_table, get_excel_workbook, get_excel_worksheet, get_sharepoint_site_list_item, get_site_drive_by_id, get_site_item, get_site_list, list_chats, list_drives, list_excel_tables, list_excel_worksheets, list_joined_teams, list_onenote_notebook_sections, list_onenote_notebooks, list_onenote_section_pages, list_outlook_contacts, list_plan_tasks, list_planner_tasks, list_sharepoint_site_list_items, list_site_drives, list_site_items, list_site_lists, list_team_channels, list_team_members, list_todo_task_lists, list_todo_tasks, upload_file_content |
| `GROUPSTOOL` | `True` | add_group_member, create_group, delete_group, get_group, list_group_conversations, list_group_members, list_group_owners, list_groups, remove_group_member, update_group |
| `IDENTITYTOOL` | `True` | create_conditional_access_policy, create_invitation, delete_conditional_access_policy, get_access_review, get_conditional_access_policy, list_access_reviews, list_conditional_access_policies, list_entitlement_access_packages, list_lifecycle_workflows, update_conditional_access_policy |
| `MAILTOOL` | `True` | add_mail_attachment, create_draft_email, delete_mail_attachment, delete_mail_message, get_channel_message, get_chat_message, get_mail_attachment, get_mail_message, get_root_folder, get_shared_mailbox_message, list_channel_messages, list_chat_message_replies, list_chat_messages, list_folder_files, list_mail_attachments, list_mail_folders, move_mail_message, reply_to_chat_message, send_channel_message, send_chat_message, send_mail, send_shared_mailbox_mail, update_mail_message |
| `METATOOL` | `True` | search_tools |
| `MISCTOOL` | `True` | add_application_password, dismiss_risky_user, format_excel_range, get_excel_range, get_org_branding, get_place, get_presence, get_sharepoint_site_by_path, get_sharepoint_sites_delta, list_deleted_items, list_directory_audits, list_directory_role_templates, list_group_drives, list_mail_folder_messages, list_mail_messages, list_risk_detections, list_service_principals, list_service_update_messages, list_shared_mailbox_folder_messages, list_shared_mailbox_messages, list_subject_rights_requests, list_users, retire_managed_device, run_hunting_query, sort_excel_range, update_place, wipe_managed_device |
| `NOTESTOOL` | `True` | create_onenote_page, get_onenote_page_content |
| `ORGANIZATIONTOOL` | `True` | get_organization, list_organization, update_org_branding, update_organization |
| `PLACESTOOL` | `True` | list_room_lists, list_rooms |
| `POLICIESTOOL` | `True` | get_admin_consent_policy, get_authorization_policy, list_permission_grant_policies, list_token_issuance_policies, list_token_lifetime_policies |
| `PRINTTOOL` | `True` | create_print_job, get_printer, list_print_jobs, list_print_shares, list_printers |
| `PRIVACYTOOL` | `True` | create_subject_rights_request, get_subject_rights_request |
| `REPORTSTOOL` | `True` | get_email_activity_report, get_mailbox_usage_report, get_office365_active_users, get_onedrive_usage_report, get_sharepoint_activity_report, get_teams_user_activity |
| `SEARCHTOOL` | `True` | search_query |
| `SECURITYTOOL` | `True` | get_risk_detection, get_risky_user, get_security_alert, get_security_incident, get_sensitivity_label, get_threat_intelligence_host, list_risky_users, list_secure_scores, list_security_alerts, list_security_incidents, list_sensitivity_labels, list_threat_intelligence_hosts, update_security_alert, update_security_incident |
| `SITESTOOL` | `True` | get_site, list_sites |
| `SOLUTIONSTOOL` | `True` | create_booking_appointment, get_booking_business, list_booking_appointments, list_booking_businesses, list_virtual_events |
| `STORAGETOOL` | `True` | create_file_storage_container, get_file_storage_container, list_file_storage_containers |
| `SUBSCRIPTIONSTOOL` | `True` | create_subscription, delete_subscription, get_subscription, list_subscriptions, update_subscription |
| `TASKSTOOL` | `True` | create_planner_task, create_todo_task, delete_todo_task, get_planner_plan, get_planner_task, get_todo_task, update_planner_task, update_planner_task_details, update_todo_task |
| `TEAMSTOOL` | `True` | get_team, get_team_channel |
| `USERTOOL` | `True` | get_current_user, get_me |

## Stdio Connection (Default)

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
        "AUTHTOOL": "${ AUTHTOOL:-True }",
        "GROUPSTOOL": "${ GROUPSTOOL:-True }",
        "AGREEMENTSTOOL": "${ AGREEMENTSTOOL:-True }",
        "FILESTOOL": "${ FILESTOOL:-True }",
        "NOTESTOOL": "${ NOTESTOOL:-True }",
        "ORGANIZATIONTOOL": "${ ORGANIZATIONTOOL:-True }",
        "AUDITTOOL": "${ AUDITTOOL:-True }",
        "PLACESTOOL": "${ PLACESTOOL:-True }",
        "PRINTTOOL": "${ PRINTTOOL:-True }",
        "TASKSTOOL": "${ TASKSTOOL:-True }",
        "SEARCHTOOL": "${ SEARCHTOOL:-True }",
        "EMPLOYEE_EXPERIENCETOOL": "${ EMPLOYEE_EXPERIENCETOOL:-True }",
        "METATOOL": "${ METATOOL:-True }",
        "CHATTOOL": "${ CHATTOOL:-True }",
        "SITESTOOL": "${ SITESTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "DIRECTORYTOOL": "${ DIRECTORYTOOL:-True }",
        "POLICIESTOOL": "${ POLICIESTOOL:-True }",
        "ADMINTOOL": "${ ADMINTOOL:-True }",
        "TEAMSTOOL": "${ TEAMSTOOL:-True }",
        "APPLICATIONSTOOL": "${ APPLICATIONSTOOL:-True }",
        "CALENDARTOOL": "${ CALENDARTOOL:-True }",
        "REPORTSTOOL": "${ REPORTSTOOL:-True }",
        "PRIVACYTOOL": "${ PRIVACYTOOL:-True }",
        "SOLUTIONSTOOL": "${ SOLUTIONSTOOL:-True }",
        "SUBSCRIPTIONSTOOL": "${ SUBSCRIPTIONSTOOL:-True }",
        "DOMAINSTOOL": "${ DOMAINSTOOL:-True }",
        "USERTOOL": "${ USERTOOL:-True }",
        "CONNECTIONSTOOL": "${ CONNECTIONSTOOL:-True }",
        "STORAGETOOL": "${ STORAGETOOL:-True }",
        "SECURITYTOOL": "${ SECURITYTOOL:-True }",
        "DEVICESTOOL": "${ DEVICESTOOL:-True }",
        "CONTACTSTOOL": "${ CONTACTSTOOL:-True }",
        "EDUCATIONTOOL": "${ EDUCATIONTOOL:-True }",
        "IDENTITYTOOL": "${ IDENTITYTOOL:-True }",
        "COMMUNICATIONSTOOL": "${ COMMUNICATIONSTOOL:-True }",
        "MAILTOOL": "${ MAILTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
microsoft-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ADMINTOOL enabled:

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
        "AUTHTOOL": "False",
        "GROUPSTOOL": "False",
        "AGREEMENTSTOOL": "False",
        "FILESTOOL": "False",
        "NOTESTOOL": "False",
        "ORGANIZATIONTOOL": "False",
        "AUDITTOOL": "False",
        "PLACESTOOL": "False",
        "PRINTTOOL": "False",
        "TASKSTOOL": "False",
        "SEARCHTOOL": "False",
        "EMPLOYEE_EXPERIENCETOOL": "False",
        "METATOOL": "False",
        "CHATTOOL": "False",
        "SITESTOOL": "False",
        "MISCTOOL": "False",
        "DIRECTORYTOOL": "False",
        "POLICIESTOOL": "False",
        "ADMINTOOL": "True",
        "TEAMSTOOL": "False",
        "APPLICATIONSTOOL": "False",
        "CALENDARTOOL": "False",
        "REPORTSTOOL": "False",
        "PRIVACYTOOL": "False",
        "SOLUTIONSTOOL": "False",
        "SUBSCRIPTIONSTOOL": "False",
        "DOMAINSTOOL": "False",
        "USERTOOL": "False",
        "CONNECTIONSTOOL": "False",
        "STORAGETOOL": "False",
        "SECURITYTOOL": "False",
        "DEVICESTOOL": "False",
        "CONTACTSTOOL": "False",
        "EDUCATIONTOOL": "False",
        "IDENTITYTOOL": "False",
        "COMMUNICATIONSTOOL": "False",
        "MAILTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py microsoft-agent help
```
