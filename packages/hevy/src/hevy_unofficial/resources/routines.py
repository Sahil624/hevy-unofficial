from __future__ import annotations

from typing import Any

from hevy_unofficial._params import merge_params, sync_query
from hevy_unofficial.resources._base import BaseAPI


class RoutinesAPI(BaseAPI):
    """Routines, folders, and sync batch."""

    def sync_batch(self, versions: dict[str, str] | None = None) -> Any:
        """
        POST /routines_sync_batch

        Pass ``{}`` or ``None`` for a full sync. Otherwise pass
        ``{routine_id: updated_at_iso, ...}`` for incremental sync.
        """
        return self._request(
            "POST",
            "/routines_sync_batch",
            json=versions if versions is not None else {},
        )

    def list(self) -> Any:
        """Full routine list via sync_batch."""
        return self.sync_batch({})

    def get(self, routine_id: str) -> Any:
        """GET /routine/{routine_id}"""
        return self._request("GET", f"/routine/{routine_id}")

    def get_by_short_id(self, short_id: str) -> Any:
        """GET /routine_with_short_id/{short_id}"""
        return self._request("GET", f"/routine_with_short_id/{short_id}")

    def create(
        self,
        routine: dict[str, Any],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """POST /routine"""
        return self._request(
            "POST",
            "/routine",
            json={"routine": routine},
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def update(
        self,
        routine_id: str,
        routine: dict[str, Any],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """PUT /routine/{routine_id}"""
        return self._request(
            "PUT",
            f"/routine/{routine_id}",
            json={"routine": routine},
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def delete(
        self,
        routine_id: str,
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """DELETE /routine/{routine_id}"""
        return self._request(
            "DELETE",
            f"/routine/{routine_id}",
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def copy(
        self,
        payload: dict[str, Any],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """POST /routine_copy"""
        return self._request(
            "POST",
            "/routine_copy",
            json=payload,
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def list_folders(self) -> Any:
        """GET /routine_folders"""
        return self._request("GET", "/routine_folders")

    def create_folder(
        self,
        folder: dict[str, Any],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """POST /routine_folder"""
        return self._request(
            "POST",
            "/routine_folder",
            json={"folder": folder},
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def update_folder(
        self,
        folder: dict[str, Any],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """PUT /routine_folder"""
        return self._request(
            "PUT",
            "/routine_folder",
            json=folder,
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def delete_folder(
        self,
        folder_id: str | int,
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """DELETE /routine_folder/{folder_id}"""
        return self._request(
            "DELETE",
            f"/routine_folder/{folder_id}",
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def update_locations(
        self,
        locations: list[dict[str, Any]],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """PUT /routine_locations — reorder routines within folders."""
        return self._request(
            "PUT",
            "/routine_locations",
            json={"locations": locations},
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def reorder_folders(
        self,
        reorders: list[dict[str, Any]],
        *,
        send_sync_event_to_mobile_app: bool = True,
    ) -> Any:
        """PUT /routine_folder_order"""
        return self._request(
            "PUT",
            "/routine_folder_order",
            json={"reorders": reorders},
            params=sync_query(send_sync_event_to_mobile_app=send_sync_event_to_mobile_app),
        )

    def get_shareable_folder(self, folder_id: str | int) -> Any:
        """GET /shareable_folder/{folder_id}"""
        return self._request("GET", f"/shareable_folder/{folder_id}")
