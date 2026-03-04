# Mealie MCP Reference

**Project:** `mealie-mcp`
**Entrypoint:** `mealie-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MEALIE_URL` | Required for authentication |
| `MEALIE_API_KEY` | Required for authentication |

## Available Tool Tags (11)

| Env Variable | Default |
|-------------|----------|
| `ADMINTOOL` | `True` |
| `APPTOOL` | `True` |
| `EXPLORETOOL` | `True` |
| `GROUPSTOOL` | `True` |
| `HOUSEHOLDSTOOL` | `True` |
| `MISCTOOL` | `True` |
| `ORGANIZERTOOL` | `True` |
| `RECIPESTOOL` | `True` |
| `SHAREDTOOL` | `True` |
| `USERSTOOL` | `True` |
| `UTILSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "mealie-mcp": {
      "command": "mealie-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MEALIE_URL": "${MEALIE_URL}",
        "MEALIE_API_KEY": "${MEALIE_API_KEY}",
        "ADMINTOOL": "True",
        "APPTOOL": "True",
        "EXPLORETOOL": "True",
        "GROUPSTOOL": "True",
        "HOUSEHOLDSTOOL": "True",
        "MISCTOOL": "True",
        "ORGANIZERTOOL": "True",
        "RECIPESTOOL": "True",
        "SHAREDTOOL": "True",
        "USERSTOOL": "True",
        "UTILSTOOL": "True"
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
    "mealie-mcp": {
      "url": "http://mealie-mcp:8787/mcp",
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
    "mealie-mcp": {
      "command": "mealie-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "MEALIE_URL": "${MEALIE_URL}",
        "MEALIE_API_KEY": "${MEALIE_API_KEY}",
        "ADMINTOOL": "True",
        "APPTOOL": "False",
        "EXPLORETOOL": "False",
        "GROUPSTOOL": "False",
        "HOUSEHOLDSTOOL": "False",
        "MISCTOOL": "False",
        "ORGANIZERTOOL": "False",
        "RECIPESTOOL": "False",
        "SHAREDTOOL": "False",
        "USERSTOOL": "False",
        "UTILSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/mealie-mcp.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command mealie-mcp \
    --enable-tag ADMINTOOL \
    --all-tags "ADMINTOOL,APPTOOL,EXPLORETOOL,GROUPSTOOL,HOUSEHOLDSTOOL,MISCTOOL,ORGANIZERTOOL,RECIPESTOOL,SHAREDTOOL,USERSTOOL,UTILSTOOL"
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

### mealie-admin

**Description:** "Generated skill for admin operations. Contains 34 tools."

#### Overview
This skill handles operations related to admin.

#### Available Tools
- `get_app_info`: Get App Info
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_app_statistics`: Get App Statistics
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `check_app_config`: Check App Config
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_users`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_admin_users`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `unlock_users`: Unlock Users
  - **Parameters**:
    - `force` (bool)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_users_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_admin_users_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_admin_users_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `generate_token`: Generate Token
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_households`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_admin_households`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_households_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_admin_households_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_admin_households_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_groups`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_admin_groups`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_groups_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_admin_groups_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_admin_groups_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `check_email_config`: Check Email Config
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `send_test_email`: Send Test Email
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_backups`: Get All
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_admin_backups`: Create One
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_admin_backups_file_name`: Get One
  - **Parameters**:
    - `file_name` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_admin_backups_file_name`: Delete One
  - **Parameters**:
    - `file_name` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `upload_one`: Upload One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `import_one`: Import One
  - **Parameters**:
    - `file_name` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_maintenance_summary`: Get Maintenance Summary
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_storage_details`: Get Storage Details
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `clean_images`: Clean Images
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `clean_temp`: Clean Temp
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `clean_recipe_folders`: Clean Recipe Folders
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `debug_openai`: Debug Openai
  - **Parameters**:
    - `accept_language` (Any)
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-app

**Description:** "Generated skill for app operations. Contains 2 tools."

#### Overview
This skill handles operations related to app.

#### Available Tools
- `get_startup_info`: Get Startup Info
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_app_theme`: Get App Theme
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### Reference Files

- [Building Packages](reference/contributors_developers-guide_building-packages.md)
- [Contributing to Mealie](reference/contributors_developers-guide_code-contributions.md)
- [Development: Database Changes](reference/contributors_developers-guide_database-changes.md)
- [Maintainers Guide](reference/contributors_developers-guide_maintainers.md)
- [Migration Guide](reference/contributors_developers-guide_migration-guide.md)
- [Development: Getting Started](reference/contributors_developers-guide_starting-dev-server.md)
- [Improving the Ingredient Parser](reference/contributors_guides_ingredient-parser.md)
- [Non-Code Contributions](reference/contributors_non-coders.md)
- [Contributing with Translations](reference/contributors_translating.md)
- [Mealie```](reference/docs.md)
- [Bring API without internet exposure](reference/documentation_community-guide_bring-api.md)
- [Bulk Url Import](reference/documentation_community-guide_bulk-url-import.md)
- [Home Assistant](reference/documentation_community-guide_home-assistant.md)
- [Import Bookmarklet](reference/documentation_community-guide_import-recipe-bookmarklet.md)
- [iOS Shortcut](reference/documentation_community-guide_ios-shortcut.md)
- [Automating Backups with n8n](reference/documentation_community-guide_n8n-backup-automation.md)
- [Using SWAG as Reverse Proxy](reference/documentation_community-guide_swag.md)
- [Usage](reference/documentation_getting-started_api-usage.md)
- [LDAP Authentication](reference/documentation_getting-started_authentication_ldap.md)
- [OpenID Connect (OIDC) Authentication](reference/documentation_getting-started_authentication_oidc-v2.md)
- [Frequently Asked Questions](reference/documentation_getting-started_faq.md)
- [Features](reference/documentation_getting-started_features.md)
- [Backend Configuration](reference/documentation_getting-started_installation_backend-config.md)
- [Installation Checklist](reference/documentation_getting-started_installation_installation-checklist.md)
- [Logs](reference/documentation_getting-started_installation_logs.md)
- [OpenAI Integration](reference/documentation_getting-started_installation_open-ai.md)
- [Installing with PostgreSQL](reference/documentation_getting-started_installation_postgres.md)
- [Security Considerations](reference/documentation_getting-started_installation_security.md)
- [Installing with SQLite](reference/documentation_getting-started_installation_sqlite.md)
- [About The Project](reference/documentation_getting-started_introduction.md)
- [Migrating to Mealie v1 Release](reference/documentation_getting-started_migrating-to-mealie-v1.md)
- [Development Road Map](reference/documentation_getting-started_roadmap.md)
- [Updating Mealie](reference/documentation_getting-started_updating.md)
- [Backups and Restores](reference/documentation_getting-started_usage_backups-and-restoring.md)
- [Permissions and Public Access](reference/documentation_getting-started_usage_permissions-and-public-access.md)
- [Mealie](reference/index.md)
- [October 2024 Survey](reference/news_surveys_2024-october_overview.md)
- [openapi.json.md](reference/openapi.json.md)

### mealie-explore

**Description:** "Generated skill for explore operations. Contains 15 tools."

#### Overview
This skill handles operations related to explore.

#### Available Tools
- `get_explore_groups_group_slug_foods`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_foods_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_households`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_household`: Get Household
  - **Parameters**:
    - `household_slug` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_categories`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_categories_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_tags`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_tags_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_tools`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_organizers_tools_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_cookbooks`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_cookbooks_item_id`: Get One
  - **Parameters**:
    - `item_id` (Any)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_recipes`: Get All
  - **Parameters**:
    - `group_slug` (str)
    - `categories` (Any)
    - `tags` (Any)
    - `tools` (Any)
    - `foods` (Any)
    - `households` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `cookbook` (Any)
    - `require_all_categories` (bool)
    - `require_all_tags` (bool)
    - `require_all_tools` (bool)
    - `require_all_foods` (bool)
    - `search` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_explore_groups_group_slug_recipes_suggestions`: Suggest Recipes
  - **Parameters**:
    - `group_slug` (str)
    - `foods` (Any)
    - `tools` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `limit` (int)
    - `max_missing_foods` (int)
    - `max_missing_tools` (int)
    - `include_foods_on_hand` (bool)
    - `include_tools_on_hand` (bool)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe`: Get Recipe
  - **Parameters**:
    - `recipe_slug` (str)
    - `group_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-groups

**Description:** "Generated skill for groups operations. Contains 20 tools."

#### Overview
This skill handles operations related to groups.

#### Available Tools
- `get_all_households`: Get All Households
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_one_household`: Get One Household
  - **Parameters**:
    - `household_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user_group`: Get Logged In User Group
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_group_members`: Get Group Members
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_group_member`: Get Group Member
  - **Parameters**:
    - `username_or_id` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_group_preferences`: Get Group Preferences
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_group_preferences`: Update Group Preferences
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_storage`: Get Storage
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `start_data_migration`: Start Data Migration
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_groups_reports`: Get All
  - **Parameters**:
    - `report_type` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_groups_reports_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_groups_reports_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_groups_labels`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_groups_labels`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_groups_labels_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_groups_labels_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_groups_labels_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `seed_foods`: Seed Foods
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `seed_labels`: Seed Labels
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `seed_units`: Seed Units
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-households

**Description:** "Generated skill for households operations. Contains 64 tools."

#### Overview
This skill handles operations related to households.

#### Available Tools
- `get_households_cookbooks`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_cookbooks`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_cookbooks`: Update Many
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_cookbooks_item_id`: Get One
  - **Parameters**:
    - `item_id` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_cookbooks_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_cookbooks_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_events_notifications`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_events_notifications`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_events_notifications_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_events_notifications_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_events_notifications_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `test_notification`: Test Notification
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_recipe_actions`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_recipe_actions`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_recipe_actions_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_recipe_actions_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_recipe_actions_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `trigger_action`: Trigger Action
  - **Parameters**:
    - `item_id` (str)
    - `recipe_slug` (str)
    - `accept_language` (Any)
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user_household`: Get Logged In User Household
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_household_recipe`: Get Household Recipe
  - **Parameters**:
    - `recipe_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_household_members`: Get Household Members
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_household_preferences`: Get Household Preferences
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_household_preferences`: Update Household Preferences
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `set_member_permissions`: Set Member Permissions
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_statistics`: Get Statistics
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_invite_tokens`: Get Invite Tokens
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create_invite_token`: Create Invite Token
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `email_invitation`: Email Invitation
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_shopping_lists`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_shopping_lists`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_shopping_lists_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_shopping_lists_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_shopping_lists_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_label_settings`: Update Label Settings
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `add_recipe_ingredients_to_list`: Add Recipe Ingredients To List
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `add_single_recipe_ingredients_to_list`: Add Single Recipe Ingredients To List
  - **Parameters**:
    - `item_id` (str)
    - `recipe_id` (str)
    - `accept_language` (Any)
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `remove_recipe_ingredients_from_list`: Remove Recipe Ingredients From List
  - **Parameters**:
    - `item_id` (str)
    - `recipe_id` (str)
    - `accept_language` (Any)
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_shopping_items`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_shopping_items`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_shopping_items`: Update Many
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_shopping_items`: Delete Many
  - **Parameters**:
    - `ids` (List)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_shopping_items_create_bulk`: Create Many
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_shopping_items_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_shopping_items_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_shopping_items_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_webhooks`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_webhooks`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `rerun_webhooks`: Rerun Webhooks
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_webhooks_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_webhooks_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_webhooks_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `test_one`: Test One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_mealplans_rules`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_mealplans_rules`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_mealplans_rules_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_mealplans_rules_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_mealplans_rules_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_mealplans`: Get All
  - **Parameters**:
    - `start_date` (Any)
    - `end_date` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_households_mealplans`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_todays_meals`: Get Todays Meals
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create_random_meal`: Create Random Meal
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_households_mealplans_item_id`: Get One
  - **Parameters**:
    - `item_id` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_households_mealplans_item_id`: Update One
  - **Parameters**:
    - `item_id` (int)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_households_mealplans_item_id`: Delete One
  - **Parameters**:
    - `item_id` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-organizer

**Description:** "Generated skill for organizer operations. Contains 20 tools."

#### Overview
This skill handles operations related to organizer.

#### Available Tools
- `get_organizers_categories`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_organizers_categories`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_all_empty`: Get All Empty
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_categories_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_organizers_categories_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_organizers_categories_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_categories_slug_category_slug`: Get One By Slug
  - **Parameters**:
    - `category_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tags`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_organizers_tags`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_empty_tags`: Get Empty Tags
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tags_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_organizers_tags_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_recipe_tag`: Delete Recipe Tag
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tags_slug_tag_slug`: Get One By Slug
  - **Parameters**:
    - `tag_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tools`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_organizers_tools`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tools_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_organizers_tools_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_organizers_tools_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_organizers_tools_slug_tool_slug`: Get One By Slug
  - **Parameters**:
    - `tool_slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-recipe

**Description:** "Generated skill for recipe operations. Contains 52 tools."

#### Overview
This skill handles operations related to recipe.

#### Available Tools
- `get_recipe_formats_and_templates`: Get Recipe Formats And Templates
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe_as_format`: Get Recipe As Format
  - **Parameters**:
    - `slug` (str)
    - `template_name` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `test_parse_recipe_url`: Test Parse Recipe Url
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create_recipe_from_html_or_json`: Create Recipe From Html Or Json
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `parse_recipe_url`: Parse Recipe Url
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `parse_recipe_url_bulk`: Parse Recipe Url Bulk
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create_recipe_from_zip`: Create Recipe From Zip
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create_recipe_from_image`: Create Recipe From Image
  - **Parameters**:
    - `data` (Dict)
    - `translate_language` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipes`: Get All
  - **Parameters**:
    - `categories` (Any)
    - `tags` (Any)
    - `tools` (Any)
    - `foods` (Any)
    - `households` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `cookbook` (Any)
    - `require_all_categories` (bool)
    - `require_all_tags` (bool)
    - `require_all_tools` (bool)
    - `require_all_foods` (bool)
    - `search` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_recipes`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_recipes`: Update Many
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `patch_many`: Patch Many
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipes_suggestions`: Suggest Recipes
  - **Parameters**:
    - `foods` (Any)
    - `tools` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `limit` (int)
    - `max_missing_foods` (int)
    - `max_missing_tools` (int)
    - `include_foods_on_hand` (bool)
    - `include_tools_on_hand` (bool)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipes_slug`: Get One
  - **Parameters**:
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_recipes_slug`: Update One
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `patch_one`: Patch One
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_recipes_slug`: Delete One
  - **Parameters**:
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `duplicate_one`: Duplicate One
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_last_made`: Update Last Made
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `scrape_image_url`: Scrape Image Url
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_recipe_image`: Update Recipe Image
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_recipe_image`: Delete Recipe Image
  - **Parameters**:
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `upload_recipe_asset`: Upload Recipe Asset
  - **Parameters**:
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe_comments`: Get Recipe Comments
  - **Parameters**:
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `bulk_tag_recipes`: Bulk Tag Recipes
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `bulk_settings_recipes`: Bulk Settings Recipes
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `bulk_categorize_recipes`: Bulk Categorize Recipes
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `bulk_delete_recipes`: Bulk Delete Recipes
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `bulk_export_recipes`: Bulk Export Recipes
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_exported_data`: Get Exported Data
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_exported_data_token`: Get Exported Data Token
  - **Parameters**:
    - `export_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `purge_export_data`: Purge Export Data
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_shared_recipe`: Get Shared Recipe
  - **Parameters**:
    - `token_id` (str)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_shared_recipe_as_zip`: Get Shared Recipe As Zip
  - **Parameters**:
    - `token_id` (str)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipes_timeline_events`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_recipes_timeline_events`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipes_timeline_events_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_recipes_timeline_events_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_recipes_timeline_events_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_event_image`: Update Event Image
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_comments`: Get All
  - **Parameters**:
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_comments`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_comments_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_comments_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_parser_ingredient`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `parse_ingredient`: Parse Ingredient
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `parse_ingredients`: Parse Ingredients
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe_img`: Get Recipe Img
  - **Parameters**:
    - `recipe_id` (str)
    - `file_name` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe_timeline_event_img`: Get Recipe Timeline Event Img
  - **Parameters**:
    - `recipe_id` (str)
    - `timeline_event_id` (str)
    - `file_name` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_recipe_asset`: Get Recipe Asset
  - **Parameters**:
    - `recipe_id` (str)
    - `file_name` (str)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_user_image`: Get User Image
  - **Parameters**:
    - `user_id` (str)
    - `file_name` (str)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_validation_text`: Get Validation Text
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-recipes

**Description:** "Generated skill for recipes operations. Contains 12 tools."

#### Overview
This skill handles operations related to recipes.

#### Available Tools
- `get_foods`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_foods`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_foods_merge`: Merge One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_foods_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_foods_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_foods_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_units`: Get All
  - **Parameters**:
    - `search` (Any)
    - `order_by` (Any)
    - `order_by_null_position` (Any)
    - `order_direction` (Any)
    - `query_filter` (Any)
    - `pagination_seed` (Any)
    - `page` (int)
    - `per_page` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_units`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_units_merge`: Merge One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_units_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `put_units_item_id`: Update One
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_units_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-shared

**Description:** "Generated skill for shared operations. Contains 4 tools."

#### Overview
This skill handles operations related to shared.

#### Available Tools
- `get_shared_recipes`: Get All
  - **Parameters**:
    - `recipe_id` (Any)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `post_shared_recipes`: Create One
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_shared_recipes_item_id`: Get One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete_shared_recipes_item_id`: Delete One
  - **Parameters**:
    - `item_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-users

**Description:** "Generated skill for users operations. Contains 22 tools."

#### Overview
This skill handles operations related to users.

#### Available Tools
- `get_token`: Get Token
  - **Parameters**:
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `oauth_login`: Oauth Login
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `oauth_callback`: Oauth Callback
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `refresh_token`: Refresh Token
  - **Parameters**:
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `logout`: Logout
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `register_new_user`: Register New User
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user`: Get Logged In User
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user_ratings`: Get Logged In User Ratings
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user_rating_for_recipe`: Get Logged In User Rating For Recipe
  - **Parameters**:
    - `recipe_id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_logged_in_user_favorites`: Get Logged In User Favorites
  - **Parameters**:
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_password`: Update Password
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_user`: Update User
  - **Parameters**:
    - `item_id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `forgot_password`: Forgot Password
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `reset_password`: Reset Password
  - **Parameters**:
    - `data` (Dict)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `update_user_image`: Update User Image
  - **Parameters**:
    - `id` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `create`: Create Api Token
  - **Parameters**:
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `delete`: Delete Api Token
  - **Parameters**:
    - `token_id` (int)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_ratings`: Get Ratings
  - **Parameters**:
    - `id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `get_favorites`: Get Favorites
  - **Parameters**:
    - `id` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `set_rating`: Set Rating
  - **Parameters**:
    - `id` (str)
    - `slug` (str)
    - `data` (Dict)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `add_favorite`: Add Favorite
  - **Parameters**:
    - `id` (str)
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)
- `remove_favorite`: Remove Favorite
  - **Parameters**:
    - `id` (str)
    - `slug` (str)
    - `accept_language` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.

### mealie-utils

**Description:** "Generated skill for utils operations. Contains 1 tools."

#### Overview
This skill handles operations related to utils.

#### Available Tools
- `download_file`: Download File
  - **Parameters**:
    - `token` (Any)
    - `mealie_base_url` (str)
    - `mealie_token` (Optional[str])
    - `mealie_verify` (bool)

#### Usage Instructions
1. Review the tool available in this skill.
2. Call the tool with the required parameters.

#### Error Handling
- Ensure all required parameters are provided.
- Check return values for error messages.
