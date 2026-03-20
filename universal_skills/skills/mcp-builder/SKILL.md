---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services using the approved FastMCP Python standardized template.
license: MIT
tags: [mcp, development, protocol, tools, api]
metadata:
  author: Audel Rouhi
  version: '0.1.48'
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

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

#### 2.4 Tool Grouping and Registration

Organize your `@mcp.tool` endpoints by common `tags` (e.g., `tags={"action"}`) and wrap related tools in a dedicated registration function named `register_<tag>_tools(mcp: FastMCP)`.

**CRITICAL: Tag Casing Constraint**
Tags **MUST** be strictly lowercase string names without special characters or spaces. (e.g. `tag="usermanagement"`, env var=`USERMANAGEMENTTOOL`). Do NOT use CamelCase or uppercase letters in tags, as it breaks downward integrations.

To provide a standard mechanism for configuring which tools are exposed by the MCP server depending on the environment, consider the following:
- **Consolidated Boilerplate**: Use the `create_mcp_server` high-level helper from `agent_utilities.mcp_utilities` to handle argument parsing, auth setup, and middleware assembly in a single call.
- **FastMCP**: Use the custom `FastMCP` available in `Workspace/fastmcp-python` which supports OIDC, JWT, and middleware out of the box.
- **Modularity**: Break down tool registration into logical groups (e.g., `register-admin-tools`).
  - **Naming**: Tags MUST be strictly lowercase. Use hyphens to split words (e.g., `user-auth` instead of `userauth`).
  - **Prefixing**: For dynamic agents, prefix tags with the service name (e.g., `leanix-pathfinder`).
  - **Toggles**: Every group MUST be triggered by explicit, human-readable static environment variables.
Use environment variables and `.env` files via `python-dotenv`:
1. Use `load_dotenv(find_dotenv())` at the start of your `mcp_server()` function.
2. For each registration function (even dynamically generated ones), define a default environment variable constant explicitly in `mcp_server.py` to allow administrators an easy visual reference of what can be toggled:
   ```python
   DEFAULT_ACTIONTOOL = to_boolean(os.getenv("ACTIONTOOL", "True"))
   if DEFAULT_ACTIONTOOL:
       register_action_tools(mcp)
   ```

This static layout is mandatory for ALL MCP servers, including massive ones combining metaprogramming routing (like `arr-mcp`), so administrators can secure environments efficiently without needing to read JSON files or code introspections to know what can be disabled.

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

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts
