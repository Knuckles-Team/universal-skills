"""Source-derived checks reject self-consistent compiler and transport mistakes."""

import importlib
import json

import httpx
import pytest
from test_mcp_builder_openapi_parity import catalog as catalog

parity = importlib.import_module("openapi_parity")
source_parity = importlib.import_module("openapi_source_parity")
converter = importlib.import_module("openapi_converter")


def test_generator_cannot_mutate_its_pinned_source(catalog, monkeypatch, tmp_path):
    document = catalog[0]
    document["paths"]["/items"]["get"]["parameters"] = [
        {"name": "X-Source", "in": "header", "schema": {"type": "string"}}
    ]
    source = tmp_path / "source.json"
    source.write_text(json.dumps(document))
    compiler = converter.compile_contract

    def incorrect(document, **kwargs):
        document["paths"]["/items"]["get"]["parameters"][0]["in"] = "query"
        return compiler(document, **kwargs)

    monkeypatch.setattr(converter, "compile_contract", incorrect)
    monkeypatch.setattr(parity, "compile_contract", incorrect)
    with pytest.raises(ValueError, match="independent source"):
        converter.generate(source, tmp_path / "example_api")
    assert not (tmp_path / "example_api").exists()


def test_inventory_is_detached_from_caller_document(catalog):
    document, _, _, contract = catalog
    inventory = parity.operation_inventory(document, contract["source_sha256"])
    before = json.dumps(inventory, sort_keys=True)
    document["info"]["title"] = "changed"
    document["security"] = None
    assert json.dumps(inventory, sort_keys=True) == before


def test_source_check_preserves_exploded_array_value_order():
    source = {
        "method": "GET",
        "path": "/items",
        "parameters": [{"in": "query", "name": "tag"}],
    }
    arguments = {"query": {"tag": ["a", "b"]}}
    correct = httpx.Request("GET", "https://fixture.invalid/items?tag=a&tag=b")
    incorrect = httpx.Request("GET", "https://fixture.invalid/items?tag=b&tag=a")
    source_parity.verify_source_request(correct, source, arguments)
    with pytest.raises(ValueError, match="raw source"):
        source_parity.verify_source_request(incorrect, source, arguments)


@pytest.mark.parametrize("field", ["method", "path", "parameters"])
def test_consistently_wrong_compiler_cannot_certify_itself(catalog, monkeypatch, field):
    document, _, _, original = catalog
    document["paths"]["/items"]["get"]["parameters"] = [
        {"name": "X-Source", "in": "header", "schema": {"type": "string"}}
    ]
    compiler = parity.compile_contract

    def incorrect(document, **kwargs):
        result = compiler(document, **kwargs)
        operation = result["operations"]["getItems"]
        if field == "parameters":
            operation[field][0]["in"] = "query"
        else:
            operation[field] = "HEAD" if field == "method" else "/wrong"
        return result

    monkeypatch.setattr(parity, "compile_contract", incorrect)
    contract = incorrect(json.loads(json.dumps(document)))
    contract["source_sha256"] = original["source_sha256"]
    contract["schemas"] = {
        domain: parity.domain_schemas(contract, domain)
        for domain in contract["domains"]
    }
    with pytest.raises(ValueError, match="independent source"):
        parity.verify_contract(document, contract, original["source_sha256"])


@pytest.mark.parametrize("extra", ["multipart/form-data", "application/xml"])
def test_multiple_body_representations_cannot_be_omitted(catalog, extra):
    document = catalog[0]
    document["paths"]["/items"]["post"]["requestBody"] = {
        "content": {
            media: {"schema": {"type": "object"}}
            for media in ["application/json", extra]
        }
    }
    with pytest.raises(ValueError, match="representation-complete"):
        parity.compile_contract(document)


@pytest.mark.parametrize("malformed", [None, {}, [None], [{"missing": []}]])
def test_security_rejected_by_compiler_and_inventory(catalog, malformed):
    document, _, _, contract = catalog
    document["security"] = malformed
    for check in (
        parity.compile_contract,
        lambda doc: parity.operation_inventory(doc, contract["source_sha256"]),
    ):
        with pytest.raises(ValueError):
            check(document)


@pytest.mark.parametrize("mistake", [None, "method", "path", "query", "header"])
def test_captured_placement_checked_against_raw_source(mistake):
    source = {
        "method": "GET",
        "path": "/api/items/{id}",
        "parameters": [
            {"in": where, "name": name}
            for where, name in [
                ("path", "id"),
                ("query", "limit"),
                ("header", "X-Source"),
            ]
        ],
    }
    arguments = {
        "path": {"id": "one"},
        "query": {"limit": 2},
        "header": {"X-Source": "proof"},
    }
    request = httpx.Request(
        "HEAD" if mistake == "method" else "GET",
        "https://fixture.invalid/api/items/"
        + ("wrong" if mistake == "path" else "one"),
        params={"limit": "wrong" if mistake == "query" else "2"},
        headers={"X-Source": "wrong" if mistake == "header" else "proof"},
    )
    if mistake:
        with pytest.raises(ValueError, match="raw source"):
            source_parity.verify_source_request(request, source, arguments)
    else:
        source_parity.verify_source_request(request, source, arguments)
