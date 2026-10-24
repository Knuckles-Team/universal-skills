"""Generate bound clients and condensed SDK tool registrars from OpenAPI 3."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tomllib
from pathlib import Path

from openapi_parity import source_context, verify_contract
from openapi_schema import compile_contract, domain_schemas


def generate(
    spec: Path,
    package: Path,
    auth_scheme: str = "",
    *,
    overlay_path=None,
    expected_overlay_sha256=None,
    evidence_root=None,
):
    source = spec.read_bytes()
    provider = {
        "source_bytes": source,
        "overlay_bytes": overlay_path.read_bytes() if overlay_path else None,
        "expected_overlay_sha256": expected_overlay_sha256,
        "evidence_root": evidence_root,
    }
    contract, inventory = _compiled_source(source, provider)
    if auth_scheme and auth_scheme not in contract["security_schemes"]:
        raise ValueError("Selected auth scheme is not declared in OpenAPI")
    files = {
        package / "openapi_inventory.json": json.dumps(
            inventory, indent=2, sort_keys=True
        )
        + "\n",
        package / "openapi_contract.json": json.dumps(
            contract, indent=2, sort_keys=True
        )
        + "\n",
    }
    files.update(_parity_files(package))
    files.update(_runtime_files(package, auth_scheme))
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    _update_metadata(package)
    return {
        str(path.relative_to(package)): hashlib.sha256(content.encode()).hexdigest()
        for path, content in files.items()
    }


def _compiled_source(source, provider):
    document = json.loads(source)
    source_sha = hashlib.sha256(source).hexdigest()
    effective, inventory = source_context(document, source_sha, **provider)
    contract = compile_contract(
        copy.deepcopy(effective),
        source_operations=inventory["operations"],
        response_corrections=inventory.get("provider_overlay", {}).get(
            "response_corrections", []
        ),
    )
    contract["source_sha256"] = source_sha
    if "provider_overlay" in inventory:
        contract["provider_overlay"] = inventory["provider_overlay"]
    contract["schemas"] = {
        domain: domain_schemas(contract, domain) for domain in contract["domains"]
    }
    verify_contract(
        document,
        json.loads(json.dumps(contract)),
        contract["source_sha256"],
        **provider,
    )
    return contract, inventory


def _parity_files(package):
    files = {}
    for name in (
        "openapi_schema",
        "openapi_schema_types",
        "openapi_schema_inputs",
        "openapi_source_parity",
        "openapi_security",
        "openapi_provider_overlay",
        "openapi_provider_responses",
        "openapi_provider_evidence",
        "openapi_schema_budget",
        "openapi_discovery",
        "unicode_patterns",
        "openapi_parity",
        "openapi_transport_parity",
        "check_openapi_parity",
    ):
        files[package / "parity" / f"{name}.py"] = (
            (Path(__file__).parent / f"{name}.py")
            .read_text()
            .replace("__PACKAGE_ENV__", package.name.upper())
        )
    files[package / "parity/unicode_properties.json"] = (
        Path(__file__).parent / "unicode_properties.json"
    ).read_text()
    files[package / "parity/__init__.py"] = (
        '"""Self-contained generated API/MCP parity checks; no sibling builder required."""\n\n'
        "from .openapi_parity import (\n    operation_inventory,\n    require_complete_coverage,\n    verify_contract,\n    verify_mcp,\n)\n"
        "from .openapi_transport_parity import verify_transport\n\n"
        '__all__ = [\n    "operation_inventory",\n    "require_complete_coverage",\n    "verify_contract",\n    "verify_mcp",\n    "verify_transport",\n]\n'
    )
    return files


def _runtime_files(package, auth_scheme):
    files = {}
    auth = (Path(__file__).parent / "templates/openapi_auth.py").read_text()
    files[package / "auth.py"] = (
        auth.replace("__PACKAGE_ENV__", package.name.upper())
        .replace("__SERVICE__", package.name.replace("_", "-"))
        .replace("__DEFAULT_AUTH_SCHEME__", auth_scheme)
    )
    for name in (
        "openapi_runtime",
        "openapi_execution",
        "openapi_request",
        "openapi_response",
        "openapi_auth_scheme",
    ):
        files[package / f"{name}.py"] = (
            (Path(__file__).parent / f"templates/{name}.py")
            .read_text()
            .replace("__PACKAGE_ENV__", package.name.upper())
        )
    for target, template in {
        "mcp/__init__.py": "openapi_registrars.py",
        "api/api_client_system.py": "openapi_client_system.py",
    }.items():
        files[package / target] = (
            Path(__file__).parent / "templates" / template
        ).read_text()
    api_init = package / "api/__init__.py"
    files[api_init] = (
        api_init.read_text()
        if api_init.exists()
        else 'from .api_client_system import ApiClientSystem\n\n__all__ = ["ApiClientSystem"]\n'
    )
    return files


def _update_metadata(package):
    metadata = package.parent / "pyproject.toml"
    if metadata.exists():
        text = metadata.read_text()
        parsed = tomllib.loads(text)
        text = _add_dependencies(text, parsed["project"]["dependencies"])
        text = _add_package_data(text, package.name, parsed)
        tomllib.loads(text)
        metadata.write_text(text)


def _add_dependencies(text, existing):
    required = [
        "jsonschema>=4.23,<5",
        "regex>=2026.9.29",
        "rfc3986-validator>=0.1.1,<0.2",
        "rfc3339-validator>=0.1.4,<0.2",
    ]
    missing = [item for item in required if item not in existing]
    if missing:
        text, count = re.subn(
            r"(?m)^dependencies\s*=\s*\[",
            lambda match: (
                match.group()
                + "\n"
                + "\n".join(f"    {json.dumps(item)}," for item in missing)
            ),
            text,
            count=1,
        )
        if count != 1:
            raise ValueError("Cannot locate project dependency declaration")
    return text


def _add_package_data(text, package_name, parsed):
    data = parsed["tool"]["setuptools"]["package-data"].get(package_name, [])
    missing_data = [
        name
        for name in (
            "openapi_contract.json",
            "openapi_inventory.json",
            "parity/unicode_properties.json",
        )
        if name not in data
    ]
    if missing_data:
        section = text.index("[tool.setuptools.package-data]")
        before, after = text[:section], text[section:]
        after, count = re.subn(
            r"(?m)^" + re.escape(package_name) + r"\s*=\s*\[",
            lambda match: (
                match.group()
                + " "
                + ", ".join(json.dumps(name) for name in missing_data)
                + ","
            ),
            after,
            count=1,
        )
        if count != 1:
            raise ValueError("Cannot locate package data declaration")
        text = before + after
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("package", type=Path)
    parser.add_argument("--auth-scheme", default="")
    parser.add_argument("--provider-overlay", type=Path)
    parser.add_argument("--expected-overlay-sha256")
    parser.add_argument("--evidence-root", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            generate(
                args.spec,
                args.package,
                args.auth_scheme,
                overlay_path=args.provider_overlay,
                expected_overlay_sha256=args.expected_overlay_sha256,
                evidence_root=args.evidence_root,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
