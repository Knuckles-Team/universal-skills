"""Verify a pinned source, generated inventory and API/native MCP contract parity.

This invokes native listing and schema search only. It does not prove transport execution or call a
provider; exhaustive mocked dispatch and live endpoint checks are separate.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path

if __package__:
    from .openapi_discovery import inspect_discovery
    from .openapi_parity import (
        require_declared_authorization,
        verify_contract,
        verify_mcp,
    )
    from .openapi_schema_budget import client_budget as validate_budget
else:
    from openapi_discovery import inspect_discovery
    from openapi_parity import (
        require_declared_authorization,
        verify_contract,
        verify_mcp,
    )
    from openapi_schema_budget import client_budget as validate_budget


def package_modules(package_name):
    return [
        name
        for name in sys.modules
        if name == package_name or name.startswith(package_name + ".")
    ]


@contextmanager
def project_imports(package):
    """Check the requested tree even when another package has the same name."""
    previous = {name: sys.modules[name] for name in package_modules(package.name)}
    search_path = list(sys.path)
    for name in previous:
        del sys.modules[name]
    sys.path.insert(0, str(package.parent))
    try:
        yield
    finally:
        for name in package_modules(package.name):
            del sys.modules[name]
        sys.modules.update(previous)
        sys.path[:] = search_path


async def native_tools(package, contract, budget=None, *, ready=False):
    try:
        from fastmcp import Client
    except ImportError as exc:
        raise RuntimeError(
            "Native parity requires the connector's existing environment"
        ) from exc
    with project_imports(package):
        server = importlib.import_module(f"{package.name}.mcp_server")
        instance = server.build_server(command_args=["--transport", "stdio"])
        if ready and getattr(
            instance, "_openapi_schema_budget", None
        ) != validate_budget(budget):
            raise ValueError(
                "Ready requires the matching client budget to be active in the normal runtime configuration"
            )
        if budget is not None:
            return await inspect_discovery(
                instance, [f"{name}_operations" for name in contract["domains"]], budget
            )
        async with Client(instance) as client:
            return await asyncio.wait_for(client.list_tools(), timeout=45), None


def check(
    spec,
    package,
    *,
    native=False,
    mode="ready",
    client_budget=None,
    overlay_path=None,
    expected_overlay_sha256=None,
    evidence_root=None,
):
    if mode not in ("ready", "inspect"):
        raise ValueError("Unknown readiness mode")
    ready = mode == "ready"
    source = spec.read_bytes()
    contract = json.loads((package / "openapi_contract.json").read_text())
    inventory = verify_contract(
        json.loads(source),
        contract,
        hashlib.sha256(source).hexdigest(),
        source_bytes=source,
        overlay_bytes=overlay_path.read_bytes() if overlay_path else None,
        expected_overlay_sha256=expected_overlay_sha256,
        evidence_root=evidence_root,
    )
    saved = json.loads((package / "openapi_inventory.json").read_text())
    if saved != inventory:
        raise ValueError("Stale or incomplete operation inventory")
    if ready:
        require_declared_authorization(inventory)
        if not native or client_budget is None:
            raise ValueError(
                "Ready requires native validation and an explicit named client budget"
            )
    result = {
        "source_sha256": inventory["source_sha256"],
        "path_count": inventory["path_count"],
        "api_contract_operations": inventory["operation_count"],
        "mocked_transport_verified": False,
        "live_endpoint_verified": False,
        "ready": False,
        "readiness_scope": "Source, authorization evidence and budgeted native schemas; excludes transport/live acceptance",
    }
    if native:
        tools, disclosure = asyncio.run(
            native_tools(package, contract, client_budget, ready=ready)
        )
        result["native_mcp"] = verify_mcp(contract, tools)
        result["disclosure"] = disclosure
        result["ready"] = ready
    else:
        result["native_mcp"] = "not checked"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("package", type=Path)
    parser.add_argument("--native", action="store_true")
    parser.add_argument(
        "--inspect", action="store_true", help="Inspect without claiming readiness"
    )
    parser.add_argument("--client-budget", type=Path)
    parser.add_argument("--provider-overlay", type=Path)
    parser.add_argument("--expected-overlay-sha256")
    parser.add_argument("--evidence-root", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            check(
                args.spec.resolve(),
                args.package.resolve(),
                native=args.native,
                mode="inspect" if args.inspect else "ready",
                client_budget=args.client_budget,
                overlay_path=args.provider_overlay,
                expected_overlay_sha256=args.expected_overlay_sha256,
                evidence_root=args.evidence_root,
            ),
            indent=2,
            sort_keys=True,
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
