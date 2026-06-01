from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hevy_unofficial.client import HevyClient


class BaseAPI:
    """Base class for grouped API endpoints."""

    def __init__(self, client: HevyClient) -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
    ) -> Any:
        return self._client.request(method, path, params=params, json=json, auth=auth)
