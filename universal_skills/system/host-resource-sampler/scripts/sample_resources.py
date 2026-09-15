#!/usr/bin/env python3
"""Emit one read-only JSON resource sample for a local or SSH-invoked host."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def number_or_text(value: str | None) -> int | str | None:
    if value is None:
        return None
    if value == "max":
        return value
    try:
        return int(value)
    except ValueError:
        return value


def psi(resource: str) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    text = read_text(Path("/proc/pressure") / resource)
    if not text:
        return result
    for line in text.splitlines():
        fields = line.split()
        values: dict[str, float | int] = {}
        for field in fields[1:]:
            name, raw = field.split("=", 1)
            values[name] = int(raw) if name == "total" else float(raw)
        result[fields[0]] = values
    return result


def meminfo() -> dict[str, int]:
    values: dict[str, int] = {}
    text = read_text(Path("/proc/meminfo")) or ""
    for line in text.splitlines():
        name, raw = line.split(":", 1)
        fields = raw.split()
        if fields:
            values[name] = int(fields[0]) * 1024
    return values


def cgroup_v2() -> dict[str, Any]:
    membership = read_text(Path("/proc/self/cgroup")) or ""
    relative = next(
        (line.split("::", 1)[1] for line in membership.splitlines() if "::" in line),
        "",
    )
    root = Path("/sys/fs/cgroup") / relative.lstrip("/")
    result: dict[str, Any] = {"path": str(root)}
    for name in (
        "memory.current",
        "memory.high",
        "memory.max",
        "memory.peak",
        "memory.swap.current",
        "memory.swap.max",
    ):
        result[name.replace(".", "_")] = number_or_text(read_text(root / name))
    for name in ("memory.events", "memory.events.local"):
        text = read_text(root / name)
        if text:
            result[name.replace(".", "_")] = {
                key: int(value)
                for key, value in (line.split() for line in text.splitlines())
            }
    return result


def filesystem(path: Path, byte_warn: float, inode_warn: float) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    disk = shutil.disk_usage(resolved)
    stats = os.statvfs(resolved)
    inode_total = stats.f_files
    inode_free = stats.f_favail
    byte_used_pct = (disk.used / disk.total * 100) if disk.total else 0.0
    inode_used_pct = (
        ((inode_total - inode_free) / inode_total * 100) if inode_total else None
    )
    return {
        "path": str(resolved),
        "bytes_total": disk.total,
        "bytes_used": disk.used,
        "bytes_free": disk.free,
        "bytes_used_pct": round(byte_used_pct, 2),
        "inodes_total": inode_total,
        "inodes_used": inode_total - inode_free if inode_total else None,
        "inodes_free": inode_free if inode_total else None,
        "inodes_used_pct": round(inode_used_pct, 2)
        if inode_used_pct is not None
        else None,
        "byte_warning": byte_used_pct >= byte_warn,
        "inode_warning": inode_used_pct is not None and inode_used_pct >= inode_warn,
    }


def directory_size(path: Path, timeout_seconds: float) -> dict[str, Any]:
    resolved = path.expanduser().resolve(strict=True)
    command = ["du", "-sB1", "--one-file-system", "--", str(resolved)]
    if shutil.which("ionice"):
        command = ["ionice", "-c", "3", *command]
    if shutil.which("nice"):
        command = ["nice", "-n", "19", *command]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return {"path": str(resolved), "bytes": None, "status": "timeout"}
    if completed.returncode != 0:
        return {"path": str(resolved), "bytes": None, "status": "unavailable"}
    try:
        size = int(completed.stdout.split()[0])
    except (IndexError, ValueError):
        return {"path": str(resolved), "bytes": None, "status": "unavailable"}
    return {"path": str(resolved), "bytes": size, "status": "ok"}


def default_size_paths() -> list[Path]:
    home = Path.home()
    candidates = [
        Path(os.environ.get("UV_CACHE_DIR", home / ".cache/uv")),
        Path(os.environ.get("PIP_CACHE_DIR", home / ".cache/pip")),
        Path(os.environ.get("PRE_COMMIT_HOME", home / ".cache/pre-commit")),
        home / ".cache/torch",
        home / ".cache/huggingface",
    ]
    cargo_target = os.environ.get("CARGO_TARGET_DIR")
    if cargo_target:
        candidates.append(Path(cargo_target))
    return candidates


def unique_existing(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        try:
            resolved = path.expanduser().resolve(strict=True)
        except OSError:
            continue
        value = str(resolved)
        if value not in seen:
            seen.add(value)
            result.append(resolved)
    return result


def percentage(value: str) -> float:
    parsed = float(value)
    if not 0 <= parsed <= 100:
        raise argparse.ArgumentTypeError("percentage must be between 0 and 100")
    return parsed


def positive_seconds(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than zero")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", type=Path, default=[])
    parser.add_argument("--size-path", action="append", type=Path, default=[])
    parser.add_argument("--disk-byte-warning", type=percentage, default=85.0)
    parser.add_argument("--disk-inode-warning", type=percentage, default=80.0)
    parser.add_argument("--size-timeout", type=positive_seconds, default=10.0)
    args = parser.parse_args()

    fs_paths = unique_existing(
        [Path("/"), Path("/home"), Path("/tmp"), Path("/var/tmp"), *args.path]
    )
    size_paths = unique_existing([*default_size_paths(), *args.size_path])
    memory = meminfo()
    swap_total = memory.get("SwapTotal", 0)
    swap_free = memory.get("SwapFree", 0)
    sample = {
        "schema": "host-resource-sample/v1",
        "observed_at": datetime.now(UTC).isoformat(),
        "host": socket.gethostname(),
        "load_average": list(os.getloadavg()),
        "memory": {
            "total_bytes": memory.get("MemTotal"),
            "available_bytes": memory.get("MemAvailable"),
            "swap_total_bytes": swap_total,
            "swap_used_bytes": max(0, swap_total - swap_free),
        },
        "pressure": {name: psi(name) for name in ("cpu", "memory", "io")},
        "cgroup_v2": cgroup_v2(),
        "filesystems": [
            filesystem(path, args.disk_byte_warning, args.disk_inode_warning)
            for path in fs_paths
        ],
        "directory_sizes": [
            directory_size(path, args.size_timeout) for path in size_paths
        ],
    }
    print(json.dumps(sample, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
