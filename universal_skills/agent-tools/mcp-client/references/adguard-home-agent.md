# Adguard Home Agent Reference

**Project:** `adguard-home-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ADGUARD_PASSWORD` | Required for authentication |
| `ADGUARD_URL` | Required for authentication |
| `ADGUARD_USERNAME` | Required for authentication |

## Available Tool Tags (15)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `ACCESSTOOL` | `True` | get_access_list, set_access_list |
| `BLOCKED_SERVICESTOOL` | `True` | get_all_blocked_services, get_blocked_services_list, update_blocked_services |
| `CLIENTSTOOL` | `True` | add_client, delete_client, list_clients, search_clients, update_client |
| `DHCPTOOL` | `True` | add_dhcp_static_lease, find_active_dhcp, get_dhcp_interfaces, get_dhcp_status, remove_dhcp_static_lease, reset_dhcp, reset_dhcp_leases, set_dhcp_config, update_dhcp_static_lease |
| `DNSTOOL` | `True` | get_dns_info, set_dns_config, test_upstream_dns |
| `FILTERINGTOOL` | `True` | add_filter_url, check_host_filtering, get_filtering_status, refresh_filters, remove_filter_url, set_filter_url_params, set_filtering_config, set_filtering_rules |
| `MISCTOOL` | `True` | (Internal tools) |
| `MOBILETOOL` | `True` | get_doh_mobile_config, get_dot_mobile_config |
| `PROFILETOOL` | `True` | get_profile, update_profile |
| `QUERY_LOGTOOL` | `True` | clear_query_log, get_query_log |
| `REWRITESTOOL` | `True` | add_rewrite, delete_rewrite, get_rewrite_settings, list_rewrites, update_rewrite, update_rewrite_settings |
| `SETTINGSTOOL` | `True` | disable_parental_control, disable_safebrowsing, enable_parental_control, enable_safebrowsing, get_parental_status, get_safebrowsing_status, get_safesearch_status |
| `STATSTOOL` | `True` | get_stats, get_stats_config, reset_stats, set_stats_config |
| `SYSTEMTOOL` | `True` | clear_cache, get_version, set_protection |
| `TLSTOOL` | `True` | configure_tls, get_tls_status, validate_tls |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "adguard-home-agent": {
      "command": "adguard-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "ADGUARD_URL": "${ADGUARD_URL}",
        "ADGUARD_USERNAME": "${ADGUARD_USERNAME}",
        "ADGUARD_PASSWORD": "${ADGUARD_PASSWORD}",
        "DHCPTOOL": "${ DHCPTOOL:-True }",
        "BLOCKED_SERVICESTOOL": "${ BLOCKED_SERVICESTOOL:-True }",
        "ACCESSTOOL": "${ ACCESSTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "SETTINGSTOOL": "${ SETTINGSTOOL:-True }",
        "REWRITESTOOL": "${ REWRITESTOOL:-True }",
        "FILTERINGTOOL": "${ FILTERINGTOOL:-True }",
        "TLSTOOL": "${ TLSTOOL:-True }",
        "MOBILETOOL": "${ MOBILETOOL:-True }",
        "STATSTOOL": "${ STATSTOOL:-True }",
        "CLIENTSTOOL": "${ CLIENTSTOOL:-True }",
        "DNSTOOL": "${ DNSTOOL:-True }",
        "PROFILETOOL": "${ PROFILETOOL:-True }",
        "QUERY_LOGTOOL": "${ QUERY_LOGTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
adguard-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only ACCESSTOOL enabled:

```json
{
  "mcpServers": {
    "adguard-home-agent": {
      "command": "adguard-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "ADGUARD_URL": "${ADGUARD_URL}",
        "ADGUARD_USERNAME": "${ADGUARD_USERNAME}",
        "ADGUARD_PASSWORD": "${ADGUARD_PASSWORD}",
        "DHCPTOOL": "False",
        "BLOCKED_SERVICESTOOL": "False",
        "ACCESSTOOL": "True",
        "SYSTEMTOOL": "False",
        "SETTINGSTOOL": "False",
        "REWRITESTOOL": "False",
        "FILTERINGTOOL": "False",
        "TLSTOOL": "False",
        "MOBILETOOL": "False",
        "STATSTOOL": "False",
        "CLIENTSTOOL": "False",
        "DNSTOOL": "False",
        "PROFILETOOL": "False",
        "QUERY_LOGTOOL": "False",
        "MISCTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py adguard-home-agent help
```
