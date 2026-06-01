from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class SocialAPI(BaseAPI):
    """Feed, follows, and discovery."""

    def feed(self, cursor: str | int | None = None) -> Any:
        """GET /feed_workouts_paged or /feed_workouts_paged/{cursor}"""
        if cursor is None:
            return self._request("GET", "/feed_workouts_paged")
        return self._request("GET", f"/feed_workouts_paged/{cursor}")

    def follow(self, username: str) -> Any:
        """POST /follow"""
        return self._request("POST", "/follow", json={"username": username})

    def unfollow(self, username: str) -> Any:
        """POST /unfollow"""
        return self._request("POST", "/unfollow", json={"username": username})

    def following(self, username: str) -> Any:
        """GET /following/{username}"""
        return self._request("GET", f"/following/{username}")

    def following_statuses(self) -> Any:
        """GET /following_statuses"""
        return self._request("GET", "/following_statuses")

    def follow_counts(self) -> Any:
        """GET /follow_counts"""
        return self._request("GET", "/follow_counts")

    def followers_paged(self, username: str, page: int) -> Any:
        """GET /followers_paged/{username}/{page}"""
        return self._request("GET", f"/followers_paged/{username}/{page}")

    def followers_search(self, username: str, query: str) -> Any:
        """GET /followers_search/{username}/{query}"""
        return self._request("GET", f"/followers_search/{username}/{query}")

    def recommended_users(self) -> Any:
        """GET /recommended_users"""
        return self._request("GET", "/recommended_users")
