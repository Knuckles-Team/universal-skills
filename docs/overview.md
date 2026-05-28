# universal-skills — Concept Overview

> **Category**: Skills | **Ecosystem Role**: MCP Server + A2A Agent
> Built on [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) — the unified AGI Harness.

## Description

Universal skill library providing cross-cutting agent capabilities.

## Enterprise Readiness

All agents in the ecosystem inherit enterprise-grade infrastructure from `agent-utilities`:

| Feature | Status | Source |
|:--------|:-------|:-------|
| **JWT/OIDC Authentication** | ✅ Built-in | `agent-utilities[auth]` — Authlib JWKS + API key middleware |
| **OpenTelemetry Instrumentation** | ✅ Built-in | `agent-utilities[logfire]` — OTLP export, FastAPI auto-instrumentation |
| **HashiCorp Vault Integration** | ✅ Built-in | `agent-utilities[vault]` — `secret://`, `env://`, `vault://` URI schemes |
| **Audit Logging** | ✅ Built-in | Append-only compliance trail with 30+ action types (CONCEPT:OS-5.4) |
| **Token Usage Analytics** | ✅ Built-in | 4-bucket tracking with budget alerting (CONCEPT:OS-5.4) |
| **Prompt Injection Defense** | ✅ Built-in | 25+ pattern scanner + jailbreak taxonomy (CONCEPT:OS-5.1) |
| **Guardrail Engine** | ✅ Built-in | Input/output interception with block/redact/warn (CONCEPT:OS-5.3) |
| **Action Execution Pipeline** | ✅ Built-in | Token, cost, duration, and node transition limits Dry-run / commit / rollback phases (CONCEPT:ORCH-1.4) |
| **Resource Scheduling** | ✅ Built-in | Priority queuing + preemption limits (CONCEPT:OS-5.2) |
| **Session Concurrency** | ✅ Built-in | Enqueue/reject/interrupt/rollback (CONCEPT:OS-5.3) |

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| AHE-3.4 | Distributed Agentic Evolution | `agent-utilities` (inherited) |
| ECO-4.1 | MCP & Universal Skills | `agent-utilities` (inherited) |
| ECO-4.8 | **Dynamic Skill Evolution** | `agent-utilities` (inherited) |

> 📖 **Full Registry**: See [`agent-utilities/docs/overview.md`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/overview.md) for the complete 5-Pillar concept index.

## Architecture

This project follows the standardized agent-package pattern:

```
universal-skills/
├── universal_skills/        # Source code
│   ├── __init__.py
│   ├── agent_server.py      # Entry point (create_graph_agent_server)
│   ├── api_client.py        # REST/GraphQL API wrapper
│   └── mcp_server.py        # FastMCP tool definitions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml           # Package metadata
├── mcp_config.json          # MCP server configuration
├── main_agent.json          # Agent identity & system prompt
└── Dockerfile               # Container deployment
```

## MCP Configuration

### stdio Mode
```json
{
  "mcpServers": {
    "universal-skills": {
      "command": "uv",
      "args": ["run", "--with", "universal-skills", "universal-mcp"],
      "env": {}
    }
  }
}
```

### Streamable HTTP Mode
```bash
universal-mcp --transport streamable-http --port 8001
```

## Day 0 Bootstrap & Multi-Service Wiring Orchestrator

The package includes a comprehensive, graph-driven **Day 0 Bootstrap & Multi-Service Wiring Orchestrator** workflow. It maps the automated top-down provisioning and configuration of all **19 homelab services** starting from a single bare-metal server:

```mermaid
graph TD
    subgraph "Layer 0: Host Discovery & Pre-flight"
        A[SSH key Full-Mesh Bootstrap] --> B[Host OS & HW Discovery]
        B --> C[Overlay Networks Provisioning]
    end

    subgraph "Layer 1: Edge Router & Authoritative DNS"
        C --> D[Technitium DNS Server macvlan/static IP 10.0.0.199]
        D --> E[Caddy Dynamic Ingress Router HTTP/HTTPS]
    end

    subgraph "Layer 2: Identity & Security Foundations"
        E --> F[Keycloak SSO OIDC/SAML]
        F --> G[OpenBao Secure Vault KV2 Engine]
    end

    subgraph "Layer 3: DevOps & GitOps Automation"
        G --> H[GitLab Project & Repo Provisioning]
        H --> I[Portainer GitOps Syncing with GitLab PATs]
    end

    subgraph "Layer 4: Automated Services Provisioning"
        I --> J[Launch 19 Services in Dependency Tiers]
    end

    subgraph "Layer 5: Unified Cross-Service Wiring"
        J --> K1[DNS: Technitium Authoritative Records Mapping]
        J --> K2[Proxy: Caddy Dynamic Overlay Routing]
        J --> K3[SSO: Keycloak Clients Auto-Registration]
        J --> K4[Observability: Loki/Prometheus Scraping & Langfuse OTEL Traces]
        J --> K5[Backups: BorgBackup Database Dumps & Repository Sync]
    end

    subgraph "Layer 6: Knowledge Graph Materialization"
        K1 & K2 & K3 & K4 & K5 --> L[Ingest Full Topology Snapshot into Graph-OS]
    end
```
