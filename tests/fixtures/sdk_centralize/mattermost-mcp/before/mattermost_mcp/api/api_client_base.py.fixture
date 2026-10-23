import keyword
from typing import Any
from urllib.parse import urljoin

import requests
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile


def _wire_names(values: dict[str, Any] | None) -> dict[str, Any] | None:
    """Restore keyword-aliased argument names (``from_``) to their wire names (``from``).

    operation_manifest.json exposes a field named after a Python keyword as
    ``<keyword>_``; the Mattermost API expects the original name.
    """
    if not values:
        return values
    return {
        (key[:-1] if key.endswith("_") and keyword.iskeyword(key[:-1]) else key): value
        for key, value in values.items()
    }


class ApiClientBase:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        self.base_url = base_url
        self.token = token
        self.username = username
        self.password = password
        self.tls_profile = tls_profile or resolve_tls_profile("mattermost")
        self._session = self.tls_profile.configure_requests_session(requests.Session())

        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self._session.auth = (username, password)

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> Any:
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = urljoin(self.base_url, endpoint)

        headers = {"Content-Type": "application/json"}
        params = _wire_names(params)
        if isinstance(data, dict):
            data = _wire_names(data)
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
        )

        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code}")

        if response.status_code == 204 or not response.text.strip():
            return {"status": "success"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}
