# AdGuard Home MCP Reference

**Project:** `adguard-home-agent`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ADGUARD_URL` | Required for authentication |
| `ADGUARD_USERNAME` | Required for authentication |
| `ADGUARD_PASSWORD` | Required for authentication |

## Available Tool Tags (15)

| Env Variable | Default |
|-------------|----------|
| `ACCESSTOOL` | `True` |
| `BLOCKED_SERVICESTOOL` | `True` |
| `CLIENTSTOOL` | `True` |
| `DHCPTOOL` | `True` |
| `DNSTOOL` | `True` |
| `FILTERINGTOOL` | `True` |
| `MISCTOOL` | `True` |
| `MOBILETOOL` | `True` |
| `PROFILETOOL` | `True` |
| `QUERY_LOGTOOL` | `True` |
| `REWRITESTOOL` | `True` |
| `SETTINGSTOOL` | `True` |
| `STATSTOOL` | `True` |
| `SYSTEMTOOL` | `True` |
| `TLSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

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
        "ACCESSTOOL": "True",
        "BLOCKED_SERVICESTOOL": "True",
        "CLIENTSTOOL": "True",
        "DHCPTOOL": "True",
        "DNSTOOL": "True",
        "FILTERINGTOOL": "True",
        "MISCTOOL": "True",
        "MOBILETOOL": "True",
        "PROFILETOOL": "True",
        "QUERY_LOGTOOL": "True",
        "REWRITESTOOL": "True",
        "SETTINGSTOOL": "True",
        "STATSTOOL": "True",
        "SYSTEMTOOL": "True",
        "TLSTOOL": "True"
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
    "adguard-home-agent": {
      "url": "http://adguard-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `ACCESSTOOL` and disable all others:

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
        "ACCESSTOOL": "True",
        "BLOCKED_SERVICESTOOL": "False",
        "CLIENTSTOOL": "False",
        "DHCPTOOL": "False",
        "DNSTOOL": "False",
        "FILTERINGTOOL": "False",
        "MISCTOOL": "False",
        "MOBILETOOL": "False",
        "PROFILETOOL": "False",
        "QUERY_LOGTOOL": "False",
        "REWRITESTOOL": "False",
        "SETTINGSTOOL": "False",
        "STATSTOOL": "False",
        "SYSTEMTOOL": "False",
        "TLSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/adguard-home-agent.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command adguard-mcp \
    --enable-tag ACCESSTOOL \
    --all-tags "ACCESSTOOL,BLOCKED_SERVICESTOOL,CLIENTSTOOL,DHCPTOOL,DNSTOOL,FILTERINGTOOL,MISCTOOL,MOBILETOOL,PROFILETOOL,QUERY_LOGTOOL,REWRITESTOOL,SETTINGSTOOL,STATSTOOL,SYSTEMTOOL,TLSTOOL"
```

## Tailored Skills Reference

### adguard-access

**Description:** AdGuard Home Access capabilities for A2A Agent.

#### Overview
This skill provides access to access operations.

#### Capabilities
- **get_access_list**: List current access list (allowed/disallowed clients, blocked hosts).
- **set_access_list**: Set access list.

#### Common Tools
- `get_access_list`: List current access list (allowed/disallowed clients, blocked hosts).
- `set_access_list`: Set access list.

#### Usage Rules
- Use these tools when the user requests actions related to **access**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please check access status"
- "Please list access"

### adguard-account

**Description:** AdGuard Home Account capabilities for A2A Agent.

#### Overview
This skill provides access to account operations.

#### Capabilities
- **get_account_limits**: Get account limits.

#### Common Tools
- `get_account_limits`: Get account limits.

#### Usage Rules
- Use these tools when the user requests actions related to **account**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please check account status"
- "Please list account"

### adguard-blocked-services

**Description:** Manage blocked services in AdGuard Home.

## AdGuard Home Blocked Services Agent

This agent is responsible for managing blocked services (e.g., YouTube, Facebook).

### Capabilities

- **List Services**: Get a list of all available services and currently blocked services.
- **Update Services**: Update the list of blocked services.

### Tools

#### `get_all_blocked_services`
- **Description**: Get all available services that can be blocked.

#### `get_blocked_services_list`
- **Description**: Get the list of currently blocked services.

#### `update_blocked_services`
- **Description**: Update the list of blocked services.
- **Parameters**: `services` (list of str)

### adguard-clients

**Description:** Manage clients in AdGuard Home.

## AdGuard Home Clients Agent

This agent is responsible for managing clients in AdGuard Home.

### Capabilities

- **List Clients**: List all configured clients.
- **Search Clients**: Search for clients by IP, name, or ClientID.
- **CRUD**: Add, update, and delete clients.

### Tools

#### `list_clients`
- **Description**: List all clients.

#### `search_clients`
- **Description**: Search for clients.
- **Parameters**: `query` (str)

#### `add_client`
- **Description**: Add a new client.
- **Parameters**: `name` (str), `ids` (list of str), various settings...

#### `update_client`
- **Description**: Update a client.
- **Parameters**: `name` (str), `data` (dict)

#### `delete_client`
- **Description**: Delete a client.
- **Parameters**: `name` (str)

### adguard-dhcp

**Description:** Manage DHCP server in AdGuard Home.

## AdGuard Home DHCP Agent

This agent is responsible for managing the built-in DHCP server in AdGuard Home.

### Capabilities

- **Status & Config**: Get status, set configuration, reset configuration.
- **Interfaces**: List interfaces, find active DHCP servers.
- **Leases**: Manage static leases, reset all leases.

### Tools

#### `get_dhcp_status`
- **Description**: Get DHCP status.

#### `get_dhcp_interfaces`
- **Description**: Get available network interfaces.

#### `set_dhcp_config`
- **Description**: Set DHCP configuration.
- **Parameters**: `config` (dict)

#### `find_active_dhcp`
- **Description**: Search for an active DHCP server on a specific interface.
- **Parameters**: `interface` (str)

#### `add_dhcp_static_lease`
- **Description**: Add a static DHCP lease.
- **Parameters**: `mac` (str), `ip` (str), `hostname` (str)

#### `remove_dhcp_static_lease`
- **Description**: Remove a static DHCP lease.
- **Parameters**: `mac` (str), `ip` (str), `hostname` (str)

#### `update_dhcp_static_lease`
- **Description**: Update a static DHCP lease.
- **Parameters**: `mac` (str), `ip` (str), `hostname` (str)

#### `reset_dhcp`
- **Description**: Reset DHCP configuration.

#### `reset_dhcp_leases`
- **Description**: Reset all DHCP leases.

### adguard-dns

**Description:** Manage DNS settings in AdGuard Home.

## AdGuard Home DNS Agent

This agent is responsible for managing DNS settings in AdGuard Home.

### Capabilities

- **Get DNS Info**: Retrieve current DNS configuration.
- **Set DNS Config**: Update DNS configuration (upstream servers, bootstrap DNS, etc.).
- **Test Upstream DNS**: Test connectivity to upstream DNS servers.
- **Set Protection**: Enable or disable protection.
- **Clear Cache**: Clear the DNS cache.

### Tools

#### `get_dns_info`
- **Description**: Get general DNS parameters.

#### `set_dns_config`
- **Description**: Set general DNS parameters.
- **Parameters**: `config` (dict)

#### `test_upstream_dns`
- **Description**: Test upstream configuration.
- **Parameters**: `upstreams` (list of str)

#### `set_protection`
- **Description**: Set protection state.
- **Parameters**: `enabled` (bool), `duration` (int, optional)

#### `clear_cache`
- **Description**: Clear DNS cache.

### adguard-filtering

**Description:** Manage filtering settings in AdGuard Home.

## AdGuard Home Filtering Agent

This agent is responsible for managing filtering settings in AdGuard Home.

### Capabilities

- **Get Filtering Status**: GET current filtering status.
- **Set Filtering Config**: Enable/disable filtering and set update interval.
- **Set Filtering Rules**: Set user-defined custom filtering rules.
- **Check Host Filtering**: Check if a host is filtered.
- **Filter Lists**: Add, remove, and update filter lists (URLs).

### Tools

#### `get_filtering_status`
- **Description**: Get filtering status.

#### `set_filtering_config`
- **Description**: Set filtering configuration.
- **Parameters**: `enabled` (bool), `interval` (int)

#### `set_filtering_rules`
- **Description**: Set user-defined filtering rules.
- **Parameters**: `rules` (list of str)

#### `check_host_filtering`
- **Description**: Check if a host is filtered.
- **Parameters**: `name` (str)

#### `set_filter_url_params`
- **Description**: Set parameters for a filter list URL.
- **Parameters**: `url` (str), `name` (str), `whitelist` (bool)

#### `add_filter_url`
- **Description**: Add a new filter list.
- **Parameters**: `name` (str), `url` (str), `whitelist` (bool)

#### `remove_filter_url`
- **Description**: Remove a filter list.
- **Parameters**: `url` (str), `whitelist` (bool)

#### `refresh_filters`
- **Description**: Refresh all filter lists.
- **Parameters**: `whitelist` (bool)

### adguard-mobile

**Description:** Retrieve mobile configuration files for AdGuard Home.

## AdGuard Home Mobile Config Agent

This agent is responsible for retrieving mobile configuration files (.mobileconfig) for iOS/macOS devices.

### Capabilities

- **Get DoH Config**: Retrieve DNS-over-HTTPS .mobileconfig.
- **Get DoT Config**: Retrieve DNS-over-TLS .mobileconfig.

### Tools

#### `get_doh_mobile_config`
- **Description**: Get DNS over HTTPS .mobileconfig.
- **Parameters**:
    - `host` (str): Host name.
    - `client_id` (str): Client ID.

#### `get_dot_mobile_config`
- **Description**: Get DNS over TLS .mobileconfig.
- **Parameters**:
    - `host` (str): Host name.
    - `client_id` (str): Client ID.

### adguard-profile

**Description:** Manage the current user profile in AdGuard Home.

## AdGuard Home Profile Agent

This agent is responsible for managing the current user profile in AdGuard Home.

### Capabilities

- **Get Profile**: Retrieve current user information.
- **Update Profile**: Update current user information (name, password, etc.).

### Tools

#### `get_profile`
- **Description**: Get current user profile info.
- **Parameters**: None (uses default connection settings).

#### `update_profile`
- **Description**: Update current user profile info.
- **Parameters**:
    - `profile_data` (dict): Profile data to update (e.g., `{"name": "newname", "password": "newpassword"}`).

### adguard-query-log

**Description:** Manage and view query logs in AdGuard Home.

## AdGuard Home Query Log Agent

This agent is responsible for managing and viewing query logs.

### Capabilities

- **Get Query Log**: Retrieve query logs with filtering options.
- **Config**: Get and set query log configuration (retention, anonymization).
- **Clear**: Clear the query log.

### Tools

#### `get_query_log`
- **Description**: Get query log.
- **Parameters**: `limit` (int), `older_than` (str), `response_status` (str), `search` (str)

#### `get_query_log_config`
- **Description**: Get query log configuration.

#### `set_query_log_config`
- **Description**: Set query log configuration.
- **Parameters**: `enabled` (bool), `interval` (int), `anonymize_client_ip` (bool)

#### `clear_query_log`
- **Description**: Clear query log.

### adguard-rewrites

**Description:** Manage DNS rewrites in AdGuard Home.

## AdGuard Home Rewrites Agent

This agent is responsible for managing DNS rewrites (custom DNS records).

### Capabilities

- **List Rewrites**: List all DNS rewrites.
- **Settings**: Get and update rewrite settings (enable/disable).
- **CRUD**: Add, update, and delete DNS rewrites.

### Tools

#### `list_rewrites`
- **Description**: List DNS rewrites.

#### `add_rewrite`
- **Description**: Add a DNS rewrite.
- **Parameters**: `domain` (str), `answer` (str)

#### `update_rewrite`
- **Description**: Update a DNS rewrite.
- **Parameters**: `target` (dict), `update` (dict)

#### `delete_rewrite`
- **Description**: Delete a DNS rewrite.
- **Parameters**: `domain` (str), `answer` (str)

#### `get_rewrite_settings`
- **Description**: Get rewrite settings.

#### `update_rewrite_settings`
- **Description**: Update rewrite settings.
- **Parameters**: `enabled` (bool)

### adguard-settings

**Description:** AdGuard Home Settings capabilities for A2A Agent.

#### Overview
This skill provides access to settings operations.

#### Capabilities
- **get_parental_status**: Get parental control status.
- **enable_parental_control**: Enable parental control.
- **disable_parental_control**: Disable parental control.
- **get_safebrowsing_status**: Get safe browsing status.
- **enable_safebrowsing**: Enable safe browsing.
- **disable_safebrowsing**: Disable safe browsing.
- **get_safesearch_status**: Get safe search status.

#### Common Tools
- `get_parental_status`: Get parental control status.
- `enable_parental_control`: Enable parental control.
- `disable_parental_control`: Disable parental control.
- `get_safebrowsing_status`: Get safe browsing status.
- `enable_safebrowsing`: Enable safe browsing.
- `disable_safebrowsing`: Disable safe browsing.
- `get_safesearch_status`: Get safe search status.

#### Prompts
- **configure_parental_controls**: Configure parental control settings.

#### Usage Rules
- Use these tools when the user requests actions related to **settings**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please check settings status"
- "Please list settings"

### adguard-stats

**Description:** Manage and view statistics in AdGuard Home.

## AdGuard Home Stats Agent

This agent is responsible for managing and viewing statistics.

### Capabilities

- **Get Stats**: Retrieve overall statistics.
- **Config**: Get and set statistics configuration (retention interval).
- **Reset**: Reset all statistics.

### Tools

#### `get_stats`
- **Description**: Get overall statistics.

#### `get_stats_config`
- **Description**: Get statistics configuration.

#### `set_stats_config`
- **Description**: Set statistics configuration.
- **Parameters**: `interval` (int)

#### `reset_stats`
- **Description**: Reset all statistics.

### adguard-system

**Description:** AdGuard Home System capabilities for A2A Agent.

#### Overview
This skill provides access to system operations.

#### Capabilities
- **get_version**: Get AdGuard Home version.

#### Common Tools
- `get_version`: Get AdGuard Home version.

#### Usage Rules
- Use these tools when the user requests actions related to **system**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please check system status"
- "Please list system"

### adguard-tls

**Description:** Manage TLS configuration in AdGuard Home.

## AdGuard Home TLS Agent

This agent is responsible for managing the TLS configuration in AdGuard Home.

### Capabilities

- **Get TLS Status**: Retrieve current TLS configuration and status.
- **Configure TLS**: Update TLS configuration.
- **Validate TLS**: Validate TLS configuration.

### Tools

#### `get_tls_status`
- **Description**: Get TLS status.
- **Parameters**: None (uses default connection settings).

#### `configure_tls`
- **Description**: Configure TLS.
- **Parameters**:
    - `config` (dict): TLS configuration object.

#### `validate_tls`
- **Description**: Validate TLS configuration.
- **Parameters**:
    - `config` (dict): TLS configuration object to validate.
