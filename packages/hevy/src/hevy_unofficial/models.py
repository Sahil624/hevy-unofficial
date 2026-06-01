from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuthTokens(BaseModel):
    """Tokens returned by POST /login and POST /auth/refresh_token."""

    model_config = ConfigDict(extra="allow")

    user_id: str | None = None
    access_token: str
    refresh_token: str
    expires_at: str | None = None

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> AuthTokens:
        return cls.model_validate(data)


class SyncParams(BaseModel):
    """Query flag used by many routine mutations."""

    send_sync_event_to_mobile_app: bool = Field(
        default=True,
        serialization_alias="sendSyncEventToMobileApp",
    )

    def to_query(self) -> dict[str, str]:
        return {"sendSyncEventToMobileApp": "true" if self.send_sync_event_to_mobile_app else "false"}
