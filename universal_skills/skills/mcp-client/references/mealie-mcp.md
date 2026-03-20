# Mealie MCP Reference

**Project:** `mealie-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `MEALIE_API_KEY` | Required for authentication |
| `MEALIE_URL` | Required for authentication |

## Available Tool Tags (11)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ADMINTOOL` | `True` | check_app_config, check_email_config, clean_images, clean_recipe_folders, clean_temp, debug_openai, delete_admin_backups_file_name, delete_admin_groups_item_id, delete_admin_households_item_id, delete_admin_users_item_id, generate_token, get_admin_backups, get_admin_backups_file_name, get_admin_groups, get_admin_groups_item_id, get_admin_households, get_admin_households_item_id, get_admin_users, get_admin_users_item_id, get_app_info, get_app_statistics, get_maintenance_summary, get_storage_details, import_one, post_admin_backups, post_admin_groups, post_admin_households, post_admin_users, put_admin_groups_item_id, put_admin_households_item_id, put_admin_users_item_id, send_test_email, unlock_users, upload_one |
| `APPTOOL` | `True` | get_app_theme, get_startup_info |
| `EXPLORETOOL` | `True` | get_explore_groups_group_slug_cookbooks, get_explore_groups_group_slug_cookbooks_item_id, get_explore_groups_group_slug_foods, get_explore_groups_group_slug_foods_item_id, get_explore_groups_group_slug_households, get_explore_groups_group_slug_organizers_categories, get_explore_groups_group_slug_organizers_categories_item_id, get_explore_groups_group_slug_organizers_tags, get_explore_groups_group_slug_organizers_tags_item_id, get_explore_groups_group_slug_organizers_tools, get_explore_groups_group_slug_organizers_tools_item_id, get_explore_groups_group_slug_recipes, get_explore_groups_group_slug_recipes_suggestions, get_household, get_recipe |
| `GROUPSTOOL` | `True` | delete_groups_labels_item_id, delete_groups_reports_item_id, get_all_households, get_group_member, get_group_members, get_group_preferences, get_groups_labels, get_groups_labels_item_id, get_groups_reports, get_groups_reports_item_id, get_logged_in_user_group, get_one_household, get_storage, post_groups_labels, put_groups_labels_item_id, seed_foods, seed_labels, seed_units, start_data_migration, update_group_preferences |
| `HOUSEHOLDSTOOL` | `True` | add_recipe_ingredients_to_list, add_single_recipe_ingredients_to_list, create_invite_token, create_random_meal, delete_households_cookbooks_item_id, delete_households_events_notifications_item_id, delete_households_mealplans_item_id, delete_households_mealplans_rules_item_id, delete_households_recipe_actions_item_id, delete_households_shopping_items, delete_households_shopping_items_item_id, delete_households_shopping_lists_item_id, delete_households_webhooks_item_id, email_invitation, get_household_members, get_household_preferences, get_household_recipe, get_households_cookbooks, get_households_cookbooks_item_id, get_households_events_notifications, get_households_events_notifications_item_id, get_households_mealplans, get_households_mealplans_item_id, get_households_mealplans_rules, get_households_mealplans_rules_item_id, get_households_recipe_actions, get_households_recipe_actions_item_id, get_households_shopping_items, get_households_shopping_items_item_id, get_households_shopping_lists, get_households_shopping_lists_item_id, get_households_webhooks, get_households_webhooks_item_id, get_invite_tokens, get_logged_in_user_household, get_statistics, get_todays_meals, post_households_cookbooks, post_households_events_notifications, post_households_mealplans, post_households_mealplans_rules, post_households_recipe_actions, post_households_shopping_items, post_households_shopping_items_create_bulk, post_households_shopping_lists, post_households_webhooks, put_households_cookbooks, put_households_cookbooks_item_id, put_households_events_notifications_item_id, put_households_mealplans_item_id, put_households_mealplans_rules_item_id, put_households_recipe_actions_item_id, put_households_shopping_items, put_households_shopping_items_item_id, put_households_shopping_lists_item_id, put_households_webhooks_item_id, remove_recipe_ingredients_from_list, rerun_webhooks, set_member_permissions, test_notification, test_one, trigger_action, update_household_preferences, update_label_settings |
| `MISCTOOL` | `True` | (Internal tools) |
| `ORGANIZERTOOL` | `True` | delete_organizers_categories_item_id, delete_organizers_tools_item_id, delete_recipe_tag, get_all_empty, get_empty_tags, get_organizers_categories, get_organizers_categories_item_id, get_organizers_categories_slug_category_slug, get_organizers_tags, get_organizers_tags_item_id, get_organizers_tags_slug_tag_slug, get_organizers_tools, get_organizers_tools_item_id, get_organizers_tools_slug_tool_slug, post_organizers_categories, post_organizers_tags, post_organizers_tools, put_organizers_categories_item_id, put_organizers_tags_item_id, put_organizers_tools_item_id |
| `RECIPESTOOL` | `True` | bulk_categorize_recipes, bulk_delete_recipes, bulk_export_recipes, bulk_settings_recipes, bulk_tag_recipes, create_recipe_from_html_or_json, create_recipe_from_image, create_recipe_from_zip, delete_foods_item_id, delete_recipe_image, delete_recipes_slug, delete_recipes_timeline_events_item_id, delete_units_item_id, duplicate_one, get_comments, get_comments_item_id, get_exported_data, get_exported_data_token, get_foods, get_foods_item_id, get_recipe_as_format, get_recipe_asset, get_recipe_comments, get_recipe_formats_and_templates, get_recipe_img, get_recipe_timeline_event_img, get_recipes, get_recipes_slug, get_recipes_suggestions, get_recipes_timeline_events, get_recipes_timeline_events_item_id, get_shared_recipe, get_shared_recipe_as_zip, get_units, get_units_item_id, get_user_image, get_validation_text, parse_ingredient, parse_ingredients, parse_recipe_url, parse_recipe_url_bulk, patch_many, patch_one, post_comments, post_foods, post_parser_ingredient, post_recipes, post_recipes_timeline_events, post_units, purge_export_data, put_comments_item_id, put_foods_item_id, put_foods_merge, put_recipes, put_recipes_slug, put_recipes_timeline_events_item_id, put_units_item_id, put_units_merge, scrape_image_url, test_parse_recipe_url, update_event_image, update_last_made, update_recipe_image, upload_recipe_asset |
| `SHAREDTOOL` | `True` | delete_shared_recipes_item_id, get_shared_recipes, get_shared_recipes_item_id, post_shared_recipes |
| `USERSTOOL` | `True` | add_favorite, create, delete, forgot_password, get_favorites, get_logged_in_user, get_logged_in_user_favorites, get_logged_in_user_rating_for_recipe, get_logged_in_user_ratings, get_ratings, get_token, logout, oauth_callback, oauth_login, refresh_token, register_new_user, remove_favorite, reset_password, set_rating, update_password, update_user, update_user_image |
| `UTILSTOOL` | `True` | download_file |

## Stdio Connection (Default)

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
        "GROUPSTOOL": "${ GROUPSTOOL:-True }",
        "ADMINTOOL": "${ ADMINTOOL:-True }",
        "USERSTOOL": "${ USERSTOOL:-True }",
        "ORGANIZERTOOL": "${ ORGANIZERTOOL:-True }",
        "HOUSEHOLDSTOOL": "${ HOUSEHOLDSTOOL:-True }",
        "EXPLORETOOL": "${ EXPLORETOOL:-True }",
        "RECIPESTOOL": "${ RECIPESTOOL:-True }",
        "UTILSTOOL": "${ UTILSTOOL:-True }",
        "SHAREDTOOL": "${ SHAREDTOOL:-True }",
        "APPTOOL": "${ APPTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
mealie-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ADMINTOOL enabled:

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
        "GROUPSTOOL": "False",
        "ADMINTOOL": "True",
        "USERSTOOL": "False",
        "ORGANIZERTOOL": "False",
        "HOUSEHOLDSTOOL": "False",
        "EXPLORETOOL": "False",
        "RECIPESTOOL": "False",
        "UTILSTOOL": "False",
        "SHAREDTOOL": "False",
        "APPTOOL": "False",
        "MISCTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py mealie-mcp help
```
