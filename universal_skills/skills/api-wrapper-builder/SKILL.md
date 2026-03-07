---
name: api-wrapper-builder
description: Guide for creating API wrappers using the established patterns in the agent-packages repository (like servicenow-api and gitlab-api). Use this when tasked with building a new API integration or creating wrapper classes for REST or GraphQL APIs from OpenAPI specs or documentation.
license: MIT
tags: [api, wrapper, integration, development, python, pydantic, graphql, gql]
metadata:
  author: Audel Rouhi
  version: '0.1.32'
---
# API Wrapper Builder

This skill provides step-by-step guidance on how to build a robust, standardized API wrapper for our Pydantic AI agents. It supports both **REST** (using `requests`) and **GraphQL** (using `gql`) APIs, with Pydantic models and decorators from `agent_utilities`.

## Creating an API Wrapper

When tasked with creating a new API wrapper from OpenAPI specifications or documentation, follow these steps:

### 1. Analyze the API Output/Input

Review the provided API documentation (e.g., OpenAPI JSON/YAML, developer guides). Identify the required endpoints, authentication methods, request parameters, and response schemas.

**Also determine if the API supports GraphQL.** If it does, you will create both a REST and GraphQL wrapper (Step 5).

### 2. Formulate Pydantic Models

Create a standard input/output models file (e.g., `[api_name]_models.py`).
- **Input Models**: Define Pydantic models for API request parameters and bodies. If an endpoint supports pagination, include fields like `page_token` or `limit`.
- **Response Models**: Define Pydantic models to strictly parse and validate the JSON response.
- Use the provided `references/api_models_template.py.template` for inspiration.

### 3. Create the API Wrapper Class

Create the main API wrapper class (e.g., `[api_name]_api.py`). The class should provide a clean, pythonic interface to the endpoints.
- Initialize the `requests.Session()` within the constructor (`__init__`).
- Configure TLS verification (`urllib3.disable_warnings` if `verify=False`), proxy support, and headers.
- Handle authentication using headers or tokens.

### 4. Implement Methods and Decorators

For each endpoint, implement a corresponding method in the class:
- Unpack arguments using the input Pydantic models (`Model(**kwargs)`).
- Ensure required parameters are checked. If absent, raise `agent_utilities.exceptions.MissingParameterError`.
- Use the `@require_auth` decorator (from `agent_utilities.decorators`) on all authenticated methods.
- Make the HTTP request using the initialized session.
- Parse the resulting JSON using the appropriate response Pydantic model.
- Catch errors such as 401/403 (raising `AuthError` or `UnauthorizedError` from `agent_utilities.exceptions`) and invalid parameters (raising `ParameterError`).
- Return a standard wrapper object (e.g., `Response(response=..., result=...)`).
- Use the provided `references/api_wrapper_template.py.template` as a blueprint.

### 5. Create GraphQL Wrapper (Optional)

If the target API supports GraphQL, create a GraphQL wrapper class (e.g., `[api_name]_gql.py`):

1. **Use the `gql` library** — The class should use `gql.Client` with `gql.transport.requests.RequestsHTTPTransport`.
2. **Follow the template** — Use `references/api_graphql_template.py.template` as the blueprint.
3. **Core method** — Implement `execute_gql(query_str, variables, operation_name)` for raw query execution.
4. **Mirror REST methods** — For each REST method that has a GraphQL equivalent, create a corresponding method using GraphQL queries/mutations.
5. **Use cursor-based pagination** — GraphQL APIs typically use `first`/`after` pagination (not `limit`/`offset`).
6. **Mutations** — Use `input` variables pattern for mutations (e.g., `mutation CreateItem($input: CreateItemInput!) { ... }`).
7. **`@require_auth` decorator** — Apply to all methods that require authentication.
8. **pyproject.toml** — Add `gql = ["gql>=4.0.0"]` as an optional dependency and include it in the `all` extras.
9. **`__init__.py`** — Register as an optional module with `_GQL_AVAILABLE` flag.

## Referencing the Templates

You should rely on the templates found in the `references/` directory as a baseline for creating these wrappers. They incorporate best practices natively supported by the project architecture.

| Template | Purpose |
|----------|---------|
| `api_wrapper_template.py.template` | REST API wrapper class |
| `api_models_template.py.template` | Pydantic input/output models |
| `api_graphql_template.py.template` | GraphQL API wrapper class |
