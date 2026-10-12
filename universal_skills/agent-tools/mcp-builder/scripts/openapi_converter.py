"""Generate bound clients and condensed SDK tool registrars from OpenAPI 3."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path

from openapi_schema import compile_contract, domain_schemas
from openapi_parity import operation_inventory, verify_contract


def generate(spec: Path, package: Path, auth_scheme: str = ""):
    source = spec.read_bytes()
    document = json.loads(source)
    contract = compile_contract(document)
    contract["source_sha256"] = hashlib.sha256(source).hexdigest()
    contract["schemas"] = {
        domain: domain_schemas(contract, domain) for domain in contract["domains"]
    }
    inventory = operation_inventory(document, contract["source_sha256"])
    verify_contract(
        document, json.loads(json.dumps(contract)), contract["source_sha256"]
    )
    files = {
        package / "openapi_inventory.json": json.dumps(
            inventory, indent=2, sort_keys=True
        )
        + "\n",
        package / "openapi_contract.json": json.dumps(
            contract, indent=2, sort_keys=True
        )
        + "\n",
        package / "openapi_runtime.py": (
            Path(__file__).parent / "templates/openapi_runtime.py"
        ).read_text(),
    }
    for name in (
        "openapi_schema",
        "openapi_schema_types",
        "openapi_schema_inputs",
        "unicode_patterns",
        "openapi_parity",
        "openapi_transport_parity",
        "check_openapi_parity",
    ):
        files[package / "parity" / f"{name}.py"] = (
            Path(__file__).parent / f"{name}.py"
        ).read_text()
    files[package / "parity/unicode_properties.json"] = (
        Path(__file__).parent / "unicode_properties.json"
    ).read_text()
    files[package / "parity/__init__.py"] = (
        '"""Self-contained generated API/MCP parity checks; no sibling builder required."""\n\n'
        "from .openapi_parity import (\n    operation_inventory,\n    require_complete_coverage,\n    verify_contract,\n    verify_mcp,\n)\n"
        "from .openapi_transport_parity import verify_transport\n\n"
        '__all__ = [\n    "operation_inventory",\n    "require_complete_coverage",\n    "verify_contract",\n    "verify_mcp",\n    "verify_transport",\n]\n'
    )
    if auth_scheme and auth_scheme not in contract["security_schemes"]:
        raise ValueError("Selected auth scheme is not declared in OpenAPI")
    auth = (Path(__file__).parent / "templates/openapi_auth.py").read_text()
    files[package / "auth.py"] = (
        auth.replace("__PACKAGE_ENV__", package.name.upper())
        .replace("__SERVICE__", package.name.replace("_", "-"))
        .replace("__DEFAULT_AUTH_SCHEME__", auth_scheme)
    )
    for name in (
        "openapi_runtime",
        "openapi_request",
        "openapi_response",
        "openapi_auth_scheme",
    ):
        files[package / f"{name}.py"] = (
            Path(__file__).parent / f"templates/{name}.py"
        ).read_text()
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
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    metadata = package.parent / "pyproject.toml"
    if metadata.exists():
        text = metadata.read_text()
        parsed = tomllib.loads(text)
        required = ["jsonschema>=4.23,<5", "regex>=2026.9.29"]
        missing = [
            item for item in required if item not in parsed["project"]["dependencies"]
        ]
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
        data = parsed["tool"]["setuptools"]["package-data"].get(package.name, [])
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
                r"(?m)^" + re.escape(package.name) + r"\s*=\s*\[",
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
        tomllib.loads(text)
        metadata.write_text(text)
    return {
        str(path.relative_to(package)): hashlib.sha256(content.encode()).hexdigest()
        for path, content in files.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("package", type=Path)
    parser.add_argument("--auth-scheme", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            generate(args.spec, args.package, args.auth_scheme),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
