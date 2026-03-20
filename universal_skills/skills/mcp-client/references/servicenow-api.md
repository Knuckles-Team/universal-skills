# Servicenow Api Reference

**Project:** `servicenow-api`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SERVICENOW_INSTANCE` | Required for authentication |
| `SERVICENOW_PASSWORD` | Required for authentication |
| `SERVICENOW_USERNAME` | Required for authentication |

## Available Tool Tags (30)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ACCOUNTTOOL` | `True` | get_account |
| `ACTIVITY_SUBSCRIPTIONSTOOL` | `True` | get_activity_subscriptions |
| `AGGREGATETOOL` | `True` | get_stats |
| `APPLICATIONTOOL` | `True` | get_application |
| `ATTACHMENTTOOL` | `True` | delete_attachment, get_attachment, upload_attachment |
| `AUTHTOOL` | `True` | refresh_auth_token |
| `BATCHTOOL` | `True` | batch_request |
| `CHANGE_MANAGEMENTTOOL` | `True` | approve_change_request, calculate_standard_change_request_risk, check_change_request_conflict, create_change_request, create_change_request_ci_association, create_change_request_task, delete_change_request, delete_change_request_conflict_scan, delete_change_request_task, get_change_request, get_change_request_ci, get_change_request_conflict, get_change_request_models, get_change_request_nextstate, get_change_request_schedule, get_change_request_tasks, get_change_request_worker, get_change_requests, get_standard_change_request_model, get_standard_change_request_template, get_standard_change_request_templates, refresh_change_request_impacted_services, update_change_request, update_change_request_first_available, update_change_request_task |
| `CICDTOOL` | `True` | app_repo_install, app_repo_publish, app_repo_rollback, batch_install, batch_install_result, batch_rollback, combo_suite_scan, full_scan, instance_scan_progress, point_scan, progress, suite_scan |
| `CILIFECYCLETOOL` | `True` | check_ci_lifecycle_compat_actions, register_ci_lifecycle_operator, unregister_ci_lifecycle_operator |
| `CMDBTOOL` | `True` | create_cmdb_instance, create_cmdb_relation, delete_cmdb_relation, get_cmdb, get_cmdb_instance, get_cmdb_instances, ingest_cmdb_data, patch_cmdb_instance, update_cmdb_instance |
| `CUSTOM_APITOOL` | `True` | api_request |
| `DATA_CLASSIFICATIONTOOL` | `True` | get_data_classification |
| `DEVOPSTOOL` | `True` | check_devops_change_control, register_devops_artifact |
| `EMAILTOOL` | `True` | send_email |
| `FLOWSTOOL` | `True` | workflow_to_mermaid |
| `HRTOOL` | `True` | get_hr_profile |
| `IMPORT_SETSTOOL` | `True` | get_import_set, insert_import_set, insert_multiple_import_sets |
| `INCIDENTSTOOL` | `True` | create_incident, get_incidents |
| `KNOWLEDGE_MANAGEMENTTOOL` | `True` | get_featured_knowledge_article, get_knowledge_article, get_knowledge_article_attachment, get_knowledge_articles, get_most_viewed_knowledge_articles |
| `METRICBASETOOL` | `True` | metricbase_insert |
| `MISCTOOL` | `True` | (Internal tools) |
| `PLUGINSTOOL` | `True` | activate_plugin, rollback_plugin |
| `PPMTOOL` | `True` | insert_cost_plans, insert_project_tasks |
| `PRODUCT_INVENTORYTOOL` | `True` | delete_product_inventory, get_product_inventory |
| `SERVICE_QUALIFICATIONTOOL` | `True` | check_service_qualification, get_service_qualification, process_service_qualification_result |
| `SOURCE_CONTROLTOOL` | `True` | apply_remote_source_control_changes, import_repository |
| `TABLE_APITOOL` | `True` | add_table_record, delete_table_record, get_table, get_table_record, patch_table_record, update_table_record |
| `TESTINGTOOL` | `True` | run_test_suite |
| `UPDATE_SETSTOOL` | `True` | update_set_back_out, update_set_commit, update_set_commit_multiple, update_set_create, update_set_preview, update_set_retrieve |

## Stdio Connection (Default)

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
        "AUTHTOOL": "${ AUTHTOOL:-True }",
        "EMAILTOOL": "${ EMAILTOOL:-True }",
        "TABLE_APITOOL": "${ TABLE_APITOOL:-True }",
        "HRTOOL": "${ HRTOOL:-True }",
        "APPLICATIONTOOL": "${ APPLICATIONTOOL:-True }",
        "CICDTOOL": "${ CICDTOOL:-True }",
        "UPDATE_SETSTOOL": "${ UPDATE_SETSTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "DATA_CLASSIFICATIONTOOL": "${ DATA_CLASSIFICATIONTOOL:-True }",
        "KNOWLEDGE_MANAGEMENTTOOL": "${ KNOWLEDGE_MANAGEMENTTOOL:-True }",
        "CMDBTOOL": "${ CMDBTOOL:-True }",
        "CILIFECYCLETOOL": "${ CILIFECYCLETOOL:-True }",
        "FLOWSTOOL": "${ FLOWSTOOL:-True }",
        "TESTINGTOOL": "${ TESTINGTOOL:-True }",
        "PLUGINSTOOL": "${ PLUGINSTOOL:-True }",
        "PPMTOOL": "${ PPMTOOL:-True }",
        "CUSTOM_APITOOL": "${ CUSTOM_APITOOL:-True }",
        "IMPORT_SETSTOOL": "${ IMPORT_SETSTOOL:-True }",
        "METRICBASETOOL": "${ METRICBASETOOL:-True }",
        "CHANGE_MANAGEMENTTOOL": "${ CHANGE_MANAGEMENTTOOL:-True }",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "${ ACTIVITY_SUBSCRIPTIONSTOOL:-True }",
        "AGGREGATETOOL": "${ AGGREGATETOOL:-True }",
        "DEVOPSTOOL": "${ DEVOPSTOOL:-True }",
        "INCIDENTSTOOL": "${ INCIDENTSTOOL:-True }",
        "SERVICE_QUALIFICATIONTOOL": "${ SERVICE_QUALIFICATIONTOOL:-True }",
        "ATTACHMENTTOOL": "${ ATTACHMENTTOOL:-True }",
        "PRODUCT_INVENTORYTOOL": "${ PRODUCT_INVENTORYTOOL:-True }",
        "ACCOUNTTOOL": "${ ACCOUNTTOOL:-True }",
        "SOURCE_CONTROLTOOL": "${ SOURCE_CONTROLTOOL:-True }",
        "BATCHTOOL": "${ BATCHTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
servicenow-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ACCOUNTTOOL enabled:

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
        "AUTHTOOL": "False",
        "EMAILTOOL": "False",
        "TABLE_APITOOL": "False",
        "HRTOOL": "False",
        "APPLICATIONTOOL": "False",
        "CICDTOOL": "False",
        "UPDATE_SETSTOOL": "False",
        "MISCTOOL": "False",
        "DATA_CLASSIFICATIONTOOL": "False",
        "KNOWLEDGE_MANAGEMENTTOOL": "False",
        "CMDBTOOL": "False",
        "CILIFECYCLETOOL": "False",
        "FLOWSTOOL": "False",
        "TESTINGTOOL": "False",
        "PLUGINSTOOL": "False",
        "PPMTOOL": "False",
        "CUSTOM_APITOOL": "False",
        "IMPORT_SETSTOOL": "False",
        "METRICBASETOOL": "False",
        "CHANGE_MANAGEMENTTOOL": "False",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "False",
        "AGGREGATETOOL": "False",
        "DEVOPSTOOL": "False",
        "INCIDENTSTOOL": "False",
        "SERVICE_QUALIFICATIONTOOL": "False",
        "ATTACHMENTTOOL": "False",
        "PRODUCT_INVENTORYTOOL": "False",
        "ACCOUNTTOOL": "True",
        "SOURCE_CONTROLTOOL": "False",
        "BATCHTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py servicenow-api help
```
