"""Interactive browser login and auth cookie extraction for hevy.com."""

from __future__ import annotations

import json
import os
import sys
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote

from hevy_unofficial.exceptions import HevyBrowserError
from hevy_unofficial.models import AuthTokens

if TYPE_CHECKING:
    from hevy_unofficial.credentials import CredentialStore

AUTH20_COOKIE_NAME = "auth2.0-token"
DEFAULT_HEVY_ORIGIN = "https://hevy.com"
DEFAULT_LOGIN_PATH = "/login"
DEFAULT_TIMEOUT_SEC = 300.0


def parse_auth20_cookie_value(raw: str) -> AuthTokens:
    """
    Parse the ``auth2.0-token`` cookie value (URL-encoded JSON) into :class:`AuthTokens`.

    Example cookie payload::

        {"access_token":"...","refresh_token":"...","expires_at":"2026-06-02T23:41:58.561Z"}
    """
    if not raw or not raw.strip():
        raise HevyBrowserError("Empty auth cookie value")

    decoded = unquote(raw.strip())
    try:
        data = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise HevyBrowserError(f"Invalid auth cookie JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise HevyBrowserError("Auth cookie JSON must be an object")

    access = data.get("access_token")
    refresh = data.get("refresh_token")
    if not access or not refresh:
        raise HevyBrowserError(
            "Auth cookie missing access_token or refresh_token "
            f"(keys: {sorted(data.keys())})"
        )

    return AuthTokens(
        user_id=data.get("user_id"),
        access_token=str(access),
        refresh_token=str(refresh),
        expires_at=data.get("expires_at"),
    )


def is_headless_environment() -> bool:
    """
    Return True when an interactive browser window is unlikely to work.

    Checks common CI flags, explicit opt-out env vars, and missing display on Linux.
    """
    if os.environ.get("HEVY_FORCE_BROWSER", "").lower() in ("1", "true", "yes"):
        return False

    if os.environ.get("HEVY_SKIP_BROWSER", "").lower() in ("1", "true", "yes"):
        return True

    if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        return True
    if os.environ.get("GITLAB_CI", "").lower() == "true":
        return True
    if os.environ.get("PLAYWRIGHT_HEADLESS_ONLY", "").lower() in ("1", "true", "yes"):
        return True

    if sys.platform.startswith("linux"):
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return True

    return False


def playwright_available() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def _require_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise HevyBrowserError(
            "Playwright is not installed. Install the full package:\n"
            "  pip install hevy-unofficial\n"
            "Or add the browser extra explicitly:\n"
            "  pip install hevy-unofficial[browser]\n"
            "For a minimal install without browser automation:\n"
            "  pip install 'hevy-unofficial[core]'"
        ) from exc
    return sync_playwright


def _cookies_to_tokens(cookies: list[Any]) -> AuthTokens | None:
    for cookie in cookies:
        if isinstance(cookie, dict):
            name, value = cookie.get("name"), cookie.get("value")
        else:
            name, value = getattr(cookie, "name", None), getattr(cookie, "value", None)
        if name == AUTH20_COOKIE_NAME and value:
            return parse_auth20_cookie_value(value)
    return None


def capture_tokens_via_browser(
    *,
    origin: str = DEFAULT_HEVY_ORIGIN,
    login_path: str = DEFAULT_LOGIN_PATH,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    headless: bool = False,
) -> AuthTokens:
    """
    Open a browser on hevy.com and wait until the ``auth2.0-token`` cookie is set.

    If you are already logged in, the cookie may appear without entering credentials.
    """
    if is_headless_environment() and not headless:
        raise HevyBrowserError(
            "Interactive browser login is not available in this environment "
            "(no display or CI detected). Set HEVY_FORCE_BROWSER=1 to override, "
            "or paste tokens manually / use a machine with a graphical session."
        )

    sync_playwright = _require_playwright()
    login_url = origin.rstrip("/") + login_path

    print(f"Opening browser at {login_url}")
    print("Log in to Hevy if prompted. Waiting for session cookie…")

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=headless)
        except Exception as exc:
            raise HevyBrowserError(
                f"Failed to launch Chromium: {exc}. "
                "Run: playwright install chromium"
            ) from exc

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(login_url, wait_until="domcontentloaded")

            end = time.monotonic() + timeout_sec
            tokens: AuthTokens | None = None

            while time.monotonic() < end:
                tokens = _cookies_to_tokens(context.cookies())
                if tokens:
                    break
                page.wait_for_timeout(500)

            if not tokens:
                raise HevyBrowserError(
                    f"Timed out after {timeout_sec:.0f}s waiting for "
                    f"cookie {AUTH20_COOKIE_NAME!r}. "
                    "Complete login in the browser window and try again."
                )

            return tokens
        finally:
            browser.close()


def login_via_browser(
    *,
    email: str | None = None,
    store: CredentialStore | None = None,
    save: bool = True,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> tuple[AuthTokens, str]:
    """
    Capture tokens via browser and optionally persist them in :class:`CredentialStore`.

    Returns ``(tokens, email)``. Prompts for email when not provided.
    """
    from hevy_unofficial.credentials import CredentialStore, normalize_email

    store = store or CredentialStore()

    if email is None:
        email = input("Email (cache key): ").strip()
    if not email:
        raise ValueError("Email is required")

    key = normalize_email(email)
    tokens = capture_tokens_via_browser(timeout_sec=timeout_sec)

    if save:
        store.save(key, tokens)
        print(f"Saved credentials for {key} → {store.path}")

    return tokens, key


def browser_client(
    *,
    email: str | None = None,
    store: CredentialStore | None = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
):
    """
    Build a :class:`~hevy_unofficial.client.HevyClient` after browser login.

    See :func:`login_via_browser`.
    """
    from hevy_unofficial.client import HevyClient

    tokens, key = login_via_browser(
        email=email,
        store=store,
        timeout_sec=timeout_sec,
    )
    return HevyClient(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user_id=tokens.user_id,
        credential_email=key,
        credential_store=store,
    )
