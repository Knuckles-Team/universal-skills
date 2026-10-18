#!/usr/bin/env python3
"""Research the web through Arbora's ``research.web`` operation.

This script fetches nothing itself. It sends one ``research.web`` call to the
configured Arbora gateway and prints the Document IDs with their citations.
Search, page selection, fetching (webarchiver, with ArchiveBox as fallback),
ingest and enrichment all happen behind that one governed operation.

Configuration: ``ARBORA_URL`` (the gateway origin) and ``ARBORA_TOKEN`` (a
bearer token for a caller holding ``ingest:write``).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Sequence
from typing import Any

#: Exit status for a refused operation; there is never a local fallback.
REFUSED = 2


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--query", help="A web search query")
    parser.add_argument("--urls", nargs="+", default=[], help="1 to 32 page URLs")
    parser.add_argument(
        "--backend", choices=("webarchiver", "archivebox"), default=None
    )
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args(argv)
    if not args.query and not args.urls:
        parser.error("name --query or --urls")
    return args


def params_from(args: argparse.Namespace) -> dict[str, Any]:
    """The ``research.web`` params the arguments map to."""
    params: dict[str, Any] = {}
    if args.query:
        params["query"] = args.query
    if args.urls:
        params["urls"] = list(args.urls)
    if args.backend:
        params["backend"] = args.backend
    if args.max_pages is not None:
        params["max_pages"] = args.max_pages
    return params


async def research(params: dict[str, Any]) -> dict[str, Any]:
    from arbora.client.http import HttpTransport
    from arbora.client.invoke import invoke

    transport = HttpTransport(
        os.environ.get("ARBORA_URL", ""), os.environ.get("ARBORA_TOKEN", "")
    )
    response = await invoke(transport, "research.web", params)
    result = response.get("result") or {}
    return dict(result.get("value", result))


def main(argv: Sequence[str] | None = None) -> int:
    from arbora.client.http import OperationError

    params = params_from(parse_args(argv))
    try:
        value = asyncio.run(research(params))
    except OperationError as refused:
        print(json.dumps({"refused": refused.code}), file=sys.stderr)
        return REFUSED
    except ValueError as invalid:
        print(
            json.dumps({"refused": "INVALID_ARGUMENT", "detail": str(invalid)}),
            file=sys.stderr,
        )
        return REFUSED
    documents = [
        {"document_id": doc["document_id"], "citations": doc.get("citations", [])}
        for doc in value.get("documents", [])
    ]
    print(json.dumps({"state": value.get("state"), "documents": documents}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
