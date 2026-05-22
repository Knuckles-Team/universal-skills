---
name: deploy_platform_stack
description: End-to-end deployment of an infrastructure platform using docker-compose files and Portainer MCP.
domain: infrastructure
tags: ['deployment', 'portainer', 'docker', 'stack', 'infrastructure']
requires: ['portainer-mcp']
---

# deploy_platform_stack Workflow

End-to-end deployment of an infrastructure platform using docker-compose files and Portainer MCP.

### Step 0: portainer-mcp
Use portainer_environment to get the endpoint ID where the stack will be deployed.
Expected: endpoint, id

### Step 1: portainer-mcp
Use portainer_stack to create the standalone stack from the docker-compose file.
Expected: stack, create
Depends On: Step 0
