import json

import httpx
import pytest
import respx

from hevy_unofficial.client import HevyClient
from hevy_unofficial.credentials import CredentialStore
from hevy_unofficial.models import AuthTokens


@pytest.fixture
def store(tmp_path):
    return CredentialStore(tmp_path / "credentials.json")


def test_save_and_load(store):
    tokens = AuthTokens(
        user_id="u1",
        access_token="access",
        refresh_token="refresh",
        expires_at="2026-06-01T18:00:00Z",
    )
    store.save("User@Example.com", tokens)
    cached = store.get("user@example.com")
    assert cached is not None
    assert cached.tokens.access_token == "access"
    assert cached.tokens.refresh_token == "refresh"


def test_persists_on_client_refresh(store):
    store.save(
        "a@b.com",
        AuthTokens(access_token="old", refresh_token="r1", user_id="u1"),
    )

    with respx.mock(base_url="https://api.hevyapp.com") as router:
        router.post("/auth/refresh_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "user_id": "u1",
                    "access_token": "new_access",
                    "refresh_token": "new_refresh",
                    "expires_at": "2026-06-01T19:00:00Z",
                },
            )
        )
        router.get("/user/account").mock(
            side_effect=[
                httpx.Response(401, json={"error": "AccessTokenExpired"}),
                httpx.Response(200, json={"username": "tester"}),
            ]
        )

        with HevyClient(
            access_token="old",
            refresh_token="r1",
            credential_email="a@b.com",
            credential_store=store,
        ) as client:
            client.users.get_account()

    cached = store.get("a@b.com")
    assert cached.tokens.access_token == "new_access"
    assert cached.tokens.refresh_token == "new_refresh"

    raw = json.loads(store.path.read_text())
    assert raw["a@b.com"]["access_token"] == "new_access"
