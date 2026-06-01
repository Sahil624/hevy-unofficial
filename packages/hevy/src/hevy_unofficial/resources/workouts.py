from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class WorkoutsAPI(BaseAPI):
    """Completed workouts, comments, likes, and metrics."""

    def get(self, workout_id: str) -> Any:
        """GET /workout/{workout_id}"""
        return self._request("GET", f"/workout/{workout_id}")

    def get_batch(self, batch_id: str) -> Any:
        """GET /workouts_batch/{batch_id}"""
        return self._request("GET", f"/workouts_batch/{batch_id}")

    def count(self) -> Any:
        """GET /workout_count"""
        return self._request("GET", "/workout_count")

    def list_paged(
        self,
        *,
        username: str,
        limit: int = 10,
        offset: int = 0,
        extra_params: dict[str, Any] | None = None,
    ) -> Any:
        """GET /user_workouts_paged"""
        params: dict[str, Any] = {
            "username": username,
            "limit": limit,
            "offset": offset,
        }
        if extra_params:
            params.update(extra_params)
        return self._request("GET", "/user_workouts_paged", params=params)

    def iter_paged(
        self,
        username: str,
        *,
        page_size: int = 10,
        max_pages: int | None = None,
    ):
        """Yield workouts across paginated user_workouts_paged results."""
        offset = 0
        pages = 0
        while max_pages is None or pages < max_pages:
            data = self.list_paged(username=username, limit=page_size, offset=offset)
            if not isinstance(data, dict):
                break
            workouts = data.get("workouts") or []
            if not workouts:
                break
            yield from workouts
            offset += page_size
            pages += 1
            if len(workouts) < page_size:
                break

    def calendar(self, year: int, month: int) -> Any:
        """GET /user_calendar_workouts/{year}/{month}"""
        return self._request("GET", f"/user_calendar_workouts/{year}/{month}")

    def metrics(
        self,
        metric: str,
        start_unix: int,
        end_unix: int,
    ) -> Any:
        """GET /user_workout_metrics/{metric}/{start}/{end}"""
        return self._request(
            "GET",
            f"/user_workout_metrics/{metric}/{start_unix}/{end_unix}",
        )

    def images(self, username: str, page: int) -> Any:
        """GET /user_workout_images/{username}/{page}"""
        return self._request("GET", f"/user_workout_images/{username}/{page}")

    def get_comments(self, workout_id: str) -> Any:
        """GET /workout_comments/{workout_id}"""
        return self._request("GET", f"/workout_comments/{workout_id}")

    def add_comment(self, workout_id: str, comment: str) -> Any:
        """POST /workout_comment"""
        return self._request(
            "POST",
            "/workout_comment",
            json={"workoutId": workout_id, "comment": comment},
        )

    def delete_comment(self, comment_id: str) -> Any:
        """DELETE /workout_comment/{comment_id}"""
        return self._request("DELETE", f"/workout_comment/{comment_id}")

    def like(self, workout_id: str) -> Any:
        """POST /workout/like/{workout_id}"""
        return self._request("POST", f"/workout/like/{workout_id}")

    def unlike(self, workout_id: str) -> Any:
        """POST /workout/unlike/{workout_id}"""
        return self._request("POST", f"/workout/unlike/{workout_id}")

    def get_likes(self, workout_id: str) -> Any:
        """GET /workout_likes/{workout_id}"""
        return self._request("GET", f"/workout_likes/{workout_id}")
