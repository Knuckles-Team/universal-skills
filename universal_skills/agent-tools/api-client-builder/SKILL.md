---
name: api-client-builder
description: >-
  Guide for creating API clients using the established patterns in the agent-
  packages repository (like servicenow-api and gitlab-api). Use this when tasked
  with building a new API integration or creating client classes for REST or
  GraphQL APIs from OpenAPI specs or documentation.
license: MIT
tags: [api, client, integration, development, python, pydantic, graphql, gql]
metadata:
  author: Genius
  version: '0.23.2'
---
# API Client Builder

This skill provides step-by-step guidance on how to build a robust, standardized API client for our Pydantic AI agents. It supports both **REST** (using `requests`) and **GraphQL** (using `gql`) APIs, with Pydantic models and decorators from `agent_utilities`.

## Standard API Client Structure

All API clients MUST use the `api/` subdirectory pattern (the monolithic `api_client.py` single-file approach is deprecated):

```
{pkg_dir}/
├── auth.py                      # Authentication setup
├── api_client.py                 # Facade re-exporting from api/ (backward compat)
├── models.py                     # Pydantic input/output models
├── api/
│   ├── __init__.py              # Expose ApiClientBase + all domain clients
│   ├── api_client_base.py       # HTTP handler base class
│   └── api_client_{domain}.py   # Domain-specific API methods
└── gql_client.py                # Optional: GraphQL client
```

## Creating an API Client

### 1. Analyze the API Output/Input

Review the provided API documentation (OpenAPI JSON/YAML, developer guides). Identify endpoints, authentication methods, request parameters, and response schemas. Determine if the API supports GraphQL (create both REST + GraphQL clients if so).

### 2. Formulate Pydantic Models

Create `{pkg_dir}/models.py`:
- **Input Models**: Pydantic models for API request parameters and bodies (include `page_token`/`limit` for pagination)
- **Response Models**: Pydantic models to parse and validate JSON responses
- Use `references/api_models_template.py.template` for reference

### 3. Create the API Client Class Structure

#### `{pkg_dir}/api/api_client_base.py`
- Inherits from a base HTTP handler or constructs a base client using `requests.Session()`
- Configures TLS verification, proxies, headers, base URL, and low-level HTTP calls (`_request`, `get`, `post`, etc.)
- Reads auth credentials from standard env vars

#### `{pkg_dir}/api/api_client_{domain}.py`
- Inherits from `ApiClientBase`
- Exposes pythonic methods mapping directly to target service endpoint actions
- One file per functional domain (e.g., `api_client_docker.py`, `api_client_system.py`)

#### `{pkg_dir}/api/__init__.py`
- Exposes all classes for clean imports: `from {pkg_dir}.api import ApiClientBase, ApiClientDocker`

#### `{pkg_dir}/api_client.py` (Facade)
- Re-exports from `api/` for backward compatibility:
  ```python
  from {pkg_dir}.api import ApiClientBase, ApiClientSystem  # noqa: F401
  ```

### 4. Implement Methods and Decorators

For each endpoint:
- Unpack arguments using Pydantic models (`Model(**kwargs)`)
- Check required parameters — raise `agent_utilities.exceptions.MissingParameterError` if absent
- Use `@require_auth` decorator from `agent_utilities.decorators` on authenticated methods
- Make HTTP requests using the initialized session
- Parse JSON responses with appropriate Pydantic response model
- Handle errors: 401/403 → `AuthError`/`UnauthorizedError`, invalid params → `ParameterError`
- Return standard response objects

### 5. Create GraphQL Client (Optional)

If the target API supports GraphQL, create `{pkg_dir}/gql_client.py`:
1. Use `gql.Client` with `gql.transport.requests.RequestsHTTPTransport`
2. Implement `execute_gql(query_str, variables, operation_name)` for raw query execution
3. Mirror REST methods with GraphQL equivalents
4. Use cursor-based pagination (`first`/`after`)
5. Apply `@require_auth` decorator
6. Add `gql = ["gql>=4.0.0"]` to pyproject.toml optional dependencies
7. Register as optional module with `_GQL_AVAILABLE` flag in `__init__.py`

### 6. Configure Authentication (`auth.py`)

Standard environment variable naming:

| Pattern | Example | Notes |
|---------|---------|-------|
| `{SERVICE}_URL` | `PORTAINER_URL` | NOT `_BASE_URL` or `_INSTANCE` |
| `{SERVICE}_TOKEN` | `PORTAINER_TOKEN` | Prefer over `_API_KEY` |
| `{SERVICE}_SSL_VERIFY` | `PORTAINER_SSL_VERIFY` | NOT `_VERIFY` or `_AGENT_VERIFY` |
| `{SERVICE}_USERNAME` | `PORTAINER_USERNAME` | For basic auth |
| `{SERVICE}_PASSWORD` | `PORTAINER_PASSWORD` | For basic auth |

**First-party env vars**: Preserve names when the upstream service defines them (e.g., `GITHUB_TOKEN`, `LANGFUSE_PUBLIC_KEY`).

Standard `auth.py` pattern:
```python
import os
from {pkg_dir}.api import ApiClient{Domain}

def get_client() -> ApiClient{Domain}:
    """Initialize authenticated API client."""
    try:
        return ApiClient{Domain}(
            url=os.getenv("{SERVICE}_URL", ""),
            token=os.getenv("{SERVICE}_TOKEN", ""),
            ssl_verify=os.getenv("{SERVICE}_SSL_VERIFY", "True").lower() in ("true", "1", "yes"),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {service} client: {e}") from e
```

## Referencing the Templates

| Template | Purpose |
|----------|---------|
| `api_client_template.py.template` | REST API client class |
| `api_models_template.py.template` | Pydantic input/output models |
| `api_graphql_template.py.template` | GraphQL API client class |

## Ecosystem Drift Check (MANDATORY)

After completing the API client, run a drift audit to confirm the project meets all ecosystem standards. This is a hard gate — the package is not complete until it passes with 0 missing items.

```bash
cd {project_dir} && echo "=== Drift Audit ===" \
  && for f in README.md CHANGELOG.md AGENTS.md pyproject.toml requirements.txt \
    .pre-commit-config.yaml .bumpversion.cfg .gitignore .gitattributes \
    .dockerignore .env; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in docs/index.md docs/overview.md docs/concepts.md; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && for f in tests/conftest.py tests/test_concept_parity.py \
    tests/test_init_dynamics.py tests/test_startup.py; do \
    [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"; done \
  && grep -q "ECO-4.0" docs/concepts.md && echo "✅ ECO-4.0 bridge" \
    || echo "❌ ECO-4.0 bridge MISSING"
```

> [!IMPORTANT]
> A new package is not complete until it passes the drift check with 0 missing items.
