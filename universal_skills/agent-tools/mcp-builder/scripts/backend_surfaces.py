"""Select backend documentation without duplicating shared MCP or agent surfaces."""

CLI_ENV = """\
# Operator-provided settings; no executable is installed by this scaffold.
HOST=127.0.0.1
PORT=8000
TRANSPORT=stdio
AUTH_TYPE=none
SYSTEMTOOL=True
# Required for tool invocation: an authorized absolute executable path.
{upper_name}_EXECUTABLE=
# The starter executes only --version on POSIX; discovery launches no process.
# Network exposure and MCP authentication remain separately authorized.
"""

CLI_USAGE = """\
# Usage — CLI backend and MCP

`{package_name}` exposes a bounded local executable through its MCP server and
Python adapter. The starter has one `status` operation, which invokes the
operator-configured executable with the fixed `--version` argument.

## Configure the executable

Set `{upper_name}_EXECUTABLE` to the authorized absolute executable path in the
server's runtime environment. The scaffold does not install the program, create
credentials, or authorize its use. Validate the program's actual `--version`
behavior before enabling it. Tool discovery and imports do not launch it.

Execution requires POSIX process controls. Unsupported platforms fail explicitly
when execution is requested; portable imports do not imply execution support.
The runner uses no shell or stdin, a restricted environment, a 10-second deadline,
and a 64 KiB combined output limit. Tools accept no arbitrary command or argument
vector. Failed execution returns a bounded error without forwarding stderr.

## As an MCP server

Run `{mcp_cmd} --transport stdio`, then call the system tool with `action="status"`.
`SYSTEMTOOL` controls registration. Consult the generated
MCP schemas for the exact tool name and argument contract.

## As a Python adapter

```python
from {pkg_dir}.cli import get_client

client = get_client()  # validates the configured executable without launching it
status = client.get_system_status()  # executes only the reviewed --version command
```

Adding operations requires reviewed argument construction, effect annotations,
source mappings, and executable tests. Never pass an arbitrary shell string or
caller-supplied argument list through the tool surface.
"""

CLI_PLATFORM = """\
# Executable platform — {display_name}

`{package_name}` integrates an operator-provided executable. Provision the reviewed
program in the same POSIX runtime as the MCP server and set
`{upper_name}_EXECUTABLE` to its absolute path. Confirm its `--version` operation
matches the starter's read-only contract before exposing the tool.

The generated Python package and container do not install the target program.
For a container deployment, review a derived image containing the executable and
its required runtime files, then refer to that image by digest. Avoid projecting
unnecessary host directories or credentials into the container.

The starter does not forward caller environment variables, accept arbitrary
arguments, or bootstrap another service. Review the [execution limits](usage.md)
before adapting it to a particular program.
"""

_REPLACEMENTS = {
    "INIT_PY": (("{pkg_dir}.api", "{pkg_dir}.cli"),),
    "ROOT_MCP_CONFIG_JSON": (
        ('"{upper_name}_ALLOW_PLAINTEXT": "false"', '"{upper_name}_EXECUTABLE": ""'),
    ),
    "MCP_COMPOSE_YML": (
        (
            "{upper_name}_ALLOW_PLAINTEXT=${{{upper_name}_ALLOW_PLAINTEXT:-false}}",
            "{upper_name}_EXECUTABLE=${{{upper_name}_EXECUTABLE:?set-absolute-executable-path-inside-container}}",
        ),
    ),
    "README_MD": (
        ("full API, deployment", "full connector, deployment"),
        (
            "Configuration uses runtime credential references; resolved credentials and\nprivate endpoints are never committed.",
            "Configuration selects an operator-provided absolute executable path.\nThe CLI adapter executes only a reviewed command with bounded resources.",
        ),
        (
            "TLS profiles, bounded responses, loopback defaults, and",
            "Fixed arguments, bounded processes, loopback defaults, and",
        ),
        ("API client → provider", "bounded CLI adapter → configured executable"),
        (
            "The MCP surface uses action-routed tools. Pass an `action` and a JSON `params_json`\npayload.",
            "The MCP surface exposes the fixed `status` action without arbitrary command arguments.",
        ),
        (
            "Keep endpoint, credential, selector, and TLS references in SDK configuration; do not put\nresolved values in client configuration.",
            "Set `{upper_name}_EXECUTABLE` in the server environment to an authorized absolute\npath. Execution requires POSIX; discovery launches no process. MCP network identity\nand TLS ingress policy remain separate from executable configuration.",
        ),
        (
            "installation details, API capabilities",
            "installation details, CLI capabilities",
        ),
    ),
    "DOCS_INDEX_MD": (
        ("**API + MCP Server", "**CLI + MCP Server"),
        ("wraps the target service", "wraps an operator-provided executable"),
        (
            "Tools resolve `{upper_name}_BASE_URL`, `{upper_name}_TOKEN_REF`, and the SDK TLS\nprofile when invoked. Discovery requires no vendor credentials or live service.",
            "Tools resolve `{upper_name}_EXECUTABLE` when invoked. The starter runs only\n`--version` on POSIX with bounded process resources. Discovery launches no process.",
        ),
        ("deploy the target service with Docker", "provision the reviewed executable"),
    ),
    "DOCS_OVERVIEW_MD": (
        (
            "split into `api/` (client mixins) and `mcp/` (action-routed\n  tool modules) for cleaner organization.",
            "split into `cli.py` (bounded process execution) and `mcp/`\n  (action-routed tool modules). The fixed status action invokes `--version` on POSIX.",
        ),
    ),
    "DOCS_INSTALLATION_MD": (
        (
            "- SDK configuration containing the service origin, a credential reference and TLS profile selectors.",
            "- A POSIX runtime and an operator-provided executable with reviewed `--version` behavior.\n- `{upper_name}_EXECUTABLE` set to that program's authorized absolute path.\n\nThe generated package and container do not install the external program. Imports\nand MCP discovery work without executing it; unsupported execution platforms fail explicitly.",
        ),
    ),
    "DOCS_DEPLOYMENT_MD": (
        (
            "This page covers running `{package_name}` as long-lived servers.",
            "This page covers running `{package_name}` as long-lived servers.\nThe CLI backend requires a POSIX runtime and an operator-provisioned executable.\nSet `{upper_name}_EXECUTABLE` to its absolute path; the generated image does not\ncontain the target program. See [Executable platform](platform.md).",
        ),
        (
            "Supply the provider profile through the operator-owned connector configuration mount or secret\nprojection. The image and this document contain no endpoint, credential, or trust material.",
            "Provision the reviewed executable inside the container runtime and pass its\nabsolute path through `{upper_name}_EXECUTABLE`. Keep the process isolated and\ninclude only the program's required runtime files. This scaffold grants no access\nto host files, credentials, or external services.",
        ),
    ),
    "ROOT_AGENTS_MD": (
        (
            "`{pkg_dir}/api/` owns service operations; `mcp/` adapts them to tools.\nThe connector SDK owns HTTP, credential references, TLS, server policy,\nregistration, content publication and ingestion transport.",
            "`{pkg_dir}/cli.py` owns bounded local execution; `mcp/` adapts it to tools.\nUse only reviewed fixed argument vectors on POSIX, with no shell, no stdin, a\nrestricted environment, and finite time/output limits. The connector SDK owns\nMCP server policy, registration, content publication and ingestion transport.",
        ),
    ),
    "CHANGELOG_MD": (
        (
            "Modular subfolders for API wrappers (`api/`) and action-routed MCP tools (`mcp/`).",
            "Bounded executable adapter (`cli.py`) and action-routed MCP tools (`mcp/`).",
        ),
    ),
    "MKDOCS_YML": (("Usage (API / CLI / MCP)", "Usage (CLI backend / MCP)"),),
}


def select_backend_template(name: str, template: str, backend: str) -> str:
    """Apply after optional-agent selection and before formatting placeholders."""
    if backend == "api_client":
        return template
    if backend != "cli":
        raise ValueError(f"unsupported connector backend: {backend}")
    overrides = {
        "ENV_EXAMPLE": CLI_ENV,
        "DOCS_USAGE_MD": CLI_USAGE,
        "DOCS_PLATFORM_MD": CLI_PLATFORM,
    }
    if name in overrides:
        return overrides[name]
    for before, after in _REPLACEMENTS.get(name, ()):
        template = template.replace(before, after)
    return template
