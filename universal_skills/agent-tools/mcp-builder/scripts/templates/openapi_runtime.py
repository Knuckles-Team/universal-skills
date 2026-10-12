"""Generated operation-bound vendor client and SDK MCP tool registration."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import regex
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.http.retry import RetryPolicy
from agent_connector_sdk.mcp.concurrency import run_blocking
from agent_connector_sdk.mcp.context import ctx_confirm_destructive
from fastmcp.server.dependencies import get_context
from fastmcp.tools import Tool, ToolResult
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from jsonschema.validators import extend
from mcp.types import ToolAnnotations
from pydantic import Field

from .openapi_auth_scheme import credential_headers
from .openapi_request import body_options, parameters
from .openapi_response import decode_body, read_body

CONTRACT = json.loads(Path(__file__).with_name("openapi_contract.json").read_text())
MAX_BYTES = 16 * 1024 * 1024


def _pattern(*arguments):
    """Adapt the four-argument jsonschema keyword callback."""
    _validator, pattern, instance, _schema = arguments
    if (
        isinstance(instance, str)
        and regex.search(pattern, instance, timeout=0.1) is None
    ):
        yield ValidationError("String does not satisfy its pattern")


SchemaValidator = extend(Draft202012Validator, {"pattern": _pattern})


def validate(value, definition):
    """Validate without disclosing caller input or provider response values."""
    validator = SchemaValidator(definition, format_checker=FormatChecker())
    if next(validator.iter_errors(value), None) is not None:
        raise ValueError("Value does not satisfy the declared OpenAPI schema")


class OpenApiClient:
    """Dispatch only catalogued actions; perform each HTTP request exactly once."""

    def __init__(
        self,
        base_url,
        auth,
        tls_profile=None,
        *,
        credential_scheme=None,
        write_mode="read-only",
        allow_plaintext=False,
        transport=None,
    ):
        if write_mode not in {"read-only", "read-write"}:
            raise ValueError("Unsupported OpenAPI write mode")
        parsed = urlsplit(base_url)
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("Base URL must be the provider origin without a path")
        if credential_scheme and parsed.scheme == "http" and not allow_plaintext:
            raise ValueError(
                "Credential-bearing plaintext HTTP requires explicit opt-in"
            )
        self.session = create_http_client(
            HttpClientOptions(
                base_url=base_url,
                auth=auth,
                tls=tls_profile,
                retry=RetryPolicy(max_attempts=1),
                allow_plaintext=allow_plaintext,
                timeout=30.0,
            ),
            transport=transport,
        )
        self.credential_scheme = credential_scheme
        self.allow_writes = write_mode == "read-write"

    def close(self):
        self.session.close()

    def execute(self, domain: str, arguments: dict[str, Any]):
        if domain not in CONTRACT["domains"]:
            raise ValueError("Unknown domain")
        validate(arguments, CONTRACT["schemas"][domain][0])
        operation = CONTRACT["operations"][arguments["action"]]
        if operation["domain"] != domain:
            raise ValueError("Action is outside this domain")
        if not operation["read_only"] and not self.allow_writes:
            raise PermissionError("Writes require explicit operator enablement")
        self._require_credentials(operation["security"])
        path, query, headers = parameters(
            operation,
            arguments,
            credential_headers=credential_headers(CONTRACT["security_schemes"]),
        )
        target = self.session.base_url.join(path)
        origin = self.session.base_url
        if (target.scheme, target.host, target.port) != (
            origin.scheme,
            origin.host,
            origin.port,
        ):
            raise ValueError(
                "Operation must stay within the configured provider origin"
            )
        options = {"params": query, "headers": headers, "follow_redirects": False}
        if "body" in arguments:
            options.update(
                body_options(
                    operation,
                    arguments["body"],
                    definitions=CONTRACT["definitions"],
                    max_bytes=MAX_BYTES,
                )
            )
        return self._send(operation, path, options)

    def _require_credentials(self, requirements):
        if requirements and not any(
            not choice or set(choice) == {self.credential_scheme}
            for choice in requirements
        ):
            raise PermissionError("Action requires a supported credential reference")

    def _send(self, operation, path, options):
        deadline = time.monotonic() + 60
        with self.session.stream(operation["method"], path, **options) as response:
            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Provider returned HTTP {response.status_code}; no automatic retry"
                )
            body = read_body(response, MAX_BYTES, deadline=deadline)
            content_type, data = decode_body(operation, response, body)
            result = {
                "action": operation["action"],
                "status": response.status_code,
                "content_type": content_type,
                "data": data,
            }
            validate(result, CONTRACT["schemas"][operation["domain"]][1])
            return result


class OpenApiTool(Tool):
    """One domain, discriminated action inputs, and declared response variants."""

    domain: str = Field(exclude=True)
    client_factory: Any = Field(exclude=True)

    async def run(self, arguments):
        validate(arguments, self.parameters)
        operation = CONTRACT["operations"][arguments["action"]]
        client = self.client_factory()
        if not operation["read_only"]:
            if not client.allow_writes:
                raise PermissionError("Writes require explicit operator enablement")
            if not await ctx_confirm_destructive(get_context(), operation["action"]):
                raise PermissionError("Write was not confirmed")
        result = await run_blocking(client.execute, self.domain, arguments)
        return ToolResult(structured_content=result)


def register_domain(mcp, domain, client_factory):
    operations = [
        CONTRACT["operations"][action] for action in CONTRACT["domains"][domain]
    ]
    read_only = all(operation["read_only"] for operation in operations)
    inputs, outputs = CONTRACT["schemas"][domain]
    mcp.add_tool(
        OpenApiTool(
            name=f"{domain}_operations",
            domain=domain,
            client_factory=client_factory,
            description="Bound OpenAPI operations: "
            + ", ".join(CONTRACT["domains"][domain]),
            parameters=inputs,
            output_schema=outputs,
            tags={domain},
            annotations=ToolAnnotations(
                readOnlyHint=read_only,
                destructiveHint=not read_only,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
    )
