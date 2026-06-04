---
name: mcp-builder
description: >-
  Guide for creating high-quality MCP (Model Context Protocol) servers that enable
  LLMs to interact with external services through well-designed tools. Use when
  building MCP servers to integrate external APIs or services using the approved
  FastMCP Python standardized template.
license: MIT
tags: [mcp, development, protocol, tools, api]
metadata:
  author: Genius
  version: '0.38.0'
---
# MCP Server Development Guide

## Overview

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks.

---

# Process

## 🚀 High-Level Workflow

Creating a high-quality MCP server involves four main phases:

### Phase 1: Deep Research and Planning

#### 1.1 Understand Modern MCP Design

**API Coverage vs. Workflow Tools:**
Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose operations. Performance varies by client—some clients benefit from code execution that combines basic tools, while others work better with higher-level workflows. When uncertain, prioritize comprehensive API coverage.

**Tool Naming and Discoverability:**
Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.

**Context Management:**
Agents benefit from concise tool descriptions and the ability to filter/paginate results. Design tools that return focused, relevant data. Some clients support code execution which can help agents filter and process data efficiently.

**Actionable Error Messages:**
Error messages should guide agents toward solutions with specific suggestions and next steps.

#### 1.2 Agent-Centric Design Principles

- **Balance API vs Workflow**: Prioritize comprehensive API coverage. High-level workflow tools are nice for speed, but granular tools allow agentic composition.
- **Predictable Outcomes**: Tools should be idempotent where possible. Use `readOnlyHint`, `destructiveHint`, and `idempotentHint` annotations.
- **Structured Data**: Return structured JSON for programmatic consumption, or clean Markdown for direct LLM processing.
- **Context Preservation**: Avoid overly large responses. Implement pagination filters by default.

#### 1.3 Study MCP Protocol Documentation

**Navigate the MCP specification:**

Start with the sitemap to find relevant pages: `https://modelcontextprotocol.io/sitemap.xml`

Then fetch specific pages with `.md` suffix for markdown format (e.g., `https://modelcontextprotocol.io/specification/draft.md`).

Key pages to review:
- Specification overview and architecture
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions

#### 1.3 Study Framework Documentation

**Recommended stack:**
- **Language**: Python (FastMCP). We build MCPs using our standard custom FastMCP template which includes standard middlewares (auth, timeout, Eunomia) and CLI argument parsing.
- **Transport**: stdio is standard for local execution, or streamable HTTP as supported by the `mcp_server()` entry point.

**Load framework documentation:**

- **MCP Best Practices**: [📋 View Best Practices](./reference/mcp_best_practices.md) - Core guidelines

**For Python (Required):**
- **Python SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Custom FastMCP Guide](./reference/python_mcp_server.md) - Our standard custom FastMCP server boilerplate, configuration, and patterns. ALL new MCPs must follow this exact pattern.

#### 1.4 Plan Your Implementation

**Understand the API:**
Review the service's API documentation to identify key endpoints, authentication requirements, and data models. Use web search and WebFetch as needed.

**Tool Selection:**
Prioritize comprehensive API coverage. List endpoints to implement, starting with the most common operations.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

See the custom FastMCP guide for project setup:
- [🐍 Custom FastMCP Guide](./reference/python_mcp_server.md) - Module organization, standard imports, middleware, and dependency requirements.

#### 2.2 Implement Core Infrastructure

Create shared utilities:
- API client with authentication
- Error handling helpers
- Response formatting (JSON/Markdown)
- Pagination support

#### 2.3 Implement Tools

For each tool:

**Input Schema:**
- Use Pydantic models to define inputs
- Include constraints and clear descriptions
- Add examples in field descriptions
- Avoid manual validation inside the tool; let Pydantic handle it
- **CRITICAL (Field Optimization)**: All parameters must explicitly use `pydantic.Field` with all parameter variables specified in an optimized fashion (e.g., `Field(default=..., description=...)`) rather than relying on standard Python defaults or positional arguments (e.g., do NOT use `Field(..., description="x")` or `Field(None, description="x")`, use `Field(description="x")` or `Field(default=None, description="x")`). This guarantees lossless JSON Schema hydration for the LLMs.

**Output Schema:**
- Determine if the output should be a straightforward string/markdown or a structured dictionary format based on the context.

**Tool Description:**
- Concise summary of functionality
- Parameter descriptions
- Return type schema

**Implementation:**
- Async/await for I/O operations
- Proper error handling with actionable messages
- Support pagination where applicable
- Be sure to properly handle and format API errors, matching the established middleware pattern.
- **Context Helpers**: Use `ctx_confirm_destructive`, `ctx_progress`, and `ctx_log` to enhance tool interaction. See the [🛠 Context Helpers Guide](./reference/ctx_helpers.md).

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

#### 2.4 Tool Grouping and Registration (Dynamic Action-Routing)

Do NOT write massive monolithic `mcp_server.py` files with individual static `@mcp.tool` decorators. Instead, use the modular **Action-Routed Dynamic Generation** pattern inside a **mandatory** `mcp/` subdirectory.

**Standard Folder Structure** (REQUIRED for all agents):
```
{pkg_dir}/
├── auth.py
├── mcp_server.py          ← Entrypoint importing registration hooks from mcp/
└── mcp/
    ├── __init__.py        ← Exposes register_*_tools functions
    ├── mcp_system.py      ← Dynamic action-routed tools for the "system" tag
    └── mcp_{domain}.py    ← One file per domain tag
```

> **Migration from `tools/` pattern**: Some older agents used a `tools/` subdirectory (e.g., documentdb-mcp, langfuse-agent). These MUST be migrated to `mcp/` for consistency. Rename `tools/` → `mcp/`, rename files from `{domain}.py` → `mcp_{domain}.py`, and update all imports.

**Dynamic Action-Routing Design**:
Group related endpoints by a conceptual `tag` (e.g., `system`) and dynamically compile a single unified tool per tag inside its own module (e.g., `{pkg_dir}/mcp/mcp_system.py`). This tool exposes an `action` enum corresponding to the underlying methods.

**CRITICAL: Tag Casing Constraint**
Tags **MUST** be strictly lowercase string names with hyphens to separate words (e.g. `user-management`). Do NOT use CamelCase or underscores in tags.

**CONCEPT ID Annotations**: Each tool domain SHOULD include its CONCEPT ID in the tool description string:
```python
def register_system_tools(mcp):
    """Register system management tools.

    CONCEPT:{PREFIX}-001
    """
```

**Environment Variable Gating**:
1. **Dynamic Loading**: `register_{domain}_tools` functions in sub-modules register action-routed tools on the main FastMCP instance.
2. **Static Toggles**: Inside `mcp_server.py`, check env vars for each suite:
   ```python
   DEFAULT_SYSTEMTOOL = to_boolean(os.getenv("SYSTEMTOOL", "True"))
   if DEFAULT_SYSTEMTOOL:
       register_system_tools(mcp)
   ```

**Environment Variable Standard for auth.py**:
| Pattern | Example | Notes |
|---------|---------|-------|
| `{SERVICE}_URL` | `PORTAINER_URL` | NOT `_BASE_URL` or `_INSTANCE` |
| `{SERVICE}_TOKEN` | `PORTAINER_TOKEN` | Prefer over `_API_KEY` |
| `{SERVICE}_SSL_VERIFY` | `PORTAINER_SSL_VERIFY` | NOT `_VERIFY` or `_AGENT_VERIFY` |

This layout is mandatory for ALL MCP servers so administrators can secure environments efficiently.

---

### Phase 3: Review and Test

#### 3.1 Code Quality

Review for:
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool descriptions

#### 3.2 Run and Test

**Python:**
- Verify execution: `python -m your_package.mcp_server --help` to check CLI args
- Check linting/pre-commits if applicable to the environment
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector`

See the Custom FastMCP Guide for detailed testing approaches and quality checklists.

---

### Phase 4: Evaluation-Driven Development

The quality of an MCP server is measured by its effectiveness in helping an LLM complete complex, multi-step tasks.

#### 4.1 Create Evaluations

After implementation, create a set of 10 evaluation questions.

**Evaluation Requirements:**
- **Independent**: No state dependency between questions.
- **Read-only**: Non-destructive operations only.
- **Complex**: Requires multiple tool calls and exploration.
- **Realistic**: Based on actual user intent.
- **Verifiable**: Clear, deterministic answer.

#### 4.2 Output Format
Create an XML file for evaluation:
```xml
<evaluation>
  <qa_pair>
    <question>...</question>
    <answer>...</answer>
  </qa_pair>
</evaluation>
```

---

### Phase 5: Ecosystem Drift Check (MANDATORY)

After completing the MCP server, run a drift audit to confirm the project meets all ecosystem standards. This is a hard gate — the MCP server is not complete until it passes with 0 missing items.

```bash
cd {project_dir} && echo "=== Drift Audit ===" \
  && for f in README.md CHANGELOG.md AGENTS.md pyproject.toml requirements.txt \
    .pre-commit-config.yaml .bumpversion.cfg .gitignore .gitattributes \
    .dockerignore .env mcp_config.json; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docs/index.md docs/overview.md docs/concepts.md; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docker/Dockerfile docker/compose.yml; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in {pkg_dir}/__init__.py {pkg_dir}/__main__.py {pkg_dir}/mcp_server.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && [ -d "{pkg_dir}/mcp" ] && echo "✅ mcp/ subdir" || echo "❌ mcp/ MISSING" \
  && for f in tests/conftest.py tests/test_concept_parity.py \
    tests/test_init_dynamics.py tests/test_startup.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && grep -q "ECO-4.0" docs/concepts.md && echo "✅ ECO-4.0 bridge" \
    || echo "❌ ECO-4.0 bridge MISSING"
```

If ANY item shows ❌, fix it before marking the build as complete. For a deeper audit with scoring, use the `ecosystem_standardizer` workflow.

> [!IMPORTANT]
> A new package is not complete until it passes the drift check with 0 missing items.

---

# Reference Files

## 📚 Documentation Library

Load these resources as needed during development:

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
  - Server and tool naming conventions
  - Response format guidelines (JSON vs Markdown)
  - Pagination best practices
  - Transport selection (streamable HTTP vs stdio)
  - Security and error handling standards

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

### Implementation Guides (Load During Phase 2)
- [🐍 Custom FastMCP Guide](./reference/python_mcp_server.md) - Complete custom FastMCP guide mapped to our internal standards containing:
  - The exact boilerplate required for the `mcp_server.py` file
  - Standardization logic for arguments, middlewares, and `mcp_server()`
  - Tool registration using `@mcp.tool`
  - Required imports and dependencies (`fastmcp`, `agent_utilities`, etc.)
  - Quality checklist
- [🛠 Context Helpers Guide](./reference/ctx_helpers.md) - Standard patterns for destructive guards, progress reporting, and logging.
- [📋 Phase 2 Implementation Plan](./reference/ctx_implementation_plan_phase_2.md) - Details on the fleet-wide instrumentation of context helpers.

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts
