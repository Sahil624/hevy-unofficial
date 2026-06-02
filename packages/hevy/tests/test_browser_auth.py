import os

import pytest

from hevy_unofficial.browser_auth import (
    AUTH20_COOKIE_NAME,
    is_headless_environment,
    parse_auth20_cookie_value,
    playwright_available,
)
from hevy_unofficial.exceptions import HevyBrowserError

# Example shape from hevy.com auth2.0-token cookie (tokens redacted in tests).
SAMPLE_COOKIE = (
    "%7B%22access_token%22%3A%22test_access%22%2C%22refresh_token%22%3A"
    "%22test_refresh%22%2C%22expires_at%22%3A%222026-06-02T23%3A41%3A58.561Z%22%7D"
)


def test_parse_auth20_cookie_value():
    tokens = parse_auth20_cookie_value(SAMPLE_COOKIE)
    assert tokens.access_token == "test_access"
    assert tokens.refresh_token == "test_refresh"
    assert tokens.expires_at == "2026-06-02T23:41:58.561Z"


def test_parse_auth20_cookie_value_json():
    raw = (
        '{"access_token":"a","refresh_token":"r","expires_at":"2026-01-01T00:00:00Z"}'
    )
    tokens = parse_auth20_cookie_value(raw)
    assert tokens.access_token == "a"
    assert tokens.refresh_token == "r"


def test_parse_auth20_cookie_missing_token():
    with pytest.raises(HevyBrowserError, match="missing"):
        parse_auth20_cookie_value('{"access_token":"only"}')


def test_auth20_cookie_name_constant():
    assert AUTH20_COOKIE_NAME == "auth2.0-token"


def test_is_headless_ci(monkeypatch):
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("HEVY_FORCE_BROWSER", raising=False)
    monkeypatch.setenv("CI", "true")
    assert is_headless_environment() is True


def test_is_headless_force_browser(monkeypatch):
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("HEVY_FORCE_BROWSER", "1")
    assert is_headless_environment() is False


def test_is_headless_skip_browser(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setenv("HEVY_SKIP_BROWSER", "yes")
    assert is_headless_environment() is True


def test_playwright_available_without_install():
    # Unit tests run with [core] in CI; import may fail
    assert playwright_available() in (True, False)


@pytest.mark.skipif(
    os.environ.get("HEVY_RUN_BROWSER_E2E") != "1",
    reason="Set HEVY_RUN_BROWSER_E2E=1 for interactive browser test",
)
def test_capture_tokens_via_browser_e2e():
    from hevy_unofficial.browser_auth import capture_tokens_via_browser

    tokens = capture_tokens_via_browser(timeout_sec=120.0)
    assert tokens.access_token
    assert tokens.refresh_token
