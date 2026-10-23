from typing import Any
from urllib.parse import urljoin

import requests
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile


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
        self.last_etag: str | None = None
        self._session = requests.Session()
        self.tls_profile = tls_profile or resolve_tls_profile("caddy")
        self.tls_profile.configure_requests_session(self._session)

        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self._session.auth = (username, password)

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = urljoin(self.base_url, endpoint)

        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        content_type = req_headers.get("Content-Type", "")
        kwargs: dict[str, Any] = {}

        if "application/json" in content_type:
            if isinstance(data, str):
                kwargs["data"] = data
            else:
                kwargs["json"] = data
        else:
            kwargs["data"] = data

        response = self._session.request(
            method=method,
            url=url,
            headers=req_headers,
            params=params,
            **kwargs,
        )

        self.last_etag = response.headers.get("ETag")

        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code}")

        if response.status_code == 204 or not response.text.strip():
            return {"status": "success"}

        try:
            return response.json()
        except Exception:
            return {"status": "success", "text": response.text}
