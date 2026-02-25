# Multi-Agent Template Reference

Use this template as a reference for building multi-agent systems. A multi-agent system utilizes a "supervisor" agent to delegate queries to specialized "child" agents, keeping tool sets distinct and organized.

## 1. pyproject.toml
Ensure your package specifies proper dependencies and scripts:

```toml
[project]
name = "my-multi-agent"
version = "0.1.0"
dependencies = [
    "agent-utilities>=0.1.10",
]

[project.optional-dependencies]
agent = [
    "agent-utilities[agent]>=0.1.10",
]

[project.scripts]
my-multi-agent = "my_package.agent:agent_server"
```

## 2. IDENTITY.md (`my_package/agent/IDENTITY.md`)
Create this file with a `[supervisor]` block, followed by blocks for each child agent tool tag:

```markdown
# IDENTITY.md - Multi-Agent Identity

## [supervisor]
 * **Name:** Multi-Agent Supervisor
 * **Role:** Delegate tasks to specialized child agents.
 * **Emoji:** 🏢
 * **Vibe:** Professional, authoritative

 ### System Prompt
 You are the Supervisor Agent.
 Your goal is to analyze the user's request, determine the domain, and delegate tasks to the appropriate child agents.
 Synthesize the results into a cohesive response.

## [child_domain_1]
 * **Name:** Domain 1 Agent
 * **Role:** Manage Domain 1 tools.
 * **Emoji:** 🛠️
 ### System Prompt
 You are the Domain 1 Agent. You handle... [Domain 1 tasks].

## [child_domain_2]
 * **Name:** Domain 2 Agent
 * **Role:** Manage Domain 2 tools.
 * **Emoji:** ⚙️
 ### System Prompt
 You are the Domain 2 Agent. You handle... [Domain 2 tasks].
```

## 3. agent.py (`my_package/agent.py`)
Create the entry point that parcels out the child agent definitions and passes them to `create_agent_server()`:

```python
#!/usr/bin/python
# coding: utf-8
import os
import logging

from agent_utilities import (
    create_agent_server,
    initialize_workspace,
    load_identities,
    build_system_prompt_from_workspace,
)
from agent_utilities.agent_utilities import create_agent_parser, get_mcp_config_path
from agent_utilities.base_utilities import to_integer, to_boolean

__version__ = "0.1.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load identity and system prompt from workspace
initialize_workspace()
identities = load_identities()

# Prepare supervisor identity
supervisor_meta = identities.get("supervisor", identities.get("default", {}))
DEFAULT_AGENT_NAME = os.getenv(
    "DEFAULT_AGENT_NAME", supervisor_meta.get("name", "Supervisor Agent")
)
DEFAULT_AGENT_DESCRIPTION = os.getenv(
    "AGENT_DESCRIPTION",
    supervisor_meta.get("description", "A multi-agent system."),
)
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT",
    supervisor_meta.get("content") or build_system_prompt_from_workspace(),
)

# Prepare child agent definitions from IDENTITY.md sections
CHILD_AGENT_DEFS = {
    tag: (data["content"], data["name"])
    for tag, data in identities.items()
    if tag not in ["supervisor", "default"]
}

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = to_integer(os.getenv("PORT", "9000"))
DEFAULT_DEBUG = to_boolean(os.getenv("DEBUG", "False"))
DEFAULT_PROVIDER = os.getenv("PROVIDER", "openai")
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "qwen/qwen3-coder-next")
DEFAULT_LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://host.docker.internal:1234/v1")
DEFAULT_LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
DEFAULT_MCP_URL = os.getenv("MCP_URL", None)
DEFAULT_MCP_CONFIG = os.getenv("MCP_CONFIG", get_mcp_config_path())
DEFAULT_CUSTOM_SKILLS_DIRECTORY = os.getenv("CUSTOM_SKILLS_DIRECTORY", None)
DEFAULT_ENABLE_WEB_UI = to_boolean(os.getenv("ENABLE_WEB_UI", "False"))
DEFAULT_SSL_VERIFY = to_boolean(os.getenv("SSL_VERIFY", "True"))

def agent_server():
    print(f"{DEFAULT_AGENT_NAME} v{__version__}")
    parser = create_agent_parser()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    create_agent_server(
        provider=args.provider,
        model_id=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config,
        custom_skills_directory=args.custom_skills_directory,
        debug=args.debug,
        host=args.host,
        port=args.port,
        enable_web_ui=args.web,
        ssl_verify=not args.insecure,
        name=DEFAULT_AGENT_NAME,
        system_prompt=DEFAULT_AGENT_SYSTEM_PROMPT,
        agent_definitions=CHILD_AGENT_DEFS if CHILD_AGENT_DEFS else None,
    )

if __name__ == "__main__":
    agent_server()
```
