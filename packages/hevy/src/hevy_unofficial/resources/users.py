from __future__ import annotations

from typing import Any

from hevy_unofficial.resources._base import BaseAPI


class UsersAPI(BaseAPI):
    """Account, profile, preferences, and user settings."""

    def get_account(self) -> Any:
        """GET /user/account"""
        return self._request("GET", "/user/account")

    def update_account(self, account: dict[str, Any]) -> Any:
        """PUT /account"""
        return self._request("PUT", "/account", json={"account": account})

    def get_preferences(self) -> Any:
        """GET /user_preferences"""
        return self._request("GET", "/user_preferences")

    def update_preferences(self, preferences: dict[str, Any]) -> Any:
        """PUT /user_preferences"""
        return self._request("PUT", "/user_preferences", json=preferences)

    def get_key_values(self) -> Any:
        """GET /user_key_values"""
        return self._request("GET", "/user_key_values")

    def update_key_values(self, values: dict[str, Any]) -> Any:
        """PUT /user_key_values"""
        return self._request("PUT", "/user_key_values", json=values)

    def get_profile(self, username: str) -> Any:
        """GET /user_profile/{username}"""
        return self._request("GET", f"/user_profile/{username}")

    def get_public_profile(self, username: str) -> Any:
        """GET /public_user_profile/{username}"""
        return self._request("GET", f"/public_user_profile/{username}")

    def get_user(self, user_id: str) -> Any:
        """GET /users/{user_id}"""
        return self._request("GET", f"/users/{user_id}")

    def update_username(
        self,
        username: str,
        *,
        is_initial_onboarding_username: bool = False,
    ) -> Any:
        """PUT /username"""
        return self._request(
            "PUT",
            "/username",
            json={
                "username": username,
                "isInitialOnboardingUsername": is_initial_onboarding_username,
            },
        )

    def get_subscription(self) -> Any:
        """GET /user_subscription"""
        return self._request("GET", "/user_subscription")

    def delete_account(self) -> Any:
        """DELETE /user"""
        return self._request("DELETE", "/user")

    def get_public_api_key(self) -> Any:
        """GET /user_public_api_key"""
        return self._request("GET", "/user_public_api_key")

    def create_public_api_key(self) -> Any:
        """POST /user_public_api_key"""
        return self._request("POST", "/user_public_api_key")

    def delete_public_api_key(self) -> Any:
        """DELETE /user_public_api_key"""
        return self._request("DELETE", "/user_public_api_key")
