# Agent-Utilities Ecosystem Standards

Follow these established patterns when building or improving agents in the `agent-utilities` ecosystem.

## 📁 Directory Structure
Standardized layouts for consistency and ease of discovery:

```text
my-new-agent/
├── pyproject.toml          # Required: Package config & dependencies
├── AGENTS.md               # Required: High-fidelity ecosystem overview
├── .env.example            # Required: Template for required keys
├── prompts/                # Required: Markdown-based system prompts
│   ├── researcher.md       # Standardized prompt names
│   └── planner.md          # Standardized prompt names
├── my_new_agent/           # Source code
│   ├── agent_server.py     # Main Agent & FastAPI entry point
│   ├── mcp_server.py       # MCP Tool definitions (FastMCP)
│   └── graph_orchestration.py # Complex graph logic (Pydantic-Graph)
└── scripts/                # Utility scripts
```

## 🛠️ MCP Tool Best Practices
- **Explicit Naming**: Use lowercase kebab-case for tool names (e.g., `git-search-code`).
- **Comprehensive Descriptions**: Every `@mcp.tool` must have a docstring that describes exactly *what* it does and *when* to use it.
- **Type-Safe Inputs**: Use Pydantic models or clean type hints for all tool arguments.
- **Human-Readable Errors**: Return clear error messages in the tool's output instead of allowing raw exceptions to bubble up.

## 🧠 Graph Execution (Pydantic-Graph)
- **Parallel Joiners**: Use specific "Barrier Sync" nodes (e.g. `res_joiner`, `exe_joiner`) to coordinate parallel expert execution.
- **Context Isolation**: Each expert node should only receive the subset of the state it needs.
- **Resilience Loops**: Implement retries or "Critic" nodes to self-correct failures before returning to the user.

## 📡 Communication & Discovery
- **A2A Protocol**: Ensure the `/a2a` endpoint is correctly configured to allow other agents to discover tools and metadata.
- **Swagger Docs**: Expose `/docs` (via FastAPI) to provide an interactive OpenAPI spec for all agent APIs.
- **SSE Streaming**: Always provide a streaming endpoint (`/stream`) for real-time visualization of the agent's graph activity.

## 🎨 Design Excellence
- **Vibrant Palettes**: Avoid default browser colors. Use HSL-based harmonious schemes.
- **Premium Micro-interactions**: Add subtle hover and active states to all buttons and inputs.
- **Rich Typography**: Use professional fonts and hierarchical font-weighting (Bold for headers, regular for body).
