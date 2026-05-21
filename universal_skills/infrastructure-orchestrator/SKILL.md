---
name: infrastructure-orchestrator
description: Deploy entire platforms and manage hardware nodes using native agent-utilities workflows, Portainer, and Tunnel Manager MCPs.
---

# Infrastructure Orchestrator

Use this skill whenever the user asks to deploy a new infrastructure service, manage existing docker stacks, track hardware inventory, or orchestrate platforms across the homelab or enterprise environments.

## Core Capabilities

1. **Discovery and Visibility**: This agent uses either `portainer-mcp` (via `get_endpoints`, `get_stacks`, `docker_list_containers`) or `container-manager-mcp` (via `list_containers`, `list_services`, `list_networks`) to scan and discover existing services running across environments. Always run discovery first to understand the existing topology before taking action.
2. **Platform Deployment**: This agent utilizes the `portainer-mcp` tools to manage Swarm/Docker deployments. The docker-compose files and environments are natively stored and managed within Portainer.
3. **Native Workflow Execution**: The native `agent-utilities` catalog provides a `deploy_platform_stack` workflow. You can conceptually refer to this workflow when reasoning about deployments.
4. **Inventory Management**: Hardware inventory is stored in the `~/.config/agent-utilities/inventory.yaml` file (Ansible inventory format). This inventory is automatically ingested into the Knowledge Graph as `HardwareNode` concepts.
5. **Tunnel Management**: If the user asks to inspect a physical host or check OS-level dependencies before deployment, you query the Knowledge Graph for the `HardwareNode` (or look at `inventory.yaml`), then use `tunnel-manager-mcp` to connect, followed by `systems-manager-mcp` to inspect.

## Workflow: Discovery Phase

When asked to manage, inspect, or deploy to infrastructure, always start by "seeing what you're working with":

1. **Via Portainer**: Use `mcp_portainer_environment` -> `get_endpoints` to see available clusters, then `mcp_portainer_stack` -> `get_stacks` to see running applications.
2. **Via Container Manager**: If direct Docker/Swarm socket access is preferred, use `container-manager-mcp` to run `list_nodes` (for swarm), `list_services`, or `list_containers` to build a mental map of the current state.
3. Compare the running state with the Knowledge Graph or `inventory.yaml` to ensure alignment.

## Workflow: Deploying a Stack

When asked to deploy a new platform stack (e.g., "deploy Mealie"):

1. **Verify Endpoint**: Use `mcp_portainer_environment` -> `get_endpoints` to verify the ID of the deployment environment (e.g., Endpoint 3 for Homelab).
2. **Fetch Stack Details**: Since `docker-compose.yml` files are managed natively in Portainer, check if a stack already exists using `mcp_portainer_stack` -> `get_stacks`.
3. **Create Stack**: If it's a new deployment, use `mcp_portainer_stack` -> `create_standalone_stack` (or similar actions) to pass the composed YAML configuration.
4. **Verification**: Check container health using `mcp_portainer_docker` -> `docker_list_containers` to ensure the platform booted successfully.

## Workflow: Hardware and Networking

When asked to track inventory or SSH into a machine:

1. Look up the machine in `~/.config/agent-utilities/inventory.yaml` to find its IP address.
2. Formulate connections using `tunnel-manager-mcp`.
3. Understand that `graph-os` natively indexes these as `HardwareNode` and `PlatformService` entities for architectural reasoning.
