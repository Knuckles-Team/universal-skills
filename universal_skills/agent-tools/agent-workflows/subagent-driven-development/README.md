# a2a-orchestrator

Supervisor skill that registers all homelab A2A agents for orchestration via `sessions_spawn`.

Each agent maps to its deployment name (e.g., `homelab-container-manager-agent`) and can be spawned with a task string.

Agents with multiple nodes (container-manager, systems-manager) are included as individual entries with node suffixes in their names.
