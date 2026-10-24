"""Preserve provider-origin and SDK write-confirmation boundaries."""

from urllib.parse import urlsplit

from agent_connector_sdk.mcp.context import ctx_confirm_destructive
from fastmcp.server.dependencies import get_context
from mcp.types import InputRequiredResult


def _reviewed_public(operation, overlay):
    classifications = overlay.get("authorization_classifications")
    binding = {
        "operation_id": operation.get("action"),
        "method": operation.get("method"),
        "path": operation.get("source_path"),
        "source_operation_sha256": operation.get("source_operation_sha256"),
        "reviewed_guard_classification": "explicit-public-decorator",
    }
    return (
        all(isinstance(value, str) and value for value in binding.values())
        and isinstance(classifications, list)
        and any(
            isinstance(entry, dict)
            and all(entry.get(key) == value for key, value in binding.items())
            for entry in classifications
        )
    )


def require_authorization(operation, contract):
    """An omitted declaration cannot dispatch as an anonymous public operation.

    Provider classifications come only from the generator's hash-bound evidence
    verifier. Preserve their exact source binding here; parity independently
    recompiles the source and rejects changes to these generated fields.
    """
    declaration = operation.get("security_declaration")
    if declaration in ("operation", "root"):
        return
    overlay = contract.get("provider_overlay")
    if (
        declaration == "unknown"
        and operation.get("security") == []
        and isinstance(overlay, dict)
        and _reviewed_public(operation, overlay)
    ):
        return
    raise PermissionError("Action authorization requires reviewed provider evidence")


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
