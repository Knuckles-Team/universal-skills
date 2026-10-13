"""Preserve provider-origin and SDK write-confirmation boundaries."""

from urllib.parse import urlsplit

from agent_connector_sdk.mcp.context import ctx_confirm_destructive
from fastmcp.server.dependencies import get_context
from mcp.types import InputRequiredResult


def require_origin(base_url, *, credential_scheme, allow_plaintext):
    parsed = urlsplit(base_url)
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Base URL must be the provider origin without a path")
    if credential_scheme and parsed.scheme == "http" and not allow_plaintext:
        raise ValueError("Credential-bearing plaintext HTTP requires explicit opt-in")


async def confirm_write(operation, arguments, client):
    if operation["read_only"]:
        return None
    if not client.allow_writes:
        raise PermissionError("Writes require explicit operator enablement")
    confirmation = await ctx_confirm_destructive(
        get_context(), operation["action"], confirmation_arguments=arguments
    )
    if isinstance(confirmation, InputRequiredResult):
        return confirmation
    if confirmation is not True:
        raise PermissionError("Write was not confirmed")
    return None
