"""Provider client with operation-bound OpenAPI dispatch."""

from ..openapi_runtime import OpenApiClient


class ApiClientSystem(OpenApiClient):
    """Use the canonical client factory with validated domain actions."""
