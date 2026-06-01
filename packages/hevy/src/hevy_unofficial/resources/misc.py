from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class MiscAPI(BaseAPI):
    """OAuth, webhooks, uploads, and feedback."""

    def presigned_url(self, file_name: str) -> Any:
        """POST /presigned_url"""
        return self._request("POST", "/presigned_url", json={"file_name": file_name})

    def email_download_link(self) -> Any:
        """POST /email_download_link"""
        return self._request("POST", "/email_download_link")

    def feedback(self, feedback: dict[str, Any]) -> Any:
        """POST /v2/feedback"""
        return self._request("POST", "/v2/feedback", json={"feedback": feedback})

    def get_webhook_subscription(self) -> Any:
        """GET /webhook-subscription"""
        return self._request("GET", "/webhook-subscription")

    def create_webhook_subscription(self, url: str, auth_token: str) -> Any:
        """POST /webhook-subscription"""
        return self._request(
            "POST",
            "/webhook-subscription",
            json={"url": url, "authToken": auth_token},
        )

    def oauth_code(self, client_id: str) -> Any:
        """GET /oauth/code?client_id=..."""
        return self._request("GET", "/oauth/code", params={"client_id": client_id})

    def oauth_client(self, client_id: str) -> Any:
        """GET /oauth/client/{client_id}"""
        return self._request("GET", f"/oauth/client/{client_id}")
