#!/usr/bin/env python3
"""
Start one or more servers, wait for them to be ready, run a command, then clean up.

Usage:
    # Single server
    python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py
    python scripts/with_server.py --server "npm start" --port 3000 -- python test.py

    # Multiple servers
    python scripts/with_server.py \
      --server "python server.py" --cwd backend --port 3000 \
      --server "npm run dev" --cwd frontend --port 5173 \
      -- python test.py

Server commands are parsed into argv and are never passed through a shell.
Working directories are independently declared and confined beneath the
configured workspace root.
"""

import argparse
import os
import shlex
import signal
import subprocess
import socket
import sys
import time
from pathlib import Path

_MAX_SERVERS = 8
_MAX_ARGV_ITEMS = 64
_MAX_ARGUMENT_BYTES = 4096


def _bounded_argv(command: str) -> list[str]:
    if (
        not isinstance(command, str)
        or len(command.encode("utf-8")) > _MAX_ARGUMENT_BYTES
    ):
        raise ValueError("Server command is empty or exceeds the size limit")
    argv = shlex.split(command, posix=os.name != "nt")
    if not argv or len(argv) > _MAX_ARGV_ITEMS:
        raise ValueError("Server command has an invalid argument count")
    if any("\x00" in item for item in argv):
        raise ValueError("Server command contains an invalid argument")
    return argv


def _workspace_root() -> Path:
    return Path(os.environ.get("WORKSPACE_PATH") or Path.cwd()).resolve()


def _confined_cwd(value: str | None) -> Path:
    root = _workspace_root()
    candidate = root if not value else Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Server working directory is outside the workspace") from exc
    if not resolved.is_dir():
        raise ValueError("Server working directory is not a directory")
    return resolved


def is_server_ready(port, timeout=30):
    """Wait for server to be ready by polling the port."""
    if not 1 <= port <= 65535 or not 1 <= timeout <= 300:
        raise ValueError("Port or timeout is outside the permitted range")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description="Run command with one or more servers")
    parser.add_argument(
        "--server",
        action="append",
        dest="servers",
        required=True,
        help="Server command (can be repeated)",
    )
    parser.add_argument(
        "--port",
        action="append",
        dest="ports",
        type=int,
        required=True,
        help="Port for each server (must match --server count)",
    )
    parser.add_argument(
        "--cwd",
        action="append",
        dest="working_directories",
        help="Workspace-relative working directory for the corresponding server",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds per server (default: 30)",
    )
    parser.add_argument(
        "--command-timeout",
        type=int,
        default=600,
        help="Maximum command runtime in seconds (default: 600, maximum: 3600)",
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="Command to run after server(s) ready"
    )

    args = parser.parse_args()

    # Remove the '--' separator if present
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]

    if not args.command:
        print("Error: No command specified to run")
        sys.exit(1)
    if not 1 <= args.command_timeout <= 3600:
        print("Error: --command-timeout must be between 1 and 3600 seconds")
        sys.exit(1)

    # Parse server configurations
    if len(args.servers) != len(args.ports) or len(args.servers) > _MAX_SERVERS:
        print("Error: Number of --server and --port arguments must match")
        sys.exit(1)
    if args.working_directories and len(args.working_directories) != len(args.servers):
        print("Error: Provide one --cwd for every --server, or omit --cwd")
        sys.exit(1)

    servers = []
    cwd_values = args.working_directories or [None] * len(args.servers)
    try:
        for cmd, port, cwd in zip(args.servers, args.ports, cwd_values, strict=True):
            servers.append(
                {"argv": _bounded_argv(cmd), "port": port, "cwd": _confined_cwd(cwd)}
            )
    except (ValueError, OSError) as exc:
        print(f"Error: invalid server configuration ({type(exc).__name__})")
        sys.exit(1)

    if (
        len(args.command) > _MAX_ARGV_ITEMS
        or sum(len(item.encode("utf-8")) for item in args.command) > _MAX_ARGUMENT_BYTES
        or any("\x00" in item for item in args.command)
    ):
        print("Error: command has an invalid argument count or value")
        sys.exit(1)

    server_processes = []

    try:
        # Start all servers
        for i, server in enumerate(servers):
            executable = Path(server["argv"][0]).name
            print(f"Starting server {i + 1}/{len(servers)}: {executable}")

            process = subprocess.Popen(
                server["argv"],
                cwd=server["cwd"],
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=os.name != "nt",
            )
            server_processes.append(process)

            # Wait for this server to be ready
            print(f"Waiting for server on port {server['port']}...")
            if not is_server_ready(server["port"], timeout=args.timeout):
                raise RuntimeError(
                    f"Server failed to start on port {server['port']} within {args.timeout}s"
                )

            print(f"Server ready on port {server['port']}")

        print(f"\nAll {len(servers)} server(s) ready")

        # Run the command
        print(f"Running: {Path(args.command[0]).name}\n")
        try:
            result = subprocess.run(
                args.command, shell=False, check=False, timeout=args.command_timeout
            )
            sys.exit(result.returncode)
        except subprocess.TimeoutExpired:
            print("Command exceeded its configured runtime limit")
            sys.exit(124)

    finally:
        # Clean up all servers
        print(f"\nStopping {len(server_processes)} server(s)...")
        for i, process in enumerate(server_processes):
            try:
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
            except ProcessLookupError:
                pass
            print(f"Server {i + 1} stopped")
        print("All servers stopped")


if __name__ == "__main__":
    main()
