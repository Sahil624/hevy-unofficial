from __future__ import annotations

from typing import Any


def sync_query(*, send_sync_event_to_mobile_app: bool = True) -> dict[str, str]:
    """Build sendSyncEventToMobileApp query param for routine mutations."""
    return {"sendSyncEventToMobileApp": "true" if send_sync_event_to_mobile_app else "false"}


def merge_params(
    params: dict[str, Any] | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if params is None and extra is None:
        return None
    merged: dict[str, Any] = {}
    if params:
        merged.update(params)
    if extra:
        merged.update(extra)
    return merged or None
