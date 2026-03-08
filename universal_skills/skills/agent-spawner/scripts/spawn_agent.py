#!/usr/bin/env python3
"""
Spawn a new Pydantic AI Agent dynamically and interact with it.
"""

import argparse
import asyncio
import os
import sys

# Optional dependency guardrail
try:
    from agent_utilities.agent_utilities import create_agent, chat
except ImportError:
    print(
        "Error: The 'agent_utilities' package is required but not installed.",
        file=sys.stderr,
    )
    print(
        "Please ensure it is installed or available in your environment.",
        file=sys.stderr,
    )
    sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Spawn a new Pydantic AI agent and interact with it."
    )

    # Required Arguments
    parser.add_argument("--prompt", required=True, help="Prompt to send to the agent")

    # Optional Arguments (Config)
    parser.add_argument(
        "--mcp-config",
        default=os.getenv("MCP_CONFIG"),
        help="Path to the mcp_config.json file",
    )
    parser.add_argument(
        "--mcp-url", default=os.getenv("MCP_URL"), help="Single MCP Server URL"
    )
    parser.add_argument(
        "--custom-skills-directory",
        default=os.getenv("CUSTOM_SKILLS_DIRECTORY"),
        help="Path to custom skills directory",
    )

    # Optional Arguments (Agent Personality)
    parser.add_argument(
        "--name",
        default=os.getenv("DEFAULT_AGENT_NAME", "SpawnedAgent"),
        help="Name for the newly spawned agent",
    )
    parser.add_argument(
        "--system-prompt",
        default=os.getenv("AGENT_SYSTEM_PROMPT", "You are a helpful assistant."),
        help="System prompt for the newly spawned agent",
    )

    # Optional Arguments (LLM Parameters)
    parser.add_argument(
        "--provider",
        default=os.getenv("PROVIDER", "openai"),
        help="LLM Provider (openai, anthropic, etc.)",
    )
    parser.add_argument(
        "--model-id",
        default=os.getenv("MODEL_ID", "qwen/qwen3.5-35b-a3b"),
        help="LLM Model ID",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("LLM_BASE_URL", "http://host.docker.internal:1234/v1"),
        help="LLM Base URL",
    )
    parser.add_argument(
        "--api-key", default=os.getenv("LLM_API_KEY", "ollama"), help="LLM API Key"
    )
    parser.add_argument(
        "--insecure", action="store_true", help="Disable SSL Verification"
    )

    args = parser.parse_args()

    # Evaluate SSL Verify (Default: Check Global env config, fallback to True; command arg overrides to False)
    ssl_verify = os.environ.get("SSL_VERIFY", "True").lower() not in (
        "false",
        "0",
        "f",
        "off",
    )
    if args.insecure:
        ssl_verify = False

    print(f"Spawning agent '{args.name}'...")
    agent = create_agent(
        provider=args.provider,
        model_id=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config,
        custom_skills_directory=args.custom_skills_directory,
        ssl_verify=ssl_verify,
        name=args.name,
        system_prompt=args.system_prompt,
    )

    print(f"Sending prompt to '{args.name}'...")
    await chat(agent, args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
