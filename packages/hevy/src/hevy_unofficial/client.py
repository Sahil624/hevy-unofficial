from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import httpx

from hevy_unofficial.config import HevyConfig
from hevy_unofficial.exceptions import HevyAPIError, HevyAuthError, HevyRateLimitError
from hevy_unofficial.models import AuthTokens

if TYPE_CHECKING:
    from hevy_unofficial.credentials import CredentialStore
from hevy_unofficial.resources import (
    AuthAPI,
    BillingAPI,
    CoachAPI,
    ExercisesAPI,
    MiscAPI,
    RoutinesAPI,
    SocialAPI,
    UsersAPI,
    WorkoutsAPI,
)


class HevyClient:
    """
    Unofficial client for https://api.hevyapp.com.

    Grouped APIs are exposed as attributes, e.g. ``client.routines.list()``,
    ``client.workouts.list_paged(username="me", limit=10)``.
    """

    def __init__(
        self,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
        user_id: str | None = None,
        config: HevyConfig | None = None,
        http_client: httpx.Client | None = None,
        credential_email: str | None = None,
        credential_store: CredentialStore | None = None,
    ) -> None:
        self.config = config or HevyConfig.from_env()
        self.credential_email = credential_email
        self.credential_store = credential_store
        self.tokens: AuthTokens | None = None
        if access_token and refresh_token:
            self.tokens = AuthTokens(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
            )
        elif access_token:
            self.tokens = AuthTokens(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token or "",
            )

        self._owns_client = http_client is None
        self._http = http_client or httpx.Client(
            base_url=self.config.base_url.rstrip("/"),
            timeout=self.config.timeout,
            headers=self._default_headers(),
        )
        self._last_token_refresh: float | None = None

        self.auth = AuthAPI(self)
        self.users = UsersAPI(self)
        self.routines = RoutinesAPI(self)
        self.workouts = WorkoutsAPI(self)
        self.exercises = ExercisesAPI(self)
        self.social = SocialAPI(self)
        self.coach = CoachAPI(self)
        self.billing = BillingAPI(self)
        self.misc = MiscAPI(self)

    def _default_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": self.config.user_agent,
            "x-api-key": self.config.api_key,
            "hevy-platform": self.config.platform,
            "Origin": self.config.origin,
            "Referer": self.config.referer,
            "Accept-Language": self.config.accept_language,
        }

    def _request_headers(self, *, auth: bool) -> dict[str, str]:
        headers = {
            "x-client-time": str(time.time()),
        }
        if auth and self.tokens:
            headers["Authorization"] = f"Bearer {self.tokens.access_token}"
        return headers

    def set_tokens(self, tokens: AuthTokens) -> None:
        self.tokens = tokens
        self._persist_credentials()

    def _persist_credentials(self) -> None:
        if (
            self.credential_store
            and self.credential_email
            and self.tokens
            and self.tokens.refresh_token
        ):
            self.credential_store.save(self.credential_email, self.tokens)

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> HevyClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
        _retry_refresh: bool = True,
    ) -> Any:
        """
        Send an HTTP request to the Hevy API.

        ``path`` may be written with or without a leading slash.
        Returns parsed JSON, or ``None`` for empty responses.
        """
        path = path if path.startswith("/") else f"/{path}"
        headers = self._request_headers(auth=auth)

        response = self._http.request(
            method.upper(),
            path,
            params=params,
            json=json,
            headers=headers,
        )

        if (
            response.status_code == 401
            and auth
            and _retry_refresh
            and self.config.auto_refresh
            and self.tokens
            and self.tokens.refresh_token
            and path not in ("/login", "/auth/refresh_token")
        ):
            body = _safe_json(response)
            error_code = body.get("error") if isinstance(body, dict) else None
            if error_code in (None, "AccessTokenExpired", "AccessTokenInvalid"):
                self._refresh_tokens()
                return self.request(
                    method,
                    path,
                    params=params,
                    json=json,
                    auth=auth,
                    _retry_refresh=False,
                )

        return self._parse_response(method, path, response)

    def _refresh_tokens(self) -> None:
        if not self.tokens or not self.tokens.refresh_token:
            raise HevyAuthError(
                "No refresh token available",
                status_code=401,
                method="POST",
                path="/auth/refresh_token",
            )

        now = time.time()
        if (
            self._last_token_refresh is not None
            and now - self._last_token_refresh < self.config.token_refresh_throttle_seconds
        ):
            return

        headers = {
            "Authorization": f"Bearer {self.tokens.access_token}",
            "x-client-time": str(now),
        }
        response = self._http.post(
            "/auth/refresh_token",
            json={"refresh_token": self.tokens.refresh_token},
            headers=headers,
        )
        if response.status_code >= 400:
            raise HevyAuthError(
                f"Token refresh failed: {response.status_code}",
                status_code=response.status_code,
                method="POST",
                path="/auth/refresh_token",
                body=_safe_json(response),
            )

        data = response.json()
        self.tokens = AuthTokens.from_response(data)
        self._last_token_refresh = now
        self._persist_credentials()

    def _parse_response(
        self,
        method: str,
        path: str,
        response: httpx.Response,
    ) -> Any:
        if response.status_code == 429:
            raise HevyRateLimitError(
                "Rate limited",
                status_code=429,
                method=method,
                path=path,
                body=_safe_json(response),
            )

        if response.status_code >= 400:
            raise HevyAPIError(
                f"HTTP {response.status_code} for {method} {path}",
                status_code=response.status_code,
                method=method,
                path=path,
                body=_safe_json(response),
            )

        if response.status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        return response.text


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text
