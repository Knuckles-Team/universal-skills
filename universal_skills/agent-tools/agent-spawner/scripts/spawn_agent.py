#!/usr/bin/env python3
"""Create one bounded delegated agent from the shared AgentConfig runtime."""

from __future__ import annotations

import argparse
import asyncio
import re
import sys

_SAFE_MODEL_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_MAX_PROMPT_BYTES = 64 * 1024
_MAX_SYSTEM_PROMPT_BYTES = 16 * 1024


def _bounded_private_text(value: str, *, limit: int, label: str) -> str:
    from agent_utilities.security.persistence_privacy import sanitize_for_persistence

    rendered = str(value or "").strip()
    if not rendered or len(rendered.encode("utf-8")) > limit or "\x00" in rendered:
        raise ValueError(f"{label}_invalid")
    clean, _ = sanitize_for_persistence(rendered)
    return str(clean)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one delegated agent using the shared AgentConfig catalog."
    )
    parser.add_argument("--prompt", required=True, help="Bounded delegated task.")
    parser.add_argument(
        "--provider",
        help="Optional provider identifier; defaults to AgentConfig's chat model.",
    )
    parser.add_argument(
        "--model-id",
        help="Optional model identifier; defaults to AgentConfig's chat model.",
    )
    parser.add_argument(
        "--system-prompt",
        help="Optional bounded system instruction for this invocation.",
    )
    return parser.parse_args()


def _require_model_token(value: object) -> str:
    if not isinstance(value, str) or not _SAFE_MODEL_TOKEN.fullmatch(value):
        raise ValueError("model_identifier_invalid")
    return value


def _resolve_agent_identity(
    args: argparse.Namespace, config: object
) -> tuple[str, str, object | None]:
    default_model = getattr(config, "default_chat_model")
    provider = _require_model_token(
        args.provider or getattr(default_model, "provider", None)
    )
    model_id = _require_model_token(args.model_id or getattr(default_model, "id", None))
    return provider, model_id, default_model


def _resolve_system_prompt(args: argparse.Namespace, config: object) -> object:
    if args.system_prompt:
        return _bounded_private_text(
            args.system_prompt,
            limit=_MAX_SYSTEM_PROMPT_BYTES,
            label="system_prompt",
        )
    return getattr(config, "agent_system_prompt")


def _prepare_delegation(args: argparse.Namespace):
    from agent_utilities.agent.factory import create_agent
    from agent_utilities.core import config as config_module
    from agent_utilities.core.chat_persistence import chat

    config = config_module.AgentConfig()
    provider, model_id, default_model = _resolve_agent_identity(args, config)
    prompt = _bounded_private_text(args.prompt, limit=_MAX_PROMPT_BYTES, label="prompt")
    system_prompt = _resolve_system_prompt(args, config)
    agent, _ = create_agent(
        provider=provider,
        model_id=model_id,
        base_url=getattr(default_model, "base_url", None),
        api_key=getattr(default_model, "api_key_ref", None),
        mcp_url=config.mcp_url,
        mcp_config=config.mcp_config,
        custom_skills_directory=config.custom_skills_directory,
        name="delegated-agent",
        system_prompt=system_prompt,
        isolate_mcp=True,
    )
    return agent, prompt, chat


async def main() -> int:
    args = _parse_args()

    try:
        agent, prompt, chat = _prepare_delegation(args)
    except Exception:
        print("Delegated agent configuration was rejected.", file=sys.stderr)
        return 2

    print("Delegated agent started.", file=sys.stderr)
    try:
        await chat(agent, prompt)
    except Exception:
        print("Delegated agent execution failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
