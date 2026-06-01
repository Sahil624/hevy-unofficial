from __future__ import annotations

from typing import Any

from hevy_unofficial.models import AuthTokens
from hevy_unofficial.resources._base import BaseAPI


class AuthAPI(BaseAPI):
    """Login, signup, session, and password endpoints."""

    def login(
        self,
        email_or_username: str,
        password: str,
        *,
        recaptcha_token: str,
        gympass_user_id: str | None = None,
    ) -> AuthTokens:
        """POST /login — requires a valid reCAPTCHA token from the web app."""
        body: dict[str, Any] = {
            "emailOrUsername": email_or_username,
            "password": password,
            "recaptchaToken": recaptcha_token,
        }
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        data = self._request("POST", "/login", json=body, auth=False)
        tokens = AuthTokens.from_response(data)
        self._client.set_tokens(tokens)
        return tokens

    def login_google(self, code: str, *, gympass_user_id: str | None = None) -> AuthTokens:
        """POST /login_google_web"""
        body: dict[str, Any] = {"code": code}
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        data = self._request("POST", "/login_google_web", json=body, auth=False)
        tokens = AuthTokens.from_response(data)
        self._client.set_tokens(tokens)
        return tokens

    def login_apple(
        self,
        identity_token: str,
        *,
        email: str | None = None,
        gympass_user_id: str | None = None,
    ) -> AuthTokens:
        """POST /login_apple_web"""
        body: dict[str, Any] = {"identityToken": identity_token}
        if email is not None:
            body["email"] = email
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        data = self._request("POST", "/login_apple_web", json=body, auth=False)
        tokens = AuthTokens.from_response(data)
        self._client.set_tokens(tokens)
        return tokens

    def refresh(self) -> AuthTokens:
        """POST /auth/refresh_token — uses stored tokens on the client."""
        self._client._refresh_tokens()
        assert self._client.tokens is not None
        return self._client.tokens

    def logout(self) -> None:
        """DELETE /auth/session"""
        self._request("DELETE", "/auth/session")
        self._client.tokens = None

    def migrate(self) -> Any:
        """POST /auth/migrate"""
        return self._request("POST", "/auth/migrate")

    def signup(
        self,
        email: str,
        password: str,
        *,
        recaptcha_token: str,
        gympass_user_id: str | None = None,
        coach_invite: str | None = None,
    ) -> Any:
        """POST /signup"""
        body: dict[str, Any] = {
            "email": email,
            "password": password,
            "recaptchaToken": recaptcha_token,
        }
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        params = {"coachInvite": coach_invite} if coach_invite else None
        return self._request("POST", "/signup", json=body, params=params, auth=False)

    def signup_google(self, code: str, *, gympass_user_id: str | None = None) -> Any:
        """POST /sign_up_google_web"""
        body: dict[str, Any] = {"code": code}
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        return self._request("POST", "/sign_up_google_web", json=body, auth=False)

    def signup_apple(
        self,
        identity_token: str,
        *,
        email: str | None = None,
        gympass_user_id: str | None = None,
    ) -> Any:
        """POST /signup_apple_web"""
        body: dict[str, Any] = {"identityToken": identity_token}
        if email is not None:
            body["email"] = email
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        return self._request("POST", "/signup_apple_web", json=body, auth=False)

    def signup_with_verified_email(
        self,
        email: str,
        password: str,
        verification_code: str,
        *,
        gympass_user_id: str | None = None,
    ) -> Any:
        """POST /signup_with_verified_email"""
        body: dict[str, Any] = {
            "email": email,
            "password": password,
            "verificationCode": verification_code,
        }
        if gympass_user_id is not None:
            body["gympassUserId"] = gympass_user_id
        return self._request("POST", "/signup_with_verified_email", json=body, auth=False)

    def send_signup_verification_email(self, email: str) -> Any:
        """POST /send_signup_verification_email"""
        return self._request(
            "POST",
            "/send_signup_verification_email",
            json={"email": email},
            auth=False,
        )

    def recover_password(self, email: str) -> Any:
        """POST /recover_password"""
        return self._request("POST", "/recover_password", json={"email": email}, auth=False)

    def update_password(self, payload: dict[str, Any]) -> Any:
        """POST /update_password"""
        return self._request("POST", "/update_password", json=payload)

    def update_password_with_password(self, payload: dict[str, Any]) -> Any:
        """PUT /update_password_with_password"""
        return self._request("PUT", "/update_password_with_password", json=payload)

    def link_with_gympass(self, gympass_user_id: str) -> Any:
        """POST /link_with_gympass"""
        return self._request(
            "POST",
            "/link_with_gympass",
            json={"gympassUserId": gympass_user_id},
        )
