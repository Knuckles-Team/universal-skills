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
        default=os.getenv("MODEL_ID", "google/gemma-4-31b"),
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

    # Dotenv support
    parser.add_argument(
        "--dotenv", help="Path to a .env file to load environment variables from"
    )

    args = parser.parse_args()

    # Load dotenv if provided
    if args.dotenv:
        try:
            from dotenv import load_dotenv

            load_dotenv(args.dotenv)
            # Re-evaluate arguments that might be in env if they weren't explicitly passed
            # This is a bit tricky with argparse defaults already set at parse time.
            # However, create_agent uses passed args, so we update the args object manually if default was used.
            # But wait, create_agent will use the args we pass.
            # If the user DID NOT pass --name, args.name is 'SpawnedAgent' (default).
            # If they have DEFAULT_AGENT_NAME in .env, we want that.
        except ImportError:
            print(
                "Error: python-dotenv is not installed. Install it with: pip install python-dotenv",
                file=sys.stderr,
            )
            sys.exit(1)

    # Resolve MCP Config Reference
    mcp_config = args.mcp_config
    if mcp_config and not os.path.exists(mcp_config):
        # Check in mcp-client references if it doesn't exist locally
        try:
            # Assuming we are running from the package root or standard install
            import universal_skills

            package_path = os.path.dirname(universal_skills.__file__)
            ref_path = os.path.join(
                package_path, "skills", "mcp-client", "references", mcp_config
            )

            if os.path.exists(ref_path):
                mcp_config = ref_path
            elif not mcp_config.endswith(".json"):
                # Try adding .json extension
                json_ref_path = ref_path + ".json"
                if os.path.exists(json_ref_path):
                    mcp_config = json_ref_path
        except (ImportError, Exception):
            pass

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
        mcp_config=mcp_config,
        custom_skills_directory=args.custom_skills_directory,
        ssl_verify=ssl_verify,
        name=args.name,
        system_prompt=args.system_prompt,
    )

    print(f"Sending prompt to '{args.name}'...")
    await chat(agent, args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
