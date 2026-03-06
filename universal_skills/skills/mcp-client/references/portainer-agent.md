# Portainer Agent MCP Reference

**Project:** `portainer-agent`
**Entrypoint:** `portainer-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `PORTAINER_URL` | Base URL of the Portainer instance (e.g., `http://localhost:9000`) |
| `PORTAINER_TOKEN` | API access token for authentication |

## Available Tool Tags (10)

| Env Variable | Default | Tools |
|-------------|---------|-------|
| `AUTHTOOL` | `True` | authenticate, logout, validate_oauth |
| `ENVIRONMENTTOOL` | `True` | get_endpoints, get_endpoint, create_endpoint, update_endpoint, delete_endpoint, snapshot_endpoint, snapshot_all_endpoints, get_endpoint_groups, create_endpoint_group, delete_endpoint_group |
| `DOCKERTOOL` | `True` | get_docker_dashboard, get_docker_images, get_container_gpus |
| `STACKTOOL` | `True` | get_stacks, get_stack, get_stack_file, create_standalone_stack, create_standalone_stack_from_repo, update_stack, delete_stack, start_stack, stop_stack, redeploy_stack_git |
| `KUBERNETESTOOL` | `True` | get_kubernetes_dashboard, get_kubernetes_namespaces, get_kubernetes_applications, get_kubernetes_services, get_kubernetes_ingresses, get_kubernetes_configmaps, get_kubernetes_secrets, get_kubernetes_volumes, get_kubernetes_events, get_kubernetes_nodes_limits, get_kubernetes_metrics_nodes, get_helm_releases, install_helm_chart, delete_helm_release |
| `EDGETOOL` | `True` | get_edge_groups, create_edge_group, delete_edge_group, get_edge_stacks, get_edge_stack, create_edge_stack, delete_edge_stack, get_edge_jobs, get_edge_job, create_edge_job, delete_edge_job |
| `TEMPLATETOOL` | `True` | get_templates, get_custom_templates, get_custom_template, create_custom_template, delete_custom_template, get_custom_template_file, get_helm_templates |
| `USERTOOL` | `True` | get_users, get_user, get_current_user, create_user, delete_user, get_teams, create_team, delete_team, get_roles, get_user_tokens |
| `REGISTRYTOOL` | `True` | get_registries, get_registry, create_registry, delete_registry |
| `SYSTEMTOOL` | `True` | get_status, get_system_info, get_system_version, get_settings, update_settings, get_tags, create_tag, delete_tag, get_motd, backup_portainer |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "portainer-agent": {
      "command": "portainer-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "PORTAINER_URL": "${PORTAINER_URL}",
        "PORTAINER_TOKEN": "${PORTAINER_TOKEN}",
        "AUTHTOOL": "True",
        "ENVIRONMENTTOOL": "True",
        "DOCKERTOOL": "True",
        "STACKTOOL": "True",
        "KUBERNETESTOOL": "True",
        "EDGETOOL": "True",
        "TEMPLATETOOL": "True",
        "USERTOOL": "True",
        "REGISTRYTOOL": "True",
        "SYSTEMTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

```bash
portainer-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Single-Tag Config Example

Only Docker + Stack tools enabled:

```json
{
  "mcpServers": {
    "portainer-agent": {
      "command": "portainer-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "PORTAINER_URL": "${PORTAINER_URL}",
        "PORTAINER_TOKEN": "${PORTAINER_TOKEN}",
        "AUTHTOOL": "False",
        "ENVIRONMENTTOOL": "True",
        "DOCKERTOOL": "True",
        "STACKTOOL": "True",
        "KUBERNETESTOOL": "False",
        "EDGETOOL": "False",
        "TEMPLATETOOL": "False",
        "USERTOOL": "False",
        "REGISTRYTOOL": "False",
        "SYSTEMTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all environments
python mcp_client.py portainer-agent get_endpoints

# Get Docker dashboard
python mcp_client.py portainer-agent get_docker_dashboard --tool-args '{"environment_id": 1}'

# Create a stack
python mcp_client.py portainer-agent create_standalone_stack --tool-args '{"name": "myapp", "file_content": "version: \"3\"\nservices:\n  web:\n    image: nginx", "endpoint_id": 1}'
```
