from typing import Any

import requests
from agent_connector_sdk.exceptions import ApiError, AuthError


class BaseApiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                json=data,
                params=params,
            )
            if response.status_code == 401:
                raise AuthError("Owncast authentication was rejected")
            response.raise_for_status()
            if response.text:
                try:
                    return response.json()
                except Exception:
                    return {"status": "success", "text": response.text}
            return {"success": True}
        except requests.exceptions.RequestException as e:
            raise ApiError(f"API request failed: {type(e).__name__}") from e
