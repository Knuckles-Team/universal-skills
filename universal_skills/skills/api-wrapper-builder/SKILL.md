---
name: api-wrapper-builder
description: Guide for creating API wrappers using the established patterns in the agent-packages repository (like servicenow-api and gitlab-api). Use this when tasked with building a new API integration or creating wrapper classes for REST APIs from OpenAPI specs or documentation.
categories: [Development, Core]
tags: [api, wrapper, integration, development, python, pydantic]
---

# API Wrapper Builder

This skill provides step-by-step guidance on how to build a robust, standardized API wrapper for our Pydantic AI agents. It uses standard components such as the `requests` library, Pydantic models, and decorators from `agent_utilities`.

## Creating an API Wrapper

When tasked with creating a new API wrapper from OpenAPI specifications or documentation, follow these steps:

### 1. Analyze the API Output/Input

Review the provided API documentation (e.g., OpenAPI JSON/YAML, developer guides). Identify the required endpoints, authentication methods, request parameters, and response schemas.

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

## Referencing the Templates

You should rely on the templates found in the `references/` directory as a baseline for creating these wrappers. They incorporate best practices natively supported by the project architecture.
