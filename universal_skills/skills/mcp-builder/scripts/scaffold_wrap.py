"""Templates for a connector that wraps an existing MCP server (US-MCP-BUILDER-R012).

`scaffold_connector.py <fleet> --wrap-mcp <url-or-command>` uses these in place
of the REST client files. The SDK upstream registry mounts the upstream under
the connector's namespace with the upstream's own typed schemas; the generated
`governance.py` adds typed refusals, write approval, a scope allow list and an
audit record on every call. The repository ships no upstream host: the URL is
a deployment setting.
"""

from __future__ import annotations

INIT = """\"\"\"MCP connector for {Display}: the provider's MCP server behind our governance.\"\"\"

from scion_sdk.connector import Connector

from .governance import register_governance
from .upstreams import UPSTREAMS

connector = Connector(
    instructions=(
        "Operate {Display} through its provider tools, served as {short_snake}_<tool>. "
        "Read before you change. Every write asks for approval first."
    ),
    upstreams=UPSTREAMS,
    extra_registrations=(register_governance,),
)
"""

UPSTREAMS = """\"\"\"The one declared {Display} upstream MCP server (SCION-CONNECTOR-CONTROL-R914).

The SDK owns the transport, the pool, the health and the drift check. This
module adds data only. The repository ships no host: the URL, the credential
and the expected fingerprint are deployment settings.
\"\"\"

from __future__ import annotations

from scion_sdk.config import setting
from scion_sdk.mcp.upstreams import UpstreamDecl

__all__ = ["CREDENTIAL", "NAMESPACE", "UPSTREAMS", "URL_SETTING", "build_upstreams"]

#: Tools are served as ``<NAMESPACE>_<upstream tool>``.
NAMESPACE = "{short_snake}"
URL_SETTING = "{upper}_UPSTREAM_URL"
FINGERPRINT_SETTING = "{upper}_UPSTREAM_FINGERPRINT"
#: A TLS profile from the SDK catalog; unset uses the system trust store.
TLS_PROFILE_SETTING = "{upper}_TLS_PROFILE"
#: The credential is a reference; the SDK resolves it per call.
CREDENTIAL = "env://{upper}_TOKEN"


def build_upstreams() -> tuple[UpstreamDecl, ...]:
    \"\"\"The upstream declaration, or none while the URL setting is unset.\"\"\"
    url = setting(URL_SETTING, "")
    if not url:
        return ()
    return (
        UpstreamDecl(
            name=NAMESPACE,
            kind="{kind}",
            {transport}
            tls_profile=setting(TLS_PROFILE_SETTING, "") or None,
            activation="active",
            expected_fingerprint=setting(FINGERPRINT_SETTING, "") or None,
            on_drift="refuse",
        ),
    )


UPSTREAMS: tuple[UpstreamDecl, ...] = build_upstreams()
"""

HTTP_TRANSPORT = 'url=url,\n            credential=CREDENTIAL,'
STDIO_TRANSPORT = 'command={command!r},\n            env={{"{upper}_TOKEN": CREDENTIAL}},'

GOVERNANCE = """\"\"\"Governance on every served {Display} tool: refusals, approval, scope and audit.

Every call passes this middleware before the upstream. A write needs approval
through the SDK confirmation; an unapproved write sends nothing upstream. A
call that names a scope outside the allow list is refused before any request.
Failures return a typed code, never a raw exception. Every write is audited
without the credential.
\"\"\"

from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools import ToolResult
from scion_sdk.config import setting
from scion_sdk.mcp.confirmation import ctx_confirm_destructive

from .upstreams import NAMESPACE

__all__ = [
    "REFUSAL_CODES",
    "SCOPE_ARGUMENTS",
    "GovernanceMiddleware",
    "is_write",
    "register_governance",
]

AUDIT = logging.getLogger("{pkg}.audit")

WRITE_NOT_APPROVED = "WRITE_NOT_APPROVED"
SCOPE_NOT_ALLOWED = "SCOPE_NOT_ALLOWED"
CREDENTIAL_UNSET = "CREDENTIAL_UNSET"
RATE_LIMITED = "RATE_LIMITED"
UPSTREAM_ERROR = "UPSTREAM_ERROR"
REFUSAL_CODES = (
    WRITE_NOT_APPROVED,
    SCOPE_NOT_ALLOWED,
    CREDENTIAL_UNSET,
    RATE_LIMITED,
    UPSTREAM_ERROR,
)

#: Upstream tool-name verbs that change state.
WRITE_VERBS = (
    "post",
    "put",
    "patch",
    "delete",
    "create",
    "update",
    "set",
    "remove",
    "enable",
    "disable",
)
#: Arguments that name a scope checked against the allow list.
SCOPE_ARGUMENTS: tuple[str, ...] = {scope_args}
ALLOWED_SCOPES_SETTING = "{upper}_ALLOWED_SCOPES"
TOKEN_ENV = "{upper}_TOKEN"
_SECRET_WORDS = ("token", "secret", "password", "key", "authorization")


def is_write(name: str, annotations: Any = None) -> bool:
    \"\"\"A tool writes unless it is annotated read-only or its verb reads.\"\"\"
    if annotations is not None and getattr(annotations, "readOnlyHint", None) is True:
        return False
    bare = name.removeprefix(f"{{NAMESPACE}}_")
    return bare.split("_", 1)[0] in WRITE_VERBS


def _refusal(code: str, detail: str) -> ToolResult:
    payload = {{"refused": True, "code": code, "detail": detail}}
    return ToolResult(content=json.dumps(payload), structured_content=payload)


def _allowed_scopes() -> frozenset[str]:
    raw = setting(ALLOWED_SCOPES_SETTING, "")
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


def _redacted(arguments: dict[str, Any]) -> dict[str, Any]:
    return {{
        key: (
            "<redacted>"
            if any(word in key.lower() for word in _SECRET_WORDS)
            else value
        )
        for key, value in sorted(arguments.items())
    }}


def _failure_code(error: Exception) -> str:
    text = str(error).lower()
    if "429" in text or "rate limit" in text:
        return RATE_LIMITED
    return getattr(error, "code", None) or UPSTREAM_ERROR


class GovernanceMiddleware(Middleware):
    \"\"\"Typed refusals, write approval, scope allow list and audit.\"\"\"

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        name = context.message.name
        arguments = dict(context.message.arguments or {{}})
        if not name.startswith(f"{{NAMESPACE}}_"):
            return await call_next(context)
        if not os.environ.get(TOKEN_ENV):
            return _refusal(CREDENTIAL_UNSET, f"{{TOKEN_ENV}} is not set")
        allowed = _allowed_scopes()
        for argument in SCOPE_ARGUMENTS:
            value = arguments.get(argument)
            if value is not None and str(value) not in allowed:
                return _refusal(
                    SCOPE_NOT_ALLOWED, f"{{argument}} is outside {{ALLOWED_SCOPES_SETTING}}"
                )
        tool = None
        if context.fastmcp_context is not None:
            tool = await context.fastmcp_context.fastmcp.get_tool(name)
        write = is_write(name, getattr(tool, "annotations", None))
        approval = None
        if write:
            approved = await ctx_confirm_destructive(
                context.fastmcp_context,
                f"{{name}} changes {Display} state",
                confirmation_arguments=arguments,
            )
            if approved is not True:
                if approved is not False:
                    return approved
                return _refusal(WRITE_NOT_APPROVED, f"{{name}} needs approval")
            approval = "confirmed"
        try:
            result = await call_next(context)
        except Exception as error:  # every upstream failure becomes a typed code
            return _refusal(_failure_code(error), type(error).__name__)
        if write:
            caller = getattr(context.fastmcp_context, "client_id", None)
            AUDIT.info(
                json.dumps(
                    {{
                        "tool": name,
                        "arguments": _redacted(arguments),
                        "caller": caller,
                        "approval": approval,
                    }},
                    sort_keys=True,
                    default=str,
                )
            )
        return result


def register_governance(ctx: Any) -> None:
    \"\"\"Install the governance middleware on the connector's server.\"\"\"
    ctx.server.add_middleware(GovernanceMiddleware())
"""

PROBE = """\"\"\"Probe the {Display} upstream tool list and report drift (exit 1 on drift).

Prints the upstream tool count, the typed-schema count and the SDK fingerprint.
With ``{upper}_UPSTREAM_FINGERPRINT`` set, a different fingerprint exits 1.
Writes no file.
\"\"\"

from __future__ import annotations

import asyncio
import json
import os
import sys

from fastmcp import Client
from scion_sdk.mcp.upstreams.drift import fingerprint_tools

from .upstreams import FINGERPRINT_SETTING, URL_SETTING


async def _tools(url: str) -> list:
    headers = {{}}
    token = os.environ.get("{upper}_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {{token}}"
    from fastmcp.client.transports import StreamableHttpTransport

    async with Client(StreamableHttpTransport(url, headers=headers)) as client:
        return await client.list_tools()


def main() -> int:
    url = os.environ.get(URL_SETTING, "")
    if not url:
        print(json.dumps({{"refused": True, "code": "UPSTREAM_URL_UNSET"}}))
        return 2
    tools = asyncio.run(_tools(url))
    fingerprint = fingerprint_tools(tools)
    typed = sum(1 for tool in tools if (tool.inputSchema or {{}}).get("type") == "object")
    expected = os.environ.get(FINGERPRINT_SETTING, "")
    print(json.dumps({{"tools": len(tools), "typed": typed, "fingerprint": fingerprint}}))
    return 1 if expected and expected != fingerprint else 0


if __name__ == "__main__":
    sys.exit(main())
"""

PYPROJECT_SCRIPTS = """{fleet}-probe = "{pkg}.probe:main"
"""

TEST_GOVERNANCE = """\"\"\"Governance of the wrapped upstream: approval, scope, refusals, audit.\"\"\"

import asyncio
from types import SimpleNamespace

from {pkg} import governance
from {pkg}.upstreams import NAMESPACE


class _Message(SimpleNamespace):
    pass


def _context(name, arguments=None):
    return SimpleNamespace(
        message=_Message(name=name, arguments=arguments or {{}}),
        fastmcp_context=None,
    )


def test_write_verbs_and_read_only_annotation():
    assert governance.is_write(f"{{NAMESPACE}}_post_items")
    assert governance.is_write(f"{{NAMESPACE}}_delete_items_id")
    assert not governance.is_write(f"{{NAMESPACE}}_get_items")
    assert not governance.is_write(
        f"{{NAMESPACE}}_post_x", SimpleNamespace(readOnlyHint=True)
    )


async def _test_unapproved_write_sends_nothing_upstream(monkeypatch):
    monkeypatch.setenv(governance.TOKEN_ENV, "unit-test")
    sent = []

    async def upstream(context):
        sent.append(context)

    result = await governance.GovernanceMiddleware().on_call_tool(
        _context(f"{{NAMESPACE}}_post_items"), upstream
    )
    assert result.structured_content["code"] == governance.WRITE_NOT_APPROVED
    assert sent == []


async def _test_each_failure_has_a_typed_code(monkeypatch):
    middleware = governance.GovernanceMiddleware()
    monkeypatch.delenv(governance.TOKEN_ENV, raising=False)
    unset = await middleware.on_call_tool(_context(f"{{NAMESPACE}}_get_items"), None)
    assert unset.structured_content["code"] == governance.CREDENTIAL_UNSET
    monkeypatch.setenv(governance.TOKEN_ENV, "unit-test")

    async def limited(context):
        raise RuntimeError("HTTP 429 rate limit")

    async def broken(context):
        raise RuntimeError("boom")

    rate = await middleware.on_call_tool(_context(f"{{NAMESPACE}}_get_items"), limited)
    fail = await middleware.on_call_tool(_context(f"{{NAMESPACE}}_get_items"), broken)
    assert rate.structured_content["code"] == governance.RATE_LIMITED
    assert fail.structured_content["code"] == governance.UPSTREAM_ERROR


async def _test_foreign_scope_refused_before_upstream(monkeypatch):
    monkeypatch.setenv(governance.TOKEN_ENV, "unit-test")
    monkeypatch.setenv(governance.ALLOWED_SCOPES_SETTING, "allowed")
    argument = "scope_under_test"
    monkeypatch.setattr(governance, "SCOPE_ARGUMENTS", (argument,))
    sent = []

    async def upstream(context):
        sent.append(context)

    result = await governance.GovernanceMiddleware().on_call_tool(
        _context(f"{{NAMESPACE}}_get_items", {{argument: "other"}}), upstream
    )
    assert result.structured_content["code"] == governance.SCOPE_NOT_ALLOWED
    assert sent == []


def test_audit_record_redacts_secrets():
    record = governance._redacted({{"name": "a", "api_token": "s3cret"}})
    assert record == {{"api_token": "<redacted>", "name": "a"}}


def test_unapproved_write_sends_nothing_upstream(monkeypatch):
    asyncio.run(_test_unapproved_write_sends_nothing_upstream(monkeypatch))


def test_each_failure_has_a_typed_code(monkeypatch):
    asyncio.run(_test_each_failure_has_a_typed_code(monkeypatch))


def test_foreign_scope_refused_before_upstream(monkeypatch):
    asyncio.run(_test_foreign_scope_refused_before_upstream(monkeypatch))
"""

TEST_COVERAGE = """\"\"\"Coverage: the connector serves every upstream tool with a typed schema.

Starts a fixture upstream over streamable HTTP, points the connector at it and
lists the served tools. Set ``{upper}_COVERAGE_LIVE_URL`` to run the same check
against a live upstream.
\"\"\"

import asyncio
import os
import socket

from fastmcp import Client, FastMCP


def _fixture_upstream() -> FastMCP:
    upstream = FastMCP("fixture")

    @upstream.tool
    def get_items(item_id: str) -> dict:
        \"\"\"Read one item.\"\"\"
        return {{"id": item_id}}

    @upstream.tool
    def post_items(name: str) -> dict:
        \"\"\"Create an item.\"\"\"
        return {{"name": name}}

    return upstream


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _typed(schema: dict) -> bool:
    if schema.get("type") != "object":
        return False
    return all(
        any(key in prop for key in ("type", "anyOf", "oneOf", "$ref", "enum"))
        for prop in (schema.get("properties") or {{}}).values()
    )


async def _served_tools(url: str):
    import importlib

    build_server = importlib.import_module("scion_sdk.connector").build_server
    upstreams = importlib.import_module("{pkg}.upstreams")

    os.environ[upstreams.URL_SETTING] = url
    importlib.reload(upstreams)
    import {pkg}

    importlib.reload({pkg})
    _, server = build_server("{pkg}", command_args=[])
    async with Client(server) as client:
        return await client.list_tools()


async def _test_served_tools_cover_upstream_with_typed_schemas(monkeypatch):
    monkeypatch.setenv("{upper}_TOKEN", "unit-test")
    live = os.environ.get("{upper}_COVERAGE_LIVE_URL")
    if live:
        url, upstream_count, task = live, None, None
    else:
        port = _free_port()
        upstream = _fixture_upstream()
        task = asyncio.create_task(
            upstream.run_http_async(host="127.0.0.1", port=port, show_banner=False)
        )
        await asyncio.sleep(1.5)
        url, upstream_count = f"http://127.0.0.1:{{port}}/mcp", 2
    try:
        from {pkg}.upstreams import NAMESPACE

        served = [
            t for t in await _served_tools(url) if t.name.startswith(f"{{NAMESPACE}}_")
        ]
        if upstream_count is not None:
            assert len(served) >= upstream_count
        assert served
        assert all(_typed(tool.inputSchema) for tool in served)
    finally:
        if task is not None:
            task.cancel()


def test_served_tools_cover_upstream_with_typed_schemas(monkeypatch):
    asyncio.run(_test_served_tools_cover_upstream_with_typed_schemas(monkeypatch))
"""

TEST_UPSTREAMS = """\"\"\"The upstream declaration ships no host and holds a credential reference only.\"\"\"

import importlib

from {pkg} import upstreams


def test_upstream_declared_without_host(monkeypatch):
    monkeypatch.delenv(upstreams.URL_SETTING, raising=False)
    assert importlib.reload(upstreams).UPSTREAMS == ()
    monkeypatch.setenv(upstreams.URL_SETTING, "https://upstream.invalid/mcp")
    (decl,) = importlib.reload(upstreams).UPSTREAMS
    assert decl.name == upstreams.NAMESPACE
    assert decl.credential == upstreams.CREDENTIAL
    assert upstreams.CREDENTIAL.startswith("env://")
    monkeypatch.setenv(upstreams.TLS_PROFILE_SETTING, "edge")
    (decl,) = importlib.reload(upstreams).UPSTREAMS
    assert decl.tls_profile == "edge"
"""

SKILL = """---
name: {short}-operations
skill_type: skill
domain: connector
description: Operate {Display} through its provider tools served as {short_snake}_<tool>. Use when reading or changing {Display} state.
---

# {Display} operations

1. Find the operation with the fleet search; every provider tool is served as `{short_snake}_<tool>`.
2. Read first with the read tools.
3. A write returns a confirmation request: approve it, or it is refused with `WRITE_NOT_APPROVED`.
4. Refusal codes: `WRITE_NOT_APPROVED`, `SCOPE_NOT_ALLOWED`, `CREDENTIAL_UNSET`, `RATE_LIMITED`, `UPSTREAM_ERROR`.
"""

PROMPT_SERVES = "{Class}Operation"

ONTOLOGY = """@prefix : <http://knuckles.team/kg#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# {Display} classes. Every class extends a core class of the parent ontology
# through rdfs:subClassOf. The pack never imports the parent ontology.

:{Class}Operation a owl:Class ;
    rdfs:subClassOf :{core} ;
    rdfs:label "{Display} Operation" ;
    rdfs:comment "One {Display} provider operation served as a typed tool." .

:{short_camel}RelatedTo a owl:ObjectProperty ;
    rdfs:label "{Display} related to" ;
    rdfs:comment "Links a {Display} operation to any core concept it acts on." ;
    rdfs:domain :{Class}Operation ;
    rdfs:range :{core} .
"""

SOURCES = """\"\"\"Declared data sources. A wrapped upstream declares none until a read is mapped.\"\"\"

SCHEMA_VERSION = 1

SOURCES = ()
"""

SPEC_ROWS = (
    ("R001", "Declare the upstream", "The connector must declare one upstream MCP server with a credential reference and a TLS profile setting. The repository must ship no host name.", "`connector` → SDK `build_server` → upstream registry", "`{pkg}/upstreams.py`, SDK `UpstreamDecl`", "tests/test_upstreams.py::test_upstream_declared_without_host"),
    ("R002", "Serve every upstream tool typed", "The connector must serve every upstream tool as `{short_snake}_<tool>` with a typed input schema.", "`tools/list` → SDK upstream gate → upstream", "`{pkg}/upstreams.py`, SDK upstream registry", "tests/test_coverage.py::test_served_tools_cover_upstream_with_typed_schemas"),
    ("R003", "Write approval", "Every write tool must ask for approval through the SDK confirmation. An unapproved write must send nothing upstream.", "`tools/call` → `GovernanceMiddleware.on_call_tool` → SDK `ctx_confirm_destructive`", "`{pkg}/governance.py`, SDK confirmation", "tests/test_governance.py::test_unapproved_write_sends_nothing_upstream"),
    ("R004", "Typed refusals", "An unset credential, a rate limit and an upstream error must each return a typed code.", "`tools/call` → `GovernanceMiddleware.on_call_tool`", "`{pkg}/governance.py` `REFUSAL_CODES`", "tests/test_governance.py::test_each_failure_has_a_typed_code"),
    ("R005", "Scope allow list", "A call that names a scope outside the allow list must be refused before any upstream request.", "`tools/call` → `GovernanceMiddleware.on_call_tool`", "`{pkg}/governance.py` `SCOPE_ARGUMENTS`", "tests/test_governance.py::test_foreign_scope_refused_before_upstream"),
    ("R006", "Audit", "Every write must record the tool, the arguments, the caller and the approval. The record must hold no credential.", "`tools/call` → `GovernanceMiddleware.on_call_tool` → audit logger", "`{pkg}/governance.py` `_redacted`", "tests/test_governance.py::test_audit_record_redacts_secrets"),
)
