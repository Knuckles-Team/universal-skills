# Systems Manager Reference

**Project:** `systems-manager`

## Required Environment Variables

| Variable | Description |
|----------|-------------|


## Available Tool Tags (17)

## Available Tool Tags (17)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `CRONTOOL` | `True` | add_cron_job, list_cron_jobs, remove_cron_job |
| `DISKTOOL` | `True` | get_disk_space_report, get_disk_usage, list_disks |
| `FILESYSTEMTOOL` | `True` | grep_files, list_files, manage_file, search_files |
| `FIREWALL_MANAGEMENTTOOL` | `True` | add_firewall_rule, get_firewall_status, list_firewall_rules, remove_firewall_rule |
| `LOGTOOL` | `True` | get_system_logs, tail_log_file |
| `MISCTOOL` | `True` | install_python_package_uv |
| `NETWORKTOOL` | `True` | dns_lookup, list_network_interfaces, list_open_ports, ping_host |
| `NODEJSTOOL` | `True` | install_node, install_nvm, use_node |
| `PROCESSTOOL` | `True` | get_process_info, kill_process, list_processes |
| `PYTHONTOOL` | `True` | create_python_venv, install_uv |
| `SERVICETOOL` | `True` | disable_service, enable_service, get_service_status, list_services, restart_service, start_service, stop_service |
| `SHELLTOOL` | `True` | add_shell_alias |
| `SSH_MANAGEMENTTOOL` | `True` | add_authorized_key, generate_ssh_key, list_ssh_keys |
| `SYSTEMTOOL` | `True` | clean, clean_package_cache, clean_temp_files, get_env_var, get_hardware_statistics, get_os_statistics, get_package_info, get_uptime, install_applications, install_fonts, install_python_modules, list_env_vars, list_installed_packages, list_upgradable_packages, optimize, search_package, system_health_check, update |
| `SYSTEM_MANAGEMENTTOOL` | `True` | add_repository, disable_windows_features, enable_windows_features, install_local_package, list_windows_features, run_command |
| `TEXT_EDITORTOOL` | `True` | text_editor |
| `USERTOOL` | `True` | list_groups, list_users |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "systems-manager": {
      "command": "systems-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TEXT_EDITORTOOL": "${ TEXT_EDITORTOOL:-True }",
        "FILESYSTEMTOOL": "${ FILESYSTEMTOOL:-True }",
        "PROCESSTOOL": "${ PROCESSTOOL:-True }",
        "LOGTOOL": "${ LOGTOOL:-True }",
        "USERTOOL": "${ USERTOOL:-True }",
        "SSH_MANAGEMENTTOOL": "${ SSH_MANAGEMENTTOOL:-True }",
        "SHELLTOOL": "${ SHELLTOOL:-True }",
        "SYSTEMTOOL": "${ SYSTEMTOOL:-True }",
        "CRONTOOL": "${ CRONTOOL:-True }",
        "NETWORKTOOL": "${ NETWORKTOOL:-True }",
        "NODEJSTOOL": "${ NODEJSTOOL:-True }",
        "SERVICETOOL": "${ SERVICETOOL:-True }",
        "SYSTEM_MANAGEMENTTOOL": "${ SYSTEM_MANAGEMENTTOOL:-True }",
        "FIREWALL_MANAGEMENTTOOL": "${ FIREWALL_MANAGEMENTTOOL:-True }",
        "PYTHONTOOL": "${ PYTHONTOOL:-True }",
        "MISCTOOL": "${ MISCTOOL:-True }",
        "DISKTOOL": "${ DISKTOOL:-True }"
      }
    }
  }
}
```

## HTTP Connection

```bash
systems-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only CRONTOOL enabled:

```json
{
  "mcpServers": {
    "systems-manager": {
      "command": "systems-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "TEXT_EDITORTOOL": "False",
        "FILESYSTEMTOOL": "False",
        "PROCESSTOOL": "False",
        "LOGTOOL": "False",
        "USERTOOL": "False",
        "SSH_MANAGEMENTTOOL": "False",
        "SHELLTOOL": "False",
        "SYSTEMTOOL": "False",
        "CRONTOOL": "True",
        "NETWORKTOOL": "False",
        "NODEJSTOOL": "False",
        "SERVICETOOL": "False",
        "SYSTEM_MANAGEMENTTOOL": "False",
        "FIREWALL_MANAGEMENTTOOL": "False",
        "PYTHONTOOL": "False",
        "MISCTOOL": "False",
        "DISKTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all resources (example)
python mcp_client.py systems-manager help
```
