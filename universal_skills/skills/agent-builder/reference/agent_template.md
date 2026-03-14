# Agent Template Reference

Use this template as a reference for building agent systems conforming to standard `agent-utilities` conventions.

## 1. pyproject.toml
Ensure your package specifies proper dependencies and scripts:

```toml
[project]
name = "my-agent"
version = "0.1.0"
dependencies = [
    "agent-utilities>=0.1.10",
]

[project.optional-dependencies]
agent = [
    "agent-utilities[agent]>=0.1.10",
]

[project.scripts]
my-agent = "my_package.agent:agent_server"
```

## 2. IDENTITY.md (`my_package/agent/IDENTITY.md`)
Create this file with a single `[default]` block for the agent:

```markdown
# IDENTITY.md - Agent Identity

## [default]
 * **Name:** My Agent Name
 * **Role:** A concise description of the agent's role.
 * **Emoji:** 🤖
 * **Vibe:** Professional, precise

 ### System Prompt
 You are the My Agent Name.
 You must always first run list_skills and list_tools to discover available skills and tools.
 Your goal is to... [Describe system instructions and constraints].
 Check the `mcp-client` reference documentation for `your-specific-tag.md` (e.g. `servicenow-api.md` or `gitlab-api.md`) to discover the exact tags and tools available for your capabilities.

 ### Capabilities
 - **MCP Operations**: Leverage the `mcp-client` skill to interact with the target MCP server. Refer to your targeted reference file for specific tool capabilities.
 - **Custom Agent**: Handle custom tasks or general tasks.
```

## 3. agent.py (`my_package/agent.py`)
Create the entry point that loads the identity and provisions the server:

```python
#!/usr/bin/python
# coding: utf-8
import os
import logging

from agent_utilities import (
    create_agent_server,
    initialize_workspace,
    load_identity,
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
meta = load_identity()
DEFAULT_AGENT_NAME = os.getenv("DEFAULT_AGENT_NAME", meta.get("name", "My Agent"))
DEFAULT_AGENT_DESCRIPTION = os.getenv("AGENT_DESCRIPTION", meta.get("description", ""))
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT", meta.get("content") or build_system_prompt_from_workspace()
)

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = to_integer(os.getenv("PORT", "9000"))
DEFAULT_DEBUG = to_boolean(os.getenv("DEBUG", "False"))
DEFAULT_PROVIDER = os.getenv("PROVIDER", "openai")
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "nvidia/nemotron-3-super")
DEFAULT_LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://host.docker.internal:1234/v1")
DEFAULT_LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
DEFAULT_MCP_URL = os.getenv("MCP_URL", None)
DEFAULT_MCP_CONFIG = os.getenv("MCP_CONFIG", get_mcp_config_path())
DEFAULT_CUSTOM_SKILLS_DIRECTORY = os.getenv("CUSTOM_SKILLS_DIRECTORY", None)
DEFAULT_ENABLE_WEB_UI = to_boolean(os.getenv("ENABLE_WEB_UI", "False"))
DEFAULT_ENABLE_OTEL = to_boolean(os.getenv("ENABLE_OTEL", "False"))
DEFAULT_OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", None)
DEFAULT_OTEL_EXPORTER_OTLP_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", None)
DEFAULT_OTEL_EXPORTER_OTLP_PUBLIC_KEY = os.getenv("OTEL_EXPORTER_OTLP_PUBLIC_KEY", None)
DEFAULT_OTEL_EXPORTER_OTLP_SECRET_KEY = os.getenv("OTEL_EXPORTER_OTLP_SECRET_KEY", None)
DEFAULT_OTEL_EXPORTER_OTLP_PROTOCOL = os.getenv(
    "OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf"
)
DEFAULT_SSL_VERIFY = to_boolean(os.getenv("SSL_VERIFY", "True"))

DEFAULT_A2A_BROKER = os.getenv("A2A_BROKER", "in-memory")
DEFAULT_A2A_BROKER_URL = os.getenv("A2A_BROKER_URL", None)
DEFAULT_A2A_STORAGE = os.getenv("A2A_STORAGE", "in-memory")
DEFAULT_A2A_STORAGE_URL = os.getenv("A2A_STORAGE_URL", None)

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
        enable_otel=args.otel,
        otel_endpoint=args.otel_endpoint,
        otel_headers=args.otel_headers,
        otel_public_key=args.otel_public_key,
        otel_secret_key=args.otel_secret_key,
        otel_protocol=args.otel_protocol,
        a2a_broker=args.a2a_broker,
        a2a_broker_url=args.a2a_broker_url,
        a2a_storage=args.a2a_storage,
        a2a_storage_url=args.a2a_storage_url,
    )

if __name__ == "__main__":
    agent_server()
```
