"""Generated operation-bound vendor client and SDK MCP tool registration."""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

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
import regex
from mcp.types import ToolAnnotations
from pydantic import Field

CONTRACT = json.loads(Path(__file__).with_name("openapi_contract.json").read_text())
MAX_BYTES = 16 * 1024 * 1024


def _pattern(validator, pattern, instance, schema):
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


def _value(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (str, int, float)):
        return str(value)
    raise ValueError("Unsupported parameter value")


def _parameters(operation, arguments):
    path = operation["path"]
    query, headers = [], {}
    for parameter in operation["parameters"]:
        name, location = parameter["name"], parameter["in"]
        values = arguments.get(location, {})
        if name not in values:
            continue
        value = values[name]
        if location == "path":
            rendered = _value(value)
            if rendered in {".", ".."} or any(c in rendered for c in "/\\%\r\n\x00"):
                raise ValueError("Unsafe path parameter")
            path = path.replace("{" + name + "}", quote(rendered, safe=""))
        elif location == "query":
            if isinstance(value, list):
                if parameter.get("explode", True):
                    query.extend((name, _value(item)) for item in value)
                else:
                    query.append((name, ",".join(_value(item) for item in value)))
            elif value is not None:
                query.append((name, _value(value)))
        elif location == "header":
            if name.casefold() in {"authorization", "cookie", "host", "x-api-key"}:
                raise ValueError("Authentication headers are controlled by credentials")
            rendered = _value(value)
            if any(c in rendered for c in "\r\n\x00"):
                raise ValueError("Invalid header parameter")
            headers[name] = rendered
    if "{" in path or "}" in path:
        raise ValueError("Missing path parameter")
    return path, query, headers


def _multipart(body, body_schema, definitions):
    while "$ref" in body_schema:
        body_schema = definitions[body_schema["$ref"].rsplit("/", 1)[1]]
    files, data = {}, {}
    for key, value in body.items():
        field = body_schema.get("properties", {}).get(key, {})
        if field.get("contentEncoding") == "base64":
            try:
                decoded = base64.b64decode(value, validate=True)
            except (ValueError, TypeError) as exc:
                raise ValueError("Invalid base64 upload") from exc
            if len(decoded) > MAX_BYTES:
                raise ValueError("Upload size limit exceeded")
            files[key] = ("upload", decoded, "application/octet-stream")
        else:
            data[key] = (
                json.dumps(value, separators=(",", ":"))
                if isinstance(value, (dict, list))
                else _value(value)
            )
    return {"files": files, "data": data}


class OpenApiClient:
    """Dispatch only catalogued actions; perform each HTTP request exactly once."""

    def __init__(
        self,
        base_url,
        auth,
        tls_profile=None,
        *,
        credential_scheme=None,
        allow_writes=False,
        allow_plaintext=False,
        transport=None,
    ):
        parsed = urlsplit(base_url)
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("Base URL must be the provider origin without a path")
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
        self.allow_writes = allow_writes

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
        requirements = operation["security"]
        if requirements and not any(
            not choice or set(choice) == {self.credential_scheme}
            for choice in requirements
        ):
            raise PermissionError("Action requires a supported credential reference")
        path, query, headers = _parameters(operation, arguments)
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
            body = arguments["body"]
            if len(json.dumps(body).encode()) > MAX_BYTES:
                raise ValueError("Request size limit exceeded")
            media = operation["content_type"]
            if media == "application/json":
                options["json"] = body
            elif media == "application/x-www-form-urlencoded":
                options["data"] = body
            elif media == "multipart/form-data":
                options.update(
                    _multipart(
                        body,
                        operation["input"]["properties"]["body"],
                        CONTRACT["definitions"],
                    )
                )
        return self._send(operation, path, options)

    def _send(self, operation, path, options):
        body = bytearray()
        deadline = time.monotonic() + 60
        with self.session.stream(operation["method"], path, **options) as response:
            if not 200 <= response.status_code < 300:
                raise RuntimeError(
                    f"Provider returned HTTP {response.status_code}; no automatic retry"
                )
            for chunk in response.iter_bytes():
                if time.monotonic() > deadline or len(body) + len(chunk) > MAX_BYTES:
                    raise RuntimeError("Provider response limit exceeded")
                body.extend(chunk)
            content_type = (
                response.headers.get("content-type", "").split(";", 1)[0].strip()
            )
            expected = operation["responses"].get(str(response.status_code))
            if expected is None:
                raise ValueError("Undeclared provider success status")
            if not expected:
                if body:
                    raise ValueError("Unexpected provider response body")
                content_type, data = "", None
            elif content_type not in expected:
                raise ValueError("Undeclared provider response media type")
            elif (
                operation["response_modes"][str(response.status_code)][content_type]
                == "json"
            ):
                try:
                    data = json.loads(body)
                except (ValueError, UnicodeDecodeError) as exc:
                    raise ValueError("Provider response is not JSON") from exc
            elif (
                operation["response_modes"][str(response.status_code)][content_type]
                == "text"
            ):
                try:
                    data = body.decode(response.charset_encoding or "utf-8")
                except (UnicodeDecodeError, LookupError) as exc:
                    raise ValueError(
                        "Provider text response cannot be decoded"
                    ) from exc
            else:
                data = base64.b64encode(body).decode()
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
