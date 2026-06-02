from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from hevy_unofficial.config import HevyConfig
from hevy_unofficial.models import AuthTokens

if TYPE_CHECKING:
    from hevy_unofficial.client import HevyClient


def default_cache_dir() -> Path:
    """Default cache directory: ~/.config/hevy-unofficial/"""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base = Path(xdg_config)
    else:
        base = Path.home() / ".config"
    return base / "hevy-unofficial"


def default_cache_path() -> Path:
    """Default credential file: ~/.config/hevy-unofficial/credentials.json"""
    return default_cache_dir() / "credentials.json"


def normalize_email(email: str) -> str:
    return email.strip().lower()


@dataclass
class CachedCredentials:
    email: str
    tokens: AuthTokens
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "email": self.email,
            "updated_at": self.updated_at,
            "user_id": self.tokens.user_id,
            "access_token": self.tokens.access_token,
            "refresh_token": self.tokens.refresh_token,
            "expires_at": self.tokens.expires_at,
        }

    @classmethod
    def from_dict(cls, email: str, data: dict[str, Any]) -> CachedCredentials:
        return cls(
            email=email,
            tokens=AuthTokens(
                user_id=data.get("user_id"),
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=data.get("expires_at"),
            ),
            updated_at=data.get("updated_at") or _utc_now(),
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CredentialStore:
    """
  Persist auth tokens keyed by email.

  File format::

      {
        "user@example.com": {
          "access_token": "...",
          "refresh_token": "...",
          "user_id": "...",
          "expires_at": "...",
          "updated_at": "2026-06-01T12:00:00+00:00"
        }
      }
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else default_cache_path()

    def load_all(self) -> dict[str, dict[str, Any]]:
        if not self.path.is_file():
            return {}
        raw = self.path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid credential cache format in {self.path}")
        return data

    def save_all(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, indent=2)
        self.path.write_text(payload + "\n", encoding="utf-8")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def get(self, email: str) -> CachedCredentials | None:
        key = normalize_email(email)
        entry = self.load_all().get(key)
        if not entry:
            return None
        return CachedCredentials.from_dict(key, entry)

    def save(self, email: str, tokens: AuthTokens) -> CachedCredentials:
        key = normalize_email(email)
        data = self.load_all()
        cached = CachedCredentials(email=key, tokens=tokens, updated_at=_utc_now())
        data[key] = cached.to_dict()
        self.save_all(data)
        return cached

    def delete(self, email: str) -> bool:
        key = normalize_email(email)
        data = self.load_all()
        if key not in data:
            return False
        del data[key]
        self.save_all(data)
        return True

    def list_emails(self) -> list[str]:
        return sorted(self.load_all().keys())


def prompt_tokens() -> AuthTokens:
    """Prompt for tokens on stdin (hidden refresh optional)."""
    access = input("Access token: ").strip()
    refresh = input("Refresh token: ").strip()
    user_id = input("User ID (optional, Enter to skip): ").strip() or None
    expires_at = input("Expires at ISO (optional, Enter to skip): ").strip() or None
    if not access or not refresh:
        raise ValueError("Access token and refresh token are required")
    return AuthTokens(
        user_id=user_id,
        access_token=access,
        refresh_token=refresh,
        expires_at=expires_at,
    )


def _try_browser_login(
    email: str,
    store: CredentialStore,
    *,
    timeout_sec: float = 300.0,
) -> AuthTokens | None:
    """Return tokens from browser login, or None if browser auth is unavailable."""
    from hevy_unofficial.browser_auth import (
        capture_tokens_via_browser,
        is_headless_environment,
        playwright_available,
    )
    from hevy_unofficial.exceptions import HevyBrowserError

    if is_headless_environment():
        print(
            "Skipping browser login (headless/CI environment). "
            "Set HEVY_FORCE_BROWSER=1 to override."
        )
        return None
    if not playwright_available():
        print(
            "Skipping browser login (Playwright not installed). "
            "Install with: pip install hevy-unofficial  "
            "or pip install hevy-unofficial[browser]"
        )
        return None

    try:
        print("Starting browser login…")
        tokens = capture_tokens_via_browser(timeout_sec=timeout_sec)
        store.save(email, tokens)
        print(f"Saved credentials from browser for {normalize_email(email)} → {store.path}")
        return tokens
    except HevyBrowserError as exc:
        print(f"Browser login failed: {exc}")
        return None


def prompt_client(
    *,
    email: str | None = None,
    store: CredentialStore | None = None,
    config: HevyConfig | None = None,
    force_prompt: bool = False,
    use_browser: bool | None = None,
    browser_timeout_sec: float = 300.0,
) -> HevyClient:
    """
    Build a :class:`HevyClient` using cached credentials when available.

    1. Ask for email (unless provided).
    2. If cache has tokens for that email and ``force_prompt`` is false, use them.
    3. Otherwise obtain tokens: browser login when ``use_browser`` is true (default
       when Playwright is installed and a display is available), else stdin prompt.
    4. On token refresh, the client updates the cache automatically.

    Parameters
    ----------
    use_browser:
        ``True`` — try browser login before stdin.
        ``False`` — never use browser login.
        ``None`` (default) — try browser when Playwright is available and not headless.
    """
    store = store or CredentialStore()
    if email is None:
        email = input("Email: ").strip()
    if not email:
        raise ValueError("Email is required")

    key = normalize_email(email)
    cached = None if force_prompt else store.get(key)
    if cached:
        print(f"Using cached credentials for {cached.email} (updated {cached.updated_at})")
        tokens = cached.tokens
    else:
        tokens = None
        if use_browser is not False:
            tokens = _try_browser_login(
                key,
                store,
                timeout_sec=browser_timeout_sec,
            )
        if tokens is None:
            if use_browser is True:
                raise ValueError(
                    "Browser login was required but did not succeed. "
                    "Install Playwright, run in a graphical session, or pass use_browser=False."
                )
            print("Enter tokens from browser DevTools or POST /login.")
            tokens = prompt_tokens()
            store.save(key, tokens)
            print(f"Saved credentials for {key} → {store.path}")

    from hevy_unofficial.client import HevyClient

    return HevyClient(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user_id=tokens.user_id,
        config=config,
        credential_email=key,
        credential_store=store,
    )
