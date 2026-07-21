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


async def main() -> int:
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
    args = parser.parse_args()

    try:
        from agent_utilities.agent_utilities import chat, create_agent
        from agent_utilities.core.config import AgentConfig

        cfg = AgentConfig()
        default_model = cfg.default_chat_model
        provider = args.provider or (
            default_model.provider if default_model is not None else "openai"
        )
        model_id = args.model_id or (
            default_model.id if default_model is not None else "qwen/qwen3.6-27b"
        )
        if not _SAFE_MODEL_TOKEN.fullmatch(provider) or not _SAFE_MODEL_TOKEN.fullmatch(
            model_id
        ):
            raise ValueError("model_identifier_invalid")
        prompt = _bounded_private_text(
            args.prompt, limit=_MAX_PROMPT_BYTES, label="prompt"
        )
        system_prompt = (
            _bounded_private_text(
                args.system_prompt,
                limit=_MAX_SYSTEM_PROMPT_BYTES,
                label="system_prompt",
            )
            if args.system_prompt
            else cfg.agent_system_prompt
        )
        api_key = default_model.api_key if default_model is not None else None
        base_url = default_model.base_url if default_model is not None else None
        agent = create_agent(
            provider=provider,
            model_id=model_id,
            base_url=base_url,
            api_key=api_key,
            mcp_url=cfg.mcp_url,
            mcp_config=cfg.mcp_config,
            custom_skills_directory=cfg.custom_skills_directory,
            ssl_verify=cfg.ssl_verify,
            name="delegated-agent",
            system_prompt=system_prompt,
            tool_guard_mode="strict",
            isolate_mcp=True,
        )
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
