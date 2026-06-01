from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from hevy_unofficial.credentials import default_cache_dir
from hevy_unofficial.exercise_catalog import ExerciseCatalogStore
from hevy_unofficial.resources._base import BaseAPI


class ExercisesAPI(BaseAPI):
    """Custom exercises, built-in catalog, and per-exercise history."""

    def _catalog_store(self) -> ExerciseCatalogStore:
        cache_dir = default_cache_dir()
        if self._client.credential_store:
            cache_dir = self._client.credential_store.path.parent
        return ExerciseCatalogStore(cache_dir)

    def list_catalog(
        self,
        *,
        refresh: bool = False,
        max_age: timedelta | None = None,
    ) -> list[dict[str, Any]]:
        """
        Built-in exercise library (~400+ templates) extracted from hevy.com ``_app`` JS.

        Cached next to credentials as ``exercise_catalog.json``. By default, rechecks
        the remote bundle after 7 days or when ``refresh=True``.
        """
        store = self._catalog_store()
        kwargs: dict[str, Any] = {
            "refresh": refresh,
            "user_agent": self._client.config.user_agent,
            "timeout": self._client.config.timeout,
        }
        if max_age is not None:
            kwargs["max_age"] = max_age
        return store.fetch_and_update(**kwargs)

    def parse_catalog_from_js(self, js_path: str | Path) -> list[dict[str, Any]]:
        """Parse and cache exercises from a local ``_app-….js`` file."""
        return self._catalog_store().parse_local_js_file(Path(js_path))

    def list_custom_templates(self) -> Any:
        """GET /custom_exercise_templates"""
        return self._request("GET", "/custom_exercise_templates")

    def create_custom_template(self, exercise: dict[str, Any]) -> Any:
        """POST /custom_exercise_template"""
        return self._request(
            "POST",
            "/custom_exercise_template",
            json={"exercise": exercise},
        )

    def update_custom_template(self, exercise: dict[str, Any]) -> Any:
        """PUT /custom_exercise_template/{id} — exercise dict must include ``id``."""
        exercise_id = exercise["id"]
        return self._request(
            "PUT",
            f"/custom_exercise_template/{exercise_id}",
            json=exercise,
        )

    def delete_custom_template(self, template_id: str) -> Any:
        """DELETE /custom_exercise_template/{template_id}"""
        return self._request("DELETE", f"/custom_exercise_template/{template_id}")

    def list_template_units(self) -> Any:
        """GET /exercise_template_units"""
        return self._request("GET", "/exercise_template_units")

    def history_paged(self, params: dict[str, Any]) -> Any:
        """GET /user_exercise_history_paged"""
        return self._request("GET", "/user_exercise_history_paged", params=params)

    def sets(self, exercise_template_id: str, page: str | int) -> Any:
        """GET /user_exercise_sets/{exercise_template_id}/{page}"""
        return self._request(
            "GET",
            f"/user_exercise_sets/{exercise_template_id}/{page}",
        )
