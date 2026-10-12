"""Verify a pinned source, generated inventory and API/native MCP contract parity.

This invokes tools/list only. It does not prove transport execution or call a
provider; exhaustive mocked dispatch and live endpoint checks are separate.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import json
import sys
from pathlib import Path

if __package__:
    from .openapi_parity import (
        require_declared_authorization,
        verify_contract,
        verify_mcp,
    )
else:
    from openapi_parity import (
        require_declared_authorization,
        verify_contract,
        verify_mcp,
    )


async def native_tools(package):
    try:
        from fastmcp import Client
    except ImportError as exc:
        raise RuntimeError(
            "Native parity requires the connector's existing environment"
        ) from exc
    sys.path.insert(0, str(package.parent))
    server = importlib.import_module(f"{package.name}.mcp_server")
    async with Client(
        server.build_server(command_args=["--transport", "stdio"])
    ) as client:
        return await asyncio.wait_for(client.list_tools(), timeout=45)


def check(spec, package, *, native=False):
    source = spec.read_bytes()
    contract = json.loads((package / "openapi_contract.json").read_text())
    inventory = verify_contract(
        json.loads(source), contract, hashlib.sha256(source).hexdigest()
    )
    saved = json.loads((package / "openapi_inventory.json").read_text())
    if saved != inventory:
        raise ValueError("Stale or incomplete operation inventory")
    require_declared_authorization(inventory)
    result = {
        "source_sha256": inventory["source_sha256"],
        "path_count": inventory["path_count"],
        "api_contract_operations": inventory["operation_count"],
        "mocked_transport_verified": False,
        "live_endpoint_verified": False,
    }
    if native:
        result["native_mcp"] = verify_mcp(contract, asyncio.run(native_tools(package)))
    else:
        result["native_mcp"] = "not checked"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("package", type=Path)
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            check(args.spec.resolve(), args.package.resolve(), native=args.native),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
