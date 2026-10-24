"""A complete source catalog is required; discovery alone is not execution proof."""

import asyncio
import copy
import importlib
import json
import sys
import tomllib
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "universal_skills/skills/mcp-builder/scripts"
sys.path.insert(0, str(SCRIPTS))
parity = importlib.import_module("openapi_parity")
generate = importlib.import_module("openapi_converter").generate


@pytest.fixture
def catalog(tmp_path):
    document = {
        "openapi": "3.0.3",
        "info": {"title": "Full fixture", "version": "1"},
        "paths": {
            "/items": {
                method: {
                    "operationId": method + "Items",
                    "tags": ["Items"],
                    "x-fixture-admin-only": method == "delete",
                    "x-fixture-permission": method + ".items",
                    "responses": {"204": {"description": "No content"}},
                }
                for method in sorted(parity.HTTP_METHODS)
            }
        },
    }
    source = tmp_path / "source.json"
    source.write_text(json.dumps(document))
    package = tmp_path / "fixture"
    generate(source, package)
    return (
        document,
        source,
        package,
        json.loads((package / "openapi_contract.json").read_text()),
    )


def test_full_inventory_preserves_authorization_and_packaging(catalog):
    document, source, package, contract = catalog
    inventory = parity.verify_contract(document, contract, contract["source_sha256"])
    assert inventory == json.loads((package / "openapi_inventory.json").read_text())
    assert inventory["operation_count"] == 8
    assert inventory["operations"]["deleteItems"]["extensions"] == {
        "x-fixture-admin-only": True,
        "x-fixture-permission": "delete.items",
    }
    assert inventory["live_verified"] is False
    first = generate(source, package)
    assert generate(source, package) == first
    metadata = package.parent / "pyproject.toml"
    metadata.write_text(
        "[project]\ndependencies=[]\n[tool.setuptools.package-data]\nfixture=[]\n"
    )
    generate(source, package)
    assert (
        "openapi_inventory.json"
        in tomllib.loads(metadata.read_text())["tool"]["setuptools"]["package-data"][
            "fixture"
        ]
    )
    assert (
        "parity/unicode_properties.json"
        in tomllib.loads(metadata.read_text())["tool"]["setuptools"]["package-data"][
            "fixture"
        ]
    )
    assert (package / "parity/unicode_properties.json").is_file()
    spec = importlib.util.spec_from_file_location(
        "generated_parity",
        package / "parity/__init__.py",
        submodule_search_locations=[str(package / "parity")],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert (
        module.verify_contract(document, contract, contract["source_sha256"])
        == inventory
    )


@pytest.mark.parametrize(
    "change",
    ["missing", "route", "parameters", "schema", "domain", "security", "source"],
)
def test_contract_drift_fails(catalog, change):
    document, _, _, contract = catalog
    operation = contract["operations"]["getItems"]
    if change == "missing":
        del contract["operations"]["getItems"]
    elif change == "schema":
        operation["input"]["required"] = []
    elif change == "domain":
        contract["domains"]["items"].remove("getItems")
    elif change == "source":
        contract["source_sha256"] = "wrong"
    else:
        operation[
            {"route": "path", "parameters": "parameters", "security": "security"}[
                change
            ]
        ] = "wrong"
    with pytest.raises(ValueError):
        parity.verify_contract(
            document,
            contract,
            "original" if change == "source" else contract["source_sha256"],
        )


def test_compiler_cannot_silently_drop_operations(catalog, monkeypatch):
    document, _, _, contract = catalog
    compiler = parity.compile_contract

    def partial(document, **kwargs):
        value = compiler(document, **kwargs)
        del value["operations"]["deleteItems"]
        return value

    monkeypatch.setattr(parity, "compile_contract", partial)
    with pytest.raises(ValueError, match="omitted"):
        parity.verify_contract(document, contract, contract["source_sha256"])


@pytest.mark.parametrize(
    ("path", "name", "location"),
    [
        ("/items/{id}", "request", "path"),
        ("/items/{id}", "id", "query"),
        ("/items", "path", "path"),
        ("/items/{id", "id", "path"),
        ("/items/{}", "id", "path"),
        ("/items", "request", "body"),
    ],
)
def test_invalid_path_parameter_export_rejected(catalog, path, name, location):
    document = catalog[0]
    operation = document["paths"]["/items"]["get"]
    operation["parameters"] = [
        {"in": location, "name": name, "required": True, "schema": {"type": "string"}}
    ]
    document["paths"] = {path: {"get": operation}}
    with pytest.raises(ValueError, match="placeholder|parameter location"):
        parity.compile_contract(document)


def test_binary_representation_preserves_source_metadata_and_extensions():
    translate = importlib.import_module("openapi_schema").schema
    definition = {
        "type": "string",
        "format": "binary",
        "contentEncoding": "binary",
        "description": "Provider file bytes",
        "x-provider-required": True,
    }
    translated = translate(definition)
    assert translated == {
        **definition,
        "contentEncoding": "base64",
        "x-mcp-source-content-encoding": "binary",
    }
    assert definition["contentEncoding"] == "binary"


@pytest.mark.parametrize(
    "constraint", [{"maxLength": 4}, {"enum": ["abc"]}, {"pattern": "^[a-z]+$"}]
)
def test_binary_constraints_require_representation_aware_adapter(constraint):
    translate = importlib.import_module("openapi_schema").schema
    with pytest.raises(ValueError, match="representation-aware"):
        translate({"type": "string", "format": "binary", **constraint})


@pytest.mark.parametrize(
    "body",
    [
        {"$ref": "#/components/schemas/File", "maxLength": 4},
        {"allOf": [{"$ref": "#/components/schemas/File"}, {"enum": ["abc"]}]},
    ],
)
def test_referenced_binary_constraints_cannot_bypass_guard(catalog, body):
    document = catalog[0]
    document["components"] = {
        "schemas": {"File": {"type": "string", "format": "binary"}}
    }
    document["paths"]["/items"]["get"]["responses"] = {
        "200": {"content": {"application/octet-stream": {"schema": body}}}
    }
    with pytest.raises(ValueError, match="representation-aware"):
        parity.compile_contract(document)


@pytest.mark.parametrize(
    "actions", [[], ["getItems"], ["invented"], ["getItems", "getItems"]]
)
def test_partial_or_duplicate_transport_claim_rejected(catalog, actions):
    contract = catalog[3]
    with pytest.raises(ValueError):
        parity.require_complete_coverage(contract, contract["operations"], actions)


def operation_tools(contract):
    tools = []
    for domain, actions in contract["domains"].items():
        for action in actions:
            tools.append(
                {
                    "name": parity.operation_tool_name(action),
                    "inputSchema": parity.operation_input_schema(contract, action),
                    "outputSchema": copy.deepcopy(contract["schemas"][domain][1]),
                }
            )
    return tools


def test_mcp_omission_and_schema_drift_rejected(catalog):
    pytest.importorskip("agent_connector_sdk")
    contract = catalog[3]
    tools = operation_tools(contract)
    assert parity.verify_mcp(contract, tools)["exposed_operations"] == 8
    with pytest.raises(ValueError, match="Unreachable"):
        parity.verify_mcp(contract, tools[1:])
    wrong = copy.deepcopy(tools)
    wrong[0]["inputSchema"]["properties"]["invented"] = {"type": "string"}
    with pytest.raises(ValueError, match="schema"):
        parity.verify_mcp(contract, wrong)


def test_native_reference_expansion_preserves_sibling_constraints(catalog):
    pytest.importorskip("agent_connector_sdk")
    from fastmcp.utilities.json_schema import dereference_refs

    document, source, package, _ = catalog
    document["components"] = {"schemas": {"Token": {"type": "string", "minLength": 1}}}
    document["paths"]["/items"]["get"]["parameters"] = [
        {
            "name": "token",
            "in": "query",
            "schema": {"$ref": "#/components/schemas/Token", "minLength": 5},
        }
    ]
    source.write_text(json.dumps(document))
    generate(source, package)
    contract = json.loads((package / "openapi_contract.json").read_text())
    tools = [
        {
            **tool,
            "inputSchema": dereference_refs(tool["inputSchema"]),
            "outputSchema": dereference_refs(tool["outputSchema"]),
        }
        for tool in operation_tools(contract)
    ]
    assert parity.verify_mcp(contract, tools)["exposed_operations"] == 8
    variant = next(
        tool["inputSchema"]
        for tool in tools
        if tool["name"] == parity.operation_tool_name("getItems")
    )
    assert variant["properties"]["query"]["properties"]["token"]["minLength"] == 5
    variant["properties"]["query"]["properties"]["token"]["minLength"] = 1
    with pytest.raises(ValueError, match="schema"):
        parity.verify_mcp(contract, tools)


def test_client_unsupported_unicode_regex_is_explicit(catalog):
    pytest.importorskip("agent_connector_sdk")
    contract = catalog[3]
    tools = operation_tools(contract)
    tools[0]["inputSchema"]["properties"] = {
        "label": {"type": "string", "pattern": r"\p{L}+"}
    }
    with pytest.raises(ValueError, match="unsupported by client validation"):
        parity.verify_mcp(contract, tools)


def test_omitted_security_is_unknown_not_public(catalog):
    document, _, _, contract = catalog
    inventory = parity.operation_inventory(document, contract["source_sha256"])
    assert {op["security_declaration"] for op in inventory["operations"].values()} == {
        "unknown"
    }
    with pytest.raises(ValueError, match="reviewed provider evidence"):
        parity.require_declared_authorization(inventory)
    document["security"] = []
    inventory = parity.operation_inventory(document, contract["source_sha256"])
    assert {op["security_declaration"] for op in inventory["operations"].values()} == {
        "root"
    }
    parity.require_declared_authorization(inventory)


def test_real_client_and_native_mcp_transport(catalog, monkeypatch):
    pytest.importorskip("agent_connector_sdk")
    pytest.importorskip("regex")
    import httpx
    from fastmcp import Client, FastMCP

    document, source, package, contract = catalog
    # This fixture source supports three read methods. Mutating operations are
    # covered by the complete inventory and fail-closed coverage tests above.
    document["security"] = []
    document["paths"]["/items"] = {
        method: operation
        for method, operation in document["paths"]["/items"].items()
        if method in {"get", "head", "options"}
    }
    unicode_schema = {"type": "string", "pattern": r"^[\p{L}\p{M}\p{N}]+$"}
    document["paths"]["/items"]["get"]["responses"] = {
        "200": {"content": {"application/json": {"schema": unicode_schema}}}
    }
    source.write_text(json.dumps(document))
    generate(source, package)
    read_contract = json.loads((package / "openapi_contract.json").read_text())
    monkeypatch.syspath_prepend(str(package.parent))
    runtime = importlib.import_module("fixture.openapi_runtime")
    fixtures = {
        action: {
            "arguments": {"action": action},
            "response": {"status_code": 204},
            "expected_request": {"path": "/items"},
            "expected_result": {
                "action": action,
                "status": 204,
                "content_type": "",
                "data": None,
            },
        }
        for action in read_contract["operations"]
    }
    fixtures["getItems"]["response"] = {"status_code": 200, "json": "é例𐐀"}
    fixtures["getItems"]["expected_result"].update(
        status=200, content_type="application/json", data="é例𐐀"
    )

    def factory(transport, operation):
        return runtime.OpenApiClientBase(
            "https://fixture.invalid", httpx.Auth(), transport=transport
        )

    async def call(name, arguments, provider):
        server = FastMCP("Parity fixture")
        runtime.register_domain(server, "items", lambda: provider)
        async with Client(server) as client:
            return await client.call_tool(name, arguments)

    runner = importlib.import_module("openapi_transport_parity").verify_transport
    result = asyncio.run(
        runner(
            source.read_bytes(),
            read_contract,
            fixtures,
            api_factory=factory,
            mcp_call=call,
        )
    )
    assert result == {
        "api_operations": 3,
        "mcp_operations": 3,
        "mocked_transport_verified": True,
        "live_endpoint_verified": False,
    }
    with pytest.raises(ValueError, match="differs"):
        asyncio.run(
            runner(
                source.read_bytes(),
                contract,
                fixtures,
                api_factory=factory,
                mcp_call=call,
            )
        )


@pytest.mark.parametrize("body", [{}, {"note": "hello"}, {"assetData": "aGk="}])
def test_optional_files_preserve_multipart_media(catalog, monkeypatch, body):
    pytest.importorskip("agent_connector_sdk")
    pytest.importorskip("regex")
    from email.parser import BytesParser
    from email.policy import default

    import httpx

    document, source, _, _ = catalog
    document["security"] = []
    operation = document["paths"]["/items"]["post"]
    operation["parameters"] = [
        {"name": "X-Trace", "in": "header", "schema": {"type": "string"}}
    ]
    operation["requestBody"] = {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "note": {"type": "string"},
                        "assetData": {"type": "string", "format": "binary"},
                    },
                }
            }
        },
    }
    source.write_text(json.dumps(document))
    package = source.parent / "multipart_fixture"
    generate(source, package)
    monkeypatch.syspath_prepend(str(package.parent))
    for name in list(sys.modules):
        if name.startswith("multipart_fixture.") or name == "multipart_fixture":
            del sys.modules[name]
    runtime = importlib.import_module("multipart_fixture.openapi_runtime")
    seen = []

    def respond(request):
        assert request.headers["x-trace"] == "kept"
        assert request.headers["content-type"].startswith("multipart/form-data;")
        message = BytesParser(policy=default).parsebytes(
            b"Content-Type: "
            + request.headers["content-type"].encode()
            + b"\r\n\r\n"
            + request.content
        )
        parts = {
            part.get_param("name", header="Content-Disposition"): part.get_payload(
                decode=True
            )
            for part in message.iter_parts()
        }
        assert parts == {
            key: (b"hi" if key == "assetData" else value.encode())
            for key, value in body.items()
        }
        seen.append(request)
        return httpx.Response(204)

    client = runtime.OpenApiClientBase(
        "https://fixture.invalid",
        httpx.Auth(),
        transport=httpx.MockTransport(respond),
        write_mode="read-write",
    )
    try:
        client.execute(
            "items",
            {"action": "postItems", "body": body, "header": {"X-Trace": "kept"}},
        )
        assert len(seen) == 1
    finally:
        client.close()


def test_legacy_verifier_fails_closed_for_missing_generated_client(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "integration_check", SCRIPTS / "templates/verify_api_integration.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pipelines_hooks]\npackages=["example"]\n'
    )
    with pytest.raises(ValueError, match="api_client_system"):
        module.find_package(tmp_path)
    package = tmp_path / "example"
    (package / "api").mkdir(parents=True)
    (package / "api/api_client.py").write_text("class ApiClientSystem: pass\n")
    with pytest.raises(ValueError, match="api_client_system"):
        module.find_package(tmp_path)
    (package / "api/api_client_system.py").write_text("class ApiClientSystem: pass\n")
    (package / "mcp_server.py").write_text("# Native server\n")
    assert module.find_package(tmp_path) == package
