#!/usr/bin/env python3
"""Fetch one page: forwards to web-crawler with one URL and ``max_pages`` 1."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", required=True)
    parser.add_argument("--backend", choices=("webarchiver", "archivebox"))
    args = parser.parse_args(argv)
    sys.path.insert(
        0, str(Path(__file__).resolve().parents[2] / "web-crawler" / "scripts")
    )
    import crawl

    forwarded = ["--urls", args.url, "--max-pages", "1"]
    if args.backend:
        forwarded += ["--backend", args.backend]
    return crawl.main(forwarded)


if __name__ == "__main__":
    sys.exit(main())
